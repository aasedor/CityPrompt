/* Free GPU regression: run against an existing Vite server with CAPTURE_QA_BASE_URL. No API calls. */
const {createRequire}=require('node:module'),path=require('node:path'),fs=require('node:fs');
const {chromium}=createRequire(path.resolve(__dirname,'../package.json'))('@playwright/test');
const out=process.env.CAPTURE_QA_OUTPUT_DIR || path.resolve(__dirname,'../../artifacts/direct3d-capture-qa');
fs.mkdirSync(out,{recursive:true});
const baseUrl=process.env.CAPTURE_QA_BASE_URL || 'http://127.0.0.1:5173';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:800,height:700}});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.route('**/__fidelity-harness',r=>r.fulfill({contentType:'text/html',body:'<html><body style="margin:0;background:#fafaf7"><h3>Exact concave source mask and capture QA</h3></body></html>'}));
 try {
  await page.goto(baseUrl+'/__fidelity-harness');
  const results=await page.evaluate(async()=>{
   const THREE=await import('/node_modules/.vite/deps/three.js');
   const masks=await import('/src/components/viewer/globe/TileSpatialMaskPlugin.ts');
   const capture=await import('/src/components/viewer/globe/direct3dCapture.ts');
   const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,stencil:true});renderer.setSize(640,640);document.body.appendChild(renderer.domElement);
   const scene=new THREE.Scene();scene.background=new THREE.Color('#ddeafa');scene.add(new THREE.AmbientLight(0xffffff,2));
   const camera=new THREE.PerspectiveCamera(45,1,0.1,100);camera.position.set(6,-9,11);camera.up.set(0,0,1);camera.lookAt(0,0,0);
   const points=[[-3,-3],[3,-3],[3,-1],[-1,-1],[-1,3],[-3,3]];
   const shape=new THREE.Shape(points.map(p=>new THREE.Vector2(...p)));
   const cfg={worldToLocal:new THREE.Matrix4(),edges:points.map((p,i)=>new THREE.Vector4(...p,...points[(i+1)%points.length])),maskRanges:[new THREE.Vector2(0,6)],maskCount:1,minHeight:-1,maxHeight:3,cacheKey:'gpu-l-shape'};
   const contextMaterial=new THREE.MeshStandardMaterial({color:'#53772b',side:THREE.DoubleSide});masks.patchMaterialForSpatialMask(contextMaterial,cfg);
   const context=new THREE.Mesh(new THREE.PlaneGeometry(10,10),contextMaterial);scene.add(context);
   const removedMaterial=new THREE.MeshStandardMaterial({color:'#ee2233'});masks.patchMaterialForSpatialMask(removedMaterial,cfg);
   const removed=new THREE.Mesh(new THREE.BoxGeometry(1,1,1.4),removedMaterial);removed.position.set(-2,1,.7);scene.add(removed);
   const notchMaterial=new THREE.MeshStandardMaterial({color:'#ffdd33'});masks.patchMaterialForSpatialMask(notchMaterial,cfg);
   const notch=new THREE.Mesh(new THREE.BoxGeometry(1,1,1.4),notchMaterial);notch.position.set(1,1,.7);scene.add(notch);
   const ground=new THREE.Mesh(new THREE.ShapeGeometry(shape),new THREE.MeshStandardMaterial({color:'#68bdd1',side:THREE.DoubleSide}));ground.position.z=-.04;ground.userData=capture.direct3DInstanceUserData({instance_id:'qa-ground',semantic_class:'park',zone_id:'qa-site'});ground.userData[capture.DIRECT_3D_PROPOSAL_ROLE_KEY]="park";scene.add(ground);
   const facadeNormal=new THREE.DataTexture(new Uint8Array([128,128,255,255]),1,1);facadeNormal.needsUpdate=true;
   const facadeBump=new THREE.DataTexture(new Uint8Array([128,128,128,255]),1,1);facadeBump.needsUpdate=true;
   const house=new THREE.Mesh(new THREE.BoxGeometry(.8,.8,1.2),new THREE.MeshStandardMaterial({color:'#ede2ce',normalMap:facadeNormal,bumpMap:facadeBump}));house.position.set(-2,-2,.6);house.userData=capture.direct3DInstanceUserData({instance_id:'qa-house',semantic_class:'building',zone_id:'qa-house'});house.userData[capture.DIRECT_3D_PROPOSAL_ROLE_KEY]="building";scene.add(house);
   scene.updateMatrixWorld(true);renderer.render(scene,camera);
   const masked=await capture.captureDirect3DScene(renderer,scene,camera,{includeGeometryPasses:true,maxLongEdge:640,minVisibleContextCoverage:.01});
   const outer=new THREE.Shape([[-5,-5],[5,-5],[5,5],[-5,5]].map(p=>new THREE.Vector2(...p)));outer.holes.push(new THREE.Path(points.map(p=>new THREE.Vector2(...p))));
   context.geometry.dispose();context.geometry=new THREE.ShapeGeometry(outer);masks.unpatchMaterialSpatialMask(contextMaterial);removed.visible=false;masks.unpatchMaterialSpatialMask(notchMaterial);scene.updateMatrixWorld(true);
   const oracle=await capture.captureDirect3DScene(renderer,scene,camera,{includeGeometryPasses:true,maxLongEdge:640,minVisibleContextCoverage:.01});
   const project=p=>{const q=new THREE.Vector3(...p).project(camera);return [Math.round((q.x+1)*320),Math.round((1-q.y)*320)]};
   const pixels=async url=>{const image=await createImageBitmap(await (await fetch(url)).blob());const cv=document.createElement('canvas');cv.width=640;cv.height=640;const ctx=cv.getContext('2d');ctx.drawImage(image,0,0);const rgba=ctx.getImageData(0,0,640,640).data;image.close();return rgba};
   const comparisons={};
   for(const key of ['depthImageBase64','normalImageBase64','proposalMaskBase64']){
    const left=await pixels(masked[key]),right=await pixels(oracle[key]);let changed=0;
    for(let i=0;i<left.length;i+=4){const differs=key==='depthImageBase64'?Math.abs((left[i]-right[i])/256+(left[i+1]-right[i+1])/65536+(left[i+2]-right[i+2])/(255*65536))>0.00002:left[i]!==right[i]||left[i+1]!==right[i+1]||left[i+2]!==right[i+2]||left[i+3]!==right[i+3];if(differs)changed++;}
    if(changed>640*640*.005)throw new Error(key+' disagrees with explicit cut geometry: '+changed+' pixels');
    comparisons[key]={changedPixels:changed};
   }
   const depth=await pixels(masked.depthImageBase64),normals=await pixels(masked.normalImageBase64);
   const expectedNormal=new THREE.Vector3(0,0,1).transformDirection(camera.matrixWorldInverse).toArray().map(n=>Math.round((n*.5+.5)*255));
   for(const [name,p] of Object.entries({notch:[1,1,1.4],house:[-2,-2,1.2],cleared:[-2,1,-.04]})){
    const [x,y]=project(p),i=(y*640+x)*4,decoded=depth[i]/256+depth[i+1]/65536+depth[i+2]/(255*65536),expected=(new THREE.Vector3(...p).project(camera).z+1)/2;
    if(depth[i+3]!==255||Math.abs(decoded-expected)>.00005)throw new Error(name+' depth PNG lost numeric values: '+JSON.stringify({decoded,expected,rgba:Array.from(depth.slice(i,i+4))}));
    for(let c=0;c<3;c++)if(Math.abs(normals[i+c]-expectedNormal[c])>1)throw new Error(name+' normal PNG is not linear encoded renderer data');
   }
   context.visible=false;notch.visible=false;
   let emptyContextRejected=false;
   try{await capture.captureDirect3DScene(renderer,scene,camera,{maxLongEdge:640,minVisibleContextCoverage:.01})}catch(e){emptyContextRejected=e.message.includes('surrounding map')}
   if(!emptyContextRejected)throw new Error('A sky-only context was accepted');
   context.visible=true;notch.visible=true;
   renderer.render(scene,camera);
   return {masked,oracle,comparisons,samples:{notch:project([1,1,1.4]),removed:project([-2,1,0]),house:project([-2,-2,1.2])},renderCalls:renderer.info.render.calls};
  });
  for(const [kind,bundle] of Object.entries({masked:results.masked,oracle:results.oracle}))for(const [key,value] of Object.entries(bundle))if(key.endsWith('Base64')&&typeof value==='string')fs.writeFileSync(path.join(out,`gpu-${kind}-${key}.png`),Buffer.from(value.replace(/^data:[^,]+,/,''),'base64'));
  fs.writeFileSync(path.join(out,'gpu-capture-summary.json'),JSON.stringify({samples:results.samples,comparisons:results.comparisons,masked:{width:results.masked.width,height:results.masked.height,coverage:results.masked.maskCoverage,classes:results.masked.classCoverage},errors},null,2));
  await page.screenshot({path:path.join(out,'gpu-oracle-scene.png')});
  if(errors.length)throw new Error('WebGL errors: '+JSON.stringify(errors));
  console.log(JSON.stringify({samples:results.samples,width:results.masked.width,height:results.masked.height,coverage:results.masked.maskCoverage,comparisons:results.comparisons,errors},null,2));
 }catch(e){console.log('HARNESS_ERROR',e.message);console.log(JSON.stringify(errors));process.exitCode=1}
 finally{fs.writeFileSync(path.join(out,'gpu-errors.json'),JSON.stringify(errors,null,2));await browser.close()}
})();
