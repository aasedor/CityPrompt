import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';

import type { FourWayStreetIntersection } from './streetGraphIntersections';
import { PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';
import { samplePlaneOffset, type TerrainContactPlane } from './terrainContactProfile';

export function GlobeIntersectionSignalInstances({
  node,
  metalColor,
  renderOrder,
  terrainPlane,
  terrainOffsetAt,
  frameElevation,
}: {
  node: FourWayStreetIntersection;
  metalColor: string;
  renderOrder: number;
  terrainPlane?: TerrainContactPlane | null;
  terrainOffsetAt?: (x: number, y: number) => number | null;
  frameElevation: number;
}) {
  const poles = useRef<THREE.InstancedMesh>(null);
  const heads = useRef<THREE.InstancedMesh>(null);
  const lenses = useRef<THREE.InstancedMesh>(null);
  const poleGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(0.09, 0.12, 4.2, 10);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const headGeometry = useMemo(() => new THREE.BoxGeometry(0.28, 0.30, 0.92), []);
  const lensGeometry = useMemo(() => {
    return new THREE.CylinderGeometry(0.085, 0.085, 0.035, 12);
  }, []);
  useEffect(() => () => {
    poleGeometry.dispose();
    headGeometry.dispose();
    lensGeometry.dispose();
  }, [headGeometry, lensGeometry, poleGeometry]);

  const placements = useMemo(() => {
    const axisA = { x: Math.cos(node.axisABearingRad), y: Math.sin(node.axisABearingRad) };
    const axisB = { x: Math.cos(node.axisBBearingRad), y: Math.sin(node.axisBBearingRad) };
    return [-1, 1].flatMap((sideA) => [-1, 1].flatMap((sideB) => {
      const x = axisA.x * sideA * (node.axisBHalfWidthM + 1.05)
        + axisB.x * sideB * (node.axisAHalfWidthM + 1.05);
      const y = axisA.y * sideA * (node.axisBHalfWidthM + 1.05)
        + axisB.y * sideB * (node.axisAHalfWidthM + 1.05);
      const sharedOffset = terrainOffsetAt?.(x, y);
      if (terrainOffsetAt && sharedOffset == null) return [];
      const terrainZ = sharedOffset ?? (terrainPlane
        ? terrainPlane.originZ + samplePlaneOffset(terrainPlane, x, y) - frameElevation
        : 0);
      return [{ x, y, yaw: Math.atan2(-y, -x), terrainZ }];
    }));
  }, [frameElevation, node, terrainPlane, terrainOffsetAt]);

  useEffect(() => {
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3(1, 1, 1);
    const rotation = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    let lensIndex = 0;
    placements.forEach((placement, index) => {
      rotation.setFromAxisAngle(zAxis, placement.yaw);
      position.set(
        placement.x,
        placement.y,
        placement.terrainZ + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 2.1,
      );
      matrix.compose(position, rotation, scale);
      poles.current?.setMatrixAt(index, matrix);
      position.z = placement.terrainZ + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 3.68;
      matrix.compose(position, rotation, scale);
      heads.current?.setMatrixAt(index, matrix);
      [-0.27, 0, 0.27].forEach((offsetZ) => {
        position.set(
          placement.x - Math.sin(placement.yaw) * 0.168,
          placement.y + Math.cos(placement.yaw) * 0.168,
          placement.terrainZ + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 3.68 + offsetZ,
        );
        matrix.compose(position, rotation, scale);
        lenses.current?.setMatrixAt(lensIndex++, matrix);
      });
    });
    for (const [ref, count] of [
      [poles, placements.length],
      [heads, placements.length],
      [lenses, placements.length * 3],
    ] as const) {
      if (!ref.current) continue;
      ref.current.count = count;
      ref.current.instanceMatrix.needsUpdate = true;
      ref.current.computeBoundingSphere();
    }
  }, [placements]);

  return (
    <>
      <instancedMesh ref={poles} args={[poleGeometry, undefined, placements.length]} renderOrder={renderOrder} frustumCulled={false}>
        <meshStandardMaterial color={metalColor} metalness={0.52} roughness={0.46} />
      </instancedMesh>
      <instancedMesh ref={heads} args={[headGeometry, undefined, placements.length]} renderOrder={renderOrder + 1} frustumCulled={false}>
        <meshStandardMaterial color="#202827" metalness={0.32} roughness={0.54} />
      </instancedMesh>
      <instancedMesh ref={lenses} args={[lensGeometry, undefined, placements.length * 3]} renderOrder={renderOrder + 2} frustumCulled={false}>
        <meshStandardMaterial color="#d7a83a" emissive="#5b3b12" emissiveIntensity={0.28} roughness={0.32} />
      </instancedMesh>
    </>
  );
}
