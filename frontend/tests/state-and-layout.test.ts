import { describe, expect, it } from 'vitest';
import { DEFAULT_FILTERS, VIEW_MODES, BANNER_TEXT } from '../src/models';
import { MOCK_LAB, computeSummary, MOCK_DEVICES } from '../src/data/mockLab';
import { appReducer, filterDevices, initialState } from '../src/state/appState';
import {
  layoutDevice,
  layoutAll,
  classColor,
  securityColor,
  segmentColor,
} from '../src/three/LayoutEngine';

describe('models & constants', () => {
  it('defines seven view modes', () => {
    expect(VIEW_MODES).toHaveLength(7);
    expect(VIEW_MODES).toContain('POLICY_REACHABILITY');
  });

  it('default filters start open', () => {
    expect(DEFAULT_FILTERS.segment).toBe('all');
    expect(DEFAULT_FILTERS.confidenceMin).toBe(0);
    expect(DEFAULT_FILTERS.confidenceMax).toBe(1);
  });

  it('banner constant is exact', () => {
    expect(BANNER_TEXT).toBe('SYNTHETIC DEMONSTRATION DATA');
  });
});

describe('computeSummary', () => {
  it('matches device aggregates', () => {
    const s = computeSummary(MOCK_DEVICES, MOCK_LAB.events);
    expect(s.total).toBe(MOCK_DEVICES.length);
    expect(s.online + (MOCK_DEVICES.length - s.online)).toBe(s.total);
    expect(s.wired + s.wireless).toBe(s.total);
    expect(s.quarantined).toBe(MOCK_DEVICES.filter((d) => d.quarantined).length);
  });

  it('fills confidence bands', () => {
    const s = computeSummary(MOCK_DEVICES, []);
    const sum =
      (s.by_confidence_band.classified ?? 0) +
      (s.by_confidence_band.uncertain ?? 0) +
      (s.by_confidence_band.unknown ?? 0);
    expect(sum).toBe(MOCK_DEVICES.length);
  });

  it('counts events by type', () => {
    const s = computeSummary([], MOCK_LAB.events);
    expect(Object.values(s.events_by_type).reduce((a, b) => a + b, 0)).toBe(MOCK_LAB.events.length);
  });
});

describe('appReducer', () => {
  it('SET_LAB stores snapshot and clears loading', () => {
    const next = appReducer(initialState, {
      type: 'SET_LAB',
      lab: MOCK_LAB,
      fromMock: true,
      error: 'x',
    });
    expect(next.loading).toBe(false);
    expect(next.lab?.version).toBe('1.0.0');
    expect(next.fromMock).toBe(true);
    expect(next.error).toBe('x');
  });

  it('SELECT_DEVICE switches to device view', () => {
    const next = appReducer(initialState, { type: 'SELECT_DEVICE', deviceId: 'dev-fw-01' });
    expect(next.selectedDeviceId).toBe('dev-fw-01');
    expect(next.appView).toBe('device');
  });

  it('SET_FILTERS merges partial filters', () => {
    const next = appReducer(initialState, {
      type: 'SET_FILTERS',
      filters: { segment: 'iot', connection: 'wireless' },
    });
    expect(next.filters.segment).toBe('iot');
    expect(next.filters.connection).toBe('wireless');
    expect(next.filters.deviceClass).toBe('all');
  });

  it('RESET_FILTERS restores defaults', () => {
    const dirty = appReducer(initialState, {
      type: 'SET_FILTERS',
      filters: { segment: 'guest' },
    });
    const next = appReducer(dirty, { type: 'RESET_FILTERS' });
    expect(next.filters).toEqual(DEFAULT_FILTERS);
  });

  it('PUSH_EVENT prepends and caps list', () => {
    const event = MOCK_LAB.events[0]!;
    let state = initialState;
    for (let i = 0; i < 510; i++) {
      state = appReducer(state, {
        type: 'PUSH_EVENT',
        event: { ...event, event_id: `e-${i}` },
      });
    }
    expect(state.events.length).toBe(500);
    expect(state.events[0]?.event_id).toBe('e-509');
  });

  it('APPLY_APPROVAL updates segment without claiming network change', () => {
    const loaded = appReducer(initialState, {
      type: 'SET_LAB',
      lab: MOCK_LAB,
      fromMock: true,
    });
    const next = appReducer(loaded, {
      type: 'APPLY_APPROVAL',
      deviceId: 'dev-unk-01',
      chosenSegment: 'trusted',
    });
    const device = next.lab?.devices.find((d) => d.device_id === 'dev-unk-01');
    expect(device?.current_segment).toBe('trusted');
    expect(device?.awaiting_approval).toBe(false);
    expect(device?.quarantined).toBe(false);
    expect(next.approvalOpen).toBe(false);
  });

  it('APPLY_APPROVAL to quarantine sets quarantined flag', () => {
    const loaded = appReducer(initialState, {
      type: 'SET_LAB',
      lab: MOCK_LAB,
      fromMock: true,
    });
    const next = appReducer(loaded, {
      type: 'APPLY_APPROVAL',
      deviceId: 'dev-srv-01',
      chosenSegment: 'quarantine',
    });
    const device = next.lab?.devices.find((d) => d.device_id === 'dev-srv-01');
    expect(device?.quarantined).toBe(true);
    expect(device?.security_state).toBe('quarantined');
  });

  it('camera commands round-trip', () => {
    const next = appReducer(initialState, { type: 'SET_CAMERA_COMMAND', command: 'fit' });
    expect(next.cameraCommand).toBe('fit');
    expect(appReducer(next, { type: 'SET_CAMERA_COMMAND', command: 'none' }).cameraCommand).toBe(
      'none',
    );
  });
});

