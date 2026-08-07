import type {
  AdapterPlan,
  ApprovalRecord,
  ApprovalRequest,
  AuditRecord,
  Classification,
  ClassificationStatus,
  ConnectionType,
  Device,
  DeviceClass,
  DriftFinding,
  EvidenceItem,
  HealthResponse,
  LabEvent,
  LabSnapshot,
  LabSummary,
  PolicyDecision,
  PolicyDecisionResult,
  Provenance,
  ReachabilityPath,
  ReachabilityReport,
  Segment,
  SegmentId,
  SecurityState,
  ServiceObservation,
  Topology,
  TopologyEdge,
  TopologyNode,
} from '../models';
import { BANNER_TEXT, VERSION_WARNING, WIRED_DISCLAIMER, WIRELESS_DISCLAIMER } from '../models';
import { MOCK_LAB } from '../data/mockLab';

export const API_BASE = 'http://127.0.0.1:8765';
export const WS_URL = 'ws://127.0.0.1:8765/ws/events';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    throw new ApiError(`API ${path} failed: ${res.status}`, res.status);
  }
  return (await res.json()) as T;
}

function asList<T>(payload: unknown, key?: string): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === 'object' && key) {
    const nested = (payload as Record<string, unknown>)[key];
    if (Array.isArray(nested)) return nested as T[];
  }
  return [];
}

function mapSecurityState(raw: unknown): SecurityState {
  const value = String(raw ?? 'uncertain');
  if (value === 'pending_approval') return 'awaiting_approval';
  const allowed: SecurityState[] = [
    'approved',
    'restricted',
    'quarantined',
    'uncertain',
    'policy_violation',
    'offline',
    'awaiting_approval',
  ];
  return (allowed.includes(value as SecurityState) ? value : 'uncertain') as SecurityState;
}

function mapClassificationStatus(raw: unknown, confidence: number): ClassificationStatus {
  const value = String(raw ?? '');
  const allowed: ClassificationStatus[] = [
    'classified',
    'uncertain',
    'unknown',
    'manually_reviewed',
  ];
  if (allowed.includes(value as ClassificationStatus)) return value as ClassificationStatus;
  if (confidence < 0.45) return 'unknown';
  if (confidence < 0.7) return 'uncertain';
  return 'classified';
}

function confidenceBand(c: number): string {
  if (c < 0.45) return 'low';
  if (c < 0.7) return 'medium';
  if (c < 0.85) return 'high';
  return 'very_high';
}

function buildSummary(devices: Device[], events: LabEvent[]): LabSummary {
  const by_segment: Record<string, number> = {};
  const by_class: Record<string, number> = {};
  const by_confidence_band: Record<string, number> = {};
  const by_security_state: Record<string, number> = {};
  const events_by_type: Record<string, number> = {};
  for (const d of devices) {
    by_segment[d.current_segment] = (by_segment[d.current_segment] ?? 0) + 1;
    by_class[d.device_class] = (by_class[d.device_class] ?? 0) + 1;
    const band = confidenceBand(d.confidence);
    by_confidence_band[band] = (by_confidence_band[band] ?? 0) + 1;
    by_security_state[d.security_state] = (by_security_state[d.security_state] ?? 0) + 1;
  }
  for (const e of events) {
    events_by_type[e.event_type] = (events_by_type[e.event_type] ?? 0) + 1;
  }
  return {
    total: devices.length,
    online: devices.filter((d) => d.online).length,
    unknown: devices.filter((d) => d.device_class === 'unknown').length,
    quarantined: devices.filter((d) => d.quarantined).length,
    awaiting_approval: devices.filter((d) => d.awaiting_approval).length,
    policy_violations: devices.filter((d) => d.policy_violation).length,
    wired: devices.filter((d) => d.connection_type === 'wired').length,
    wireless: devices.filter((d) => d.connection_type === 'wireless').length,
    by_segment,
    by_class,
    by_confidence_band,
    by_security_state,
    events_by_type,
  };
}

