"""Policy validation: unique IDs, known classes/segments, no executable values."""

from __future__ import annotations

from typing import Any

from secure_network_segmentation_lab.config import (
    PolicyConfigError,
    load_device_classes,
    load_segments,
)


def _known_segments() -> set[str]:
    data = load_segments()
    return {s["segment_id"] for s in data.get("segments", [])}


def _known_classes() -> set[str]:
    return set(load_device_classes())


def validate_segmentation_policy(raw: dict[str, Any]) -> None:
    from secure_network_segmentation_lab.config import validate_policy_structure

    if raw.get("implicit_default_permit") is True:
        raise PolicyConfigError("implicit_default_permit must be false")
    if raw.get("default_decision") in {"permit", "allow", "allowed"}:
        raise PolicyConfigError("implicit default permit rejected; use no_match/denied")

    validate_policy_structure(raw, "segmentation")

    classes = _known_classes()
    segments = _known_segments()
    rules = raw.get("rules") or []
    ids: list[str] = []
    transitions: list[tuple[str, str]] = []

    for rule in rules:
        rid = rule.get("id")
        if not rid:
            raise PolicyConfigError("segmentation rule missing id")
        ids.append(rid)
        if "precedence" not in rule:
            raise PolicyConfigError(f"{rid}: missing precedence")
        match = rule.get("match") or {}
        if "device_class" in match and match["device_class"] not in classes:
            raise PolicyConfigError(f"{rid}: unknown device_class {match['device_class']}")
        rec = rule.get("recommend_segment")
        if rec and rec not in segments:
            raise PolicyConfigError(f"{rid}: unknown recommend_segment {rec}")
        src = match.get("source_segment")
        dst = match.get("destination_segment")
        if src and src not in segments:
            raise PolicyConfigError(f"{rid}: unknown source_segment {src}")
        if dst and dst not in segments:
            raise PolicyConfigError(f"{rid}: unknown destination_segment {dst}")
        if src and dst:
            transitions.append((src, dst))
        for key in ("confidence_minimum", "confidence_maximum"):
            if key in match:
                val = float(match[key])
                if not 0.0 <= val <= 1.0:
                    raise PolicyConfigError(f"{rid}: {key} out of range")

    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise PolicyConfigError(f"duplicate segmentation rule IDs: {dupes}")

    # Detect trivial circular transition pairs A→B and B→A both deny/keep loops
    # as structural circular transitions when both directions appear as transition rules.
    pair_set = set(transitions)
    for a, b in transitions:
        if a == b:
            continue
        if (b, a) in pair_set and a < b:
            # Informational structural note — only fail if identical bidirectional
            # recommend loops without quarantine escape (conservative check).
            pass
    # Explicit circular self-transition with recommend back to same via deny is OK;
    # reject A→B recommend and B→A recommend forming a cycle of recommend_move.
    rec_edges: list[tuple[str, str]] = []
    for rule in rules:
        match = rule.get("match") or {}
        src = match.get("source_segment")
        rec = rule.get("recommend_segment")
        decision = rule.get("decision")
        if src and rec and decision in {"recommend_move", "require_approval"} and src != rec:
            rec_edges.append((src, rec))
    # DFS cycle detection on recommend graph
    graph: dict[str, list[str]] = {}
    for a, b in rec_edges:
        graph.setdefault(a, []).append(b)

    def _has_cycle() -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for nxt in graph.get(node, []):
                if dfs(nxt):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(dfs(n) for n in list(graph))

    if _has_cycle():
        raise PolicyConfigError("circular segment transition recommendations detected")


def validate_reachability_policy(raw: dict[str, Any]) -> None:
    if raw.get("implicit_default_permit") is True:
        raise PolicyConfigError("implicit_default_permit must be false")
    if str(raw.get("default_decision", "")).lower() in {"permit", "allow", "allowed"}:
        raise PolicyConfigError("reachability default must not be permit")

    segments = _known_segments() | {"any", "internet"}
    rules = raw.get("rules") or []
    ids: list[str] = []
    for rule in rules:
        rid = rule.get("id")
        if not rid:
            raise PolicyConfigError("reachability rule missing id")
        ids.append(rid)
        src = rule.get("source")
        dst = rule.get("destination")
        if src not in segments:
            raise PolicyConfigError(f"{rid}: unknown source {src}")
        if dst not in segments:
            raise PolicyConfigError(f"{rid}: unknown destination {dst}")
        if rule.get("decision") not in {"allowed", "denied", "conditional", "unknown"}:
            raise PolicyConfigError(f"{rid}: invalid decision")
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise PolicyConfigError(f"duplicate reachability rule IDs: {dupes}")
