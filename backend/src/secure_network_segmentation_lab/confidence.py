"""Confidence normalization and status thresholds."""

from __future__ import annotations

from secure_network_segmentation_lab.config import ConfidenceThresholds
from secure_network_segmentation_lab.enums import ClassificationStatus


def normalize_scores(raw: dict[str, float]) -> dict[str, float]:
    """Normalize non-negative weighted scores so they sum to 1.0 (or empty)."""
    cleaned = {k: max(0.0, float(v)) for k, v in raw.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return {k: 0.0 for k in cleaned}
    return {k: v / total for k, v in cleaned.items()}


def status_for_confidence(
    confidence: float,
    thresholds: ConfidenceThresholds | None = None,
) -> ClassificationStatus:
    thresholds = thresholds or ConfidenceThresholds()
    if confidence >= thresholds.classified:
        return ClassificationStatus.CLASSIFIED
    if confidence >= thresholds.uncertain:
        return ClassificationStatus.UNCERTAIN
    return ClassificationStatus.UNKNOWN


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
