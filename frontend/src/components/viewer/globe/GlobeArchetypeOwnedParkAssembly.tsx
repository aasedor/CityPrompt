import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';

import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch16ParkSkinForSelection } from './parkBatch16Skins';
import { batch17ParkSkinForSelection, parkGlbMaterialRole, type ParkSkinRole } from './parkBatch17Skins';
import { batch21ParkSkinForSelection } from './parkBatch21Skins';
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
  | 'park_community_garden_v0'
  | 'park_tennis_cluster_v0'
  | 'park_nature_play_v0'
  | 'park_pump_track_v0'
  | 'park_outdoor_fitness_v0'
  | 'park_memorial_garden_v0'
  | 'park_pickleball_community_v1'
  | 'park_track_oval_school_v2'
  | 'park_baseball_club_hub_v1'
  | 'park_cricket_village_green_v0'
  | 'park_sports_complex_tournament_v0';

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

function MetricGlb({ url, position = [0, 0, 0], yaw = 0, materialMaps }: {
  url: string;
  position?: [number, number, number];
  yaw?: number;
  materialMaps?: Readonly<Partial<Record<ParkSkinRole, MaterialMaps>>>;
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    const ownedMaterials: THREE.Material[] = [];
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (mesh.isMesh) {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.renderOrder = RENDER_ORDER + 3;
        const reskin = (source: THREE.Material): THREE.Material => {
          const role = parkGlbMaterialRole(source.name);
          const maps = role ? materialMaps?.[role] : null;
          if (!maps || !(source instanceof THREE.MeshStandardMaterial)) return source;
          const material = source.clone();
          material.color.set('#ffffff');
          material.map = maps.map;
          material.normalMap = maps.normalMap;
          material.roughnessMap = maps.roughnessMap;
          material.aoMap = maps.aoMap;
          material.roughness = 0.92;
          material.normalScale.set(0.45, 0.45);
          material.needsUpdate = true;
          ownedMaterials.push(material);
          return material;
        };
        mesh.material = Array.isArray(mesh.material)
          ? mesh.material.map(reskin)
          : reskin(mesh.material);
      }
    });
    return { root: next, ownedMaterials };
  }, [materialMaps, scene]);
  useEffect(
    () => () => clone.ownedMaterials.forEach((material) => material.dispose()),
    [clone],
  );
  return (
    <group position={position} rotation={[0, 0, yaw]}>
      <group rotation={[Math.PI / 2, 0, 0]}><primitive object={clone.root} /></group>
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

function GroundLine({ x = 0, y = 0, width, depth, color = '#f1f0e8' }: {
  x?: number; y?: number; width: number; depth: number; color?: string;
}) {
  return <mesh position={[x, y, 0.075]} renderOrder={RENDER_ORDER + 2}>
    <boxGeometry args={[width, depth, 0.025]} />
    <meshStandardMaterial color={color} roughness={0.78} />
  </mesh>;
}

function GroundDot({ x, y = 0, radius = 0.12, color = '#f1f0e8' }: {
  x: number; y?: number; radius?: number; color?: string;
}) {
  return <mesh position={[x, y, 0.077]} renderOrder={RENDER_ORDER + 2}>
    <circleGeometry args={[radius, 20]} />
    <meshStandardMaterial color={color} roughness={0.78} side={THREE.DoubleSide} />
  </mesh>;
}

function MowingStripes({ widthM, depthM }: { widthM: number; depthM: number }) {
  const stripeWidth = widthM / 10;
  return <>{Array.from({ length: 10 }, (_, index) => (
    <mesh
      key={index}
      position={[-widthM / 2 + stripeWidth * (index + 0.5), 0, 0.024]}
      renderOrder={RENDER_ORDER + 1}
    >
      <planeGeometry args={[stripeWidth, depthM]} />
      <meshStandardMaterial
        color={index % 2 ? '#d7e4c8' : '#76955f'}
        transparent
        opacity={index % 2 ? 0.08 : 0.05}
        roughness={0.96}
        depthWrite={false}
      />
    </mesh>
  ))}</>;
}

function SoccerMarkings({ widthM, depthM, smallSided = false }: {
  widthM: number; depthM: number; smallSided?: boolean;
}) {
  const halfLength = widthM / 2;
  const halfWidth = depthM / 2;
  const penaltyDepth = smallSided ? 5 : 16.5;
  const penaltyWidth = smallSided ? 10 : 40.32;
  const goalAreaDepth = 5.5;
  const goalAreaWidth = 18.32;
  const circleRadius = smallSided ? 3 : 9.15;
  const line = 0.1;
  return <>
    <GroundLine x={-halfLength} width={line} depth={depthM} />
    <GroundLine x={halfLength} width={line} depth={depthM} />
    <GroundLine y={-halfWidth} width={widthM} depth={line} />
    <GroundLine y={halfWidth} width={widthM} depth={line} />
    <GroundLine width={line} depth={depthM} />
    {[-1, 1].map((side) => <group key={side} position={[side * (halfLength - penaltyDepth / 2), 0, 0]}>
      <GroundLine width={penaltyDepth} depth={line} y={-penaltyWidth / 2} />
      <GroundLine width={penaltyDepth} depth={line} y={penaltyWidth / 2} />
      <GroundLine width={line} depth={penaltyWidth} x={-side * penaltyDepth / 2} />
    </group>)}
    {!smallSided && [-1, 1].map((side) => <group key={`goal-area-${side}`} position={[side * (halfLength - goalAreaDepth / 2), 0, 0]}>
      <GroundLine width={goalAreaDepth} depth={line} y={-goalAreaWidth / 2} />
      <GroundLine width={goalAreaDepth} depth={line} y={goalAreaWidth / 2} />
      <GroundLine width={line} depth={goalAreaWidth} x={-side * goalAreaDepth / 2} />
      <GroundDot x={-side * (goalAreaDepth / 2 + 5.5)} />
    </group>)}
    <mesh position={[0, 0, 0.076]} renderOrder={RENDER_ORDER + 2}>
      <ringGeometry args={[circleRadius - line, circleRadius, 48]} />
      <meshStandardMaterial color="#f1f0e8" roughness={0.78} side={THREE.DoubleSide} />
    </mesh>
  </>;
}

function SoccerGoal({ x, goalWidthM, goalHeightM }: {
  x: number; goalWidthM: number; goalHeightM: number;
}) {
  return <group position={[x, 0, 0.08]}>
    {[-goalWidthM / 2, goalWidthM / 2].map((y) => <mesh key={y} position={[0, y, goalHeightM / 2]}>
      <boxGeometry args={[0.1, 0.1, goalHeightM]} />
      <meshStandardMaterial color="#eef0ea" roughness={0.66} />
    </mesh>)}
    <mesh position={[0, 0, goalHeightM]}><boxGeometry args={[0.1, goalWidthM, 0.1]} /><meshStandardMaterial color="#eef0ea" roughness={0.66} /></mesh>
    <mesh position={[0.55 * Math.sign(x), 0, goalHeightM / 2]} rotation={[0, Math.PI / 2, 0]}>
      <planeGeometry args={[goalWidthM, Math.hypot(goalHeightM, 1.1), 12, 5]} />
      <meshStandardMaterial color="#e3e7df" wireframe transparent opacity={0.32} side={THREE.DoubleSide} depthWrite={false} />
    </mesh>
  </group>;
}

function Floodlight({ x, y, heightM = 10 }: { x: number; y: number; heightM?: number }) {
  return <group position={[x, y, 0.08]}>
    <mesh position={[0, 0, heightM / 2]}><cylinderGeometry args={[0.08, 0.13, heightM, 10]} /><meshStandardMaterial color="#50595a" metalness={0.54} roughness={0.5} /></mesh>
    <mesh position={[0, 0, heightM]}><boxGeometry args={[2.2, 0.22, 0.22]} /><meshStandardMaterial color="#51595b" metalness={0.48} roughness={0.5} /></mesh>
    {[-0.72, 0, 0.72].map((lampX) => <mesh key={lampX} position={[lampX, 0.16, heightM]}><boxGeometry args={[0.4, 0.24, 0.3]} /><meshStandardMaterial color="#d9ddd4" roughness={0.38} /></mesh>)}
  </group>;
}

function CagedPitchEnclosure({ widthM, depthM }: { widthM: number; depthM: number }) {
  const heightM = 3.6;
  const boardHeightM = 1.05;
  const panels = Math.max(4, Math.ceil(widthM / 4));
  const endPanels = Math.max(3, Math.ceil(depthM / 4));
  const meshMaterial = <meshStandardMaterial color="#313b39" wireframe transparent opacity={0.42} side={THREE.DoubleSide} depthWrite={false} />;
  return <>
    {[-1, 1].map((side) => <group key={`long-${side}`} position={[0, side * depthM / 2, 0]}>
      <mesh position={[0, 0, boardHeightM / 2]}><boxGeometry args={[widthM, 0.09, boardHeightM]} /><meshStandardMaterial color="#e4e1d5" roughness={0.78} /></mesh>
      <mesh position={[0, 0, boardHeightM + (heightM - boardHeightM) / 2]}><planeGeometry args={[widthM, heightM - boardHeightM, panels * 3, 6]} />{meshMaterial}</mesh>
    </group>)}
    {[-1, 1].map((side) => <group key={`end-${side}`} position={[side * widthM / 2, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
      <mesh position={[0, 0, boardHeightM / 2]}><boxGeometry args={[depthM, 0.09, boardHeightM]} /><meshStandardMaterial color="#e4e1d5" roughness={0.78} /></mesh>
      <mesh position={[0, 0, boardHeightM + (heightM - boardHeightM) / 2]}><planeGeometry args={[depthM, heightM - boardHeightM, endPanels * 3, 6]} />{meshMaterial}</mesh>
    </group>)}
    {[-widthM / 2, 0, widthM / 2].flatMap((x) => [-depthM / 2, depthM / 2].map((y) => <mesh key={`${x}-${y}`} position={[x, y, heightM / 2]}><boxGeometry args={[0.11, 0.11, heightM]} /><meshStandardMaterial color="#303938" metalness={0.42} roughness={0.56} /></mesh>))}
  </>;
}

function BasketballMarkings({ halfCourt = false, lineColor = '#f1f0e8' }: {
  halfCourt?: boolean; lineColor?: string;
}) {
  const playingLength = halfCourt ? 14 : 28;
  const playingWidth = 15;
  const halfLength = playingLength / 2;
  const halfWidth = playingWidth / 2;
  const line = 0.10;
  const directions = halfCourt ? [-1] : [-1, 1];
  return <>
    <GroundLine x={-halfLength} width={line} depth={playingWidth} color={lineColor} />
    <GroundLine x={halfLength} width={line} depth={playingWidth} color={lineColor} />
    <GroundLine y={-halfWidth} width={playingLength} depth={line} color={lineColor} />
    <GroundLine y={halfWidth} width={playingLength} depth={line} color={lineColor} />
    {!halfCourt && <>
      <GroundLine width={line} depth={playingWidth} color={lineColor} />
      <mesh position={[0, 0, 0.077]} renderOrder={RENDER_ORDER + 2}>
        <ringGeometry args={[1.70, 1.80, 48]} />
        <meshStandardMaterial color={lineColor} roughness={0.78} side={THREE.DoubleSide} />
      </mesh>
    </>}
    {halfCourt && <mesh position={[halfLength, 0, 0.077]} renderOrder={RENDER_ORDER + 2}>
      <ringGeometry args={[1.70, 1.80, 32, 1, Math.PI / 2, Math.PI]} />
      <meshStandardMaterial color={lineColor} roughness={0.78} side={THREE.DoubleSide} />
    </mesh>}
    {directions.map((direction) => {
      const baselineX = direction * halfLength;
      const freeThrowX = baselineX - direction * 5.8;
      const basketX = baselineX - direction * 1.575;
      const arcStart = direction < 0 ? -1.18 : Math.PI - 1.18;
      return <group key={direction}>
        <GroundLine x={(baselineX + freeThrowX) / 2} y={-2.45} width={5.8} depth={line} color={lineColor} />
        <GroundLine x={(baselineX + freeThrowX) / 2} y={2.45} width={5.8} depth={line} color={lineColor} />
        <GroundLine x={freeThrowX} width={line} depth={4.9} color={lineColor} />
        <mesh position={[freeThrowX, 0, 0.077]} renderOrder={RENDER_ORDER + 2}>
          <ringGeometry args={[1.70, 1.80, 36]} />
          <meshStandardMaterial color={lineColor} roughness={0.78} side={THREE.DoubleSide} />
        </mesh>
        <mesh position={[basketX, 0, 0.078]} renderOrder={RENDER_ORDER + 2}>
          <ringGeometry args={[6.65, 6.75, 56, 1, arcStart, 2.36]} />
          <meshStandardMaterial color={lineColor} roughness={0.78} side={THREE.DoubleSide} />
        </mesh>
      </group>;
    })}
  </>;
}

function BasketballSurfaceArt({ variantIndex, halfCourt }: {
  variantIndex: number; halfCourt: boolean;
}) {
  if (variantIndex === 0) return null;
  if (variantIndex === 1) {
    const halfLength = halfCourt ? 7 : 14;
    return <>{(halfCourt ? [-1] : [-1, 1]).map((side) => (
      <mesh key={side} position={[side * (halfLength - 2.9), 0, 0.057]} renderOrder={RENDER_ORDER + 1}>
        <planeGeometry args={[5.8, 4.9]} />
        <meshStandardMaterial color="#a64f42" roughness={0.82} />
      </mesh>
    ))}</>;
  }
  const colors = variantIndex === 2
    ? ['#182d53', '#d3983f', '#cc5c3e', '#2f7590', '#142847', '#e0ad50']
    : ['#9e5145', '#39747a', '#d09840', '#385f84', '#75526b'];
  const pieces = variantIndex === 2 ? [
    [-4.6, -4.6, 5.4, 2.5, -0.28], [-0.6, -3.3, 5.8, 2.2, 0.22],
    [3.6, -2.7, 4.0, 2.0, -0.36], [-3.4, 0.0, 5.8, 2.2, 0.35],
    [0.5, 1.0, 6.4, 2.3, -0.22], [3.8, 4.2, 4.0, 1.9, 0.25],
    [-1.8, 4.6, 4.8, 1.8, -0.16],
  ] : [
    [-8.7, -4.8, 4.2, 1.2, -0.32], [-3.8, 3.6, 3.8, 1.1, 0.28],
    [1.2, -2.8, 4.6, 1.2, -0.18], [5.2, 3.0, 4.2, 1.1, 0.34],
    [9.4, -4.0, 3.8, 1.0, -0.25], [0.0, 5.4, 4.0, 1.1, 0.10],
  ];
  return <>{pieces.map(([x, y, width, depth, yaw], index) => (
    <mesh key={index} position={[x, y, 0.058]} rotation={[0, 0, yaw]} renderOrder={RENDER_ORDER + 1}>
      <planeGeometry args={[width, depth]} />
      <meshStandardMaterial color={colors[index % colors.length]} transparent opacity={variantIndex === 3 ? 0.54 : 0.88} roughness={0.9} depthWrite={false} />
    </mesh>
  ))}</>;
}

function BasketballFence({ widthM, depthM, variantIndex }: {
  widthM: number; depthM: number; variantIndex: number;
}) {
  const wall = variantIndex === 2;
  const street = variantIndex === 3;
  const fenceHeight = wall ? 2.25 : variantIndex === 1 ? 3.6 : 3.05;
  const meshColor = variantIndex === 1 ? '#172222' : '#58605d';
  const longSides = street ? [1] : [-1, 1];
  const endSides = street ? [-1] : [-1, 1];
  const mesh = <meshStandardMaterial color={meshColor} wireframe transparent opacity={variantIndex === 1 ? 0.54 : 0.42} side={THREE.DoubleSide} depthWrite={false} roughness={0.78} />;
  return <>
    {wall && <>
      {[-1, 1].map((side) => <mesh key={`wall-long-${side}`} position={[0, side * depthM / 2, 0.52]}><boxGeometry args={[widthM, 0.34, 1.04]} /><meshStandardMaterial color="#9c9a92" roughness={0.92} /></mesh>)}
      <mesh position={[-widthM / 2, 0, 0.52]}><boxGeometry args={[0.34, depthM, 1.04]} /><meshStandardMaterial color="#9c9a92" roughness={0.92} /></mesh>
    </>}
    {longSides.map((side) => <mesh key={`long-${side}`} position={[0, side * depthM / 2, (wall ? 1.04 : 0) + fenceHeight / 2]}>
      <planeGeometry args={[widthM, fenceHeight, Math.max(12, Math.ceil(widthM)), 8]} />{mesh}
    </mesh>)}
    {endSides.map((side) => <mesh key={`end-${side}`} position={[side * widthM / 2, 0, (wall ? 1.04 : 0) + fenceHeight / 2]} rotation={[0, Math.PI / 2, 0]}>
      <planeGeometry args={[depthM, fenceHeight, Math.max(10, Math.ceil(depthM)), 8]} />{mesh}
    </mesh>)}
    {[-widthM / 2, 0, widthM / 2].flatMap((x) => [-depthM / 2, depthM / 2].map((y) => (
      <mesh key={`${x}-${y}`} position={[x, y, (wall ? 1.04 : 0) + fenceHeight / 2]}>
        <boxGeometry args={[0.10, 0.10, fenceHeight + (wall ? 1.04 : 0)]} />
        <meshStandardMaterial color={meshColor} metalness={0.42} roughness={0.58} />
      </mesh>
    )))}
    {street && Array.from({ length: 6 }, (_, index) => (
      <mesh key={`graffiti-${index}`} position={[-widthM / 2 + 3.1 + index * 5.0, depthM / 2 - 0.04, 1.25]}>
        <planeGeometry args={[4.4, 1.55]} />
        <meshStandardMaterial color={['#8f4b43', '#d09a41', '#3e7778', '#6f526c'][index % 4]} roughness={0.9} side={THREE.DoubleSide} />
      </mesh>
    ))}
  </>;
}

export interface RegulationParkModule {
  x: number;
  y: number;
  rotationZ: number;
  widthM: number;
  depthM: number;
}

export type RegulationParkFamilyId =
  | 'park_basketball_court_v0'
  | 'park_tennis_cluster_v0'
  | 'park_caged_soccer_v0'
  | 'park_athletics_fields_v0';

/** Regulation surfaces are archetype-skinned LEGO modules. Their dimensions
 * come from fitted metric guides, so larger polygons receive more complete
 * modules rather than one distorted court or field. */
export function GlobeRegulationParkAssembly({ familyId, modules, terrainZ, variantId }: {
  familyId: RegulationParkFamilyId;
  modules: readonly RegulationParkModule[];
  terrainZ: (x: number, y: number) => number;
  variantId?: string;
}) {
  const basketballVariantIndex = familyId === 'park_basketball_court_v0'
    ? Number(variantId?.match(/_v([0-3])$/)?.[1] ?? 0)
    : 0;
  const basketballSlug = [
    'basketball-classic-asphalt',
    'basketball-pro-acrylic',
    'basketball-community-mural',
    'basketball-urban-streetball',
  ][basketballVariantIndex] ?? 'basketball-classic-asphalt';
  const batch16Slug = batch16ParkSkinForSelection(
    familyId === 'park_tennis_cluster_v0' ? 'tennis_court_cluster' : '',
    variantId ?? '',
  )?.slug;
  const batch17Slug = batch17ParkSkinForSelection(
    familyId === 'park_caged_soccer_v0' ? 'soccer_pitch_caged' : '',
    variantId ?? '',
  )?.slug;
  const batch21Slug = batch21ParkSkinForSelection(
    familyId === 'park_athletics_fields_v0' ? 'athletics_precinct_sports_fields' : '',
    variantId ?? '',
  )?.slug;
  const tennisVariantIndex = familyId === 'park_tennis_cluster_v0'
    ? Number(variantId?.match(/_v([0-3])$/)?.[1] ?? 0)
    : 0;
  const slug = familyId === 'park_basketball_court_v0' ? basketballSlug
    : familyId === 'park_tennis_cluster_v0' ? (batch16Slug ?? 'tennis-court-professional')
    : familyId === 'park_caged_soccer_v0' ? (batch17Slug ?? 'caged-soccer-european')
      : (batch21Slug ?? 'athletics-fields-regulation');
  const basketballSurfaceRole = basketballVariantIndex === 0 || basketballVariantIndex === 3
    ? 'asphalt'
    : basketballVariantIndex === 1 ? 'paver' : 'asphalt';
  const surface = useSkinMaterial(slug, familyId === 'park_athletics_fields_v0' ? 'lawn'
    : familyId === 'park_basketball_court_v0' ? basketballSurfaceRole : 'safety', [8, 5]);
  const edgeRole = familyId === 'park_basketball_court_v0'
    ? basketballVariantIndex === 1 ? 'safety' : 'paver'
    : familyId === 'park_caged_soccer_v0' ? 'asphalt'
    : familyId === 'park_athletics_fields_v0' ? 'lawn'
      : 'planting';
  const edge = useSkinMaterial(slug, edgeRole, [6, 4]);
  const tennisKit = archetypeOwnedParkKitForFamily('park_tennis_cluster_v0');
  const tennisAsset = (name: string) => tennisKit ? `/park-kits/${tennisKit.slug}/${tennisKit.assets[name]}` : '';
  if (modules.length === 0) return null;

  return <group renderOrder={RENDER_ORDER}>
    {modules.map((module, index) => {
      const cos = Math.cos(module.rotationZ);
      const sin = Math.sin(module.rotationZ);
      const sampleOffsets = [-0.5, 0, 0.5];
      const terrainSamples = sampleOffsets.flatMap((unitX) => sampleOffsets.map((unitY) => {
        const localX = unitX * module.widthM;
        const localY = unitY * module.depthM;
        return terrainZ(
          module.x + localX * cos - localY * sin,
          module.y + localX * sin + localY * cos,
        );
      }));
      // Regulation courts and pitches must remain planar. Seat the complete
      // module above the highest sampled terrain point so a sloping tile or
      // residual landscape cannot clip through half of the playing surface.
      const baseZ = Math.max(...terrainSamples) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
      if (familyId === 'park_basketball_court_v0') {
        const halfCourt = basketballVariantIndex === 2;
        const playingLength = halfCourt ? 14 : 28;
        // `color` multiplies the source-derived albedo. Keep the tint light
        // enough for aggregate, repairs and court wear to remain legible in
        // the Google-tile scene instead of collapsing into a flat near-black.
        const surfaceTint = basketballVariantIndex === 1 ? '#86c8e4'
          : basketballVariantIndex === 2 ? '#6f91bd'
            : basketballVariantIndex === 3 ? '#b9b5ad'
              : '#e0dfda';
        const apronTint = basketballVariantIndex === 1 ? '#f1d2cb'
          : basketballVariantIndex === 2 ? '#d4d0c7'
            : basketballVariantIndex === 3 ? '#c6c0b7'
              : '#d5d3cc';
        return <group key={index} position={[module.x, module.y, baseZ]} rotation={[0, 0, module.rotationZ]}>
          <TexturedRect width={module.widthM} depth={module.depthM} z={-0.01} maps={edge} color={apronTint} />
          <TexturedRect width={playingLength} depth={15} z={0.02} maps={surface} color={surfaceTint} />
          <BasketballSurfaceArt variantIndex={basketballVariantIndex} halfCourt={halfCourt} />
          <BasketballMarkings halfCourt={halfCourt} lineColor={basketballVariantIndex === 3 ? '#ddd8ca' : '#f1f0e8'} />
          <BasketballFence widthM={module.widthM + 0.5} depthM={module.depthM + 0.5} variantIndex={basketballVariantIndex} />
          {basketballVariantIndex === 0 && <>
            <SimpleBench x={0} y={module.depthM / 2 + 1.2} />
            {[[-module.widthM / 2 + 2.2, -module.depthM / 2 - 0.7], [module.widthM / 2 - 2.2, module.depthM / 2 + 0.7]].map(([x, y]) => <Floodlight key={`${x}-${y}`} x={x} y={y} heightM={10} />)}
          </>}
          {basketballVariantIndex === 1 && <>
            {[0, 1, 2].map((row) => <mesh key={row} position={[0, module.depthM / 2 + 1.15 + row * 0.72, 0.16 + row * 0.30]}>
              <boxGeometry args={[8.4, 0.64, 0.26]} /><meshStandardMaterial color={row % 2 ? '#7f8787' : '#a0a6a5'} metalness={0.36} roughness={0.58} />
            </mesh>)}
            <group position={[0, module.depthM / 2 + 0.35, 3.1]}>
              <mesh><boxGeometry args={[3.3, 0.20, 1.45]} /><meshStandardMaterial color="#202526" roughness={0.64} /></mesh>
              <mesh position={[0, -0.12, 0]} rotation={[Math.PI / 2, 0, 0]}><planeGeometry args={[2.8, 1.0]} /><meshStandardMaterial color="#9b372d" emissive="#2a0805" emissiveIntensity={0.18} /></mesh>
            </group>
            {[[-module.widthM / 2 + 2.2, -module.depthM / 2 - 0.8], [-module.widthM / 2 + 2.2, module.depthM / 2 + 0.8], [module.widthM / 2 - 2.2, -module.depthM / 2 - 0.8], [module.widthM / 2 - 2.2, module.depthM / 2 + 0.8]].map(([x, y]) => <Floodlight key={`${x}-${y}`} x={x} y={y} heightM={11} />)}
          </>}
          {basketballVariantIndex === 2 && <>
            <mesh position={[module.widthM / 2 + 0.55, 0, 0.52]}><boxGeometry args={[0.95, module.depthM - 1.4, 1.04]} /><meshStandardMaterial color="#99968e" roughness={0.92} /></mesh>
            <mesh position={[module.widthM / 2 + 0.12, 0, 1.10]}><boxGeometry args={[0.42, module.depthM - 2.0, 0.13]} /><meshStandardMaterial color="#8b6645" roughness={0.86} /></mesh>
          </>}
          {basketballVariantIndex === 3 && <>
            {[0, 1, 2].map((row) => <mesh key={row} position={[0, -module.depthM / 2 - 0.7 - row * 0.72, 0.15 + row * 0.28]}>
              <boxGeometry args={[10.5, 0.68, 0.28]} /><meshStandardMaterial color={row % 2 ? '#85827b' : '#aaa69c'} roughness={0.94} />
            </mesh>)}
            {[[-module.widthM / 2 + 3, module.depthM / 2 + 0.7], [module.widthM / 2 - 3, module.depthM / 2 + 0.7]].map(([x, y]) => <Floodlight key={`${x}-${y}`} x={x} y={y} heightM={9} />)}
          </>}
        </group>;
      }
      if (familyId === 'park_tennis_cluster_v0') return <group key={index} position={[module.x, module.y, baseZ]} rotation={[0, 0, module.rotationZ]}>
        {/* `color` multiplies the source albedo. Keep these near-white so the
            card-derived aggregate, turf and weathering remain legible. */}
        <TexturedRect width={module.widthM + 2} depth={module.depthM + 2} z={-0.01} maps={edge} color={['#d9e6d2', '#e2ead8', '#e8e4d5', '#d9dde1'][tennisVariantIndex]} />
        <TexturedRect width={module.widthM} depth={module.depthM} z={0.02} maps={surface} color={['#cfdfeb', '#dcead2', '#e7e3d5', '#dce2eb'][tennisVariantIndex]} />
        <GroundLine x={-11.885} width={0.055} depth={10.97} /><GroundLine x={11.885} width={0.055} depth={10.97} />
        <GroundLine y={-5.485} width={23.77} depth={0.055} /><GroundLine y={5.485} width={23.77} depth={0.055} />
        <GroundLine y={-4.115} width={23.77} depth={0.055} /><GroundLine y={4.115} width={23.77} depth={0.055} />
        <GroundLine x={-6.4} width={0.055} depth={10.97} /><GroundLine x={6.4} width={0.055} depth={10.97} />
        <GroundLine width={12.8} depth={0.055} />
        {tennisKit && <><MetricGlb url={tennisAsset('net')} position={[0, 0, 0.12]} yaw={Math.PI / 2} />
          <FenceRectangle url={tennisAsset('fence')} width={module.widthM + 1.2} depth={module.depthM + 1.2} section={6} />
          <MetricGlb url={tennisAsset('bleacher')} position={[0, module.depthM / 2 + 1.7, 0.12]} />
          {[[-module.widthM / 2, -module.depthM / 2], [-module.widthM / 2, module.depthM / 2], [module.widthM / 2, -module.depthM / 2], [module.widthM / 2, module.depthM / 2]].map(([x, y]) => <MetricGlb key={`${x}-${y}`} url={tennisAsset('floodlight')} position={[x, y, 0.12]} />)}</>}
      </group>;

      const smallSided = familyId === 'park_caged_soccer_v0';
      const apron = smallSided ? 2 : 4;
      const goalWidth = smallSided ? 3 : 7.32;
      const goalHeight = smallSided ? 2 : 2.44;
      return <group key={index} position={[module.x, module.y, baseZ]} rotation={[0, 0, module.rotationZ]}>
        {!smallSided && <mesh position={[0, 0, -0.48]} receiveShadow renderOrder={RENDER_ORDER - 1}>
          <boxGeometry args={[module.widthM + apron * 2, module.depthM + apron * 2, 0.96]} />
          <meshStandardMaterial color="#536745" roughness={0.98} />
        </mesh>}
        <TexturedRect width={module.widthM + apron * 2} depth={module.depthM + apron * 2} z={-0.01} maps={edge} color={smallSided ? '#77736b' : '#b5c59c'} />
        <TexturedRect width={module.widthM} depth={module.depthM} z={0.02} maps={surface} color={smallSided ? '#2e713b' : '#ffffff'} />
        {!smallSided && <MowingStripes widthM={module.widthM} depthM={module.depthM} />}
        <SoccerMarkings widthM={module.widthM} depthM={module.depthM} smallSided={smallSided} />
        <SoccerGoal x={-module.widthM / 2} goalWidthM={goalWidth} goalHeightM={goalHeight} />
        <SoccerGoal x={module.widthM / 2} goalWidthM={goalWidth} goalHeightM={goalHeight} />
        {smallSided ? <CagedPitchEnclosure widthM={module.widthM + 0.5} depthM={module.depthM + 0.5} /> : <>
          {[-1, 1].flatMap((side) => [0, 1, 2].map((row) => <mesh key={`${side}-${row}`} position={[0, side * (module.depthM / 2 + 2 + row * 0.75), 0.18 + row * 0.3]}><boxGeometry args={[24, 0.68, 0.28]} /><meshStandardMaterial color={row % 2 ? '#808888' : '#9ba2a1'} metalness={0.34} roughness={0.6} /></mesh>))}
        </>}
        {[[-module.widthM / 2 + 4, -module.depthM / 2 - apron + 0.5], [-module.widthM / 2 + 4, module.depthM / 2 + apron - 0.5], [module.widthM / 2 - 4, -module.depthM / 2 - apron + 0.5], [module.widthM / 2 - 4, module.depthM / 2 + apron - 0.5]].map(([x, y]) => <Floodlight key={`${x}-${y}`} x={x} y={y} heightM={smallSided ? 8 : 14} />)}
        {smallSided && <SimpleBench x={0} y={module.depthM / 2 + 1.4} />}
      </group>;
    })}
  </group>;
}

function ExactTree({ x, y, scale = 1 }: { x: number; y: number; scale?: number }) {
  return <group position={[x, y, 0.12]} scale={scale}>
    <mesh position={[0, 0, 1.8]} castShadow><cylinderGeometry args={[0.18, 0.25, 3.6, 10]} /><meshStandardMaterial color="#563920" roughness={0.94} /></mesh>
    <mesh position={[0, 0, 4.6]} castShadow><icosahedronGeometry args={[2.2, 2]} /><meshStandardMaterial color="#405b2c" roughness={0.96} /></mesh>
  </group>;
}

function FormalEvergreen({ x, y }: { x: number; y: number }) {
  return <group position={[x, y, 0.12]}>
    <mesh position={[0, 0, 1.6]}><cylinderGeometry args={[0.14, 0.18, 3.2, 10]} /><meshStandardMaterial color="#4b3422" roughness={0.94} /></mesh>
    <mesh position={[0, 0, 4.2]} castShadow><coneGeometry args={[1.8, 5.5, 28]} /><meshStandardMaterial color="#1f3a20" roughness={0.96} /></mesh>
  </group>;
}

function ExactSurface({ kit, materialSlug = kit.slug }: { kit: ArchetypeOwnedParkKitDefinition; materialSlug?: string }) {
  const paver = useSkinMaterial(materialSlug, 'paver', [kit.widthM / 4, kit.depthM / 4]);
  const lawn = useSkinMaterial(materialSlug, 'lawn', [kit.widthM / 5, kit.depthM / 5]);
  const asphalt = useSkinMaterial(materialSlug, 'asphalt', [kit.widthM / 4, kit.depthM / 4]);
  const safety = useSkinMaterial(materialSlug, 'safety', [kit.widthM / 4, kit.depthM / 4]);
  const planting = useSkinMaterial(materialSlug, 'planting', [kit.widthM / 3, kit.depthM / 3]);
  const timber = useSkinMaterial(materialSlug, 'timber', [kit.widthM / 3, kit.depthM / 3]);
  const asset = (name: string) => `/park-kits/${kit.slug}/${kit.assets[name]}`;
  const variantSkin = materialSlug !== kit.slug;
  const fullAssemblyMaps = useMemo(
    () => ({ paver, lawn, asphalt, planting, safety, timber }),
    [asphalt, lawn, paver, planting, safety, timber],
  );

  if (
    kit.surfaceKind === 'pickleball_community'
    || kit.surfaceKind === 'track_oval_school'
    || kit.surfaceKind === 'baseball_club_hub'
    || kit.surfaceKind === 'cricket_village_green'
    || kit.surfaceKind === 'sports_complex_tournament'
  ) return <MetricGlb url={asset('assembly')} materialMaps={fullAssemblyMaps} />;

  if (kit.surfaceKind === 'inclusive_playground') return <>
    <TexturedRect width={50} depth={40} z={0} maps={paver} />
    {[
      [-12, 8, 9.45, 5.6, '#529ac1'], [0, 4, 12.15, 7.2, '#7da65c'],
      [12, -7, 9.45, 5.6, '#d68b42'], [-10, -10, 8.1, 4.8, '#c7ae75'],
      [14, 9, 6.75, 4, '#5496b7'],
    ].map(([x, y, rx, ry, color]) => <TexturedEllipse key={`${x}-${y}`} x={Number(x)} y={Number(y)} rx={Number(rx)} ry={Number(ry)} z={0.04} maps={safety} color={variantSkin ? '#ffffff' : String(color)} />)}
    <MetricGlb url={asset('playStructure')} position={[0, 1, 0.16]} />
    <MetricGlb url={asset('swingBay')} position={[-15, 9, 0.15]} />
    <MetricGlb url={asset('spinner')} position={[14, -8, 0.15]} />
    <MetricGlb url={asset('sensoryPanel')} position={[-14, -8, 0.15]} />
    <MetricGlb url={asset('shadeCanopy')} position={[14, 9, 0.15]} />
    <SimpleBench x={-21} y={0} yaw={Math.PI / 2} /><SimpleBench x={21} y={0} yaw={-Math.PI / 2} />
  </>;

  if (kit.surfaceKind === 'dog_park') {
    const compact = kit.widthM < 55 || kit.depthM < 40;
    const penDepth = compact ? Math.max(8, kit.depthM - 7) : Math.max(10, (kit.depthM - 9) / 2);
    const pens = compact
      ? [
        [-kit.widthM * 0.23, 1, Math.max(10, kit.widthM * 0.42), penDepth],
        [kit.widthM * 0.23, 1, Math.max(10, kit.widthM * 0.42), penDepth],
      ]
      : [
        [-kit.widthM * 0.30, kit.depthM * 0.25, kit.widthM * 0.27, penDepth],
        [0, kit.depthM * 0.25, kit.widthM * 0.27, penDepth],
        [kit.widthM * 0.30, kit.depthM * 0.25, kit.widthM * 0.27, penDepth],
        [-kit.widthM * 0.22, -kit.depthM * 0.25, kit.widthM * 0.40, penDepth],
        [kit.widthM * 0.22, -kit.depthM * 0.25, kit.widthM * 0.40, penDepth],
      ];
    return <>
      <TexturedRect width={kit.widthM} depth={kit.depthM} z={0} maps={paver} />
      {pens.map(([x, y, width, depth]) => <group key={`${x}-${y}`} position={[x, y, 0.03]}><TexturedRect width={width} depth={depth} z={0} maps={lawn} /><FenceRectangle url={asset('fence')} width={width} depth={depth} section={6} /></group>)}
      <FenceRectangle url={asset('fence')} width={Math.max(26, kit.widthM - 3)} depth={Math.max(21, kit.depthM - 3)} section={6} />
      <MetricGlb url={asset('gate')} position={[0, -kit.depthM / 2 + 1.5, 0]} />
      {(compact ? [-kit.widthM * 0.23, kit.widthM * 0.23] : [-kit.widthM * 0.30, 0, kit.widthM * 0.30])
        .map((x) => <MetricGlb key={x} url={asset('shade')} position={[x, compact ? 1 : kit.depthM * 0.25, 0.15]} />)}
      <MetricGlb url={asset('boulders')} position={[-2, -2, 0.15]} />
    </>;
  }

  if (kit.surfaceKind === 'splash_pad') return <>
    <TexturedEllipse x={0} y={0} rx={14.8} ry={12.43} z={0} maps={paver} />
    <TexturedEllipse x={0} y={0} rx={10.6} ry={8.27} z={0.04} maps={safety} color={variantSkin ? '#ffffff' : '#718b91'} />
    <MetricGlb url={asset('waterTower')} position={[3, 1, 0.18]} />
    <MetricGlb url={asset('sprayArch')} position={[-6, -2, 0.18]} />
    {[[-5, 4], [-3, 6], [0, -5], [5, -3], [7, 3]].map(([x, y]) => <MetricGlb key={`${x}-${y}`} url={asset('groundJet')} position={[x, y, 0.18]} />)}
    <FenceRectangle url={asset('fence')} width={27.5} depth={21} section={4.5} />
    <SimpleBench x={12} y={-7} yaw={2.094} />
  </>;

  if (kit.surfaceKind === 'tennis_cluster') {
    const courts = [[-19.6, -10], [19.6, -10], [-19.6, 10], [19.6, 10]];
    return <>
      <TexturedRect width={82} depth={46} z={0} maps={lawn} color="#315a32" />
      {courts.map(([x, y]) => <group key={`${x}-${y}`} position={[x, y, 0.02]}>
        <TexturedRect width={36.58} depth={18.29} z={0} maps={safety} color="#315b85" />
        <GroundLine width={36.58} depth={0.055} y={-9.145} /><GroundLine width={36.58} depth={0.055} y={9.145} />
        <GroundLine width={0.055} depth={18.29} x={-18.29} /><GroundLine width={0.055} depth={18.29} x={18.29} />
        <GroundLine width={36.58} depth={0.055} y={-6.4} /><GroundLine width={36.58} depth={0.055} y={6.4} />
        <GroundLine width={0.055} depth={12.8} x={-6.4} /><GroundLine width={0.055} depth={12.8} x={6.4} />
        <GroundLine width={12.8} depth={0.055} />
        <MetricGlb url={asset('net')} position={[0, 0, 0.12]} yaw={Math.PI / 2} />
      </group>)}
      <FenceRectangle url={asset('fence')} width={82} depth={46} section={6} />
      <MetricGlb url={asset('bleacher')} position={[-19.6, 0, 0.12]} />
      <MetricGlb url={asset('bleacher')} position={[19.6, 0, 0.12]} />
      {[[-39, -21], [0, -21], [39, -21], [-39, 21], [0, 21], [39, 21]].map(([x, y]) => (
        <MetricGlb key={`${x}-${y}`} url={asset('floodlight')} position={[x, y, 0.12]} />
      ))}
    </>;
  }

  if (kit.surfaceKind === 'nature_play') return <>
    <TexturedRect width={40} depth={30} z={0} maps={paver} color={variantSkin ? '#ffffff' : '#866f52'} />
    <TexturedEllipse x={12} y={-6} rx={7.2} ry={4.8} z={0.035} maps={safety} color={variantSkin ? '#ffffff' : '#bda477'} />
    <MetricGlb url={asset('rill')} position={[0, 0, 0.02]} />
    {[[-12, -6, 0.2], [-6, -9, -0.35], [-3, 9, 0.55]].map(([x, y, yaw]) => (
      <MetricGlb key={`${x}-${y}`} url={asset('balanceLog')} position={[x, y, 0.12]} yaw={yaw} />
    ))}
    <MetricGlb url={asset('logFort')} position={[9, 7, 0.12]} />
    <MetricGlb url={asset('willowTunnel')} position={[-10, 7, 0.12]} />
    {[[-2, -4], [0, -5], [2, -4], [4, -2], [6, -1]].map(([x, y]) => (
      <MetricGlb key={`${x}-${y}`} url={asset('steppingStump')} position={[x, y, 0.12]} />
    ))}
    <MetricGlb url={asset('boulders')} position={[12, -6, 0.12]} />
    {[[-16, -11], [-7, -13], [7, -13], [16, -11], [-16, 11], [-7, 13], [7, 13], [16, 11]].map(([x, y], index) => (
      <ExactTree key={`${x}-${y}`} x={x} y={y} scale={0.72 + (index % 3) * 0.08} />
    ))}
  </>;

  if (kit.surfaceKind === 'pump_track') return <>
    <TexturedRect width={50} depth={30} z={0} maps={lawn} />
    <MetricGlb url={asset('loop')} position={[0, 0, 0.12]} />
    <MetricGlb url={asset('startMound')} position={[-18, -2, 0.12]} />
    <SimpleBench x={0} y={-13} />
  </>;

  if (kit.surfaceKind === 'outdoor_fitness') return <>
    <TexturedRect width={30} depth={25} z={0} maps={paver} color={variantSkin ? '#ffffff' : '#d0ccc2'} />
    {[[-7, 4, 6, 4.5], [6, 3, 6, 4.5], [-5, -7, 5, 3.5], [7, -6, 5, 3.5]].map(([x, y, rx, ry]) => (
      <TexturedEllipse key={`${x}-${y}`} x={x} y={y} rx={rx} ry={ry} z={0.035} maps={safety} color={variantSkin ? '#ffffff' : '#313a3d'} />
    ))}
    <MetricGlb url={asset('rig')} position={[-6, 4, 0.12]} />
    <MetricGlb url={asset('parallelBars')} position={[6, 3, 0.12]} />
    <MetricGlb url={asset('situpBench')} position={[-5, -7, 0.12]} />
    <MetricGlb url={asset('rings')} position={[7, -6, 0.12]} />
    <SimpleBench x={0} y={-11} />
  </>;

  if (kit.surfaceKind === 'memorial_garden') return <>
    <TexturedRect width={50} depth={40} z={0} maps={paver} color="#d4cbc0" />
    {[[-15, -11], [15, -11], [-15, 8], [15, 8]].map(([x, y]) => <group key={`${x}-${y}`} position={[x, y, 0.02]}>
      <mesh position={[0, 0, 0.28]} castShadow><boxGeometry args={[13, 7, 0.58]} /><meshStandardMaterial color="#17391c" roughness={0.96} /></mesh>
      <TexturedRect width={9} depth={3} z={0.59} maps={paver} color="#c9c1b5" />
    </group>)}
    <MetricGlb url={asset('pool')} position={[0, 4, 0.12]} />
    <MetricGlb url={asset('fountain')} position={[0, -10, 0.12]} />
    <MetricGlb url={asset('wall')} position={[0, 18, 0.12]} />
    {[[-20, -13], [-20, 13], [20, -13], [20, 13]].map(([x, y]) => (
      <MetricGlb key={`${x}-${y}`} url={asset('urn')} position={[x, y, 0.12]} />
    ))}
    {[-22, 22].flatMap((x) => [-15, -5, 5, 15].map((y) => <FormalEvergreen key={`${x}-${y}`} x={x} y={y} />))}
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

export function GlobeArchetypeOwnedParkAssembly({ familyId, boundary, terrainZ, archetypeId, variantId }: {
  familyId: ExactParkFamilyId; boundary: readonly SkateParkPoint[]; terrainZ: (x: number, y: number) => number;
  archetypeId?: string; variantId?: string;
}) {
  const kit = archetypeOwnedParkKitForFamily(familyId);
  const adaptiveProgram = useMemo(() => {
    if (!kit || kit.surfaceKind !== 'dog_park') {
      return { kit, fit: kit ? fitFixedParkProgram(boundary, kit) : null };
    }
    const xs = boundary.map(({ x }) => x);
    const ys = boundary.map(({ y }) => y);
    const availableWidth = Math.max(...xs) - Math.min(...xs) - 1;
    const availableDepth = Math.max(...ys) - Math.min(...ys) - 1;
    for (const fraction of [1, 0.88, 0.76, 0.64]) {
      const candidate = {
        ...kit,
        widthM: Math.max(30, Math.min(80, availableWidth * fraction)),
        depthM: Math.max(25, Math.min(50, availableDepth * fraction)),
      };
      const candidateFit = fitFixedParkProgram(boundary, candidate);
      if (candidateFit) return { kit: candidate, fit: candidateFit };
    }
    const minimumKit = { ...kit, widthM: 30, depthM: 25 };
    return { kit: minimumKit, fit: fitFixedParkProgram(boundary, minimumKit) };
  }, [boundary, kit]);
  const adaptiveKit = adaptiveProgram.kit;
  const materialSlug = batch21ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug
    ?? batch17ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug
    ?? batch16ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug
    ?? adaptiveKit?.slug;
  const fit = adaptiveProgram.fit;
  const grassGeometry = useMemo(() => fit ? buildGrassBuffer(boundary, fit) : null, [boundary, fit]);
  useEffect(() => () => grassGeometry?.dispose(), [grassGeometry]);
  const lawn = useSkinMaterial(materialSlug ?? 'skate-park', 'lawn', [8, 8]);
  if (!adaptiveKit || !fit || !grassGeometry) return null;
  const baseZ = terrainZ(fit.center.x, fit.center.y) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  return <group renderOrder={RENDER_ORDER}>
    <mesh geometry={grassGeometry} position={[0, 0, baseZ - 0.015]} receiveShadow><meshStandardMaterial {...lawn} roughness={0.96} /></mesh>
    <group position={[fit.center.x, fit.center.y, baseZ]} rotation={[0, 0, fit.rotationRad]}>
      <ExactSurface kit={adaptiveKit} materialSlug={materialSlug} />
    </group>
  </group>;
}
