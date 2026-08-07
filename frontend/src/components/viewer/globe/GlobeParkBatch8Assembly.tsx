import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch25ParkSkinForSelection } from './parkBatch25Skins';
import { batch27ParkSkinForSelection } from './parkBatch27Skins';
import { PARK_MESHY_ARCHETYPE_ASSETS } from './parkMeshyArchetypeAssets';

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
function ParkKitGlb({ url, position, yaw = 0 }: {
  url: string; position: [number, number, number]; yaw?: number;
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true; mesh.receiveShadow = true; mesh.renderOrder = 149;
    });
    return next;
  }, [scene]);
  return <group position={position} rotation={[0, 0, yaw]}><group rotation={[Math.PI / 2, 0, 0]}><primitive object={clone} /></group></group>;
}
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
function ParkPavilion({ x, y, z, width, depth, maps, glass = false }: { x: number; y: number; z: number; width: number; depth: number; maps: MaterialMaps; glass?: boolean }) {
  return <group position={[x,y,z]}>
    {[-1,1].flatMap((sx)=>[-1,1].map((sy)=><mesh key={`${sx}-${sy}`} position={[sx*width*.42,sy*depth*.40,1.55]}><boxGeometry args={[.18,.18,3.1]}/><meshStandardMaterial {...maps} color={glass?'#5d6665':'#795a41'} roughness={.74}/></mesh>))}
    {glass&&<mesh position={[0,0,1.65]}><boxGeometry args={[width*.82,depth*.72,2.7]}/><meshPhysicalMaterial color="#b9d0cc" transparent opacity={.34} roughness={.16}/></mesh>}
    <mesh position={[0,0,3.22]}><boxGeometry args={[width,depth,.28]}/><meshStandardMaterial {...maps} color={glass?'#89928e':'#76573e'} roughness={.84}/></mesh>
  </group>;
}
function Pergola({ x, y, z, width, depth, maps }: { x: number; y: number; z: number; width: number; depth: number; maps: MaterialMaps }) {
  return <group position={[x,y,z]}>
    {[-1,1].flatMap((sx)=>[-1,1].map((sy)=><mesh key={`${sx}-${sy}`} position={[sx*width*.43,sy*depth*.42,1.45]}><boxGeometry args={[.16,.16,2.9]}/><meshStandardMaterial {...maps} color="#74543d"/></mesh>))}
    {Array.from({length:7},(_,i)=><mesh key={i} position={[0,-depth/2+i*depth/6,3]}><boxGeometry args={[width,.13,.18]}/><meshStandardMaterial {...maps} color="#79583f"/></mesh>)}
  </group>;
}
function RaisedPlot({ x, y, z, width, depth, maps, plantingMaps, rotation = 0 }: { x: number; y: number; z: number; width: number; depth: number; maps: MaterialMaps; plantingMaps: MaterialMaps; rotation?: number }) {
  return <group position={[x,y,z]} rotation={[0,0,rotation]}><mesh position={[0,0,.34]}><boxGeometry args={[width,depth,.68]}/><meshStandardMaterial {...maps} color="#806044" roughness={.94}/></mesh><mesh position={[0,0,.72]}><boxGeometry args={[Math.max(.4,width-.5),Math.max(.4,depth-.5),.12]}/><meshStandardMaterial {...plantingMaps} color="#ffffff" roughness={.99}/></mesh></group>;
}

