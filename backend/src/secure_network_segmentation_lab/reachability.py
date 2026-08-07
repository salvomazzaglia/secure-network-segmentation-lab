"""Logical reachability evaluation — intended policy only, no firewall checks."""

from __future__ import annotations

from typing import Any

from secure_network_segmentation_lab.config import (
    load_reachability_policy_raw,
    validate_policy_structure,
)
from secure_network_segmentation_lab.enums import ReachabilityDecision
from secure_network_segmentation_lab.models import ReachabilityResult
from secure_network_segmentation_lab.policy_validation import validate_reachability_policy


def load_reachability_policy() -> dict[str, Any]:
    raw = load_reachability_policy_raw()
    validate_policy_structure(raw, "reachability")
    validate_reachability_policy(raw)
    return raw


def _rule_matches(rule: dict[str, Any], source: str, destination: str, service: str) -> bool:
    src = rule.get("source")
    dst = rule.get("destination")
    svc = rule.get("service")
    if src not in {source, "any"}:
        return False
    if dst not in {destination, "any"}:
        return False
    if svc not in {service, "any"}:
        return False
    return True


def evaluate_reachability(
    source_segment: str,
    destination_segment: str,
    service: str,
    *,
    policy: dict[str, Any] | None = None,
) -> ReachabilityResult:
    policy = policy or load_reachability_policy()
    version = str(policy.get("version", "1.0.0"))
    rules = sorted(policy.get("rules", []), key=lambda r: int(r.get("precedence", 9999)))

    # Quarantine isolation emphasis in explanations
    for rule in rules:
        if _rule_matches(rule, source_segment, destination_segment, service):
            decision = ReachabilityDecision(rule["decision"])
            explanation = (
                f"{source_segment} → {service} → {destination_segment}: "
                f"{decision.value} by {rule['id']} — {rule.get('description', '')}"
            )
            return ReachabilityResult(
                source_segment=source_segment,
                destination_segment=destination_segment,
                service=service,
                decision=decision,
                matched_rule=rule["id"],
                explanation=explanation,
                policy_version=version,
            )

    default = ReachabilityDecision(policy.get("default_decision", "denied"))
    explanation = (
        f"{source_segment} → {service} → {destination_segment}: "
        f"{default.value} (default; no rule matched)"
    )
    if source_segment == "quarantine":
        explanation += " — quarantine isolation model (SIMULATED, not enforced)"
    return ReachabilityResult(
        source_segment=source_segment,
        destination_segment=destination_segment,
        service=service,
        decision=default,
        matched_rule=None,
        explanation=explanation,
        policy_version=version,
    )


def evaluate_matrix(
    sources: list[str],
    destinations: list[str],
    services: list[str],
    *,
    policy: dict[str, Any] | None = None,
) -> list[ReachabilityResult]:
    policy = policy or load_reachability_policy()
    results: list[ReachabilityResult] = []
    for src in sources:
        for dst in destinations:
            for svc in services:
                results.append(evaluate_reachability(src, dst, svc, policy=policy))
    return results
