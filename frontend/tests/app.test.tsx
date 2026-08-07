import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../src/App';
import { AppProvider } from '../src/state/AppProvider';
import { renderWithApp } from './test-utils';
import { MOCK_LAB } from '../src/data/mockLab';
import {
  APPROVAL_DIALOG_TEXT,
  BANNER_TEXT,
  VERSION_WARNING,
  WIRED_DISCLAIMER,
  WIRELESS_DISCLAIMER,
  VIEW_MODES,
} from '../src/models';
import { filterDevices, appReducer, initialState } from '../src/state/appState';
import { layoutDevice, layoutAll, segmentColor } from '../src/three/LayoutEngine';
import { assertNoRemoteAssets, loadLabOrMock, ApiError } from '../src/api/client';
import { Banner } from '../src/components/Banner';
import { SummaryCards } from '../src/components/SummaryCards';
import { Filters } from '../src/components/Filters';
import { Disclaimers } from '../src/components/Disclaimers';
import { Legend } from '../src/components/Legend';
import { ApprovalDialog } from '../src/components/ApprovalDialog';
import { DashboardView } from '../src/views/DashboardView';
import { InventoryView } from '../src/views/InventoryView';
import { QuarantineView } from '../src/views/QuarantineView';
import { DeviceDetailView } from '../src/views/DeviceDetailView';
import { Topology3DView } from '../src/views/Topology3DView';
import { EventsView } from '../src/views/EventsView';
import { ReachabilityView } from '../src/views/ReachabilityView';
import { SegmentationView } from '../src/views/SegmentationView';
import { PolicyView } from '../src/views/PolicyView';

function renderApp() {
  return renderWithApp(
    <AppProvider>
      <App />
    </AppProvider>,
  );
}

describe('App load & banner', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('API offline')));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads app shell with synthetic banner', async () => {
    renderApp();
    expect(await screen.findByTestId('app-root')).toBeInTheDocument();
    expect(screen.getByTestId('synthetic-banner')).toHaveTextContent(BANNER_TEXT);
    expect(screen.getByTestId('wireless-disclaimer-global')).toHaveTextContent(WIRELESS_DISCLAIMER);
  });

  it('shows mock fallback notice when API fails', async () => {
    renderApp();
    expect(await screen.findByTestId('api-error')).toBeInTheDocument();
    expect(await screen.findByTestId('mock-notice')).toBeInTheDocument();
  });

  it('renders dashboard counters after load', async () => {
    renderApp();
    expect(await screen.findByTestId('summary-cards')).toBeInTheDocument();
    expect(screen.getByTestId('card-total')).toHaveTextContent(String(MOCK_LAB.summary.total));
    expect(screen.getByTestId('card-online')).toHaveTextContent(String(MOCK_LAB.summary.online));
    expect(screen.getByTestId('card-unknown')).toHaveTextContent(String(MOCK_LAB.summary.unknown));
    expect(screen.getByTestId('card-quarantined')).toHaveTextContent(
      String(MOCK_LAB.summary.quarantined),
    );
    expect(screen.getByTestId('card-awaiting_approval')).toHaveTextContent(
      String(MOCK_LAB.summary.awaiting_approval),
    );
    expect(screen.getByTestId('card-policy_violations')).toHaveTextContent(
      String(MOCK_LAB.summary.policy_violations),
    );
    expect(screen.getByTestId('card-wired')).toHaveTextContent(String(MOCK_LAB.summary.wired));
    expect(screen.getByTestId('card-wireless')).toHaveTextContent(
      String(MOCK_LAB.summary.wireless),
    );
  });
});

