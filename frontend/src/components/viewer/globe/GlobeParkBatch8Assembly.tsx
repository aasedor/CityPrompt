import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

export interface Batch8ProgramFrame { minX: number; maxX: number; minY: number; maxY: number; width: number; height: number }
interface Point { x: number; y: number }
type Batch8FamilyId = Extract<ParkLegoFamilyId,
  | 'park_reclaimed_wharf_v0' | 'park_quarry_tier_cascade_v2'
  | 'park_estate_oak_picnic_v1' | 'park_constructed_wetland_boardwalk_v0'
  | 'park_academic_planted_court_v0' | 'park_campus_green_spine_v0'
  | 'park_botanical_rose_garden_v3' | 'park_research_arboretum_v0'
  | 'park_rewilding_reforestation_v1' | 'park_stormwater_arid_channel_v3'>;

const SKIN_SLUG: Record<Batch8FamilyId, string> = {
  park_reclaimed_wharf_v0: 'reclaimed-industrial-wharf-v0',
  park_quarry_tier_cascade_v2: 'quarry-limestone-tier-cascade-v2',
  park_estate_oak_picnic_v1: 'estate-oak-picnic-grove-v1',
  park_constructed_wetland_boardwalk_v0: 'constructed-urban-boardwalk-wetland-v0',
  park_academic_planted_court_v0: 'academic-modern-planted-courtyard-v0',
  park_campus_green_spine_v0: 'campus-green-planted-spine-v0',
  park_botanical_rose_garden_v3: 'botanical-romantic-rose-garden-v3',
  park_research_arboretum_v0: 'research-tree-collection-arboretum-v0',
  park_rewilding_reforestation_v1: 'rewilding-reforestation-zone-v1',
  park_stormwater_arid_channel_v3: 'stormwater-arid-rock-channel-v3',
};

interface MaterialMaps { map: THREE.Texture; normalMap: THREE.Texture; roughnessMap: THREE.Texture; aoMap: THREE.Texture }
function useRoleMaps(slug: string, role: string, repeat = 3): MaterialMaps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({ map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`, roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg` });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone(); texture.wrapS = THREE.RepeatWrapping; texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat, repeat); texture.needsUpdate = true; return [key, texture];
  })) as unknown as MaterialMaps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function center(guide: ParkGroundGuide, frame: Batch8ProgramFrame): Point { return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y }; }
