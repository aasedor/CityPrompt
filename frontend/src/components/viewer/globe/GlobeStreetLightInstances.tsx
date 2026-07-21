import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';

import type { StreetLightPlacement } from './streetFamilyFurniture';

export function GlobeStreetLightInstances({
  placements,
  metalColor,
  renderOrder,
}: {
  placements: StreetLightPlacement[];
  metalColor: string;
  renderOrder: number;
}) {
  const poleRef = useRef<THREE.InstancedMesh>(null);
  const headRef = useRef<THREE.InstancedMesh>(null);
  const poleGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(0.07, 0.1, 5.5, 10);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const headGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(0.24, 0.17, 0.15, 12);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);

  useEffect(() => () => {
    poleGeometry.dispose();
    headGeometry.dispose();
  }, [headGeometry, poleGeometry]);

  useEffect(() => {
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3(1, 1, 1);
    const rotation = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    placements.forEach((placement, index) => {
      rotation.setFromAxisAngle(zAxis, placement.yawRad);
      position.set(placement.x, placement.y, placement.z + 2.75);
      matrix.compose(position, rotation, scale);
      poleRef.current?.setMatrixAt(index, matrix);
      position.set(placement.x, placement.y, placement.z + 5.52);
      matrix.compose(position, rotation, scale);
      headRef.current?.setMatrixAt(index, matrix);
    });
    for (const ref of [poleRef, headRef]) {
      if (!ref.current) continue;
      ref.current.count = placements.length;
      ref.current.instanceMatrix.needsUpdate = true;
      ref.current.computeBoundingSphere();
    }
  }, [placements]);

  if (placements.length === 0) return null;
  return (
    <>
      <instancedMesh
        ref={poleRef}
        args={[poleGeometry, undefined, placements.length]}
        renderOrder={renderOrder}
        frustumCulled={false}
      >
        <meshStandardMaterial color={metalColor} metalness={0.55} roughness={0.42} />
      </instancedMesh>
      <instancedMesh
        ref={headRef}
        args={[headGeometry, undefined, placements.length]}
        renderOrder={renderOrder}
        frustumCulled={false}
      >
        <meshStandardMaterial
          color="#e7d9b0"
          emissive="#7d6a40"
          emissiveIntensity={0.28}
          roughness={0.3}
        />
      </instancedMesh>
    </>
  );
}
