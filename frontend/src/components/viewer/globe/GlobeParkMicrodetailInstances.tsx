import { Suspense, useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';

import type { ParkLegoPalette } from './parkLegoFamilies';
import type {
  ParkMicrodetailKind,
  ParkMicrodetailPlacement,
} from './parkMicrodetailFamilies';
import { buildParkMicrodetailElementOffsets } from './parkMicrodetailFamilies';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { SHARED_PARK_EQUIPMENT } from '@/data/sharedParkEquipment';

interface PartTransform {
  x: number;
  y: number;
  z: number;
  yaw: number;
  sx: number;
  sy: number;
  sz: number;
}

type ResolvedMicrodetailPlacement = ParkMicrodetailPlacement & { z: number };

const SHARED_EQUIPMENT = {
  bin: {
    url: SHARED_PARK_EQUIPMENT.dual_stream_bin.url,
    targetHeightM: SHARED_PARK_EQUIPMENT.dual_stream_bin.targetHeightM,
  },
  bike_rack: {
    url: SHARED_PARK_EQUIPMENT.bike_rack_three_stall.url,
    targetHeightM: SHARED_PARK_EQUIPMENT.bike_rack_three_stall.targetHeightM,
  },
  picnic_table: {
    url: SHARED_PARK_EQUIPMENT.picnic_table_accessible.url,
    targetHeightM: SHARED_PARK_EQUIPMENT.picnic_table_accessible.targetHeightM,
  },
  drinking_fountain: {
    url: SHARED_PARK_EQUIPMENT.drinking_fountain_accessible.url,
    targetHeightM: SHARED_PARK_EQUIPMENT.drinking_fountain_accessible.targetHeightM,
  },
} as const;

function ParkMicrodetailGlbInstances({
  url,
  targetHeightM,
  placements,
  renderOrder,
}: {
  url: string;
  targetHeightM: number;
  placements: ResolvedMicrodetailPlacement[];
  renderOrder: number;
}) {
  const { scene } = useGLTF(url);
  const parts = useMemo(() => {
    const bounds = new THREE.Box3().setFromObject(scene);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const scale = size.y > 0 ? targetHeightM / size.y : 1;
    const normalization = new THREE.Matrix4()
      .makeRotationX(Math.PI / 2)
      .multiply(new THREE.Matrix4().makeScale(scale, scale, scale))
      .multiply(new THREE.Matrix4().makeTranslation(-center.x, -bounds.min.y, -center.z));
    const collected: Array<{ geometry: THREE.BufferGeometry; material: THREE.Material }> = [];
    scene.updateMatrixWorld(true);
    scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      const geometry = mesh.geometry.clone();
      geometry.applyMatrix4(mesh.matrixWorld);
      geometry.applyMatrix4(normalization);
      const material = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
      collected.push({ geometry, material });
    });
    return collected;
  }, [scene, targetHeightM]);
  useEffect(() => () => parts.forEach(({ geometry }) => geometry.dispose()), [parts]);
  const transforms = useMemo<PartTransform[]>(() => placements.map((placement) => ({
    x: placement.x,
    y: placement.y,
    z: placement.z + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
    yaw: placement.yawRad,
    sx: placement.scale,
    sy: placement.scale,
    sz: placement.scale,
  })), [placements]);
  return (
    <>
      {parts.map((part, index) => (
        <ParkInstancedPart
          key={index}
          geometry={part.geometry}
          transforms={transforms}
          color="#ffffff"
          roughness={0.6}
          renderOrder={renderOrder}
          material={part.material}
        />
      ))}
    </>
  );
}

function ParkInstancedPart({
  geometry,
  transforms,
  color,
  roughness,
  metalness = 0,
  renderOrder,
  material,
}: {
  geometry: THREE.BufferGeometry;
  transforms: PartTransform[];
  color: string;
  roughness: number;
  metalness?: number;
  renderOrder: number;
  material?: THREE.Material;
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
      args={[geometry, material, transforms.length]}
      renderOrder={renderOrder}
      frustumCulled={false}
    >
      {!material && (
        <meshStandardMaterial
          color={color}
          roughness={roughness}
          metalness={metalness}
          side={THREE.DoubleSide}
        />
      )}
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
    case 'bollard':
    case 'drinking_fountain': return palette?.metal ?? '#384242';
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
  const grateGeometry = useMemo(() => new THREE.RingGeometry(0.26, 1, 24), []);
  useEffect(() => () => {
    shrubGeometry.dispose();
    tuftGeometry.dispose();
    stoneGeometry.dispose();
    boxGeometry.dispose();
    poleGeometry.dispose();
    grateGeometry.dispose();
  }, [boxGeometry, grateGeometry, poleGeometry, shrubGeometry, stoneGeometry, tuftGeometry]);

  const byKind = useMemo(() => {
    const result = new Map<ParkMicrodetailKind, ResolvedMicrodetailPlacement[]>();
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
  const lightPoleTransforms = (byKind.get('light') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 1.8,
    yaw: placement.yawRad, sx: 0.065, sy: 0.065, sz: 3.6,
  }));
  const lightHeadTransforms = (byKind.get('light') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 3.65,
    yaw: placement.yawRad, sx: 0.34, sy: 0.24, sz: 0.16,
  }));
  const bollardTransforms = (byKind.get('bollard') ?? []).map((placement) => ({
    x: placement.x, y: placement.y, z: baseZ(placement.z) + 0.42,
    yaw: placement.yawRad, sx: 0.09, sy: 0.09, sz: 0.84,
  }));
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
      <ParkInstancedPart geometry={poleGeometry} transforms={bollardTransforms} color={colorFor('bollard', palette)} roughness={0.56} metalness={0.42} renderOrder={renderOrder + 1} />
      {(Object.keys(SHARED_EQUIPMENT) as Array<keyof typeof SHARED_EQUIPMENT>).map((kind) => {
        const asset = SHARED_EQUIPMENT[kind];
        const equipmentPlacements = byKind.get(kind) ?? [];
        if (equipmentPlacements.length === 0) return null;
        return (
          <Suspense key={kind} fallback={null}>
            <ParkMicrodetailGlbInstances
              url={asset.url}
              targetHeightM={asset.targetHeightM}
              placements={equipmentPlacements}
              renderOrder={renderOrder + 1}
            />
          </Suspense>
        );
      })}
      <ParkInstancedPart geometry={grateGeometry} transforms={grateTransforms} color={colorFor('tree_grate', palette)} roughness={0.58} metalness={0.5} renderOrder={renderOrder} />
    </>
  );
}