function route(guide: ParkGroundGuide, frame: Batch8ProgramFrame): Point[] {
  if (guide.points && guide.points.length > 1) return guide.points.map(([x, y]) => ({ x: frame.minX + frame.width * x, y: frame.maxY - frame.height * y }));
  const c = center(guide, frame); const width = guide.widthM ?? guide.width * frame.width; const height = guide.heightM ?? guide.height * frame.height;
  const angle = ((guide.rotationDeg ?? 0) * Math.PI) / 180; const length = width || height;
  return [{ x: c.x - Math.cos(angle) * length / 2, y: c.y - Math.sin(angle) * length / 2 }, { x: c.x + Math.cos(angle) * length / 2, y: c.y + Math.sin(angle) * length / 2 }];
}
function Segment({ from, to, width, height, z, maps, color }: { from: Point; to: Point; width: number; height: number; z: number; maps?: MaterialMaps; color: string }) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return <mesh position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]} rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]} renderOrder={146}>
    <boxGeometry args={[length, width, height]} /><meshStandardMaterial {...maps} color={color} roughness={0.88} metalness={0.02} />
  </mesh>;
}
function Tree({ x, y, z, scale = 1, leaf = '#557047', young = false }: { x: number; y: number; z: number; scale?: number; leaf?: string; young?: boolean }) {
  const height = young ? 2.8 : 5.4;
  return <group position={[x, y, z]} scale={scale}>
    <mesh position={[0, 0, height * 0.38]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[young ? 0.08 : 0.2, young ? 0.11 : 0.3, height * 0.76, 8]} /><meshStandardMaterial color="#594536" roughness={0.96} /></mesh>
    <mesh position={[0, 0, height]} scale={young ? [0.55,0.48,0.8] : [1.35,1.2,1.0]}><dodecahedronGeometry args={[young ? 1.0 : 1.7, 1]} /><meshStandardMaterial color={leaf} roughness={0.98} /></mesh>
  </group>;
}
function PicnicTable({ x, y, z, maps, rotation = 0 }: { x: number; y: number; z: number; maps: MaterialMaps; rotation?: number }) {
  return <group position={[x,y,z]} rotation={[0,0,rotation]}>
    <mesh position={[0,0,0.78]}><boxGeometry args={[2.2,0.72,0.12]} /><meshStandardMaterial {...maps} color="#8b6745" roughness={0.92} /></mesh>
    {[-0.72,0.72].map((side) => <mesh key={side} position={[0,side,0.45]}><boxGeometry args={[2.2,0.32,0.10]} /><meshStandardMaterial {...maps} color="#806040" roughness={0.94} /></mesh>)}
    {[-0.66,0.66].map((along) => <mesh key={along} position={[along,0,0.38]}><boxGeometry args={[0.10,1.5,0.72]} /><meshStandardMaterial color="#414744" metalness={0.45} roughness={0.5} /></mesh>)}
  </group>;
}
function Boulder({ x, y, z, scale = 1, color = '#827a6d' }: { x: number; y: number; z: number; scale?: number; color?: string }) {
  return <mesh position={[x,y,z + 0.4 * scale]} scale={[1.1*scale,0.8*scale,0.65*scale]} rotation={[0.15,0.1,(x+y)*0.03]}><dodecahedronGeometry args={[0.75,1]} /><meshStandardMaterial color={color} roughness={0.98} /></mesh>;
}

