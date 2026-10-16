/** Local-only deterministic roadway fixture. No project or provider writes. */
import { Suspense, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import { Box3, Vector3, Matrix4, Mesh, Scene, Color, PerspectiveCamera, AmbientLight, DirectionalLight, WebGLRenderer, type Material } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import rows from '../features/parks/calgarySafetyCatalogue.json';
import { buildDetailInstances, disposeDetailInstances } from '../features/parks/detailInstances';
import { SafetyVariantCards } from '../features/parks/SafetyVariantCards';
import type { DetailAsset } from '../features/parks/detailCatalogue';
import '../index.css';

type Row = typeof rows[number];
interface Result { id: string; status: string; image?: string; error?: string; triangles?: number; calls?: number; geometryBytes?: number; loadMs?: number; repeated100?: {calls:number;triangles:number;cpuSubmitMedianMs:number;textureCount:number} }
const positions: Record<string, [number,number]> = {
  'speed-cushion': [3,-23], 'speed-cushion-pair': [0,-9], 'school-crossing-sign': [0,-17],
  'left-turn-calming': [0,4], 'high-visibility-crossing': [6.6,-16], 'green-bike-box': [0,12],
  'green-conflict-strip': [-4.5,20], 'bicycle-signal': [-6.6,15], 'traffic-diverter': [0,29], 'speed-display-trailer': [8,-4],
};
function Model({row,solo}:{row:Row;solo:boolean}) {
  const {scene}=useGLTF(row.url);
  const group=useMemo(()=>{
    const key=row.id.replace('detail-calgary-','').replace(/-v1$/,'');
    const [x,z]=solo?[0,0]:positions[key];
    return buildDetailInstances(scene,[new Matrix4().makeTranslation(x,0,z)]);
  },[scene,row,solo]);
  useEffect(()=>()=>disposeDetailInstances(group),[group]);
  return <primitive object={group} dispose={null}/>;
}
function Thumbnail({asset}:{asset:DetailAsset}){return <img src={asset.thumbnailUrl} alt={asset.label} className="h-40 w-full object-contain"/>;}
async function inspect(update:(r:Result[])=>void) {
  const results:Result[]=[];
  const renderer=new WebGLRenderer({antialias:true,preserveDrawingBuffer:true,logarithmicDepthBuffer:true});
  renderer.setSize(640,480);renderer.setPixelRatio(1);
  try { for (const row of rows) {
    const geometry=new Set<Mesh['geometry']>(),materials=new Set<Material>();
    let batch:ReturnType<typeof buildDetailInstances>|undefined;
    try {
      const start=performance.now(), response=await fetch(row.url);
      if (!response.ok) throw Error(`HTTP ${response.status}`);
      const bytes=await response.arrayBuffer();
      const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
      if(hash!==row.sha256)throw Error('Source hash mismatch');
      const loaded=await new GLTFLoader().parseAsync(bytes,'');
      loaded.scene.traverse(o=>{const m=o as Mesh;if(!m.isMesh)return;geometry.add(m.geometry);(Array.isArray(m.material)?m.material:[m.material]).forEach(v=>materials.add(v));});
      const buffers=new Set<ArrayBufferLike>();
      geometry.forEach(g=>{if(g.index)buffers.add(g.index.array.buffer);Object.values(g.attributes).forEach(a=>buffers.add(a.array.buffer));});
      const bounds=new Box3().setFromObject(loaded.scene),size=bounds.getSize(new Vector3()),center=bounds.getCenter(new Vector3());
      [size.x,size.z,size.y].forEach((v,i)=>{if(Math.abs(v-row.dimensions[i])>.002)throw Error('Metre bounds mismatch');});
      if(Math.abs(bounds.min.y-row.nativeBoundsZUp[0][2])>.002)throw Error('Authored ground datum mismatch');
      const scene=new Scene();scene.background=new Color('#e8edf0');scene.add(new AmbientLight('white',2));
      const sun=new DirectionalLight('white',3);sun.position.set(8,14,9);scene.add(sun);
      const camera=new PerspectiveCamera(40,4/3,.01,500);
      camera.position.copy(center).add(new Vector3(.7,.65,1).normalize().multiplyScalar(Math.max(size.x,size.y,size.z)*1.8));camera.lookAt(center);
      batch=buildDetailInstances(loaded.scene,[new Matrix4()]);scene.add(batch);renderer.render(scene,camera);
      if(!renderer.info.render.triangles)throw Error('No visible triangles');
      const result:Result={id:row.id,status:'PASS',triangles:renderer.info.render.triangles,calls:renderer.info.render.calls,
        geometryBytes:[...buffers].reduce((n,b)=>n+b.byteLength,0),loadMs:performance.now()-start,image:renderer.domElement.toDataURL('image/png')};
      scene.remove(batch);disposeDetailInstances(batch);
      const spacing=Math.max(size.x,size.z)+1;
      batch=buildDetailInstances(loaded.scene,Array.from({length:100},(_,i)=>new Matrix4().makeTranslation((i%10-4.5)*spacing,0,(Math.floor(i/10)-4.5)*spacing)));
      scene.add(batch);camera.position.set(spacing*10,spacing*12,spacing*14);camera.lookAt(center);
      const times:number[]=[];
      for(let frame=0;frame<25;frame++){
        const begun=performance.now();renderer.render(scene,camera);
        if(frame>=5)times.push(performance.now()-begun);
      }
      times.sort((a,b)=>a-b);
      // CPU submission timing only: not a GPU timer or representative walking FPS.
      result.repeated100={calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,cpuSubmitMedianMs:times[10],textureCount:renderer.info.memory.textures};
      results.push(result);
    } catch(error){results.push({id:row.id,status:'FAIL',error:String(error)});}
    finally{if(batch)disposeDetailInstances(batch);geometry.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());renderer.renderLists.dispose();}
    update([...results]);
  }}finally{renderer.dispose();renderer.forceContextLoss();}
}
function Review(){
  const [selection,setSelection]=useState(rows[0].id),[results,setResults]=useState<Result[]>([]),[busy,setBusy]=useState(false);
  const solo=selection!=='roadway',chosen=rows.find(r=>r.id===selection)??rows[0];
  return <><header><h1>Calgary safety additions · local review</h1><p>Concept visualization · fixed metres · illustrative dimensions · no live project changes</p>
    <select aria-label="Review view" value={selection} onChange={e=>setSelection(e.target.value)}><option value="roadway">All assets on a roadway</option>{rows.map(r=><option key={r.id} value={r.id}>{r.label}</option>)}</select>
    <button disabled={busy} onClick={()=>{setBusy(true);void inspect(setResults).finally(()=>setBusy(false));}}>{busy?'Inspecting…':'Inspect all GLBs'}</button><p>{solo?chosen.description:'Level synthetic road fixture. This checks model drawing and contact, not real terrain, traffic operation or project persistence.'}</p></header>
    <div className="road"><Canvas key={selection} camera={{position:solo?[6,5,9]:[32,34,43],fov:40,near:.01,far:500}} dpr={1} gl={{logarithmicDepthBuffer:true}}>
      <color attach="background" args={['#d9e2e6']}/><ambientLight intensity={2}/><directionalLight position={[10,20,15]} intensity={3}/>
      <mesh rotation={[-Math.PI/2,0,0]} position={[0,-.001,0]}><planeGeometry args={[solo?30:12,solo?30:80]}/><meshStandardMaterial color="#50585c" roughness={1}/></mesh>
      {!solo&&[-1,1].map(s=><mesh key={s} position={[s*7.3,-.04,0]}><boxGeometry args={[2.6,.08,80]}/><meshStandardMaterial color="#aaa99f"/></mesh>)}
      <Suspense fallback={null}>{(solo?[chosen]:rows).map(row=><Model key={row.id} row={row} solo={solo}/>)}</Suspense>
      <OrbitControls target={[0,solo?Math.min(chosen.dimensions[2]/2,1):0,0]}/>
    </Canvas></div>
    <section className="p-5"><h2 className="text-xl font-bold">Eight catalogue families</h2><p>Local review: “Choose & place” opens the selected model above. It does not save to a project.</p>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4"><SafetyVariantCards assets={rows as unknown as DetailAsset[]} selected={selection} disabled={false} onChoose={setSelection} thumbnail={Thumbnail}/></div></section>
    <section style={{padding:20,display:'grid',gridTemplateColumns:'repeat(3,minmax(0,1fr))',gap:16}}>{results.map(r=><figure key={r.id}>{r.image&&<img alt={r.id} src={r.image}/>}<figcaption>{r.id}<br/>{r.status} · {r.triangles} triangles · {r.calls} draws</figcaption></figure>)}</section>
    <details><summary>Measured GLB results</summary><output aria-label="Expansion audit">{JSON.stringify(results.map(({image:_image,...r})=>r),null,2)}</output></details></>;
}
const root=createRoot(document.getElementById('root')!);if(import.meta.hot)import.meta.hot.dispose(()=>root.unmount());root.render(<Review/>);
