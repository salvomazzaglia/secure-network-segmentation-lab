"""FastAPI application — synthetic lab API. Default bind 127.0.0.1."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from secure_network_segmentation_lab import __version__
from secure_network_segmentation_lab.adapters import build_all_plans, build_plan
from secure_network_segmentation_lab.approval import record_approval
from secure_network_segmentation_lab.audit import make_audit, store_audit
from secure_network_segmentation_lab.config import load_app_config
from secure_network_segmentation_lab.database import Database, open_database
from secure_network_segmentation_lab.drift import detect_drift
from secure_network_segmentation_lab.enums import ApprovalDecision, EventType, SourceMode
from secure_network_segmentation_lab.events import make_event, store_event
from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab
from secure_network_segmentation_lab.models import Device
from secure_network_segmentation_lab.paths import database_path
from secure_network_segmentation_lab.reachability import evaluate_reachability
from secure_network_segmentation_lab.simulator import (
    reset_simulation_events,
    simulate_run,
    simulate_step,
)
from secure_network_segmentation_lab.websocket import router as ws_router

logger = logging.getLogger("snsl.api")

_db: Database | None = None
_source_mode: SourceMode = SourceMode.SYNTHETIC


class ApprovalRequest(BaseModel):
    device_id: str
    decision: ApprovalDecision
    synthetic: bool = True
    recommended_segment: str | None = None
    chosen_segment: str | None = None
    policy_id: str | None = None
    justification: str = ""


def get_db() -> Database:
    global _db
    if _db is None:
        cfg = load_app_config("demo.config.json")
        _db = open_database(database_path(cfg.database_path))
    return _db


def create_app(*, bootstrap: bool = False) -> FastAPI:
    app = FastAPI(
        title="Secure Network Segmentation Lab",
        version=__version__,
        description="Synthetic offline segmentation lab — PROPOSED / SIMULATED — NOT APPLIED",
    )
    app.include_router(ws_router)

    @app.on_event("startup")
    def _startup() -> None:
        global _db, _source_mode
        cfg = load_app_config("demo.config.json")
        _source_mode = cfg.source_mode
        if bootstrap:
            _db = bootstrap_lab(config_name="demo.config.json")
        else:
            _db = open_database(database_path(cfg.database_path))
            if not _db.list_devices():
                _db = bootstrap_lab(config_name="demo.config.json")

    @app.get("/api/v1/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "synthetic": True,
            "note": "PROPOSED / SIMULATED — NOT APPLIED",
        }

    @app.get("/api/v1/lab")
    def lab() -> dict[str, Any]:
        db = get_db()
        return {
            "version": __version__,
            "source_mode": db.get_meta("source_mode", "synthetic"),
            "device_count": len(db.list_devices()),
            "segment_count": len(db.list_segments()),
            "warnings": [
                "PROPOSED / SIMULATED — NOT APPLIED",
                "SYNTHETIC DEMONSTRATION DATA",
            ],
        }

    @app.get("/api/v1/devices")
    def devices() -> list[dict[str, Any]]:
        return get_db().list_devices()

    @app.get("/api/v1/devices/{device_id}")
    def device_detail(device_id: str) -> dict[str, Any]:
        db = get_db()
        device = db.get_device(device_id)
        if not device:
            raise HTTPException(404, "Device not found")
        return {
            "device": device,
            "classification": db.get_classification(device_id),
            "observations": db.list_observations(device_id),
            "services": [s for s in db.list_services() if s.get("device_id") == device_id],
            "note": "Classification is separate from VLAN/segment assignment.",
        }

    @app.get("/api/v1/segments")
    def segments() -> list[dict[str, Any]]:
        return get_db().list_segments()

    @app.get("/api/v1/topology")
    def topology() -> dict[str, Any]:
        db = get_db()
        return {
            "nodes": db.list_nodes(),
            "edges": db.list_edges(),
            "note": (
                "The position and edge length are normalized for visualization. "
                "No physical cable-length estimation is performed."
            ),
        }

    @app.get("/api/v1/classifications")
    def classifications() -> list[dict[str, Any]]:
        return get_db().list_classifications()

    @app.get("/api/v1/policy/decisions")
    def policy_decisions() -> list[dict[str, Any]]:
        return get_db().list_policy_decisions()

    @app.get("/api/v1/reachability")
    def reachability(
        source: str = Query(...),
        destination: str = Query(...),
        service: str = Query("any"),
    ) -> dict[str, Any]:
        result = evaluate_reachability(source, destination, service)
        return result.model_dump(mode="json")

    @app.get("/api/v1/drift")
    def drift() -> list[dict[str, Any]]:
        db = get_db()
        findings = detect_drift(
            db.list_devices(),
            db.list_classifications(),
            db.list_policy_decisions(),
            node_ids={n["node_id"] for n in db.list_nodes()},
        )
        return [f.model_dump(mode="json") for f in findings]

    @app.get("/api/v1/events")
    def events(limit: int = 100) -> list[dict[str, Any]]:
        return get_db().list_events(limit=limit)

    @app.get("/api/v1/audit")
    def audit(limit: int = 100) -> list[dict[str, Any]]:
        return get_db().list_audit(limit=limit)

    @app.get("/api/v1/adapters")
    def adapters(adapter_id: str | None = None) -> Any:
        if adapter_id:
            try:
                return build_plan(adapter_id).model_dump(mode="json")
            except KeyError as exc:
                raise HTTPException(404, str(exc)) from exc
        return [p.model_dump(mode="json") for p in build_all_plans()]

    @app.post("/api/v1/simulation/reset")
    def simulation_reset() -> dict[str, Any]:
        db = get_db()
        reset_simulation_events(db)
        store_audit(db, make_audit("simulation_reset", {"synthetic": True}))
        return {"status": "reset", "note": "PROPOSED / SIMULATED — NOT APPLIED"}

    @app.post("/api/v1/simulation/step")
    def simulation_step(
        scenario: str = "normal",
        seed: int = 42,
        step_index: int = 0,
    ) -> dict[str, Any]:
        events = simulate_step(get_db(), scenario=scenario, seed=seed, step_index=step_index)
        return {"events": events, "note": "PROPOSED / SIMULATED — NOT APPLIED"}

    @app.post("/api/v1/simulation/run")
    def simulation_run(
        scenario: str = "mixed",
        seed: int = 42,
        duration_steps: int = 10,
        speed: float = 1.0,
    ) -> dict[str, Any]:
        events = simulate_run(
            get_db(),
            scenario=scenario,
            seed=seed,
            duration_steps=duration_steps,
            speed=speed,
        )
        return {
            "events": events,
            "count": len(events),
            "note": "PROPOSED / SIMULATED — NOT APPLIED",
        }

    @app.post("/api/v1/approvals")
    def approvals(payload: ApprovalRequest) -> dict[str, Any]:
        if not payload.synthetic:
            raise HTTPException(400, "synthetic=true is required")
        if _source_mode != SourceMode.SYNTHETIC:
            raise HTTPException(400, "Approvals rejected when source_mode != synthetic")
        db = get_db()
        device_raw = db.get_device(payload.device_id)
        if not device_raw:
            raise HTTPException(404, "Device not found")
        try:
            approval, updated = record_approval(
                Device.model_validate(device_raw),
                payload.decision,
                source_mode=_source_mode,
                synthetic=True,
                recommended_segment=payload.recommended_segment,
                chosen_segment=payload.chosen_segment,
                policy_id=payload.policy_id,
                justification=payload.justification,
            )
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        db.insert_approval(approval)
        db.upsert_device(updated)
        store_audit(
            db,
            make_audit(
                "approval_recorded",
                {"approval_id": approval.approval_id, "device_id": payload.device_id},
            ),
        )
        store_event(
            db,
            make_event(
                EventType.APPROVAL_RECORDED,
                f"Approval {payload.decision.value} for {payload.device_id}",
                device_id=payload.device_id,
                payload=approval.model_dump(mode="json"),
            ),
        )
        return {
            "approval": approval.model_dump(mode="json"),
            "device": updated.model_dump(mode="json"),
            "note": "SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED",
        }

    return app


def warn_if_non_localhost(host: str) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        msg = (
            f"WARNING: Binding to {host} exposes the synthetic lab API beyond localhost. "
            "Default is 127.0.0.1. No authentication is enabled."
        )
        print(msg)
        logger.warning(msg)


def run_server(host: str = "127.0.0.1", port: int = 8765, *, bootstrap: bool = True) -> None:
    import uvicorn

    warn_if_non_localhost(host)
    app = create_app(bootstrap=bootstrap)
    uvicorn.run(app, host=host, port=port, log_level="info")