export function GlobeParkBatch8Assembly({ familyId, guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; guides: ParkGroundGuide[]; frame: Batch8ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const slug = SKIN_SLUG[familyId as Batch8FamilyId];
  const paverMaps = useRoleMaps(slug, 'paver'); const plantingMaps = useRoleMaps(slug, 'planting', 5); const safetyMaps = useRoleMaps(slug, 'safety'); const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_reclaimed_wharf_v0') {
    const walk = guides.find((g) => g.kind === 'polyline'); const points = walk ? route(walk, frame) : [];
    const craneCount = Math.min(4, Math.max(1, Math.floor(frame.width / 34)));
    return <group>{points.slice(0,-1).map((point,index) => <Segment key={index} from={point} to={points[index+1]} width={5.5} height={0.24} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.22} maps={timberMaps} color="#806a53" />)}
      {Array.from({ length: craneCount }, (_, index) => { const x=frame.minX+frame.width*(0.18+(index+0.5)*0.64/craneCount); const y=frame.minY+frame.height*0.30; const z=terrainZ(x,y)+lift; return <group key={index} position={[x,y,z]}>
        <mesh position={[0,0,3.2]}><boxGeometry args={[3.0,2.4,6.4]} /><meshStandardMaterial {...safetyMaps} color="#7b412e" metalness={0.45} roughness={0.62} /></mesh>
        <mesh position={[0,0,6.8]} rotation={[0,0,-0.12]}><boxGeometry args={[11,0.42,0.48]} /><meshStandardMaterial {...safetyMaps} color="#7a3e2c" metalness={0.5} roughness={0.6} /></mesh>
        <mesh position={[4.7,0,4.0]} rotation={[0,-0.76,0]}><boxGeometry args={[0.22,0.22,7.5]} /><meshStandardMaterial color="#3f4543" metalness={0.55} roughness={0.5} /></mesh>
      </group>; })}
    </group>;
  }

  if (familyId === 'park_quarry_tier_cascade_v2') {
    const pools = guides.filter((g) => g.kind === 'rectangle'); const tierCount=Math.min(5,Math.max(3,Math.floor(frame.height/26)));
    return <group>{Array.from({length:tierCount},(_,i)=>{const inset=frame.width*(0.08+i*0.045); const y=frame.maxY-frame.height*(0.14+(i+0.5)*0.68/tierCount); const z=terrainZ(frame.minX+frame.width/2,y)+lift+i*0.7; return <group key={i}>
      <mesh position={[frame.minX+frame.width/2,y,z+0.22]}><boxGeometry args={[Math.max(12,frame.width-2*inset),frame.height*0.62/tierCount,0.44]} /><meshStandardMaterial {...(i%2?paverMaps:plantingMaps)} color={i%2?'#b5a998':'#627250'} roughness={0.94} /></mesh>
      <mesh position={[frame.minX+frame.width/2,y-frame.height*0.31/tierCount,z+0.75]}><boxGeometry args={[Math.max(12,frame.width-2*inset),0.6,1.5]} /><meshStandardMaterial {...paverMaps} color="#9b907d" roughness={0.96} /></mesh>
    </group>;})}
    {pools.map((pool,index)=>{const c=center(pool,frame); const s=resolveParkGuideDimensionsM(pool,frame); const z=terrainZ(c.x,c.y)+lift+index*0.45; return <group key={index}><mesh position={[c.x,c.y,z+0.20]}><boxGeometry args={[s.width+0.8,s.height+0.8,0.4]} /><meshStandardMaterial {...paverMaps} color="#8f8576" roughness={0.92} /></mesh><mesh position={[c.x,c.y,z+0.44]}><boxGeometry args={[s.width,s.height,0.08]} /><meshPhysicalMaterial color="#678b8d" transparent opacity={0.8} roughness={0.12} /></mesh></group>;})}
    </group>;
  }

  if (familyId === 'park_estate_oak_picnic_v1') {
    const cols=Math.min(5,Math.max(2,Math.floor(frame.width/28))); const rows=Math.min(4,Math.max(2,Math.floor(frame.height/28))); const count=cols*rows;
    return <group>{Array.from({length:count},(_,i)=>{const col=i%cols,row=Math.floor(i/cols); const x=frame.minX+frame.width*(0.14+(col+0.5)*0.72/cols); const y=frame.minY+frame.height*(0.14+(row+0.5)*0.72/rows); const z=terrainZ(x,y)+lift; return <group key={i}><Tree x={x} y={y} z={z} scale={0.9+(i%3)*0.08} leaf="#4f6e42" /><PicnicTable x={x+3.0} y={y+1.1} z={terrainZ(x+3,y+1.1)+lift} maps={timberMaps} rotation={i%2?Math.PI/2:0}/><mesh position={[x-2.2,y+1.2,z+0.7]}><cylinderGeometry args={[0.28,0.22,1.4,10]} /><meshStandardMaterial color="#393f3d" metalness={0.55} roughness={0.5} /></mesh></group>;})}</group>;
  }

  if (familyId === 'park_constructed_wetland_boardwalk_v0') {
    const cells=guides.filter((g)=>g.kind==='ellipse'); const walk=guides.find((g)=>g.kind==='polyline'); const points=walk?route(walk,frame):[];
    return <group>{cells.map((cell,index)=>{const c=center(cell,frame); const s=resolveParkGuideDimensionsM(cell,frame); const z=terrainZ(c.x,c.y)+lift; return <group key={index}><mesh position={[c.x,c.y,z+0.11]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,0.22,32]} /><meshPhysicalMaterial color="#527b74" transparent opacity={0.82} roughness={0.2} /></mesh>{Array.from({length:14},(_,j)=>{const a=j*2.4; const x=c.x+Math.cos(a)*s.width*0.35; const y=c.y+Math.sin(a)*s.height*0.35; return <mesh key={j} position={[x,y,terrainZ(x,y)+lift+0.65]}><coneGeometry args={[0.14,1.3+(j%3)*0.25,6]} /><meshStandardMaterial {...plantingMaps} color={j%2?'#718451':'#556f43'} roughness={0.98} /></mesh>;})}</group>;})}
      {points.slice(0,-1).map((point,index)=><Segment key={index} from={point} to={points[index+1]} width={2.2} height={0.22} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.48} maps={timberMaps} color="#80664d" />)}
    </group>;
  }

  if (familyId === 'park_academic_planted_court_v0') {
    const beds=guides.filter((g)=>g.kind==='rounded_rectangle'||g.kind==='rectangle');
    return <group>{beds.map((bed,index)=>{const c=center(bed,frame); const s=resolveParkGuideDimensionsM(bed,frame); const z=terrainZ(c.x,c.y)+lift; return <group key={index}>
      <mesh position={[c.x,c.y,z+0.38]}><boxGeometry args={[s.width,s.height,0.76]} /><meshStandardMaterial {...paverMaps} color="#80786b" roughness={0.9} /></mesh>
      <mesh position={[c.x,c.y,z+0.8]}><boxGeometry args={[Math.max(0.5,s.width-0.7),Math.max(0.5,s.height-0.7),0.16]} /><meshStandardMaterial {...plantingMaps} color="#596b45" roughness={0.98} /></mesh>
      {index%2===0&&<mesh position={[c.x,c.y-s.height/2-0.35,z+0.72]}><boxGeometry args={[Math.min(4,s.width*0.72),0.48,0.18]} /><meshStandardMaterial {...timberMaps} color="#947354" roughness={0.9} /></mesh>}
    </group>;})}</group>;
  }

  if (familyId === 'park_campus_green_spine_v0') {
    const axis=guides.find((g)=>g.kind==='polyline'||g.kind==='axis'); const points=axis?route(axis,frame):[]; const bays=Math.min(16,Math.max(4,Math.floor(frame.height/18)));
    return <group>{points.slice(0,-1).map((point,index)=><Segment key={index} from={point} to={points[index+1]} width={5.2} height={0.18} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.15} maps={paverMaps} color="#aaa59a" />)}
      {Array.from({length:bays},(_,i)=>[-1,1].map((side)=>{const x=frame.minX+frame.width*(0.5+side*0.29); const y=frame.maxY-frame.height*(0.08+(i+0.5)*0.84/bays); return <group key={`${i}-${side}`}><Tree x={x} y={y} z={terrainZ(x,y)+lift} scale={0.72} leaf="#4f7149" /><mesh position={[x-side*2.5,y,terrainZ(x-side*2.5,y)+lift+0.16]}><boxGeometry args={[3.2,2.8,0.32]} /><meshStandardMaterial {...plantingMaps} color="#65794e" roughness={0.98} /></mesh></group>;}))}
    </group>;
  }

  if (familyId === 'park_botanical_rose_garden_v3') {
    const beds=guides.filter((g)=>g.kind==='ellipse'||g.kind==='rounded_rectangle'); const arborCount=Math.min(5,Math.max(2,Math.floor(frame.width/24)));
    return <group>{beds.map((bed,index)=>{const c=center(bed,frame); const s=resolveParkGuideDimensionsM(bed,frame); const z=terrainZ(c.x,c.y)+lift; return <group key={index}><mesh position={[c.x,c.y,z+0.16]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,0.32,24]} /><meshStandardMaterial {...plantingMaps} color={index%2?'#73524f':'#7d6a53'} roughness={0.98} /></mesh>{Array.from({length:10},(_,j)=>{const a=j*Math.PI*2/10; return <mesh key={j} position={[c.x+Math.cos(a)*s.width*.32,c.y+Math.sin(a)*s.height*.32,z+0.6]}><sphereGeometry args={[0.32,8,6]} /><meshStandardMaterial color={['#a94757','#d79a9f','#e5c1c0'][j%3]} roughness={0.9} /></mesh>;})}</group>;})}
      {Array.from({length:arborCount},(_,i)=>{const x=frame.minX+frame.width*(0.18+(i+0.5)*0.64/arborCount); const y=frame.minY+frame.height*0.2; const z=terrainZ(x,y)+lift; return <group key={i} position={[x,y,z]}>{[-1,1].map(side=><mesh key={side} position={[side*1.1,0,1.4]}><boxGeometry args={[0.14,0.14,2.8]} /><meshStandardMaterial {...timberMaps} color="#755941" roughness={0.94} /></mesh>)}<mesh position={[0,0,2.8]}><torusGeometry args={[1.1,0.10,8,18,Math.PI]} /><meshStandardMaterial {...timberMaps} color="#755941" roughness={0.94} /></mesh></group>;})}
    </group>;
  }

  if (familyId === 'park_research_arboretum_v0') {
    const count=Math.min(34,Math.max(10,Math.floor(frame.width*frame.height/1200)));
    return <group>{Array.from({length:count},(_,i)=>{const x=frame.minX+frame.width*(0.08+((i*.347)%0.84)); const y=frame.minY+frame.height*(0.08+((i*.619)%0.84)); const z=terrainZ(x,y)+lift; return <group key={i}><Tree x={x} y={y} z={z} scale={0.58+(i%5)*0.11} leaf={['#496946','#617a45','#456b58'][i%3]} />{i%3===0&&<mesh position={[x+1.8,y,z+0.62]} rotation={[0.15,0,0]}><boxGeometry args={[0.9,0.08,0.62]} /><meshStandardMaterial {...timberMaps} color="#765f48" roughness={0.9} /></mesh>}{i%5===0&&<Boulder x={x-2} y={y+1.3} z={z} scale={0.8}/>}</group>;})}</group>;
  }

  if (familyId === 'park_rewilding_reforestation_v1') {
    const count=Math.min(72,Math.max(20,Math.floor(frame.width*frame.height/700)));
    return <group>{Array.from({length:count},(_,i)=>{const x=frame.minX+frame.width*(0.06+((i*.283)%0.88)); const y=frame.minY+frame.height*(0.06+((i*.491)%0.88)); return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={0.62+(i%4)*0.12} leaf={i%2?'#64805a':'#55704a'} young />;})}
      {Array.from({length:Math.min(10,Math.max(3,Math.floor(frame.width/24)))},(_,i)=>{const x=frame.minX+frame.width*(0.12+((i*.37)%0.76)); const y=frame.minY+frame.height*(0.18+((i*.53)%0.64)); const z=terrainZ(x,y)+lift; return <group key={i}>{[-1,0,1].map((n)=><mesh key={n} position={[x+n*0.8,y,z+0.35]} rotation={[0,Math.PI/2,n*.18]}><cylinderGeometry args={[0.18,0.28,3.4,8]} /><meshStandardMaterial {...timberMaps} color="#69523c" roughness={0.98} /></mesh>)}</group>;})}
    </group>;
  }

  if (familyId === 'park_stormwater_arid_channel_v3') {
    const channel=guides.find((g)=>g.kind==='polyline'); const points=channel?route(channel,frame):[];
    return <group>{points.slice(0,-1).map((point,index)=><group key={index}><Segment from={point} to={points[index+1]} width={6.5} height={0.25} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.08} maps={safetyMaps} color="#9a866b" />{Array.from({length:5},(_,j)=>{const t=(j+.5)/5; const x=point.x+(points[index+1].x-point.x)*t; const y=point.y+(points[index+1].y-point.y)*t+(j%2?1.8:-1.8); return <Boulder key={j} x={x} y={y} z={terrainZ(x,y)+lift} scale={0.65+(j%3)*.18} color="#8d806e" />;})}</group>)}
      {Array.from({length:Math.min(28,Math.max(10,Math.floor(frame.width*frame.height/800)))},(_,i)=>{const x=frame.minX+frame.width*(0.08+((i*.31)%0.84)); const y=frame.minY+frame.height*(0.08+((i*.57)%0.84)); return <mesh key={i} position={[x,y,terrainZ(x,y)+lift+0.65]}><coneGeometry args={[0.55,1.3+(i%3)*0.35,7]} /><meshStandardMaterial {...plantingMaps} color={i%2?'#718060':'#8b7650'} roughness={0.99} /></mesh>;})}
    </group>;
  }
  return null;
}