function normalizeTopology(
  raw: Record<string, unknown>,
  devices: Device[],
  reachability: ReachabilityReport,
): Topology {
  const rawNodes = asList<Record<string, unknown>>(raw.nodes ?? raw);
  const nodeById = new Map<string, Record<string, unknown>>();
  const deviceBySegment = new Map<string, string>();
  for (const d of devices) {
    if (!deviceBySegment.has(d.current_segment))
      deviceBySegment.set(d.current_segment, d.device_id);
  }

  const nodes: TopologyNode[] = rawNodes.map((n, i) => {
    const deviceId = String(n.device_id ?? n.node_id ?? `node-${i}`);
    const nodeId = String(n.node_id ?? `node-${deviceId}`);
    nodeById.set(nodeId, n);
    if (n.device_id) nodeById.set(String(n.device_id), n);
    const device = devices.find((d) => d.device_id === deviceId);
    return {
      node_id: nodeId,
      device_id: deviceId,
      label: String(n.label ?? device?.alias ?? deviceId),
      segment_id: (n.segment ?? n.segment_id ?? device?.current_segment ?? 'trusted') as SegmentId,
      connection_type: (device?.connection_type ?? 'wired') as ConnectionType,
      position: {
        x: Number(n.x ?? (n.position as { x?: number } | undefined)?.x ?? 0),
        y: Number(n.y ?? (n.position as { y?: number } | undefined)?.y ?? 0),
        z: Number(n.z ?? (n.position as { z?: number } | undefined)?.z ?? 0),
      },
      role: n.node_type ? String(n.node_type) : undefined,
    };
  });

  const resolveDeviceId = (ref: unknown): string | null => {
    const key = String(ref ?? '');
    if (!key) return null;
    if (devices.some((d) => d.device_id === key)) return key;
    const node = nodeById.get(key);
    if (node?.device_id) return String(node.device_id);
    if (key.startsWith('node-')) {
      const stripped = key.slice(5);
      if (devices.some((d) => d.device_id === stripped)) return stripped;
    }
    return null;
  };

  const edges: TopologyEdge[] = [];
  for (const e of asList<Record<string, unknown>>(raw.edges)) {
    const source = resolveDeviceId(e.source_id ?? e.source_node_id ?? e.source);
    const target = resolveDeviceId(e.target_id ?? e.target_node_id ?? e.target);
    if (!source || !target) continue;
    let edgeType = String(e.edge_type ?? 'wired');
    if (edgeType === 'logical_upstream' || edgeType === 'logical') edgeType = 'wired';
    if (!['wired', 'wireless_association', 'policy', 'logical'].includes(edgeType)) {
      edgeType = 'wired';
    }
    edges.push({
      edge_id: String(e.edge_id ?? `${source}-${target}`),
      source_id: source,
      target_id: target,
      edge_type: edgeType as TopologyEdge['edge_type'],
      provenance: (String(e.provenance ?? 'synthetic') as Provenance) || 'synthetic',
      note: e.label ? String(e.label) : e.note ? String(e.note) : undefined,
      allowed: typeof e.allowed === 'boolean' ? e.allowed : undefined,
    });
  }

  // Illustrative policy edges for POLICY_REACHABILITY mode (segment representatives).
  let policyIdx = 0;
  for (const path of reachability.paths) {
    if (path.decision !== 'allowed' && path.decision !== 'denied') continue;
    const src =
      path.source_device_id && devices.some((d) => d.device_id === path.source_device_id)
        ? path.source_device_id
        : deviceBySegment.get(String(path.source_segment));
    const dst = deviceBySegment.get(String(path.destination_segment));
    if (!src || !dst || src === dst) continue;
    edges.push({
      edge_id: `policy-${path.path_id}-${policyIdx++}`,
      source_id: src,
      target_id: dst,
      edge_type: 'policy',
      provenance: 'synthetic',
      allowed: path.decision === 'allowed',
      note: path.explanation,
    });
    if (policyIdx >= 24) break;
  }

  return {
    nodes,
    edges,
    banner: BANNER_TEXT,
    wireless_disclaimer: WIRELESS_DISCLAIMER,
    wired_disclaimer: WIRED_DISCLAIMER,
  };
}

