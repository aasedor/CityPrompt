import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';

import type { ParkLegoPalette } from './parkLegoFamilies';
import type {
  ParkMicrodetailKind,
  ParkMicrodetailPlacement,
} from './parkMicrodetailFamilies';
import { buildParkMicrodetailElementOffsets } from './parkMicrodetailFamilies';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

interface PartTransform {
  x: number;
  y: number;
  z: number;
  yaw: number;
  sx: number;
  sy: number;
  sz: number;
}

function ParkInstancedPart({
  geometry,
  transforms,
  color,
  roughness,
  metalness = 0,
  renderOrder,
}: {
  geometry: THREE.BufferGeometry;
  transforms: PartTransform[];
  color: string;
  roughness: number;
  metalness?: number;
  renderOrder: number;
}) {
  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    if (!ref.current) return;
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const zAxis = new THREE.Vector3(0, 0, 1);
    transforms.forEach((transform, index) => {
      position.set(transform.x, transform.y, transform.z);
      scale.set(transform.sx, transform.sy, transform.sz);
      rotation.setFromAxisAngle(zAxis, transform.yaw);
      matrix.compose(position, rotation, scale);
      ref.current?.setMatrixAt(index, matrix);
    });
    ref.current.count = transforms.length;
    ref.current.instanceMatrix.needsUpdate = true;
    ref.current.computeBoundingSphere();
  }, [transforms]);
  if (transforms.length === 0) return null;
  return (
    <instancedMesh
      ref={ref}
      args={[geometry, undefined, transforms.length]}
      renderOrder={renderOrder}
      frustumCulled={false}
    >
      <meshStandardMaterial
        color={color}
        roughness={roughness}
        metalness={metalness}
        side={THREE.DoubleSide}
      />
    </instancedMesh>
  );
}

function colorFor(kind: ParkMicrodetailKind, palette?: ParkLegoPalette | null): string {
  switch (kind) {
    case 'shrub': return '#536f43';
    case 'perennial': return palette?.accentSecondary ?? '#a77767';
    case 'ornamental_grass': return '#9aa16b';
    case 'reed': return '#8a9862';
    case 'boulder': return '#85847d';
    case 'riprap': return '#96938a';
    case 'light':
    case 'bin':
    case 'bike_rack':
    case 'bollard': return palette?.metal ?? '#384242';
    case 'picnic_table': return palette?.timber ?? '#8c6040';
    case 'tree_grate': return '#585f5d';
  }
}

