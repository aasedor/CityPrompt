import React, {Suspense,useMemo,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Canvas,useThree} from '@react-three/fiber';
import {OrbitControls} from '@react-three/drei';
import * as THREE from 'three';
import {GlobeNeighborhoodParkPilot} from '../components/viewer/globe/GlobeNeighborhoodParkPilot';
import {neighborhoodParkLayoutForZone} from '../components/viewer/globe/neighborhoodParkLayout';
import type {SiteZone} from '../types';
import {METERS_PER_DEG_LAT,metersPerDegLon} from '../components/viewer/mapEngine/geoUtils';

const center={lng:-114.04677,lat:51.04542};
const SHAPES: Record<string,number[][]> = {
  compact:[[-20,-17.5],[20,-17.5],[20,17.5],[-20,17.5]],
  standard:[[-35,-27.5],[35,-27.5],[35,27.5],[-35,27.5]],
  large:[[-52.5,-37.5],[52.5,-37.5],[52.5,37.5],[-52.5,37.5]],
  irregular:[[-40,-30],[40,-30],[40,0],[15,0],[15,30],[-40,30]],
  narrow:[[-4,-40],[4,-40],[4,40],[-4,40]],
};
function Pose({view,scale}:{view:string;scale:number}) {
  const {camera}=useThree();
  React.useEffect(()=>{
    const poses:Record<string,number[]>={aerial:[46*scale,-58*scale,51*scale],overhead:[0,-.01,100*scale],walk:[0,-21,1.8],detail:[-18,-7,6]};
    camera.position.set(...poses[view] as [number,number,number]); camera.up.set(0,0,1);
    camera.lookAt(0,view==='walk'?12:view==='detail'?15:0,view==='walk'?1.7:view==='detail'?1:0);camera.updateProjectionMatrix();
  },[camera,view,scale]);
  return null;
}
function App(){
  const [size,setSize]=useState('standard'),[slope,setSlope]=useState(false),[view,setView]=useState('aerial');
  const zone=useMemo<SiteZone>(()=>({id:'review-park',project_id:'local-pilot',zone_type:'green_space',color:'#718456',sort_order:0,created_at:'2026-09-05',updated_at:'2026-09-05',
    coordinates:SHAPES[size].map(([x,y])=>{
      const angle=size==='irregular'?.38:0, east=x*Math.cos(angle)-y*Math.sin(angle), north=x*Math.sin(angle)+y*Math.cos(angle);
      return [center.lng+east/metersPerDegLon(center.lat),center.lat+north/METERS_PER_DEG_LAT];
    }),
    properties:{green_space_archetype_id:'neighborhood_park',green_space_selected_variant_id:'neighborhood_park_v0',neighborhood_park_layout:'adaptive_rustic_v1'}}),[size]);
  const layout=useMemo(()=>neighborhoodParkLayoutForZone(zone,center),[zone]);
  const ground=useMemo(()=>(x:number,y:number)=>slope ? .03*x+.008*y : 0,[slope]);
  const floor=useMemo(()=>{
    const geometry=new THREE.PlaneGeometry(350,350);
    const points=geometry.getAttribute('position');
    for(let i=0;i<points.count;i++)points.setZ(i,ground(points.getX(i),points.getY(i))-.015);
    geometry.computeVertexNormals();return geometry;
  },[ground]);
  React.useEffect(()=>()=>floor.dispose(),[floor]);
  const labels={compact:'40 × 35 m · compact',standard:'70 × 55 m · full programme',large:'105 × 75 m · large',irregular:'Rotated L-shaped site',narrow:'8 × 80 m · too narrow'};
  const scale=size==='large'?1.35:size==='compact'?.75:1;
  return <main style={{fontFamily:'Arial,sans-serif',height:'100vh',background:'#f6f4eb',color:'#203529',display:'flex',flexDirection:'column'}}>
    <header style={{padding:'20px 28px',display:'flex',alignItems:'center',justifyContent:'space-between',borderBottom:'1px solid #ccd1c2'}}>
      <div><div style={{fontSize:11,letterSpacing:2,fontWeight:700}}>CITY PROMPT · LANDSCAPE LAB</div><h1 style={{fontSize:25,margin:'7px 0 0'}}>A park that fits the place.</h1></div>
      <div style={{fontSize:12,maxWidth:300,lineHeight:1.5}}>Neighbourhood park / rustic timber<br/>Local candidate · September 2026</div>
    </header>
    <section style={{display:'flex',gap:12,padding:'12px 28px',alignItems:'center',flexWrap:'wrap'}}>
      <label>Site size <select aria-label="Site size" value={size} onChange={e=>setSize(e.target.value)} style={{marginLeft:8,padding:9,borderRadius:6}}>{Object.entries(labels).map(([id,label])=><option key={id} value={id}>{label}</option>)}</select></label>
      <label style={{marginRight:18}}><input type="checkbox" checked={slope} onChange={e=>setSlope(e.target.checked)}/> Test sloping ground</label>
      {['aerial','overhead','walk','detail'].map(id=><button key={id} onClick={()=>setView(id)} style={{padding:'10px 15px',border:'1px solid #60775b',background:view===id?'#304d36':'transparent',color:view===id?'white':'#304d36',borderRadius:6,cursor:'pointer',textTransform:'capitalize'}}>{id==='walk'?'Pedestrian view':id}</button>)}
    </section>
    <div style={{flex:1,minHeight:0}}>
      <Canvas shadows camera={{position:[65,-85,75],up:[0,0,1],near:.1,far:500,fov:48}} gl={{antialias:true,preserveDrawingBuffer:true,logarithmicDepthBuffer:true}} onCreated={({gl,scene,camera})=>{
        gl.toneMapping=THREE.ACESFilmicToneMapping;gl.toneMappingExposure=1.1;
        Object.assign(window,{__parkReview:{gl,scene,camera}});
      }}>
        <color attach="background" args={['#dde7df']}/><fog attach="fog" args={['#dde7df',150,380]}/>
        <ambientLight intensity={.7}/><hemisphereLight args={['#eaf3ff','#66764b',1.3]}/>
        <directionalLight position={[-35,-25,80]} intensity={3} castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-80} shadow-camera-right={80} shadow-camera-top={80} shadow-camera-bottom={-80} shadow-camera-far={250} shadow-normalBias={.04}/>
        <Suspense fallback={null}><GlobeNeighborhoodParkPilot zone={zone} centroid={center} terrainZ={ground}/></Suspense>
        <mesh geometry={floor} receiveShadow><meshStandardMaterial color="#b7b59b" roughness={1}/></mesh>
        <Pose view={view} scale={scale}/><OrbitControls key={`${view}-${size}`} makeDefault target={view==='walk'?[0,12,1.7]:view==='detail'?[0,15,1]:[0,0,0]} enableDamping={false} maxPolarAngle={Math.PI*.49}/>
      </Canvas>
    </div>
    <footer style={{padding:'14px 28px',fontSize:13,lineHeight:1.6,borderTop:'1px solid #ccd1c2',display:'flex',justifyContent:'space-between',gap:24}}>
      <div><strong>{layout.status==='full'?'Full programme':layout.status==='compact'?'Compact arrangement':'Footprint needs review'}</strong><br/>{layout.notes.join(' ')}</div>
      <div style={{maxWidth:380,color:'#5b695c'}}>Drag to orbit · Scroll to zoom<br/>This page inspects the actual park geometry. The Google tiles integration is in the separate local project.</div>
    </footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