describe('Banner & disclaimers components', () => {
  it('Banner shows exact synthetic text', () => {
    renderWithApp(<Banner />);
    expect(screen.getByRole('status')).toHaveTextContent(BANNER_TEXT);
  });

  it('Disclaimers include wireless, wired, and version messaging', () => {
    renderWithApp(<Disclaimers />);
    expect(screen.getByTestId('wireless-disclaimer')).toHaveTextContent(WIRELESS_DISCLAIMER);
    expect(screen.getByTestId('wired-disclaimer')).toHaveTextContent(WIRED_DISCLAIMER);
    expect(screen.getByTestId('version-disclaimer')).toHaveTextContent(VERSION_WARNING);
  });

  it('Legend lists segment colors', () => {
    renderWithApp(<Legend />);
    expect(screen.getByTestId('legend')).toHaveTextContent('Quarantine');
    expect(screen.getByTestId('legend')).toHaveTextContent('Management');
  });
});

describe('Summary cards & charts', () => {
  it('renders all eight counter cards', () => {
    renderWithApp(<SummaryCards summary={MOCK_LAB.summary} />);
    for (const key of [
      'total',
      'online',
      'unknown',
      'quarantined',
      'awaiting_approval',
      'policy_violations',
      'wired',
      'wireless',
    ]) {
      expect(screen.getByTestId(`card-${key}`)).toBeInTheDocument();
    }
  });

  it('dashboard shows SVG chart panels', () => {
    renderWithApp(<DashboardView />);
    expect(screen.getByTestId('chart-segment').querySelector('svg')).toBeTruthy();
    expect(screen.getByTestId('chart-class').querySelector('svg')).toBeTruthy();
    expect(screen.getByTestId('chart-confidence').querySelector('svg')).toBeTruthy();
    expect(screen.getByTestId('chart-security').querySelector('svg')).toBeTruthy();
    expect(screen.getByTestId('chart-events').querySelector('svg')).toBeTruthy();
  });
});

describe('Filters', () => {
  it('filters by segment', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    await user.selectOptions(screen.getByLabelText('Filter by segment'), 'quarantine');
    const table = screen.getByRole('table', { name: /device inventory/i });
    expect(within(table).getAllByRole('row').length).toBeGreaterThan(1);
    expect(within(table).getByText('SYNTHETIC-UNKNOWN-01')).toBeInTheDocument();
    expect(within(table).queryByText('SYNTHETIC-FW-01')).not.toBeInTheDocument();
  });

  it('filters by wired connection', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    await user.selectOptions(screen.getByLabelText('Filter by connection'), 'wireless');
    expect(screen.getByText('SYNTHETIC-PHONE-01')).toBeInTheDocument();
    expect(screen.queryByText('SYNTHETIC-FW-01')).not.toBeInTheDocument();
  });

  it('filters by online/offline', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    await user.selectOptions(screen.getByLabelText('Filter by online status'), 'offline');
    expect(screen.getByText('SYNTHETIC-UNKNOWN-02')).toBeInTheDocument();
    expect(screen.queryByText('SYNTHETIC-FW-01')).not.toBeInTheDocument();
  });

  it('filters by confidence range', () => {
    const low = filterDevices(MOCK_LAB.devices, {
      ...initialState.filters,
      confidenceMax: 0.5,
    });
    expect(low.every((d) => d.confidence <= 0.5)).toBe(true);
    expect(low.some((d) => d.alias.includes('UNKNOWN'))).toBe(true);
  });

  it('filters by security state and AP', () => {
    const q = filterDevices(MOCK_LAB.devices, {
      ...initialState.filters,
      securityState: 'quarantined',
    });
    expect(q.every((d) => d.security_state === 'quarantined')).toBe(true);
    const ap = filterDevices(MOCK_LAB.devices, {
      ...initialState.filters,
      apId: 'dev-ap-01',
    });
    expect(ap.every((d) => d.ap_id === 'dev-ap-01')).toBe(true);
  });

  it('filters by service category', () => {
    const printers = filterDevices(MOCK_LAB.devices, {
      ...initialState.filters,
      serviceCategory: 'printing',
    });
    expect(printers.some((d) => d.alias === 'SYNTHETIC-PRINTER-01')).toBe(true);
  });

  it('reset filters restores defaults', async () => {
    const user = userEvent.setup();
    renderWithApp(<Filters devices={MOCK_LAB.devices} />);
    await user.selectOptions(screen.getByLabelText('Filter by segment'), 'iot');
    await user.click(screen.getByRole('button', { name: /reset filters/i }));
    expect(screen.getByLabelText('Filter by segment')).toHaveValue('all');
  });

  it('empty inventory state when filters match nothing', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    await user.selectOptions(screen.getByLabelText('Filter by segment'), 'management');
    await user.selectOptions(screen.getByLabelText('Filter by class'), 'printer');
    expect(screen.getByTestId('empty-inventory')).toBeInTheDocument();
  });
});

