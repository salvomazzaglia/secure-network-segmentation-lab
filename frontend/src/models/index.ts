/** Shared domain types for Secure Network Segmentation Lab (synthetic). */

export type DeviceClass =
  | 'firewall'
  | 'router'
  | 'switch'
  | 'access_point'
  | 'server'
  | 'workstation'
  | 'laptop'
  | 'smartphone'
  | 'tablet'
  | 'printer'
  | 'camera'
  | 'nas'
  | 'media_device'
  | 'iot'
  | 'network_appliance'
  | 'unknown';

export type ClassificationStatus = 'classified' | 'uncertain' | 'unknown' | 'manually_reviewed';

export type PolicyDecision =
  'keep' | 'recommend_move' | 'quarantine' | 'require_approval' | 'deny_transition' | 'no_match';

export type ReachabilityDecision = 'allowed' | 'denied' | 'conditional' | 'unknown';

export type SecurityState =
  | 'approved'
  | 'restricted'
  | 'quarantined'
  | 'uncertain'
  | 'policy_violation'
  | 'offline'
  | 'awaiting_approval';

export type ConnectionType = 'wired' | 'wireless';

export type Provenance =
  'synthetic' | 'imported' | 'simulated' | 'observed' | 'reported' | 'inferred';

export type EdgeType = 'wired' | 'wireless_association' | 'policy' | 'logical';

export type EventType =
  | 'device_seen'
  | 'device_offline'
  | 'address_changed'
  | 'ap_association_changed'
  | 'signal_changed'
  | 'classification_changed'
  | 'classification_uncertain'
  | 'policy_decision_created'
  | 'quarantine_recommended'
  | 'approval_requested'
  | 'approval_recorded'
  | 'simulated_segment_changed'
  | 'service_observed'
  | 'topology_changed'
  | 'policy_violation_detected'
  | 'policy_violation_resolved';

export type ApprovalDecision =
  'approve' | 'reject' | 'keep_quarantined' | 'choose_alternate_segment';

export type SignalBucket = 'strong' | 'good' | 'moderate' | 'weak';

export type ServiceCategory =
  | 'web'
  | 'secure_web'
  | 'ssh'
  | 'dns'
  | 'ntp'
  | 'dhcp'
  | 'printing'
  | 'file_service'
  | 'media'
  | 'database'
  | 'management'
  | 'unknown';

export type ServiceProvenance = 'observed' | 'reported' | 'inferred';

export type DriftSeverity = 'informational' | 'low' | 'medium' | 'high' | 'critical';

export type ViewMode =
  | 'TOPOLOGY'
  | 'SEGMENTATION'
  | 'CLASSIFICATION'
  | 'SECURITY_STATE'
  | 'WIRELESS'
  | 'POLICY_REACHABILITY'
  | 'SERVICES';

export type SegmentId =
  'management' | 'infrastructure' | 'trusted' | 'iot' | 'guest' | 'quarantine';

export type AppView =
  | 'dashboard'
  | 'topology'
  | 'segmentation'
  | 'reachability'
  | 'inventory'
  | 'quarantine'
  | 'policy'
  | 'events'
  | 'device';

export interface EvidenceItem {
  source: string;
  weight: number;
  contribution: number;
  detail: string;
}

export interface ClassificationAlternative {
  class: DeviceClass;
  confidence: number;
}

export interface Classification {
  device_id: string;
  predicted_class: DeviceClass;
  confidence: number;
  alternatives: ClassificationAlternative[];
  evidence: EvidenceItem[];
  classification_status: ClassificationStatus;
  generated_at_utc: string;
}

export interface ServiceObservation {
  service_id: string;
  device_id: string;
  category: ServiceCategory;
  port?: number;
  protocol?: string;
  provenance: ServiceProvenance;
  note?: string;
}

export interface Device {
  device_id: string;
  alias: string;
  mac: string;
  ipv4?: string | null;
  ipv6?: string | null;
  device_class: DeviceClass;
  predicted_class?: DeviceClass;
  confidence: number;
  classification_status: ClassificationStatus;
  current_segment: SegmentId;
  recommended_segment: SegmentId;
  security_state: SecurityState;
  connection_type: ConnectionType;
  online: boolean;
  switch_id?: string | null;
  ap_id?: string | null;
  ssid?: string | null;
  signal_bucket?: SignalBucket | null;
  policy_decision?: PolicyDecision;
  approval_required: boolean;
  awaiting_approval: boolean;
  quarantined: boolean;
  policy_violation: boolean;
  vendor_hint: string;
  first_seen_utc: string;
  last_seen_utc: string;
  tags: string[];
  provenance: Provenance;
  services: ServiceObservation[];
  evidence?: EvidenceItem[];
  position?: { x: number; y: number; z: number };
}

export interface Segment {
  segment_id: SegmentId;
  label: string;
  vlan_id: number;
  vlan_note: string;
  logical_prefix: string;
  demo_ipv4_map: string | null;
  security_tier: string;
  default_quarantine: boolean;
}

