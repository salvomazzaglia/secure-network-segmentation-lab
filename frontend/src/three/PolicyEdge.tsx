import { useMemo } from 'react';
import * as THREE from 'three';
import type { LayoutPosition } from './LayoutEngine';

interface Props {
  from: LayoutPosition;
  to: LayoutPosition;
  allowed: boolean;
}

export function PolicyEdge({ from, to, allowed }: Props) {
  const object = useMemo(() => {
    const points = [
      new THREE.Vector3(from.x, from.y + 0.15, from.z),
      new THREE.Vector3(to.x, to.y + 0.15, to.z),
    ];
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: allowed ? '#5dbe8a' : '#e06c75',
      transparent: true,
      opacity: 0.9,
    });
    return new THREE.Line(geometry, material);
  }, [from, to, allowed]);

  return <primitive object={object} />;
}
