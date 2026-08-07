"""SQLite schema and CRUD for the synthetic lab store."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from secure_network_segmentation_lab.paths import database_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS segments (
  segment_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
  device_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  last_seen_utc TEXT,
  current_segment TEXT,
  online INTEGER
);

CREATE TABLE IF NOT EXISTS observations (
  observation_id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL,
  observed_at_utc TEXT,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS classifications (
  device_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  generated_at_utc TEXT
);

CREATE TABLE IF NOT EXISTS policy_decisions (
  device_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  generated_at_utc TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
  approval_id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at_utc TEXT
);

CREATE TABLE IF NOT EXISTS topology_nodes (
  node_id TEXT PRIMARY KEY,
  device_id TEXT,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topology_edges (
  edge_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS services (
  service_id TEXT PRIMARY KEY,
  device_id TEXT,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT,
  timestamp_utc TEXT,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  audit_id TEXT PRIMARY KEY,
  timestamp_utc TEXT,
  payload TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_observations_device ON observations(device_id);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_approvals_device ON approvals(device_id);
"""


def _dumps(obj: Any) -> str:
    if hasattr(obj, "model_dump"):
        data = obj.model_dump(mode="json")
    elif isinstance(obj, dict):
        data = obj
    else:
        data = dict(obj)
    return json.dumps(data, default=str, sort_keys=True)


def _loads(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object in database payload")
    return data


class Database:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def set_meta(self, key: str, value: str) -> None:
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_meta(self, key: str, default: str | None = None) -> str | None:
        with self.connection() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            return row["value"] if row else default

    def clear_all(self) -> None:
        tables = [
            "devices",
            "observations",
            "classifications",
            "policy_decisions",
            "approvals",
            "segments",
            "topology_nodes",
            "topology_edges",
            "services",
            "events",
            "audit_log",
        ]
        with self.connection() as conn:
            for table in tables:
                conn.execute(f"DELETE FROM {table}")

    # --- devices ---
    def upsert_device(self, device: Any) -> None:
        payload = _dumps(device)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO devices(device_id, payload, last_seen_utc, current_segment, online) "
                "VALUES(?,?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET "
                "payload=excluded.payload, last_seen_utc=excluded.last_seen_utc, "
                "current_segment=excluded.current_segment, online=excluded.online",
                (
                    data["device_id"],
                    payload,
                    data.get("last_seen_utc"),
                    data.get("current_segment"),
                    1 if data.get("online", True) else 0,
                ),
            )

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT payload FROM devices WHERE device_id=?", (device_id,)
            ).fetchone()
            return _loads(row["payload"]) if row else None

    def list_devices(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM devices ORDER BY device_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- observations ---
    def upsert_observation(self, observation: Any) -> None:
        payload = _dumps(observation)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO observations(observation_id, device_id, observed_at_utc, payload) "
                "VALUES(?,?,?,?) ON CONFLICT(observation_id) DO UPDATE SET "
                "payload=excluded.payload, observed_at_utc=excluded.observed_at_utc, "
                "device_id=excluded.device_id",
                (
                    data["observation_id"],
                    data["device_id"],
                    data.get("observed_at_utc"),
                    payload,
                ),
            )

    def list_observations(self, device_id: str | None = None) -> list[dict[str, Any]]:
        with self.connection() as conn:
            if device_id:
                rows = conn.execute(
                    "SELECT payload FROM observations WHERE device_id=? ORDER BY observed_at_utc",
                    (device_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT payload FROM observations ORDER BY observed_at_utc"
                ).fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- classifications ---
    def upsert_classification(self, classification: Any) -> None:
        payload = _dumps(classification)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO classifications(device_id, payload, generated_at_utc) "
                "VALUES(?,?,?) ON CONFLICT(device_id) DO UPDATE SET "
                "payload=excluded.payload, generated_at_utc=excluded.generated_at_utc",
                (data["device_id"], payload, data.get("generated_at_utc")),
            )

    def list_classifications(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM classifications ORDER BY device_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    def get_classification(self, device_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT payload FROM classifications WHERE device_id=?", (device_id,)
            ).fetchone()
            return _loads(row["payload"]) if row else None

    # --- policy decisions ---
    def upsert_policy_decision(self, decision: Any) -> None:
        payload = _dumps(decision)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO policy_decisions(device_id, payload, generated_at_utc) "
                "VALUES(?,?,?) ON CONFLICT(device_id) DO UPDATE SET "
                "payload=excluded.payload, generated_at_utc=excluded.generated_at_utc",
                (data["device_id"], payload, data.get("generated_at_utc")),
            )

    def list_policy_decisions(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM policy_decisions ORDER BY device_id"
            ).fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- approvals ---
    def insert_approval(self, approval: Any) -> None:
        payload = _dumps(approval)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO approvals(approval_id, device_id, payload, created_at_utc) "
                "VALUES(?,?,?,?)",
                (
                    data["approval_id"],
                    data["device_id"],
                    payload,
                    data.get("created_at_utc"),
                ),
            )

    def list_approvals(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM approvals ORDER BY created_at_utc").fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- segments ---
    def upsert_segment(self, segment: Any) -> None:
        payload = _dumps(segment)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO segments(segment_id, payload) VALUES(?,?) "
                "ON CONFLICT(segment_id) DO UPDATE SET payload=excluded.payload",
                (data["segment_id"], payload),
            )

    def list_segments(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM segments ORDER BY segment_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- topology ---
    def upsert_node(self, node: Any) -> None:
        payload = _dumps(node)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO topology_nodes(node_id, device_id, payload) VALUES(?,?,?) "
                "ON CONFLICT(node_id) DO UPDATE SET payload=excluded.payload, "
                "device_id=excluded.device_id",
                (data["node_id"], data.get("device_id"), payload),
            )

    def upsert_edge(self, edge: Any) -> None:
        payload = _dumps(edge)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO topology_edges(edge_id, payload) VALUES(?,?) "
                "ON CONFLICT(edge_id) DO UPDATE SET payload=excluded.payload",
                (data["edge_id"], payload),
            )

    def list_nodes(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM topology_nodes ORDER BY node_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    def list_edges(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM topology_edges ORDER BY edge_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- services ---
    def upsert_service(self, service: Any) -> None:
        payload = _dumps(service)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO services(service_id, device_id, payload) VALUES(?,?,?) "
                "ON CONFLICT(service_id) DO UPDATE SET payload=excluded.payload, "
                "device_id=excluded.device_id",
                (data["service_id"], data.get("device_id"), payload),
            )

    def list_services(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT payload FROM services ORDER BY service_id").fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- events ---
    def insert_event(self, event: Any) -> None:
        payload = _dumps(event)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO events(event_id, event_type, timestamp_utc, payload) VALUES(?,?,?,?)",
                (
                    data["event_id"],
                    data.get("event_type"),
                    data.get("timestamp_utc"),
                    payload,
                ),
            )

    def list_events(self, limit: int = 500) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM events ORDER BY timestamp_utc DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [_loads(r["payload"]) for r in rows]

    # --- audit ---
    def insert_audit(self, record: Any) -> None:
        payload = _dumps(record)
        data = json.loads(payload)
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO audit_log(audit_id, timestamp_utc, payload) VALUES(?,?,?)",
                (data["audit_id"], data.get("timestamp_utc"), payload),
            )

    def list_audit(self, limit: int = 500) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT payload FROM audit_log ORDER BY timestamp_utc DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [_loads(r["payload"]) for r in rows]


def open_database(path: Path | str | None = None) -> Database:
    return Database(path)


def isoformat(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()
