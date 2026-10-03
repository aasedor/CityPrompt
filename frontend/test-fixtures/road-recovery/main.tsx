/** Local Vite fixture. Not imported by the application or production build.
 * Exercises the real street layer, tile-set retry and capture gate with
 * deterministic terrain hits. No project writes, Google tiles or paid calls. */
import React, { Suspense, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { TilesRendererContext } from '3d-tiles-renderer/r3f';
import { TilesRenderer } from '3d-tiles-renderer';
import { GlobeStreetDetailLayer } from '../../src/components/viewer/globe/GlobeStreetDetailLayer';
import { assertStreetGroundReady } from '../../src/components/viewer/globe/streetGroundCapture';
import { bufferLineToPolygon } from '../../src/utils/roadGeometry';
import type { SiteZone } from '../../src/types';

const line = [[-114.125, 51.017], [-114.1246, 51.017]];
const base = {project_id:'fixture',name:'Fixture',color:'#888',sort_order:0,created_at:'2026-09-24',updated_at:'2026-09-24'};
const zones: SiteZone[] = [
  {...base,id:'boundary',zone_type:'site_boundary',is_active_boundary:true,
    coordinates:[[-114.1252,51.0168],[-114.1248,51.0168],[-114.1248,51.0172],[-114.1252,51.0172]],
    properties:{terrain_elevation_m:1100}},
  {...base,id:'road',zone_type:'road',coordinates:bufferLineToPolygon(line,10),properties:{
    width:10,plan_centerline:line,road_archetype_id:'narrow_residential_street',connect_to_public_road:true,
    terrain_elevation_m:1100,community_3d:{schema_version:1,state:'compiled',kind:'street',generator:'fixture',compiled_at:'2026-09-24'},
  }},
];

function makeTiles() {
  const group = new THREE.Group();
  const surface = new THREE.Object3D();
  const state = {complete:false};
  surface.raycast = (raycaster, hits) => {
    if (state.complete) hits.push({distance:48900,point:raycaster.ray.at(48900,new THREE.Vector3()),object:surface});
  };
  group.add(surface);
  const tiles = new TilesRenderer();
  tiles.group.add(group);
  tiles.visibleTiles.add({} as never);
  return Object.assign(tiles,{state});
}

function Observe({onChange,onScene}:{onChange:(s:string)=>void;onScene:(s:THREE.Scene)=>void}) {
  const {scene}=useThree(); const previous=useRef('');
  useFrame(()=>{
    const rows:unknown[]=[];
    scene.traverse(o=>{if(o.userData.streetGroundZoneId) rows.push(o.userData);});
    const value=JSON.stringify(rows,null,2);
    if(value!==previous.current){previous.current=value;onChange(value);onScene(scene);}
  });
  return null;
}

function Fixture() {
  const [tiles]=useState(makeTiles),[diagnostics,setDiagnostics]=useState('Starting actual street renderer…');
  const [result,setResult]=useState('Export not attempted'); const [replacements,setReplacements]=useState(0);
  const scene=useRef<THREE.Scene|null>(null);
  const replace=(complete:boolean)=>{tiles.state.complete=complete;tiles.visibleTiles.clear();tiles.visibleTiles.add({});setReplacements(n=>n+1);};
  return <main style={{fontFamily:'system-ui',padding:24,maxWidth:900}}>
    <h1>Road readiness recovery fixture</h1>
    <p>Actual street renderer and export guard; deterministic missing/complete terrain. Reload resets the two-retry budget.</p>
    <button onClick={()=>replace(false)}>Replace with incomplete tiles</button>{' '}
    <button onClick={()=>replace(true)}>Replace with complete tiles</button>{' '}
    <button onClick={()=>{try{if(!scene.current)throw Error('Renderer not ready');assertStreetGroundReady(scene.current);setResult('Export allowed: measured road ready');}catch(e){setResult('Export refused: '+(e as Error).message);}}}>Try exact export guard</button>
    <p>Tile replacements: {replacements}</p><p role="status">{result}</p>
    <pre aria-label="Street diagnostics">{diagnostics}</pre>
    <div style={{width:320,height:160}}><Canvas><Suspense fallback={null}>
      <TilesRendererContext.Provider value={tiles as never}>
        <GlobeStreetDetailLayer zones={zones} terrainHeight={1100}/>
        <Observe onChange={setDiagnostics} onScene={s=>{scene.current=s;}}/>
      </TilesRendererContext.Provider>
    </Suspense></Canvas></div>
  </main>;
}
createRoot(document.getElementById('root')!).render(<Fixture/>);
