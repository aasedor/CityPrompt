import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

export interface Batch10ProgramFrame { minX: number; maxX: number; minY: number; maxY: number; width: number; height: number }
interface Point { x: number; y: number }
type Batch10FamilyId = Extract<ParkLegoFamilyId,
  | 'park_amsterdam_hofje_garden_v0' | 'park_amsterdam_plein_v0'
  | 'park_amsterdam_vondelpark_pavilion_v3' | 'park_barcelona_pati_green_v0'
  | 'park_barcelona_xamfra_corner_v2' | 'park_barcelona_superilla_green_v1'
  | 'park_calgary_prairie_market_v1' | 'park_calgary_princes_island_festival_v0'
  | 'park_montreal_mount_royal_grove_v2' | 'park_montreal_neighbourhood_square_v3'>;

const SKIN_SLUG: Record<Batch10FamilyId, string> = {
  park_amsterdam_hofje_garden_v0: 'amsterdam-hofje-garden-v0',
  park_amsterdam_plein_v0: 'amsterdam-brick-plein-v0',
  park_amsterdam_vondelpark_pavilion_v3: 'amsterdam-vondelpark-pavilion-v3',
  park_barcelona_pati_green_v0: 'barcelona-pati-green-v0',
  park_barcelona_xamfra_corner_v2: 'barcelona-xamfra-corner-v2',
  park_barcelona_superilla_green_v1: 'barcelona-superilla-green-v1',
  park_calgary_prairie_market_v1: 'calgary-prairie-market-v1',
  park_calgary_princes_island_festival_v0: 'calgary-princes-island-festival-v0',
  park_montreal_mount_royal_grove_v2: 'montreal-mount-royal-grove-v2',
  park_montreal_neighbourhood_square_v3: 'montreal-neighbourhood-square-v3',
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

function center(guide: ParkGroundGuide, frame: Batch10ProgramFrame): Point {
  return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y };
}
function route(guide: ParkGroundGuide, frame: Batch10ProgramFrame): Point[] {
  if (guide.points && guide.points.length > 1) return guide.points.map(([x, y]) => ({ x: frame.minX + frame.width * x, y: frame.maxY - frame.height * y }));
  const c = center(guide, frame); const length = guide.widthM ?? guide.heightM ?? Math.max(guide.width * frame.width, guide.height * frame.height);
  const angle = ((guide.rotationDeg ?? (guide.kind === 'axis' ? 90 : 0)) * Math.PI) / 180;
  return [{ x: c.x - Math.cos(angle) * length / 2, y: c.y - Math.sin(angle) * length / 2 }, { x: c.x + Math.cos(angle) * length / 2, y: c.y + Math.sin(angle) * length / 2 }];
}
function Segment({ from, to, width, height, z, maps, color }: { from: Point; to: Point; width: number; height: number; z: number; maps?: MaterialMaps; color: string }) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return <mesh position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]} rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]} renderOrder={147}>
    <boxGeometry args={[length, width, height]} /><meshStandardMaterial {...maps} color={color} roughness={0.9} metalness={0.02} />
  </mesh>;
}
function Tree({ x, y, z, scale = 1, autumn = false }: { x: number; y: number; z: number; scale?: number; autumn?: boolean }) {
  return <group position={[x, y, z]} scale={scale}>
    <mesh position={[0, 0, 1.8]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.16, 0.24, 3.6, 8]} /><meshStandardMaterial color="#594638" roughness={0.98} /></mesh>
    <mesh position={[0, 0, 4.25]} scale={[1.45, 1.3, 1.0]}><dodecahedronGeometry args={[1.65, 1]} /><meshStandardMaterial color={autumn ? '#8d603b' : '#4f7049'} roughness={0.99} /></mesh>
  </group>;
}
function Bench({ x, y, z, rotation = 0, maps }: { x: number; y: number; z: number; rotation?: number; maps: MaterialMaps }) {
  return <group position={[x, y, z]} rotation={[0, 0, rotation]}><mesh position={[0,0,.55]}><boxGeometry args={[2,.58,.14]} /><meshStandardMaterial {...maps} color="#795d43" roughness={.94} /></mesh>{[-.7,.7].map((side)=><mesh key={side} position={[side,0,.27]}><boxGeometry args={[.12,.48,.54]} /><meshStandardMaterial color="#333735" metalness={.5} roughness={.55} /></mesh>)}</group>;
}
function Planter({ x, y, z, maps, width = 2.6, depth = 1.2 }: { x: number; y: number; z: number; maps: MaterialMaps; width?: number; depth?: number }) {
  return <group position={[x,y,z]}><mesh position={[0,0,.34]}><boxGeometry args={[width,depth,.68]} /><meshStandardMaterial {...maps} color="#786d5f" roughness={.92} /></mesh>{[-.28,0,.28].map((offset)=><mesh key={offset} position={[offset*width,0,.95]}><sphereGeometry args={[Math.min(.5,depth*.34),9,6]} /><meshStandardMaterial color="#55704a" roughness={.99} /></mesh>)}</group>;
}
function Canopy({ x, y, z, timberMaps, width = 5, depth = 3.4 }: { x: number; y: number; z: number; timberMaps: MaterialMaps; width?: number; depth?: number }) {
  return <group position={[x,y,z]}>{[-1,1].flatMap((sx)=>[-1,1].map((sy)=><mesh key={`${sx}-${sy}`} position={[sx*width*.42,sy*depth*.40,1.6]}><boxGeometry args={[.16,.16,3.2]} /><meshStandardMaterial {...timberMaps} color="#76573e" roughness={.92} /></mesh>))}<mesh position={[0,0,3.22]}><boxGeometry args={[width,depth,.22]} /><meshStandardMaterial {...timberMaps} color="#8a6849" roughness={.90} /></mesh></group>;
}

