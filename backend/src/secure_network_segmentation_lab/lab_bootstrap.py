"""Load synthetic lab artifacts into SQLite and run classify/policy pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from secure_network_segmentation_lab.classification import classify_inventory
from secure_network_segmentation_lab.config import load_app_config, load_segments
from secure_network_segmentation_lab.database import Database, open_database
from secure_network_segmentation_lab.enums import SourceMode
from secure_network_segmentation_lab.inventory import merge_devices
from secure_network_segmentation_lab.models import Device, Observation, Segment
from secure_network_segmentation_lab.observations import normalize_observations
from secure_network_segmentation_lab.paths import database_path, synthetic_dir
from secure_network_segmentation_lab.policy import evaluate_all
from secure_network_segmentation_lab.segmentation import apply_recommended_segment_simulated
from secure_network_segmentation_lab.services import normalize_services
from secure_network_segmentation_lab.topology import build_topology_from_lab


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def bootstrap_lab(
    db: Database | None = None,
    *,
    synth: Path | None = None,
    config_name: str = "demo.config.json",
) -> Database:
    """Load synthetic/ into SQLite. Classification SEPARATE from VLAN assignment."""
    cfg = load_app_config(config_name)
    db = db or open_database(database_path(cfg.database_path))
    synth = synth or synthetic_dir()

    db.clear_all()
    db.set_meta("source_mode", SourceMode.SYNTHETIC.value)
    db.set_meta("change_label", "PROPOSED / SIMULATED — NOT APPLIED")
    db.set_meta("seed", str(cfg.synthetic_seed))

    for seg in load_segments().get("segments", []):
        db.upsert_segment(Segment.model_validate(seg))

    devices_raw = _load_json(synth / "devices.json")
    if isinstance(devices_raw, dict):
        devices_raw = devices_raw.get("devices", [])
    observations_raw = _load_jsonl(synth / "observations.jsonl")
    observations = [o.model_dump(mode="json") for o in normalize_observations(observations_raw)]

    devices = merge_devices(devices_raw, observations, stale_after_seconds=cfg.stale_after_seconds)
    for device in devices:
        db.upsert_device(device)
    for obs in observations:
        db.upsert_observation(Observation.model_validate(obs))

    # Classification first (no VLAN assignment here)
    classifications = classify_inventory(devices, observations)
    for clf in classifications:
        db.upsert_classification(clf)

    # Policy second — recommended segment only, simulated application
    decisions = evaluate_all(devices, classifications)
    updated_devices: list[Device] = []
    for device, decision in zip(devices, decisions, strict=True):
        db.upsert_policy_decision(decision)
        simulated = apply_recommended_segment_simulated(device, decision)
        db.upsert_device(simulated)
        updated_devices.append(simulated)

    # Topology
    topo_path = synth / "lab-topology.json"
    extra_edges: list[dict[str, Any]] = []
    if topo_path.is_file():
        topo = _load_json(topo_path)
        extra_edges = topo.get("edges", [])
        # Optional explicit node positions
        pos = {n["device_id"]: n for n in topo.get("nodes", []) if "device_id" in n}
    else:
        pos = {}

    device_dicts = [d.model_dump(mode="json") for d in updated_devices]
    for d in device_dicts:
        if d["device_id"] in pos:
            d["node_type"] = pos[d["device_id"]].get("node_type", d.get("device_class_hint"))
    nodes, edges = build_topology_from_lab(
        device_dicts,
        [c.model_dump(mode="json") for c in classifications],
        extra_edges,
    )
    # Apply illustrative positions from topology file when present
    for node in nodes:
        meta = pos.get(node.device_id)
        if meta:
            data = node.model_dump()
            data["x"] = meta.get("x", 0.0)
            data["y"] = meta.get("y", 0.0)
            data["z"] = meta.get("z", 0.0)
            data["node_type"] = meta.get("node_type", data["node_type"])
            node = type(node).model_validate(data)
        db.upsert_node(node)
    for edge in edges:
        db.upsert_edge(edge)

    # Services
    services_path = synth / "services.json"
    if services_path.is_file():
        svc_raw = _load_json(services_path)
        if isinstance(svc_raw, dict):
            svc_raw = svc_raw.get("services", [])
        for svc in normalize_services(svc_raw):
            db.upsert_service(svc)

    # Optional event streams as historical events
    for name in ("radius-events.jsonl", "wireless-metrics.jsonl", "policy-events.jsonl"):
        path = synth / name
        if not path.is_file():
            continue
        for row in _load_jsonl(path):
            from secure_network_segmentation_lab.enums import EventType
            from secure_network_segmentation_lab.events import make_event

            et = row.get("event_type", "device_seen")
            try:
                event_type = EventType(et)
            except ValueError:
                event_type = EventType.DEVICE_SEEN
            ev = make_event(
                event_type,
                row.get("message", name),
                device_id=row.get("device_id"),
                payload=row,
            )
            db.insert_event(ev)

    return db
