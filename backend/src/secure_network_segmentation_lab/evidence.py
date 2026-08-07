"""Evidence item helpers for explainable classification."""

from __future__ import annotations

from secure_network_segmentation_lab.enums import Provenance
from secure_network_segmentation_lab.models import EvidenceItem


def make_evidence(
    key: str,
    label: str,
    weight: float,
    contribution: float,
    detail: str,
    provenance: Provenance = Provenance.SYNTHETIC,
) -> EvidenceItem:
    return EvidenceItem(
        key=key,
        label=label,
        weight=round(weight, 4),
        contribution=round(contribution, 4),
        detail=detail,
        provenance=provenance,
    )


# Alias used by alternate call sites
def evidence(
    source: str,
    weight: float,
    score: float,
    detail: str,
    provenance: Provenance = Provenance.SYNTHETIC,
) -> EvidenceItem:
    contribution = max(0.0, min(1.0, weight * score))
    return make_evidence(source, source, weight, contribution, detail, provenance)


def evidence_to_dict(item: EvidenceItem) -> dict[str, object]:
    return item.model_dump(mode="json")


def summarize_evidence(items: list[EvidenceItem]) -> str:
    if not items:
        return "No evidence available."
    parts = [f"{e.label}={e.contribution:.2f} (w={e.weight:.2f})" for e in items]
    return "Why classified? " + "; ".join(parts)


def why_classified(items: list[EvidenceItem]) -> list[dict[str, float | str]]:
    return [
        {
            "source": item.key,
            "weight": item.weight,
            "contribution": item.contribution,
            "detail": item.detail,
            "provenance": item.provenance.value,
        }
        for item in items
    ]
