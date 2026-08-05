import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';

import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { fitFixedParkProgram, type SkateParkPoint } from './skateParkFit';
import {
  archetypeOwnedParkKitForFamily,
  type ArchetypeOwnedParkKitDefinition,
} from './parkArchetypeOwnedKits';

const RENDER_ORDER = 148;

type ExactParkFamilyId =
  | 'park_inclusive_playground_v0'
  | 'park_dog_archetype_v0'
  | 'park_splash_pad_v0'
  | 'park_community_garden_v0';

interface MaterialMaps {
  map: THREE.Texture;
  normalMap: THREE.Texture;
  roughnessMap: THREE.Texture;
  aoMap: THREE.Texture;
}

function useSkinMaterial(slug: string, role: string, repeat: readonly [number, number]): MaterialMaps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({
    map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`,
    roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg`,
  });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat[0], repeat[1]);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as MaterialMaps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function MetricGlb({ url, position = [0, 0, 0], yaw = 0 }: {
  url: string; position?: [number, number, number]; yaw?: number;
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (mesh.isMesh) {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.renderOrder = RENDER_ORDER + 3;
      }
    });
    return next;
  }, [scene]);
  return (
    <group position={position} rotation={[0, 0, yaw]}>
      <group rotation={[Math.PI / 2, 0, 0]}><primitive object={clone} /></group>
    </group>
  );
}

function TexturedRect({ width, depth, z, maps, color = '#ffffff' }: {
  width: number; depth: number; z: number; maps: MaterialMaps; color?: string;
}) {
  return (
    <mesh position={[0, 0, z]} receiveShadow renderOrder={RENDER_ORDER}>
      <planeGeometry args={[width, depth]} />
      <meshStandardMaterial {...maps} color={color} roughness={0.92} normalScale={new THREE.Vector2(0.45, 0.45)} />
    </mesh>
  );
}

function TexturedEllipse({ x, y, rx, ry, z, maps, color = '#ffffff' }: {
  x: number; y: number; rx: number; ry: number; z: number; maps: MaterialMaps; color?: string;
}) {
  return (
    <mesh position={[x, y, z]} scale={[rx, ry, 1]} receiveShadow renderOrder={RENDER_ORDER + 1}>
      <circleGeometry args={[1, 64]} />
      <meshStandardMaterial {...maps} color={color} roughness={0.88} normalScale={new THREE.Vector2(0.38, 0.38)} />
    </mesh>
  );
}

function FenceRectangle({ url, width, depth, section = 6 }: {
  url: string; width: number; depth: number; section?: number;
}) {
  const horizontal = Array.from({ length: Math.max(1, Math.round(width / section)) }, (_, index) => (
    -width / 2 + width * (index + 0.5) / Math.max(1, Math.round(width / section))
  ));
  const vertical = Array.from({ length: Math.max(1, Math.round(depth / section)) }, (_, index) => (
    -depth / 2 + depth * (index + 0.5) / Math.max(1, Math.round(depth / section))
  ));
  return <>{horizontal.flatMap((x) => [
    <MetricGlb key={`n-${x}`} url={url} position={[x, depth / 2, 0.12]} />,
    <MetricGlb key={`s-${x}`} url={url} position={[x, -depth / 2, 0.12]} />,
  ])}{vertical.flatMap((y) => [
    <MetricGlb key={`e-${y}`} url={url} position={[width / 2, y, 0.12]} yaw={Math.PI / 2} />,
    <MetricGlb key={`w-${y}`} url={url} position={[-width / 2, y, 0.12]} yaw={Math.PI / 2} />,
  ])}</>;
}

function SimpleBench({ x, y, yaw = 0 }: { x: number; y: number; yaw?: number }) {
  return (
    <group position={[x, y, 0.18]} rotation={[0, 0, yaw]}>
      <mesh position={[0, 0, 0.52]}><boxGeometry args={[2.2, 0.48, 0.12]} /><meshStandardMaterial color="#8c6746" roughness={0.86} /></mesh>
      {[-0.75, 0.75].map((lx) => <mesh key={lx} position={[lx, 0, 0.25]}><boxGeometry args={[0.1, 0.38, 0.5]} /><meshStandardMaterial color="#43494a" metalness={0.35} /></mesh>)}
    </group>
  );
}

