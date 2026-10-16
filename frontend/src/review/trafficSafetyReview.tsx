/** Local-only acceptance harness. Uses the shipped catalogue and instance builder. */

import { Suspense, useEffect, useMemo, useRef, useState } from 'react';

import { createRoot } from 'react-dom/client';

import { Canvas, useFrame } from '@react-three/fiber';

import { OrbitControls, useGLTF } from '@react-three/drei';

import { Box3, Matrix4, Vector3, Mesh } from 'three';

import { safetyGpuAudit, type SafetyGpuResult } from './safetyGpuAudit';

import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

import { DETAIL_CATALOGUE, detailAsset } from '../features/parks/detailCatalogue';

import { buildDetailInstances, disposeDetailInstances } from '../features/parks/detailInstances';

const rows=DETAIL_CATALOGUE.filter(a=>a.safety);

function Model({id,count,onLoad}:{id:string;count:number;onLoad:(s:string)=>void}) {

  const {scene}=useGLTF(detailAsset(id).url);

  const group=useMemo(()=>buildDetailInstances(scene,Array.from({length:count},(_,i)=>new Matrix4().makeTranslation((i%10)*22,0,Math.floor(i/10)*22)),true),[scene,count]);

  useEffect(()=>()=>disposeDetailInstances(group),[group]);

  useEffect(()=>{const box=new Box3().setFromObject(scene); onLoad(JSON.stringify({id,metreBounds:{min:box.min.toArray(),max:box.max.toArray()},dimensions:box.getSize(new Vector3()).toArray(),scale:[1,1,1],datum:0},null,2));},[scene,id,onLoad]);

  return <primitive object={group} dispose={null}/>;

}

function Stats({set}:{set:(s:string)=>void}) {

 const samples=useRef<number[]>([]),elapsed=useRef(0);

 useFrame(({gl},delta)=>{samples.current.push(delta*1000);elapsed.current+=delta;if(elapsed.current<2)return;

 const values=samples.current.sort((a,b)=>a-b);set(JSON.stringify({calls:gl.info.render.calls,triangles:gl.info.render.triangles,geometries:gl.info.memory.geometries,textures:gl.info.memory.textures,frameMedianMs:values[Math.floor(values.length*.5)],frameP95Ms:values[Math.floor(values.length*.95)],samples:values.length,dpr:gl.getPixelRatio()},null,2));samples.current=[];elapsed.current=0;});return null;

}

function Review(){

 const [gpu,setGpu]=useState<SafetyGpuResult[]>([]);

 const [id,setId]=useState('calgary_tc_curb_2750_yellow_r1'),[count,setCount]=useState(1),[load,setLoad]=useState('Loading'),[stats,setStats]=useState(''),[audit,setAudit]=useState('Not run');

 async function checkAll(){const results=[];for(const row of rows){const start=performance.now();try{const response=await fetch(row.url);if(!response.ok)throw Error('HTTP '+response.status);const data=await response.arrayBuffer();const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==row.safety!.sha256)throw Error('Hash mismatch');const model=await new GLTFLoader().parseAsync(data,'');const box=new Box3().setFromObject(model.scene);results.push({id:row.id,status:'PASS',bytes:data.byteLength,loadMs:performance.now()-start,min:box.min.toArray(),max:box.max.toArray()});const geometries=new Set<Mesh['geometry']>();const materials=new Set<Mesh['material']>();model.scene.traverse(o=>{const m=o as Mesh;if(m.isMesh){geometries.add(m.geometry);materials.add(m.material);}});geometries.forEach(g=>g.dispose());materials.forEach(ms=>(Array.isArray(ms)?ms:[ms]).forEach(m=>m.dispose()));}catch(error){results.push({id:row.id,status:'FAIL',error:String(error)});}setAudit(JSON.stringify(results,null,2));}}

 return <><aside><h1>Traffic safety Ã‚· local preview</h1><p>Fixed metres, source pivots, unchanged GLBs. Grey plane is road datum; grid is 1 metre.</p><label>Asset<select aria-label="Safety asset" value={id} onChange={e=>{setLoad('Loading');setId(e.target.value);}}>{rows.map(r=><option key={r.id} value={r.id}>{r.label}</option>)}</select></label><label>Instances<select aria-label="Instance count" value={count} onChange={e=>setCount(Number(e.target.value))}>{[1,10,50,100].map(n=><option key={n}>{n}</option>)}</select></label><button onClick={()=>void safetyGpuAudit(setGpu)}>Draw all 56 variants</button><button onClick={()=>void checkAll()}>Check all 56 GLBs</button><details open><summary>Selected model</summary><output aria-label="Model load">{load}</output></details><output aria-label="Renderer metrics">{stats}</output><details><summary>All asset results</summary><output aria-label="Asset results">{audit}</output></details><details><summary>GPU results {gpu.length}/56</summary><output aria-label="GPU audit">{JSON.stringify(gpu.map(({image:_image,...r})=>r),null,2)}</output></details></aside>{gpu.length>0 && <section aria-label="GPU contact sheet" style={{position:'absolute',zIndex:5,top:0,left:500,right:0,maxHeight:'100vh',overflow:'auto',background:'white',display:'grid',gridTemplateColumns:'repeat(3,1fr)'}}>{gpu.map(r=><figure key={r.id} style={{margin:4}}><img alt={r.id} src={r.image} style={{width:'100%'}}/><figcaption style={{fontSize:10}}>{r.id} · {r.status}</figcaption></figure>)}</section>}<Canvas camera={{position:[12,12,18],fov:45,near:.1,far:1000}} gl={{logarithmicDepthBuffer:true}} dpr={1}><color attach="background" args={['#cfd8dc']}/><ambientLight intensity={2}/><directionalLight position={[5,15,8]} intensity={3}/><mesh rotation={[-Math.PI/2,0,0]} position={[0,-.0001,0]}><planeGeometry args={[500,500]}/><meshStandardMaterial color="#58616a"/></mesh><gridHelper args={[200,200,'#d5dce2','#77828b']}/><Suspense fallback={null}><Model id={id} count={count} onLoad={setLoad}/></Suspense><Stats set={setStats}/><OrbitControls target={[0,0,0]}/></Canvas></>;

}

const root=createRoot(document.getElementById('root')!);if(import.meta.hot)import.meta.hot.dispose(()=>root.unmount());root.render(<Review/>);
