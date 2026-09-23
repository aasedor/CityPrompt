import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { createMeadowVegetation, type MeadowVegetationKind } from './meadowVegetationGeometry';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';

export interface MeadowVegetationPlacement {
  x: number; y: number; z: number; yawRad: number; scale: number;
}

/** Component library only: the owning park must supply validated terrain and
 * canopy/route clearance before placing these metre-scale prototypes. */
export function GlobeMeadowVegetation({ kind, placements, renderOrder = 145, seed = 17 }: {
  kind: MeadowVegetationKind;
  placements: MeadowVegetationPlacement[];
  renderOrder?: number;
  seed?: number;
}) {
  const geometry = useMemo(() => createMeadowVegetation(kind, seed), [kind, seed]);
  const wood = useRef<THREE.InstancedMesh>(null);
  const foliage = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    const releases = Object.values(geometry).map(g => retainResourceForDeferredDisposal(g, owned => owned.dispose()));
    return () => releases.forEach(release => release());
  }, [geometry]);
  useLayoutEffect(() => {
    const matrix = new THREE.Matrix4(), p = new THREE.Vector3(), s = new THREE.Vector3();
    const q = new THREE.Quaternion(), axis = new THREE.Vector3(0, 0, 1);
    placements.forEach((instance, i) => {
      matrix.compose(p.set(instance.x, instance.y, instance.z), q.setFromAxisAngle(axis, instance.yawRad), s.setScalar(instance.scale));
      wood.current?.setMatrixAt(i, matrix);
      foliage.current?.setMatrixAt(i, matrix);
    });
    for (const mesh of [wood.current, foliage.current]) {
      if (!mesh) continue;
      mesh.count = placements.length;
      mesh.instanceMatrix.needsUpdate = true;
      mesh.computeBoundingSphere();
    }
  }, [placements, geometry]);
  if (!placements.length) return null;
  return <>
    <instancedMesh ref={wood} args={[geometry.wood, undefined, placements.length]} renderOrder={renderOrder}>
      <meshStandardMaterial vertexColors roughness={1} />
    </instancedMesh>
    <instancedMesh ref={foliage} args={[geometry.foliage, undefined, placements.length]} renderOrder={renderOrder + 1}>
      <meshStandardMaterial vertexColors roughness={1} side={THREE.DoubleSide} />
    </instancedMesh>
  </>;
}
