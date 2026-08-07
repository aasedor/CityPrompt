import { useEffect, useMemo } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import {
  resolveParkGuideDimensionsM,
  type ParkGroundGuide,
} from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import { batch18ParkSkinForSelection } from './parkBatch18Skins';
import { PARK_MESHY_ARCHETYPE_ASSETS } from './parkMeshyArchetypeAssets';

export interface Batch5ProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
}

interface Point { x: number; y: number }

type Batch5FamilyId = Extract<ParkLegoFamilyId,
  | 'park_disc_golf_wooded_v0' | 'park_bocce_piazza_v0'
  | 'park_climbing_competition_v0' | 'park_mini_golf_classic_v0'
  | 'park_beach_volleyball_competition_v0' | 'park_pollinator_prairie_v0'
  | 'park_orchard_heritage_v0' | 'park_bioswale_streetside_v0'
  | 'park_sculpture_museum_court_v0' | 'park_labyrinth_classical_v0'>;

const SKIN_SLUG: Record<Batch5FamilyId, string> = {
  park_disc_golf_wooded_v0: 'disc-golf-wooded-championship',
  park_bocce_piazza_v0: 'bocce-italian-piazza',
  park_climbing_competition_v0: 'climbing-competition-boulder',
  park_mini_golf_classic_v0: 'mini-golf-classic-themed',
  park_beach_volleyball_competition_v0: 'beach-volleyball-competition',
  park_pollinator_prairie_v0: 'pollinator-prairie-restoration',
  park_orchard_heritage_v0: 'urban-orchard-heritage-apple',
  park_bioswale_streetside_v0: 'bioswale-streetside',
  park_sculpture_museum_court_v0: 'sculpture-museum-court',
  park_labyrinth_classical_v0: 'labyrinth-classical-stone',
};

interface MaterialMaps {
  map: THREE.Texture; normalMap: THREE.Texture; roughnessMap: THREE.Texture; aoMap: THREE.Texture;
}

function ParkKitGlb({ url, position, yaw = 0 }: {
  url: string;
  position: [number, number, number];
  yaw?: number;
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const next = scene.clone(true);
    next.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.renderOrder = 149;
    });
    return next;
  }, [scene]);
  return <group position={position} rotation={[0, 0, yaw]}>
    <group rotation={[Math.PI / 2, 0, 0]}><primitive object={clone} /></group>
  </group>;
}

