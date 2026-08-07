"""Deterministic seeded synthetic event simulation — no real network I/O."""

from __future__ import annotations

import random
from typing import Any

from secure_network_segmentation_lab.database import Database
from secure_network_segmentation_lab.enums import EventType, SimulationScenario
from secure_network_segmentation_lab.events import make_event, store_event
from secure_network_segmentation_lab.wireless import bucket_from_rssi

CHANGE_LABEL = "PROPOSED / SIMULATED — NOT APPLIED"


def _pick_device(rng: random.Random, devices: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not devices:
        return None
    return rng.choice(devices)


def simulate_step(
    db: Database,
    *,
    scenario: SimulationScenario | str = SimulationScenario.NORMAL,
    seed: int = 42,
    step_index: int = 0,
) -> list[dict[str, Any]]:
    if isinstance(scenario, str):
        scenario = SimulationScenario(scenario)
    rng = random.Random(seed + step_index * 997)
    devices = db.list_devices()
    emitted: list[dict[str, Any]] = []

    def emit(
        event_type: EventType, message: str, device_id: str | None = None, **payload: Any
    ) -> None:
        ev = make_event(
            event_type,
            message,
            device_id=device_id,
            payload={**payload, "change_label": CHANGE_LABEL, "scenario": scenario.value},
        )
        store_event(db, ev)
        emitted.append(ev.model_dump(mode="json"))

    if scenario == SimulationScenario.NORMAL:
        d = _pick_device(rng, devices)
        if d:
            emit(EventType.DEVICE_SEEN, f"Device seen: {d['device_id']}", d["device_id"])
    elif scenario == SimulationScenario.NEW_DEVICE:
        new_id = f"SYNTHETIC-NEW-{seed}-{step_index:03d}"
        emit(
            EventType.DEVICE_SEEN,
            f"New synthetic device observed: {new_id}",
            new_id,
            segment="quarantine",
        )
        emit(
            EventType.QUARANTINE_RECOMMENDED,
            f"Quarantine recommended for {new_id}",
            new_id,
        )
        emit(
            EventType.APPROVAL_REQUESTED,
            f"Approval requested for {new_id}",
            new_id,
        )
    elif scenario == SimulationScenario.QUARANTINE:
        candidates = [d for d in devices if d.get("current_segment") == "quarantine"] or devices
        d = _pick_device(rng, candidates)
        if d:
            emit(EventType.QUARANTINE_RECOMMENDED, "Quarantine isolation reminder", d["device_id"])
            emit(
                EventType.POLICY_DECISION_CREATED, "Policy decision for quarantine", d["device_id"]
            )
    elif scenario == SimulationScenario.ROAMING:
        wireless = [d for d in devices if d.get("connection_type") == "wireless"] or devices
        d = _pick_device(rng, wireless)
        if d:
            aps = ["SYNTHETIC-AP-01", "SYNTHETIC-AP-02", "SYNTHETIC-AP-03"]
            new_ap = rng.choice(aps)
            rssi = rng.randint(-80, -45)
            emit(
                EventType.AP_ASSOCIATION_CHANGED,
                f"{d['device_id']} associated to {new_ap}",
                d["device_id"],
                ap_id=new_ap,
            )
            emit(
                EventType.SIGNAL_CHANGED,
                f"Signal bucket {bucket_from_rssi(rssi).value}",
                d["device_id"],
                rssi=rssi,
                signal_bucket=bucket_from_rssi(rssi).value,
                note="Illustrative wireless position — not physical localization",
            )
    elif scenario == SimulationScenario.POLICY_DRIFT:
        d = _pick_device(rng, devices)
        if d:
            emit(
                EventType.POLICY_VIOLATION_DETECTED,
                f"Simulated policy drift on {d['device_id']}",
                d["device_id"],
            )
            emit(
                EventType.CLASSIFICATION_UNCERTAIN,
                f"Classification uncertain for {d['device_id']}",
                d["device_id"],
            )
    elif scenario == SimulationScenario.MIXED:
        # Deterministically cycle sub-scenarios
        sub = [
            SimulationScenario.NORMAL,
            SimulationScenario.ROAMING,
            SimulationScenario.QUARANTINE,
            SimulationScenario.POLICY_DRIFT,
            SimulationScenario.NEW_DEVICE,
        ][step_index % 5]
        return simulate_step(db, scenario=sub, seed=seed, step_index=step_index)

    return emitted


def simulate_run(
    db: Database,
    *,
    scenario: SimulationScenario | str = SimulationScenario.MIXED,
    seed: int = 42,
    duration_steps: int = 10,
    speed: float = 1.0,
) -> list[dict[str, Any]]:
    """Run N deterministic steps. ``speed`` is recorded only (no sleeps required)."""
    all_events: list[dict[str, Any]] = []
    for i in range(duration_steps):
        step_events = simulate_step(db, scenario=scenario, seed=seed, step_index=i)
        for ev in step_events:
            ev["sim_speed"] = speed
        all_events.extend(step_events)
    return all_events


def reset_simulation_events(db: Database) -> None:
    """Clear events table for a clean simulation (devices retained)."""
    with db.connection() as conn:
        conn.execute("DELETE FROM events")
