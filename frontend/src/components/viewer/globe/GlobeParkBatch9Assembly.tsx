import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch22ParkSkinForSelection } from './parkBatch22Skins';

export interface Batch9ProgramFrame { minX: number; maxX: number; minY: number; maxY: number; width: number; height: number }
interface Point { x: number; y: number }
type Batch9FamilyId = Extract<ParkLegoFamilyId,
  | 'park_urban_pocket_rustic_v0' | 'park_neighborhood_contemporary_v3'
  | 'park_cemetery_classical_v0' | 'park_courtyard_linear_water_v1'
  | 'park_parklet_sf_timber_v1' | 'park_french_parterre_axis_v1'
  | 'park_london_railed_square_v1' | 'park_halifax_rose_bandstand_v0'
  | 'park_olmsted_multilandscape_v3' | 'park_hilltop_viewpoint_v3'>;

const SKIN_SLUG: Record<Batch9FamilyId, string> = {
  park_urban_pocket_rustic_v0: 'urban-pocket-rustic-v0',
  park_neighborhood_contemporary_v3: 'neighborhood-urban-contemporary-v3',
  park_cemetery_classical_v0: 'cemetery-classical-formal-v0',
  park_courtyard_linear_water_v1: 'courtyard-contemporary-water-v1',
  park_parklet_sf_timber_v1: 'street-parklet-sf-timber-v1',
  park_french_parterre_axis_v1: 'jardin-francaise-water-axis-v1',
  park_london_railed_square_v1: 'london-garden-square-railed-v1',
  park_halifax_rose_bandstand_v0: 'halifax-public-rose-bandstand-v0',
  park_olmsted_multilandscape_v3: 'olmsted-central-park-multilandscape-v3',
  park_hilltop_viewpoint_v3: 'hilltop-pacific-terraced-viewpoint-v3',
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

function center(guide: ParkGroundGuide, frame: Batch9ProgramFrame): Point {
  return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y };
}
function route(guide: ParkGroundGuide, frame: Batch9ProgramFrame): Point[] {
  if (guide.points && guide.points.length > 1) return guide.points.map(([x, y]) => ({ x: frame.minX + frame.width * x, y: frame.maxY - frame.height * y }));
  const c = center(guide, frame); const length = guide.widthM ?? guide.heightM ?? Math.max(guide.width * frame.width, guide.height * frame.height);
  const angle = ((guide.rotationDeg ?? (guide.kind === 'axis' ? 90 : 0)) * Math.PI) / 180;
  return [{ x: c.x - Math.cos(angle) * length / 2, y: c.y - Math.sin(angle) * length / 2 }, { x: c.x + Math.cos(angle) * length / 2, y: c.y + Math.sin(angle) * length / 2 }];
}
function Segment({ from, to, width, height, z, maps, color }: { from: Point; to: Point; width: number; height: number; z: number; maps?: MaterialMaps; color: string }) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return <mesh position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]} rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]} renderOrder={146}>
    <boxGeometry args={[length, width, height]} /><meshStandardMaterial {...maps} color={color} roughness={0.9} metalness={0.02} />
  </mesh>;
}
function Tree({ x, y, z, scale = 1, conifer = false }: { x: number; y: number; z: number; scale?: number; conifer?: boolean }) {
  return <group position={[x, y, z]} scale={scale}>
    <mesh position={[0, 0, 1.8]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.16, 0.24, 3.6, 8]} /><meshStandardMaterial color="#594638" roughness={0.98} /></mesh>
    <mesh position={[0, 0, conifer ? 4.5 : 4.3]} scale={conifer ? [1.1, 1.1, 1.9] : [1.45, 1.3, 1.0]}>{conifer ? <coneGeometry args={[1.8, 4.2, 9]} /> : <dodecahedronGeometry args={[1.65, 1]} />}<meshStandardMaterial color={conifer ? '#3f6049' : '#4f7049'} roughness={0.99} /></mesh>
  </group>;
}
function Planter({ x, y, z, maps, radius = 0.65 }: { x: number; y: number; z: number; maps: MaterialMaps; radius?: number }) {
  return <group position={[x,y,z]}><mesh position={[0,0,0.42]}><cylinderGeometry args={[radius,radius*0.9,0.84,14]} /><meshStandardMaterial {...maps} color="#9a6542" roughness={0.9} /></mesh><mesh position={[0,0,1.08]}><sphereGeometry args={[radius*0.78,10,7]} /><meshStandardMaterial color="#55724a" roughness={0.98} /></mesh></group>;
}
function WaterJet({ x, y, z, height }: { x: number; y: number; z: number; height: number }) {
  return <mesh position={[x,y,z+height/2]}><cylinderGeometry args={[0.035,0.055,height,6]} /><meshPhysicalMaterial color="#bde5e8" transparent opacity={0.72} roughness={0.05} transmission={0.25} /></mesh>;
}

