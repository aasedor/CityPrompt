/** Development rehearsal only. No saved design or production terrain provider
 * is changed. Promotion requires edit/reload/capture and multi-route integration. */
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { fitRoadTerrainEdges, type CorridorProbe } from './roadTerrainTransition';
import { createRoadRetainingEdge, constrainRoadEdgeWalk, type RoadEdgeBlocker } from './roadRetainingEdge';
import { TerrainTilesChangedError } from './roadTerrainTrialController';
import { createTransitionRoadGeometry, createTransitionTileGeometry } from './roadTerrainTransitionMesh';
import { patchMaterialForSpatialMask, unpatchMaterialSpatialMask, type TileSpatialMaskConfig } from './TileSpatialMaskPlugin';
import { createStreetSurfaceMaterialResources, type StreetSurfaceMaterialResources, type StreetSurfaceMaterialKind } from './streetSurfaceMaterials';

export interface RoadRehearsalInput {
  origin:[number,number,number];
  headingDegrees:number;
  length:number;
  halfWidth:number;
  blendWidth:number;
  endBlend:number;
  profile:{x:number;z:number}[];
  /** Complete 1 m grid, ordered x then y. Heights are local, converted DEM. */
  ground:{x:number;y:number;z:number}[];
  label:string;
  /** Optional, explicit stress case; not a datum correction. */
  designRaiseM?:number;
}
interface Tiles {
  group:THREE.Object3D;
  visibleTiles:Set<unknown>;
  forEachLoadedModel:(fn:(scene:THREE.Object3D,tile:unknown)=>void)=>void;
  addEventListener:(name:string,fn:(event:{scene?:THREE.Object3D})=>void)=>void;
  removeEventListener:(name:string,fn:(event:{scene?:THREE.Object3D})=>void)=>void;
}
export async function rehearseRoadTerrain(scene:THREE.Scene,tiles:Tiles,input:RoadRehearsalInput,signal?:AbortSignal) {
  const checkCancelled=()=>{if(signal?.aborted)throw new DOMException('Terrain build cancelled.','AbortError');};
  checkCancelled();
  if(!import.meta.env.DEV) throw new Error('Road terrain rehearsal is development-only.');
  if(scene.userData.roadTerrainRehearsal)throw new Error('Close the previous road rehearsal first.');
  const enu=new THREE.Matrix4();
  WGS84_ELLIPSOID.getEastNorthUpFrame(input.origin[1]*Math.PI/180,input.origin[0]*Math.PI/180,input.origin[2],enu);
  const frame=enu.clone().multiply(new THREE.Matrix4().makeRotationZ((90-input.headingDegrees)*Math.PI/180));
  const inverse=frame.clone().invert();
  const visibleScenes=()=>{const result=new Set<THREE.Object3D>();
    tiles.forEachLoadedModel((s,t)=>{if(tiles.visibleTiles.has(t))result.add(s);});return result;};
  const scenes=visibleScenes();
  if(!scenes.size)throw new Error('Wait for visible Google tiles.');
  const visible=(hit:THREE.Intersection)=>{let o:THREE.Object3D|null=hit.object,seen=false;while(o){if(!o.visible)return false;if(scenes.has(o))seen=true;if(o===tiles.group)return seen;o=o.parent;}return false;};
  const ray=new THREE.Raycaster(),up=new THREE.Vector3(0,0,1).transformDirection(frame);
  ray.far=1000;
  const hitAt=(x:number,y:number)=>{
    ray.set(new THREE.Vector3(x,y,400).applyMatrix4(frame),up.clone().negate());
    return ray.intersectObjects([...scenes],true).find(visible);
  };
  const outer=input.halfWidth+.6+input.blendWidth;
  const expectedCount=(input.length+2*input.endBlend+1)*(Math.ceil(outer)*2+1);
  if(input.ground.length!==expectedCount || expectedCount>6500) throw new Error('The complete bounded ground grid is required.');
  const passes:CorridorProbe[][]=[];
  for(let pass=0;pass<2;pass++) {
    const probes:CorridorProbe[]=[];
    for(const p of input.ground) {
      const hit=hitAt(p.x,p.y);probes.push({x:p.x,y:p.y,z:hit?hit.point.clone().applyMatrix4(inverse).z:null});
      if(probes.length%30===0)await new Promise(requestAnimationFrame);
      checkCancelled();
    }
    passes.push(probes);await new Promise(r=>setTimeout(r,700));
  }
  checkCancelled();
  const measuredScenes=visibleScenes();
  if(measuredScenes.size!==scenes.size||[...scenes].some(s=>!measuredScenes.has(s)))
    throw new TerrainTilesChangedError('Visible tiles changed during measurement; rebuild the transition.');
  const maxPassDelta=Math.max(...passes[0].map((p,i)=>p.z===null||passes[1][i].z===null?Infinity:Math.abs(p.z-passes[1][i].z!)));
  if(maxPassDelta>.08)throw new TerrainTilesChangedError('Tiles are still refining; measure again before changing terrain.');
  const probes=passes[1];
  // Five predetermined centreline stations estimate local visual registration.
  // The independent surrounding grid is held out for object detection.
  const controls=[0,.25,.5,.75,1].map(t=>probes.find(p=>p.x===Math.round(input.length*t)&&p.y===0)!);
  const ground=new Map(input.ground.map(p=>[`${p.x},${p.y}`,p.z]));
  if(ground.size!==expectedCount)throw new Error('Ground grid contains duplicate or missing positions.');
  const offsets=controls.map(p=>p.z===null?NaN:p.z-ground.get(`${p.x},0`)!);
  if(offsets.some(v=>!Number.isFinite(v)))throw new Error('Endpoint control ground is unavailable.');
  const contextOffset=[...offsets].sort((a,b)=>a-b)[2];
  if(Math.abs(contextOffset)>2.5)throw new Error('The local alignment is too large to distinguish ground from an object surface.');
  if(Math.max(...offsets)-Math.min(...offsets)>.6)throw new Error(`Control stations do not agree on a ground surface. ${JSON.stringify(offsets)}`);
  // A local visual registration is separate from the official height datum.
  // Preserve the input DEM; place this proposal in the observed tile context.
  // Applying the raw absolute mismatch only at the ends creates a false hump.
  const designRaise=input.designRaiseM??0;
  if(!Number.isFinite(designRaise)||Math.abs(designRaise)>1.5)throw new Error('Invalid road grading stress case.');
  const endSection=(x:number)=>{
    const width=Math.ceil(input.halfWidth+.6),result:{y:number;z:number}[]=[];
    for(let y=-width;y<=width;y+=.25){const hit=hitAt(x,y);
      if(!hit)throw new Error('Road-end ground is incomplete.');result.push({y,z:hit.point.clone().applyMatrix4(inverse).z});}
    return result;
  };
  const {field,validation}=fitRoadTerrainEdges({profile:input.profile.map(p=>({x:p.x,z:p.z+contextOffset+designRaise})),halfWidth:input.halfWidth,shoulderWidth:.6,
    blendWidth:input.blendWidth,endBlend:input.endBlend,tieLength:input.length/2,
    startHeight:controls[0].z!,endHeight:controls[4].z!,
    startCrossSection:endSection(0),endCrossSection:endSection(input.length)},probes,(x,y)=>(ground.get(`${x},${y}`)??NaN)+contextOffset);
  const expectedGround=(x:number,y:number)=>{
    const ix=Math.floor(x),iy=Math.floor(y),u=x-ix,v=y-iy;
    let z=0;
    for(const [dx,dy,w] of [[0,0,(1-u)*(1-v)],[1,0,u*(1-v)],[0,1,(1-u)*v],[1,1,u*v]]) {
      if(w<1e-10)continue;
      const value=ground.get(`${ix+dx},${iy+dy}`);if(value===undefined)return null;z+=w*value;
    }
    return z+contextOffset;
  };
  const controlChecks:{x:number;y:number;z:number}[]=[];
  for(const x of [.0001,input.length-.0001])for(let y=-input.halfWidth+.0001;y<input.halfWidth;y+=.25){
    const hit=hitAt(x,y);if(!hit)throw new Error('Road-end ground is incomplete.');
    controlChecks.push({x,y,z:hit.point.clone().applyMatrix4(inverse).z});
  }
  const seamChecks:{x:number;y:number;z:number}[]=[];
  for(let x=-input.endBlend;x<=input.length+input.endBlend;x++)for(const y of [-field.outerWidthAt(-1),field.outerWidthAt(1)]){
    const hit=hitAt(x,y);if(!hit)throw new Error('The outer terrain join is incomplete.');
    seamChecks.push({x,y,z:hit.point.clone().applyMatrix4(inverse).z});
  }
  const road=new THREE.Group();road.name='road-terrain-rehearsal';road.matrixAutoUpdate=false;road.matrix.copy(frame);
  road.userData={streetGroundStatus:'ready',terrainRehearsal:true};
  const owned:THREE.BufferGeometry[]=[],materials:THREE.Material[]=[];
  const surfaceResources:StreetSurfaceMaterialResources[]=[];
  const surface=(low:number,high:number,kind:StreetSurfaceMaterialKind,lift=0)=>{
    const geometry=createTransitionRoadGeometry(field,low,high,lift);owned.push(geometry);
    const resources=createStreetSurfaceMaterialResources(kind,{seed:'road-terrain-rehearsal',relief:true,anisotropy:8});surfaceResources.push(resources);
    const mesh=new THREE.Mesh(geometry,resources.material);mesh.receiveShadow=true;road.add(mesh);return mesh;
  };
  surface(-input.halfWidth,input.halfWidth,'asphalt');
  // Narrow aggregate shoulders soften the asphalt boundary without laying a
  // large generic grass texture over the surrounding aerial photography.
  surface(-input.halfWidth-.5,-input.halfWidth,'buffer_stone',-.003);
  surface(input.halfWidth,input.halfWidth+.5,'buffer_stone',-.003);
  const markings=new THREE.MeshBasicMaterial({color:'#e2dfce',side:THREE.DoubleSide});materials.push(markings);
  for(const y of [-input.halfWidth+.16,input.halfWidth-.16]) {
    const geometry=createTransitionRoadGeometry(field,y-.045,y+.045,.006);owned.push(geometry);road.add(new THREE.Mesh(geometry,markings));
  }
  const replacements:{mesh:THREE.Mesh;original:THREE.BufferGeometry;geometry:THREE.BufferGeometry}[]=[];
  const blockers:RoadEdgeBlocker[]=[];
  let retainingMaximumHeightM=0;
  const patched=new Set<THREE.Material>();
  const core=input.halfWidth+.5;
  const mask:TileSpatialMaskConfig={worldToLocal:inverse,edges:[new THREE.Vector4(0,-core,input.length,-core),
    new THREE.Vector4(input.length,-core,input.length,core),new THREE.Vector4(input.length,core,0,core),new THREE.Vector4(0,core,0,-core)],
    maskRanges:[new THREE.Vector2(0,4)],maskCount:1,minHeight:-30,maxHeight:40,cacheKey:`corridor-rehearsal:${road.uuid}`};
  const box=new THREE.Box3(new THREE.Vector3(-input.endBlend,-outer,-20),new THREE.Vector3(input.length+input.endBlend,outer,25));
  // Prepare everything before installing any geometry or cut. A rejected
  // canopy, missing tile, budget overrun or unsupported material leaves context.
  try {
    for(const side of [-1,1] as const)if(field.edgeAt(side)==='retaining') {
      const edge=createRoadRetainingEdge(field,side,(x,y)=>{const hit=hitAt(x,y);return hit?hit.point.clone().applyMatrix4(inverse).z:null;},expectedGround);
      owned.push(edge.face,edge.cap,edge.rail);blockers.push(...edge.blockers);
      retainingMaximumHeightM=Math.max(retainingMaximumHeightM,edge.maximumHeight);
      for(const [geometry,kind] of [[edge.face,'concrete'],[edge.cap,'buffer_stone']] as const) {
        const resources=createStreetSurfaceMaterialResources(kind,{seed:'road-retaining-edge',relief:true,anisotropy:8});
        surfaceResources.push(resources);resources.material.side=THREE.DoubleSide;
        const mesh=new THREE.Mesh(geometry,resources.material);mesh.receiveShadow=true;road.add(mesh);
      }
      const guardMaterial=new THREE.MeshStandardMaterial({color:'#394449',roughness:.7,side:THREE.DoubleSide});materials.push(guardMaterial);
      road.add(new THREE.Mesh(edge.rail,guardMaterial));
    }
    for(const root of scenes)root.traverse(object=>{
      if(!(object instanceof THREE.Mesh)||!object.visible)return;
      const mesh=object as THREE.Mesh, transform=inverse.clone().multiply(mesh.matrixWorld);
      mesh.geometry.computeBoundingBox();
      if(!mesh.geometry.boundingBox?.clone().applyMatrix4(transform).intersectsBox(box))return;
      const mats=Array.isArray(mesh.material)?mesh.material:[mesh.material];
      if(mats.some(m=>m.userData.__cityPromptTileSpatialMaskPatch))throw new Error('Use an empty natural-ground project for this rehearsal.');
      const geometry=createTransitionTileGeometry(mesh.geometry,transform,field,300_000,expectedGround);
      if(geometry)replacements.push({mesh,original:mesh.geometry,geometry});
      if(replacements.reduce((n,r)=>n+r.geometry.getAttribute('position').count,0)>600_000)
        throw new Error('The transition exceeds the total geometry budget. Shorten the route.');
    });
  }catch(e){replacements.forEach(r=>r.geometry.dispose());owned.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());surfaceResources.forEach(r=>r.dispose());throw e;}
  let active=false,disposed=false,stale=false;
  const summary={label:input.label,probes:probes.length,maxPassDelta,contextOffset,
    leftEdge:field.edgeAt(1),rightEdge:field.edgeAt(-1),retainingMaximumHeightM,
    maxGroundChangeM:validation.maxChangeM,visualAlignmentOffsetM:contextOffset,designRaiseM:designRaise,
    profileRetention:field.profileRetention,changedMeshes:replacements.length,
    replacementVertices:replacements.reduce((n,r)=>n+r.geometry.getAttribute('position').count,0),
    endpointMaxGapM:0,outerSeamMaxGapM:0,roadMaximumGrade:0};
  const localPoint=(lng:number,lat:number)=>{
    const world=new THREE.Vector3();WGS84_ELLIPSOID.getCartographicToPosition(lat*Math.PI/180,lng*Math.PI/180,input.origin[2],world);
    return world.applyMatrix4(inverse);
  };
  const registration={summary,constrainWalk:(from:{lng:number;lat:number},to:{lng:number;lat:number})=>{
    if(!active||stale||!blockers.length)return to;
    const a=localPoint(from.lng,from.lat),b=localPoint(to.lng,to.lat),allowed=constrainRoadEdgeWalk(a,b,blockers);
    if(allowed===b)return to;
    const world=new THREE.Vector3(allowed.x,allowed.y,b.z).applyMatrix4(frame),geo={lat:0,lon:0,height:0};
    WGS84_ELLIPSOID.getPositionToCartographic(world,geo);return {lng:geo.lon*180/Math.PI,lat:geo.lat*180/Math.PI};
  },heightAt:(lng:number,lat:number):number|null=>{
    if(!active||stale)return null;
    const world=new THREE.Vector3();WGS84_ELLIPSOID.getCartographicToPosition(lat*Math.PI/180,lng*Math.PI/180,input.origin[2],world);
    const local=world.clone().applyMatrix4(inverse);
    if(local.x< -input.endBlend||local.x>input.length+input.endBlend||Math.abs(local.y)>outer)return null;
    if(local.x>=0&&local.x<=input.length&&Math.abs(local.y)<=core)
      local.z=field.roadHeight(local.x,local.y)+(Math.abs(local.y)>input.halfWidth?-.003:0);
    else {const hit=hitAt(local.x,local.y);if(!hit)return null;local.z=hit.point.clone().applyMatrix4(inverse).z;}
    return WGS84_ELLIPSOID.getPositionElevation(local.applyMatrix4(frame));
  }};
  const setVisible=(show:boolean)=>{
    if(disposed||stale&&show)return;
    active=show;
    replacements.forEach(r=>{
      r.mesh.geometry=show?r.geometry:r.original;
      const mats=Array.isArray(r.mesh.material)?r.mesh.material:[r.mesh.material];
      mats.forEach(m=>{if(show){patchMaterialForSpatialMask(m,mask);patched.add(m);}else unpatchMaterialSpatialMask(m);});
    });
    if(show){scene.add(road);scene.userData.roadTerrainRehearsal=registration;}
    else {scene.remove(road);if(scene.userData.roadTerrainRehearsal===registration)delete scene.userData.roadTerrainRehearsal;
      patched.forEach(unpatchMaterialSpatialMask);patched.clear();}
  };
  const invalidate=(event:{scene?:THREE.Object3D})=>{
    if(!event.scene || !new THREE.Box3().setFromObject(event.scene).applyMatrix4(inverse).intersectsBox(box))return;
    setVisible(false);stale=true;road.userData.streetGroundStatus='unavailable';
  };
  // A refined tile must never carry the previous tile's cut or grade. Restore
  // the original scene and require a fresh complete measurement.
  tiles.addEventListener('load-model',invalidate);
  tiles.addEventListener('dispose-model',invalidate);
  // Cached tiles can become visible without another load-model event.
  tiles.addEventListener('tile-visibility-change',invalidate);
  setVisible(true);
  scene.updateMatrixWorld(true);
  for(const p of controlChecks){
    ray.set(new THREE.Vector3(p.x,p.y,400).applyMatrix4(frame),up.clone().negate());
    const hit=ray.intersectObject(road,true)[0];
    summary.endpointMaxGapM=Math.max(summary.endpointMaxGapM,hit?Math.abs(hit.point.clone().applyMatrix4(inverse).z-p.z):Infinity);
  }
  for(const p of seamChecks){const hit=hitAt(p.x,p.y);
    summary.outerSeamMaxGapM=Math.max(summary.outerSeamMaxGapM,hit?Math.abs(hit.point.clone().applyMatrix4(inverse).z-p.z):Infinity);}
  for(const y of [-input.halfWidth,0,input.halfWidth])for(let x=.25;x<=input.length;x+=.25)
    summary.roadMaximumGrade=Math.max(summary.roadMaximumGrade,Math.abs(field.roadHeight(x,y)-field.roadHeight(x-.25,y))/.25);
  const dispose=()=>{if(disposed)return;setVisible(false);disposed=true;tiles.removeEventListener('load-model',invalidate);tiles.removeEventListener('dispose-model',invalidate);
    tiles.removeEventListener('tile-visibility-change',invalidate);
    replacements.forEach(r=>r.geometry.dispose());owned.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());surfaceResources.forEach(r=>r.dispose());};
  if(summary.endpointMaxGapM>.025||summary.outerSeamMaxGapM>.015||summary.roadMaximumGrade>.12){
    dispose();throw new Error(`The physical road join did not pass: ${JSON.stringify(summary)}`);
  }
  return {field,frame,road,summary,
    setVisible,status:()=>({active,stale}),
    dispose};
}