function normalizeDevice(
  raw: Record<string, unknown>,
  clf: Record<string, unknown> | undefined,
  decision: Record<string, unknown> | undefined,
  services: ServiceObservation[],
  position?: { x: number; y: number; z: number },
): Device {
  const confidence = Number(clf?.confidence ?? raw.confidence ?? 0);
  const predicted = String(
    clf?.predicted_class ??
      raw.predicted_class ??
      raw.device_class_hint ??
      raw.device_class ??
      'unknown',
  ) as DeviceClass;
  const security = mapSecurityState(raw.security_state);
  const current = String(raw.current_segment ?? 'quarantine') as SegmentId;
  const recommended = String(
    decision?.recommended_segment ?? raw.recommended_segment ?? current,
  ) as SegmentId;
  const evidence = asList<EvidenceItem>(clf?.evidence ?? raw.evidence);

  return {
    device_id: String(raw.device_id),
    alias: String(raw.alias ?? raw.hostname ?? raw.device_id),
    mac: String(raw.mac ?? '02:00:00:00:00:00'),
    ipv4: (raw.ipv4 as string | null | undefined) ?? null,
    ipv6: (raw.ipv6 as string | null | undefined) ?? null,
    device_class: predicted,
    predicted_class: predicted,
    confidence,
    classification_status: mapClassificationStatus(clf?.classification_status, confidence),
    current_segment: current,
    recommended_segment: recommended,
    security_state: security,
    connection_type: (String(raw.connection_type ?? 'wired') as ConnectionType) || 'wired',
    online: Boolean(raw.online ?? true),
    switch_id: (raw.switch_id as string | null | undefined) ?? null,
    ap_id: (raw.ap_id as string | null | undefined) ?? null,
    ssid: (raw.ssid as string | null | undefined) ?? null,
    signal_bucket: (raw.signal_bucket as Device['signal_bucket']) ?? null,
    policy_decision: decision?.decision
      ? (String(decision.decision) as PolicyDecision)
      : ((raw.policy_decision as PolicyDecision | undefined) ?? undefined),
    approval_required: Boolean(decision?.approval_required ?? raw.approval_required ?? false),
    awaiting_approval: security === 'awaiting_approval',
    quarantined: security === 'quarantined' || current === 'quarantine',
    policy_violation: security === 'policy_violation',
    vendor_hint: String(raw.vendor_hint ?? raw.vendor ?? 'Synthetic Devices Ltd.'),
    first_seen_utc: String(raw.first_seen_utc ?? ''),
    last_seen_utc: String(raw.last_seen_utc ?? ''),
    tags: asList<string>(raw.tags),
    provenance: (String(raw.provenance ?? 'synthetic') as Provenance) || 'synthetic',
    services,
    evidence,
    position,
  };
}