export function GlobeParkBatch8Assembly({ familyId, archetypeId, variantId, guides, frame, terrainZ }: { familyId: ParkLegoFamilyId; archetypeId?: string; variantId?: string; guides: ParkGroundGuide[]; frame: Batch8ProgramFrame; terrainZ: (x: number, y: number) => number }) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const slug = batch27ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug ?? batch25ParkSkinForSelection(archetypeId ?? '', variantId ?? '')?.slug ?? SKIN_SLUG[familyId as Batch8FamilyId];
  const paverMaps = useRoleMaps(slug, 'paver'); const plantingMaps = useRoleMaps(slug, 'planting', 5); const safetyMaps = useRoleMaps(slug, 'safety'); const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_reclaimed_wharf_v0' && variantId && variantId !== 'reclaimed_industrial_park_v0') {
    const cx=frame.minX+frame.width/2, cy=frame.minY+frame.height/2, base=terrainZ(cx,cy)+lift;
    if (variantId === 'reclaimed_industrial_park_v1') {
      const mound=Math.min(frame.width,frame.height)*0.23;
      return <group>
        <mesh position={[cx,cy,base+.55]} scale={[mound,mound*.82,1]}><cylinderGeometry args={[1,1,1.1,48]}/><meshStandardMaterial {...plantingMaps} color="#6f8656" roughness={.98}/></mesh>
        {[-1,0,1].map((side)=><group key={side} position={[cx+side*Math.min(13,frame.width*.18),cy+frame.height*.20,base]}><mesh position={[0,0,3.7]}><cylinderGeometry args={[2.7,3.0,7.4,18]}/><meshStandardMaterial {...safetyMaps} color={side===0?'#647a82':'#8a654d'} metalness={.38} roughness={.67}/></mesh><mesh position={[0,0,7.65]}><cylinderGeometry args={[2.8,2.8,.3,18]}/><meshStandardMaterial color="#35413f" metalness={.55}/></mesh></group>)}
        {Array.from({length:8},(_,i)=>{const a=i*Math.PI/4,x=cx+Math.cos(a)*mound*.82,y=cy+Math.sin(a)*mound*.65;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.55} leaf="#6a7b4d" young/>})}
      </group>;
    }
    if (variantId === 'reclaimed_industrial_park_v2') {
      const bays=Math.min(5,Math.max(2,Math.floor(frame.width/38)));
      return <group>
        <group position={[cx,cy,base]}>{[-1,1].map((side)=><group key={side} position={[side*3.8,0,0]}>{[0,6.5,13].map((z,i)=><mesh key={z} position={[0,0,z+1.6]} rotation={[0,side*.18,i===1?side*.22:0]}><boxGeometry args={[.55,3.0,3.2]}/><meshStandardMaterial color="#303b3b" metalness={.65} roughness={.45}/></mesh>)}</group>)}<mesh position={[0,0,15.4]}><boxGeometry args={[8.8,3.2,.7]}/><meshStandardMaterial color="#303b3b" metalness={.65} roughness={.45}/></mesh></group>
        <Segment from={{x:frame.minX+frame.width*.08,y:cy-frame.height*.2}} to={{x:frame.maxX-frame.width*.08,y:cy+frame.height*.2}} width={2.4} height={.32} z={base+4.8} maps={safetyMaps} color="#8a553d"/>
        {Array.from({length:bays*2},(_,i)=>{const x=frame.minX+frame.width*(.1+(i%bays+.5)*.8/bays),y=frame.minY+frame.height*(i<bays?.18:.82);return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.55} young/>})}
      </group>;
    }
    return <group>
      {[-1,0,1].map((side)=><group key={side} position={[cx+side*Math.min(17,frame.width*.18),cy+frame.height*.15,base]}><mesh position={[0,0,5.5]}><cylinderGeometry args={[2.3,3.1,11,16]}/><meshStandardMaterial {...safetyMaps} color="#5a4e45" metalness={.5} roughness={.58}/></mesh><mesh position={[0,0,11.5]}><boxGeometry args={[7,.8,.7]}/><meshStandardMaterial color="#3d4240" metalness={.62}/></mesh></group>)}
      <mesh position={[cx,cy-frame.height*.22,base+.18]}><boxGeometry args={[Math.min(30,frame.width*.46),Math.min(13,frame.height*.22),.36]}/><meshStandardMaterial {...paverMaps} color="#5e625f"/></mesh>
      <mesh position={[cx,cy-frame.height*.22,base+.40]}><boxGeometry args={[Math.min(27,frame.width*.42),Math.min(10,frame.height*.18),.08]}/><meshPhysicalMaterial color="#396c78" transparent opacity={.82} roughness={.16}/></mesh>
    </group>;
  }

  if (familyId === 'park_quarry_tier_cascade_v2' && variantId && variantId !== 'quarry_sunken_garden_park_v2') {
    const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift,r=Math.min(frame.width,frame.height)*.30;
    if (variantId === 'quarry_sunken_garden_park_v0') return <group>
      {[1,.82,.64].map((scale,i)=><mesh key={scale} position={[cx,cy,base+i*.38]} scale={[r*scale,r*scale*.78,1]}><ringGeometry args={[.86,1,48]}/><meshStandardMaterial {...(i===2?plantingMaps:paverMaps)} color={i===2?'#6f8554':'#a69c8a'} roughness={.96}/></mesh>)}
      {Array.from({length:9},(_,i)=>{const a=i*Math.PI*2/9,x=cx+Math.cos(a)*r*.5,y=cy+Math.sin(a)*r*.38;return <mesh key={i} position={[x,y,terrainZ(x,y)+lift+.85]}><boxGeometry args={[.42,.42,1.7]}/><meshStandardMaterial color={i%2?'#4c554f':'#81796d'} metalness={.25}/></mesh>})}
    </group>;
    if (variantId === 'quarry_sunken_garden_park_v1') return <group>
      <mesh position={[cx,cy,base+.20]} scale={[r,r*.76,1]}><cylinderGeometry args={[1,1,.40,48]}/><meshStandardMaterial {...paverMaps} color="#9b907d"/></mesh>
      <mesh position={[cx,cy,base+.44]} scale={[r*.91,r*.67,1]}><cylinderGeometry args={[1,1,.08,48]}/><meshPhysicalMaterial color="#4f8990" transparent opacity={.84} roughness={.13}/></mesh>
      <mesh position={[cx-r*.42,cy-r*.49,base+.50]} scale={[r*.36,r*.15,1]}><cylinderGeometry args={[1,1,.10,28]}/><meshStandardMaterial color="#c4aa76" roughness={.96}/></mesh>
      {Array.from({length:14},(_,i)=>{const a=i*Math.PI*2/14,x=cx+Math.cos(a)*r*1.14,y=cy+Math.sin(a)*r*.91;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={.58} leaf={i%2?'#5a7149':'#405f48'}/>})}
    </group>;
    return <group>
      {[1,.74,.47].map((scale,i)=><mesh key={scale} position={[cx,cy,base+i*.34]} scale={[r*scale,r*scale*.78,1]}><ringGeometry args={[.58,1,64]}/><meshStandardMaterial {...plantingMaps} color={['#b7c49a','#b7a78b','#a7bd8d'][i]} roughness={.98}/></mesh>)}
      {[0,Math.PI/2].map((angle)=><Segment key={angle} from={{x:cx-Math.cos(angle)*r*.96,y:cy-Math.sin(angle)*r*.75}} to={{x:cx+Math.cos(angle)*r*.96,y:cy+Math.sin(angle)*r*.75}} width={1.45} height={.16} z={base+.72} maps={paverMaps} color="#ffffff"/>)}
      <mesh position={[cx,cy,base+1.10]} scale={[r*.25,r*.20,1]}><cylinderGeometry args={[1,1,.14,48]}/><meshPhysicalMaterial color="#4b7b80" transparent opacity={.84}/></mesh>
      {Array.from({length:36},(_,i)=>{const a=i*Math.PI*2/36,rr=r*(.45+(i%3)*.19),x=cx+Math.cos(a)*rr,y=cy+Math.sin(a)*rr*.78;return <mesh key={i} position={[x,y,terrainZ(x,y)+lift+1.12]} scale={[1.25,.8,.72]}><sphereGeometry args={[.46,8,6]}/><meshStandardMaterial color={['#c74963','#e8b04b','#80599e','#efe0bf'][i%4]}/></mesh>})}
      {Array.from({length:8},(_,i)=>{const a=i*Math.PI*2/8,x=cx+Math.cos(a)*r*1.15,y=cy+Math.sin(a)*r*.90;return <Tree key={`show-tree-${i}`} x={x} y={y} z={terrainZ(x,y)+lift} scale={.64+(i%2)*.08}/>})}
    </group>;
  }

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
    const pine=variantId==='estate_picnic_grove_v0',meadow=variantId==='estate_picnic_grove_v2',regional=variantId==='estate_picnic_grove_v3';
    const cols=Math.min(regional?7:meadow?5:pine?4:5,Math.max(2,Math.floor(frame.width/(regional?22:28)))); const rows=Math.min(regional?5:4,Math.max(2,Math.floor(frame.height/(regional?23:28)))); const count=cols*rows;
    return <group>
      {pine&&<Segment from={{x:frame.minX+frame.width*.08,y:frame.minY+frame.height*.18}} to={{x:frame.maxX-frame.width*.08,y:frame.minY+frame.height*.30}} width={2.2} height={.12} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.24)+lift+.08} color="#4a7880"/>}
      {Array.from({length:count},(_,i)=>{const col=i%cols,row=Math.floor(i/cols); const x=frame.minX+frame.width*(0.10+(col+0.5)*0.80/cols); const y=frame.minY+frame.height*(0.10+(row+0.5)*0.80/rows); const z=terrainZ(x,y)+lift; const keep=!meadow||row===0||col===0||col===cols-1||i%4===0; return keep?<group key={i}><Tree x={x} y={y} z={z} scale={pine ? .78 : .82+(i%3)*.08} leaf={pine?'#3d6049':'#4f6e42'} /><PicnicTable x={x+2.5} y={y+1.0} z={terrainZ(x+2.5,y+1)+lift} maps={timberMaps} rotation={i%2?Math.PI/2:0}/><mesh position={[x-2,y+1,z+.7]}><cylinderGeometry args={[.24,.2,1.4,10]}/><meshStandardMaterial color="#393f3d" metalness={.55}/></mesh></group>:null;})}
      {(meadow||regional)&&Array.from({length:regional?3:1},(_,i)=>{const x=frame.minX+frame.width*(.28+i*.22),y=frame.maxY-frame.height*.16,z=terrainZ(x,y)+lift;return <group key={`p-${i}`} position={[x,y,z]}>{[-1,1].flatMap(sx=>[-1,1].map(sy=><mesh key={`${sx}-${sy}`} position={[sx*3.8,sy*2,1.6]}><boxGeometry args={[.2,.2,3.2]}/><meshStandardMaterial {...timberMaps} color="#765a3e"/></mesh>))}<mesh position={[0,0,3.3]}><boxGeometry args={[8.5,4.8,.3]}/><meshStandardMaterial {...timberMaps} color="#73543a"/></mesh></group>})}
    </group>;
  }

  if (familyId === 'park_constructed_wetland_boardwalk_v0') {
    const cells=guides.filter((g)=>g.kind==='ellipse'); const walk=guides.find((g)=>g.kind==='polyline'); const points=walk?route(walk,frame):[];
    const tidal=variantId==='constructed_wetland_eco_park_variant_1', wildlife=variantId==='constructed_wetland_eco_park_variant_2', natureCenter=variantId==='constructed_wetland_eco_park_variant_3';
    const visibleCells=wildlife?cells.slice(0,Math.max(1,Math.ceil(cells.length/2))):cells;
    return <group>{cells.map((cell,index)=>{const c=center(cell,frame); const s=resolveParkGuideDimensionsM(cell,frame); const z=terrainZ(c.x,c.y)+lift; return <group key={index}><mesh position={[c.x,c.y,z+0.11]} scale={[s.width/2,s.height/2,1]}><cylinderGeometry args={[1,1,0.22,32]} /><meshPhysicalMaterial color="#527b74" transparent opacity={0.82} roughness={0.2} /></mesh>{Array.from({length:14},(_,j)=>{const a=j*2.4; const x=c.x+Math.cos(a)*s.width*0.35; const y=c.y+Math.sin(a)*s.height*0.35; return <mesh key={j} position={[x,y,terrainZ(x,y)+lift+0.65]}><coneGeometry args={[0.14,1.3+(j%3)*0.25,6]} /><meshStandardMaterial {...plantingMaps} color={j%2?'#718451':'#556f43'} roughness={0.98} /></mesh>;})}</group>;})}
      {points.slice(0,-1).map((point,index)=><Segment key={index} from={point} to={points[index+1]} width={2.2} height={0.22} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.48} maps={timberMaps} color="#80664d" />)}
      {tidal&&<><Segment from={{x:frame.minX+frame.width*.08,y:frame.minY+frame.height*.32}} to={{x:frame.maxX-frame.width*.08,y:frame.maxY-frame.height*.28}} width={Math.max(5,frame.width*.08)} height={.18} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.52)+lift+.1} maps={plantingMaps} color="#ffffff"/><mesh position={[frame.minX+frame.width*.72,frame.minY+frame.height*.59,terrainZ(frame.minX+frame.width*.72,frame.minY+frame.height*.59)+lift+.45]}><boxGeometry args={[Math.min(8,frame.width*.12),1.2,.9]}/><meshStandardMaterial {...paverMaps} color="#ffffff" roughness={.94}/></mesh></>}
      {wildlife&&visibleCells.map((cell,index)=>{const c=center(cell,frame),s=resolveParkGuideDimensionsM(cell,frame),z=terrainZ(c.x,c.y)+lift;return <mesh key={`deck-${index}`} position={[c.x+s.width*.28,c.y-s.height*.30,z+.36]}><boxGeometry args={[Math.min(7,s.width*.35),Math.min(5,s.height*.28),.28]}/><meshStandardMaterial {...timberMaps} color="#ffffff" roughness={.92}/></mesh>})}
      {natureCenter&&<ParkPavilion x={frame.maxX-frame.width*.18} y={frame.maxY-frame.height*.19} z={terrainZ(frame.maxX-frame.width*.18,frame.maxY-frame.height*.19)+lift} width={Math.min(10,frame.width*.18)} depth={Math.min(6,frame.height*.16)} maps={timberMaps} glass/>}
    </group>;
  }

  if (familyId === 'park_academic_planted_court_v0') {
    const beds=guides.filter((g)=>g.kind==='rounded_rectangle'||g.kind==='rectangle');
    const corten=variantId==='academic_courtyard_variant_1', glass=variantId==='academic_courtyard_variant_2', timber=variantId==='academic_courtyard_variant_3';
    return <group>{beds.map((bed,index)=>{const c=center(bed,frame); const s=resolveParkGuideDimensionsM(bed,frame); const z=terrainZ(c.x,c.y)+lift; return <group key={index}>
      <mesh position={[c.x,c.y,z+0.38]}><boxGeometry args={[s.width,s.height,0.76]} /><meshStandardMaterial {...(corten?safetyMaps:paverMaps)} color={corten?'#944d31':'#80786b'} roughness={0.9} /></mesh>
      {(!corten||index%3===0)&&<mesh position={[c.x,c.y,z+0.8]}><boxGeometry args={[Math.max(0.5,s.width-0.7),Math.max(0.5,s.height-0.7),0.16]} /><meshStandardMaterial {...plantingMaps} color="#596b45" roughness={0.98} /></mesh>}
      {index%2===0&&<mesh position={[c.x,c.y-s.height/2-0.35,z+0.72]}><boxGeometry args={[Math.min(4,s.width*0.72),0.48,0.18]} /><meshStandardMaterial {...timberMaps} color="#947354" roughness={0.9} /></mesh>}
    </group>;})}
      {corten&&<><mesh position={[frame.minX+frame.width*.12,frame.minY+frame.height*.50,terrainZ(frame.minX+frame.width*.12,frame.minY+frame.height*.50)+lift+1.4]}><boxGeometry args={[.35,frame.height*.68,2.8]}/><meshStandardMaterial {...safetyMaps} color="#93482f" metalness={.36} roughness={.62}/></mesh><Pergola x={frame.maxX-frame.width*.23} y={frame.maxY-frame.height*.18} z={terrainZ(frame.maxX-frame.width*.23,frame.maxY-frame.height*.18)+lift} width={Math.min(10,frame.width*.26)} depth={Math.min(5,frame.height*.17)} maps={safetyMaps}/></>}
      {glass&&<ParkPavilion x={frame.minX+frame.width*.5} y={frame.maxY-frame.height*.22} z={terrainZ(frame.minX+frame.width*.5,frame.maxY-frame.height*.22)+lift} width={Math.min(14,frame.width*.34)} depth={Math.min(7,frame.height*.20)} maps={paverMaps} glass/>}
      {timber&&<>{[-1,1].map((side)=><mesh key={side} position={[frame.minX+frame.width*.5+side*frame.width*.23,frame.maxY-frame.height*.12,terrainZ(frame.minX+frame.width*.5+side*frame.width*.23,frame.maxY-frame.height*.12)+lift+1.7]}><boxGeometry args={[Math.min(9,frame.width*.20),.28,3.4]}/><meshStandardMaterial {...timberMaps} color="#ffffff" roughness={.92}/></mesh>)}{[-.22,0,.22].map((offset,i)=><Boulder key={i} x={frame.minX+frame.width*(.5+offset)} y={frame.minY+frame.height*.26} z={terrainZ(frame.minX+frame.width*(.5+offset),frame.minY+frame.height*.26)+lift} scale={1.1+(i%2)*.25} color="#846f59"/>)}</>}
    </group>;
  }

  if (familyId === 'park_campus_green_spine_v0') {
    const axis=guides.find((g)=>g.kind==='polyline'||g.kind==='axis'); const points=axis?route(axis,frame):[]; const bays=Math.min(16,Math.max(4,Math.floor(frame.height/18)));
    const paved=variantId==='campus_pedestrian_spine_variant_1', pavilion=variantId==='campus_pedestrian_spine_variant_2', garden=variantId==='campus_pedestrian_spine_variant_3';
    return <group>{points.slice(0,-1).map((point,index)=><Segment key={index} from={point} to={points[index+1]} width={paved?Math.min(10,frame.width*.18):5.2} height={0.18} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.15} maps={paverMaps} color="#aaa59a" />)}
      {Array.from({length:bays},(_,i)=>[-1,1].map((side)=>{const x=frame.minX+frame.width*(0.5+side*(paved?.38:.29)); const y=frame.maxY-frame.height*(0.08+(i+0.5)*0.84/bays); return <group key={`${i}-${side}`}><Tree x={x} y={y} z={terrainZ(x,y)+lift} scale={paved?.58:.72} leaf="#4f7149" />{!paved&&<mesh position={[x-side*2.5,y,terrainZ(x-side*2.5,y)+lift+0.16]}><boxGeometry args={[3.2,2.8,0.32]} /><meshStandardMaterial {...plantingMaps} color="#65794e" roughness={0.98} /></mesh>}{paved&&<mesh position={[x-side*1.5,y,terrainZ(x-side*1.5,y)+lift+.55]}><cylinderGeometry args={[.13,.16,1.1,10]}/><meshStandardMaterial color="#3e4544" metalness={.48} roughness={.5}/></mesh>}</group>;}))}
      {pavilion&&<ParkPavilion x={frame.minX+frame.width*.5} y={frame.minY+frame.height*.5} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.5)+lift} width={Math.min(13,frame.width*.27)} depth={Math.min(7,frame.height*.14)} maps={paverMaps} glass/>}
      {garden&&Array.from({length:Math.min(4,Math.max(2,Math.floor(frame.height/35)))},(_,i)=>{const y=frame.minY+frame.height*(.18+(i+.5)*.64/Math.min(4,Math.max(2,Math.floor(frame.height/35))));return <Pergola key={i} x={frame.minX+frame.width*.5} y={y} z={terrainZ(frame.minX+frame.width*.5,y)+lift} width={Math.min(9,frame.width*.20)} depth={Math.min(4,frame.height*.08)} maps={timberMaps}/>})}
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
    const greenhouse=variantId==='research_garden_teaching_arboretum_variant_1', teaching=variantId==='research_garden_teaching_arboretum_variant_2', plots=variantId==='research_garden_teaching_arboretum_variant_3';
    if(greenhouse||teaching||plots){const cols=plots?4:3,rows=plots?3:2;return <group>
      {Array.from({length:cols*rows},(_,i)=>{const x=frame.minX+frame.width*(.12+(i%cols+.5)*.62/cols),y=frame.minY+frame.height*(.13+(Math.floor(i/cols)+.5)*.60/rows);return <RaisedPlot key={i} x={x} y={y} z={terrainZ(x,y)+lift} width={Math.min(5,frame.width*.13)} depth={Math.min(2.6,frame.height*.11)} maps={timberMaps} plantingMaps={plantingMaps} rotation={plots&&i%2?Math.PI/2:0}/>})}
      {greenhouse&&<ParkPavilion x={frame.maxX-frame.width*.18} y={frame.minY+frame.height*.5} z={terrainZ(frame.maxX-frame.width*.18,frame.minY+frame.height*.5)+lift} width={Math.min(13,frame.width*.22)} depth={Math.min(8,frame.height*.28)} maps={paverMaps} glass/>}
      {teaching&&<ParkPavilion x={frame.maxX-frame.width*.20} y={frame.maxY-frame.height*.22} z={terrainZ(frame.maxX+frame.width*-.20,frame.maxY-frame.height*.22)+lift} width={Math.min(12,frame.width*.22)} depth={Math.min(7,frame.height*.20)} maps={timberMaps}/>}
      {plots&&<Pergola x={frame.maxX-frame.width*.18} y={frame.maxY-frame.height*.20} z={terrainZ(frame.maxX+frame.width*-.18,frame.maxY-frame.height*.20)+lift} width={Math.min(8,frame.width*.16)} depth={Math.min(5,frame.height*.16)} maps={timberMaps}/>}
      {Array.from({length:Math.min(8,Math.max(4,Math.floor(frame.width/20)))},(_,i)=>{const x=frame.minX+frame.width*(.10+i*.80/Math.max(1,Math.min(8,Math.max(4,Math.floor(frame.width/20)))-1)),y=frame.maxY-frame.height*.10;return <Tree key={`t-${i}`} x={x} y={y} z={terrainZ(x,y)+lift} scale={.58+(i%3)*.09}/>})}
    </group>}
    return <group>{Array.from({length:count},(_,i)=>{const x=frame.minX+frame.width*(0.08+((i*.347)%0.84)); const y=frame.minY+frame.height*(0.08+((i*.619)%0.84)); const z=terrainZ(x,y)+lift; return <group key={i}><Tree x={x} y={y} z={z} scale={0.58+(i%5)*0.11} leaf={['#496946','#617a45','#456b58'][i%3]} />{i%3===0&&<mesh position={[x+1.8,y,z+0.62]} rotation={[0.15,0,0]}><boxGeometry args={[0.9,0.08,0.62]} /><meshStandardMaterial {...timberMaps} color="#765f48" roughness={0.9} /></mesh>}{i%5===0&&<Boulder x={x-2} y={y+1.3} z={z} scale={0.8}/>}</group>;})}</group>;
  }

  if (familyId === 'park_rewilding_reforestation_v1') {
    const count=Math.min(72,Math.max(20,Math.floor(frame.width*frame.height/700)));
    const prairie=variantId==='rewilding_ecological_restoration_zone_variant_0', interpretive=variantId==='rewilding_ecological_restoration_zone_variant_2', riparian=variantId==='rewilding_ecological_restoration_zone_variant_3';
    if(prairie||interpretive||riparian){const treeCount=prairie?Math.min(12,Math.max(4,Math.floor(frame.width/22))):interpretive?Math.ceil(count*.34):Math.ceil(count*.48);const habitat=(fx:number,fy:number)=>({x:frame.minX+frame.width*fx,y:frame.minY+frame.height*fy});const a=habitat(.24,.25),b=habitat(.74,.68);return <group>
      {Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.08+((i*.337)%.84)),y=frame.minY+frame.height*(.08+((i*.581)%.84));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={prairie?.48:.58+(i%3)*.1} leaf={riparian?'#4f7056':'#637851'} young/>})}
      {prairie&&<><Segment from={{x:frame.minX+frame.width*.08,y:frame.minY+frame.height*.64}} to={{x:frame.maxX-frame.width*.08,y:frame.maxY-frame.height*.28}} width={2.2} height={.24} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.50)+lift+.34} maps={timberMaps} color="#ffffff"/><mesh position={[frame.maxX-frame.width*.16,frame.maxY-frame.height*.24,terrainZ(frame.maxX-frame.width*.16,frame.maxY-frame.height*.24)+lift+.38]}><boxGeometry args={[Math.min(8,frame.width*.16),Math.min(5,frame.height*.12),.28]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh></>}
      {interpretive&&Array.from({length:5},(_,i)=>{const x=frame.minX+frame.width*(.16+i*.68/4),y=frame.minY+frame.height*(i%2?.30:.67),z=terrainZ(x,y)+lift;return <group key={i}><Boulder x={x} y={y} z={z} scale={1+(i%2)*.25}/><mesh position={[x+1.3,y,z+1.0]} rotation={[0,.12,0]}><boxGeometry args={[1.1,.1,1.35]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh></group>})}
      {riparian&&<><Segment from={{x:frame.minX+frame.width*.06,y:frame.minY+frame.height*.42}} to={{x:frame.maxX-frame.width*.06,y:frame.maxY-frame.height*.35}} width={Math.max(4,frame.width*.07)} height={.18} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.53)+lift+.05} maps={safetyMaps} color="#6c8790"/>{Array.from({length:12},(_,i)=>{const x=frame.minX+frame.width*(.1+i*.8/11),y=frame.minY+frame.height*(.42+i*.18/11)+(i%2?2:-2),z=terrainZ(x,y)+lift;return <group key={i}><Boulder x={x} y={y} z={z} scale={.65+(i%3)*.12}/>{i%4===0&&<mesh position={[x,y+2,z+.32]} rotation={[0,Math.PI/2,.12]}><cylinderGeometry args={[.16,.23,3.4,8]}/><meshStandardMaterial {...timberMaps} color="#ffffff"/></mesh>}</group>})}</>}
      {prairie&&<><ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingStandingSnag.url} position={[b.x,b.y,terrainZ(b.x,b.y)+lift]} yaw={.32}/><ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingBrushPile.url} position={[a.x,a.y,terrainZ(a.x,a.y)+lift]} yaw={-.24}/></>}
      {interpretive && <ParkKitGlb
        url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingHollowSnag.url}
        position={[b.x, b.y, terrainZ(b.x, b.y) + lift]}
        yaw={-0.2}
      />}
      {riparian&&<><ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingRootWad.url} position={[a.x,a.y,terrainZ(a.x,a.y)+lift]} yaw={.15}/><ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingBrushPile.url} position={[b.x,b.y,terrainZ(b.x,b.y)+lift]} yaw={-.42}/></>}
    </group>}
    const snag={x:frame.minX+frame.width*.72,y:frame.minY+frame.height*.68};const brush={x:frame.minX+frame.width*.28,y:frame.minY+frame.height*.24};return <group>{Array.from({length:count},(_,i)=>{const x=frame.minX+frame.width*(0.06+((i*.283)%0.88)); const y=frame.minY+frame.height*(0.06+((i*.491)%0.88)); return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} scale={0.62+(i%4)*0.12} leaf={i%2?'#64805a':'#55704a'} young />;})}
      {Array.from({length:Math.min(10,Math.max(3,Math.floor(frame.width/24)))},(_,i)=>{const x=frame.minX+frame.width*(0.12+((i*.37)%0.76)); const y=frame.minY+frame.height*(0.18+((i*.53)%0.64)); const z=terrainZ(x,y)+lift; return <group key={i}>{[-1,0,1].map((n)=><mesh key={n} position={[x+n*0.8,y,z+0.35]} rotation={[0,Math.PI/2,n*.18]}><cylinderGeometry args={[0.18,0.28,3.4,8]} /><meshStandardMaterial {...timberMaps} color="#69523c" roughness={0.98} /></mesh>)}</group>;})}
      <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingHollowSnag.url} position={[snag.x,snag.y,terrainZ(snag.x,snag.y)+lift]} yaw={.18}/>
      <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.rewildingBrushPile.url} position={[brush.x,brush.y,terrainZ(brush.x,brush.y)+lift]} yaw={-.31}/>
    </group>;
  }

  if (familyId === 'park_stormwater_arid_channel_v3') {
    const channel=guides.find((g)=>g.kind==='polyline'); const points=channel?route(channel,frame):[];
    const bioswale=variantId==='stormwater_resilience_park_variant_0', detention=variantId==='stormwater_resilience_park_variant_1', terraced=variantId==='stormwater_resilience_park_variant_2';
    if(bioswale||detention||terraced){return <group>
      {bioswale&&Array.from({length:4},(_,i)=>{const y=frame.minY+frame.height*(.16+i*.68/3),z=terrainZ(frame.minX+frame.width*.5,y)+lift;return <group key={i}><mesh position={[frame.minX+frame.width*.5,y,z+.18+i*.08]}><boxGeometry args={[frame.width*(.78-i*.06),Math.min(7,frame.height*.12),.34]}/><meshStandardMaterial {...(i%2?plantingMaps:paverMaps)} color="#ffffff" roughness={.96}/></mesh>{i<3&&<Segment from={{x:frame.minX+frame.width*.16,y:y+frame.height*.07}} to={{x:frame.maxX-frame.width*.16,y:y+frame.height*.07}} width={1.8} height={.20} z={z+.35} maps={timberMaps} color="#ffffff"/>}</group>})}
      {detention&&<><mesh position={[frame.minX+frame.width*.5,frame.minY+frame.height*.52,terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.52)+lift+.16]} scale={[frame.width*.34,frame.height*.30,1]}><cylinderGeometry args={[1,1,.30,48]}/><meshPhysicalMaterial color="#5e8581" transparent opacity={.78} roughness={.2}/></mesh><Segment from={{x:frame.minX+frame.width*.10,y:frame.minY+frame.height*.28}} to={{x:frame.maxX-frame.width*.10,y:frame.maxY-frame.height*.28}} width={2.2} height={.24} z={terrainZ(frame.minX+frame.width*.5,frame.minY+frame.height*.5)+lift+.42} maps={timberMaps} color="#ffffff"/><ParkPavilion x={frame.maxX-frame.width*.18} y={frame.maxY-frame.height*.17} z={terrainZ(frame.maxX-frame.width*.18,frame.maxY-frame.height*.17)+lift} width={Math.min(8,frame.width*.14)} depth={Math.min(5,frame.height*.14)} maps={timberMaps}/></>}
      {terraced&&Array.from({length:5},(_,i)=>{const y=frame.minY+frame.height*(.15+i*.7/4),z=terrainZ(frame.minX+frame.width*.5,y)+lift+i*.18;return <group key={i}><mesh position={[frame.minX+frame.width*.5,y,z+.17]}><boxGeometry args={[frame.width*(.84-i*.07),Math.min(8,frame.height*.13),.34]}/><meshStandardMaterial {...paverMaps} color="#ffffff" roughness={.9}/></mesh>{i%2===1&&<mesh position={[frame.minX+frame.width*.5,y,z+.38]}><boxGeometry args={[frame.width*(.42-i*.025),Math.min(2.2,frame.height*.04),.08]}/><meshPhysicalMaterial color="#5f8f97" roughness={.18}/></mesh>}</group>})}
    </group>}
    return <group>{points.slice(0,-1).map((point,index)=><group key={index}><Segment from={point} to={points[index+1]} width={6.5} height={0.25} z={Math.max(terrainZ(point.x,point.y),terrainZ(points[index+1].x,points[index+1].y))+lift+0.08} maps={safetyMaps} color="#9a866b" />{Array.from({length:5},(_,j)=>{const t=(j+.5)/5; const x=point.x+(points[index+1].x-point.x)*t; const y=point.y+(points[index+1].y-point.y)*t+(j%2?1.8:-1.8); return <Boulder key={j} x={x} y={y} z={terrainZ(x,y)+lift} scale={0.65+(j%3)*.18} color="#8d806e" />;})}</group>)}
      {Array.from({length:Math.min(28,Math.max(10,Math.floor(frame.width*frame.height/800)))},(_,i)=>{const x=frame.minX+frame.width*(0.08+((i*.31)%0.84)); const y=frame.minY+frame.height*(0.08+((i*.57)%0.84)); return <mesh key={i} position={[x,y,terrainZ(x,y)+lift+0.65]}><coneGeometry args={[0.55,1.3+(i%3)*0.35,7]} /><meshStandardMaterial {...plantingMaps} color={i%2?'#718060':'#8b7650'} roughness={0.99} /></mesh>;})}
    </group>;
  }
  return null;
}