export function GlobeParkBatch10Assembly({ familyId, guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; guides: ParkGroundGuide[]; frame: Batch10ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const slug = SKIN_SLUG[familyId as Batch10FamilyId];
  const paver = useRoleMaps(slug, 'paver'); const lawn = useRoleMaps(slug, 'lawn', 5); const planting = useRoleMaps(slug, 'planting', 5); const safety = useRoleMaps(slug, 'safety'); const timber = useRoleMaps(slug, 'timber');
  const cx=frame.minX+frame.width/2, cy=frame.minY+frame.height/2, base=terrainZ(cx,cy)+lift;

  if (familyId === 'park_amsterdam_hofje_garden_v0') {
    return <group><mesh position={[cx,cy,base+.14]}><boxGeometry args={[frame.width*.86,frame.height*.82,.28]} /><meshStandardMaterial {...paver} color="#a8997e" roughness={.94} /></mesh>{guides.filter((g)=>g.kind==='rectangle').map((g,i)=>{const c=center(g,frame);const s=resolveParkGuideDimensionsM(g,frame);return <mesh key={i} position={[c.x,c.y,terrainZ(c.x,c.y)+lift+.27]}><boxGeometry args={[s.width,s.height,.54]} /><meshStandardMaterial {...planting} color="#566a45" roughness={.98} /></mesh>})}<group position={[cx,cy,base]}><mesh position={[0,0,.58]}><cylinderGeometry args={[1.0,1.2,1.16,18]} /><meshStandardMaterial {...paver} color="#8f8372" roughness={.96} /></mesh><mesh position={[0,0,1.28]}><cylinderGeometry args={[.12,.16,1.4,10]} /><meshStandardMaterial color="#4a514e" metalness={.55} roughness={.54} /></mesh></group>{[-.30,.30].map((o)=><Tree key={o} x={cx+frame.width*o} y={cy-frame.height*.25} z={terrainZ(cx+frame.width*o,cy-frame.height*.25)+lift} scale={.65}/>)}</group>;
  }
  if (familyId === 'park_amsterdam_plein_v0') {
    const bays=Math.min(6,Math.max(2,Math.floor(frame.width/16)));
    return <group><mesh position={[cx,cy,base+.12]}><boxGeometry args={[frame.width*.94,frame.height*.90,.24]} /><meshStandardMaterial {...paver} color="#9c8a72" roughness={.94} /></mesh>{Array.from({length:bays},(_,i)=>{const x=frame.minX+frame.width*(.12+(i+.5)*.76/bays),y=frame.maxY-frame.height*.18,z=terrainZ(x,y)+lift;return <group key={i}><Canopy x={x} y={y} z={z} timberMaps={timber} width={Math.min(5,frame.width*.10)} depth={3}/><mesh position={[x,y,z+.85]}><boxGeometry args={[2.1,1.1,1.7]} /><meshStandardMaterial {...timber} color="#826044" roughness={.9} /></mesh></group>})}{Array.from({length:Math.min(8,bays+2)},(_,i)=>{const x=frame.minX+frame.width*(.10+(i+.5)*.80/Math.min(8,bays+2)),y=frame.minY+frame.height*.15;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.64}/>})}</group>;
  }
  if (familyId === 'park_amsterdam_vondelpark_pavilion_v3') {
    const ellipses=guides.filter((g)=>g.kind==='ellipse');const pond=ellipses[0],meadow=ellipses[1];const path=guides.find((g)=>g.kind==='polyline');const pts=path?route(path,frame):[];const px=frame.maxX-frame.width*.22,py=frame.maxY-frame.height*.22,pz=terrainZ(px,py)+lift;
    return <group>{meadow&&(()=>{const c=center(meadow,frame),s=resolveParkGuideDimensionsM(meadow,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.08]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.16,32]} /><meshStandardMaterial {...lawn} color="#6d8a52" roughness={.96} /></mesh>})()}{pond&&(()=>{const c=center(pond,frame),s=resolveParkGuideDimensionsM(pond,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.1]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.2,32]} /><meshPhysicalMaterial color="#557f83" transparent opacity={.78} roughness={.14} /></mesh>})()}{pts.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={pts[i+1]} width={3} height={.16} z={Math.max(terrainZ(p.x,p.y),terrainZ(pts[i+1].x,pts[i+1].y))+lift+.08} maps={paver} color="#9e927b" />)}<Canopy x={px} y={py} z={pz} timberMaps={timber} width={7} depth={5}/>{Array.from({length:Math.min(24,Math.max(10,Math.floor(frame.width*frame.height/1400)))},(_,i)=>{const x=frame.minX+frame.width*(.05+((i*.337)%0.9)),y=frame.minY+frame.height*(.05+((i*.611)%0.9));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.72+(i%3)*.08}/>})}</group>;
  }
  if (familyId === 'park_barcelona_pati_green_v0') {
    const fountain=guides.find((g)=>g.kind==='ellipse');
    return <group>{guides.filter((g)=>g.kind==='rectangle').map((g,i)=>{const c=center(g,frame),s=resolveParkGuideDimensionsM(g,frame),z=terrainZ(c.x,c.y)+lift;return <mesh key={i} position={[c.x,c.y,z+.22]}><boxGeometry args={[s.width,s.height,.44]} /><meshStandardMaterial {...planting} color="#5f704a" roughness={.98} /></mesh>})}{fountain&&(()=>{const c=center(fountain,frame),s=resolveParkGuideDimensionsM(fountain,frame),z=terrainZ(c.x,c.y)+lift;return <group><mesh position={[c.x,c.y,z+.22]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.44,24]} /><meshStandardMaterial {...paver} color="#978d7c" roughness={.92} /></mesh><mesh position={[c.x,c.y,z+.46]} scale={[s.width*.34,s.height*.34,1]}><cylinderGeometry args={[1,1,.16,24]} /><meshPhysicalMaterial color="#5c8d91" transparent opacity={.78} roughness={.12} /></mesh></group>})()}{Array.from({length:6},(_,i)=>{const a=i*Math.PI/3,x=cx+Math.cos(a)*frame.width*.34,y=cy+Math.sin(a)*frame.height*.31;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={i%2?.68:.82}/>})}</group>;
  }
  if (familyId === 'park_barcelona_xamfra_corner_v2') {
    const radius=Math.min(frame.width,frame.height)*.27;
    return <group><mesh position={[cx,cy,base+.14]} rotation={[0,0,Math.PI/8]}><cylinderGeometry args={[radius,radius,.28,8]} /><meshStandardMaterial {...paver} color="#aaa095" roughness={.9} /></mesh><Tree x={cx} y={cy} z={base+.28} scale={.82}/>{Array.from({length:Math.min(10,Math.max(4,Math.floor((frame.width+frame.height)/10)))},(_,i)=>{const a=i*Math.PI*2/Math.min(10,Math.max(4,Math.floor((frame.width+frame.height)/10))),x=cx+Math.cos(a)*radius*.74,y=cy+Math.sin(a)*radius*.74,z=terrainZ(x,y)+lift;return <group key={i}><mesh position={[x,y,z+.76]}><cylinderGeometry args={[.52,.52,.10,18]} /><meshStandardMaterial {...timber} color="#80624a" roughness={.92} /></mesh><mesh position={[x,y,z+.37]}><cylinderGeometry args={[.06,.08,.72,8]} /><meshStandardMaterial color="#383c3a" metalness={.5} roughness={.5} /></mesh></group>})}</group>;
  }
  if (familyId === 'park_barcelona_superilla_green_v1') {
    const cells=guides.filter((g)=>g.kind==='rectangle');
    return <group>{cells.map((g,i)=>{const c=center(g,frame),s=resolveParkGuideDimensionsM(g,frame),z=terrainZ(c.x,c.y)+lift;return <group key={i}><mesh position={[c.x,c.y,z+.13]} rotation={[0,0,(g.rotationDeg??0)*Math.PI/180]}><boxGeometry args={[s.width,s.height,.26]} /><meshStandardMaterial {...safety} color={['#c1a34e','#71927a','#668b9c','#b36f57'][i%4]} roughness={.9} /></mesh>{i%2===0&&<Planter x={c.x} y={c.y} z={z+.26} maps={paver} width={Math.min(4,s.width*.34)} depth={Math.min(1.5,s.height*.28)}/>}</group>})}{Array.from({length:Math.min(16,Math.max(6,Math.floor(frame.width/14)))},(_,i)=>{const x=frame.minX+frame.width*(.08+((i*.291)%0.84)),y=frame.minY+frame.height*(.08+((i*.537)%0.84));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.62}/>})}</group>;
  }
  if (familyId === 'park_calgary_prairie_market_v1') {
    const pool=guides.find((g)=>g.kind==='rectangle'&&g.color==='#668c91');const stalls=Math.min(8,Math.max(2,Math.floor(frame.width/12)));
    return <group>{pool&&(()=>{const c=center(pool,frame),s=resolveParkGuideDimensionsM(pool,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.10]}><boxGeometry args={[s.width,s.height,.20]} /><meshPhysicalMaterial color="#668c91" transparent opacity={.78} roughness={.12} /></mesh>})()}{Array.from({length:stalls},(_,i)=>{const x=frame.minX+frame.width*(.10+(i+.5)*.80/stalls),y=frame.maxY-frame.height*.18,z=terrainZ(x,y)+lift;return <Canopy key={i} x={x} y={y} z={z} timberMaps={timber} width={Math.min(4.8,frame.width*.11)} depth={3.2}/>})}{Array.from({length:Math.min(8,stalls)},(_,i)=>{const x=frame.minX+frame.width*(.12+(i+.5)*.76/Math.min(8,stalls));return <Planter key={i} x={x} y={frame.minY+frame.height*.15} z={terrainZ(x,frame.minY+frame.height*.15)+lift} maps={paver} width={3} depth={1.4}/>})}</group>;
  }
  if (familyId === 'park_calgary_princes_island_festival_v0') {
    const wetland=guides.find((g)=>g.kind==='ellipse');const boardwalk=guides.find((g)=>g.kind==='polyline');const pts=boardwalk?route(boardwalk,frame):[];const sx=frame.minX+frame.width*.28,sy=frame.minY+frame.height*.28,sz=terrainZ(sx,sy)+lift;
    return <group>{wetland&&(()=>{const c=center(wetland,frame),s=resolveParkGuideDimensionsM(wetland,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.08]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.16,32]} /><meshPhysicalMaterial color="#597f7b" transparent opacity={.72} roughness={.2} /></mesh>})()}{pts.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={pts[i+1]} width={2.5} height={.28} z={Math.max(terrainZ(p.x,p.y),terrainZ(pts[i+1].x,pts[i+1].y))+lift+.32} maps={timber} color="#816347" />)}<Canopy x={sx} y={sy} z={sz} timberMaps={timber} width={8} depth={5.5}/>{Array.from({length:Math.min(22,Math.max(8,Math.floor(frame.width*frame.height/1600)))},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.319)%0.88)),y=frame.minY+frame.height*(.06+((i*.587)%0.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.7+(i%3)*.08}/>})}</group>;
  }
  if (familyId === 'park_montreal_mount_royal_grove_v2') {
    const trail=guides.find((g)=>g.kind==='polyline');const pts=trail?route(trail,frame):[];const deck=guides.find((g)=>g.kind==='rectangle');
    return <group>{pts.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={pts[i+1]} width={3.2} height={.18} z={Math.max(terrainZ(p.x,p.y),terrainZ(pts[i+1].x,pts[i+1].y))+lift+.10} maps={paver} color="#a09178" />)}{deck&&(()=>{const c=center(deck,frame),s=resolveParkGuideDimensionsM(deck,frame),z=terrainZ(c.x,c.y)+lift;return <group><mesh position={[c.x,c.y,z+.42]}><boxGeometry args={[s.width,s.height,.84]} /><meshStandardMaterial {...safety} color="#8f8b83" roughness={.94} /></mesh><Segment from={{x:c.x-s.width*.45,y:c.y+s.height*.42}} to={{x:c.x+s.width*.45,y:c.y+s.height*.42}} width={.14} height={1.1} z={z+.84} color="#4c504d" /></group>})()}{Array.from({length:Math.min(32,Math.max(12,Math.floor(frame.width*frame.height/2400)))},(_,i)=>{const x=frame.minX+frame.width*(.04+((i*.277)%0.92)),y=frame.minY+frame.height*(.04+((i*.523)%0.92));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.72+(i%4)*.08} autumn={i%5===0}/>})}</group>;
  }
  if (familyId === 'park_montreal_neighbourhood_square_v3') {
    const fountain=guides.find((g)=>g.kind==='ellipse');const railZ=base+.15;const inset=1.0;
    return <group>{fountain&&(()=>{const c=center(fountain,frame),s=resolveParkGuideDimensionsM(fountain,frame),z=terrainZ(c.x,c.y)+lift;return <group><mesh position={[c.x,c.y,z+.30]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.60,24]} /><meshStandardMaterial {...paver} color="#91877a" roughness={.92} /></mesh><mesh position={[c.x,c.y,z+.66]}><cylinderGeometry args={[.15,.22,.72,12]} /><meshStandardMaterial color="#77736b" roughness={.9} /></mesh></group>})()}{[[{x:frame.minX+inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.minY+inset}],[{x:frame.maxX-inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.maxY-inset}],[{x:frame.maxX-inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.maxY-inset}],[{x:frame.minX+inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.minY+inset}]].map(([from,to],i)=><Segment key={i} from={from} to={to} width={.09} height={.9} z={railZ} color="#303532" />)}{Array.from({length:8},(_,i)=>{const a=i*Math.PI/4,x=cx+Math.cos(a)*frame.width*.34,y=cy+Math.sin(a)*frame.height*.30,z=terrainZ(x,y)+lift;return <group key={i}><Tree x={x} y={y} z={z} scale={.66}/><Bench x={x-Math.sin(a)*1.8} y={y+Math.cos(a)*1.8} z={z} rotation={a+Math.PI/2} maps={timber}/></group>})}</group>;
  }
  return null;
}
