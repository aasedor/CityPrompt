import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch16ParkSkinForSelection } from './parkBatch16Skins';
import { batch20ParkSkinForSelection } from './parkBatch20Skins';

export interface Batch7ProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
}

interface Point { x: number; y: number }

type Batch7FamilyId = Extract<ParkLegoFamilyId,
  | 'park_regional_english_landscape_v0' | 'park_beer_garden_munich_v0'
  | 'park_sunken_courtyard_v0' | 'park_terraced_cascade_v3'
  | 'park_market_festival_lawn_v1' | 'park_boardwalk_maritime_v0'
  | 'park_fountain_formal_pool_v1' | 'park_natural_swimming_pond_v0'
  | 'park_nature_preserve_prairie_v1' | 'park_riverfront_lake_beach_v1'>;

const SKIN_SLUG: Record<Batch7FamilyId, string> = {
  park_regional_english_landscape_v0: 'regional-park-english-landscape',
  park_beer_garden_munich_v0: 'beer-garden-munich-chestnut',
  park_sunken_courtyard_v0: 'sunken-plaza-intimate-courtyard',
  park_terraced_cascade_v3: 'stepped-plaza-modernist-cascade',
  park_market_festival_lawn_v1: 'market-square-festival-lawn',
  park_boardwalk_maritime_v0: 'promenade-maritime-boardwalk',
  park_fountain_formal_pool_v1: 'fountain-formal-reflecting-pool',
  park_natural_swimming_pond_v0: 'swimming-natural-pond',
  park_nature_preserve_prairie_v1: 'nature-preserve-tallgrass-prairie',
  park_riverfront_lake_beach_v1: 'riverfront-lake-swimming-beach',
};

interface MaterialMaps {
  map: THREE.Texture;
  normalMap: THREE.Texture;
  roughnessMap: THREE.Texture;
  aoMap: THREE.Texture;
}

function useRoleMaps(slug: string, role: string, repeat = 3): MaterialMaps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({
    map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`,
    roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg`,
  });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat, repeat);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as MaterialMaps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function center(guide: ParkGroundGuide, frame: Batch7ProgramFrame): Point {
  return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y };
}

function route(guide: ParkGroundGuide, frame: Batch7ProgramFrame): Point[] {
  if (guide.points && guide.points.length > 1) {
    return guide.points.map(([x, y]) => ({
      x: frame.minX + frame.width * x,
      y: frame.maxY - frame.height * y,
    }));
  }
  const c = center(guide, frame);
  const width = guide.widthM ?? guide.width * frame.width;
  const height = guide.heightM ?? guide.height * frame.height;
  const angle = ((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const length = width || height;
  return [
    { x: c.x - Math.cos(angle) * length / 2, y: c.y - Math.sin(angle) * length / 2 },
    { x: c.x + Math.cos(angle) * length / 2, y: c.y + Math.sin(angle) * length / 2 },
  ];
}

function Segment({ from, to, width, height, z, maps, color }: {
  from: Point; to: Point; width: number; height: number; z: number;
  maps?: MaterialMaps; color: string;
}) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return <mesh
    position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]}
    rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]}
    renderOrder={146}
  >
    <boxGeometry args={[length, width, height]} />
    <meshStandardMaterial {...maps} color={color} roughness={0.86} metalness={0.02} />
  </mesh>;
}

function DeciduousTree({ x, y, z, scale = 1, trunk = '#5d4936', leaf = '#526c3c' }: {
  x: number; y: number; z: number; scale?: number; trunk?: string; leaf?: string;
}) {
  return <group position={[x, y, z]} scale={scale}>
    <mesh position={[0, 0, 2.1]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.22, 0.32, 4.2, 9]} /><meshStandardMaterial color={trunk} roughness={0.96} /></mesh>
    <mesh position={[0, 0, 5.5]} scale={[1.6, 1.4, 1.15]}><dodecahedronGeometry args={[2.0, 1]} /><meshStandardMaterial color={leaf} roughness={0.98} /></mesh>
    <mesh position={[1.1, 0.4, 5.2]} scale={[0.9, 0.85, 0.8]}><dodecahedronGeometry args={[1.5, 1]} /><meshStandardMaterial color="#647b48" roughness={0.98} /></mesh>
  </group>;
}