function ExactSurface({ kit }: { kit: ArchetypeOwnedParkKitDefinition }) {
  const paver = useSkinMaterial(kit.slug, 'paver', [kit.widthM / 4, kit.depthM / 4]);
  const lawn = useSkinMaterial(kit.slug, 'lawn', [kit.widthM / 5, kit.depthM / 5]);
  const safety = useSkinMaterial(kit.slug, 'safety', [kit.widthM / 4, kit.depthM / 4]);
  const planting = useSkinMaterial(kit.slug, 'planting', [kit.widthM / 3, kit.depthM / 3]);
  const asset = (name: string) => `/park-kits/${kit.slug}/${kit.assets[name]}`;

  if (kit.surfaceKind === 'inclusive_playground') return <>
    <TexturedRect width={50} depth={40} z={0} maps={paver} />
    {[
      [-12, 8, 9.45, 5.6, '#529ac1'], [0, 4, 12.15, 7.2, '#7da65c'],
      [12, -7, 9.45, 5.6, '#d68b42'], [-10, -10, 8.1, 4.8, '#c7ae75'],
      [14, 9, 6.75, 4, '#5496b7'],
    ].map(([x, y, rx, ry, color]) => <TexturedEllipse key={`${x}-${y}`} x={Number(x)} y={Number(y)} rx={Number(rx)} ry={Number(ry)} z={0.04} maps={safety} color={String(color)} />)}
    <MetricGlb url={asset('playStructure')} position={[0, 1, 0.16]} />
    <MetricGlb url={asset('swingBay')} position={[-15, 9, 0.15]} />
    <MetricGlb url={asset('spinner')} position={[14, -8, 0.15]} />
    <MetricGlb url={asset('sensoryPanel')} position={[-14, -8, 0.15]} />
    <MetricGlb url={asset('shadeCanopy')} position={[14, 9, 0.15]} />
    <SimpleBench x={-21} y={0} yaw={Math.PI / 2} /><SimpleBench x={21} y={0} yaw={-Math.PI / 2} />
  </>;

  if (kit.surfaceKind === 'dog_park') {
    const pens = [[-24, 13, 18, 12], [0, 13, 18, 12], [24, 13, 18, 12], [-18, -13, 24, 14], [18, -13, 24, 14]];
    return <>
      <TexturedRect width={80} depth={50} z={0} maps={paver} />
      {pens.map(([x, y, width, depth]) => <group key={`${x}-${y}`} position={[x, y, 0.03]}><TexturedRect width={width} depth={depth} z={0} maps={lawn} /><FenceRectangle url={asset('fence')} width={width} depth={depth} section={6} /></group>)}
      <FenceRectangle url={asset('fence')} width={72} depth={43} section={6} />
      <MetricGlb url={asset('gate')} position={[0, -21.5, 0]} />
      {[-25, 0, 25].map((x) => <MetricGlb key={x} url={asset('shade')} position={[x, 13, 0.15]} />)}
      <MetricGlb url={asset('boulders')} position={[-2, -2, 0.15]} />
    </>;
  }

  if (kit.surfaceKind === 'splash_pad') return <>
    <TexturedEllipse x={0} y={0} rx={14.8} ry={12.43} z={0} maps={paver} />
    <TexturedEllipse x={0} y={0} rx={10.6} ry={8.27} z={0.04} maps={safety} color="#718b91" />
    <MetricGlb url={asset('waterTower')} position={[3, 1, 0.18]} />
    <MetricGlb url={asset('sprayArch')} position={[-6, -2, 0.18]} />
    {[[-5, 4], [-3, 6], [0, -5], [5, -3], [7, 3]].map(([x, y]) => <MetricGlb key={`${x}-${y}`} url={asset('groundJet')} position={[x, y, 0.18]} />)}
    <FenceRectangle url={asset('fence')} width={27.5} depth={21} section={4.5} />
    <SimpleBench x={12} y={-7} yaw={2.094} />
  </>;

  const beds = [-15, -7.5, 0, 7.5, 15].flatMap((y, row) => [-15, -7.5, 0, 7.5]
    .filter((_x, column) => !(row === 4 && column >= 2)).map((x) => ({ x, y, yaw: row === 0 ? Math.PI / 2 : 0 })));
  return <>
    <TexturedRect width={50} depth={50} z={0} maps={paver} />
    <TexturedRect width={44} depth={44} z={0.025} maps={planting} color="#8a7753" />
    {beds.map(({ x, y, yaw }) => <MetricGlb key={`${x}-${y}`} url={asset('raisedBed')} position={[x, y, 0.1]} yaw={yaw} />)}
    <MetricGlb url={asset('greenhouse')} position={[15.5, 15, 0.1]} />
    <MetricGlb url={asset('trellis')} position={[15, 0, 0.1]} />
    <MetricGlb url={asset('compost')} position={[18, -15, 0.1]} />
    <FenceRectangle url={asset('fence')} width={48} depth={48} section={6} />
    <SimpleBench x={-21} y={0} yaw={Math.PI / 2} />
  </>;
}

