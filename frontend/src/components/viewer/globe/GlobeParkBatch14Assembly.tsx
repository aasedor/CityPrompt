import { useEffect, useMemo, type ReactNode } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import type { ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { Batch10ProgramFrame as ProgramFrame } from './GlobeParkBatch10Assembly';
import { batch14ParkSkinForSelection } from './parkBatch14Skins';
import { batch15ParkSkinForSelection } from './parkBatch15Skins';

type FamilyId = Extract<ParkLegoFamilyId,
  | 'park_surface_parking_standard_v0'
  | 'park_structured_parking_urban_v2'
  | 'park_underground_parking_green_v1'
  | 'park_green_parking_infrastructure_v1'
  | 'park_airport_general_aviation_v2'
  | 'park_equestrian_working_stable_v1'
  | 'park_golf_seaside_links_v0'
  | 'park_driving_range_single_tier_v0'
  | 'park_multi_sport_track_field_v3'
  | 'park_retail_parking_landscaped_v1'
>;

const SLUG: Record<FamilyId, string> = {
  park_surface_parking_standard_v0: 'surface-parking-standard-v0',
  park_structured_parking_urban_v2: 'structured-parking-urban-v2',
  park_underground_parking_green_v1: 'underground-parking-green-v1',
  park_green_parking_infrastructure_v1: 'green-parking-infrastructure-v1',
  park_airport_general_aviation_v2: 'airport-general-aviation-v2',
  park_equestrian_working_stable_v1: 'equestrian-working-stable-v1',
  park_golf_seaside_links_v0: 'golf-seaside-links-v0',
  park_driving_range_single_tier_v0: 'driving-range-single-tier-v0',
  park_multi_sport_track_field_v3: 'multi-sport-track-field-v3',
  park_retail_parking_landscaped_v1: 'retail-parking-landscaped-v1',
};

interface Maps { map: THREE.Texture; normalMap: THREE.Texture; roughnessMap: THREE.Texture; aoMap: THREE.Texture }

function useMaps(slug: string, role: string, repeat = 4): Maps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({ map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`, roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg` });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat, repeat);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as Maps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function FlatBox({ x, y, z, width, depth, color, maps, rotation = 0, height = .18 }: { x: number; y: number; z: number; width: number; depth: number; color: string; maps?: Maps; rotation?: number; height?: number }) {
  return <mesh position={[x, y, z + height / 2]} rotation={[0, 0, rotation]}><boxGeometry args={[width, depth, height]} /><meshStandardMaterial {...maps} color={color} roughness={.93} /></mesh>;
}

function Line({ x, y, z, width, depth, rotation = 0, color = '#ece7d8' }: { x: number; y: number; z: number; width: number; depth: number; rotation?: number; color?: string }) {
  return <FlatBox x={x} y={y} z={z} width={width} depth={depth} rotation={rotation} height={.035} color={color} />;
}

function Tree({ x, y, z }: { x: number; y: number; z: number }) {
  return <group position={[x, y, z]}><mesh position={[0, 0, 1.25]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[.1, .16, 2.5, 8]} /><meshStandardMaterial color="#5a4635" roughness={.98} /></mesh><mesh position={[0, 0, 3]}><dodecahedronGeometry args={[1.15, 1]} /><meshStandardMaterial color="#4f6e45" roughness={.98} /></mesh></group>;
}

function LightPole({ x, y, z, height = 6 }: { x: number; y: number; z: number; height?: number }) {
  return <group position={[x, y, z]}><mesh position={[0, 0, height / 2]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[.07, .1, height, 8]} /><meshStandardMaterial color="#454947" metalness={.55} roughness={.42} /></mesh><mesh position={[0, 0, height]}><boxGeometry args={[.7, .24, .14]} /><meshStandardMaterial color="#d6d2bf" /></mesh></group>;
}

function Car({ x, y, z, rotation = 0, color = '#7d3d34' }: { x: number; y: number; z: number; rotation?: number; color?: string }) {
  return <group position={[x, y, z + .16]} rotation={[0, 0, rotation]}><mesh><boxGeometry args={[1.75, 4.25, .42]} /><meshStandardMaterial color={color} metalness={.18} roughness={.58} /></mesh><mesh position={[0, 0, .38]}><boxGeometry args={[1.48, 2.1, .48]} /><meshStandardMaterial color="#81909a" metalness={.32} roughness={.38} /></mesh></group>;
}