function useRoleMaps(slug: string, role: string): MaterialMaps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({
    map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`,
    roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg`,
  });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(3, 3);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as MaterialMaps, [source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

function center(guide: ParkGroundGuide, frame: Batch5ProgramFrame): Point {
  return { x: frame.minX + frame.width * guide.x, y: frame.maxY - frame.height * guide.y };
}

function route(guide: ParkGroundGuide, frame: Batch5ProgramFrame): Point[] {
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
  const dx = (width || height) * 0.5 * Math.cos(angle);
  const dy = (width || height) * 0.5 * Math.sin(angle);
  return [{ x: c.x - dx, y: c.y - dy }, { x: c.x + dx, y: c.y + dy }];
}

function Segment({
  from, to, width, height, z, color,
}: { from: Point; to: Point; width: number; height: number; z: number; color: string }) {
  const length = Math.max(0.05, Math.hypot(to.x - from.x, to.y - from.y));
  return (
    <mesh position={[(from.x + to.x) / 2, (from.y + to.y) / 2, z + height / 2]} rotation={[0, 0, Math.atan2(to.y - from.y, to.x - from.x)]} renderOrder={146}>
      <boxGeometry args={[length, width, height]} />
      <meshStandardMaterial color={color} roughness={0.86} metalness={0.02} />
    </mesh>
  );
}

export function GlobeParkBatch5Assembly({
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
  frame: Batch5ProgramFrame;
  terrainZ: (x: number, y: number) => number;
}) {
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const selectedSkin = batch18ParkSkinForSelection(archetypeId ?? '', variantId ?? '');
  const variantSkin = selectedSkin !== null;
  const slug = selectedSkin?.slug ?? SKIN_SLUG[familyId as Batch5FamilyId];
  const paverMaps = useRoleMaps(slug, 'paver');
  const lawnMaps = useRoleMaps(slug, 'lawn');
  const safetyMaps = useRoleMaps(slug, 'safety');
  const timberMaps = useRoleMaps(slug, 'timber');

  if (familyId === 'park_disc_golf_wooded_v0') {
    const tees = guides.filter((guide) => guide.kind === 'rectangle');
    const targets = guides.filter((guide) => guide.kind === 'ellipse');
    return <group>{tees.map((tee, index) => {
      const c = center(tee, frame); const size = resolveParkGuideDimensionsM(tee, frame);
      const yaw = -((tee.rotationDeg ?? 0) * Math.PI) / 180;
      return <group key={`tee-${index}`}>
        <mesh position={[c.x, c.y, terrainZ(c.x, c.y) + lift + 0.06]} rotation={[0, 0, yaw]}><boxGeometry args={[size.width, size.height, 0.12]} /><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#d5d1c7'} roughness={0.94} /></mesh>
        <ParkKitGlb url="/park-kits/disc-golf/disc-golf-tee-sign.glb" position={[c.x - Math.cos(yaw) * (size.width / 2 + 0.55), c.y - Math.sin(yaw) * (size.width / 2 + 0.55), terrainZ(c.x, c.y) + lift + 0.12]} yaw={yaw} />
      </group>;
    })}{targets.map((target, index) => {
      const c = center(target, frame); const z = terrainZ(c.x, c.y) + lift;
      return <ParkKitGlb key={`basket-${index}`} url="/park-kits/disc-golf/disc-golf-basket.glb" position={[c.x, c.y, z]} />;
    })}</group>;
  }

  if (familyId === 'park_bocce_piazza_v0') {
    const lane = guides.find((guide) => guide.kind === 'rounded_rectangle');
    const pergola = guides.find((guide) => guide.kind === 'line');
    if (!lane) return null;
    const c = center(lane, frame); const size = resolveParkGuideDimensionsM(lane, frame); const z = terrainZ(c.x, c.y) + lift;
    const pRoute = pergola ? route(pergola, frame) : [];
    return <group>
      <mesh position={[c.x, c.y, z + 0.025]}><planeGeometry args={[size.width, size.height]} /><meshStandardMaterial {...safetyMaps} color={variantSkin ? '#ffffff' : '#ded4b8'} roughness={0.94} /></mesh>
      {[-1, 1].map((side) => <mesh key={`long-${side}`} position={[c.x, c.y + side * size.height / 2, z + 0.22]}><boxGeometry args={[size.width, 0.34, 0.44]} /><meshStandardMaterial color="#94836a" roughness={0.94} /></mesh>)}
      {[-1, 1].map((side) => <mesh key={`short-${side}`} position={[c.x + side * size.width / 2, c.y, z + 0.22]}><boxGeometry args={[0.34, size.height, 0.44]} /><meshStandardMaterial color="#94836a" roughness={0.94} /></mesh>)}
      {pRoute.length === 2 && <>{Array.from({ length: 6 }, (_, index) => { const t = index / 5; const x = pRoute[0].x + (pRoute[1].x - pRoute[0].x) * t; const y = pRoute[0].y + (pRoute[1].y - pRoute[0].y) * t; return <mesh key={index} position={[x, y, terrainZ(x, y) + lift + 1.45]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.10, 0.13, 2.9, 8]} /><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#9e7850'} roughness={0.9} /></mesh>; })}<Segment from={pRoute[0]} to={pRoute[1]} width={3.2} height={0.15} z={Math.max(terrainZ(pRoute[0].x,pRoute[0].y),terrainZ(pRoute[1].x,pRoute[1].y))+lift+2.82} color="#7d5d3c" /></>}
      <ParkKitGlb url="/park-kits/bocce-petanque/bocce-score-stand.glb" position={[c.x - size.width / 2 - 1.0, c.y, z]} yaw={Math.PI / 2} />
      <ParkKitGlb url="/park-kits/bocce-petanque/bocce-ball-rack.glb" position={[c.x + size.width / 2 + 1.25, c.y, z]} yaw={Math.PI / 2} />
    </group>;
  }

  if (familyId === 'park_climbing_competition_v0') {
    const walls = guides.filter((guide) => guide.kind === 'rectangle');
    const variantIndex = Number(variantId?.match(/_v([0-3])$/)?.[1] ?? 0);
    const filename = variantIndex === 1 ? 'climbing-natural-boulder.glb'
      : variantIndex === 3 ? 'climbing-traverse-wall.glb'
        : 'climbing-competition-wall.glb';
    return <group>{walls.slice(0, variantIndex === 1 ? 3 : 2).map((wall, index) => {
      const c = center(wall, frame); const z = terrainZ(c.x,c.y)+lift;
      return <ParkKitGlb key={index} url={`/park-kits/climbing-bouldering/${filename}`} position={[c.x,c.y,z]} yaw={(index - 0.5) * 0.24} />;
    })}</group>;
  }

  if (familyId === 'park_mini_golf_classic_v0') {
    const lanes = guides.filter((guide) => guide.kind === 'rounded_rectangle');
    return <group>{lanes.map((lane,index)=>{const c=center(lane,frame);const s=resolveParkGuideDimensionsM(lane,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={index} position={[c.x,c.y,z]} rotation={[0,0,-((lane.rotationDeg??0)*Math.PI)/180]}>
      <mesh position={[0,0,0.025]}><planeGeometry args={[s.width,s.height]}/><meshStandardMaterial {...lawnMaps} color={variantSkin ? '#ffffff' : '#7da067'} roughness={0.94}/></mesh>{[-1,1].map(side=><mesh key={side} position={[0,side*s.height/2,0.16]}><boxGeometry args={[s.width,0.22,0.32]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#aaa396'} roughness={0.91}/></mesh>)}
      {variantId!=='mini_golf_course_v3'&&index===1&&<ParkKitGlb url="/park-kits/mini-golf/mini-golf-windmill.glb" position={[0,0,0.04]} />}
      {variantId!=='mini_golf_course_v3'&&index===3&&<ParkKitGlb url="/park-kits/mini-golf/mini-golf-bridge.glb" position={[0,0,0.04]} yaw={Math.PI / 2} />}
      {variantId!=='mini_golf_course_v3'&&index===4&&<ParkKitGlb url="/park-kits/mini-golf/mini-golf-loop.glb" position={[0,0,0.04]} />}
      {variantId==='mini_golf_course_v3'&&index===0&&<ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.miniGolfHollowLogTunnel.url} position={[0,0,0.04]} yaw={Math.PI/2} />}
      {variantId==='mini_golf_course_v3'&&index===2&&<ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.miniGolfRockObstacle.url} position={[0,0,0.04]} yaw={Math.PI/2} />}
      {variantId==='mini_golf_course_v3'&&index===3&&<ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.miniGolfStumpGate.url} position={[0,0,0.04]} yaw={Math.PI/2} />}
      {index===lanes.length-1&&<ParkKitGlb url="/park-kits/mini-golf/mini-golf-cup-flag.glb" position={[s.width*.32,0,0.04]} />}
    </group>;})}</group>;
  }

  if (familyId === 'park_beach_volleyball_competition_v0') {
    const net = guides.find((guide)=>guide.kind==='line'); if(!net)return null; const r=route(net,frame); if(r.length<2)return null; const mid={x:(r[0].x+r[1].x)/2,y:(r[0].y+r[1].y)/2}; const yaw=Math.atan2(r[1].y-r[0].y,r[1].x-r[0].x); const length=Math.hypot(r[1].x-r[0].x,r[1].y-r[0].y); const z=terrainZ(mid.x,mid.y)+lift;
    return <group position={[mid.x,mid.y,z]} rotation={[0,0,yaw]}>
      <ParkKitGlb url="/park-kits/beach-volleyball/beach-volleyball-net.glb" position={[0,0,0]} />
      <ParkKitGlb url="/park-kits/beach-volleyball/beach-volleyball-referee-stand.glb" position={[length/2+0.85,-0.85,0]} yaw={Math.PI / 2} />
    </group>;
  }

  if (familyId === 'park_pollinator_prairie_v0') {
    const nodes = [{x:frame.minX+frame.width*0.16,y:frame.minY+frame.height*0.20},{x:frame.minX+frame.width*0.82,y:frame.minY+frame.height*0.72}];
    const hotel = { x: frame.minX + frame.width * 0.77, y: frame.minY + frame.height * 0.22 };
    return <group>{nodes.map((p,index)=>{const z=terrainZ(p.x,p.y)+lift;return <group key={index} position={[p.x,p.y,z]}><mesh position={[0,0,0.55]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.05,0.07,1.1,8]}/><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#7a6248'} roughness={0.88}/></mesh><mesh position={[0,0,1.05]} rotation={[0.65,0,0]}><boxGeometry args={[1.15,0.08,0.7]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#a79673'} roughness={0.82}/></mesh></group>;})}
      <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.pollinatorInsectHotel.url} position={[hotel.x, hotel.y, terrainZ(hotel.x, hotel.y) + lift]} yaw={-0.25} />
    </group>;
  }

  if (familyId === 'park_orchard_heritage_v0') {
    const rows=guides.filter((guide)=>guide.kind==='line').slice(1,6);
    const potting = { x: frame.maxX - frame.width * 0.13, y: frame.minY + frame.height * 0.16 };
    return <group>{rows.flatMap((row,rowIndex)=>{const r=route(row,frame);if(r.length<2)return[];const length=Math.hypot(r[1].x-r[0].x,r[1].y-r[0].y);const count=Math.max(4,Math.min(14,Math.floor(length/7)));return Array.from({length:count},(_,index)=>{const t=(index+0.5)/count;const x=r[0].x+(r[1].x-r[0].x)*t;const y=r[0].y+(r[1].y-r[0].y)*t;const z=terrainZ(x,y)+lift;return <group key={`${rowIndex}-${index}`} position={[x,y,z]}><mesh position={[0,0,1.25]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[0.13,0.18,2.5,9]}/><meshStandardMaterial {...timberMaps} color={variantSkin ? '#ffffff' : '#7b5a3e'} roughness={0.95}/></mesh><mesh position={[0,0,2.7]} scale={[1.3,1.1,0.9]}><sphereGeometry args={[1.25,12,8]}/><meshStandardMaterial {...lawnMaps} color={variantSkin ? '#ffffff' : rowIndex%2?'#6a8054':'#74875b'} roughness={0.98}/></mesh>{[-0.6,0.2,0.65].map((offset,fruit)=><mesh key={fruit} position={[offset,fruit*0.25,2.8+fruit*0.15]}><sphereGeometry args={[0.09,8,6]}/><meshStandardMaterial color="#a34532" roughness={0.75}/></mesh>)}</group>;});})}
      <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.productiveGardenPottingBench.url} position={[potting.x, potting.y, terrainZ(potting.x, potting.y) + lift]} yaw={Math.PI} />
    </group>;
  }

  if (familyId === 'park_bioswale_streetside_v0') {
    const crossings=guides.filter((guide)=>guide.kind==='line');
    return <group>{crossings.map((guide,index)=>{const r=route(guide,frame);if(r.length<2)return null;const z=Math.max(terrainZ(r[0].x,r[0].y),terrainZ(r[1].x,r[1].y))+lift+0.12;return <group key={index}><Segment from={r[0]} to={r[1]} width={1.4} height={0.20} z={z} color="#8a775d"/>{[-1,1].map(side=>{const p=r[side===-1?0:1];return <mesh key={side} position={[p.x,p.y,terrainZ(p.x,p.y)+lift+0.04]}><boxGeometry args={[1.2,0.8,0.08]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#756650'} metalness={0.2} roughness={0.72}/></mesh>;})}</group>;})}</group>;
  }

  if (familyId === 'park_sculpture_museum_court_v0') {
    const plinths=guides.filter((guide)=>guide.kind==='rectangle');
    return <group>{plinths.map((guide,index)=>{const c=center(guide,frame);const s=resolveParkGuideDimensionsM(guide,frame);const z=terrainZ(c.x,c.y)+lift;return <group key={index} position={[c.x,c.y,z]}><mesh position={[0,0,0.25]}><boxGeometry args={[s.width,s.height,0.5]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#aaa295'} roughness={0.86}/></mesh>{index%2===0
      ? <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.sculptureCortenLoop.url} position={[0,0,0.5]} yaw={index * 0.31} />
      : <ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.sculptureStonePortal.url} position={[0,0,0.5]} yaw={index * -0.27} />}</group>;})}</group>;
  }

  if (familyId === 'park_labyrinth_classical_v0') {
    const rings=guides.filter((guide)=>guide.kind==='ellipse'); if(rings.length===0)return null; const c=center(rings[0],frame); const z=terrainZ(c.x,c.y)+lift;
    return <group position={[c.x,c.y,z]}>{rings.filter((_,index)=>index%2===1).map((ring,index)=>{const s=resolveParkGuideDimensionsM(ring,frame);return <mesh key={index} position={[0,0,0.32]} scale={[s.width/Math.max(s.height,0.1),1,1]}><torusGeometry args={[s.height/2,0.24,8,64]}/><meshStandardMaterial {...lawnMaps} color={variantSkin ? '#ffffff' : '#5b764a'} roughness={0.97}/></mesh>})}<group position={[0,0,0.45]}><mesh><boxGeometry args={[2.4,0.48,0.18]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#b9b09d'} roughness={0.9}/></mesh>{[-0.85,0.85].map(x=><mesh key={x} position={[x,0,-0.26]}><boxGeometry args={[0.24,0.40,0.52]}/><meshStandardMaterial {...paverMaps} color={variantSkin ? '#ffffff' : '#a79d89'} roughness={0.9}/></mesh>)}</group>{variantId==='labyrinth_meditation_v0'&&<ParkKitGlb url={PARK_MESHY_ARCHETYPE_ASSETS.labyrinthBronzeWaterBowl.url} position={[Math.min(9,frame.width*.22),0,0.12]} />}</group>;
  }

  return null;
}
