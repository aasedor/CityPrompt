import { useEffect, useMemo, type ReactNode } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { ParkLegoFamilyId } from './parkLegoFamilies';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { Batch10ProgramFrame as ProgramFrame } from './GlobeParkBatch10Assembly';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { batch24ParkSkinForSelection } from './parkBatch24Skins';

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
function CafeTable({x,y,z,maps}:{x:number;y:number;z:number;maps:Maps}) { return <group><mesh position={[x,y,z+.72]}><cylinderGeometry args={[.5,.5,.10,18]}/><meshStandardMaterial {...maps} color="#ffffff" roughness={.9}/></mesh><mesh position={[x,y,z+.36]}><cylinderGeometry args={[.06,.08,.68,8]}/><meshStandardMaterial color="#343936" metalness={.55} roughness={.5}/></mesh></group>; }
function Bench({x,y,z,rotation=0,maps}:{x:number;y:number;z:number;rotation?:number;maps:Maps}) { return <group position={[x,y,z]} rotation={[0,0,rotation]}><mesh position={[0,0,.56]}><boxGeometry args={[2.2,.62,.14]}/><meshStandardMaterial {...maps} color="#ffffff" roughness={.94}/></mesh>{[-.78,.78].map(s=><mesh key={s} position={[s,0,.28]}><boxGeometry args={[.12,.52,.56]}/><meshStandardMaterial color="#333735" metalness={.5}/></mesh>)}</group>; }
function RaisedBed({x,y,z,width,depth,maps}:{x:number;y:number;z:number;width:number;depth:number;maps:Maps}) { return <group><mesh position={[x,y,z+.32]}><boxGeometry args={[width,depth,.64]}/><meshStandardMaterial {...maps} color="#ffffff" roughness={.95}/></mesh>{Array.from({length:5},(_,i)=><mesh key={i} position={[x-width*.34+i*width*.17,y,z+.82]} scale={[.45,.72,.38]}><dodecahedronGeometry args={[Math.min(.65,depth*.28),1]}/><meshStandardMaterial color={['#4c7047','#667a45','#8a6b43'][i%3]} roughness={.99}/></mesh>)}</group>; }