export function GlobeParkMicrodetailInstances({
  placements,
  terrainOffsets,
  palette,
  renderOrder,
}: {
  placements: ParkMicrodetailPlacement[];
  terrainOffsets: number[] | null;
  palette?: ParkLegoPalette | null;
  renderOrder: number;
}) {
  const shrubGeometry = useMemo(() => new THREE.DodecahedronGeometry(0.55, 1), []);
  const tuftGeometry = useMemo(() => {
    const geometry = new THREE.ConeGeometry(0.44, 1, 7);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const stoneGeometry = useMemo(() => new THREE.DodecahedronGeometry(0.55, 0), []);
  const boxGeometry = useMemo(() => new THREE.BoxGeometry(1, 1, 1), []);
  const poleGeometry = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(1, 1.15, 1, 10);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const rackGeometry = useMemo(() => {
    const geometry = new THREE.TorusGeometry(0.4, 0.045, 8, 18, Math.PI);
    geometry.rotateX(Math.PI / 2);
    geometry.translate(0, 0, 0.4);
    return geometry;
  }, []);
  const grateGeometry = useMemo(() => new THREE.RingGeometry(0.26, 1, 24), []);
  useEffect(() => () => {
    shrubGeometry.dispose();
    tuftGeometry.dispose();
    stoneGeometry.dispose();
    boxGeometry.dispose();
    poleGeometry.dispose();
    rackGeometry.dispose();
    grateGeometry.dispose();
  }, [boxGeometry, grateGeometry, poleGeometry, rackGeometry, shrubGeometry, stoneGeometry, tuftGeometry]);

  const byKind = useMemo(() => {
    const result = new Map<ParkMicrodetailKind, Array<ParkMicrodetailPlacement & { z: number }>>();
    placements.forEach((placement, index) => {
      const list = result.get(placement.kind) ?? [];
      list.push({ ...placement, z: terrainOffsets?.[index] ?? 0 });
      result.set(placement.kind, list);
    });
    return result;
  }, [placements, terrainOffsets]);
  const baseZ = (z: number) => z + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const organicTransforms = (kind: ParkMicrodetailKind): PartTransform[] => (
    (byKind.get(kind) ?? []).flatMap((placement) => {
      const radius = placement.footprintRadiusM;
      const isTall = kind === 'reed' || kind === 'ornamental_grass';
      return buildParkMicrodetailElementOffsets(placement).map((element, index) => {
        const elementSize = radius * element.sizeFactor;
        return {
          x: placement.x + element.x,
          y: placement.y + element.y,
          z: baseZ(placement.z) + (isTall ? elementSize * 0.72 : elementSize * 0.4),
          yaw: element.yawRad,
          sx: elementSize,
          sy: elementSize * (0.78 + (index % 3) * 0.08),
          sz: elementSize * (isTall ? 1.55 : 0.9),
        };
      });
    })
  );
  const simpleBoxTransforms = (
    kind: ParkMicrodetailKind,
    dimensions: [number, number, number],
  ): PartTransform[] => (byKind.get(kind) ?? []).map((placement) => ({
    x: placement.x,
    y: placement.y,
    z: baseZ(placement.z) + dimensions[2] * placement.scale / 2,
    yaw: placement.yawRad,
    sx: dimensions[0] * placement.scale,
    sy: dimensions[1] * placement.scale,
    sz: dimensions[2] * placement.scale,
  }));
  const lightPoleTransforms = (byKind.get('light') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 1.8,
    yaw: placement.yawRad, sx: 0.065, sy: 0.065, sz: 3.6,
  }));
  const lightHeadTransforms = (byKind.get('light') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 3.65,
    yaw: placement.yawRad, sx: 0.34, sy: 0.24, sz: 0.16,
  }));
  const rackTransforms = (byKind.get('bike_rack') ?? []).flatMap((placement) => (
    [-0.62, 0, 0.62].map((shift) => ({
      x: placement.x + Math.cos(placement.yawRad) * shift,
      y: placement.y + Math.sin(placement.yawRad) * shift,
      z: baseZ(placement.z), yaw: placement.yawRad,
      sx: placement.scale, sy: placement.scale, sz: placement.scale,
    }))
  ));
  const bollardTransforms = (byKind.get('bollard') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 0.42,
    yaw: placement.yawRad, sx: 0.09, sy: 0.09, sz: 0.84,
  }));
  const picnicTopTransforms = simpleBoxTransforms('picnic_table', [1.8, 0.82, 0.12])
    .map((part) => ({ ...part, z: part.z + 0.68 }));
  const picnicBenchTransforms = (byKind.get('picnic_table') ?? []).flatMap((placement) => (
    [-0.82, 0.82].map((side) => ({
      x: placement.x - Math.sin(placement.yawRad) * side * placement.scale,
      y: placement.y + Math.cos(placement.yawRad) * side * placement.scale,
      z: baseZ(placement.z) + 0.46 * placement.scale,
      yaw: placement.yawRad,
      sx: 1.9 * placement.scale,
      sy: 0.28 * placement.scale,
      sz: 0.11 * placement.scale,
    }))
  ));
  const picnicLegTransforms = (byKind.get('picnic_table') ?? []).flatMap((placement) => (
    ([-0.58, 0.58] as const).flatMap((along) => (
      ([-0.26, 0.26] as const).map((across) => ({
        x: placement.x
          + Math.cos(placement.yawRad) * along * placement.scale
          - Math.sin(placement.yawRad) * across * placement.scale,
        y: placement.y
          + Math.sin(placement.yawRad) * along * placement.scale
          + Math.cos(placement.yawRad) * across * placement.scale,
        z: baseZ(placement.z) + 0.34 * placement.scale,
        yaw: placement.yawRad,
        sx: 0.12 * placement.scale,
        sy: 0.12 * placement.scale,
        sz: 0.68 * placement.scale,
      }))
    ))
  ));
  const grateTransforms = (byKind.get('tree_grate') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 0.006,
    yaw: placement.yawRad, sx: placement.footprintRadiusM, sy: placement.footprintRadiusM, sz: 1,
  }));

  return (
    <>
      {(['shrub', 'perennial'] as const).map((kind) => (
        <ParkInstancedPart key={kind} geometry={shrubGeometry} transforms={organicTransforms(kind)} color={colorFor(kind, palette)} roughness={0.98} renderOrder={renderOrder} />
      ))}
      {(['ornamental_grass', 'reed'] as const).map((kind) => (
        <ParkInstancedPart key={kind} geometry={tuftGeometry} transforms={organicTransforms(kind)} color={colorFor(kind, palette)} roughness={0.98} renderOrder={renderOrder} />
      ))}
      {(['boulder', 'riprap'] as const).map((kind) => (
        <ParkInstancedPart key={kind} geometry={stoneGeometry} transforms={organicTransforms(kind)} color={colorFor(kind, palette)} roughness={0.98} renderOrder={renderOrder} />
      ))}
      <ParkInstancedPart geometry={poleGeometry} transforms={lightPoleTransforms} color={colorFor('light', palette)} roughness={0.48} metalness={0.52} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={boxGeometry} transforms={lightHeadTransforms} color="#e4d7ae" roughness={0.35} renderOrder={renderOrder + 2} />
      <ParkInstancedPart geometry={boxGeometry} transforms={simpleBoxTransforms('bin', [0.5, 0.46, 0.86])} color={colorFor('bin', palette)} roughness={0.58} metalness={0.24} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={rackGeometry} transforms={rackTransforms} color={colorFor('bike_rack', palette)} roughness={0.44} metalness={0.56} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={poleGeometry} transforms={bollardTransforms} color={colorFor('bollard', palette)} roughness={0.56} metalness={0.42} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={boxGeometry} transforms={picnicTopTransforms} color={colorFor('picnic_table', palette)} roughness={0.84} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={boxGeometry} transforms={picnicBenchTransforms} color={colorFor('picnic_table', palette)} roughness={0.86} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={boxGeometry} transforms={picnicLegTransforms} color={palette?.benchFrame ?? '#3f403b'} roughness={0.62} metalness={0.2} renderOrder={renderOrder + 1} />
      <ParkInstancedPart geometry={grateGeometry} transforms={grateTransforms} color={colorFor('tree_grate', palette)} roughness={0.58} metalness={0.5} renderOrder={renderOrder} />
    </>
  );
}
