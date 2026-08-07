"""Topology nodes and edges with provenance. No cable-length estimation."""

from __future__ import annotations

from typing import Any

from secure_network_segmentation_lab.enums import (
    ConnectionType,
    EdgeType,
    Provenance,
    SecurityState,
)
from secure_network_segmentation_lab.models import TopologyEdge, TopologyNode

CABLE_NOTE = (
    "The position and edge length are normalized for visualization. "
    "No physical cable-length estimation is performed."
)


def make_node(
    device: dict[str, Any],
    *,
    classification_confidence: float | None = None,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> TopologyNode:
    device_id = device["device_id"]
    return TopologyNode(
        node_id=f"node-{device_id}",
        device_id=device_id,
        node_type=str(device.get("device_class_hint") or device.get("node_type") or "endpoint"),
        label=device.get("alias") or device_id,
        segment=device.get("current_segment") or "quarantine",
        device_class=device.get("device_class_hint") or device.get("predicted_class") or "unknown",
        classification_confidence=classification_confidence,
        connection_type=ConnectionType(device.get("connection_type") or "unknown"),
        security_state=SecurityState(device.get("security_state") or "uncertain"),
        online=bool(device.get("online", True)),
        last_seen=device.get("last_seen_utc"),
        metadata_source=Provenance(device.get("provenance") or "synthetic"),
        position_source="illustrative",
        x=x,
        y=y,
        z=z,
        note=CABLE_NOTE,
    )


def make_edge(
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    edge_type: EdgeType | str,
    *,
    provenance: Provenance | str = Provenance.SYNTHETIC,
    label: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> TopologyEdge:
    if isinstance(edge_type, str):
        edge_type = EdgeType(edge_type)
    if isinstance(provenance, str):
        provenance = Provenance(provenance)
    return TopologyEdge(
        edge_id=edge_id,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_type=edge_type,
        provenance=provenance,
        label=label,
        metadata=metadata or {},
        note=CABLE_NOTE,
    )


def wired_path_edges(
    device_node: str,
    edge_switch_node: str,
    core_switch_node: str,
    firewall_node: str,
    *,
    port_id: str | None = None,
) -> list[TopologyEdge]:
    """device → edge switch → core → firewall. Visualization only."""
    meta = {"port_id": port_id} if port_id else {}
    return [
        make_edge(
            f"wired-{device_node}-{edge_switch_node}",
            device_node,
            edge_switch_node,
            EdgeType.WIRED,
            label="access",
            metadata=meta,
        ),
        make_edge(
            f"uplink-{edge_switch_node}-{core_switch_node}",
            edge_switch_node,
            core_switch_node,
            EdgeType.LOGICAL_UPSTREAM,
            label="uplink",
        ),
        make_edge(
            f"uplink-{core_switch_node}-{firewall_node}",
            core_switch_node,
            firewall_node,
            EdgeType.LOGICAL_UPSTREAM,
            label="core-to-fw",
        ),
    ]


def build_topology_from_lab(
    devices: list[dict[str, Any]],
    classifications: list[dict[str, Any]] | None = None,
    extra_edges: list[dict[str, Any]] | None = None,
) -> tuple[list[TopologyNode], list[TopologyEdge]]:
    conf_by_id = {
        c["device_id"]: c.get("confidence") for c in (classifications or []) if "device_id" in c
    }
    nodes = [
        make_node(d, classification_confidence=conf_by_id.get(d["device_id"])) for d in devices
    ]
    edges: list[TopologyEdge] = []
    for raw in extra_edges or []:
        edges.append(
            make_edge(
                raw["edge_id"],
                raw["source_node_id"],
                raw["target_node_id"],
                raw["edge_type"],
                provenance=raw.get("provenance", "synthetic"),
                label=raw.get("label"),
                metadata=raw.get("metadata"),
            )
        )
    return nodes, edges
