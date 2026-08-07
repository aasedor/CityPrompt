import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import {
  resolveParkGuideDimensionsM,
  type ParkGroundGuide,
} from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch19ParkSkinForSelection } from './parkBatch19Skins';

export interface Batch6ProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
}

interface Point { x: number; y: number }

type Batch6FamilyId = Extract<ParkLegoFamilyId,
  | 'park_ice_rink_multipurpose_v3' | 'park_kayak_river_launch_v0'
  | 'park_tidal_marsh_cordgrass_v0' | 'park_cinema_lawn_projection_v1'
  | 'park_food_truck_permanent_v1' | 'park_great_lawn_v2'
  | 'park_campus_meadow_quad_v0' | 'park_urban_beach_family_v2'
  | 'park_velodrome_open_air_v0' | 'park_mtb_skills_dirt_v2'>;

const SKIN_SLUG: Record<Batch6FamilyId, string> = {
  park_ice_rink_multipurpose_v3: 'outdoor-ice-rink-multipurpose',
  park_kayak_river_launch_v0: 'kayak-river-launch',
  park_tidal_marsh_cordgrass_v0: 'tidal-marsh-cordgrass',
  park_cinema_lawn_projection_v1: 'outdoor-cinema-park-lawn',
  park_food_truck_permanent_v1: 'food-truck-permanent-park',
  park_great_lawn_v2: 'festival-great-lawn',
  park_campus_meadow_quad_v0: 'campus-naturalized-meadow-quad',
  park_urban_beach_family_v2: 'urban-beach-family-splash',
  park_velodrome_open_air_v0: 'velodrome-open-air',
  park_mtb_skills_dirt_v2: 'mountain-bike-skills-dirt',
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

function center(guide: ParkGroundGuide, frame: Batch6ProgramFrame): Point {
  return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y };
}

function route(guide: ParkGroundGuide, frame: Batch6ProgramFrame): Point[] {
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

function Segment({
  from, to, width, height, z, color,
}: { from: Point; to: Point; width: number; height: number; z: number; color: string }) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return (
    <mesh
      position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]}
      rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]}
      renderOrder={146}
    >
      <boxGeometry args={[length, width, height]} />
      <meshStandardMaterial color={color} roughness={0.86} metalness={0.02} />
    </mesh>
  );
}

function LightStandard({ x, y, z }: { x: number; y: number; z: number }) {
  return <group position={[x, y, z]}>
    <mesh position={[0, 0, 4]} rotation={[Math.PI / 2, 0, 0]}>
      <cylinderGeometry args={[0.09, 0.13, 8, 10]} />
      <meshStandardMaterial color="#434b4c" metalness={0.65} roughness={0.38} />
    </mesh>
    <mesh position={[0, 0, 7.7]}><boxGeometry args={[1.4, 0.35, 0.28]} /><meshStandardMaterial color="#353d3e" metalness={0.55} roughness={0.4} /></mesh>
  </group>;
}

function PicnicTable({ x, y, z, rotation = 0, timberMaps, neutralTint = false }: {
  x: number; y: number; z: number; rotation?: number; timberMaps: MaterialMaps; neutralTint?: boolean;
}) {
  return <group position={[x, y, z]} rotation={[0, 0, rotation]}>
    <mesh position={[0, 0, 0.72]}><boxGeometry args={[2.3, 0.72, 0.12]} /><meshStandardMaterial {...timberMaps} color={neutralTint ? '#ffffff' : '#a57a4f'} roughness={0.86} /></mesh>
    {[-0.72, 0.72].map((side) => <mesh key={side} position={[0, side, 0.44]}><boxGeometry args={[2.3, 0.32, 0.10]} /><meshStandardMaterial {...timberMaps} color={neutralTint ? '#ffffff' : '#95704a'} roughness={0.88} /></mesh>)}
    {[-0.72, 0.72].flatMap((side) => [-0.7, 0.7].map((along) => <mesh key={`${side}-${along}`} position={[along, side * 0.35, 0.35]} rotation={[0, side * 0.18, 0]}><boxGeometry args={[0.10, 0.10, 0.7]} /><meshStandardMaterial color="#343a39" metalness={0.55} roughness={0.48} /></mesh>))}
  </group>;
}

