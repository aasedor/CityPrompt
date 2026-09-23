import { useLayoutEffect, useMemo, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { createMeadowFurniture, type MeadowFurnitureKind } from './meadowFurnitureGeometry';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

export interface MeadowFurniturePlacement {
  x: number; y: number; z: number; yawRad: number; scale: number;
}

/** Receives the existing authoritative placements, including supported base Z. */
export function GlobeMeadowFurniture({ kind, placements, renderOrder }: {
  kind: MeadowFurnitureKind;
  placements: MeadowFurniturePlacement[];
  renderOrder: number;
}) {
  const geometry = useMemo(() => createMeadowFurniture(kind), [kind]);
  const mesh = useRef<THREE.InstancedMesh>(null);
  useEffect(() => retainResourceForDeferredDisposal(geometry, owned => owned.dispose()), [geometry]);
  useLayoutEffect(() => {
    if (!mesh.current) return;
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const scale = new THREE.Vector3();
    const axis = new THREE.Vector3(0, 0, 1);
    placements.forEach((p, index) => {
      matrix.compose(position.set(p.x, p.y, p.z), rotation.setFromAxisAngle(axis, p.yawRad), scale.setScalar(p.scale));
      mesh.current!.setMatrixAt(index, matrix);
    });
    mesh.current.count = placements.length;
    mesh.current.instanceMatrix.needsUpdate = true;
    mesh.current.computeBoundingSphere();
  }, [placements, geometry]);
  if (!placements.length) return null;
  return <instancedMesh ref={mesh} args={[geometry, undefined, placements.length]} renderOrder={renderOrder}>
    <meshStandardMaterial vertexColors roughness={.78} metalness={.08} />
  </instancedMesh>;
}