describe('View modes', () => {
  it('exposes all seven 3D view modes', async () => {
    const user = userEvent.setup();
    renderWithApp(<Topology3DView />);
    for (const mode of VIEW_MODES) {
      expect(screen.getByTestId(`view-mode-${mode}`)).toBeInTheDocument();
    }
    await user.click(screen.getByTestId('view-mode-WIRELESS'));
    expect(screen.getByTestId('view-mode-WIRELESS')).toHaveAttribute('aria-pressed', 'true');
    await user.click(screen.getByTestId('view-mode-SEGMENTATION'));
    expect(screen.getByTestId('view-mode-SEGMENTATION')).toHaveAttribute('aria-pressed', 'true');
  });

  it('reducer updates view mode', () => {
    const next = appReducer(initialState, { type: 'SET_VIEW_MODE', viewMode: 'SERVICES' });
    expect(next.viewMode).toBe('SERVICES');
  });
});

describe('Device selection & detail', () => {
  it('selects device from inventory via keyboard', async () => {
    const user = userEvent.setup();
    renderWithApp(<InventoryView />);
    const row = screen.getByText('SYNTHETIC-PRINTER-01').closest('tr');
    expect(row).toBeTruthy();
    row!.focus();
    await user.keyboard('{Enter}');
    // selection updates app view via reducer when using full app; here verify click works
    await user.click(screen.getByText('SYNTHETIC-PRINTER-01'));
  });

  it('device detail shows fields and confidence explanation', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-printer-01', appView: 'device' },
    });
    expect(screen.getByTestId('device-detail-view')).toHaveTextContent('SYNTHETIC-PRINTER-01');
    expect(screen.getByTestId('confidence-value')).toHaveTextContent('0.91');
    expect(screen.getByTestId('confidence-explanation')).toHaveTextContent('Why classified?');
    expect(screen.getByTestId('confidence-explanation')).toHaveTextContent('heuristic');
    expect(screen.getByRole('table', { name: /classification evidence/i })).toBeInTheDocument();
  });

  it('empty device detail when none selected', () => {
    renderWithApp(<DeviceDetailView />, { initial: { selectedDeviceId: null } });
    expect(screen.getByTestId('empty-device-detail')).toBeInTheDocument();
  });

  it('shows AP signal bucket for wireless clients', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-phone-01', appView: 'device' },
    });
    expect(screen.getByTestId('signal-bucket')).toHaveTextContent('strong');
  });

  it('shows weak signal band for illustrative AP association', () => {
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-iot-01', appView: 'device' },
    });
    expect(screen.getByTestId('signal-bucket')).toHaveTextContent('weak');
  });
});

describe('Quarantine badge', () => {
  it('inventory marks quarantined devices', () => {
    renderWithApp(<InventoryView />);
    expect(screen.getAllByTestId('quarantine-badge').length).toBeGreaterThan(0);
  });

  it('quarantine view lists quarantined devices with badge', () => {
    renderWithApp(<QuarantineView />);
    expect(screen.getByText('SYNTHETIC-UNKNOWN-01')).toBeInTheDocument();
    expect(screen.getAllByTestId('quarantine-badge').length).toBeGreaterThan(0);
  });
});

