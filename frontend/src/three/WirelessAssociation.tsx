import { useMemo } from 'react';
import * as THREE from 'three';
import type { LayoutPosition } from './LayoutEngine';

interface Props {
  from: LayoutPosition;
  to: LayoutPosition;
  signal?: string | null;
}

export function WirelessAssociation({ from, to, signal }: Props) {
  const object = useMemo(() => {
    const mid = new THREE.Vector3(
      (from.x + to.x) / 2,
      Math.max(from.y, to.y) + 0.8,
      (from.z + to.z) / 2,
    );
    const curve = new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(from.x, from.y, from.z),
      mid,
      new THREE.Vector3(to.x, to.y, to.z),
    );
    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(16));
    const color =
      signal === 'strong'
        ? '#5dbe8a'
        : signal === 'good'
          ? '#2ec4b6'
          : signal === 'moderate'
            ? '#e6b84d'
            : '#e06c75';
    const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.85 });
    return new THREE.Line(geometry, material);
  }, [from, to, signal]);

  return <primitive object={object} />;
}