function ParkingField({ frame, z, maps, green = false, retail = false, baseColor = '#ffffff' }: { frame: ProgramFrame; z: number; maps: Maps; green?: boolean; retail?: boolean; baseColor?: string }) {
  const marginX = Math.max(2.5, frame.width * .06);
  const marginY = Math.max(2.5, frame.height * .08);
  const width = frame.width - marginX * 2;
  const depth = frame.height - marginY * 2;
  const columns = Math.max(4, Math.min(14, Math.floor(width / 3.1)));
  const rows = Math.max(2, Math.min(6, Math.floor(depth / 8.5)));
  const stallW = width / columns;
  const rowDepth = depth / rows;
  const children: ReactNode[] = [];
  children.push(<FlatBox key="base" x={(frame.minX + frame.maxX) / 2} y={(frame.minY + frame.maxY) / 2} z={z} width={width} depth={depth} maps={maps} color={baseColor} />);
  for (let row = 0; row < rows; row += 1) {
    const y = frame.minY + marginY + rowDepth * (row + .5);
    for (let column = 0; column <= columns; column += 1) {
      const x = frame.minX + marginX + stallW * column;
      children.push(<Line key={`s-${row}-${column}`} x={x} y={y} z={z + .19} width={.08} depth={Math.min(5.3, rowDepth * .72)} />);
    }
    if (row % 2 === 0) {
      for (let column = 1; column < columns; column += 3) {
        const x = frame.minX + marginX + stallW * (column + .5);
        children.push(<Car key={`c-${row}-${column}`} x={x} y={y} z={z + .19} rotation={row % 2 ? Math.PI : 0} color={['#7f4036', '#446278', '#b2aca0', '#3d4b44'][(row + column) % 4]} />);
      }
    }
  }
  const islandCount = green || retail ? Math.max(2, Math.min(7, Math.floor(width / 14))) : Math.max(1, Math.min(4, Math.floor(width / 24)));
  for (let index = 0; index < islandCount; index += 1) {
    const x = frame.minX + marginX + width * ((index + .5) / islandCount);
    children.push(<FlatBox key={`island-${index}`} x={x} y={frame.minY + marginY + depth * .52} z={z + .19} width={Math.min(3.2, stallW * 1.15)} depth={Math.min(10, rowDepth * .82)} color="#627a50" />);
    children.push(<Tree key={`tree-${index}`} x={x} y={frame.minY + marginY + depth * .52} z={z + .36} />);
  }
  return <group>{children}</group>;
}

function FenceRect({ x, y, z, width, depth, color = '#6d5a43' }: { x: number; y: number; z: number; width: number; depth: number; color?: string }) {
  const rails = [[0, -depth / 2, width, .09], [0, depth / 2, width, .09], [-width / 2, 0, .09, depth], [width / 2, 0, .09, depth]] as const;
  return <group>{rails.map(([dx, dy, w, d], index) => <mesh key={index} position={[x + dx, y + dy, z + .7]}><boxGeometry args={[w, d, .12]} /><meshStandardMaterial color={color} roughness={.9} /></mesh>)}</group>;
}

function Aircraft({ x, y, z, rotation = 0 }: { x: number; y: number; z: number; rotation?: number }) {
  return <group position={[x, y, z + .35]} rotation={[0, 0, rotation]}><mesh><boxGeometry args={[.72, 6.2, .6]} /><meshStandardMaterial color="#e5e2d8" roughness={.65} /></mesh><mesh position={[0, .1, .05]}><boxGeometry args={[6.4, .78, .18]} /><meshStandardMaterial color="#d9dbd7" roughness={.65} /></mesh><mesh position={[0, -2.55, .35]}><boxGeometry args={[2.4, .5, .14]} /><meshStandardMaterial color="#4a6579" /></mesh></group>;
}

function Flag({ x, y, z }: { x: number; y: number; z: number }) {
  return <group position={[x, y, z]}><mesh position={[0, 0, 1.1]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[.025, .025, 2.2, 6]} /><meshStandardMaterial color="#e9e5d4" /></mesh><mesh position={[.25, 0, 1.8]}><boxGeometry args={[.5, .03, .34]} /><meshStandardMaterial color="#b84b3e" /></mesh></group>;
}