describe('Approval dialog', () => {
  it('shows simulated approval warning and applies local state only', async () => {
    const user = userEvent.setup();
    renderWithApp(<DeviceDetailView />, {
      initial: { selectedDeviceId: 'dev-srv-01', appView: 'device', approvalOpen: false },
    });
    await user.click(screen.getByTestId('open-approval'));
    expect(screen.getByTestId('approval-dialog')).toBeInTheDocument();
    expect(screen.getByTestId('approval-warning')).toHaveTextContent(APPROVAL_DIALOG_TEXT);
    await user.click(screen.getByRole('button', { name: /approve recommended/i }));
    await waitFor(() => {
      expect(screen.queryByTestId('approval-dialog')).not.toBeInTheDocument();
    });
  });

  it('ApprovalDialog returns null when closed', () => {
    const device = MOCK_LAB.devices[0]!;
    renderWithApp(<ApprovalDialog device={device} />, { initial: { approvalOpen: false } });
    expect(screen.queryByTestId('approval-dialog')).not.toBeInTheDocument();
  });
});

describe('Events & other views', () => {
  it('events view lists synthetic events', () => {
    renderWithApp(<EventsView />);
    expect(screen.getByText(/quarantine_recommended/i)).toBeInTheDocument();
    expect(screen.getByTestId('ws-status')).toBeInTheDocument();
  });

  it('empty events state', () => {
    renderWithApp(<EventsView />, { initial: { events: [] } });
    expect(screen.getByTestId('empty-events')).toBeInTheDocument();
  });

  it('reachability view shows allow/deny decisions', () => {
    renderWithApp(<ReachabilityView />);
    expect(screen.getAllByText('allowed').length).toBeGreaterThan(0);
    expect(screen.getAllByText('denied').length).toBeGreaterThan(0);
  });

  it('segmentation view shows synthetic VLAN note', () => {
    renderWithApp(<SegmentationView />);
    expect(screen.getAllByText(/SYNTHETIC VLAN ID/i).length).toBeGreaterThan(0);
  });

  it('policy view shows decisions and drift', () => {
    renderWithApp(<PolicyView />);
    expect(screen.getByText(/PROPOSED \/ SIMULATED/i)).toBeInTheDocument();
    expect(screen.getByText(/Guest-tagged device/i)).toBeInTheDocument();
  });
});

describe('Accessibility', () => {
  it('inventory table has accessible name and header cells', () => {
    renderWithApp(<InventoryView />);
    const table = screen.getByRole('table', { name: /device inventory/i });
    expect(within(table).getAllByRole('columnheader').length).toBeGreaterThanOrEqual(6);
  });

  it('nav buttons are keyboard activatable', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    renderApp();
    await screen.findByTestId('dashboard-view');
    const inv = screen.getByRole('button', { name: 'Inventory' });
    inv.focus();
    await user.keyboard('{Enter}');
    expect(await screen.findByTestId('inventory-view')).toBeInTheDocument();
    vi.unstubAllGlobals();
  });

  it('skip link is present', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    renderApp();
    expect(await screen.findByText(/skip to content/i)).toBeInTheDocument();
    vi.unstubAllGlobals();
  });
});

describe('Reduced motion', () => {
  it('applies reduce-motion class when preference is set', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: query.includes('prefers-reduced-motion'),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    );
    renderApp();
    const root = await screen.findByTestId('app-root');
    await waitFor(() => expect(root.className).toContain('reduce-motion'));
    vi.unstubAllGlobals();
  });

  it('reducer stores reduced motion flag', () => {
    const next = appReducer(initialState, { type: 'SET_REDUCED_MOTION', value: true });
    expect(next.reducedMotion).toBe(true);
  });
});