function TrestleSet({ x, y, z, timberMaps, neutralTint = false }: { x: number; y: number; z: number; timberMaps: MaterialMaps; neutralTint?: boolean }) {
  return <group position={[x, y, z]}>
    <mesh position={[0, 0, 0.78]}><boxGeometry args={[5.8, 0.72, 0.12]} /><meshStandardMaterial {...timberMaps} color={neutralTint ? '#ffffff' : '#9a7044'} roughness={0.9} /></mesh>
    {[-0.82, 0.82].map((side) => <mesh key={side} position={[0, side, 0.46]}><boxGeometry args={[5.8, 0.32, 0.10]} /><meshStandardMaterial {...timberMaps} color={neutralTint ? '#ffffff' : '#89633f'} roughness={0.92} /></mesh>)}
    {[-1.8, 1.8].flatMap((along) => [-0.42, 0.42].map((side) => <mesh key={`${along}-${side}`} position={[along, side, 0.38]} rotation={[0, side * 0.35, 0]}><boxGeometry args={[0.10, 0.10, 0.75]} /><meshStandardMaterial color="#33413b" metalness={0.55} roughness={0.46} /></mesh>))}
  </group>;
}

function WaterJet({ x, y, z, height = 1.8 }: { x: number; y: number; z: number; height?: number }) {
  return <group position={[x, y, z]}>
    <mesh position={[0, 0, 0.08]}><cylinderGeometry args={[0.12, 0.14, 0.16, 12]} /><meshStandardMaterial color="#737b7c" metalness={0.72} roughness={0.3} /></mesh>
    <mesh position={[0, 0, height / 2 + 0.1]}><cylinderGeometry args={[0.035, 0.08, height, 9]} /><meshPhysicalMaterial color="#c7e5e4" transparent opacity={0.68} roughness={0.1} transmission={0.1} /></mesh>
  </group>;
}

