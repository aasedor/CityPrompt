import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { batch24ParkSkinForSelection } from './parkBatch24Skins';

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

export function GlobeParkBatch10Assembly({ familyId, archetypeId, variantId, guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; archetypeId?: string; variantId?: string; guides: ParkGroundGuide[]; frame: Batch10ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const variantSkin = batch24ParkSkinForSelection(archetypeId ?? '', variantId ?? '') ?? batch23ParkSkinForSelection(archetypeId ?? '', variantId ?? ''); const slug = variantSkin?.slug ?? SKIN_SLUG[familyId as Batch10FamilyId];
  const paver = useRoleMaps(slug, 'paver'); const lawn = useRoleMaps(slug, 'lawn', 5); const planting = useRoleMaps(slug, 'planting', 5); const safety = useRoleMaps(slug, 'safety'); const timber = useRoleMaps(slug, 'timber');
  const cx=frame.minX+frame.width/2, cy=frame.minY+frame.height/2, base=terrainZ(cx,cy)+lift;

  if (familyId === 'park_amsterdam_hofje_garden_v0' && variantId && variantId !== 'amsterdam_hofje_garden_v0') {
    const historic = variantId === 'amsterdam_hofje_garden_v3';
    const lush = variantId === 'amsterdam_hofje_garden_v1';
    const bedCount = lush ? 8 : historic ? 4 : 5;
    return <group>
      <mesh position={[cx,cy,base+.1]}><boxGeometry args={[frame.width*.88,frame.height*.84,.2]}/><meshStandardMaterial {...(historic?lawn:paver)} color="#ffffff" roughness={.94}/></mesh>
      <Segment from={{x:frame.minX+frame.width*.10,y:cy}} to={{x:frame.maxX-frame.width*.10,y:cy}} width={2.2} height={.16} z={base+.20} maps={paver} color="#ffffff"/>
      <Segment from={{x:cx,y:frame.minY+frame.height*.10}} to={{x:cx,y:frame.maxY-frame.height*.10}} width={2.2} height={.16} z={base+.20} maps={paver} color="#ffffff"/>
      {Array.from({length:bedCount},(_,i)=>{const a=i*Math.PI*2/bedCount,x=cx+Math.cos(a)*frame.width*(historic?.27:.30),y=cy+Math.sin(a)*frame.height*(historic?.25:.29),z=terrainZ(x,y)+lift;return <group key={i}><mesh position={[x,y,z+.28]} scale={[lush?1.25:1,1,1]}><boxGeometry args={[Math.min(5,frame.width*.15),Math.min(3,frame.height*.12),.56]}/><meshStandardMaterial {...planting} color="#ffffff" roughness={.98}/></mesh>{(lush||i%2===0)&&<Tree x={x} y={y} z={z+.56} scale={lush?.62:.52}/>}</group>})}
      {historic&&[-1,1].map((s)=><Bench key={s} x={cx+s*frame.width*.18} y={cy+frame.height*.18} z={base+.3} rotation={0} maps={timber}/>) }
    </group>;
  }
  if (familyId === 'park_amsterdam_plein_v0' && variantId && variantId !== 'amsterdam_plein_v0') {
    const glass = variantId === 'amsterdam_plein_v1';
    const cafe = variantId === 'amsterdam_plein_v2';
    const tableCount = cafe ? Math.min(10,Math.max(4,Math.floor(frame.width/6))) : glass ? 4 : 2;
    return <group>
      <mesh position={[cx,cy,base+.12]}><boxGeometry args={[frame.width*.94,frame.height*.90,.24]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {glass&&<group position={[cx,cy+frame.height*.12,base]}>{[-1,1].flatMap(sx=>[-1,1].map(sy=><mesh key={`${sx}-${sy}`} position={[sx*frame.width*.20,sy*frame.height*.13,1.6]}><boxGeometry args={[.15,.15,3.2]}/><meshStandardMaterial color="#454b49" metalness={.55} roughness={.45}/></mesh>))}<mesh position={[0,0,3.25]}><boxGeometry args={[frame.width*.44,frame.height*.30,.16]}/><meshPhysicalMaterial color="#b7cfcc" transparent opacity={.48} roughness={.16}/></mesh></group>}
      {Array.from({length:tableCount},(_,i)=>{const cols=Math.ceil(tableCount/2),x=frame.minX+frame.width*(.18+(i%cols)*.64/Math.max(1,cols-1)),y=cy+(Math.floor(i/cols)-.5)*frame.height*.28,z=terrainZ(x,y)+lift;return <group key={i}><mesh position={[x,y,z+.75]}><cylinderGeometry args={[.55,.55,.10,18]}/><meshStandardMaterial {...timber} color="#ffffff"/></mesh><mesh position={[x,y,z+.38]}><cylinderGeometry args={[.06,.08,.72,8]}/><meshStandardMaterial color="#363b39" metalness={.5}/></mesh></group>})}
      {Array.from({length:glass?4:6},(_,i)=>{const x=frame.minX+frame.width*(.12+i*.76/Math.max(1,(glass?3:5))),y=frame.minY+frame.height*.12;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.58}/>})}
    </group>;
  }
  if (familyId === 'park_amsterdam_vondelpark_pavilion_v3' && variantId && variantId !== 'amsterdam_vondelpark_v3') {
    const cafe = variantId === 'amsterdam_vondelpark_v1';
    const planted = variantId === 'amsterdam_vondelpark_v2';
    const treeCount = planted ? 16 : 10;
    return <group>
      <mesh position={[cx,cy,base+.10]} scale={[frame.width*.40,frame.height*.38,1]}><cylinderGeometry args={[1,1,.20,36]}/><meshStandardMaterial {...lawn} color="#ffffff" roughness={.98}/></mesh>
      <Segment from={{x:frame.minX+frame.width*.08,y:frame.minY+frame.height*.28}} to={{x:frame.maxX-frame.width*.08,y:frame.maxY-frame.height*.30}} width={3} height={.18} z={base+.20} maps={paver} color="#ffffff"/>
      {cafe&&<Canopy x={frame.maxX-frame.width*.24} y={frame.maxY-frame.height*.23} z={terrainZ(frame.maxX-frame.width*.24,frame.maxY-frame.height*.23)+lift} timberMaps={timber} width={6} depth={4}/>}
      {planted&&Array.from({length:5},(_,i)=>{const a=i*Math.PI*2/5,x=frame.minX+frame.width*.72+Math.cos(a)*frame.width*.12,y=frame.minY+frame.height*.30+Math.sin(a)*frame.height*.12;return <Planter key={i} x={x} y={y} z={terrainZ(x,y)+lift} maps={paver} width={3.2} depth={1.3}/>})}
      {Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.337)%.88)),y=frame.minY+frame.height*(.06+((i*.611)%.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.64+(i%3)*.07}/>})}
    </group>;
  }
  if (familyId === 'park_barcelona_pati_green_v0' && variantId && variantId !== 'barcelona_pati_interior_v0') {
    const lawnCourt = variantId === 'barcelona_pati_interior_v1';
    const shadeCourt = variantId === 'barcelona_pati_interior_v3';
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.90,frame.height*.86,.22]}/><meshStandardMaterial {...(lawnCourt?lawn:paver)} color="#ffffff" roughness={.95}/></mesh>
      {lawnCourt&&<Segment from={{x:frame.minX+frame.width*.12,y:cy}} to={{x:frame.maxX-frame.width*.12,y:cy}} width={2.4} height={.16} z={base+.22} maps={paver} color="#ffffff"/>}
      {Array.from({length:shadeCourt?6:4},(_,i)=>{const a=i*Math.PI*2/(shadeCourt?6:4),x=cx+Math.cos(a)*frame.width*.32,y=cy+Math.sin(a)*frame.height*.29,z=terrainZ(x,y)+lift;return <group key={i}><Tree x={x} y={y} z={z} scale={shadeCourt?.70:.62}/>{!lawnCourt&&<Bench x={x-Math.sin(a)*1.5} y={y+Math.cos(a)*1.5} z={z} rotation={a+Math.PI/2} maps={timber}/>}</group>})}
      {!shadeCourt&&Array.from({length:4},(_,i)=>{const x=cx+(i%2-.5)*frame.width*.42,y=cy+(Math.floor(i/2)-.5)*frame.height*.40;return <Planter key={i} x={x} y={y} z={terrainZ(x,y)+lift+.22} maps={paver} width={Math.min(4,frame.width*.16)} depth={1.4}/>})}
    </group>;
  }
  if (familyId === 'park_barcelona_xamfra_corner_v2' && variantId && variantId !== 'barcelona_placa_xamfra_v2') {
    const cafe = variantId === 'barcelona_placa_xamfra_v0';
    const active = variantId === 'barcelona_placa_xamfra_v3';
    const radius=Math.min(frame.width,frame.height)*.28;
    return <group>
      <mesh position={[cx,cy,base+.14]} rotation={[0,0,Math.PI/8]}><cylinderGeometry args={[radius,radius,.28,8]}/><meshStandardMaterial {...(active?safety:paver)} color="#ffffff" roughness={.92}/></mesh>
      <Segment from={{x:cx-radius*.8,y:cy-radius*.8}} to={{x:cx+radius*.8,y:cy+radius*.8}} width={2.8} height={.14} z={base+.28} maps={paver} color="#ffffff"/>
      {Array.from({length:cafe?7:active?4:2},(_,i)=>{const a=(i+.5)*Math.PI*2/(cafe?7:active?4:2),x=cx+Math.cos(a)*radius*.62,y=cy+Math.sin(a)*radius*.62,z=terrainZ(x,y)+lift;return cafe?<group key={i}><mesh position={[x,y,z+.72]}><cylinderGeometry args={[.52,.52,.10,18]}/><meshStandardMaterial {...timber} color="#ffffff"/></mesh><mesh position={[x,y,z+.36]}><cylinderGeometry args={[.06,.08,.68,8]}/><meshStandardMaterial color="#343936"/></mesh></group>:<Tree key={i} x={x} y={y} z={z} scale={.68}/>})}
      {active&&<Planter x={cx} y={cy-radius*.25} z={base+.28} maps={paver} width={Math.min(5,radius*.75)} depth={1.5}/>}
    </group>;
  }
  if (familyId === 'park_barcelona_superilla_green_v1' && variantId && variantId !== 'barcelona_superilla_v1') {
    const corridor = variantId === 'barcelona_superilla_v2';
    const social = variantId === 'barcelona_superilla_v3';
    return <group>
      <mesh position={[cx,cy,base+.10]}><boxGeometry args={[frame.width*.94,frame.height*.90,.20]}/><meshStandardMaterial {...(corridor?planting:paver)} color="#ffffff" roughness={.95}/></mesh>
      {corridor&&<Segment from={{x:frame.minX+frame.width*.08,y:cy}} to={{x:frame.maxX-frame.width*.08,y:cy}} width={Math.min(6,frame.height*.20)} height={.18} z={base+.20} maps={paver} color="#ffffff"/>}
      {Array.from({length:social?8:6},(_,i)=>{const x=frame.minX+frame.width*(.10+((i*.31)%.80)),y=social?frame.minY+frame.height*(.18+((i*.53)%.64)):cy+(i%2?1:-1)*frame.height*.25,z=terrainZ(x,y)+lift;return <group key={i}><Planter x={x} y={y} z={z+.20} maps={paver} width={social?3.4:2.8} depth={1.3}/>{(corridor||social)&&<Tree x={x} y={y} z={z+1.1} scale={.54}/>}</group>})}
      {social&&<Canopy x={cx} y={frame.maxY-frame.height*.22} z={terrainZ(cx,frame.maxY-frame.height*.22)+lift} timberMaps={timber} width={Math.min(7,frame.width*.24)} depth={Math.min(4,frame.height*.16)}/>}
    </group>;
  }

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
  if (familyId === 'park_calgary_prairie_market_v1' && variantId && variantId !== 'calgary_prairie_plaza_v1') {
    const art=variantId==='calgary_prairie_plaza_v2',corporate=variantId==='calgary_prairie_plaza_v3';
    const bandCount=corporate?3:6;
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.94,frame.height*.90,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {Array.from({length:bandCount},(_,i)=>{const x=frame.minX+frame.width*(.12+(i+.5)*.76/bandCount),y=cy+(i%2?1:-1)*frame.height*(corporate?.22:.25),z=terrainZ(x,y)+lift;return <group key={i}><Planter x={x} y={y} z={z+.22} maps={paver} width={Math.min(corporate?5:4,frame.width*.14)} depth={Math.min(1.8,frame.height*.08)}/>{!corporate&&<mesh position={[x,y,z+1.28]} scale={[1.5,.8,.55]}><dodecahedronGeometry args={[.8,1]}/><meshStandardMaterial {...planting} color="#ffffff" roughness={.99}/></mesh>}</group>})}
      <Segment from={{x:frame.minX+frame.width*.06,y:cy}} to={{x:frame.maxX-frame.width*.06,y:cy}} width={corporate?5:3.2} height={.14} z={base+.22} maps={paver} color="#ffffff"/>
      {art&&Array.from({length:5},(_,i)=>{const x=cx+(i-2)*Math.min(3.2,frame.width*.07);return <group key={i}><mesh position={[x,cy,base+1.05+(i%2)*.35]} rotation={[0,.2*(i-2),0]}><boxGeometry args={[.3,.3,1.8+(i%2)*.7]}/><meshStandardMaterial {...safety} color="#ffffff" metalness={.25}/></mesh></group>})}
      {Array.from({length:corporate?4:6},(_,i)=>{const x=frame.minX+frame.width*(.12+i*.76/Math.max(1,(corporate?3:5))),y=frame.minY+frame.height*(i%2?.12:.88),z=terrainZ(x,y)+lift;return <group key={i}><Tree x={x} y={y} z={z+.22} scale={.62}/><Bench x={x} y={y+(i%2?2:-2)} z={z+.22} maps={timber}/></group>})}
    </group>;
  }
  if (familyId === 'park_calgary_prairie_market_v1') {
    const pool=guides.find((g)=>g.kind==='rectangle'&&g.color==='#668c91');const stalls=Math.min(8,Math.max(2,Math.floor(frame.width/12)));
    return <group>{pool&&(()=>{const c=center(pool,frame),s=resolveParkGuideDimensionsM(pool,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.10]}><boxGeometry args={[s.width,s.height,.20]} /><meshPhysicalMaterial color="#668c91" transparent opacity={.78} roughness={.12} /></mesh>})()}{Array.from({length:stalls},(_,i)=>{const x=frame.minX+frame.width*(.10+(i+.5)*.80/stalls),y=frame.maxY-frame.height*.18,z=terrainZ(x,y)+lift;return <Canopy key={i} x={x} y={y} z={z} timberMaps={timber} width={Math.min(4.8,frame.width*.11)} depth={3.2}/>})}{Array.from({length:Math.min(8,stalls)},(_,i)=>{const x=frame.minX+frame.width*(.12+(i+.5)*.76/Math.min(8,stalls));return <Planter key={i} x={x} y={frame.minY+frame.height*.15} z={terrainZ(x,frame.minY+frame.height*.15)+lift} maps={paver} width={3} depth={1.4}/>})}</group>;
  }
  if (familyId === 'park_calgary_princes_island_festival_v0' && variantId && variantId !== 'calgary_princes_island_v0') {
    const winter=variantId==='calgary_princes_island_v2',flood=variantId==='calgary_princes_island_v3';
    const pathY=cy+(flood?.10:-.04)*frame.height;
    return <group>
      <mesh position={[cx,cy,base+.09]}><boxGeometry args={[frame.width*.94,frame.height*.90,.18]}/><meshStandardMaterial {...(flood?planting:lawn)} color="#ffffff" roughness={.98}/></mesh>
      {flood&&<mesh position={[cx,frame.minY+frame.height*.30,base+.13]}><boxGeometry args={[frame.width*.90,frame.height*.22,.26]}/><meshPhysicalMaterial color="#5c8587" transparent opacity={.78} roughness={.16}/></mesh>}
      <Segment from={{x:frame.minX+frame.width*.06,y:pathY}} to={{x:frame.maxX-frame.width*.06,y:pathY}} width={flood?3.2:3.8} height={flood?.34:.18} z={base+(flood?.28:.18)} maps={flood?timber:paver} color="#ffffff"/>
      {winter&&<Canopy x={frame.maxX-frame.width*.24} y={frame.maxY-frame.height*.24} z={terrainZ(frame.maxX-frame.width*.24,frame.maxY-frame.height*.24)+lift+.18} timberMaps={timber} width={Math.min(8,frame.width*.24)} depth={Math.min(5,frame.height*.18)}/>}
      {Array.from({length:flood?12:16},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.337)%.88)),y=frame.minY+frame.height*(.08+((i*.611)%.84));if(Math.abs(y-pathY)<4)return null;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift+.18} scale={.68+(i%3)*.08} autumn={!winter&&!flood}/>})}
      {Array.from({length:4},(_,i)=>{const x=frame.minX+frame.width*(.18+i*.64/3),z=terrainZ(x,pathY)+lift;return <Bench key={i} x={x} y={pathY+(i%2?2.5:-2.5)} z={z+.2} rotation={i%2?0:Math.PI} maps={timber}/>})}
    </group>;
  }
  if (familyId === 'park_calgary_princes_island_festival_v0') {
    const wetland=guides.find((g)=>g.kind==='ellipse');const boardwalk=guides.find((g)=>g.kind==='polyline');const pts=boardwalk?route(boardwalk,frame):[];const sx=frame.minX+frame.width*.28,sy=frame.minY+frame.height*.28,sz=terrainZ(sx,sy)+lift;
    return <group>{wetland&&(()=>{const c=center(wetland,frame),s=resolveParkGuideDimensionsM(wetland,frame),z=terrainZ(c.x,c.y)+lift;return <mesh position={[c.x,c.y,z+.08]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.16,32]} /><meshPhysicalMaterial color="#597f7b" transparent opacity={.72} roughness={.2} /></mesh>})()}{pts.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={pts[i+1]} width={2.5} height={.28} z={Math.max(terrainZ(p.x,p.y),terrainZ(pts[i+1].x,pts[i+1].y))+lift+.32} maps={timber} color="#816347" />)}<Canopy x={sx} y={sy} z={sz} timberMaps={timber} width={8} depth={5.5}/>{Array.from({length:Math.min(22,Math.max(8,Math.floor(frame.width*frame.height/1600)))},(_,i)=>{const x=frame.minX+frame.width*(.06+((i*.319)%0.88)),y=frame.minY+frame.height*(.06+((i*.587)%0.88));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.7+(i%3)*.08}/>})}</group>;
  }
  if (familyId === 'park_montreal_mount_royal_grove_v2' && variantId && variantId !== 'montreal_mount_royal_v2') {
    const lawnGrove=variantId==='montreal_mount_royal_v1',hillside=variantId==='montreal_mount_royal_v3';
    const trail=<Segment from={{x:frame.minX+frame.width*.08,y:frame.minY+frame.height*.25}} to={{x:frame.maxX-frame.width*.08,y:frame.maxY-frame.height*.24}} width={3.2} height={.18} z={base+.22} maps={paver} color="#ffffff"/>;
    return <group>
      <mesh position={[cx,cy,base+.10]}><boxGeometry args={[frame.width*.94,frame.height*.90,.20]}/><meshStandardMaterial {...(lawnGrove?lawn:planting)} color="#ffffff" roughness={.98}/></mesh>
      {trail}
      {hillside&&Array.from({length:4},(_,i)=>{const y=frame.minY+frame.height*(.20+i*.18),z=terrainZ(cx,y)+lift;return <mesh key={i} position={[cx,y,z+.28+i*.08]}><boxGeometry args={[frame.width*(.68-i*.05),2.0,.56+i*.16]}/><meshStandardMaterial {...(i%2?planting:paver)} color="#ffffff" roughness={.96}/></mesh>})}
      {!lawnGrove&&<group><mesh position={[frame.maxX-frame.width*.22,frame.maxY-frame.height*.20,base+.46]}><boxGeometry args={[Math.min(10,frame.width*.28),Math.min(5,frame.height*.16),.92]}/><meshStandardMaterial {...paver} color="#ffffff"/></mesh><Segment from={{x:frame.maxX-frame.width*.36,y:frame.maxY-frame.height*.14}} to={{x:frame.maxX-frame.width*.08,y:frame.maxY-frame.height*.14}} width={.12} height={1.1} z={base+.9} color="#414745"/></group>}
      {Array.from({length:lawnGrove?14:20},(_,i)=>{const x=frame.minX+frame.width*(.05+((i*.277)%.90)),y=frame.minY+frame.height*(.05+((i*.523)%.90));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift+.2} scale={.68+(i%4)*.08} autumn={hillside&&i%4===0}/>})}
      {[-1,1].map((s)=><Bench key={s} x={cx+s*frame.width*.22} y={cy+s*frame.height*.10} z={terrainZ(cx+s*frame.width*.22,cy+s*frame.height*.10)+lift+.2} rotation={Math.PI/4} maps={timber}/>) }
    </group>;
  }
  if (familyId === 'park_montreal_mount_royal_grove_v2') {
    const trail=guides.find((g)=>g.kind==='polyline');const pts=trail?route(trail,frame):[];const deck=guides.find((g)=>g.kind==='rectangle');
    return <group>{pts.slice(0,-1).map((p,i)=><Segment key={i} from={p} to={pts[i+1]} width={3.2} height={.18} z={Math.max(terrainZ(p.x,p.y),terrainZ(pts[i+1].x,pts[i+1].y))+lift+.10} maps={paver} color="#a09178" />)}{deck&&(()=>{const c=center(deck,frame),s=resolveParkGuideDimensionsM(deck,frame),z=terrainZ(c.x,c.y)+lift;return <group><mesh position={[c.x,c.y,z+.42]}><boxGeometry args={[s.width,s.height,.84]} /><meshStandardMaterial {...safety} color="#8f8b83" roughness={.94} /></mesh><Segment from={{x:c.x-s.width*.45,y:c.y+s.height*.42}} to={{x:c.x+s.width*.45,y:c.y+s.height*.42}} width={.14} height={1.1} z={z+.84} color="#4c504d" /></group>})()}{Array.from({length:Math.min(32,Math.max(12,Math.floor(frame.width*frame.height/2400)))},(_,i)=>{const x=frame.minX+frame.width*(.04+((i*.277)%0.92)),y=frame.minY+frame.height*(.04+((i*.523)%0.92));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.72+(i%4)*.08} autumn={i%5===0}/>})}</group>;
  }
  if (familyId === 'park_montreal_neighbourhood_square_v3' && variantId && variantId !== 'montreal_square_v3') {
    const linear=variantId==='montreal_square_v1',pocket=variantId==='montreal_square_v2';
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.94,frame.height*.90,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {variantId==='montreal_square_v0'&&<group><mesh position={[cx,cy,base+.27]}><cylinderGeometry args={[Math.min(3.2,frame.width*.10),Math.min(3.2,frame.width*.10),.32,24]}/><meshStandardMaterial {...safety} color="#ffffff"/></mesh><mesh position={[cx,cy,base+.72]}><cylinderGeometry args={[.12,.18,.9,10]}/><meshStandardMaterial color="#696e6a"/></mesh></group>}
      {Array.from({length:linear?6:pocket?5:4},(_,i)=>{const x=linear?frame.minX+frame.width*(.14+i*.72/5):cx+Math.cos(i*Math.PI*2/(pocket?5:4))*frame.width*.27;const y=linear?cy+(i%2?1:-1)*frame.height*.18:cy+Math.sin(i*Math.PI*2/(pocket?5:4))*frame.height*.25;const z=terrainZ(x,y)+lift;return <group key={i}><Planter x={x} y={y} z={z+.22} maps={paver} width={linear?4:3.2} depth={1.35}/><Bench x={x} y={y+(i%2?1.8:-1.8)} z={z+.22} rotation={linear?0:i*Math.PI*2/(pocket?5:4)+Math.PI/2} maps={timber}/>{(linear||pocket)&&<Tree x={x} y={y} z={z+1.3} scale={.55}/>}</group>})}
      {pocket&&<Segment from={{x:frame.minX+frame.width*.08,y:cy}} to={{x:frame.maxX-frame.width*.08,y:cy}} width={2.6} height={.14} z={base+.22} maps={paver} color="#ffffff"/>}
    </group>;
  }
  if (familyId === 'park_montreal_neighbourhood_square_v3') {
    const fountain=guides.find((g)=>g.kind==='ellipse');const railZ=base+.15;const inset=1.0;
    return <group>{fountain&&(()=>{const c=center(fountain,frame),s=resolveParkGuideDimensionsM(fountain,frame),z=terrainZ(c.x,c.y)+lift;return <group><mesh position={[c.x,c.y,z+.30]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,.60,24]} /><meshStandardMaterial {...paver} color="#91877a" roughness={.92} /></mesh><mesh position={[c.x,c.y,z+.66]}><cylinderGeometry args={[.15,.22,.72,12]} /><meshStandardMaterial color="#77736b" roughness={.9} /></mesh></group>})()}{[[{x:frame.minX+inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.minY+inset}],[{x:frame.maxX-inset,y:frame.minY+inset},{x:frame.maxX-inset,y:frame.maxY-inset}],[{x:frame.maxX-inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.maxY-inset}],[{x:frame.minX+inset,y:frame.maxY-inset},{x:frame.minX+inset,y:frame.minY+inset}]].map(([from,to],i)=><Segment key={i} from={from} to={to} width={.09} height={.9} z={railZ} color="#303532" />)}{Array.from({length:8},(_,i)=>{const a=i*Math.PI/4,x=cx+Math.cos(a)*frame.width*.34,y=cy+Math.sin(a)*frame.height*.30,z=terrainZ(x,y)+lift;return <group key={i}><Tree x={x} y={y} z={z} scale={.66}/><Bench x={x-Math.sin(a)*1.8} y={y+Math.cos(a)*1.8} z={z} rotation={a+Math.PI/2} maps={timber}/></group>})}</group>;
  }
  return null;
}