describe('filterDevices combinations', () => {
  it('class filter', () => {
    const out = filterDevices(MOCK_DEVICES, { ...DEFAULT_FILTERS, deviceClass: 'camera' });
    expect(out.every((d) => d.device_class === 'camera')).toBe(true);
  });

  it('online filter', () => {
    const out = filterDevices(MOCK_DEVICES, { ...DEFAULT_FILTERS, online: 'online' });
    expect(out.every((d) => d.online)).toBe(true);
  });

  it('confidence min filter', () => {
    const out = filterDevices(MOCK_DEVICES, { ...DEFAULT_FILTERS, confidenceMin: 0.9 });
    expect(out.every((d) => d.confidence >= 0.9)).toBe(true);
  });

  it('combined segment + connection', () => {
    const out = filterDevices(MOCK_DEVICES, {
      ...DEFAULT_FILTERS,
      segment: 'guest',
      connection: 'wireless',
    });
    expect(
      out.every((d) => d.current_segment === 'guest' && d.connection_type === 'wireless'),
    ).toBe(true);
  });
});

describe('LayoutEngine modes', () => {
  const sample = MOCK_DEVICES;

  it.each([
    'TOPOLOGY',
    'SEGMENTATION',
    'CLASSIFICATION',
    'SECURITY_STATE',
    'WIRELESS',
    'POLICY_REACHABILITY',
    'SERVICES',
  ] as const)('layoutAll covers all devices in %s', (mode) => {
    const map = layoutAll(sample, mode);
    expect(map.size).toBe(sample.length);
    for (const d of sample) {
      const p = map.get(d.device_id)!;
      expect(Number.isFinite(p.x + p.y + p.z)).toBe(true);
    }
  });

  it('classification layout differs from segmentation for same device', () => {
    const d = sample.find((x) => x.device_class === 'printer')!;
    const a = layoutDevice(d, 'CLASSIFICATION', 3, sample.length);
    const b = layoutDevice(d, 'SEGMENTATION', 3, sample.length);
    expect(a).not.toEqual(b);
  });

  it('security colors distinguish violation and quarantine', () => {
    expect(securityColor('policy_violation')).not.toBe(securityColor('quarantined'));
    expect(classColor('firewall')).toBeTruthy();
    expect(segmentColor('iot')).toBeTruthy();
  });
});

describe('mock topology integrity', () => {
  it('every edge endpoint exists as a device', () => {
    const ids = new Set(MOCK_LAB.devices.map((d) => d.device_id));
    for (const e of MOCK_LAB.topology.edges) {
      expect(ids.has(e.source_id)).toBe(true);
      expect(ids.has(e.target_id)).toBe(true);
    }
  });

  it('topology carries wireless and wired disclaimers', () => {
    expect(MOCK_LAB.topology.wireless_disclaimer).toMatch(/not physical localization/i);
    expect(MOCK_LAB.topology.wired_disclaimer).toMatch(/cable length/i);
  });

  it('segments use demonstration VLAN IDs only', () => {
    const vlans = MOCK_LAB.segments.map((s) => s.vlan_id).sort();
    expect(vlans).toEqual([210, 220, 230, 240, 250, 260]);
    for (const s of MOCK_LAB.segments) {
      expect(s.vlan_note).toMatch(/SYNTHETIC VLAN ID/i);
    }
  });

  it('adapters never claim connects=true', () => {
    for (const a of MOCK_LAB.adapters) {
      expect(a.connects).toBe(false);
      expect(a.dry_run).toBe(true);
    }
  });

  it('warnings include version never applies messaging', () => {
    expect(MOCK_LAB.warnings.some((w) => /never applies network changes/i.test(w))).toBe(true);
  });
});