async function assembleLabFromApi(): Promise<LabSnapshot> {
  const [
    labMeta,
    devicesPayload,
    segmentsPayload,
    topologyPayload,
    classificationsPayload,
    decisionsPayload,
    driftPayload,
    eventsPayload,
    auditPayload,
    adaptersPayload,
    reachabilityPayload,
    servicesPayload,
  ] = await Promise.all([
    request<Record<string, unknown>>('/api/v1/lab'),
    request<unknown>('/api/v1/devices'),
    request<unknown>('/api/v1/segments'),
    request<Record<string, unknown>>('/api/v1/topology'),
    request<unknown>('/api/v1/classifications'),
    request<unknown>('/api/v1/policy/decisions'),
    request<unknown>('/api/v1/drift'),
    request<unknown>('/api/v1/events'),
    request<unknown>('/api/v1/audit'),
    request<unknown>('/api/v1/adapters'),
    request<unknown>('/api/v1/reachability'),
    request<unknown>('/api/v1/services').catch(() => []),
  ]);

  // Full snapshot compatibility (tests / future backend).
  if (Array.isArray((labMeta as { devices?: unknown }).devices)) {
    return labMeta as unknown as LabSnapshot;
  }

  const rawDevices = asList<Record<string, unknown>>(devicesPayload, 'devices');
  if (rawDevices.length === 0) {
    throw new Error('Malformed lab payload: empty devices');
  }

  const classifications = asList<Record<string, unknown>>(
    classificationsPayload,
    'classifications',
  );
  const decisions = asList<Record<string, unknown>>(decisionsPayload, 'decisions');
  const clfById = new Map(classifications.map((c) => [String(c.device_id), c]));
  const decById = new Map(decisions.map((d) => [String(d.device_id), d]));
  const allServices = asList<ServiceObservation>(servicesPayload, 'services');

  const topoNodes = asList<Record<string, unknown>>(topologyPayload.nodes);
  const posByDevice = new Map<string, { x: number; y: number; z: number }>();
  for (const n of topoNodes) {
    const id = String(n.device_id ?? '');
    if (!id) continue;
    posByDevice.set(id, {
      x: Number(n.x ?? 0),
      y: Number(n.y ?? 0),
      z: Number(n.z ?? 0),
    });
  }

  const devices = rawDevices.map((raw) => {
    const id = String(raw.device_id);
    const services = allServices.filter((s) => s.device_id === id);
    return normalizeDevice(raw, clfById.get(id), decById.get(id), services, posByDevice.get(id));
  });

  const segments = asList<Segment>(segmentsPayload, 'segments');
  const events = asList<LabEvent>(eventsPayload, 'events').map((e) => ({
    ...e,
    synthetic: true as const,
  }));
  const audit = asList<AuditRecord>(auditPayload, 'audit').map((a) => ({
    ...a,
    synthetic: true as const,
  }));
  const adapters = asList<AdapterPlan>(adaptersPayload, 'adapters');
  const drift = asList<DriftFinding>(driftPayload, 'drift');

  let reachability: ReachabilityReport;
  if (
    reachabilityPayload &&
    typeof reachabilityPayload === 'object' &&
    Array.isArray((reachabilityPayload as ReachabilityReport).paths)
  ) {
    reachability = {
      paths: (reachabilityPayload as ReachabilityReport).paths,
      note:
        (reachabilityPayload as ReachabilityReport).note ||
        'PROPOSED / SIMULATED — NOT APPLIED. Reachability is modelled from intended policy only.',
    };
  } else if (
    reachabilityPayload &&
    typeof reachabilityPayload === 'object' &&
    'decision' in (reachabilityPayload as object)
  ) {
    const single = reachabilityPayload as Record<string, unknown>;
    reachability = {
      note: 'PROPOSED / SIMULATED — NOT APPLIED. Reachability is modelled from intended policy only.',
      paths: [
        {
          path_id: 'rch-single',
          source_segment: String(single.source_segment) as ReachabilityPath['source_segment'],
          destination_segment: String(
            single.destination_segment,
          ) as ReachabilityPath['destination_segment'],
          service: (String(single.service ?? 'any') as ReachabilityPath['service']) || 'any',
          decision: String(single.decision) as ReachabilityPath['decision'],
          rule_id: single.matched_rule ? String(single.matched_rule) : undefined,
          explanation: String(single.explanation ?? ''),
        },
      ],
    };
  } else {
    reachability = {
      note: 'PROPOSED / SIMULATED — NOT APPLIED. Reachability is modelled from intended policy only.',
      paths: [],
    };
  }

  const topology = normalizeTopology(topologyPayload, devices, reachability);

  const normalizedClassifications: Classification[] = devices.map((d) => {
    const raw = clfById.get(d.device_id);
    return {
      device_id: d.device_id,
      predicted_class: d.predicted_class ?? d.device_class,
      confidence: d.confidence,
      alternatives: asList(raw?.alternatives),
      evidence: d.evidence ?? [],
      classification_status: d.classification_status,
      generated_at_utc: String(raw?.generated_at_utc ?? d.last_seen_utc),
    };
  });

  const policy_decisions: PolicyDecisionResult[] = decisions.map((d, i) => ({
    decision_id: String(d.decision_id ?? `pd-${i + 1}`),
    device_id: String(d.device_id),
    policy_id: String(d.policy_id ?? 'SNSL-SEG'),
    matched_rule: String(d.matched_rule ?? 'none'),
    current_segment: String(d.current_segment) as SegmentId,
    recommended_segment: String(d.recommended_segment ?? d.current_segment) as SegmentId,
    decision: String(d.decision) as PolicyDecision,
    approval_required: Boolean(d.approval_required),
    reason: String(d.reason ?? ''),
    confidence: Number(d.confidence ?? 0),
    policy_version: String(d.policy_version ?? '1.0.0'),
    generated_at_utc: String(d.generated_at_utc ?? ''),
    synthetic: true,
  }));

  return {
    version: String(labMeta.version ?? '1.0.0'),
    banner: BANNER_TEXT,
    source_mode: 'synthetic',
    warnings: asList<string>(labMeta.warnings).length
      ? asList<string>(labMeta.warnings)
      : [VERSION_WARNING, BANNER_TEXT],
    summary: buildSummary(devices, events),
    devices,
    segments,
    topology,
    classifications: normalizedClassifications,
    policy_decisions,
    reachability,
    drift,
    events,
    audit,
    adapters,
  };
}

