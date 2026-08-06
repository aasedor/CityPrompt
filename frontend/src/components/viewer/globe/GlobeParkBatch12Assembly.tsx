import { useEffect, useMemo, type ReactNode } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { Batch10ProgramFrame as ProgramFrame } from './GlobeParkBatch10Assembly';

type FamilyId = Extract<ParkLegoFamilyId,
  | 'park_city_hall_modernist_fountain_v2' | 'park_cathedral_courtyard_fountain_v3'
  | 'park_cultural_museum_terrace_v0' | 'park_transit_green_civic_v2'
  | 'park_amphitheater_terraced_v0' | 'park_concert_timber_lawn_v2'
  | 'park_night_market_hawker_v0' | 'park_parade_national_mall_v3'
  | 'park_canal_ecological_wetland_v3' | 'park_custom_biophilic_urban_v1'>;

const SLUG: Record<FamilyId,string> = {
  park_city_hall_modernist_fountain_v2:'city-hall-modernist-fountain-v2', park_cathedral_courtyard_fountain_v3:'cathedral-mosque-courtyard-v3',
  park_cultural_museum_terrace_v0:'cultural-museum-terrace-v0', park_transit_green_civic_v2:'transit-green-civic-v2',
  park_amphitheater_terraced_v0:'amphitheater-terraced-v0', park_concert_timber_lawn_v2:'concert-timber-lawn-v2',
  park_night_market_hawker_v0:'night-market-hawker-v0', park_parade_national_mall_v3:'parade-national-mall-v3',
  park_canal_ecological_wetland_v3:'canal-ecological-wetland-v3', park_custom_biophilic_urban_v1:'custom-biophilic-urban-v1',
};
interface Maps { map:THREE.Texture; normalMap:THREE.Texture; roughnessMap:THREE.Texture; aoMap:THREE.Texture }
function useMaps(slug:string,role:string,repeat=4):Maps { const root=`/park-skins/${slug}/adaptive-v1/${role}`; const source=useTexture({map:`${root}/albedo.jpg`,normalMap:`${root}/normal.png`,roughnessMap:`${root}/roughness.jpg`,aoMap:`${root}/ao.jpg`}); const maps=useMemo(()=>Object.fromEntries(Object.entries(source).map(([k,v])=>{const t=v.clone();t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat,repeat);t.needsUpdate=true;return[k,t]})) as unknown as Maps,[repeat,source]); maps.map.colorSpace=THREE.SRGBColorSpace; useEffect(()=>()=>Object.values(maps).forEach(t=>t.dispose()),[maps]); return maps; }
const point=(g:ParkGroundGuide,f:ProgramFrame)=>({x:f.minX+f.width*g.x,y:f.maxY-f.height*g.y});
function Segment({a,b,width,z,maps,color}:{a:{x:number;y:number};b:{x:number;y:number};width:number;z:number;maps?:Maps;color:string}) { const len=Math.hypot(b.x-a.x,b.y-a.y); return <mesh position={[(a.x+b.x)/2,(a.y+b.y)/2,z+.09]} rotation={[0,0,Math.atan2(b.y-a.y,b.x-a.x)]}><boxGeometry args={[len,width,.18]}/><meshStandardMaterial {...maps} color={color} roughness={.92}/></mesh>; }
function Tree({x,y,z}:{x:number;y:number;z:number}) { return <group position={[x,y,z]}><mesh position={[0,0,1.55]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.12,.19,3.1,8]}/><meshStandardMaterial color="#554638" roughness={.98}/></mesh><mesh position={[0,0,3.7]} scale={[1.05,.95,1.05]}><dodecahedronGeometry args={[1.25,1]}/><meshStandardMaterial color="#526f49" roughness={.99}/></mesh></group>; }
function Canopy({x,y,z,w=6,d=3,maps}:{x:number;y:number;z:number;w?:number;d?:number;maps:Maps}) { return <group position={[x,y,z]}>{[-1,1].flatMap(sx=>[-1,1].map(sy=><mesh key={`${sx}-${sy}`} position={[sx*w*.42,sy*d*.38,1.45]}><boxGeometry args={[.15,.15,2.9]}/><meshStandardMaterial {...maps} color="#72533e"/></mesh>))}<mesh position={[0,0,3]}><boxGeometry args={[w,d,.24]}/><meshStandardMaterial {...maps} color="#77543a"/></mesh></group>; }
function Fountain({x,y,z,wide=false}:{x:number;y:number;z:number;wide?:boolean}) { return <group position={[x,y,z]}><mesh><boxGeometry args={[wide?10:4,wide?2.2:4,.45]}/><meshStandardMaterial color="#b8afa2" roughness={.86}/></mesh><mesh position={[0,0,.25]}><boxGeometry args={[wide?9.4:3.4,wide?1.6:3.4,.10]}/><meshPhysicalMaterial color="#4f8790" roughness={.2} metalness={.05}/></mesh></group>; }
function Stall({x,y,z,flip,maps}:{x:number;y:number;z:number;flip:boolean;maps:Maps}) { return <group position={[x,y,z]} rotation={[0,0,flip?Math.PI:0]}><Canopy x={0} y={0} z={0} w={4.2} d={2.5} maps={maps}/><mesh position={[0,-.45,1.15]}><boxGeometry args={[3.8,.65,1.4]}/><meshStandardMaterial {...maps} color={flip?'#a85c3f':'#5b7782'}/></mesh><mesh position={[0,-1.45,2.15]} rotation={[.35,0,0]}><boxGeometry args={[4.1,1.5,.12]}/><meshStandardMaterial color={flip?'#d08a51':'#d4b46b'} roughness={.9}/></mesh></group>; }

