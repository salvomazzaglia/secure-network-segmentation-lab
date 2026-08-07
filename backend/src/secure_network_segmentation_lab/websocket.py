"""FastAPI WebSocket event stream at /ws/events."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from secure_network_segmentation_lab.database import Database

router = APIRouter()


class EventHub:
    def __init__(self) -> None:
        self._subscribers: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._subscribers.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._subscribers:
            self._subscribers.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in self._subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


hub = EventHub()


def get_hub() -> EventHub:
    return hub


@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    try:
        await websocket.send_json(
            {
                "type": "hello",
                "message": "SYNTHETIC event stream",
                "note": "PROPOSED / SIMULATED — NOT APPLIED",
            }
        )
        while True:
            # Keep-alive / client pings; ignore payloads
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except TimeoutError:
                await websocket.send_json({"type": "ping", "synthetic": True})
    except WebSocketDisconnect:
        hub.disconnect(websocket)


async def publish_db_events(db: Database, hub_: EventHub | None = None) -> int:
    """Push latest DB events to subscribers (best-effort)."""
    hub_ = hub_ or hub
    events = db.list_events(limit=20)
    for ev in reversed(events):
        await hub_.broadcast({"type": "event", "event": ev})
    return len(events)