export interface TopologyNode {
  node_id: string;
  device_id: string;
  label: string;
  segment_id: SegmentId;
  connection_type: ConnectionType;
  position: { x: number; y: number; z: number };
  role?: string;
}

export interface TopologyEdge {
  edge_id: string;
  source_id: string;
  target_id: string;
  edge_type: EdgeType;
  provenance: Provenance;
  note?: string;
  allowed?: boolean;
}

export interface Topology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  banner: string;
  wireless_disclaimer: string;
  wired_disclaimer: string;
}

export interface PolicyDecisionResult {
  decision_id: string;
  device_id: string;
  policy_id: string;
  matched_rule: string;
  current_segment: SegmentId;
  recommended_segment: SegmentId;
  decision: PolicyDecision;
  approval_required: boolean;
  reason: string;
  confidence: number;
  policy_version: string;
  generated_at_utc: string;
  synthetic: true;
}

export interface ReachabilityPath {
  path_id: string;
  source_device_id?: string;
  source_segment: SegmentId | 'internet' | 'any';
  destination_segment: SegmentId | 'internet' | 'any';
  service: ServiceCategory | 'any';
  decision: ReachabilityDecision;
  rule_id?: string;
  explanation: string;
}

export interface ReachabilityReport {
  paths: ReachabilityPath[];
  note: string;
}

export interface DriftFinding {
  finding_id: string;
  device_id?: string;
  severity: DriftSeverity;
  summary: string;
  detail: string;
}

export interface LabEvent {
  event_id: string;
  event_type: EventType;
  device_id?: string;
  message: string;
  created_at_utc: string;
  synthetic: true;
}

export interface AuditRecord {
  audit_id: string;
  action: string;
  operator_label: string;
  detail: string;
  created_at_utc: string;
  synthetic: true;
}

export interface ApprovalRequest {
  device_id: string;
  decision: ApprovalDecision;
  chosen_segment?: SegmentId;
  justification: string;
  operator_label: string;
  synthetic: true;
}

export interface ApprovalRecord {
  approval_id: string;
  device_id: string;
  previous_segment: SegmentId;
  recommended_segment: SegmentId;
  chosen_segment: SegmentId;
  decision: ApprovalDecision;
  operator_label: string;
  justification: string;
  created_at_utc: string;
  policy_id: string;
  synthetic: true;
  message: string;
}

export interface AdapterPlan {
  adapter_id: string;
  name: string;
  connects: false;
  dry_run: true;
  description: string;
  steps: string[];
}

export interface LabSummary {
  total: number;
  online: number;
  unknown: number;
  quarantined: number;
  awaiting_approval: number;
  policy_violations: number;
  wired: number;
  wireless: number;
  by_segment: Record<string, number>;
  by_class: Record<string, number>;
  by_confidence_band: Record<string, number>;
  by_security_state: Record<string, number>;
  events_by_type: Record<string, number>;
}

export interface LabSnapshot {
  version: string;
  banner: string;
  source_mode: 'synthetic';
  warnings: string[];
  summary: LabSummary;
  devices: Device[];
  segments: Segment[];
  topology: Topology;
  classifications: Classification[];
  policy_decisions: PolicyDecisionResult[];
  reachability: ReachabilityReport;
  drift: DriftFinding[];
  events: LabEvent[];
  audit: AuditRecord[];
  adapters: AdapterPlan[];
}

export interface HealthResponse {
  status: string;
  version: string;
  source_mode: string;
  banner: string;
}

export interface AppFilters {
  segment: SegmentId | 'all';
  deviceClass: DeviceClass | 'all';
  connection: ConnectionType | 'all';
  online: 'all' | 'online' | 'offline';
  confidenceMin: number;
  confidenceMax: number;
  securityState: SecurityState | 'all';
  apId: string | 'all';
  serviceCategory: ServiceCategory | 'all';
}

export const DEFAULT_FILTERS: AppFilters = {
  segment: 'all',
  deviceClass: 'all',
  connection: 'all',
  online: 'all',
  confidenceMin: 0,
  confidenceMax: 1,
  securityState: 'all',
  apId: 'all',
  serviceCategory: 'all',
};

export const VIEW_MODES: ViewMode[] = [
  'TOPOLOGY',
  'SEGMENTATION',
  'CLASSIFICATION',
  'SECURITY_STATE',
  'WIRELESS',
  'POLICY_REACHABILITY',
  'SERVICES',
];

export const BANNER_TEXT = 'SYNTHETIC DEMONSTRATION DATA';
export const APPROVAL_DIALOG_TEXT = 'SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED';
export const WIRELESS_DISCLAIMER = 'Illustrative wireless position — not physical localization';
export const WIRED_DISCLAIMER = 'Wired edge length does not represent cable length';
export const VERSION_WARNING =
  'Version 1.0 never applies network changes. VLAN transitions, approvals, quarantine actions, and reachability policies are simulated or proposed only.';
