import { GlobeTreeWells } from './GlobeTreeWells';
import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { createPublicRealmPlant } from './publicRealmPlantGeometry';

import {
  PUBLIC_REALM_STREET_MARKING_LIFT_METERS,
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';
import type {
  StreetBikeRackPlacement,
  StreetBollardPlacement,
  StreetDrainPlacement,
  StreetFamilyFixturePlacements,
  StreetFixturePose,
  StreetPlantingCellPlacement,
  StreetSidewalkJointPlacement,
  StreetWasteBinPlacement,
} from './streetFamilyFurniture';

interface InstanceTransform {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  scaleX: number;
  scaleY: number;
  scaleZ: number;
}

function InstancedPart({
  geometry,
  transforms,
  color,
  renderOrder,
  metalness = 0,
  roughness = 0.85,
}: {
  geometry: THREE.BufferGeometry;
  transforms: InstanceTransform[];
  color: string;
  renderOrder: number;
  metalness?: number;
  roughness?: number;
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
      rotation.setFromAxisAngle(zAxis, transform.yawRad);
      scale.set(transform.scaleX, transform.scaleY, transform.scaleZ);
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
      <meshStandardMaterial color={geometry.getAttribute('color') ? '#ffffff' : color} vertexColors={Boolean(geometry.getAttribute('color'))} side={THREE.DoubleSide} roughness={roughness} metalness={metalness} />
    </instancedMesh>
  );
}

function poseTransform(
  placement: StreetFixturePose,
  z: number,
  scaleX: number,
  scaleY: number,
  scaleZ: number,
): InstanceTransform {
  return {
    x: placement.x,
    y: placement.y,
    z,
    yawRad: placement.yawRad,
    scaleX,
    scaleY,
    scaleZ,
  };
}

export function GlobeStreetMicrodetailInstances({
  fixtures,
  fixtureMetalColor,
  detailedPlanting = false,
  renderOrder,
}: {
  fixtures: StreetFamilyFixturePlacements;
  fixtureMetalColor: string;
  detailedPlanting?: boolean;
  renderOrder: number;
}) {
  const box = useMemo(() => new THREE.BoxGeometry(1, 1, 1), []);
  const cylinder = useMemo(() => {
    const geometry = new THREE.CylinderGeometry(1, 1, 1, 12);
    geometry.rotateX(Math.PI / 2);
    return geometry;
  }, []);
  const rack = useMemo(() => {
    const geometry = new THREE.TorusGeometry(0.42, 0.045, 8, 18, Math.PI);
    geometry.rotateX(Math.PI / 2);
    geometry.translate(0, 0, 0.42);
    return geometry;
  }, []);
  const shrub = useMemo(() => detailedPlanting ? createPublicRealmPlant('grass') : new THREE.DodecahedronGeometry(0.5, 1), [detailedPlanting]);
  useEffect(() => () => {
    box.dispose();
    cylinder.dispose();
    rack.dispose();
    shrub.dispose();
  }, [box, cylinder, rack, shrub]);

  const drainTransforms = useMemo(() => fixtures.drains.map((placement: StreetDrainPlacement) => (
    poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_MARKING_LIFT_METERS + 0.004,
      placement.lengthM,
      placement.widthM,
      0.012,
    )
  )), [fixtures.drains]);
  const jointTransforms = useMemo(() => fixtures.sidewalkJoints.map((placement: StreetSidewalkJointPlacement) => (
    poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.002,
      placement.lengthM,
      placement.widthM,
      0.006,
    )
  )), [fixtures.sidewalkJoints]);
  const binTransforms = useMemo(() => fixtures.wasteBins.map((placement: StreetWasteBinPlacement) => (
    poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.44 * placement.scale,
      0.48 * placement.scale,
      0.42 * placement.scale,
      0.88 * placement.scale,
    )
  )), [fixtures.wasteBins]);
  const rackTransforms = useMemo(() => fixtures.bikeRacks.flatMap((placement: StreetBikeRackPlacement) => (
    Array.from({ length: placement.rackCount }, (_, index) => {
      const shift = (index - (placement.rackCount - 1) / 2) * placement.spacingM;
      return {
        x: placement.x + placement.tangentX * shift,
        y: placement.y + placement.tangentY * shift,
        z: placement.z + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
        yawRad: placement.yawRad,
        scaleX: 1,
        scaleY: 1,
        scaleZ: 1,
      };
    })
  )), [fixtures.bikeRacks]);
  const bollardTransforms = useMemo(() => fixtures.bollards.map((placement: StreetBollardPlacement) => (
    poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + placement.heightM / 2,
      placement.radiusM,
      placement.radiusM,
      placement.heightM,
    )
  )), [fixtures.bollards]);
  const treeWells = useMemo(() => fixtures.plantingCells
    .filter(placement => placement.style === 'tree_grate')
    .map(placement => ({ ...placement,
      z: placement.z + (placement.surfaceLiftM ?? PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS),
    })), [fixtures.plantingCells]);
  const lowCellTransforms = useMemo(() => fixtures.plantingCells
    .filter((placement: StreetPlantingCellPlacement) => placement.style === 'low_planting_cell')
    .map((placement) => poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.035,
      placement.lengthM,
      placement.widthM,
      0.07,
    )), [fixtures.plantingCells]);
  const shrubTransforms = useMemo(() => fixtures.plantingCells
    .filter((placement: StreetPlantingCellPlacement) => placement.style === 'low_planting_cell')
    .map((placement, index) => poseTransform(
      placement,
      placement.z + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.32,
      0.78 + (index % 3) * 0.08,
      0.58 + (index % 2) * 0.08,
      0.52 + (index % 4) * 0.05,
    )), [fixtures.plantingCells]);

  return (
    <>
      <InstancedPart geometry={box} transforms={drainTransforms} color="#32383a" metalness={0.38} roughness={0.58} renderOrder={renderOrder} />
      <InstancedPart geometry={box} transforms={jointTransforms} color="#8e918e" roughness={0.92} renderOrder={renderOrder} />
      <InstancedPart geometry={box} transforms={binTransforms} color={fixtureMetalColor} metalness={0.28} roughness={0.58} renderOrder={renderOrder + 1} />
      <InstancedPart geometry={rack} transforms={rackTransforms} color={fixtureMetalColor} metalness={0.58} roughness={0.42} renderOrder={renderOrder + 1} />
      <InstancedPart geometry={cylinder} transforms={bollardTransforms} color="#d6b03c" metalness={0.18} roughness={0.62} renderOrder={renderOrder + 1} />
      <GlobeTreeWells placements={treeWells} renderOrder={renderOrder} />
      <InstancedPart geometry={box} transforms={lowCellTransforms} color="#4b3c2c" roughness={0.98} renderOrder={renderOrder} />
      <InstancedPart geometry={shrub} transforms={shrubTransforms} color="#627c4d" roughness={0.98} renderOrder={renderOrder + 1} />
    </>
  );
}
