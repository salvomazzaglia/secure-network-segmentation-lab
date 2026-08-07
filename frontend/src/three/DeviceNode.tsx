import { Html } from '@react-three/drei';
import type { Device, ViewMode } from '../models';
import { classColor, securityColor, segmentColor, type LayoutPosition } from './LayoutEngine';

interface Props {
  device: Device;
  position: LayoutPosition;
  selected: boolean;
  viewMode: ViewMode;
  reducedMotion: boolean;
  onSelect: (id: string) => void;
}

function nodeColor(device: Device, viewMode: ViewMode): string {
  if (viewMode === 'SEGMENTATION') return segmentColor(device.current_segment);
  if (viewMode === 'CLASSIFICATION') return classColor(device.device_class);
  if (viewMode === 'SECURITY_STATE') return securityColor(device.security_state);
  if (viewMode === 'WIRELESS') {
    if (device.device_class === 'access_point') return '#2ec4b6';
    if (device.signal_bucket === 'strong') return '#5dbe8a';
    if (device.signal_bucket === 'good') return '#2ec4b6';
    if (device.signal_bucket === 'moderate') return '#e6b84d';
    if (device.signal_bucket === 'weak') return '#e06c75';
  }
  if (!device.online) return '#607078';
  return segmentColor(device.current_segment);
}

function geometryFor(device: Device): 'box' | 'sphere' | 'cylinder' | 'octahedron' {
  if (device.device_class === 'access_point') return 'cylinder';
  if (device.device_class === 'switch' || device.device_class === 'firewall') return 'box';
  if (device.quarantined || device.device_class === 'unknown') return 'octahedron';
  return 'sphere';
}

export function DeviceNode({
  device,
  position,
  selected,
  viewMode,
  reducedMotion,
  onSelect,
}: Props) {
  const color = nodeColor(device, viewMode);
  const geom = geometryFor(device);
  const scale = selected ? 1.25 : 1;

  return (
    <group
      position={[position.x, position.y, position.z]}
      scale={scale}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(device.device_id);
      }}
      onPointerOver={() => {
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        document.body.style.cursor = 'default';
      }}
    >
      {geom === 'box' && (
        <mesh>
          <boxGeometry args={[0.7, 0.35, 0.7]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.15} />
        </mesh>
      )}
      {geom === 'sphere' && (
        <mesh>
          <sphereGeometry args={[0.35, 16, 16]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.12} />
        </mesh>
      )}
      {geom === 'cylinder' && (
        <mesh>
          <cylinderGeometry args={[0.4, 0.4, 0.25, 20]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.18} />
        </mesh>
      )}
      {geom === 'octahedron' && (
        <mesh>
          <octahedronGeometry args={[0.4, 0]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.2} />
        </mesh>
      )}
      {!reducedMotion && device.awaiting_approval && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.55, 0.65, 24]} />
          <meshBasicMaterial color="#3d8bfd" transparent opacity={0.7} />
        </mesh>
      )}
      <Html position={[0, 0.7, 0]} center style={{ pointerEvents: 'none' }}>
        <span
          style={{
            color: '#e6f2f4',
            fontFamily: 'Segoe UI, Helvetica Neue, sans-serif',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            textShadow: '0 1px 2px #000',
          }}
        >
          {device.alias}
        </span>
      </Html>
    </group>
  );
}
