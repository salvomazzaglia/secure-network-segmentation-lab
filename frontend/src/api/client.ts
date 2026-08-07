import type {
  AdapterPlan,
  ApprovalRecord,
  ApprovalRequest,
  AuditRecord,
  Classification,
  Device,
  DriftFinding,
  HealthResponse,
  LabEvent,
  LabSnapshot,
  PolicyDecisionResult,
  ReachabilityReport,
  Segment,
  Topology,
} from '../models';
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
    const lab = await api.lab();
    if (!lab || !Array.isArray(lab.devices)) {
      return { lab: MOCK_LAB, fromMock: true, error: 'Malformed lab payload' };
    }
    return { lab, fromMock: false };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'API unavailable';
    return { lab: MOCK_LAB, fromMock: true, error: message };
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
