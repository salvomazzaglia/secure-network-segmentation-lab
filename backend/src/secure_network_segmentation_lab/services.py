"""Service overlay with provenance — port→category hint only."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.config import load_service_catalog
from secure_network_segmentation_lab.enums import Provenance, ServiceCategory
from secure_network_segmentation_lab.models import ServiceObservation, utc_now


def category_for_port(port: int | str | None) -> ServiceCategory:
    catalog = load_service_catalog()
    hints = catalog.get("port_hints") or {}
    if port is None:
        return ServiceCategory.UNKNOWN
    key = str(port)
    cat = hints.get(key)
    if cat and cat in {c.value for c in ServiceCategory}:
        return ServiceCategory(cat)
    return ServiceCategory.UNKNOWN


def make_service_observation(
    device_id: str,
    *,
    port: int | None = None,
    protocol: str = "tcp",
    category: ServiceCategory | str | None = None,
    provenance: Provenance | str = Provenance.SYNTHETIC,
    detail: str | None = None,
) -> ServiceObservation:
    if category is None:
        category = category_for_port(port)
    if isinstance(category, str):
        category = ServiceCategory(category)
    if isinstance(provenance, str):
        provenance = Provenance(provenance)
    return ServiceObservation(
        service_id=f"svc-{uuid4().hex[:12]}",
        device_id=device_id,
        port=port,
        protocol=protocol,
        category=category,
        provenance=provenance,
        observed_at_utc=utc_now(),
        detail=detail or f"Port {port} → category hint {category.value} (no product inference)",
        note="Port maps to category hint only; no product inference.",
    )


def normalize_services(items: list[dict[str, Any]]) -> list[ServiceObservation]:
    out: list[ServiceObservation] = []
    for item in items:
        cat = item.get("category")
        if cat is None and item.get("port") is not None:
            cat = category_for_port(item["port"]).value
        out.append(
            ServiceObservation(
                service_id=item.get("service_id") or f"svc-{uuid4().hex[:12]}",
                device_id=item["device_id"],
                port=item.get("port"),
                protocol=item.get("protocol", "tcp"),
                category=ServiceCategory(cat or "unknown"),
                provenance=Provenance(item.get("provenance", "synthetic")),
                observed_at_utc=item.get("observed_at_utc") or utc_now(),
                detail=item.get("detail"),
            )
        )
    return out