export function GlobeParkBatch9Assembly({ familyId, archetypeId, variantId, guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; archetypeId?: string; variantId?: string; guides: ParkGroundGuide[]; frame: Batch9ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const selectedSkin = batch22ParkSkinForSelection(archetypeId ?? '', variantId ?? '');
  const slug = selectedSkin?.slug ?? SKIN_SLUG[familyId as Batch9FamilyId];
  const variantSkin = selectedSkin !== null;
  const paverMaps = useRoleMaps(slug, 'paver'); const plantingMaps = useRoleMaps(slug, 'planting', 5); const safetyMaps = useRoleMaps(slug, 'safety'); const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_urban_pocket_rustic_v0') {
    const bays = Math.min(4, Math.max(1, Math.floor(frame.width / 9))); const y = frame.maxY - frame.height * 0.18;
    return <group>{Array.from({ length: bays }, (_, i) => { const x=frame.minX+frame.width*(0.24+(i+.5)*.52/bays); const z=terrainZ(x,y)+lift; return <group key={i} position={[x,y,z]}>{[-1,1].map((side)=><mesh key={side} position={[side*1.35,0,1.35]}><boxGeometry args={[.16,.16,2.7]} /><meshStandardMaterial {...timberMaps} color="#74543b" roughness={.95} /></mesh>)}<mesh position={[0,0,2.72]}><boxGeometry args={[3.0,.20,.18]} /><meshStandardMaterial {...timberMaps} color="#74543b" roughness={.95} /></mesh></group>; })}{Array.from({length:Math.min(4,Math.max(2,Math.floor(frame.width/8)))},(_,i)=>{const x=frame.minX+frame.width*(.18+i*.64/Math.max(1,Math.min(3,Math.floor(frame.width/8))));const yTree=frame.minY+frame.height*(i%2?.30:.72);return <Tree key={i} x={x} y={yTree} z={terrainZ(x,yTree)+lift} scale={.78}/>})}{[-1,1].map((side)=><mesh key={side} position={[frame.minX+frame.width*(.5+side*.26),frame.minY+frame.height*.46,terrainZ(frame.minX+frame.width*(.5+side*.26),frame.minY+frame.height*.46)+lift+.5]} scale={[1.2,.85,.65]}><dodecahedronGeometry args={[.75,1]} /><meshStandardMaterial color="#847b6d" roughness={.99} /></mesh>)}</group>;
  }

  if (familyId === 'park_neighborhood_contemporary_v3') {
    const social=guides.find((g)=>g.kind==='rectangle'); const c=social?center(social,frame):{x:frame.minX+frame.width*.68,y:frame.minY+frame.height*.52}; const size=social?resolveParkGuideDimensionsM(social,frame):{width:frame.width*.3,height:frame.height*.28}; const z=terrainZ(c.x,c.y)+lift;
    return <group><mesh position={[c.x,c.y,z+.12]}><boxGeometry args={[size.width,size.height,.24]} /><meshStandardMaterial {...paverMaps} color="#9b9891" roughness={.9} /></mesh>{Array.from({length:9},(_,i)=>{const x=c.x+(i%3-1)*Math.min(3,size.width*.2);const y=c.y+(Math.floor(i/3)-1)*Math.min(3,size.height*.2);return <WaterJet key={i} x={x} y={y} z={z+.25} height={.45+(i%3)*.28}/>})}{Array.from({length:6},(_,i)=>{const angle=i*Math.PI*2/6;const x=frame.minX+frame.width*.5+Math.cos(angle)*frame.width*.36;const y=frame.minY+frame.height*.5+Math.sin(angle)*frame.height*.32;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.75}/>})}</group>;
  }

  if (familyId === 'park_cemetery_classical_v0') {
    const woodland=variantId==='cemetery_memorial_grounds_v1',sculptural=variantId==='cemetery_memorial_grounds_v2',romantic=variantId==='cemetery_memorial_grounds_v3';
    const cols=Math.min(12,Math.max(4,Math.floor(frame.width/(sculptural?18:12)))); const rows=Math.min(14,Math.max(4,Math.floor(frame.height/(woodland?15:11))));
    return <group>{Array.from({length:cols*rows},(_,i)=>{const col=i%cols,row=Math.floor(i/cols);const jitter=woodland?((i*37)%9-4)*.22:0;const x=frame.minX+frame.width*(.10+(col+.5)*.80/cols)+jitter;const y=frame.minY+frame.height*(.10+(row+.5)*.80/rows)-jitter*.45;if(Math.abs(x-(frame.minX+frame.width/2))<3.5)return null;const z=terrainZ(x,y)+lift;return <mesh key={i} position={[x,y,z+(sculptural?1.0:.48)]} rotation={[0,sculptural?.18:0,sculptural?((i%3)-1)*.2:0]}><boxGeometry args={[sculptural?1.1:.72,sculptural?.35:.20,sculptural?2:.96]} /><meshStandardMaterial {...safetyMaps} color={variantSkin?'#ffffff':romantic?'#b8aa98':'#c2bbae'} roughness={.96} /></mesh>})}<mesh position={[frame.minX+frame.width/2,frame.minY+frame.height/2,terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift+.5]}><cylinderGeometry args={[2.2,2.6,1.0,24]} /><meshStandardMaterial {...paverMaps} color={variantSkin?'#ffffff':'#aaa293'} roughness={.9} /></mesh>{woodland&&Array.from({length:Math.min(18,Math.max(8,Math.floor((frame.width+frame.height)/12)))},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.379)%.88));const y=frame.minY+frame.height*(.06+((i*.617)%.88));return <Tree key={`t${i}`} x={x} y={y} z={terrainZ(x,y)+lift} scale={.72+(i%3)*.1}/>})}</group>;
  }

  if (familyId === 'park_courtyard_linear_water_v1') {
    const water=guides.find((g)=>g.kind==='polyline');const points=water?route(water,frame):[];
    const neoclassical=variantId==='courtyard_plaza_v0',festival=variantId==='courtyard_plaza_v3';
    return <group>{points.slice(0,-1).map((point,i)=><Segment key={i} from={point} to={points[i+1]} width={neoclassical?3:1.4} height={.10} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[i+1].x,points[i+1].y))+lift+.14} maps={neoclassical?paverMaps:undefined} color={variantSkin?'#ffffff':'#5f858b'} />)}{guides.filter((g)=>g.kind==='rectangle').map((guide,i)=>{const c=center(guide,frame);const s=resolveParkGuideDimensionsM(guide,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,z+.36]}><boxGeometry args={[s.width,s.height,.72]} /><meshStandardMaterial {...(variantId==='courtyard_plaza_v2'?plantingMaps:paverMaps)} color={variantSkin?'#ffffff':'#807d75'} roughness={.88} /></mesh>{[-.3,.3].map((offset)=><Tree key={offset} x={c.x+s.width*offset} y={c.y} z={z+.72} scale={.58}/>)}</group>})}{neoclassical&&<group position={[frame.minX+frame.width/2,frame.minY+frame.height/2,terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift]}><mesh position={[0,0,.42]}><cylinderGeometry args={[2.2,2.6,.84,24]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh><WaterJet x={0} y={0} z={.84} height={2.1}/></group>}{festival&&Array.from({length:Math.min(5,Math.max(2,Math.floor(frame.width/9)))},(_,i)=>{const x=frame.minX+frame.width*(.15+i*.7/Math.max(1,Math.min(4,Math.floor(frame.width/9))));const y=frame.minY+frame.height*.25;const z=terrainZ(x,y)+lift;return <group key={`stall${i}`} position={[x,y,z]}><mesh position={[0,0,1]}><boxGeometry args={[3,1.8,2]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh><mesh position={[0,0,2.3]}><coneGeometry args={[2.1,1.1,4]}/><meshStandardMaterial {...safetyMaps} color="#ffffff"/></mesh></group>})}</group>;
  }

  if (familyId === 'park_parklet_sf_timber_v1') {
    const z=terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift;const bayCount=Math.min(6,Math.max(1,Math.floor(frame.width/4.2)));
    const timberDeck=variantId==='street_plaza_parklet_v1';
    return <group><mesh position={[frame.minX+frame.width/2,frame.minY+frame.height/2,z+.16]}><boxGeometry args={[frame.width*.92,frame.height*.82,.32]} /><meshStandardMaterial {...(timberDeck?timberMaps:paverMaps)} color={variantSkin?'#ffffff':'#8d6745'} roughness={.9} /></mesh>{Array.from({length:bayCount},(_,i)=>{const x=frame.minX+frame.width*(.10+(i+.5)*.80/bayCount);const y=frame.minY+frame.height*.52;return <group key={i}><mesh position={[x,y,z+.76]}><cylinderGeometry args={[.55,.55,.10,20]} /><meshStandardMaterial {...(variantId==='street_plaza_parklet_v2'?safetyMaps:timberMaps)} color={variantSkin?'#ffffff':'#7b5b40'} roughness={.9} /></mesh><mesh position={[x,y,z+.38]}><cylinderGeometry args={[.06,.09,.72,8]} /><meshStandardMaterial color="#333836" metalness={.55} roughness={.48} /></mesh><Planter x={x} y={frame.minY+frame.height*.18} z={z+.32} maps={paverMaps} radius={.38}/></group>})}<Segment from={{x:frame.minX+frame.width*.05,y:frame.maxY-frame.height*.08}} to={{x:frame.maxX-frame.width*.05,y:frame.maxY-frame.height*.08}} width={.12} height={1.2} z={z+.30} maps={timberDeck?timberMaps:paverMaps} color={variantSkin?'#ffffff':'#78583f'} /></group>;
  }

  if (familyId === 'park_french_parterre_axis_v1') {
    const axis=guides.find((g)=>g.kind==='axis');const points=axis?route(axis,frame):[];
    return <group>{points.length===2&&<Segment from={points[0]} to={points[1]} width={4} height={.12} z={Math.max(terrainZ(points[0].x,points[0].y),terrainZ(points[1].x,points[1].y))+lift+.12} color="#668d94" />}{guides.filter((g)=>g.kind==='rectangle').map((guide,i)=>{const c=center(guide,frame);const s=resolveParkGuideDimensionsM(guide,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,z+.24]}><boxGeometry args={[s.width,s.height,.48]} /><meshStandardMaterial {...plantingMaps} color={i%2?'#4f6543':'#566c46'} roughness={.97} /></mesh>{Array.from({length:4},(_,j)=>{const x=c.x+(j%2-.5)*s.width*.55;const y=c.y+(Math.floor(j/2)-.5)*s.height*.55;return <mesh key={j} position={[x,y,z+1]}><sphereGeometry args={[.8,10,7]} /><meshStandardMaterial color="#46603d" roughness={.98} /></mesh>})}</group>})}</group>;
  }

  if (familyId === 'park_london_railed_square_v1') {
    const inset=1.1,z=terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift;const rails=[[{x:frame.minX+inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.minY+inset}],[{x:frame.maxX-inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.maxY-inset}],[{x:frame.maxX-inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.maxY-inset}],[{x:frame.minX+inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.minY+inset}]];
    const trees=Math.min(16,Math.max(6,Math.floor((frame.width+frame.height)/15)));
    return <group>{rails.map(([from,to],i)=><Segment key={i} from={from} to={to} width={.10} height={1.35} z={z+.12} color="#252a28" />)}{Array.from({length:trees},(_,i)=>{const t=i/trees;const side=i%4;const x=side===0?frame.minX+frame.width*(.12+t*.76):side===2?frame.maxX-frame.width*(.12+t*.76):side===1?frame.maxX-frame.width*.12:frame.minX+frame.width*.12;const y=side===1?frame.minY+frame.height*(.12+t*.76):side===3?frame.maxY-frame.height*(.12+t*.76):side===0?frame.minY+frame.height*.12:frame.maxY-frame.height*.12;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.75}/>})}</group>;
  }

  if (familyId === 'park_halifax_rose_bandstand_v0') {
    const beds=guides.filter((g)=>g.kind==='ellipse').slice(0,2);const x=frame.minX+frame.width*.5,y=frame.maxY-frame.height*.28,z=terrainZ(x,y)+lift;
    return <group>{beds.map((bed,i)=>{const c=center(bed,frame);const s=resolveParkGuideDimensionsM(bed,frame);const base=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,base+.18]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.36,24]} /><meshStandardMaterial {...plantingMaps} color="#5b6845" roughness={.98} /></mesh>{Array.from({length:18},(_,j)=>{const a=j*Math.PI*2/18;return <mesh key={j} position={[c.x+Math.cos(a)*s.width*.34,c.y+Math.sin(a)*s.height*.34,base+.62]}><sphereGeometry args={[.28,8,6]} /><meshStandardMaterial color={['#9f4055','#d58e9d','#ece0d0'][j%3]} roughness={.9} /></mesh>})}</group>})}<group position={[x,y,z]}>{Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <mesh key={i} position={[Math.cos(a)*2.2,Math.sin(a)*2.2,1.7]}><cylinderGeometry args={[.10,.12,3.4,10]} /><meshStandardMaterial color="#e3dcc9" roughness={.82} /></mesh>})}<mesh position={[0,0,3.5]}><coneGeometry args={[3.0,1.5,8]} /><meshStandardMaterial {...timberMaps} color="#dad0b9" roughness={.82} /></mesh><mesh position={[0,0,.28]}><cylinderGeometry args={[2.8,2.8,.56,24]} /><meshStandardMaterial {...paverMaps} color="#aaa08e" roughness={.9} /></mesh></group></group>;
  }

  if (familyId === 'park_olmsted_multilandscape_v3') {
    const pond=guides.find((g)=>g.kind==='ellipse'&&g.color==='#5f8585');const bridge=guides.find((g)=>g.kind==='polyline');const bridgePoints=bridge?route(bridge,frame):[];const treeCount=Math.min(28,Math.max(10,Math.floor(frame.width*frame.height/900)));
    return <group>{pond&&(()=>{const c=center(pond,frame);const s=resolveParkGuideDimensionsM(pond,frame);const z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.10]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.20,36]} /><meshPhysicalMaterial color="#587f82" transparent opacity={.78} roughness={.12} /></mesh>})()}{bridgePoints.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={bridgePoints[i+1]} width={2.5} height={.32} z={Math.max(terrainZ(p.x,p.y),terrainZ(bridgePoints[i+1].x,bridgePoints[i+1].y))+lift+.38} maps={timberMaps} color="#755840" />)}{Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.367)%0.88));const y=frame.minY+frame.height*(.06+((i*.613)%0.88));if(x<frame.minX+frame.width*.47&&y>frame.minY+frame.height*.36&&y<frame.minY+frame.height*.68)return null;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.65+(i%4)*.08}/>})}</group>;
  }

  if (familyId === 'park_hilltop_viewpoint_v3') {
    const trail=guides.find((g)=>g.kind==='polyline');const points=trail?route(trail,frame):[];const decks=guides.filter((g)=>g.kind==='rectangle');
    return <group>{points.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={points[i+1]} width={2.8} height={.20} z={Math.max(terrainZ(p.x,p.y),terrainZ(points[i+1].x,points[i+1].y))+lift+.12} maps={paverMaps} color="#a49375" />)}{decks.map((deck,i)=>{const c=center(deck,frame);const s=resolveParkGuideDimensionsM(deck,frame);const z=terrainZ(c.x,c.y)+lift+i*.35;return <group key={i}><mesh position={[c.x,c.y,z+.34]}><boxGeometry args={[s.width,s.height,.68]} /><meshStandardMaterial {...safetyMaps} color="#918c84" roughness={.9} /></mesh><Segment from={{x:c.x-s.width/2,y:c.y+s.height/2}} to={{x:c.x+s.width/2,y:c.y+s.height/2}} width={.10} height={1.1} z={z+.68} color="#5e625f" /></group>})}{Array.from({length:Math.min(24,Math.max(8,Math.floor(frame.width*frame.height/1000)))},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.283)%0.88));const y=frame.minY+frame.height*(.06+((i*.527)%0.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.68+(i%3)*.08} conifer/>})}</group>;
  }
  return null;
}