export function GlobeParkBatch12Assembly({familyId,guides,frame,terrainZ}:{familyId:ParkLegoFamilyId;guides:ParkGroundGuide[];frame:ProgramFrame;terrainZ:(x:number,y:number)=>number}) {
  const id=familyId as FamilyId,slug=SLUG[id],lift=PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,paver=useMaps(slug,'paver'),planting=useMaps(slug,'planting',5),timber=useMaps(slug,'timber'),safety=useMaps(slug,'safety');
  const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift; const paths:ReactNode[]=[];
  guides.forEach((g,gi)=>{if(g.kind==='polyline'&&g.points){const ps=g.points.map(([x,y])=>({x:frame.minX+frame.width*x,y:frame.maxY-frame.height*y}));ps.slice(0,-1).forEach((p,i)=>paths.push(<Segment key={`p-${gi}-${i}`} a={p} b={ps[i+1]} width={g.strokeWidthM??3} z={Math.max(terrainZ(p.x,p.y),terrainZ(ps[i+1].x,ps[i+1].y))+lift} maps={g.color.startsWith('#5')?undefined:paver} color={g.color}/>));}else if(g.kind==='axis'){const c=point(g,frame),len=Math.max(g.widthM??0,g.heightM??0,g.width*frame.width,g.height*frame.height),a=(g.rotationDeg??90)*Math.PI/180,p1={x:c.x-Math.cos(a)*len/2,y:c.y-Math.sin(a)*len/2},p2={x:c.x+Math.cos(a)*len/2,y:c.y+Math.sin(a)*len/2};paths.push(<Segment key={`a-${gi}`} a={p1} b={p2} width={g.strokeWidthM??3} z={Math.max(terrainZ(p1.x,p1.y),terrainZ(p2.x,p2.y))+lift} maps={paver} color={g.color}/>);}});
  const pads=guides.filter(g=>['rectangle','rounded_rectangle','ellipse'].includes(g.kind)).map((g,i)=>{const c=point(g,frame),s=resolveParkGuideDimensionsM(g,frame),z=terrainZ(c.x,c.y)+lift,green=['#5','#6','#7'].includes(g.color.slice(0,2));return <mesh key={i} position={[c.x,c.y,z+.12]} rotation={g.kind==='ellipse'?[Math.PI/2,0,(g.rotationDeg??0)*Math.PI/180]:[0,0,(g.rotationDeg??0)*Math.PI/180]} scale={g.kind==='ellipse'?[s.width/2,s.height/2,1]:[1,1,1]}>{g.kind==='ellipse'?<cylinderGeometry args={[1,1,.24,36]}/>:<boxGeometry args={[s.width,s.height,.24]}/>}<meshStandardMaterial {...(green?planting:paver)} color={g.color} roughness={.93}/></mesh>});
  const trees=Array.from({length:Math.min(22,Math.max(6,Math.floor(frame.width*frame.height/800)))},(_,i)=>{const edge=i%2===0,x=frame.minX+frame.width*(edge?(.07+(i%4)*.29):(.12+((i*.37)%.76))),y=frame.minY+frame.height*(edge?(.08+((i*.47)%.84)):(.08+(i%3)*.42));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift}/>});
  const extras:ReactNode[]=[];
  if(id==='park_city_hall_modernist_fountain_v2') extras.push(<Fountain key="f" x={cx} y={cy} z={base+.18} wide/>);
  if(id==='park_cathedral_courtyard_fountain_v3') extras.push(<Fountain key="f" x={cx} y={cy} z={base+.18}/>);
  if(id==='park_cultural_museum_terrace_v0') [0,1,2].forEach(i=>extras.push(<mesh key={i} position={[cx,frame.maxY-frame.height*(.31+i*.045),base+.12+i*.18]}><boxGeometry args={[frame.width*.66,2.2,.35]}/><meshStandardMaterial {...paver} color="#aaa69f"/></mesh>));
  if(id==='park_transit_green_civic_v2') [-1,1].forEach(s=>extras.push(<Canopy key={s} x={cx+s*frame.width*.24} y={frame.maxY-frame.height*.23} z={base} w={Math.min(7,frame.width*.18)} d={2.6} maps={timber}/>));
  if(id==='park_amphitheater_terraced_v0') [0,1,2].forEach(i=>extras.push(<mesh key={i} position={[cx,cy+i*frame.height*.025,base+.12+i*.32]} rotation={[Math.PI/2,0,0]} scale={[frame.width*(.33-i*.06),frame.height*(.26-i*.05),1]}><cylinderGeometry args={[1,1,.35,48]}/><meshStandardMaterial {...(i===0?planting:paver)} color={i===0?'#708755':'#8b816f'}/></mesh>));
  if(id==='park_concert_timber_lawn_v2') extras.push(<Canopy key="stage" x={cx} y={frame.maxY-frame.height*.19} z={base} w={Math.min(12,frame.width*.28)} d={Math.min(7,frame.height*.16)} maps={timber}/>);
  if(id==='park_night_market_hawker_v0'){const n=Math.min(8,Math.max(3,Math.floor(frame.width/12)));for(let i=0;i<n;i++){const x=frame.minX+frame.width*(.12+i*.76/Math.max(1,n-1));extras.push(<Stall key={`a${i}`} x={x} y={frame.maxY-frame.height*.22} z={terrainZ(x,frame.maxY-frame.height*.22)+lift} flip={false} maps={timber}/>,<Stall key={`b${i}`} x={x} y={frame.minY+frame.height*.22} z={terrainZ(x,frame.minY+frame.height*.22)+lift} flip maps={timber}/>);}}
  if(id==='park_parade_national_mall_v3') extras.push(<Fountain key="water" x={cx} y={cy} z={base+.18} wide/>);
  if(id==='park_canal_ecological_wetland_v3') [-.18,.18].forEach((d,i)=>extras.push(<mesh key={i} position={[cx+d*frame.width,cy,base+.4]}><boxGeometry args={[2.4,Math.min(16,frame.height*.45),.35]}/><meshStandardMaterial {...timber} color="#76583f"/></mesh>));
  return <group>{pads}{paths}{trees}{extras}<mesh position={[cx,cy,base-.02]}><boxGeometry args={[.01,.01,.01]}/><meshStandardMaterial {...safety}/></mesh></group>;
}
