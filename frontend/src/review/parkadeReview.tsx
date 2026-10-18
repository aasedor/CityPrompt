/** Standalone DEV model review. No catalogue activation or project mutations. */
import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Html, OrbitControls, useGLTF } from '@react-three/drei';
import { Box3, BufferGeometry, Mesh, Vector3 } from 'three';
import {
  prepareArchitecturalClone, disposeArchitecturalCloneMaterials,
} from '../components/viewer/globe/modelMaterialQuality';
import trial from '../data/parkadeFamilyTrial.json';
const MODELS=trial.assets.map(asset=>({id:asset.id,label:asset.label,url:`/models/parkade-pilot/${asset.model.revision}.glb`,levels:asset.properties.floor_count}));
let START=performance.now();
const VIEWS={
  Oblique: {position:[65,38,75],target:[0,5,0]},
  Front: {position:[0,8,80],target:[0,6,0]},
  Aerial: {position:[45,75,50],target:[0,3,0]},
  Rear: {position:[-60,30,-65],target:[0,5,0]},
  Stairs: {position:[35,7,30],target:[27.5,5,14.5]},
} satisfies Record<string,{position:number[];target:number[]}>;
type View=keyof typeof VIEWS;
function Model({x,z,url,onReady}:{x:number;z:number;url:string;onReady:(text:string)=>void}) {
  const {scene}=useGLTF(url);
  const {gl}=useThree();
  const model=useMemo(()=>{
    return prepareArchitecturalClone(scene,{renderOrder:0,maxAnisotropy:gl.capabilities.getMaxAnisotropy(),
      ambientOcclusion:'disable',preserveSourcePbr:true,restyleUntextured:false});
  },[scene,gl]);
  useEffect(()=>{
    const box=new Box3().setFromObject(model);const size=box.getSize(new Vector3());
    const geometries=new Set<BufferGeometry>();
    model.traverse(object=>{if(object instanceof Mesh)geometries.add(object.geometry);});
    let bytes=0;
    for(const geo of geometries){
      for(const attribute of Object.values(geo.attributes))bytes+=attribute.array.byteLength;
      bytes+=geo.index?.array.byteLength??0;
    }
    if(x===0&&z===0)onReady(`${size.x.toFixed(2)} × ${size.z.toFixed(2)} × ${size.y.toFixed(2)} m · native scale 1 · first model ready ${(performance.now()-START).toFixed(0)} ms · geometry attributes/index ${(bytes/1024).toFixed(0)} KiB (excludes JS/GPU overhead)`);
    return ()=>disposeArchitecturalCloneMaterials(model);
  },[model,onReady,x,z]);
  return <primitive object={model} position={[x,0,z]} dispose={null}/>;
}
function Scene({view,copies,url,onReady,onStats}:{view:View;copies:number;url:string;onReady:(text:string)=>void;onStats:(text:string)=>void}) {
  const {camera,gl}=useThree();
  const timings=useRef<number[]>([]);const elapsed=useRef(0);
  const center=useMemo(()=>copies===1?new Vector3():new Vector3(140,0,copies===20?84:0),[copies]);
  const target=useMemo(()=>new Vector3().fromArray(VIEWS[view].target).add(center),[view,center]);
  useEffect(()=>{
    const scale=copies===1?1:copies===5?4.0:4.8;
    camera.position.fromArray(VIEWS[view].position).multiplyScalar(scale).add(center);
    camera.lookAt(target);camera.updateProjectionMatrix();timings.current=[];elapsed.current=0;
    onStats('Sampling selected grid after camera/copy change…');
  },[camera,view,copies,center,target,onStats]);
  useFrame((_,delta)=>{
    timings.current.push(delta*1000);elapsed.current+=delta;
    if(elapsed.current>=2){
      const sample=timings.current.filter(n=>n<1000).sort((a,b)=>a-b);
      const middle=sample[Math.floor(sample.length*.5)]??0;const p95=sample[Math.floor(sample.length*.95)]??0;
      onStats(`${copies} model(s) · ${gl.info.render.calls} draw calls · ${gl.info.render.triangles.toLocaleString()} triangles · frame median ${middle.toFixed(1)} ms / p95 ${p95.toFixed(1)} ms · ${gl.info.memory.geometries} geometries / ${gl.info.memory.textures} textures · ${gl.domElement.width} × ${gl.domElement.height} buffer`);
      timings.current=[];elapsed.current=0;
    }
  });
  return <>
    <color attach="background" args={['#dbe5e9']}/>
    <ambientLight intensity={.45}/>
    <hemisphereLight args={['#f5f8ff','#b4ae96',.55]}/>
    <directionalLight position={[-40,70,60]} intensity={2.0} castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-55} shadow-camera-right={55} shadow-camera-top={55} shadow-camera-bottom={-55} shadow-camera-far={200} shadow-bias={-.0001}/>
    <directionalLight position={[50,35,-40]} intensity={.5}/>
    <mesh receiveShadow rotation={[-Math.PI/2,0,0]} position={[0,-.015,0]}><planeGeometry args={[800,800]}/><meshStandardMaterial color="#b9b9a8" roughness={1}/></mesh>
    <Suspense fallback={<Html center>Loading exact GLB…</Html>}>
      {Array.from({length:copies},(_,i)=><Model key={`${url}:${i}`} url={url} x={(i%5)*70} z={Math.floor(i/5)*56} onReady={onReady}/>)}
    </Suspense>
    <OrbitControls key={`${view}:${copies}`} makeDefault target={target} maxPolarAngle={Math.PI/2-.01}/>
  </>;
}
function Review(){
  const [modelId,setModelId]=useState(MODELS[0]?.id??'');
  const current=MODELS.find(model=>model.id===modelId)??MODELS[0];
  const [view,setView]=useState<View>('Oblique');const [copies,setCopies]=useState(1);
  const [ready,setReady]=useState('Loading model…');const [stats,setStats]=useState('Sampling browser frames…');
  return <main style={{height:'100%',display:'grid',gridTemplateRows:'auto 1fr auto'}}>
    <header style={{padding:'12px 18px',borderBottom:'2px solid #151515',display:'flex',gap:14,alignItems:'center',flexWrap:'wrap'}}>
      <div><strong>{current?.label??'Parkade family review'}</strong><div style={{fontSize:12,marginTop:4}}>Local pilot · {current?.levels} parking levels · fixed size · DEV catalogue trial · not published</div></div>
      <label>Model <select aria-label="Parkade design" value={modelId} onChange={e=>{START=performance.now();setReady('Loading model...');setModelId(e.target.value);}}>{MODELS.map(model=><option key={model.id} value={model.id}>{model.label}</option>)}</select></label>
      <nav aria-label="Review cameras" style={{display:'flex',gap:6,flexWrap:'wrap'}}>{(Object.keys(VIEWS) as View[]).map(name=><button key={name} aria-pressed={view===name} onClick={()=>setView(name)}>{name}</button>)}</nav>
      <label>Copies <select aria-label="Number of parkade copies" value={copies} onChange={e=>setCopies(Number(e.target.value))}>{[1,5,20].map(n=><option key={n} value={n}>{n}</option>)}</select></label>
    </header>
    <Canvas shadows camera={{position:[65,38,75],fov:45,near:.1,far:1500}} dpr={1} gl={{preserveDrawingBuffer:true}}>
      <Scene key={current?.id} url={current?.url??''} view={view} copies={copies} onReady={setReady} onStats={setStats}/>
    </Canvas>
    <footer style={{padding:'10px 18px',borderTop:'2px solid #151515',fontSize:12,lineHeight:1.7}}>
      <div role="status">{ready}</div><div aria-label="Measured renderer statistics">{stats}</div>
      <div>Drag to orbit · Scroll to zoom · Desktop isolated model measurement, not a student-laptop or full-map benchmark. Concept visualization; no engineering certification.</div>
    </footer>
  </main>;
}
if(import.meta.env.DEV){
  const root=createRoot(document.getElementById('root')!);
  if(import.meta.hot)import.meta.hot.dispose(()=>root.unmount());
  root.render(<Review/>);
}
