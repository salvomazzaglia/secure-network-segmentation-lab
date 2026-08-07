"""CLI for Secure Network Segmentation Lab (snsl)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from secure_network_segmentation_lab import __version__
from secure_network_segmentation_lab.adapters import build_all_plans, build_plan
from secure_network_segmentation_lab.api import run_server, warn_if_non_localhost
from secure_network_segmentation_lab.classification import classify_inventory
from secure_network_segmentation_lab.config import (
    load_app_config,
    load_reachability_policy_raw,
    load_segmentation_policy_raw,
    validate_policy_structure,
)
from secure_network_segmentation_lab.database import open_database
from secure_network_segmentation_lab.drift import detect_drift
from secure_network_segmentation_lab.enums import PrivacyMode
from secure_network_segmentation_lab.imports import ImportError_, summarize_import
from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab
from secure_network_segmentation_lab.paths import (
    database_path,
    repo_root,
    runtime_dir,
)
from secure_network_segmentation_lab.policy import evaluate_all, load_segmentation_policy
from secure_network_segmentation_lab.policy_validation import (
    validate_reachability_policy,
    validate_segmentation_policy,
)
from secure_network_segmentation_lab.reachability import (
    evaluate_reachability,
    load_reachability_policy,
)
from secure_network_segmentation_lab.reports import export_reports
from secure_network_segmentation_lab.simulator import simulate_run
from secure_network_segmentation_lab.snapshots import build_snapshot, snapshot_to_dict


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def cmd_version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def cmd_generate_demo(args: argparse.Namespace) -> int:
    script = repo_root() / "scripts" / "generate-synthetic-lab.py"
    # No shell=True — invoke interpreter directly
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(script), "--seed", str(args.seed)],
        check=False,
    )
    if result.returncode != 0:
        return result.returncode
    bootstrap_lab(config_name=args.config)
    print("Demo generated and loaded into SQLite.")
    print("PROPOSED / SIMULATED — NOT APPLIED")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    errors: list[str] = []
    try:
        seg = load_segmentation_policy_raw()
        validate_policy_structure(seg, "segmentation")
        validate_segmentation_policy(seg)
        print("segmentation-policy.yml: OK")
    except Exception as exc:  # noqa: BLE001 — CLI surfaces all validation errors
        errors.append(f"segmentation-policy: {exc}")
    try:
        rch = load_reachability_policy_raw()
        validate_policy_structure(rch, "reachability")
        validate_reachability_policy(rch)
        print("reachability-policy.yml: OK")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"reachability-policy: {exc}")
    try:
        load_app_config("default.config.json")
        load_app_config("demo.config.json")
        print("app configs: OK")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"app config: {exc}")
    if args.import_path:
        try:
            summary = summarize_import(Path(args.import_path))
            _print_json(summary)
        except ImportError_ as exc:
            errors.append(str(exc))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("validate: all checks passed")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    devices = db.list_devices()
    if not devices:
        db = bootstrap_lab(config_name=args.config)
        devices = db.list_devices()
    _print_json(devices)
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    if not db.list_devices():
        db = bootstrap_lab(config_name=args.config)
    results = classify_inventory(db.list_devices(), db.list_observations())
    for clf in results:
        db.upsert_classification(clf)
    _print_json([c.model_dump(mode="json") for c in results])
    return 0


def cmd_evaluate_policy(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    if not db.list_devices():
        db = bootstrap_lab(config_name=args.config)
    policy = load_segmentation_policy()
    decisions = evaluate_all(db.list_devices(), db.list_classifications(), policy=policy)
    for d in decisions:
        db.upsert_policy_decision(d)
    _print_json([d.model_dump(mode="json") for d in decisions])
    return 0


def cmd_reachability(args: argparse.Namespace) -> int:
    load_reachability_policy()
    result = evaluate_reachability(args.source, args.destination, args.service)
    _print_json(result.model_dump(mode="json"))
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    if not db.list_devices():
        db = bootstrap_lab(config_name=args.config)
    findings = detect_drift(
        db.list_devices(),
        db.list_classifications(),
        db.list_policy_decisions(),
    )
    _print_json([f.model_dump(mode="json") for f in findings])
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    if not db.list_devices():
        db = bootstrap_lab(config_name=args.config)
    events = simulate_run(
        db,
        scenario=args.scenario,
        seed=args.seed,
        duration_steps=args.duration,
        speed=args.speed,
    )
    if args.output:
        Path(args.output).write_text(json.dumps(events, indent=2, default=str), encoding="utf-8")
    _print_json({"count": len(events), "events": events[:20], "truncated": len(events) > 20})
    return 0


def cmd_adapter_plan(args: argparse.Namespace) -> int:
    if args.adapter:
        _print_json(build_plan(args.adapter).model_dump(mode="json"))
    else:
        _print_json([p.model_dump(mode="json") for p in build_all_plans()])
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    warn_if_non_localhost(args.host)
    run_server(host=args.host, port=args.port, bootstrap=not args.no_bootstrap)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    cfg = load_app_config(args.config)
    db = open_database(database_path(cfg.database_path))
    if not db.list_devices():
        db = bootstrap_lab(config_name=args.config)
    out = Path(args.output or (runtime_dir() / "exports"))
    out.mkdir(parents=True, exist_ok=True)
    mode = PrivacyMode(args.privacy_mode)
    from secure_network_segmentation_lab.reachability import evaluate_matrix

    segments = [s["segment_id"] for s in db.list_segments()]
    reach = [
        r.model_dump(mode="json")
        for r in evaluate_matrix(
            segments, segments, ["any", "dns", "ssh"], policy=load_reachability_policy()
        )
    ]
    drift = [
        f.model_dump(mode="json")
        for f in detect_drift(
            db.list_devices(), db.list_classifications(), db.list_policy_decisions()
        )
    ]
    written = export_reports(
        out,
        devices=db.list_devices(),
        classifications=db.list_classifications(),
        decisions=db.list_policy_decisions(),
        reachability=reach,
        drift=drift,
        audit=db.list_audit(),
        privacy_mode=mode,
    )
    snap = snapshot_to_dict(build_snapshot(db))
    snap_path = out / "lab-snapshot.json"
    snap_path.write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")
    written.append(snap_path)
    _print_json({"written": [str(p) for p in written], "privacy_mode": mode.value})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snsl",
        description="Secure Network Segmentation Lab CLI (synthetic, offline)",
    )
    parser.add_argument(
        "--config", default="demo.config.json", help="App config filename under config/"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("version", help="Print version")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("generate-demo", help="Regenerate synthetic lab and load SQLite")
    p.add_argument("--seed", type=int, default=42)
    p.set_defaults(func=cmd_generate_demo)

    p = sub.add_parser("validate", help="Validate configs/policies/imports")
    p.add_argument("--import", dest="import_path", default=None)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("inventory", help="Show inventory")
    p.set_defaults(func=cmd_inventory)

    p = sub.add_parser("classify", help="Run classifier")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("evaluate-policy", help="Evaluate segmentation policy")
    p.set_defaults(func=cmd_evaluate_policy)

    p = sub.add_parser("reachability", help="Evaluate reachability")
    p.add_argument("--source", required=True)
    p.add_argument("--destination", required=True)
    p.add_argument("--service", default="any")
    p.set_defaults(func=cmd_reachability)

    p = sub.add_parser("drift", help="Detect segmentation drift")
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("simulate", help="Run deterministic synthetic simulation")
    p.add_argument("--scenario", default="mixed")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--duration", type=int, default=10)
    p.add_argument("--output", default=None)
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("adapter-plan", help="Show DRY-RUN adapter plans")
    p.add_argument("--adapter", default=None)
    p.set_defaults(func=cmd_adapter_plan)

    p = sub.add_parser("serve", help="Start local API (default 127.0.0.1)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-bootstrap", action="store_true")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("export", help="Export sanitized reports/snapshot")
    p.add_argument("--output", default=None)
    p.add_argument("--privacy-mode", default="masked", choices=[m.value for m in PrivacyMode])
    p.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Refuse enforcement-style commands if somehow aliased
    forbidden = {"apply", "enforce", "disconnect", "change-vlan", "push-config"}
    if args.command in forbidden:
        print(f"Command '{args.command}' is not available in v1.0", file=sys.stderr)
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