export const api = {
  health: () => request<HealthResponse>('/api/v1/health'),
  lab: () => request<LabSnapshot>('/api/v1/lab'),
  devices: () => request<Device[]>('/api/v1/devices'),
  device: (id: string) => request<Device>(`/api/v1/devices/${encodeURIComponent(id)}`),
  segments: () => request<Segment[]>('/api/v1/segments'),
  topology: () => request<Topology>('/api/v1/topology'),
  classifications: () => request<Classification[]>('/api/v1/classifications'),
  policyDecisions: () => request<PolicyDecisionResult[]>('/api/v1/policy/decisions'),
  reachability: () => request<ReachabilityReport>('/api/v1/reachability'),
  drift: () => request<DriftFinding[]>('/api/v1/drift'),
  events: () => request<LabEvent[]>('/api/v1/events'),
  audit: () => request<AuditRecord[]>('/api/v1/audit'),
  adapters: () => request<AdapterPlan[]>('/api/v1/adapters'),
  simulationReset: () => request<{ ok: boolean }>('/api/v1/simulation/reset', { method: 'POST' }),
  simulationStep: () => request<{ ok: boolean }>('/api/v1/simulation/step', { method: 'POST' }),
  simulationRun: (body?: Record<string, unknown>) =>
    request<{ ok: boolean }>('/api/v1/simulation/run', {
      method: 'POST',
      body: JSON.stringify(body ?? { scenario: 'mixed', seed: 42 }),
    }),
  submitApproval: (body: ApprovalRequest) =>
    request<ApprovalRecord>('/api/v1/approvals', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
};

/** Load lab snapshot from API, falling back to local synthetic mock data. */
export async function loadLabOrMock(): Promise<{
  lab: LabSnapshot;
  fromMock: boolean;
  error?: string;
}> {
  try {
    const lab = await assembleLabFromApi();
    if (!lab || !Array.isArray(lab.devices) || lab.devices.length === 0) {
      return { lab: MOCK_LAB, fromMock: true, error: 'Malformed lab payload' };
    }
    return { lab, fromMock: false };
  } catch (err) {
    // Compatibility: single-shot lab snapshot with devices (used by unit tests).
    try {
      const snapshot = await request<LabSnapshot>('/api/v1/lab');
      if (snapshot && Array.isArray(snapshot.devices) && snapshot.devices.length > 0) {
        return { lab: snapshot, fromMock: false };
      }
      if (snapshot && 'devices' in snapshot && !Array.isArray(snapshot.devices)) {
        return { lab: MOCK_LAB, fromMock: true, error: 'Malformed lab payload' };
      }
    } catch {
      /* continue to mock */
    }
    const message = err instanceof Error ? err.message : 'API unavailable';
    const malformed = /malformed/i.test(message);
    return {
      lab: MOCK_LAB,
      fromMock: true,
      error: malformed ? 'Malformed lab payload' : message,
    };
  }
}

export function createEventsSocket(
  onEvent: (event: LabEvent) => void,
  onStatus?: (status: 'connecting' | 'open' | 'closed' | 'error') => void,
): WebSocket | null {
  if (typeof WebSocket === 'undefined') return null;
  onStatus?.('connecting');
  try {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => onStatus?.('open');
    ws.onclose = () => onStatus?.('closed');
    ws.onerror = () => onStatus?.('error');
    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(String(msg.data)) as LabEvent;
        if (data && typeof data.event_id === 'string') onEvent(data);
      } catch {
        /* ignore malformed frames */
      }
    };
    return ws;
  } catch {
    onStatus?.('error');
    return null;
  }
}

export function assertNoRemoteAssets(doc: Document = document): string[] {
  const offenders: string[] = [];
  const attrs = ['src', 'href'];
  for (const el of Array.from(doc.querySelectorAll('*'))) {
    for (const attr of attrs) {
      const val = el.getAttribute(attr);
      if (!val) continue;
      if (/^https?:\/\//i.test(val) && !val.includes('127.0.0.1') && !val.includes('localhost')) {
        offenders.push(`${el.tagName.toLowerCase()}[${attr}]=${val}`);
      }
    }
  }
  return offenders;
}
