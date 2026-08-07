import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithApp } from './test-utils';
import { DashboardView } from '../src/views/DashboardView';
import { Topology3DView } from '../src/views/Topology3DView';
import { DeviceDetailView } from '../src/views/DeviceDetailView';
import { QuarantineView } from '../src/views/QuarantineView';
import { InventoryView } from '../src/views/InventoryView';
import { SummaryCharts } from '../src/components/SummaryCards';
import { Disclaimers } from '../src/components/Disclaimers';
import { MOCK_LAB } from '../src/data/mockLab';
import { api, createEventsSocket } from '../src/api/client';

describe('Dashboard empty / charts', () => {
  it('shows loading empty when lab missing', () => {
    renderWithApp(<DashboardView />, { initial: { lab: null, loading: true } });
    expect(screen.getByText(/loading lab snapshot/i)).toBeInTheDocument();
  });

  it('charts render empty-state when series empty', () => {
    const empty = {
      ...MOCK_LAB.summary,
      by_segment: {},
      by_class: {},
      by_confidence_band: {},
      by_security_state: {},
      events_by_type: {},
    };
    renderWithApp(<SummaryCharts summary={empty} />);
    expect(screen.getAllByText('No data').length).toBeGreaterThanOrEqual(5);
  });
});

describe('Topology camera controls', () => {
  it('exposes fit focus reset controls', () => {
    renderWithApp(<Topology3DView />, { initial: { selectedDeviceId: 'dev-fw-01' } });
    expect(screen.getByRole('button', { name: 'Fit' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Focus' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Reset' })).toBeEnabled();
    expect(screen.getByTestId('camera-orbit-hint')).toBeInTheDocument();
  });

  it('focus disabled without selection', () => {
    renderWithApp(<Topology3DView />, { initial: { selectedDeviceId: null } });
    expect(screen.getByRole('button', { name: 'Focus' })).toBeDisabled();
  });
});

describe('Device detail edge cases', () => {
  it('handles device without evidence list', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-sw-core', appView: 'device' },
    });
    expect(screen.getByTestId('confidence-explanation')).toBeInTheDocument();
  });

  it('lists services with provenance', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-fw-01', appView: 'device' },
    });
    expect(screen.getByText(/provenance observed/i)).toBeInTheDocument();
  });

  it('shows reachability explanations for camera', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-cam-01', appView: 'device' },
    });
    expect(screen.getByText(/IoT → DNS → allowed/i)).toBeInTheDocument();
  });
});

describe('Quarantine empty state', () => {
  it('shows empty message when no quarantined devices', () => {
    const lab = {
      ...MOCK_LAB,
      devices: MOCK_LAB.devices.map((d) => ({
        ...d,
        quarantined: false,
        current_segment:
          d.current_segment === 'quarantine' ? ('trusted' as const) : d.current_segment,
      })),
    };
    renderWithApp(<QuarantineView />, { initial: { lab } });
    expect(screen.getByTestId('empty-quarantine')).toBeInTheDocument();
  });
});

describe('Disclaimer visibility toggles', () => {
  it('can hide wireless disclaimer', () => {
    renderWithApp(<Disclaimers showWireless={false} showWired />);
    expect(screen.queryByTestId('wireless-disclaimer')).not.toBeInTheDocument();
    expect(screen.getByTestId('wired-disclaimer')).toBeInTheDocument();
  });
});

describe('Inventory a11y selection', () => {
  it('marks selected row with aria-selected', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    const cell = screen.getByText('SYNTHETIC-FW-01');
    await user.click(cell);
    expect(cell.closest('tr')).toHaveAttribute('aria-selected', 'true');
  });
});

describe('API client helpers', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('api.health hits expected path', async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', version: '1.0.0', source_mode: 'synthetic', banner: 'x' }),
    } as Response);
    await api.health();
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain('/api/v1/health');
  });

  it('api.submitApproval posts JSON', async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        approval_id: 'a1',
        device_id: 'dev-srv-01',
        previous_segment: 'infrastructure',
        recommended_segment: 'infrastructure',
        chosen_segment: 'infrastructure',
        decision: 'approve',
        operator_label: 'SYNTHETIC-OPERATOR',
        justification: 'demo',
        created_at_utc: '2026-08-07T12:00:00Z',
        policy_id: 'SNSL-SEG',
        synthetic: true,
        message: 'SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED',
      }),
    } as Response);
    await api.submitApproval({
      device_id: 'dev-srv-01',
      decision: 'approve',
      justification: 'demo',
      operator_label: 'SYNTHETIC-OPERATOR',
      synthetic: true,
    });
    expect(fetchMock.mock.calls[0]?.[1]?.method).toBe('POST');
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain('/api/v1/approvals');
  });

  it('api throws ApiError on non-OK', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: false, status: 500 } as Response);
    await expect(api.devices()).rejects.toMatchObject({ status: 500 });
  });

  it('createEventsSocket returns null when WebSocket missing', () => {
    const original = globalThis.WebSocket;
    // @ts-expect-error intentional
    delete globalThis.WebSocket;
    expect(createEventsSocket(() => undefined)).toBeNull();
    globalThis.WebSocket = original;
  });

  it('createEventsSocket wires handlers', () => {
    const instances: FakeSocket[] = [];
    class FakeSocket {
      onopen: (() => void) | null = null;
      onclose: (() => void) | null = null;
      onerror: (() => void) | null = null;
      onmessage: ((ev: { data: string }) => void) | null = null;
      close = vi.fn();
      constructor(public url: string) {
        instances.push(this);
      }
    }
    vi.stubGlobal('WebSocket', FakeSocket);
    const events: unknown[] = [];
    const statuses: string[] = [];
    createEventsSocket(
      (e) => events.push(e),
      (s) => statuses.push(s),
    );
    expect(instances[0]?.url).toContain('/ws/events');
    instances[0]!.onopen?.();
    instances[0]!.onmessage?.({
      data: JSON.stringify({
        event_id: 'e9',
        event_type: 'device_seen',
        message: 'hi',
        created_at_utc: '2026-08-07T12:00:00Z',
        synthetic: true,
      }),
    });
    instances[0]!.onmessage?.({ data: 'not-json' });
    expect(events).toHaveLength(1);
    expect(statuses).toContain('connecting');
    expect(statuses).toContain('open');
  });
});
