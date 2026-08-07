"""Event store helpers."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.database import Database
from secure_network_segmentation_lab.enums import EventType
from secure_network_segmentation_lab.models import Event, utc_now


def make_event(
    event_type: EventType | str,
    message: str,
    *,
    device_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Event:
    if isinstance(event_type, str):
        event_type = EventType(event_type)
    return Event(
        event_id=f"evt-{uuid4().hex[:12]}",
        event_type=event_type,
        device_id=device_id,
        timestamp_utc=utc_now(),
        message=message,
        payload=payload or {},
        synthetic=True,
        change_label="PROPOSED / SIMULATED — NOT APPLIED",
    )


def store_event(db: Database, event: Event) -> Event:
    db.insert_event(event)
    return event


def list_events(db: Database, limit: int = 500) -> list[dict[str, Any]]:
    return db.list_events(limit=limit)
