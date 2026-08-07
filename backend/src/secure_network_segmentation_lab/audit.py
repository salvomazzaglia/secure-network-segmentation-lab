"""Audit log helpers."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.database import Database
from secure_network_segmentation_lab.models import AuditRecord, utc_now

ACTOR = "SYNTHETIC-OPERATOR"


def make_audit(
    action: str,
    details: dict[str, Any] | None = None,
    *,
    actor: str = ACTOR,
) -> AuditRecord:
    return AuditRecord(
        audit_id=f"aud-{uuid4().hex[:12]}",
        action=action,
        actor=actor,
        timestamp_utc=utc_now(),
        details=details or {},
        synthetic=True,
        note="SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED",
    )


def store_audit(db: Database, record: AuditRecord) -> AuditRecord:
    db.insert_audit(record)
    return record


def list_audit(db: Database, limit: int = 500) -> list[dict[str, Any]]:
    return db.list_audit(limit=limit)