export function GlobeParkBatch11Assembly({familyId,archetypeId,variantId,guides,frame,terrainZ}:{familyId:ParkLegoFamilyId;archetypeId?:string;variantId?:string;guides:ParkGroundGuide[];frame:ProgramFrame;terrainZ:(x:number,y:number)=>number}) {
  const id=familyId as Batch11FamilyId, variantSkin=batch24ParkSkinForSelection(archetypeId??'',variantId??'')??batch23ParkSkinForSelection(archetypeId??'',variantId??''), slug=variantSkin?.slug??SLUG[id], lift=PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS; const paver=useMaps(slug,'paver'); const planting=useMaps(slug,'planting',5); const timber=useMaps(slug,'timber'); const safety=useMaps(slug,'safety');
  const cx=frame.minX+frame.width/2,cy=frame.minY+frame.height/2,base=terrainZ(cx,cy)+lift;
  if (id==='park_paris_place_royale_v2'&&variantId&&variantId!=='parisian_place_v2') {
    const statue=variantId==='parisian_place_v1',cafe=variantId==='parisian_place_v3';
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.94,frame.height*.90,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {statue&&<group position={[cx,cy,base+.22]}><mesh position={[0,0,.45]}><cylinderGeometry args={[1.45,1.65,.9,20]}/><meshStandardMaterial {...paver} color="#ffffff"/></mesh><mesh position={[0,0,1.65]}><boxGeometry args={[.7,.7,1.5]}/><meshStandardMaterial color="#4d5a54" metalness={.35} roughness={.62}/></mesh></group>}
      {statue&&<Segment a={{x:cx,y:frame.minY+frame.height*.08}} b={{x:cx,y:frame.maxY-frame.height*.08}} width={3} z={base+.22} maps={paver} color="#ffffff"/>}
      {Array.from({length:cafe?9:4},(_,i)=>{if(cafe){const cols=3,x=cx+(i%cols-1)*frame.width*.18,y=cy+(Math.floor(i/cols)-1)*frame.height*.18;return <CafeTable key={i} x={x} y={y} z={terrainZ(x,y)+lift+.22} maps={timber}/>;}const a=i*Math.PI/2,x=cx+Math.cos(a)*frame.width*.34,y=cy+Math.sin(a)*frame.height*.31;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift}/>;})}
    </group>;
  }
  if (id==='park_paris_square_tree_grid_v3'&&variantId&&variantId!=='parisian_square_v3') {
    const cafe=variantId==='parisian_square_v1',compact=variantId==='parisian_square_v2';
    const treeCount=compact?4:cafe?5:Math.min(9,Math.max(4,Math.floor(frame.width/8)));
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.92,frame.height*.88,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {Array.from({length:treeCount},(_,i)=>{const x=variantId==='parisian_square_v0'?frame.minX+frame.width*(.12+i*.76/Math.max(1,treeCount-1)):cx+(i%2?1:-1)*frame.width*.27,y=variantId==='parisian_square_v0'?frame.minY+frame.height*.18:cy+(Math.floor(i/2)-.5)*frame.height*.26;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift}/>;})}
      {cafe&&Array.from({length:6},(_,i)=>{const x=frame.maxX-frame.width*(.12+(i%2)*.10),y=frame.maxY-frame.height*(.14+Math.floor(i/2)*.12);return <CafeTable key={i} x={x} y={y} z={terrainZ(x,y)+lift+.22} maps={timber}/>})}
      {compact&&<mesh position={[cx,cy,base+.42]}><cylinderGeometry args={[1.8,2.1,.62,20]}/><meshStandardMaterial {...planting} color="#ffffff" roughness={.98}/></mesh>}
    </group>;
  }
  if (id==='park_london_circus_planted_v1'&&variantId&&variantId!=='london_circus_v1') {
    const round=variantId==='london_circus_v0',side=variantId==='london_circus_v2';
    const radius=Math.min(frame.width,frame.height)*(round?.24:.18);
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.94,frame.height*.90,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      {round&&<group><mesh position={[cx,cy,base+.28]}><cylinderGeometry args={[radius,radius,.34,36]}/><meshStandardMaterial {...planting} color="#ffffff" roughness={.98}/></mesh><mesh position={[cx,cy,base+.48]}><torusGeometry args={[radius*.94,.10,8,48]}/><meshStandardMaterial color="#2d322f" metalness={.45}/></mesh></group>}
      {side&&Array.from({length:5},(_,i)=>{const x=frame.minX+frame.width*(.15+i*.70/4),y=frame.minY+frame.height*(i%2?.24:.76),z=terrainZ(x,y)+lift;return <group key={i}><RaisedBed x={x} y={y} z={z+.22} width={Math.min(4,frame.width*.14)} depth={1.4} maps={paver}/><Tree x={x} y={y} z={z+1.3}/></group>})}
      {!round&&!side&&<Segment a={{x:frame.minX+frame.width*.06,y:cy}} b={{x:frame.maxX-frame.width*.06,y:cy}} width={Math.min(6,frame.height*.24)} z={base+.22} maps={paver} color="#ffffff"/>}
      {Array.from({length:round?6:side?4:3},(_,i)=>{const a=i*Math.PI*2/(round?6:Math.max(1,side?4:3));const x=round?cx+Math.cos(a)*radius*1.45:frame.minX+frame.width*(.22+i*.56/Math.max(1,(side?3:2)));const y=round?cy+Math.sin(a)*radius*1.45:cy+(side?(i%2?1:-1)*frame.height*.16:frame.height*.18);return <Bench key={i} x={x} y={y} z={terrainZ(x,y)+lift+.22} rotation={round?a+Math.PI/2:0} maps={timber}/>})}
      {round&&Array.from({length:4},(_,i)=>{const a=i*Math.PI/2;const x=cx+Math.cos(a)*radius*.52,y=cy+Math.sin(a)*radius*.52;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift+.4}/>})}
    </group>;
  }
  if (id==='park_newyork_community_greenhouse_v3'&&variantId&&variantId!=='newyork_community_garden_v3') {
    const shed=variantId==='newyork_community_garden_v2';
    const cols=Math.min(5,Math.max(2,Math.floor(frame.width/7))),rows=Math.min(4,Math.max(2,Math.floor(frame.height/8)));
    return <group>
      <mesh position={[cx,cy,base+.10]}><boxGeometry args={[frame.width*.94,frame.height*.90,.20]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.96}/></mesh>
      {Array.from({length:cols*rows},(_,i)=>{const x=frame.minX+frame.width*(.10+(i%cols+.5)*.80/cols),y=frame.minY+frame.height*(.12+(Math.floor(i/cols)+.5)*.76/rows),z=terrainZ(x,y)+lift;return <RaisedBed key={i} x={x} y={y} z={z+.20} width={Math.min(4.8,frame.width*.68/cols)} depth={Math.min(2.7,frame.height*.60/rows)} maps={timber}/>})}
      <Segment a={{x:frame.minX+frame.width*.06,y:cy}} b={{x:frame.maxX-frame.width*.06,y:cy}} width={1.8} z={base+.22} maps={paver} color="#ffffff"/>
      {shed&&<Shelter x={frame.maxX-frame.width*.15} y={frame.maxY-frame.height*.15} z={terrainZ(frame.maxX-frame.width*.15,frame.maxY-frame.height*.15)+lift+.2} maps={timber}/>}
      {Array.from({length:4},(_,i)=>{const x=frame.minX+frame.width*(.10+i*.80/3),y=frame.maxY-frame.height*.08;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift+.2}/>})}
    </group>;
  }
  if (id==='park_newyork_pocket_water_v0'&&variantId&&variantId!=='newyork_pocket_park_v0') {
    const linear=variantId==='newyork_pocket_park_v1',brick=variantId==='newyork_pocket_park_v2';
    const count=linear?7:brick?6:5;
    return <group>
      <mesh position={[cx,cy,base+.11]}><boxGeometry args={[frame.width*.94,frame.height*.90,.22]}/><meshStandardMaterial {...paver} color="#ffffff" roughness={.94}/></mesh>
      <Segment a={{x:frame.minX+frame.width*.06,y:cy}} b={{x:frame.maxX-frame.width*.06,y:cy}} width={linear?3.2:4.2} z={base+.22} maps={paver} color="#ffffff"/>
      {Array.from({length:count},(_,i)=>{const x=linear?frame.minX+frame.width*(.10+i*.80/Math.max(1,count-1)):frame.minX+frame.width*(.14+((i*.39)%.72));const y=linear?cy+(i%2?1:-1)*frame.height*.26:frame.minY+frame.height*(.18+((i*.57)%.64));const z=terrainZ(x,y)+lift;return <group key={i}><RaisedBed x={x} y={y} z={z+.22} width={brick?3.8:3.2} depth={brick?1.7:1.4} maps={brick?paver:timber}/>{i%2===0&&<Tree x={x} y={y} z={z+1.3}/>}<Bench x={x} y={y+(i%2?1.8:-1.8)} z={z+.22} maps={timber}/></group>})}
      {linear&&<Shelter x={frame.maxX-frame.width*.18} y={cy} z={terrainZ(frame.maxX-frame.width*.18,cy)+lift+.22} maps={timber}/>}
    </group>;
  }
  if (id==='park_halifax_coastal_fog_path_v2'&&variantId&&variantId!=='halifax_coastal_park_v2') {
    const boardwalk=variantId==='halifax_coastal_park_v3',summer=variantId==='halifax_coastal_park_v1';
    const a={x:frame.minX+frame.width*.06,y:frame.minY+frame.height*(boardwalk?.28:.22)},b={x:frame.maxX-frame.width*.06,y:frame.maxY-frame.height*(boardwalk?.20:.26)};
    return <group>
      <mesh position={[cx,cy,base+.10]}><boxGeometry args={[frame.width*.94,frame.height*.90,.20]}/><meshStandardMaterial {...planting} color="#ffffff" roughness={.98}/></mesh>
      <Segment a={a} b={b} width={boardwalk?3.4:3.0} z={base+(boardwalk?.34:.20)} maps={boardwalk?timber:paver} color="#ffffff"/>
      {boardwalk&&<><Segment a={{x:a.x,y:a.y+1.8}} b={{x:b.x,y:b.y+1.8}} width={.10} z={base+1.12} color="#3f4542"/><Segment a={{x:a.x,y:a.y-1.8}} b={{x:b.x,y:b.y-1.8}} width={.10} z={base+1.12} color="#3f4542"/></>}
      {Array.from({length:summer?14:18},(_,i)=>{const x=frame.minX+frame.width*(.05+((i*.293)%.90)),y=frame.minY+frame.height*(.06+((i*.541)%.88));if(Math.abs((y-a.y)-((b.y-a.y)*(x-a.x)/(b.x-a.x)))<4)return null;return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift+.2} coastal/>})}
      {Array.from({length:4},(_,i)=>{const x=frame.minX+frame.width*(.18+i*.64/3),y=a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x);return <Bench key={i} x={x} y={y+(i%2?2.4:-2.4)} z={terrainZ(x,y)+lift+.22} rotation={Math.atan2(b.y-a.y,b.x-a.x)} maps={timber}/>})}
    </group>;
  }
  const paths:ReactNode[]=[]; guides.forEach((g,gi)=>{if(g.kind==='polyline'&&g.points){const ps=g.points.map(([x,y])=>({x:frame.minX+frame.width*x,y:frame.maxY-frame.height*y}));ps.slice(0,-1).forEach((p,i)=>paths.push(<Segment key={`p-${gi}-${i}`} a={p} b={ps[i+1]} width={g.strokeWidthM??3} z={Math.max(terrainZ(p.x,p.y),terrainZ(ps[i+1].x,ps[i+1].y))+lift} maps={g.color==='#587f82'?undefined:paver} color={g.color}/>));}else if(g.kind==='axis'){const c=pt(g,frame),len=Math.max(g.widthM??0,g.heightM??0,g.width*frame.width,g.height*frame.height),a=(g.rotationDeg??90)*Math.PI/180;const p1={x:c.x-Math.cos(a)*len/2,y:c.y-Math.sin(a)*len/2},p2={x:c.x+Math.cos(a)*len/2,y:c.y+Math.sin(a)*len/2};paths.push(<Segment key={`a-${gi}`} a={p1} b={p2} width={g.strokeWidthM??3} z={Math.max(terrainZ(p1.x,p1.y),terrainZ(p2.x,p2.y))+lift} maps={paver} color={g.color}/>);}});
  const pads=guides.filter(g=>['rectangle','rounded_rectangle','ellipse'].includes(g.kind)).map((g,i)=>{const c=pt(g,frame),s=resolveParkGuideDimensionsM(g,frame),z=terrainZ(c.x,c.y)+lift,green=/^#(?:5|6|7|8|9)[0-9a-f]{5}$/i.test(g.color)&&g.color!=='#a8a49b';return <mesh key={i} position={[c.x,c.y,z+.12]} rotation={[0,0,(g.rotationDeg??0)*Math.PI/180]} scale={g.kind==='ellipse'?[s.width/2,s.height/2,1]:[1,1,1]}>{g.kind==='ellipse'?<cylinderGeometry args={[1,1,.24,32]}/>:<boxGeometry args={[s.width,s.height,.24]}/>}<meshStandardMaterial {...(green?planting:paver)} color={g.color} roughness={.93}/></mesh>});
  const coastal=id==='park_halifax_coastal_fog_path_v2'; const treeCount=id.includes('place_royale')?4:id.includes('seawall')?5:Math.min(20,Math.max(6,Math.floor(frame.width*frame.height/900)));
  const shelter=id==='park_newyork_community_greenhouse_v3'||id==='park_newyork_pocket_water_v0'||id==='park_vancouver_beach_pavilion_v0';
  const vendor=id==='park_toronto_urban_market_v1';
  return <group>{pads}{paths}{Array.from({length:treeCount},(_,i)=>{const x=frame.minX+frame.width*(.08+((i*.293)%0.84)),y=frame.minY+frame.height*(.08+((i*.541)%0.84));return <Tree key={i} x={x} y={y} z={terrainZ(x,y)+lift} coastal={coastal}/>})}{shelter&&<Shelter x={frame.maxX-frame.width*.22} y={frame.maxY-frame.height*.20} z={terrainZ(frame.maxX-frame.width*.22,frame.maxY-frame.height*.20)+lift} maps={timber} greenhouse={id==='park_newyork_community_greenhouse_v3'}/>} {vendor&&Array.from({length:Math.min(6,Math.max(2,Math.floor(frame.width/16)))},(_,i)=>{const x=frame.minX+frame.width*(.15+i*.7/Math.min(6,Math.max(2,Math.floor(frame.width/16))));return <Shelter key={i} x={x} y={frame.maxY-frame.height*.16} z={terrainZ(x,frame.maxY-frame.height*.16)+lift} maps={timber}/>})}<mesh position={[cx,cy,base-.02]}><boxGeometry args={[.01,.01,.01]}/><meshStandardMaterial {...safety}/></mesh></group>;
}