export function GlobeParkBatch7Assembly({ familyId, guides, frame, terrainZ, archetypeId, variantId }: {
  familyId: ParkLegoFamilyId;
  guides: ParkGroundGuide[];
  frame: Batch7ProgramFrame;
  terrainZ: (x: number, y: number) => number;
  archetypeId?: string;
  variantId?: string;
}) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const batch20Skin = batch20ParkSkinForSelection(archetypeId ?? '', variantId ?? '');
  const slug = batch20Skin?.slug
    ?? batch16ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug
    ?? SKIN_SLUG[familyId as Batch7FamilyId];
  const variantSkin = batch20Skin !== null;
  const paverMaps = useRoleMaps(slug, 'paver');
  const asphaltMaps = useRoleMaps(slug, 'asphalt');
  const plantingMaps = useRoleMaps(slug, 'planting', 5);
  const safetyMaps = useRoleMaps(slug, 'safety');
  const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_regional_english_landscape_v0') {
    const bridge = guides.find((guide) => guide.kind === 'line');
    const points = bridge ? route(bridge, frame) : [];
    const treeCount = Math.min(24, Math.max(10, Math.round((frame.width * frame.height) / 2600)));
    return <group>
      {points.length === 2 && <>
        <Segment from={points[0]} to={points[1]} width={2.8} height={0.28} z={Math.max(terrainZ(points[0].x, points[0].y), terrainZ(points[1].x, points[1].y)) + lift + 0.65} maps={timberMaps} color="#81735d" />
        {[points[0], points[1]].map((point, index) => <mesh key={index} position={[point.x, point.y, terrainZ(point.x, point.y) + lift + 0.48]}><boxGeometry args={[1.2, 3.8, 0.96]} /><meshStandardMaterial {...paverMaps} color="#8f8b80" roughness={0.94} /></mesh>)}
      </>}
      {Array.from({ length: treeCount }, (_, index) => {
        const side = index % 2 === 0 ? 0.10 + ((index * 0.137) % 0.20) : 0.70 + ((index * 0.113) % 0.20);
        const along = 0.10 + ((index * 0.229) % 0.80);
        const x = frame.minX + frame.width * side;
        const y = frame.maxY - frame.height * along;
        return <DeciduousTree key={index} x={x} y={y} z={terrainZ(x, y) + lift} scale={0.82 + (index % 4) * 0.12} />;
      })}
    </group>;
  }

  if (familyId === 'park_beer_garden_munich_v0') {
    const kiosk = guides.find((guide) => guide.kind === 'rectangle');
    const rowCount = Math.min(10, Math.max(3, Math.floor((frame.height - 10) / 4.2)));
    const columnCount = Math.min(8, Math.max(2, Math.floor((frame.width - 12) / 7.2)));
    const usableWidth = Math.min(frame.width * 0.72, columnCount * 6.8);
    const usableHeight = Math.min(frame.height * 0.68, rowCount * 4.0);
    const treesAcross = Math.max(2, Math.ceil(columnCount / 2));
    const treesDown = Math.max(2, Math.ceil(rowCount / 2));
    return <group>
      {Array.from({ length: rowCount * columnCount }, (_, index) => {
        const row = Math.floor(index / columnCount); const column = index % columnCount;
        const x = frame.minX + frame.width / 2 - usableWidth / 2 + (column + 0.5) * usableWidth / columnCount;
        const y = frame.minY + frame.height / 2 - usableHeight / 2 + (row + 0.5) * usableHeight / rowCount;
        return <TrestleSet key={index} x={x} y={y} z={terrainZ(x, y) + lift} timberMaps={timberMaps} neutralTint={variantSkin} />;
      })}
      {Array.from({ length: treesAcross * treesDown }, (_, index) => {
        const row = Math.floor(index / treesAcross); const column = index % treesAcross;
        const x = frame.minX + frame.width / 2 - usableWidth / 2 + (column + 0.5) * usableWidth / treesAcross;
        const y = frame.minY + frame.height / 2 - usableHeight / 2 + (row + 0.5) * usableHeight / treesDown;
        return <DeciduousTree key={index} x={x} y={y} z={terrainZ(x, y) + lift} scale={0.78} leaf="#48643d" />;
      })}
      {kiosk && (() => { const c = center(kiosk, frame); const guideSize = resolveParkGuideDimensionsM(kiosk, frame); const s = { width: Math.min(8, guideSize.width), height: Math.min(6, guideSize.height) }; const z = terrainZ(c.x, c.y) + lift; return <group position={[c.x, c.y, z]}>
        <mesh position={[0, 0, 1.45]}><boxGeometry args={[s.width, s.height, 2.9]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#725033'} roughness={0.9} /></mesh>
        <mesh position={[0, 0, 3.25]} rotation={[0, 0, 0]}><coneGeometry args={[Math.min(5, Math.max(s.width, s.height) * 0.62), 1.5, 4]} /><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : '#7d4932'} roughness={0.88} /></mesh>
        <mesh position={[0, -s.height / 2 - 0.01, 1.65]}><planeGeometry args={[s.width * 0.62, 1.15]} /><meshStandardMaterial color="#202826" roughness={0.5} /></mesh>
      </group>; })()}
      {Array.from({ length: 3 }, (_, row) => {
        const y = frame.minY + frame.height * (0.28 + row * 0.22);
        const a = { x: frame.minX + frame.width * 0.10, y }; const b = { x: frame.maxX - frame.width * 0.10, y };
        const z = Math.max(terrainZ(a.x, a.y), terrainZ(b.x, b.y)) + lift + 5.2;
        return <group key={row}><Segment from={a} to={b} width={0.04} height={0.04} z={z} color="#315a70" />{Array.from({ length: 14 }, (_, flag) => { const t = (flag + 0.5) / 14; return <mesh key={flag} position={[a.x + (b.x - a.x) * t, y, z - 0.28]} rotation={[Math.PI / 2, 0, 0]}><coneGeometry args={[0.22, 0.55, 3]} /><meshStandardMaterial color={flag % 2 ? '#f2f0df' : '#4f86a4'} side={THREE.DoubleSide} /></mesh>; })}</group>;
      })}
    </group>;
  }

  if (familyId === 'park_sunken_courtyard_v0') {
    const court = guides.find((guide) => guide.kind === 'rounded_rectangle');
    const fountain = guides.find((guide) => guide.kind === 'ellipse');
    if (!court || !fountain) return null;
    const c = center(court, frame); const s = resolveParkGuideDimensionsM(court, frame); const z = terrainZ(c.x, c.y) + lift;
    const fc = center(fountain, frame); const fs = resolveParkGuideDimensionsM(fountain, frame);
    const tiers = 4;
    return <group>
      {Array.from({ length: tiers }, (_, tier) => {
        const inset = tier * 1.15; const h = 0.22 + tier * 0.24;
        return <group key={tier}>
          <mesh position={[c.x, c.y + s.height / 2 + inset / 2, z + h / 2]}><boxGeometry args={[s.width + inset * 2, 1.15, h]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#bdb5a7'} roughness={0.9} /></mesh>
          <mesh position={[c.x - s.width / 2 - inset / 2, c.y, z + h / 2]}><boxGeometry args={[1.15, s.height + inset * 2, h]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#bdb5a7'} roughness={0.9} /></mesh>
          <mesh position={[c.x + s.width / 2 + inset / 2, c.y, z + h / 2]}><boxGeometry args={[1.15, s.height + inset * 2, h]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#bdb5a7'} roughness={0.9} /></mesh>
        </group>;
      })}
      <mesh position={[fc.x, fc.y, terrainZ(fc.x, fc.y) + lift + 0.32]}><cylinderGeometry args={[fs.width / 2, fs.width / 2 + 0.35, 0.64, 24]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#77756d'} roughness={0.82} /></mesh>
      <mesh position={[fc.x, fc.y, terrainZ(fc.x, fc.y) + lift + 0.67]}><cylinderGeometry args={[fs.width * 0.39, fs.width * 0.39, 0.08, 24]} /><meshPhysicalMaterial color="#668a8c" transparent opacity={0.82} roughness={0.14} /></mesh>
      <mesh position={[fc.x, fc.y, terrainZ(fc.x, fc.y) + lift + 1.1]}><dodecahedronGeometry args={[0.58, 1]} /><meshStandardMaterial color="#4c5b50" metalness={0.55} roughness={0.48} /></mesh>
    </group>;
  }

  if (familyId === 'park_terraced_cascade_v3') {
    const basins = guides.filter((guide) => guide.kind === 'rectangle');
    const ramp = guides.find((guide) => guide.kind === 'polyline');
    const bands = Math.min(12, Math.max(6, Math.floor(frame.height / 9)));
    const bandDepth = frame.height * 0.72 / bands;
    return <group>
      {Array.from({ length: bands }, (_, index) => {
        const y = frame.maxY - frame.height * 0.14 - (index + 0.5) * bandDepth;
        const z = terrainZ(frame.minX + frame.width / 2, y) + lift + index * 0.28;
        return <group key={index}>
          <mesh position={[frame.minX + frame.width / 2, y, z + 0.14]}><boxGeometry args={[frame.width * 0.72, bandDepth * 0.92, 0.28]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : index % 2 ? '#9f9e99' : '#aaa8a1'} roughness={0.92} /></mesh>
          {[-1, 1].map((side) => <mesh key={side} position={[frame.minX + frame.width / 2 + side * frame.width * 0.31, y, z + 0.5]}><boxGeometry args={[frame.width * 0.12, bandDepth * 0.84, 0.9]} /><meshStandardMaterial {...plantingMaps} color={variantSkin ? '#ffffff' : '#536747'} roughness={0.98} /></mesh>)}
        </group>;
      })}
      {basins.map((basin, index) => { const c = center(basin, frame); const s = resolveParkGuideDimensionsM(basin, frame); const z = terrainZ(c.x, c.y) + lift + index * 0.24; return <group key={index}>
        <mesh position={[c.x, c.y, z + 0.24]}><boxGeometry args={[s.width + 0.8, s.height + 0.8, 0.48]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#777b79'} roughness={0.82} /></mesh>
        <mesh position={[c.x, c.y, z + 0.50]}><boxGeometry args={[s.width, s.height, 0.07]} /><meshPhysicalMaterial color="#668d92" transparent opacity={0.8} roughness={0.12} /></mesh>
      </group>; })}
      {ramp && (() => { const points = route(ramp, frame); return points.slice(0, -1).map((point, index) => <Segment key={index} from={point} to={points[index + 1]} width={3.2} height={0.18} z={Math.max(terrainZ(point.x, point.y), terrainZ(points[index + 1].x, points[index + 1].y)) + lift + 0.45} maps={paverMaps} color={variantSkin ? '#ffffff' : '#aaa79f'} />); })()}
    </group>;
  }

  if (familyId === 'park_market_festival_lawn_v1') {
    const padCount = Math.min(12, Math.max(4, Math.floor((frame.width + frame.height) / 30)));
    return <group>
      {Array.from({ length: padCount }, (_, index) => {
        const t = index / padCount; const horizontal = index < Math.ceil(padCount / 2);
        const x = horizontal ? frame.minX + frame.width * (0.15 + 0.7 * (t * 2)) : frame.minX + frame.width * (index % 2 ? 0.88 : 0.12);
        const y = horizontal ? frame.minY + frame.height * (index % 2 ? 0.88 : 0.12) : frame.minY + frame.height * (0.2 + 0.6 * ((t * 2) % 1));
        const z = terrainZ(x, y) + lift;
        return <group key={index} position={[x, y, z]}>
          <mesh position={[0, 0, 0.10]}><boxGeometry args={[4.6, 3.4, 0.20]} /><meshStandardMaterial {...paverMaps} color="#a8a49b" roughness={0.9} /></mesh>
          <mesh position={[0, 0, 0.62]}><cylinderGeometry args={[0.14, 0.18, 1.04, 10]} /><meshStandardMaterial {...asphaltMaps} color="#555b58" metalness={0.48} roughness={0.48} /></mesh>
        </group>;
      })}
      {[-1, 1].flatMap((sx) => [-1, 1].map((sy) => { const x = frame.minX + frame.width * (0.5 + sx * 0.34); const y = frame.minY + frame.height * (0.5 + sy * 0.30); const z = terrainZ(x, y) + lift; return <mesh key={`${sx}-${sy}`} position={[x, y, z + 3]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.08, 0.12, 6, 9]} /><meshStandardMaterial color="#4a5250" metalness={0.62} roughness={0.4} /></mesh>; }))}
    </group>;
  }

  if (familyId === 'park_boardwalk_maritime_v0') {
    const boardwalk = guides.find((guide) => guide.kind === 'polyline');
    if (!boardwalk) return null;
    const points = route(boardwalk, frame);
    return <group>
      {points.slice(0, -1).map((point, index) => {
        const next = points[index + 1]; const z = Math.max(terrainZ(point.x, point.y), terrainZ(next.x, next.y)) + lift + 0.22;
        return <group key={index}>
          <Segment from={point} to={next} width={7} height={0.28} z={z} maps={timberMaps} color="#826d56" />
          {[0.18, 0.50, 0.82].map((t, postIndex) => { const x = point.x + (next.x - point.x) * t; const y = point.y + (next.y - point.y) * t; const angle = Math.atan2(next.y - point.y, next.x - point.x); const rx = x - Math.sin(angle) * 3.3; const ry = y + Math.cos(angle) * 3.3; return <group key={postIndex} position={[rx, ry, terrainZ(rx, ry) + lift]}>
            <mesh position={[0, 0, 0.75]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.10, 0.14, 1.5, 9]} /><meshStandardMaterial {...timberMaps} color="#5c4939" roughness={0.94} /></mesh>
            <mesh position={[0, 0, 1.55]}><sphereGeometry args={[0.16, 9, 7]} /><meshStandardMaterial color="#26302e" metalness={0.5} roughness={0.5} /></mesh>
          </group>; })}
          {index % 2 === 0 && <group position={[(point.x + next.x) / 2, (point.y + next.y) / 2, z + 0.35]} rotation={[0, 0, Math.atan2(next.y - point.y, next.x - point.x)]}>
            <mesh position={[0, 1.9, 0.35]}><boxGeometry args={[2.8, 0.42, 0.12]} /><meshStandardMaterial {...timberMaps} color="#8d704e" roughness={0.9} /></mesh>
            <mesh position={[0, 2.05, 0.95]} rotation={[0.22, 0, 0]}><boxGeometry args={[2.8, 0.16, 0.85]} /><meshStandardMaterial {...timberMaps} color="#8d704e" roughness={0.9} /></mesh>
          </group>}
        </group>;
      })}
    </group>;
  }

  if (familyId === 'park_fountain_formal_pool_v1') {
    const pool = guides.find((guide) => guide.kind === 'rectangle');
    if (!pool) return null;
    const c = center(pool, frame); const s = resolveParkGuideDimensionsM(pool, frame); const z = terrainZ(c.x, c.y) + lift;
    const jetPairs = Math.min(8, Math.max(4, Math.floor(s.width / 5)));
    return <group position={[c.x, c.y, z]} rotation={[0, 0, -((pool.rotationDeg ?? 0) * Math.PI) / 180]}>
      <mesh position={[0, 0, 0.20]}><boxGeometry args={[s.width + 1.2, s.height + 1.2, 0.4]} /><meshStandardMaterial {...paverMaps} color="#4f5352" roughness={0.72} /></mesh>
      <mesh position={[0, 0, 0.43]}><boxGeometry args={[s.width, s.height, 0.08]} /><meshPhysicalMaterial color="#557c84" transparent opacity={0.84} roughness={0.12} metalness={0.05} /></mesh>
      {Array.from({ length: jetPairs }, (_, index) => {
        const x = -s.width / 2 + (index + 1) * s.width / (jetPairs + 1);
        return [-1, 1].map((side) => <WaterJet key={`${index}-${side}`} x={x} y={side * s.height * 0.22} z={0.48} height={1.4 + (index % 3) * 0.4} />);
      })}
      {[-1, 1].flatMap((side) => [-0.36, 0, 0.36].map((ratio) => <group key={`${side}-${ratio}`} position={[ratio * s.width, side * (s.height / 2 + 2.5), 0]}>
        <mesh position={[0, 0, 0.7]}><cylinderGeometry args={[0.62, 0.48, 1.4, 16]} /><meshStandardMaterial {...paverMaps} color="#d2c8b6" roughness={0.86} /></mesh>
        <mesh position={[0, 0, 1.7]} scale={[0.72, 0.72, 0.86]}><sphereGeometry args={[0.8, 14, 10]} /><meshStandardMaterial {...plantingMaps} color="#49613f" roughness={0.98} /></mesh>
      </group>))}
    </group>;
  }

  if (familyId === 'park_natural_swimming_pond_v0') {
    const pool = guides.find((guide) => guide.kind === 'rectangle');
    const dock = guides.find((guide) => guide.kind === 'line');
    if (!pool) return null;
    const c = center(pool, frame); const s = resolveParkGuideDimensionsM(pool, frame); const z = terrainZ(c.x, c.y) + lift;
    const dockPoints = dock ? route(dock, frame) : [];
    return <group>
      <mesh position={[c.x, c.y, z + 0.18]}><boxGeometry args={[s.width + 4.4, s.height + 4.4, 0.36]} /><meshStandardMaterial {...paverMaps} color="#c7bca8" roughness={0.86} /></mesh>
      <mesh position={[c.x, c.y, z + 0.40]}><boxGeometry args={[s.width, s.height, 0.09]} /><meshPhysicalMaterial color="#5c9b9e" transparent opacity={0.86} roughness={0.1} /></mesh>
      {Array.from({ length: 4 }, (_, lane) => <mesh key={lane} position={[c.x - s.width / 2 + (lane + 1) * s.width / 5, c.y, z + 0.46]}><boxGeometry args={[0.06, s.height - 0.5, 0.025]} /><meshStandardMaterial color="#d9e5dd" roughness={0.5} /></mesh>)}
      {dockPoints.length === 2 && <Segment from={dockPoints[0]} to={dockPoints[1]} width={2.2} height={0.24} z={Math.max(terrainZ(dockPoints[0].x, dockPoints[0].y), terrainZ(dockPoints[1].x, dockPoints[1].y)) + lift + 0.36} maps={timberMaps} color="#846c52" />}
      {Array.from({ length: 18 }, (_, index) => { const angle = index * Math.PI * 2 / 18; const x = c.x + Math.cos(angle) * (s.width / 2 + 7 + (index % 3)); const y = c.y + Math.sin(angle) * (s.height / 2 + 6 + (index % 2)); return <mesh key={index} position={[x, y, terrainZ(x, y) + lift + 0.8]}><coneGeometry args={[0.34, 1.6 + (index % 3) * 0.4, 7]} /><meshStandardMaterial {...plantingMaps} color={index % 2 ? '#69815a' : '#7d8c55'} roughness={0.98} /></mesh>; })}
    </group>;
  }

  if (familyId === 'park_nature_preserve_prairie_v1') {
    const deck = guides.find((guide) => guide.kind === 'rectangle');
    const driftCount = Math.min(48, Math.max(18, Math.floor((frame.width * frame.height) / 700)));
    return <group>
      {Array.from({ length: driftCount }, (_, index) => { const x = frame.minX + frame.width * (0.08 + ((index * 0.257) % 0.84)); const y = frame.minY + frame.height * (0.08 + ((index * 0.419) % 0.84)); const z = terrainZ(x, y) + lift; return <group key={index} position={[x, y, z]}>{Array.from({ length: 5 }, (__, stem) => <mesh key={stem} position={[(stem - 2) * 0.24, ((stem * 7) % 5 - 2) * 0.18, 0.7 + (stem % 3) * 0.18]}><coneGeometry args={[0.12, 1.4 + (stem % 3) * 0.35, 6]} /><meshStandardMaterial {...plantingMaps} color={['#927946','#aa8849','#6f7645','#815f38'][index % 4]} roughness={0.99} /></mesh>)}</group>; })}
      {deck && (() => { const c = center(deck, frame); const s = resolveParkGuideDimensionsM(deck, frame); const z = terrainZ(c.x, c.y) + lift; return <group position={[c.x, c.y, z]}>
        <mesh position={[0, 0, 0.45]}><boxGeometry args={[s.width, s.height, 0.24]} /><meshStandardMaterial {...timberMaps} color="#81684c" roughness={0.92} /></mesh>
        {[-1, 1].map((side) => <mesh key={side} position={[0, side * s.height / 2, 1.15]}><boxGeometry args={[s.width, 0.08, 0.08]} /><meshStandardMaterial {...timberMaps} color="#5f4d3b" roughness={0.94} /></mesh>)}
      </group>; })()}
    </group>;
  }

  if (familyId === 'park_riverfront_lake_beach_v1') {
    const dock = guides.find((guide) => guide.kind === 'polyline');
    const rectangles = guides.filter((guide) => guide.kind === 'rectangle');
    const kayakRack = rectangles[1];
    const points = dock ? route(dock, frame) : [];
    return <group>
      {points.slice(0, -1).map((point, index) => <Segment key={index} from={point} to={points[index + 1]} width={2.6} height={0.24} z={Math.max(terrainZ(point.x, point.y), terrainZ(points[index + 1].x, points[index + 1].y)) + lift + 0.28} maps={timberMaps} color="#82694e" />)}
      {kayakRack && (() => { const c = center(kayakRack, frame); const s = resolveParkGuideDimensionsM(kayakRack, frame); const z = terrainZ(c.x, c.y) + lift; return <group position={[c.x, c.y, z]}>
        {[-1, 1].map((side) => <mesh key={side} position={[side * s.width * 0.38, 0, 0.9]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.08, 0.10, 1.8, 8]} /><meshStandardMaterial color="#4a514f" metalness={0.55} roughness={0.45} /></mesh>)}
        {[-0.8, 0, 0.8].map((offset, index) => <mesh key={offset} position={[0, offset, 0.7 + index * 0.32]} scale={[s.width * 0.09, 0.32, 0.16]}><sphereGeometry args={[1, 18, 8]} /><meshStandardMaterial color={['#d3a02e','#c95035','#4c8d88'][index]} roughness={0.7} /></mesh>)}
      </group>; })()}
      {points.length > 0 && <mesh position={[points[points.length - 1].x + 8, points[points.length - 1].y - 4, terrainZ(points[points.length - 1].x + 8, points[points.length - 1].y - 4) + lift + 0.18]}><boxGeometry args={[5.5, 5.5, 0.36]} /><meshStandardMaterial {...timberMaps} color="#82694e" roughness={0.9} /></mesh>}
    </group>;
  }

  return null;
}
