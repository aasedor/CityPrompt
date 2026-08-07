import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch22ParkSkinForSelection } from './parkBatch22Skins';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { batch24ParkSkinForSelection } from './parkBatch24Skins';
import { batch25ParkSkinForSelection } from './parkBatch25Skins';

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
  const selectedSkin = batch25ParkSkinForSelection(archetypeId ?? '', variantId ?? '')
    ?? batch24ParkSkinForSelection(archetypeId ?? '', variantId ?? '')
    ?? batch23ParkSkinForSelection(archetypeId ?? '', variantId ?? '')
    ?? batch22ParkSkinForSelection(archetypeId ?? '', variantId ?? '');
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
    const paved=variantId==='parisian_jardin_v3',rill=variantId==='parisian_jardin_v2',clipped=variantId==='parisian_jardin_v0';
    const axisZ=points.length===2?Math.max(terrainZ(points[0].x,points[0].y),terrainZ(points[1].x,points[1].y))+lift+.12:lift;
    return <group>
      {paved&&<mesh position={[frame.minX+frame.width/2,frame.minY+frame.height/2,terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift+.10]}><boxGeometry args={[frame.width*.92,frame.height*.88,.20]}/><meshStandardMaterial {...paverMaps} color="#ffffff" roughness={.94}/></mesh>}
      {points.length===2&&!paved&&<Segment from={points[0]} to={points[1]} width={clipped?2.4:rill?1.25:4} height={.12} z={axisZ} maps={clipped?paverMaps:undefined} color={variantSkin?'#ffffff':'#668d94'} />}
      {points.length===2&&rill&&[-1,1].map((side)=><Segment key={side} from={{x:points[0].x+side*3,y:points[0].y}} to={{x:points[1].x+side*3,y:points[1].y}} width={.8} height={.10} z={axisZ+.02} color="#668d94"/>)}
      {!paved&&guides.filter((g)=>g.kind==='rectangle').map((guide,i)=>{const c=center(guide,frame);const s=resolveParkGuideDimensionsM(guide,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,z+.24]}><boxGeometry args={[s.width,s.height,.48]} /><meshStandardMaterial {...plantingMaps} color={variantSkin?'#ffffff':i%2?'#4f6543':'#566c46'} roughness={.97} /></mesh>{Array.from({length:clipped?6:4},(_,j)=>{const columns=clipped?3:2,x=c.x+(j%columns-(columns-1)/2)*s.width*.25;const y=c.y+(Math.floor(j/columns)-.5)*s.height*.55;return <mesh key={j} position={[x,y,z+1]}><sphereGeometry args={[clipped?.62:.8,10,7]} /><meshStandardMaterial color="#46603d" roughness={.98} /></mesh>})}</group>})}
      {paved&&Array.from({length:6},(_,i)=>{const a=i*Math.PI*2/6,x=frame.minX+frame.width/2+Math.cos(a)*frame.width*.31,y=frame.minY+frame.height/2+Math.sin(a)*frame.height*.28;return <Planter key={i} x={x} y={y} z={terrainZ(x,y)+lift+.2} maps={paverMaps} radius={.52}/>})}
    </group>;
  }

  if (familyId === 'park_london_railed_square_v1' && variantId && variantId !== 'london_garden_square_v1') {
    const lush = variantId === 'london_garden_square_v2';
    const cafe = variantId === 'london_garden_square_v3';
    const cx = frame.minX + frame.width / 2; const cy = frame.minY + frame.height / 2;
    const base = terrainZ(cx, cy) + lift;
    const bedCount = lush ? 8 : cafe ? 3 : 6;
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.92,frame.height*.88,.22]} /><meshStandardMaterial {...(cafe?paverMaps:plantingMaps)} color="#ffffff" roughness={.96} /></mesh>
      {!cafe&&<><Segment from={{x:frame.minX+frame.width*.08,y:cy}} to={{x:frame.maxX-frame.width*.08,y:cy}} width={2.5} height={.16} z={base+.22} maps={paverMaps} color="#ffffff"/><Segment from={{x:cx,y:frame.minY+frame.height*.08}} to={{x:cx,y:frame.maxY-frame.height*.08}} width={2.5} height={.16} z={base+.22} maps={paverMaps} color="#ffffff"/></>}
      {Array.from({length:bedCount},(_,i)=>{const columns=lush?4:3;const row=Math.floor(i/columns);const x=frame.minX+frame.width*(.16+(i%columns)*.68/Math.max(1,columns-1));const y=frame.minY+frame.height*(lush?.28+row*.42:.25+row*.50);const z=terrainZ(x,y)+lift;return <group key={i}><mesh position={[x,y,z+.36]}><boxGeometry args={[Math.min(lush?5:4,frame.width*.16),Math.min(lush?2.2:2.8,frame.height*.14),.72]}/><meshStandardMaterial {...(lush?paverMaps:plantingMaps)} color="#ffffff" roughness={.96}/></mesh>{!cafe&&<mesh position={[x,y,z+.86]} scale={[1.4,.7,.55]}><dodecahedronGeometry args={[1,1]}/><meshStandardMaterial {...plantingMaps} color="#ffffff" roughness={.98}/></mesh>}</group>})}
      {Array.from({length:cafe?6:lush?8:6},(_,i)=>{const x=frame.minX+frame.width*(.10+((i*.37)%.80));const y=cafe?frame.minY+frame.height*(.25+(i%2)*.46):frame.minY+frame.height*(i%2?.12:.88);const z=terrainZ(x,y)+lift;return cafe?<group key={i}><mesh position={[x,y,z+.74]}><cylinderGeometry args={[.55,.55,.10,18]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh><mesh position={[x,y,z+.37]}><cylinderGeometry args={[.06,.08,.70,8]}/><meshStandardMaterial color="#343936" metalness={.5}/></mesh></group>:<Tree key={i} x={x} y={y} z={z+.22} scale={lush?.72:.64}/>})}
    </group>;
  }

  if (familyId === 'park_london_railed_square_v1') {
    const inset=1.1,z=terrainZ(frame.minX+frame.width/2,frame.minY+frame.height/2)+lift;const rails=[[{x:frame.minX+inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.minY+inset}],[{x:frame.maxX-inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.maxY-inset}],[{x:frame.maxX-inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.maxY-inset}],[{x:frame.minX+inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.minY+inset}]];
    const trees=Math.min(16,Math.max(6,Math.floor((frame.width+frame.height)/15)));
    return <group>{rails.map(([from,to],i)=><Segment key={i} from={from} to={to} width={.10} height={1.35} z={z+.12} color="#252a28" />)}{Array.from({length:trees},(_,i)=>{const t=i/trees;const side=i%4;const x=side===0?frame.minX+frame.width*(.12+t*.76):side===2?frame.maxX-frame.width*(.12+t*.76):side===1?frame.maxX-frame.width*.12:frame.minX+frame.width*.12;const y=side===1?frame.minY+frame.height*(.12+t*.76):side===3?frame.maxY-frame.height*(.12+t*.76):side===0?frame.minY+frame.height*.12:frame.maxY-frame.height*.12;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.75}/>})}</group>;
  }

  if (familyId === 'park_halifax_rose_bandstand_v0' && variantId && variantId !== 'halifax_public_gardens_v0') {
    const concert = variantId === 'halifax_public_gardens_v1';
    const autumn = variantId === 'halifax_public_gardens_v2';
    const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift;
    const bedCount=concert?4:autumn?6:10;
    return <group>
      <Segment from={{x:frame.minX+frame.width*.08,y:cy}} to={{x:frame.maxX-frame.width*.08,y:cy}} width={2.4} height={.18} z={base+.18} maps={paverMaps} color="#ffffff"/>
      <Segment from={{x:cx,y:frame.minY+frame.height*.08}} to={{x:cx,y:frame.maxY-frame.height*.08}} width={2.4} height={.18} z={base+.18} maps={paverMaps} color="#ffffff"/>
      {Array.from({length:bedCount},(_,i)=>{const a=i*Math.PI*2/bedCount,x=cx+Math.cos(a)*frame.width*(concert?.27:.32),y=cy+Math.sin(a)*frame.height*(concert?.24:.29),z=terrainZ(x,y)+lift;return <group key={i}><mesh position={[x,y,z+.24]} scale={[Math.min(2.8,frame.width*.10),Math.min(1.6,frame.height*.07),1]} rotation={[0,0,a]}><cylinderGeometry args={[1,1,.48,18]}/><meshStandardMaterial {...plantingMaps} color="#ffffff" roughness={.98}/></mesh>{!autumn&&Array.from({length:5},(_,j)=>{const color=variantId==='halifax_public_gardens_v3'?['#e07d7f','#f0c95e','#d95f82'][j%3]:['#9f4055','#d58e9d','#ece0d0'][j%3];return <mesh key={j} position={[x+(j-2)*.32,y,z+.60]}><sphereGeometry args={[.22,8,6]}/><meshStandardMaterial color={color} roughness={.92}/></mesh>})}</group>})}
      {concert&&<group position={[cx,cy+frame.height*.20,base]}>{Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <mesh key={i} position={[Math.cos(a)*2.1,Math.sin(a)*2.1,1.65]}><cylinderGeometry args={[.09,.11,3.3,10]}/><meshStandardMaterial color="#e3dcc9"/></mesh>})}<mesh position={[0,0,3.35]}><coneGeometry args={[2.9,1.45,8]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh><mesh position={[0,0,.28]}><cylinderGeometry args={[2.7,2.7,.56,24]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh></group>}
      {Array.from({length:autumn?10:6},(_,i)=>{const x=frame.minX+frame.width*(.08+((i*.31)%.84));const y=frame.minY+frame.height*(i%2?.10:.90);return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.70}/>})}
      <Segment from={{x:cx-3,y:frame.minY+frame.height*.06}} to={{x:cx+3,y:frame.minY+frame.height*.06}} width={.12} height={1.5} z={base+.1} color="#292d2b"/>
    </group>;
  }

  if (familyId === 'park_halifax_rose_bandstand_v0') {
    const beds=guides.filter((g)=>g.kind==='ellipse').slice(0,2);const x=frame.minX+frame.width*.5,y=frame.maxY-frame.height*.28,z=terrainZ(x,y)+lift;
    return <group>{beds.map((bed,i)=>{const c=center(bed,frame);const s=resolveParkGuideDimensionsM(bed,frame);const base=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,base+.18]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.36,24]} /><meshStandardMaterial {...plantingMaps} color="#5b6845" roughness={.98} /></mesh>{Array.from({length:18},(_,j)=>{const a=j*Math.PI*2/18;return <mesh key={j} position={[c.x+Math.cos(a)*s.width*.34,c.y+Math.sin(a)*s.height*.34,base+.62]}><sphereGeometry args={[.28,8,6]} /><meshStandardMaterial color={['#9f4055','#d58e9d','#ece0d0'][j%3]} roughness={.9} /></mesh>})}</group>})}<group position={[x,y,z]}>{Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <mesh key={i} position={[Math.cos(a)*2.2,Math.sin(a)*2.2,1.7]}><cylinderGeometry args={[.10,.12,3.4,10]} /><meshStandardMaterial color="#e3dcc9" roughness={.82} /></mesh>})}<mesh position={[0,0,3.5]}><coneGeometry args={[3.0,1.5,8]} /><meshStandardMaterial {...timberMaps} color="#dad0b9" roughness={.82} /></mesh><mesh position={[0,0,.28]}><cylinderGeometry args={[2.8,2.8,.56,24]} /><meshStandardMaterial {...paverMaps} color="#aaa08e" roughness={.9} /></mesh></group></group>;
  }

  if (familyId === 'park_olmsted_multilandscape_v3' && variantId && variantId !== 'picturesque_olmsted_park_v3') {
    const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift;
    if (variantId === 'picturesque_olmsted_park_v0') {
      const pondX=frame.minX+frame.width*.73,pondY=frame.minY+frame.height*.28;
      return <group>
        <mesh position={[cx,cy,base+.08]} scale={[frame.width*.34,frame.height*.30,1]}><cylinderGeometry args={[1,1,.16,48]}/><meshStandardMaterial {...plantingMaps} color="#ffffff" roughness={.99}/></mesh>
        <mesh position={[pondX,pondY,terrainZ(pondX,pondY)+lift+.12]} scale={[frame.width*.11,frame.height*.09,1]}><cylinderGeometry args={[1,1,.16,32]}/><meshPhysicalMaterial color="#527b7d" transparent opacity={.8} roughness={.18}/></mesh>
        {[[.08,.18,.43,.44],[.43,.44,.68,.32],[.68,.32,.90,.70]].map((p,i)=>{const from={x:frame.minX+frame.width*p[0],y:frame.minY+frame.height*p[1]},to={x:frame.minX+frame.width*p[2],y:frame.minY+frame.height*p[3]};return <Segment key={i} from={from} to={to} width={2.1} height={.16} z={Math.max(terrainZ(from.x,from.y),terrainZ(to.x,to.y))+lift+.14} maps={paverMaps} color="#ffffff"/>})}
        {Array.from({length:20},(_,i)=>{const a=i*Math.PI*2/20,rr=i%2?.42:.47,x=cx+Math.cos(a)*frame.width*rr,y=cy+Math.sin(a)*frame.height*rr;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.65+(i%4)*.07}/>})}
      </group>;
    }
    if (variantId === 'picturesque_olmsted_park_v1') {
      const points=[[.08,.12],[.78,.22],[.24,.38],[.82,.54],[.30,.70],[.70,.86]].map(([x,y])=>({x:frame.minX+frame.width*x,y:frame.minY+frame.height*y}));
      const tx=frame.minX+frame.width*.70,ty=frame.minY+frame.height*.86,tz=terrainZ(tx,ty)+lift+1.1;
      return <group>
        {points.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={points[i+1]} width={3.4} height={.22} z={Math.max(terrainZ(p.x,p.y),terrainZ(points[i+1].x,points[i+1].y))+lift+i*.17} maps={paverMaps} color="#ffffff"/>)}
        <mesh position={[tx,ty,tz]}><boxGeometry args={[Math.min(22,frame.width*.22),Math.min(12,frame.height*.14),2.2]}/><meshStandardMaterial {...paverMaps} color="#ffffff" roughness={.95}/></mesh>
        <group position={[tx,ty,tz+1.1]}>{[-1,1].flatMap(sx=>[-1,1].map(sy=><mesh key={`${sx}-${sy}`} position={[sx*3.4,sy*2.2,1.6]}><boxGeometry args={[.25,.25,3.2]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh>))}<mesh position={[0,0,3.35]}><boxGeometry args={[8,5.4,.34]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh></group>
        {Array.from({length:28},(_,i)=>{const x=frame.minX+frame.width*(.04+((i*.347)%.92)),y=frame.minY+frame.height*(.04+((i*.619)%.92));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.58+(i%4)*.08}/>})}
      </group>;
    }
    const lakeX=frame.minX+frame.width*.72,lakeY=frame.minY+frame.height*.35;
    return <group>
      <mesh position={[frame.minX+frame.width*.30,frame.minY+frame.height*.62,base+.09]} scale={[frame.width*.24,frame.height*.23,1]}><cylinderGeometry args={[1,1,.18,48]}/><meshStandardMaterial {...plantingMaps} color="#ffffff" roughness={.99}/></mesh>
      <mesh position={[lakeX,lakeY,terrainZ(lakeX,lakeY)+lift+.10]} scale={[frame.width*.19,frame.height*.14,1]}><cylinderGeometry args={[1,1,.16,48]}/><meshPhysicalMaterial color="#517b80" transparent opacity={.82}/></mesh>
      <Segment from={{x:frame.minX+frame.width*.48,y:frame.minY+frame.height*.20}} to={{x:frame.minX+frame.width*.67,y:frame.minY+frame.height*.50}} width={2.8} height={.28} z={base+.48} maps={timberMaps} color="#ffffff"/>
      {Array.from({length:24},(_,i)=>{const x=frame.minX+frame.width*(.05+((i*.383)%.9)),y=frame.minY+frame.height*(.05+((i*.571)%.9));if(x<frame.minX+frame.width*.52&&y>frame.minY+frame.height*.40)return null;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.6+(i%3)*.08}/>})}
    </group>;
  }

  if (familyId === 'park_olmsted_multilandscape_v3') {
    const pond=guides.find((g)=>g.kind==='ellipse'&&g.color==='#5f8585');const bridge=guides.find((g)=>g.kind==='polyline');const bridgePoints=bridge?route(bridge,frame):[];const treeCount=Math.min(28,Math.max(10,Math.floor(frame.width*frame.height/900)));
    return <group>{pond&&(()=>{const c=center(pond,frame);const s=resolveParkGuideDimensionsM(pond,frame);const z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.10]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.20,36]} /><meshPhysicalMaterial color="#587f82" transparent opacity={.78} roughness={.12} /></mesh>})()}{bridgePoints.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={bridgePoints[i+1]} width={2.5} height={.32} z={Math.max(terrainZ(p.x,p.y),terrainZ(bridgePoints[i+1].x,bridgePoints[i+1].y))+lift+.38} maps={timberMaps} color="#755840" />)}{Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.367)%0.88));const y=frame.minY+frame.height*(.06+((i*.613)%0.88));if(x<frame.minX+frame.width*.47&&y>frame.minY+frame.height*.36&&y<frame.minY+frame.height*.68)return null;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.65+(i%4)*.08}/>})}</group>;
  }

  if (familyId === 'park_hilltop_viewpoint_v3' && variantId && variantId !== 'hilltop_topographic_park_v3') {
    const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift,r=Math.min(frame.width,frame.height)*.30;
    if (variantId === 'hilltop_topographic_park_v0') return <group>
      {[1,.72,.45].map((scale,i)=><mesh key={scale} position={[cx,cy,base+i*.58]} scale={[r*scale,r*scale*.82,1]}><ringGeometry args={[.70,1,44]}/><meshStandardMaterial {...paverMaps} color="#ffffff" roughness={.96}/></mesh>)}
      <mesh position={[cx,cy,base+1.95]}><cylinderGeometry args={[r*.22,r*.22,.24,32]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh>
      {Array.from({length:14},(_,i)=>{const a=i*Math.PI*2/14,rr=r*(i%2?.78:1.05),x=cx+Math.cos(a)*rr,y=cy+Math.sin(a)*rr*.82;return <group key={i} position={[x,y,terrainZ(x,y)+lift]}><mesh position={[0,0,2.8]}><cylinderGeometry args={[.12,.18,5.6,8]}/><meshStandardMaterial color="#4e4439"/></mesh><mesh position={[0,0,5.6]}><coneGeometry args={[.72,4.8,9]}/><meshStandardMaterial {...plantingMaps} color="#ffffff"/></mesh></group>})}
    </group>;
    if (variantId === 'hilltop_topographic_park_v1') {
      const ps=[[.08,.08],[.82,.18],[.18,.34],[.80,.50],[.22,.67],[.70,.84]].map(([x,y])=>({x:frame.minX+frame.width*x,y:frame.minY+frame.height*y}));
      const tx=ps[ps.length-1].x,ty=ps[ps.length-1].y,tz=terrainZ(tx,ty)+lift+1.6;
      return <group>{ps.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={ps[i+1]} width={3} height={.20} z={Math.max(terrainZ(p.x,p.y),terrainZ(ps[i+1].x,ps[i+1].y))+lift+i*.20} maps={paverMaps} color="#ffffff"/>)}<mesh position={[tx,ty,tz]}><cylinderGeometry args={[4.8,5.2,.55,8]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh><mesh position={[tx,ty,tz+5]}><cylinderGeometry args={[1.6,2.4,9.5,12]}/><meshStandardMaterial {...safetyMaps} color="#ffffff" roughness={.9}/></mesh>{Array.from({length:18},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.31)%.88)),y=frame.minY+frame.height*(.06+((i*.57)%.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.62} conifer/>})}</group>;
    }
    const rockX=cx+frame.width*.08,rockY=cy+frame.height*.06;
    return <group>
      {[[-2.1,-.8,3.0,2.5,3.8],[1.8,-.5,2.7,2.2,4.6],[0,1.5,3.3,2.6,5.2]].map(([ox,oy,sx,sy,sz],i)=><mesh key={i} position={[rockX+ox,rockY+oy,base+sz*.62]} scale={[sx,sy,sz]} rotation={[.1*i,.08*i,.55*i]}><dodecahedronGeometry args={[1,1]}/><meshStandardMaterial {...safetyMaps} color="#ffffff" roughness={.99}/></mesh>)}
      <mesh position={[rockX,rockY,base+7.9]}><cylinderGeometry args={[3.5,4.1,.7,16]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh>
      {Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <mesh key={i} position={[rockX+Math.cos(a)*2.65,rockY+Math.sin(a)*2.65,base+10.15]}><cylinderGeometry args={[.15,.18,4.4,10]}/><meshStandardMaterial color="#e1dccb"/></mesh>})}
      <mesh position={[rockX,rockY,base+12.45]}><coneGeometry args={[4.0,1.8,8]}/><meshStandardMaterial {...paverMaps} color="#ffffff"/></mesh>
      <Segment from={{x:frame.minX+frame.width*.22,y:frame.minY+frame.height*.46}} to={{x:rockX,y:rockY}} width={2.1} height={.25} z={base+5.0} maps={safetyMaps} color="#ffffff"/>
      <mesh position={[frame.minX+frame.width*.24,frame.minY+frame.height*.23,base+.12]} scale={[frame.width*.14,frame.height*.10,1]}><cylinderGeometry args={[1,1,.16,36]}/><meshPhysicalMaterial color="#507b80" transparent opacity={.8}/></mesh>
    </group>;
  }

  if (familyId === 'park_hilltop_viewpoint_v3') {
    const trail=guides.find((g)=>g.kind==='polyline');const points=trail?route(trail,frame):[];const decks=guides.filter((g)=>g.kind==='rectangle');
    return <group>{points.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={points[i+1]} width={2.8} height={.20} z={Math.max(terrainZ(p.x,p.y),terrainZ(points[i+1].x,points[i+1].y))+lift+.12} maps={paverMaps} color="#a49375" />)}{decks.map((deck,i)=>{const c=center(deck,frame);const s=resolveParkGuideDimensionsM(deck,frame);const z=terrainZ(c.x,c.y)+lift+i*.35;return <group key={i}><mesh position={[c.x,c.y,z+.34]}><boxGeometry args={[s.width,s.height,.68]} /><meshStandardMaterial {...safetyMaps} color="#918c84" roughness={.9} /></mesh><Segment from={{x:c.x-s.width/2,y:c.y+s.height/2}} to={{x:c.x+s.width/2,y:c.y+s.height/2}} width={.10} height={1.1} z={z+.68} color="#5e625f" /></group>})}{Array.from({length:Math.min(24,Math.max(8,Math.floor(frame.width*frame.height/1000)))},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.283)%0.88));const y=frame.minY+frame.height*(.06+((i*.527)%0.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.68+(i%3)*.08} conifer/>})}</group>;
  }
  return null;
}
