import { useEffect, useMemo, type ReactNode } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { Batch10ProgramFrame as ProgramFrame } from './GlobeParkBatch10Assembly';

type Batch11FamilyId = Extract<ParkLegoFamilyId,
  | 'park_paris_place_royale_v2' | 'park_paris_square_tree_grid_v3' | 'park_london_circus_planted_v1'
  | 'park_newyork_pocket_water_v0' | 'park_newyork_community_greenhouse_v3'
  | 'park_vancouver_seawall_cycle_v2' | 'park_vancouver_beach_pavilion_v0'
  | 'park_toronto_ravine_creek_v1' | 'park_toronto_urban_market_v1' | 'park_halifax_coastal_fog_path_v2'>;
const SLUG: Record<Batch11FamilyId,string> = {
  park_paris_place_royale_v2:'paris-place-royale-cobbles-v2', park_paris_square_tree_grid_v3:'paris-square-tree-grid-v3',
  park_london_circus_planted_v1:'london-circus-planted-v1', park_newyork_pocket_water_v0:'new-york-pocket-water-v0',
  park_newyork_community_greenhouse_v3:'new-york-community-greenhouse-v3', park_vancouver_seawall_cycle_v2:'vancouver-seawall-cycle-v2',
  park_vancouver_beach_pavilion_v0:'vancouver-beach-pavilion-v0', park_toronto_ravine_creek_v1:'toronto-ravine-creek-v1',
  park_toronto_urban_market_v1:'toronto-urban-market-v1', park_halifax_coastal_fog_path_v2:'halifax-coastal-fog-path-v2',
};
interface Maps { map:THREE.Texture; normalMap:THREE.Texture; roughnessMap:THREE.Texture; aoMap:THREE.Texture }
function useMaps(slug:string,role:string,repeat=4):Maps { const root=`/park-skins/${slug}/adaptive-v1/${role}`; const source=useTexture({map:`${root}/albedo.jpg`,normalMap:`${root}/normal.png`,roughnessMap:`${root}/roughness.jpg`,aoMap:`${root}/ao.jpg`}); const maps=useMemo(()=>Object.fromEntries(Object.entries(source).map(([k,v])=>{const t=v.clone();t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat,repeat);t.needsUpdate=true;return[k,t]})) as unknown as Maps,[repeat,source]); maps.map.colorSpace=THREE.SRGBColorSpace; useEffect(()=>()=>Object.values(maps).forEach(t=>t.dispose()),[maps]); return maps; }
const pt=(g:ParkGroundGuide,f:ProgramFrame)=>({x:f.minX+f.width*g.x,y:f.maxY-f.height*g.y});
function Segment({a,b,width,z,maps,color}:{a:{x:number;y:number};b:{x:number;y:number};width:number;z:number;maps?:Maps;color:string}) { const len=Math.hypot(b.x-a.x,b.y-a.y); return <mesh position={[(a.x+b.x)/2,(a.y+b.y)/2,z+.09]} rotation={[0,0,Math.atan2(b.y-a.y,b.x-a.x)]}><boxGeometry args={[len,width,.18]}/><meshStandardMaterial {...maps} color={color} roughness={.92}/></mesh>; }
function Tree({x,y,z,coastal=false}:{x:number;y:number;z:number;coastal?:boolean}) { return <group position={[x,y,z]}><mesh position={[0,0,1.7]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.13,.21,3.4,8]}/><meshStandardMaterial color="#58483b" roughness={.98}/></mesh><mesh position={[0,0,coastal?4.0:4.1]} scale={coastal?[.75,.75,1.45]:[1.2,1.1,1]}><dodecahedronGeometry args={[1.35,1]}/><meshStandardMaterial color={coastal?'#425f48':'#55734c'} roughness={.99}/></mesh></group>; }
function Shelter({x,y,z,maps,greenhouse=false}:{x:number;y:number;z:number;maps:Maps;greenhouse?:boolean}) { return <group position={[x,y,z]}>{[-1,1].flatMap(sx=>[-1,1].map(sy=><mesh key={`${sx}-${sy}`} position={[sx*2.2,sy*1.5,1.5]}><boxGeometry args={[.16,.16,3]}/><meshStandardMaterial {...maps} color="#775c43" roughness={.9}/></mesh>))}<mesh position={[0,0,3.1]}><boxGeometry args={[4.8,3.4,.22]}/>{greenhouse?<meshPhysicalMaterial color="#b8cfca" transparent opacity={.55} roughness={.18}/>:<meshStandardMaterial {...maps} color="#856547" roughness={.88}/>}</mesh></group>; }

