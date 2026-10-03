import { Suspense, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { NativeParkModel } from '@/features/parks/NativeParkLayer';
import { nativeParkLayouts, type NativeParkLayout } from '@/features/parks/nativeParkRegistry';

if (!import.meta.env.DEV) throw new Error('The park review fixture is development-only.');
const choices=nativeParkLayouts.filter(p=>p.status==='pilot');
function Pose({layout,view}:{layout:NativeParkLayout;view:string}) {
  const {camera}=useThree();
  useEffect(()=>{
    camera.up.set(0,0,1);
    const size=Math.max(layout.widthM,layout.depthM);
    if(view==='walk'){camera.position.set(0,-layout.depthM/2-5,1.7);camera.lookAt(0,0,1.7);}
    else if(view==='overhead'){camera.position.set(0,-.01,size*1.3);camera.lookAt(0,0,0);}
    else {camera.position.set(size*.65,-size*.85,size*.8);camera.lookAt(0,0,0);}
    camera.updateProjectionMatrix();
  },[camera,layout,view]);
  return null;
}
function Ready({layout}:{layout:NativeParkLayout}) {
  useEffect(()=>{document.documentElement.dataset.parkReady=layout.id;return()=>{delete document.documentElement.dataset.parkReady;};},[layout]);
  return null;
}
function App(){
  const [id,setId]=useState('basketball_court_v1--native-v1'),[view,setView]=useState('aerial');
  const layout=choices.find(p=>p.id===id)!;
  return <main style={{height:'100vh',fontFamily:'Arial',background:'#f7f4e9',color:'#183a30'}}>
    <header style={{padding:16,display:'flex',gap:18,alignItems:'center',height:56}}>
      <strong>City Prompt · Native park pilot</strong>
      <select aria-label="Review park" value={id} onChange={e=>setId(e.target.value)}>{choices.map(p=><option key={p.id} value={p.id}>{p.title} · {p.label}</option>)}</select>
      <select aria-label="Review view" value={view} onChange={e=>setView(e.target.value)}>{['aerial','overhead','walk'].map(v=><option key={v}>{v}</option>)}</select>
      <span>{layout.widthM} × {layout.depthM} m · Visual fixture; app acceptance pending</span>
    </header>
    <div style={{height:'calc(100vh - 88px)'}}><Canvas shadows camera={{fov:45,near:.1,far:1000,up:[0,0,1]}} gl={{preserveDrawingBuffer:true,antialias:true}}>
      <color attach="background" args={['#dce6e3']}/><ambientLight intensity={1.5}/>
      <directionalLight position={[-50,-70,100]} intensity={3} castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-100} shadow-camera-right={100} shadow-camera-top={100} shadow-camera-bottom={-100} shadow-camera-far={300} shadow-bias={-.0004} shadow-normalBias={.035}/>
      <mesh position={[0,0,-.14]} receiveShadow><planeGeometry args={[600,600]}/><meshStandardMaterial color="#859677" roughness={1}/></mesh>
      <Pose layout={layout} view={view}/>
      <Suspense fallback={null}><NativeParkModel layout={layout}/><Ready layout={layout}/></Suspense>
      <OrbitControls key={`${id}:${view}`} target={[0,0,view==='walk'?1.7:0]}/>
    </Canvas></div>
  </main>;
}
const root=createRoot(document.getElementById('root')!);
root.render(<App/>);
if(import.meta.hot)import.meta.hot.dispose(()=>root.unmount());