function buildGrassBuffer(boundary: readonly SkateParkPoint[], fit: NonNullable<ReturnType<typeof fitFixedParkProgram>>) {
  const outer = new THREE.Shape();
  outer.moveTo(boundary[0].x, boundary[0].y);
  boundary.slice(1).forEach(({ x, y }) => outer.lineTo(x, y));
  outer.closePath();
  const cos = Math.cos(fit.rotationRad); const sin = Math.sin(fit.rotationRad);
  const corners = [[-fit.widthM / 2, -fit.depthM / 2], [-fit.widthM / 2, fit.depthM / 2], [fit.widthM / 2, fit.depthM / 2], [fit.widthM / 2, -fit.depthM / 2]]
    .map(([x, y]) => ({ x: fit.center.x + x * cos - y * sin, y: fit.center.y + x * sin + y * cos }));
  const hole = new THREE.Path(); hole.moveTo(corners[0].x, corners[0].y);
  corners.slice(1).forEach(({ x, y }) => hole.lineTo(x, y)); hole.closePath(); outer.holes.push(hole);
  const geometry = new THREE.ShapeGeometry(outer, 24);
  const uv = geometry.getAttribute('uv'); if (uv) geometry.setAttribute('uv1', uv.clone());
  return geometry;
}

export function GlobeArchetypeOwnedParkAssembly({ familyId, boundary, terrainZ }: {
  familyId: ExactParkFamilyId; boundary: readonly SkateParkPoint[]; terrainZ: (x: number, y: number) => number;
}) {
  const kit = archetypeOwnedParkKitForFamily(familyId);
  const fit = useMemo(() => kit ? fitFixedParkProgram(boundary, kit) : null, [boundary, kit]);
  const grassGeometry = useMemo(() => fit ? buildGrassBuffer(boundary, fit) : null, [boundary, fit]);
  useEffect(() => () => grassGeometry?.dispose(), [grassGeometry]);
  const lawn = useSkinMaterial(kit?.slug ?? 'skate-park', 'lawn', [8, 8]);
  if (!kit || !fit || !grassGeometry) return null;
  const baseZ = terrainZ(fit.center.x, fit.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  return <group renderOrder={RENDER_ORDER}>
    <mesh geometry={grassGeometry} position={[0, 0, baseZ - 0.015]} receiveShadow><meshStandardMaterial {...lawn} roughness={0.96} /></mesh>
    <group position={[fit.center.x, fit.center.y, baseZ]} rotation={[0, 0, fit.rotationRad]}>
      <ExactSurface kit={kit} />
    </group>
  </group>;
}
