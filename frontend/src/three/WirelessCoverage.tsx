import type { LayoutPosition } from './LayoutEngine';

interface Props {
  position: LayoutPosition;
  reducedMotion: boolean;
}

/** Illustrative coverage disc — not a physical RF model. */
export function WirelessCoverage({ position, reducedMotion }: Props) {
  return (
    <mesh position={[position.x, 0.05, position.z]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.8, reducedMotion ? 3.2 : 3.6, 48]} />
      <meshBasicMaterial color="#2ec4b6" transparent opacity={0.12} />
    </mesh>
  );
}
