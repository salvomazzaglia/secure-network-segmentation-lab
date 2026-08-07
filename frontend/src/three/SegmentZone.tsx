import type { SegmentId } from '../models';
import { segmentColor } from './LayoutEngine';

const CENTERS: Record<SegmentId, [number, number, number]> = {
  management: [0, 0.02, -8],
  infrastructure: [0, 0.02, 0],
  trusted: [-8, 0.02, 2],
  iot: [8, 0.02, 2],
  guest: [-6, 0.02, 8],
  quarantine: [6, 0.02, 8],
};

interface Props {
  segmentId: SegmentId;
  visible: boolean;
}

export function SegmentZone({ segmentId, visible }: Props) {
  if (!visible) return null;
  const pos = CENTERS[segmentId];
  return (
    <mesh position={pos} rotation={[-Math.PI / 2, 0, 0]}>
      <circleGeometry args={[3.4, 48]} />
      <meshBasicMaterial color={segmentColor(segmentId)} transparent opacity={0.1} />
    </mesh>
  );
}