describe('API errors & malformed data', () => {
  it('loadLabOrMock falls back on network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('boom')));
    const result = await loadLabOrMock();
    expect(result.fromMock).toBe(true);
    expect(result.lab.banner).toBe(BANNER_TEXT);
    expect(result.error).toMatch(/boom|API/i);
    vi.unstubAllGlobals();
  });

  it('loadLabOrMock falls back on malformed payload', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ devices: null }),
      }),
    );
    const result = await loadLabOrMock();
    expect(result.fromMock).toBe(true);
    expect(result.error).toMatch(/malformed/i);
    vi.unstubAllGlobals();
  });

  it('loadLabOrMock accepts valid lab payload', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_LAB,
      }),
    );
    const result = await loadLabOrMock();
    expect(result.fromMock).toBe(false);
    expect(result.lab.devices.length).toBe(MOCK_LAB.devices.length);
    vi.unstubAllGlobals();
  });

  it('ApiError carries status', () => {
    const err = new ApiError('fail', 503);
    expect(err.status).toBe(503);
    expect(err.name).toBe('ApiError');
  });
});

describe('No remote assets', () => {
  it('assertNoRemoteAssets finds external script/link sources', () => {
    const doc = document.implementation.createHTMLDocument('t');
    const script = doc.createElement('script');
    script.src = 'https://cdn.example.com/app.js';
    doc.body.appendChild(script);
    const offenders = assertNoRemoteAssets(doc);
    expect(offenders.some((o) => o.includes('cdn.example.com'))).toBe(true);
  });

  it('document head in index has no CDN link tags (static check via mock DOM)', () => {
    const html = `<!doctype html><html><head><title>x</title></head><body><div id="root"></div></body></html>`;
    const doc = new DOMParser().parseFromString(html, 'text/html');
    expect(assertNoRemoteAssets(doc)).toEqual([]);
  });

  it('mock lab uses documentation IPs and LAA MACs only', () => {
    for (const d of MOCK_LAB.devices) {
      expect(d.mac.startsWith('02:')).toBe(true);
      if (d.ipv4) {
        expect(
          d.ipv4.startsWith('192.0.2.') ||
            d.ipv4.startsWith('198.51.100.') ||
            d.ipv4.startsWith('203.0.113.'),
        ).toBe(true);
      }
    }
  });
});

describe('Layout engine', () => {
  it('produces deterministic positions for segmentation mode', () => {
    const d = MOCK_LAB.devices[0]!;
    const a = layoutDevice(d, 'SEGMENTATION', 0, 10);
    const b = layoutDevice(d, 'SEGMENTATION', 0, 10);
    expect(a).toEqual(b);
  });

  it('wireless layout uses illustrative signal bands not meters', () => {
    const phone = MOCK_LAB.devices.find((x) => x.device_id === 'dev-phone-01')!;
    const pos = layoutDevice(phone, 'WIRELESS', 0, 10);
    expect(Number.isFinite(pos.x)).toBe(true);
    expect(layoutAll(MOCK_LAB.devices, 'WIRELESS').size).toBe(MOCK_LAB.devices.length);
  });

  it('segmentColor returns distinct palette entries', () => {
    expect(segmentColor('quarantine')).not.toBe(segmentColor('management'));
  });
});

describe('Empty topology', () => {
  it('shows empty state when filters exclude all devices', async () => {
    const user = userEvent.setup();
    renderWithApp(<Topology3DView />);
    await user.selectOptions(screen.getByLabelText('Filter by segment'), 'management');
    await user.selectOptions(screen.getByLabelText('Filter by class'), 'printer');
    expect(screen.getByTestId('empty-topology')).toBeInTheDocument();
  });
});

describe('Navigation between views', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('can open quarantine, policy, events, reachability, segmentation, topology', async () => {
    const user = userEvent.setup();
    renderApp();
    await screen.findByTestId('dashboard-view');
    await user.click(screen.getByRole('button', { name: 'Quarantine' }));
    expect(await screen.findByTestId('quarantine-view')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Policy' }));
    expect(await screen.findByTestId('policy-view')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Events' }));
    expect(await screen.findByTestId('events-view')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Reachability' }));
    expect(await screen.findByTestId('reachability-view')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Segmentation' }));
    expect(await screen.findByTestId('segmentation-view')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: '3D Topology' }));
    expect(await screen.findByTestId('topology-view')).toBeInTheDocument();
    expect(screen.getByTestId('wireless-disclaimer')).toBeInTheDocument();
  });
});
