import { useMemo } from 'react';
import * as THREE from 'three';
import type { LayoutPosition } from './LayoutEngine';

interface Props {
  from: LayoutPosition;
  to: LayoutPosition;
}

export function WiredEdge({ from, to }: Props) {
  const object = useMemo(() => {
    const points = [new THREE.Vector3(from.x, from.y, from.z), new THREE.Vector3(to.x, to.y, to.z)];
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: '#5ea8b2',
      transparent: true,
      opacity: 0.75,
    });
    return new THREE.Line(geometry, material);
  }, [from, to]);

  return <primitive object={object} />;
}
