"""Enumerations used across the Secure Network Segmentation Lab."""

from __future__ import annotations

from enum import Enum


class SourceMode(str, Enum):
    SYNTHETIC = "synthetic"
    IMPORTED = "imported"


class DeviceClass(str, Enum):
    FIREWALL = "firewall"
    ROUTER = "router"
    SWITCH = "switch"
    ACCESS_POINT = "access_point"
    SERVER = "server"
    WORKSTATION = "workstation"
    LAPTOP = "laptop"
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    PRINTER = "printer"
    CAMERA = "camera"
    NAS = "nas"
    MEDIA_DEVICE = "media_device"
    IOT = "iot"
    NETWORK_APPLIANCE = "network_appliance"
    UNKNOWN = "unknown"


class ClassificationStatus(str, Enum):
    CLASSIFIED = "classified"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"
    MANUALLY_REVIEWED = "manually_reviewed"


class PolicyDecision(str, Enum):
    KEEP = "keep"
    RECOMMEND_MOVE = "recommend_move"
    QUARANTINE = "quarantine"
    REQUIRE_APPROVAL = "require_approval"
    DENY_TRANSITION = "deny_transition"
    NO_MATCH = "no_match"


class ReachabilityDecision(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    UNKNOWN = "unknown"


class SecurityState(str, Enum):
    APPROVED = "approved"
    RESTRICTED = "restricted"
    QUARANTINED = "quarantined"
    UNCERTAIN = "uncertain"
    POLICY_VIOLATION = "policy_violation"
    OFFLINE = "offline"
    PENDING_APPROVAL = "pending_approval"


class ConnectionType(str, Enum):
    WIRED = "wired"
    WIRELESS = "wireless"
    UNKNOWN = "unknown"


class Provenance(str, Enum):
    OBSERVED = "observed"
    REPORTED = "reported"
    INFERRED = "inferred"
    SYNTHETIC = "synthetic"
    OPERATOR_DEFINED = "operator_defined"


class EdgeType(str, Enum):
    WIRED = "wired"
    WIRELESS_ASSOCIATION = "wireless_association"
    LOGICAL_UPSTREAM = "logical_upstream"
    SEGMENT_MEMBERSHIP = "segment_membership"
    OBSERVED_COMMUNICATION = "observed_communication"
    ALLOWED_POLICY_PATH = "allowed_policy_path"
    DENIED_POLICY_PATH = "denied_policy_path"


class EventType(str, Enum):
    DEVICE_SEEN = "device_seen"
    DEVICE_OFFLINE = "device_offline"
    ADDRESS_CHANGED = "address_changed"
    AP_ASSOCIATION_CHANGED = "ap_association_changed"
    SIGNAL_CHANGED = "signal_changed"
    CLASSIFICATION_CHANGED = "classification_changed"
    CLASSIFICATION_UNCERTAIN = "classification_uncertain"
    POLICY_DECISION_CREATED = "policy_decision_created"
    QUARANTINE_RECOMMENDED = "quarantine_recommended"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RECORDED = "approval_recorded"
    SIMULATED_SEGMENT_CHANGED = "simulated_segment_changed"
    SERVICE_OBSERVED = "service_observed"
    TOPOLOGY_CHANGED = "topology_changed"
    POLICY_VIOLATION_DETECTED = "policy_violation_detected"
    POLICY_VIOLATION_RESOLVED = "policy_violation_resolved"


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    KEEP_QUARANTINED = "keep_quarantined"
    CHOOSE_ALTERNATE_SEGMENT = "choose_alternate_segment"


class PrivacyMode(str, Enum):
    MASKED = "masked"
    HASHED = "hashed"
    FULL = "full"


class SignalBucket(str, Enum):
    STRONG = "strong"
    GOOD = "good"
    MODERATE = "moderate"
    WEAK = "weak"


class ServiceCategory(str, Enum):
    WEB = "web"
    SECURE_WEB = "secure_web"
    SSH = "ssh"
    DNS = "dns"
    NTP = "ntp"
    DHCP = "dhcp"
    PRINTING = "printing"
    FILE_SERVICE = "file_service"
    MEDIA = "media"
    DATABASE = "database"
    MANAGEMENT = "management"
    UNKNOWN = "unknown"


class DriftSeverity(str, Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViewMode(str, Enum):
    """Conceptual 3D / dashboard view modes (frontend consumes these labels)."""

    TOPOLOGY = "topology"
    SEGMENTATION = "segmentation"
    CLASSIFICATION = "classification"
    SECURITY_STATE = "security_state"
    WIRELESS = "wireless"
    POLICY_REACHABILITY = "policy_reachability"
    SERVICES = "services"


class SimulationScenario(str, Enum):
    NORMAL = "normal"
    NEW_DEVICE = "new-device"
    QUARANTINE = "quarantine"
    ROAMING = "roaming"
    POLICY_DRIFT = "policy-drift"
    MIXED = "mixed"


class ChangeLabel(str, Enum):
    """Every simulated change must carry this semantics."""

    PROPOSED = "PROPOSED"
    SIMULATED = "SIMULATED"
    NOT_APPLIED = "NOT_APPLIED"
