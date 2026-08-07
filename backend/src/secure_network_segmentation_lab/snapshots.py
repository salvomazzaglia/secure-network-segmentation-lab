"""Lab snapshot export."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.database import Database
from secure_network_segmentation_lab.enums import SourceMode
from secure_network_segmentation_lab.models import (
    Classification,
    Device,
    DriftFinding,
    Event,
    LabSnapshot,
    PolicyDecisionResult,
    Segment,
    ServiceObservation,
    TopologyEdge,
    TopologyNode,
    utc_now,
)


def build_snapshot(db: Database, *, source_mode: SourceMode = SourceMode.SYNTHETIC) -> LabSnapshot:
    def map_list(rows: list[dict[str, Any]], model: type[Any]) -> list[Any]:
        validate = model.model_validate
        return [validate(r) for r in rows]

    return LabSnapshot(
        snapshot_id=f"snap-{uuid4().hex[:12]}",
        created_at_utc=utc_now(),
        version="1.0.0",
        source_mode=source_mode,
        devices=map_list(db.list_devices(), Device),
        classifications=map_list(db.list_classifications(), Classification),
        policy_decisions=map_list(db.list_policy_decisions(), PolicyDecisionResult),
        segments=map_list(db.list_segments(), Segment),
        nodes=map_list(db.list_nodes(), TopologyNode),
        edges=map_list(db.list_edges(), TopologyEdge),
        services=map_list(db.list_services(), ServiceObservation),
        events=map_list(db.list_events(limit=200), Event),
        drift=[],
        warnings=[
            "PROPOSED / SIMULATED — NOT APPLIED",
            "SYNTHETIC DEMONSTRATION DATA",
            "Version 1.0 never applies network changes.",
        ],
    )


def snapshot_to_dict(snapshot: LabSnapshot) -> dict[str, Any]:
    return snapshot.model_dump(mode="json")


def attach_drift(snapshot: LabSnapshot, findings: list[DriftFinding]) -> LabSnapshot:
    data = snapshot.model_dump()
    data["drift"] = [f.model_dump(mode="json") for f in findings]
    return LabSnapshot.model_validate(data)
