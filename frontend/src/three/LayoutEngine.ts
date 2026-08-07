import type { Device, SegmentId, ViewMode } from '../models';

const SEGMENT_OFFSET: Record<SegmentId, { x: number; z: number }> = {
  management: { x: 0, z: -8 },
  infrastructure: { x: 0, z: 0 },
  trusted: { x: -8, z: 2 },
  iot: { x: 8, z: 2 },
  guest: { x: -6, z: 8 },
  quarantine: { x: 6, z: 8 },
};

const CLASS_RING: Record<string, number> = {
  firewall: 0,
  router: 0.5,
  switch: 1,
  access_point: 2,
  server: 3,
  workstation: 4,
  laptop: 4.5,
  smartphone: 5,
  tablet: 5.2,
  printer: 5.5,
  camera: 5.8,
  nas: 3.2,
  media_device: 6,
  iot: 6.5,
  network_appliance: 2.5,
  unknown: 7,
};

export interface LayoutPosition {
  x: number;
  y: number;
  z: number;
}

function hashUnit(id: string): number {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
  return (h % 1000) / 1000;
}

/** Deterministic logical layout — not physical localization. */
export function layoutDevice(
  device: Device,
  mode: ViewMode,
  index: number,
  total: number,
): LayoutPosition {
  if (mode === 'SEGMENTATION') {
    const base = SEGMENT_OFFSET[device.current_segment];
    const a = hashUnit(device.device_id) * Math.PI * 2;
    const r = 1.2 + hashUnit(device.device_id + 'r') * 2.2;
    return { x: base.x + Math.cos(a) * r, y: 0.2, z: base.z + Math.sin(a) * r };
  }

  if (mode === 'CLASSIFICATION') {
    const ring = CLASS_RING[device.device_class] ?? 7;
    const a = (index / Math.max(1, total)) * Math.PI * 2;
    return { x: Math.cos(a) * ring, y: 0.2, z: Math.sin(a) * ring };
  }

  if (mode === 'SECURITY_STATE') {
    const lane: Record<string, number> = {
      approved: -6,
      restricted: -2,
      quarantined: 2,
      uncertain: 4,
      policy_violation: 6,
      offline: 8,
      awaiting_approval: 0,
    };
    const x = lane[device.security_state] ?? 0;
    const z = (hashUnit(device.device_id) - 0.5) * 10;
    return { x, y: 0.2, z };
  }

  if (mode === 'WIRELESS') {
    if (device.device_class === 'access_point') {
      return device.position ?? { x: 0, y: 1, z: 0 };
    }
    if (device.connection_type === 'wireless' && device.ap_id) {
      // Illustrative radial placement from device id hash — NOT meters.
      const a = hashUnit(device.device_id) * Math.PI * 2;
      const band =
        device.signal_bucket === 'strong'
          ? 1.2
          : device.signal_bucket === 'good'
            ? 2.0
            : device.signal_bucket === 'moderate'
              ? 2.8
              : 3.6;
      return {
        x: (device.position?.x ?? 0) * 0.15 + Math.cos(a) * band,
        y: 0.4,
        z: (device.position?.z ?? 0) * 0.15 + Math.sin(a) * band,
      };
    }
  }

  return (
    device.position ?? {
      x: Math.cos((index / Math.max(1, total)) * Math.PI * 2) * 5,
      y: 0.2,
      z: Math.sin((index / Math.max(1, total)) * Math.PI * 2) * 5,
    }
  );
}

export function layoutAll(devices: Device[], mode: ViewMode): Map<string, LayoutPosition> {
  const map = new Map<string, LayoutPosition>();
  devices.forEach((d, i) => map.set(d.device_id, layoutDevice(d, mode, i, devices.length)));
  return map;
}

export function segmentColor(segment: SegmentId): string {
  switch (segment) {
    case 'management':
      return '#3d8bfd';
    case 'infrastructure':
      return '#2ec4b6';
    case 'trusted':
      return '#5dbe8a';
    case 'iot':
      return '#e6b84d';
    case 'guest':
      return '#9b7bff';
    case 'quarantine':
      return '#c47a4a';
    default:
      return '#9bb6bc';
  }
}

export function securityColor(state: Device['security_state']): string {
  switch (state) {
    case 'approved':
      return '#5dbe8a';
    case 'restricted':
      return '#e6b84d';
    case 'quarantined':
      return '#c47a4a';
    case 'uncertain':
      return '#9bb6bc';
    case 'policy_violation':
      return '#e06c75';
    case 'offline':
      return '#607078';
    case 'awaiting_approval':
      return '#3d8bfd';
    default:
      return '#9bb6bc';
  }
}

export function classColor(deviceClass: string): string {
  const palette = [
    '#2ec4b6',
    '#3d8bfd',
    '#5dbe8a',
    '#e6b84d',
    '#c47a4a',
    '#9b7bff',
    '#e06c75',
    '#7dd3fc',
  ];
  let h = 0;
  for (let i = 0; i < deviceClass.length; i++) h += deviceClass.charCodeAt(i);
  return palette[h % palette.length] ?? '#2ec4b6';
}