export function GlobeParkBatch14Assembly({ familyId, archetypeId, variantId, guides: _guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; archetypeId: string; variantId: string; guides: ParkGroundGuide[]; frame: ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const id = familyId as FamilyId;
  const slug = batch14ParkSkinForSelection(archetypeId, variantId)?.slug
    ?? batch15ParkSkinForSelection(archetypeId, variantId)?.slug
    ?? SLUG[id];
  const variantIndex = Number(variantId.match(/(?:_variant_|_v)([0-3])$/)?.[1] ?? 0);
  const asphalt = useMaps(slug, 'asphalt', 6);
  const lawn = useMaps(slug, 'lawn', 5);
  const paver = useMaps(slug, 'paver', 5);
  const planting = useMaps(slug, 'planting', 5);
  const safety = useMaps(slug, 'safety', 4);
  const timber = useMaps(slug, 'timber', 4);
  const cx = (frame.minX + frame.maxX) / 2;
  const cy = (frame.minY + frame.maxY) / 2;
  const base = terrainZ(cx, cy) + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const items: ReactNode[] = [];

  if (id === 'park_surface_parking_standard_v0' || id === 'park_green_parking_infrastructure_v1' || id === 'park_retail_parking_landscaped_v1') {
    const isRetail = id === 'park_retail_parking_landscaped_v1';
    const isGreen = (!isRetail && variantIndex === 1) || (isRetail && variantIndex === 1);
    const isScreened = variantIndex === 3 && !isRetail;
    const isGravel = isRetail && variantIndex === 2;
    const fieldMaps = isGravel ? safety : isGreen ? paver : asphalt;
    const fieldColor = isGravel ? '#f0e2c7' : isGreen ? '#dde8d5' : '#ffffff';
    items.push(<ParkingField key="parking" frame={frame} z={base} maps={fieldMaps} green={isGreen} retail={isRetail && variantIndex !== 2} baseColor={fieldColor} />);
    const poles = Math.max(2, Math.min(6, Math.floor(frame.width / 18)));
    for (let index = 0; index < poles; index += 1) items.push(<LightPole key={`pole-${index}`} x={frame.minX + frame.width * ((index + .5) / poles)} y={frame.maxY - frame.height * .12} z={base + .2} />);
    if (isGreen) {
      items.push(<FlatBox key="bioswale" x={cx} y={frame.minY + frame.height * .18} z={base + .2} width={frame.width * .78} depth={Math.max(2.4, frame.height * .10)} maps={planting} color="#526f4b" />);
    }
    if (isScreened) {
      const treeCount = Math.max(8, Math.min(20, Math.floor((frame.width + frame.height) / 8)));
      for (let index = 0; index < treeCount; index += 1) {
        const t = (index + .5) / treeCount;
        const horizontal = index % 2 === 0;
        items.push(<Tree key={`screen-${index}`} x={horizontal ? frame.minX + frame.width * t : frame.minX + frame.width * (index % 4 < 2 ? .05 : .95)} y={horizontal ? frame.minY + frame.height * (index % 4 < 2 ? .06 : .94) : frame.minY + frame.height * t} z={base + .2} />);
      }
    }
    if (!isRetail && variantIndex === 2) {
      items.push(<FlatBox key="urban-reservation" x={cx} y={frame.maxY - frame.height * .045} z={base + .18} width={frame.width * .62} depth={Math.max(1.6, frame.height * .07)} maps={paver} color="#aaa59c" height={.12} />);
    }
    if (isRetail && variantIndex !== 2) {
      items.push(<FlatBox key="store-reservation" x={cx} y={frame.maxY - frame.height * .045} z={base + .18} width={frame.width * .72} depth={Math.max(1.6, frame.height * .07)} maps={paver} color="#b9b4aa" height={.12} />);
      items.push(<group key="pylon" position={[frame.maxX - frame.width * .08, frame.minY + frame.height * .10, base]}><mesh position={[0, 0, 2.4]}><boxGeometry args={[.22, .22, 4.8]} /><meshStandardMaterial color="#515755" /></mesh><mesh position={[0, 0, 4.7]}><boxGeometry args={[2.1, .35, 1.25]} /><meshStandardMaterial color="#847a6e" /></mesh></group>);
    }
    if (isRetail && variantIndex === 3) items.push(<FlatBox key="frontage-plaza" x={cx} y={frame.maxY - frame.height * .15} z={base + .2} width={frame.width * .66} depth={frame.height * .13} maps={paver} color="#b4aa98" />);
  }

  if (id === 'park_structured_parking_urban_v2') {
    items.push(<FlatBox key="garage-reservation" x={cx} y={cy + frame.height * .06} z={base} width={frame.width * .72} depth={frame.height * .62} maps={variantIndex === 1 ? lawn : paver} color={variantIndex === 1 ? '#71825f' : '#a19d95'} height={.32} />);
    items.push(<ParkingField key="arrival" frame={{ ...frame, maxY: frame.minY + frame.height * .25, height: frame.height * .25 }} z={base} maps={asphalt} baseColor="#ffffff" />);
    items.push(<Line key="reserve-line" x={cx} y={cy + frame.height * .06} z={base + .34} width={frame.width * .66} depth={.16} color="#d4cfc2" />);
    if (variantIndex === 1 || variantIndex === 3) for (let index = 0; index < 8; index += 1) items.push(<Tree key={`garage-tree-${index}`} x={frame.minX + frame.width * (.06 + .88 * (index / 7))} y={frame.maxY - frame.height * .08} z={base + .36} />);
  }

  if (id === 'park_underground_parking_green_v1') {
    items.push(<FlatBox key="landscape" x={cx} y={cy} z={base} width={frame.width * .92} depth={frame.height * .90} maps={variantIndex === 0 ? asphalt : variantIndex === 2 ? paver : lawn} color={variantIndex === 0 ? '#5b5d5b' : variantIndex === 2 ? '#9b9588' : '#69845b'} />);
    const rampW = Math.min(9, frame.width * .28);
    const rampD = frame.height * .48;
    items.push(<FlatBox key="ramp" x={cx} y={cy - frame.height * .12} z={base + .16} width={rampW} depth={rampD} maps={asphalt} color="#414443" height={.12} />);
    [-1, 1].forEach((side) => items.push(<mesh key={`wall-${side}`} position={[cx + side * rampW / 2, cy - frame.height * .12, base + .75]}><boxGeometry args={[.24, rampD, 1.4]} /><meshStandardMaterial {...paver} color="#a8a49a" /></mesh>));
    items.push(<mesh key="opening" position={[cx, cy + rampD * .10, base + .42]}><boxGeometry args={[rampW * .82, .7, .82]} /><meshStandardMaterial color="#171b1c" /></mesh>);
    items.push(<FlatBox key="grate" x={frame.minX + frame.width * .23} y={frame.maxY - frame.height * .24} z={base + .2} width={Math.min(5, frame.width * .12)} depth={Math.min(2.4, frame.height * .08)} color="#353a39" />);
    const treeCount = variantIndex === 3 ? 10 : variantIndex === 1 ? 5 : 2;
    for (let index = 0; index < treeCount; index += 1) items.push(<Tree key={`tree-${index}`} x={frame.minX + frame.width * (.08 + .84 * ((index + .5) / treeCount))} y={frame.maxY - frame.height * .18} z={base + .2} />);
  }

  if (id === 'park_airport_general_aviation_v2') {
    items.push(<FlatBox key="field" x={cx} y={cy} z={base} width={frame.width * .96} depth={frame.height * .94} maps={lawn} color="#667956" />);
    const runwayW = Math.max(10, frame.height * (variantIndex === 2 ? .22 : .18));
    const runwayYs = variantIndex === 0 ? [cy - frame.height * .20, cy + frame.height * .20] : [cy - frame.height * .12];
    runwayYs.forEach((runwayY, runwayIndex) => items.push(<FlatBox key={`runway-${runwayIndex}`} x={cx} y={runwayY} z={base + .18} width={frame.width * .86} depth={runwayW} maps={asphalt} color="#494d4e" />));
    const dashes = Math.max(6, Math.min(18, Math.floor(frame.width / 18)));
    runwayYs.forEach((runwayY, runwayIndex) => { for (let index = 0; index < dashes; index += 1) items.push(<Line key={`dash-${runwayIndex}-${index}`} x={frame.minX + frame.width * (.10 + .80 * ((index + .5) / dashes))} y={runwayY} z={base + .38} width={Math.max(2, frame.width / dashes * .45)} depth={.24} />); });
    const apronWidth = frame.width * (variantIndex === 0 ? .54 : variantIndex === 2 ? .34 : .44);
    items.push(<FlatBox key="apron" x={frame.minX + frame.width * .32} y={frame.maxY - frame.height * .12} z={base + .18} width={apronWidth} depth={frame.height * (variantIndex === 0 ? .15 : .20)} maps={paver} color="#8d8d88" />);
    items.push(<FlatBox key="terminal-reservation" x={frame.minX + frame.width * .20} y={frame.maxY - frame.height * .045} z={base + .28} width={frame.width * (variantIndex === 0 ? .38 : variantIndex === 2 ? .26 : .32)} depth={frame.height * .07} color="#b0ada5" />);
    const aircraftCount = variantIndex === 0 ? 6 : variantIndex === 2 ? 3 : 4;
    for (let index = 0; index < aircraftCount; index += 1) items.push(<Aircraft key={`aircraft-${index}`} x={frame.minX + frame.width * (.13 + index * .08)} y={frame.maxY - frame.height * .15} z={base + .38} rotation={Math.PI / 2} />);
  }

  if (id === 'park_equestrian_working_stable_v1') {
    items.push(<FlatBox key="field" x={cx} y={cy} z={base} width={frame.width * .96} depth={frame.height * .94} maps={lawn} color="#70805a" />);
    const arenaX = cx + frame.width * .16;
    const arenaY = cy - frame.height * .08;
    const arenaW = frame.width * (variantIndex === 2 ? .34 : .52);
    const arenaD = frame.height * (variantIndex === 2 ? .38 : .48);
    items.push(<FlatBox key="arena" x={arenaX} y={arenaY} z={base + .18} width={arenaW} depth={arenaD} maps={safety} color="#a68a67" />);
    items.push(<FenceRect key="arena-fence" x={arenaX} y={arenaY} z={base + .2} width={arenaW} depth={arenaD} />);
    if (variantIndex === 2) {
      const secondX = cx - frame.width * .20;
      items.push(<FlatBox key="show-ring-2" x={secondX} y={arenaY} z={base + .18} width={arenaW} depth={arenaD} maps={safety} color="#b09a78" />);
      items.push(<FenceRect key="show-ring-2-fence" x={secondX} y={arenaY} z={base + .2} width={arenaW} depth={arenaD} />);
      items.push(<FlatBox key="bleacher-reservation" x={cx} y={arenaY + arenaD * .64} z={base + .2} width={frame.width * .46} depth={Math.max(1.6, frame.height * .06)} maps={paver} color="#9e998f" />);
    }
    items.push(<FlatBox key="barn-reservation" x={frame.minX + frame.width * .20} y={cy + frame.height * .20} z={base + .18} width={frame.width * .28} depth={frame.height * .22} maps={timber} color="#6f5844" height={.22} />);
    const paddockCount = variantIndex === 0 ? 5 : variantIndex === 2 ? 2 : variantIndex === 3 ? 4 : 3;
    for (let index = 0; index < paddockCount; index += 1) items.push(<FenceRect key={`paddock-${index}`} x={frame.minX + frame.width * (.10 + .80 * ((index + .5) / paddockCount))} y={frame.minY + frame.height * .20} z={base + .2} width={frame.width * (.70 / paddockCount)} depth={frame.height * .22} color={variantIndex === 3 ? '#505a56' : '#6d5a43'} />);
  }

  if (id === 'park_golf_seaside_links_v0') {
    const groundColor = variantIndex === 1 ? '#4f713f' : variantIndex === 2 ? '#b69a65' : variantIndex === 3 ? '#557b45' : '#8a805d';
    items.push(<FlatBox key="links" x={cx} y={cy} z={base} width={frame.width * .97} depth={frame.height * .95} maps={variantIndex === 2 ? safety : planting} color={groundColor} />);
    const holeCount = Math.max(3, Math.min(18, Math.floor(frame.width * frame.height / 3500)));
    for (let index = 0; index < holeCount; index += 1) {
      const column = index % 6;
      const row = Math.floor(index / 6);
      const x = frame.minX + frame.width * (.10 + .16 * column);
      const y = frame.minY + frame.height * (.20 + .30 * row + .04 * (column % 2));
      const fw = Math.min(frame.width * .13, 34);
      const fd = Math.min(frame.height * .24, 70);
      items.push(<mesh key={`fairway-${index}`} position={[x, y, base + .22]} rotation={[Math.PI / 2, 0, (index % 2 ? -.12 : .12)]} scale={[fw / 2, fd / 2, 1]}><cylinderGeometry args={[1, 1, .18, 28]} /><meshStandardMaterial {...lawn} color="#6f8656" roughness={.96} /></mesh>);
      items.push(<mesh key={`bunker-${index}`} position={[x + fw * .25, y + fd * .12, base + .35]} rotation={[Math.PI / 2, 0, 0]} scale={[Math.max(1.6, fw * .15), Math.max(1.2, fd * .05), 1]}><cylinderGeometry args={[1, 1, .08, 20]} /><meshStandardMaterial color="#c8b88e" roughness={.99} /></mesh>);
      items.push(<Flag key={`flag-${index}`} x={x} y={y + fd * .34} z={base + .3} />);
    }
    if (variantIndex === 1) for (let index = 0; index < 14; index += 1) items.push(<Tree key={`parkland-tree-${index}`} x={frame.minX + frame.width * (.04 + .92 * ((index * 7 % 17) / 17))} y={frame.minY + frame.height * (.08 + .84 * ((index * 11 % 19) / 19))} z={base + .2} />);
    if (variantIndex === 2) for (let index = 0; index < 12; index += 1) items.push(<mesh key={`xeric-${index}`} position={[frame.minX + frame.width * (.08 + .84 * ((index * 5 % 13) / 13)), frame.minY + frame.height * (.1 + .8 * ((index * 7 % 17) / 17)), base + .65]}><coneGeometry args={[.45, 1.3, 7]} /><meshStandardMaterial {...planting} color="#6f7750" /></mesh>);
    if (variantIndex === 3) items.push(<mesh key="water-hazard" position={[cx + frame.width * .24, cy - frame.height * .18, base + .3]} rotation={[Math.PI / 2, 0, 0]} scale={[frame.width * .08, frame.height * .10, 1]}><cylinderGeometry args={[1, 1, .08, 28]} /><meshStandardMaterial color="#3e7888" roughness={.24} metalness={.08} /></mesh>);
  }

  if (id === 'park_driving_range_single_tier_v0') {
    items.push(<FlatBox key="range" x={cx} y={cy - frame.height * .04} z={base} width={frame.width * .82} depth={frame.height * .82} maps={lawn} color="#668052" />);
    const targetCount = Math.max(4, Math.min(10, Math.floor(frame.height / 28)));
    for (let index = 0; index < targetCount; index += 1) {
      const x = frame.minX + frame.width * (.25 + .50 * ((index % 3) / 2));
      const y = frame.minY + frame.height * (.24 + .55 * ((index + .5) / targetCount));
      const targetColor = variantIndex === 1 ? ['#d8493f', '#e6b83f', '#3d79a8'][index % 3] : variantIndex === 3 ? ['#60b9c7', '#d7e1df'][index % 2] : index % 2 ? '#d8b55e' : '#d7d8cf';
      items.push(<mesh key={`target-${index}`} position={[x, y, base + .22]} scale={[2.4 + index * .2, 2.4 + index * .2, 1]}><ringGeometry args={[.55, 1, 28]} /><meshStandardMaterial color={targetColor} side={THREE.DoubleSide} /></mesh>);
      items.push(<Flag key={`flag-${index}`} x={x} y={y} z={base + .24} />);
    }
    const bayY = frame.maxY - frame.height * .09;
    items.push(<FlatBox key="bay-deck" x={cx} y={bayY} z={base + .16} width={frame.width * .72} depth={frame.height * .11} maps={paver} color="#88877f" />);
    const bays = Math.max(5, Math.min(16, Math.floor(frame.width / 5)));
    for (let index = 0; index <= bays; index += 1) {
      const x = cx - frame.width * .36 + frame.width * .72 * (index / bays);
      items.push(<mesh key={`post-${index}`} position={[x, bayY, base + (variantIndex === 1 || variantIndex === 3 ? 2.8 : 1.8)]}><boxGeometry args={[.12, .12, variantIndex === 1 || variantIndex === 3 ? 5.2 : 3.2]} /><meshStandardMaterial {...timber} color={variantIndex === 3 ? '#3e494b' : '#6d5643'} /></mesh>);
    }
    items.push(<mesh key="canopy" position={[cx, bayY, base + (variantIndex === 1 || variantIndex === 3 ? 5.45 : 3.35)]}><boxGeometry args={[frame.width * .74, frame.height * .13, .18]} /><meshStandardMaterial {...timber} color={variantIndex === 3 ? '#394448' : '#79614b'} /></mesh>);
    if (variantIndex === 2) for (let index = 0; index < 8; index += 1) items.push(<Tree key={`range-tree-${index}`} x={frame.minX + frame.width * (.08 + .84 * (index / 7))} y={frame.minY + frame.height * .10} z={base + .2} />);
    [-1, 1].forEach((side) => { for (let index = 0; index < 9; index += 1) items.push(<LightPole key={`net-${side}-${index}`} x={cx + side * frame.width * .43} y={frame.minY + frame.height * (.10 + .10 * index)} z={base} height={12} />); });
  }

  if (id === 'park_multi_sport_track_field_v3') {
    items.push(<FlatBox key="precinct" x={cx} y={cy} z={base} width={frame.width * .96} depth={frame.height * .94} maps={paver} color="#aaa497" />);
    if (variantIndex === 0) {
      [-.21, .21].forEach((dx, index) => {
        items.push(<FlatBox key={`community-field-${index}`} x={cx + frame.width * dx} y={cy - frame.height * .05} z={base + .2} width={frame.width * .34} depth={frame.height * .58} maps={lawn} color="#5d8050" />);
        items.push(<Line key={`community-center-${index}`} x={cx + frame.width * dx} y={cy - frame.height * .05} z={base + .41} width={frame.width * .30} depth={.12} />);
      });
      items.push(<FlatBox key="pavilion-reservation" x={cx} y={frame.maxY - frame.height * .08} z={base + .22} width={frame.width * .36} depth={frame.height * .08} maps={timber} color="#79614b" />);
    } else if (variantIndex === 1) {
      items.push(<FlatBox key="stadium-field" x={cx} y={cy} z={base + .2} width={frame.width * .58} depth={frame.height * .58} maps={lawn} color="#56804b" />);
      items.push(<Line key="stadium-center" x={cx} y={cy} z={base + .41} width={frame.width * .54} depth={.14} />);
      [-1, 1].forEach((side) => items.push(<FlatBox key={`grandstand-${side}`} x={cx + side * frame.width * .36} y={cy} z={base + .23} width={frame.width * .12} depth={frame.height * .62} maps={paver} color="#858783" />));
    } else if (variantIndex === 2) {
      items.push(<FlatBox key="dome-reservation" x={cx - frame.width * .08} y={cy} z={base + .2} width={frame.width * .58} depth={frame.height * .68} maps={paver} color="#c0c4c1" height={.26} />);
      items.push(<FlatBox key="training-field" x={frame.maxX - frame.width * .18} y={cy} z={base + .2} width={frame.width * .24} depth={frame.height * .52} maps={lawn} color="#5d8050" />);
    } else {
      const trackX = cx + frame.width * .10;
      const trackY = cy;
      const outerW = frame.width * .66;
      const outerD = frame.height * .72;
      items.push(<mesh key="track" position={[trackX, trackY, base + .25]} scale={[outerW / 2, outerD / 2, 1]}><ringGeometry args={[.73, 1, 64]} /><meshStandardMaterial {...safety} color="#a85443" side={THREE.DoubleSide} /></mesh>);
      items.push(<FlatBox key="infield" x={trackX} y={trackY} z={base + .21} width={outerW * .63} depth={outerD * .54} maps={lawn} color="#5f8252" />);
      items.push(<Line key="field-center" x={trackX} y={trackY} z={base + .42} width={outerW * .60} depth={.12} />);
      items.push(<FlatBox key="fieldhouse-reservation" x={frame.minX + frame.width * .11} y={cy} z={base + .25} width={frame.width * .14} depth={frame.height * .44} color="#9a958b" height={.22} />);
    }
    [[-.38, -.36], [.38, -.36], [-.38, .36], [.38, .36]].forEach(([dx, dy], index) => items.push(<LightPole key={`flood-${index}`} x={cx + frame.width * dx} y={cy + frame.height * dy} z={base + .2} height={10} />));
  }

  return <group>{items}</group>;
}
