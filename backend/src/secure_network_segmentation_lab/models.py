"""Pydantic domain models for the Secure Network Segmentation Lab."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from secure_network_segmentation_lab.enums import (
    ApprovalDecision,
    ClassificationStatus,
    ConnectionType,
    DeviceClass,
    DriftSeverity,
    EdgeType,
    EventType,
    PolicyDecision,
    PrivacyMode,
    Provenance,
    ReachabilityDecision,
    SecurityState,
    ServiceCategory,
    SignalBucket,
    SourceMode,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class ConfidenceThresholds(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classified: float = 0.80
    uncertain: float = 0.60


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str = "1.0.0"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    bind_host: str = "127.0.0.1"
    bind_port: int = 8765
    privacy_mode: PrivacyMode = PrivacyMode.MASKED
    database_path: str = "runtime/lab.sqlite3"
    synthetic_seed: int = 42
    confidence_thresholds: ConfidenceThresholds = Field(default_factory=ConfidenceThresholds)
    stale_after_seconds: int = 86400
    approval_stale_after_seconds: int = 604800
    warnings: list[str] = Field(default_factory=list)
    demo_banner: str | None = None


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    weight: float
    contribution: float
    detail: str
    provenance: Provenance = Provenance.SYNTHETIC


class ClassAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    device_class: DeviceClass = Field(alias="class")
    confidence: float


class Observation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    observation_id: str
    device_id: str
    observed_at_utc: datetime
    provenance: Provenance = Provenance.SYNTHETIC
    source: str = "synthetic"
    ipv4: str | None = None
    ipv6: str | None = None
    mac: str | None = None
    hostname: str | None = None
    vendor_hint: str | None = None
    dhcp_fingerprint: str | None = None
    reported_os: str | None = None
    ssid: str | None = None
    ap_id: str | None = None
    switch_id: str | None = None
    port_id: str | None = None
    rssi: int | None = None
    signal_bucket: SignalBucket | None = None
    connection_type: ConnectionType | None = None
    tags: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    raw_notes: str | None = None


class Device(BaseModel):
    model_config = ConfigDict(extra="ignore")

    device_id: str
    alias: str
    mac: str
    ipv4: str | None = None
    ipv6: str | None = None
    hostname: str | None = None
    vendor: str | None = None
    device_class_hint: DeviceClass | None = None
    connection_type: ConnectionType = ConnectionType.UNKNOWN
    current_segment: str = "quarantine"
    recommended_segment: str | None = None
    security_state: SecurityState = SecurityState.UNCERTAIN
    online: bool = True
    first_seen_utc: datetime
    last_seen_utc: datetime
    stale: bool = False
    tags: list[str] = Field(default_factory=list)
    ssid: str | None = None
    ap_id: str | None = None
    switch_id: str | None = None
    port_id: str | None = None
    signal_bucket: SignalBucket | None = None
    rssi: int | None = None
    ownership_label: str | None = None
    provenance: Provenance = Provenance.SYNTHETIC
    source_mode: SourceMode = SourceMode.SYNTHETIC
    metadata: dict[str, Any] = Field(default_factory=dict)


class Classification(BaseModel):
    model_config = ConfigDict(extra="ignore")

    device_id: str
    predicted_class: DeviceClass
    confidence: float
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    classification_status: ClassificationStatus
    generated_at_utc: datetime = Field(default_factory=utc_now)
    explanation: str = ""
    note: str = "confidence is a normalized heuristic evidence score, not statistical probability"


class PolicyDecisionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    policy_id: str
    matched_rule: str | None
    device_id: str
    current_segment: str
    recommended_segment: str | None
    decision: PolicyDecision
    approval_required: bool
    reason: str
    confidence: float | None = None
    policy_version: str
    generated_at_utc: datetime = Field(default_factory=utc_now)
    change_label: str = "PROPOSED / SIMULATED — NOT APPLIED"


class Segment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    segment_id: str
    label: str
    vlan_id: int
    vlan_note: str = "SYNTHETIC VLAN ID — EXAMPLE ONLY"
    logical_prefix: str
    demo_ipv4_map: str | None = None
    security_tier: str
    default_quarantine: bool = False


class TopologyNode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    node_id: str
    device_id: str
    node_type: str
    label: str
    segment: str
    device_class: DeviceClass | str
    classification_confidence: float | None = None
    connection_type: ConnectionType = ConnectionType.UNKNOWN
    security_state: SecurityState = SecurityState.UNCERTAIN
    online: bool = True
    last_seen: datetime | None = None
    metadata_source: Provenance = Provenance.SYNTHETIC
    position_source: str = "illustrative"
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    note: str = (
        "The position and edge length are normalized for visualization. "
        "No physical cable-length estimation is performed."
    )


class TopologyEdge(BaseModel):
    model_config = ConfigDict(extra="ignore")

    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    provenance: Provenance = Provenance.SYNTHETIC
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    note: str = (
        "The position and edge length are normalized for visualization. "
        "No physical cable-length estimation is performed."
    )


class ServiceObservation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    service_id: str
    device_id: str
    port: int | None = None
    protocol: str = "tcp"
    category: ServiceCategory = ServiceCategory.UNKNOWN
    provenance: Provenance = Provenance.SYNTHETIC
    observed_at_utc: datetime = Field(default_factory=utc_now)
    detail: str | None = None
    note: str = "Port maps to category hint only; no product inference."


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    event_type: EventType
    device_id: str | None = None
    timestamp_utc: datetime = Field(default_factory=utc_now)
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True
    change_label: str = "PROPOSED / SIMULATED — NOT APPLIED"


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    audit_id: str
    action: str
    actor: str = "SYNTHETIC-OPERATOR"
    timestamp_utc: datetime = Field(default_factory=utc_now)
    details: dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True
    note: str = "SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED"


class Approval(BaseModel):
    model_config = ConfigDict(extra="ignore")

    approval_id: str
    device_id: str
    previous_segment: str
    recommended_segment: str | None
    chosen_segment: str | None
    decision: ApprovalDecision
    operator_label: str = "SYNTHETIC-OPERATOR"
    justification: str = ""
    created_at_utc: datetime = Field(default_factory=utc_now)
    policy_id: str | None = None
    synthetic: bool = True
    change_label: str = "PROPOSED / SIMULATED — NOT APPLIED"
    note: str = "SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED"


class DriftFinding(BaseModel):
    model_config = ConfigDict(extra="ignore")

    finding_id: str
    device_id: str | None = None
    severity: DriftSeverity
    category: str
    summary: str
    detail: str
    generated_at_utc: datetime = Field(default_factory=utc_now)
    synthetic: bool = True


class ReachabilityResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_segment: str
    destination_segment: str
    service: str
    decision: ReachabilityDecision
    matched_rule: str | None
    explanation: str
    policy_version: str
    note: str = "Models intended policy only. No real firewall verification."


class LabSnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")

    snapshot_id: str
    created_at_utc: datetime = Field(default_factory=utc_now)
    version: str = "1.0.0"
    source_mode: SourceMode = SourceMode.SYNTHETIC
    devices: list[Device] = Field(default_factory=list)
    classifications: list[Classification] = Field(default_factory=list)
    policy_decisions: list[PolicyDecisionResult] = Field(default_factory=list)
    segments: list[Segment] = Field(default_factory=list)
    nodes: list[TopologyNode] = Field(default_factory=list)
    edges: list[TopologyEdge] = Field(default_factory=list)
    services: list[ServiceObservation] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    drift: list[DriftFinding] = Field(default_factory=list)
    warnings: list[str] = Field(
        default_factory=lambda: [
            "PROPOSED / SIMULATED — NOT APPLIED",
            "SYNTHETIC DEMONSTRATION DATA",
        ]
    )


class AdapterPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    adapter_id: str
    mode: str = "live-adapter-plan"
    capability: str = "read-only-plan"
    connects: bool = False
    mutates: bool = False
    steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(
        default_factory=lambda: [
            "DRY-RUN PLAN ONLY",
            "PROPOSED / SIMULATED — NOT APPLIED",
            "No network connection will be opened.",
        ]
    )
    generated_at_utc: datetime = Field(default_factory=utc_now)