export function GlobeParkBatch6Assembly({
  familyId,
  archetypeId,
  variantId,
  guides,
  frame,
  terrainZ,
}: {
  familyId: ParkLegoFamilyId;
  archetypeId?: string;
  variantId?: string;
  guides: ParkGroundGuide[];
  frame: Batch6ProgramFrame;
  terrainZ: (x: number, y: number) => number;
}) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const selectedSkin = batch19ParkSkinForSelection(archetypeId ?? '', variantId ?? '');
  const variantSkin = selectedSkin !== null;
  const slug = selectedSkin?.slug ?? SKIN_SLUG[familyId as Batch6FamilyId];
  const paverMaps = useRoleMaps(slug, 'paver');
  const lawnMaps = useRoleMaps(slug, 'lawn', 4);
  const asphaltMaps = useRoleMaps(slug, 'asphalt');
  const plantingMaps = useRoleMaps(slug, 'planting', 5);
  const safetyMaps = useRoleMaps(slug, 'safety');
  const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_ice_rink_multipurpose_v3') {
    const pad = guides.find((guide) => guide.kind === 'rounded_rectangle');
    if (!pad) return null;
    const c = center(pad, frame); const s = resolveParkGuideDimensionsM(pad, frame);
    const yaw = -((pad.rotationDeg ?? 0) * Math.PI) / 180; const z = terrainZ(c.x, c.y) + lift;
    const boardH = 1.1;
    return <group position={[c.x, c.y, z]} rotation={[0, 0, yaw]}>
      <mesh position={[0, 0, 0.035]}><boxGeometry args={[s.width, s.height, 0.07]} /><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : '#d7e2e3'} roughness={0.54} metalness={0.02} /></mesh>
      {[-1, 1].map((side) => <mesh key={`long-${side}`} position={[0, side * s.height / 2, boardH / 2]}><boxGeometry args={[s.width, 0.12, boardH]} /><meshStandardMaterial color="#aeb9b9" transparent opacity={0.72} roughness={0.38} metalness={0.15} /></mesh>)}
      {[-1, 1].map((side) => <mesh key={`short-${side}`} position={[side * s.width / 2, 0, boardH / 2]}><boxGeometry args={[0.12, s.height, boardH]} /><meshStandardMaterial color="#aeb9b9" transparent opacity={0.72} roughness={0.38} metalness={0.15} /></mesh>)}
      {[-0.28, 0, 0.28].map((ratio, index) => <mesh key={ratio} position={[ratio * s.width, 0, 0.075]}><boxGeometry args={[index === 1 ? 0.18 : 0.14, s.height - 0.4, 0.018]} /><meshStandardMaterial color={index === 1 ? '#a65050' : '#5774a0'} roughness={0.7} /></mesh>)}
      {[-1, 1].flatMap((sx) => [-1, 1].map((sy) => <LightStandard key={`${sx}-${sy}`} x={sx * (s.width / 2 + 2.2)} y={sy * (s.height / 2 + 1.8)} z={0} />))}
    </group>;
  }

  if (familyId === 'park_kayak_river_launch_v0') {
    const dock = guides.find((guide) => guide.kind === 'rectangle');
    const launch = guides.find((guide) => guide.kind === 'line');
    if (!dock || !launch) return null;
    const c = center(dock, frame); const s = resolveParkGuideDimensionsM(dock, frame); const z = terrainZ(c.x, c.y) + lift;
    const launchRoute = route(launch, frame);
    return <group>
      <mesh position={[c.x, c.y, z + 0.25]}><boxGeometry args={[s.width, s.height, 0.5]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#8b765f'} roughness={0.86} /></mesh>
      {[-1, 1].map((side) => <mesh key={side} position={[c.x, c.y + side * (s.height / 2 - 0.18), z + 0.9]}><boxGeometry args={[s.width, 0.07, 0.07]} /><meshStandardMaterial color="#87908f" metalness={0.72} roughness={0.3} /></mesh>)}
      {launchRoute.length === 2 && <Segment from={launchRoute[0]} to={launchRoute[1]} width={2.4} height={0.18} z={Math.max(terrainZ(launchRoute[0].x, launchRoute[0].y), terrainZ(launchRoute[1].x, launchRoute[1].y)) + lift + 0.16} color="#a79a83" />}
      {[-1, 0, 1].map((rack) => <group key={rack} position={[frame.minX + frame.width * 0.24, frame.maxY - frame.height * (0.34 + rack * 0.035), terrainZ(frame.minX + frame.width * 0.24, frame.maxY - frame.height * 0.34) + lift + 0.8]}>
        <mesh rotation={[0, Math.PI / 2, 0]}><torusGeometry args={[1.4, 0.12, 8, 24, Math.PI]} /><meshStandardMaterial color="#555e5d" metalness={0.6} roughness={0.35} /></mesh>
        <mesh position={[0, 0, 0.15]} scale={[1.8, 0.38, 0.18]}><sphereGeometry args={[1, 18, 8]} /><meshStandardMaterial color={['#b64b38', '#d3a536', '#3f766e'][rack + 1]} roughness={0.68} /></mesh>
      </group>)}
    </group>;
  }

  if (familyId === 'park_tidal_marsh_cordgrass_v0') {
    const boardwalk = guides.find((guide) => guide.kind === 'polyline');
    const overlook = guides.find((guide) => guide.kind === 'ellipse');
    if (!boardwalk || !overlook) return null;
    const points = route(boardwalk, frame); const oc = center(overlook, frame); const os = resolveParkGuideDimensionsM(overlook, frame); const oz = terrainZ(oc.x, oc.y) + lift;
    return <group>
      {points.slice(0, -1).map((point, index) => <Segment key={index} from={point} to={points[index + 1]} width={2.6} height={0.24} z={Math.max(terrainZ(point.x, point.y), terrainZ(points[index + 1].x, points[index + 1].y)) + lift + 0.75} color="#88745d" />)}
      {points.map((point, index) => <mesh key={`post-${index}`} position={[point.x, point.y, terrainZ(point.x, point.y) + lift + 0.42]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.10, 0.12, 0.84, 8]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#6f5d49'} roughness={0.9} /></mesh>)}
      <mesh position={[oc.x, oc.y, oz + 0.88]}><cylinderGeometry args={[os.width / 2, os.width / 2, 0.24, 6]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#88745d'} roughness={0.88} /></mesh>
      <group position={[points[0]?.x ?? oc.x, points[0]?.y ?? oc.y, terrainZ(points[0]?.x ?? oc.x, points[0]?.y ?? oc.y) + lift]}>
        <mesh position={[0, 0, 1.3]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.10, 0.12, 2.6, 8]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#6f5d49'} /></mesh>
        <mesh position={[0, 0, 2.25]} rotation={[0.55, 0, 0]}><boxGeometry args={[1.6, 0.10, 0.9]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#9c8d73'} roughness={0.82} /></mesh>
      </group>
    </group>;
  }

  if (familyId === 'park_cinema_lawn_projection_v1') {
    const rectangles = guides.filter((guide) => guide.kind === 'rectangle');
    if (rectangles.length < 2) return null;
    const screen = rectangles[0]; const booth = rectangles[1]; const sc = center(screen, frame); const ss = resolveParkGuideDimensionsM(screen, frame); const sz = terrainZ(sc.x, sc.y) + lift;
    const bc = center(booth, frame); const bs = resolveParkGuideDimensionsM(booth, frame); const bz = terrainZ(bc.x, bc.y) + lift;
    return <group>
      <group position={[sc.x, sc.y, sz]}>
        <mesh position={[0, 0, 0.55]}><boxGeometry args={[ss.width + 2.4, Math.max(1.2, ss.height), 1.1]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#aaa59a'} roughness={0.88} /></mesh>
        <mesh position={[0, 0, 4.7]}><boxGeometry args={[ss.width, 0.32, 7.2]} /><meshStandardMaterial color="#252d2d" metalness={0.55} roughness={0.35} /></mesh>
        <mesh position={[0, -0.19, 4.7]}><planeGeometry args={[ss.width - 0.8, 6.3]} /><meshStandardMaterial color="#d5d7d0" roughness={0.48} /></mesh>
      </group>
      <group position={[bc.x, bc.y, bz]}>
        <mesh position={[0, 0, 1.6]}><boxGeometry args={[bs.width, bs.height, 3.2]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#766352'} roughness={0.86} /></mesh>
        <mesh position={[0, 0, 3.35]}><boxGeometry args={[bs.width + 0.6, bs.height + 0.6, 0.22]} /><meshStandardMaterial color="#464b48" metalness={0.3} roughness={0.55} /></mesh>
      </group>
      {[-0.22, 0, 0.22].map((ratio) => <group key={ratio} position={[frame.minX + frame.width * (0.5 + ratio), frame.maxY - frame.height * 0.70, terrainZ(frame.minX + frame.width * (0.5 + ratio), frame.maxY - frame.height * 0.70) + lift + 0.42]}><mesh><boxGeometry args={[3.4, 0.48, 0.18]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#98704a'} /></mesh></group>)}
    </group>;
  }

  if (familyId === 'park_food_truck_permanent_v1') {
    const bays = guides.filter((guide) => guide.kind === 'rectangle').slice(0, 8);
    const tables = [[0.38,0.44],[0.58,0.44],[0.38,0.64],[0.58,0.64]];
    return <group>
      {bays.map((bay, index) => { const c = center(bay, frame); const s = resolveParkGuideDimensionsM(bay, frame); const z = terrainZ(c.x, c.y) + lift; const yaw = -((bay.rotationDeg ?? 0) * Math.PI) / 180; return <group key={index} position={[c.x, c.y, z]} rotation={[0,0,yaw]}>
        <mesh position={[0,0,1.45]}><boxGeometry args={[s.width, s.height, 2.9]} /><meshStandardMaterial color={['#9a3f31','#c69d28','#577c6b','#ca7040','#3f5360','#bb623b','#73783d','#bb7441'][index]} roughness={0.65} metalness={0.05} /></mesh>
        <mesh position={[0,-s.height/2-0.015,1.65]}><planeGeometry args={[s.width*0.46,1.15]} /><meshStandardMaterial color="#202625" metalness={0.35} roughness={0.4} /></mesh>
        {[-s.width*0.32,s.width*0.32].map((wheel) => <mesh key={wheel} position={[wheel,0,0.38]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.38,0.38,s.height+0.16,12]} /><meshStandardMaterial color="#242827" roughness={0.72} /></mesh>)}
      </group>; })}
      {tables.map(([x,y],index) => { const px=frame.minX+frame.width*x; const py=frame.maxY-frame.height*y; return <PicnicTable key={index} x={px} y={py} z={terrainZ(px,py)+lift} rotation={index%2?Math.PI/2:0} timberMaps={timberMaps} neutralTint={variantSkin} />; })}
      {[-0.18,0,0.18].map((offset,row) => { const a={x:frame.minX+frame.width*0.22,y:frame.maxY-frame.height*(0.52+offset)}; const b={x:frame.minX+frame.width*0.80,y:a.y}; return <group key={row}><Segment from={a} to={b} width={0.04} height={0.04} z={Math.max(terrainZ(a.x,a.y),terrainZ(b.x,b.y))+lift+4.2} color="#303736" />{Array.from({length:8},(_,lamp)=>{const t=(lamp+0.5)/8;return <mesh key={lamp} position={[a.x+(b.x-a.x)*t,a.y,terrainZ(a.x+(b.x-a.x)*t,a.y)+lift+4.05]}><sphereGeometry args={[0.11,8,6]}/><meshStandardMaterial color="#f1c56b" emissive="#e5a83e" emissiveIntensity={0.5}/></mesh>;})}</group>; })}
    </group>;
  }

  if (familyId === 'park_great_lawn_v2') {
    const pads = guides.filter((guide) => guide.kind === 'rectangle');
    return <group>
      {pads.map((pad,index)=>{const c=center(pad,frame);const s=resolveParkGuideDimensionsM(pad,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={index} position={[c.x,c.y,z]}><mesh position={[0,0,0.12]}><boxGeometry args={[s.width,s.height,0.24]}/><meshStandardMaterial {...asphaltMaps} color={variantSkin ? '#ffffff' : '#676963'} roughness={0.82}/></mesh><mesh position={[0,0,0.46]}><cylinderGeometry args={[0.18,0.22,0.68,10]}/><meshStandardMaterial color="#444a48" metalness={0.45} roughness={0.5}/></mesh></group>;})}
      {[[-0.34,-0.28],[0.32,0.26]].map(([dx,dy],index)=><mesh key={index} position={[frame.minX+frame.width*(0.5+dx),frame.minY+frame.height*(0.5+dy),terrainZ(frame.minX+frame.width*(0.5+dx),frame.minY+frame.height*(0.5+dy))+lift-0.6]} scale={[10+index*3,7+index*2,1.2]}><sphereGeometry args={[1,20,10]}/><meshStandardMaterial {...(index ? plantingMaps : lawnMaps)} color={variantSkin ? '#ffffff' : index?'#708b55':'#66834e'} roughness={0.98}/></mesh>)}
    </group>;
  }

  if (familyId === 'park_campus_meadow_quad_v0') {
    const node = guides.find((guide) => guide.kind === 'ellipse' && guide.widthM === 12);
    if (!node) return null;
    const c = center(node, frame); const z = terrainZ(c.x,c.y)+lift;
    return <group>
      {Array.from({length:9},(_,index)=>{const angle=index*Math.PI*2/9;const radius=index%2?4.4:3.1;const x=c.x+Math.cos(angle)*radius;const y=c.y+Math.sin(angle)*radius;return <mesh key={index} position={[x,y,terrainZ(x,y)+lift+0.45]} rotation={[index*0.17,index*0.09,index*0.23]} scale={[1.1+(index%3)*0.25,0.8+(index%2)*0.22,0.65+(index%4)*0.16]}><dodecahedronGeometry args={[0.9,0]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#8e8b83'} roughness={0.92}/></mesh>;})}
      <mesh position={[c.x,c.y,z+0.04]}><cylinderGeometry args={[5.4,5.4,0.08,28]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#ada38d'} roughness={0.91}/></mesh>
    </group>;
  }

  if (familyId === 'park_urban_beach_family_v2') {
    const sails = guides.filter((guide) => guide.kind === 'line');
    const splash = guides.find((guide) => guide.kind === 'ellipse' && guide.widthM === 18);
    return <group>
      {sails.map((sail,index)=>{const c=center(sail,frame);const length=sail.widthM??14;const z=terrainZ(c.x,c.y)+lift;return <group key={index} position={[c.x,c.y,z]} rotation={[0,0,-((sail.rotationDeg??0)*Math.PI)/180]}>
        {[-1,0.92].map((side,post)=><mesh key={side} position={[side*length*0.42,post?1.6:-1.4,2.4+post*0.6]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.08,0.11,4.8+post*1.2,9]}/><meshStandardMaterial color="#68706f" metalness={0.62} roughness={0.4}/></mesh>)}
        <mesh position={[0,0,4.2]} rotation={[0.12,index%2?0.12:-0.12,0]}><circleGeometry args={[length*0.46,3]}/><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : index%2?'#d0b78d':'#c7a97b'} side={THREE.DoubleSide} roughness={0.72}/></mesh>
      </group>;})}
      {splash && (()=>{const c=center(splash,frame);const z=terrainZ(c.x,c.y)+lift;return <group>{Array.from({length:7},(_,index)=>{const angle=index*Math.PI*2/7;const r=index%2?4.2:2.2;const x=c.x+Math.cos(angle)*r;const y=c.y+Math.sin(angle)*r;return <group key={index} position={[x,y,terrainZ(x,y)+lift]}><mesh position={[0,0,0.75]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.11,0.16,1.5,9]}/><meshStandardMaterial color={index%2?'#d55b44':'#4b9d9b'} roughness={0.62}/></mesh><mesh position={[0,0,1.55]}><sphereGeometry args={[0.18,10,8]}/><meshStandardMaterial color="#8ecfd0" transparent opacity={0.78}/></mesh></group>;})}<group position={[c.x-7,c.y+5,z]}><mesh position={[0,0,1.6]}><boxGeometry args={[1.2,1.0,3.2]}/><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#9a744f'} roughness={0.86}/></mesh><mesh position={[0,0,3.4]}><boxGeometry args={[1.8,1.4,0.2]}/><meshStandardMaterial color="#d5b969" roughness={0.75}/></mesh></group></group>;})()}
    </group>;
  }

  if (familyId === 'park_velodrome_open_air_v0') {
    const track = guides.find((guide) => guide.kind === 'track');
    const bleacher = guides.find((guide) => guide.kind === 'rectangle');
    if (!track || !bleacher) return null;
    const c=center(track,frame);const s=resolveParkGuideDimensionsM(track,frame);const z=terrainZ(c.x,c.y)+lift;const yaw=-((track.rotationDeg??0)*Math.PI)/180;
    const bc=center(bleacher,frame);const bs=resolveParkGuideDimensionsM(bleacher,frame);const bz=terrainZ(bc.x,bc.y)+lift;
    return <group>
      <group position={[c.x,c.y,z+0.7]} rotation={[0,0,yaw]} scale={[s.width/s.height,1,0.22]}>
        <mesh><torusGeometry args={[s.height*0.36,s.height*0.075,18,96]}/><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : '#d3c093'} roughness={0.78}/></mesh>
        <mesh position={[0,0,-0.22]}><torusGeometry args={[s.height*0.285,s.height*0.026,12,96]}/><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : '#69a4b7'} roughness={0.72}/></mesh>
      </group>
      <group position={[bc.x,bc.y,bz]}>{Array.from({length:5},(_,step)=><mesh key={step} position={[0,step*0.78,0.28+step*0.34]}><boxGeometry args={[bs.width,1.0,0.56]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#a5a39d'} roughness={0.88}/></mesh>)}</group>
      <group position={[frame.minX+frame.width*0.82,frame.maxY-frame.height*0.82,terrainZ(frame.minX+frame.width*0.82,frame.maxY-frame.height*0.82)+lift]}><mesh position={[0,0,3]}><boxGeometry args={[6,5,6]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#74736f'} roughness={0.78}/></mesh><mesh position={[0,-2.55,3.7]}><planeGeometry args={[4.4,2.2]}/><meshStandardMaterial color="#1c2627" metalness={0.28} roughness={0.3}/></mesh></group>
    </group>;
  }

  if (familyId === 'park_mtb_skills_dirt_v2') {
    const loop=guides.find((guide)=>guide.kind==='track');const jumpLine=guides.find((guide)=>guide.kind==='polyline');if(!loop||!jumpLine)return null;
    const c=center(loop,frame);const s=resolveParkGuideDimensionsM(loop,frame);const z=terrainZ(c.x,c.y)+lift;const points=route(jumpLine,frame);
    return <group>
      <group position={[c.x,c.y,z+0.28]} scale={[s.width/s.height,1,0.20]}><mesh><torusGeometry args={[s.height*0.34,s.height*0.065,14,72]}/><meshStandardMaterial {...asphaltMaps} color={variantSkin ? '#ffffff' : '#8e7658'} roughness={0.95}/></mesh></group>
      {points.slice(1,-1).map((point,index)=>{const next=points[index+2]??point;const yaw=Math.atan2(next.y-point.y,next.x-point.x);const zz=terrainZ(point.x,point.y)+lift;return <group key={index} position={[point.x,point.y,zz]} rotation={[0,0,yaw]}><mesh position={[-1.2,0,0.48]} rotation={[0,-0.32,0]}><boxGeometry args={[2.8,4.0,0.7]}/><meshStandardMaterial {...asphaltMaps} color={variantSkin ? '#ffffff' : '#91714d'} roughness={0.96}/></mesh><mesh position={[1.5,0,0.40]} rotation={[0,0.22,0]}><boxGeometry args={[3.2,4.4,0.65]}/><meshStandardMaterial {...asphaltMaps} color={variantSkin ? '#ffffff' : '#9b7a52'} roughness={0.96}/></mesh></group>;})}
      {[-1,0,1].map((row)=>[-1,1].map((side)=>{const x=frame.minX+frame.width*(0.72+side*0.04);const y=frame.maxY-frame.height*(0.50+row*0.055);return <mesh key={`${row}-${side}`} position={[x,y,terrainZ(x,y)+lift+0.38]} rotation={[0,Math.PI/2,0]}><cylinderGeometry args={[0.22,0.26,4.5,10]}/><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#6e543d'} roughness={0.94}/></mesh>}))}
    </group>;
  }

  return null;
}