export function GlobeParkBatch11Assembly({familyId,guides,frame,terrainZ}:{familyId:ParkLegoFamilyId;guides:ParkGroundGuide[];frame:ProgramFrame;terrainZ:(x:number,y:number)=>number}) {
  const id=familyId as Batch11FamilyId, slug=SLUG[id], lift=PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const paver=useMaps(slug,'paver'); const planting=useMaps(slug,'planting',5); const timber=useMaps(slug,'timber'); const safety=useMaps(slug,'safety');
  const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift;
  const paths:ReactNode[]=[]; guides.forEach((g,gi)=>{if(g.kind==='polyline'&&g.points){const ps=g.points.map(([x,y])=>({x:frame.minX+frame.width*x,y:frame.maxY-frame.height*y}));ps.slice(0,-1).forEach((p,i)=>paths.push(<Segment key={`p-${gi}-${i}`} a={p} b={ps[i+1]} width={g.strokeWidthM??3} z={Math.max(terrainZ(p.x,p.y),terrainZ(ps[i+1].x,ps[i+1].y))+lift} maps={g.color==='#587f82'?undefined:paver} color={g.color}/>));}else if(g.kind==='axis'){const c=pt(g,frame),len=Math.max(g.widthM??0,g.heightM??0,g.width*frame.width,g.height*frame.height),a=(g.rotationDeg??90)*Math.PI/180;const p1={x:c.x-Math.cos(a)*len/2,y:c.y-Math.sin(a)*len/2},p2={x:c.x+Math.cos(a)*len/2,y:c.y+Math.sin(a)*len/2};paths.push(<Segment key={`a-${gi}`} a={p1} b={p2} width={g.strokeWidthM??3} z={Math.max(terrainZ(p1.x,p1.y),terrainZ(p2.x,p2.y))+lift} maps={paver} color={g.color}/>);}});
  const pads=guides.filter(g=>['rectangle','rounded_rectangle','ellipse'].includes(g.kind)).map((g,i)=>{const c=pt(g,frame),s=resolveParkGuideDimensionsM(g,frame),z=terrainZ(c.x,c.y)+lift,green=/^#(?:5|6|7|8|9)[0-9a-f]{5}$/i.test(g.color)&&g.color!=='#a8a49b';return <mesh key={i} position={[c.x,c.y,z+.12]} rotation={[0,0,(g.rotationDeg??0)*Math.PI/180]} scale={g.kind==='ellipse'?[s.width/2,s.height/2,1]:[1,1,1]}>{g.kind==='ellipse'?<cylinderGeometry args={[1,1,.24,32]}/>:<boxGeometry args={[s.width,s.height,.24]}/>}<meshStandardMaterial {...(green?planting:paver)} color={g.color} roughness={.93}/></mesh>});
  const coastal=id==='park_halifax_coastal_fog_path_v2'; const treeCount=id.includes('place_royale')?4:id.includes('seawall')?5:Math.min(20,Math.max(6,Math.floor(frame.width*frame.height/900)));
  const shelter=id==='park_newyork_community_greenhouse_v3'||id==='park_newyork_pocket_water_v0'||id==='park_vancouver_beach_pavilion_v0';
  const vendor=id==='park_toronto_urban_market_v1';
  return <group>{pads}{paths}{Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.08+((i*.293)%0.84)),y=frame.minY+frame.height*(.08+((i*.541)%0.84));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} coastal={coastal}/>})}{shelter&&<Shelter x={frame.maxX-frame.width*.22} y={frame.maxY-frame.height*.20} z={terrainZ(frame.maxX-frame.width*.22,frame.maxY-frame.height*.20)+lift} maps={timber} greenhouse={id==='park_newyork_community_greenhouse_v3'}/>} {vendor&&Array.from({length:Math.min(6,Math.max(2,Math.floor(frame.width/16)))},(_,i)=>{const x=frame.minX+frame.width*(.15+i*.7/Math.min(6,Math.max(2,Math.floor(frame.width/16))));return <Shelter key={i} x={x} y={frame.maxY-frame.height*.16} z={terrainZ(x,frame.maxY-frame.height*.16)+lift} maps={timber}/>})}<mesh position={[cx,cy,base-.02]}><boxGeometry args={[.01,.01,.01]}/><meshStandardMaterial {...safety}/></mesh></group>;
}
