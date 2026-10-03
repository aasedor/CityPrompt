import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { advanceParkWalk,parkWalkHeight } from '@walk-solver';
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(innerWidth-330,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.domElement.style.marginLeft='330px';document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#dbe2e3');scene.environment=new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(),.04).texture;
scene.environmentIntensity=.35;scene.add(new THREE.HemisphereLight(0xf6f1e9,0x6b7668,.65));const sun=new THREE.DirectionalLight(0xfff1dc,2.5);sun.position.set(-20,35,30);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-30,right:30,top:30,bottom:-30,near:1,far:100});sun.shadow.bias=-.0002;sun.shadow.normalBias=.025;scene.add(sun);
const camera=new THREE.PerspectiveCamera(48,(innerWidth-330)/innerHeight,.04,1000),controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,4,0);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(140,140),new THREE.MeshStandardMaterial({color:0xb8c2b1,roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);
let model,network,spec,walking=false,position,yaw=0;const keys=new Set(),status=document.querySelector('#status');
const v=p=>new THREE.Vector3(p[0],p[2],-p[1]);
function view(loc,target,lens=null){camera.fov=lens?THREE.MathUtils.radToDeg(2*Math.atan(36/(2*lens*camera.aspect))):48;camera.updateProjectionMatrix();walking=false;controls.enabled=true;camera.position.copy(v(loc));controls.target.copy(v(target));controls.update();}
function exterior(){const k=spec?.archetype_id==='neighborhood_fourplex' ? .67 : 1;view([35*k,-45*k,26*k],[0,0,4*k]);status.textContent=document.querySelector('#model').value+' - exterior';}
async function load(name){document.querySelector('#results').textContent='';status.textContent='Loading '+name+'…';walking=false;if(model)scene.remove(model);network=null;spec=await fetch('/'+name+'/prework-manifest.json').then(r=>r.json());
 if(spec.archetype_id==='neighborhood_fourplex')spec.camera_roster.push({name:'shower_detail',location:[-2.65,2.1,2.15],target:[-3.6,2.4,1.4],lens:14,whole:false});
 const gltf=await new GLTFLoader().loadAsync('/'+name+'/'+name+'.glb');model=gltf.scene;scene.add(model);let count=0;model.traverse(o=>{if(o.isMesh){count++;o.castShadow=true;o.receiveShadow=true;}if(o.userData.cityprompt_walking_json)network=JSON.parse(o.userData.cityprompt_walking_json);});
 document.querySelector('#view').innerHTML='<option value="">Select an interior view</option>'+spec.camera_roster.filter(c=>!c.whole).map(c=>`<option>${c.name}</option>`).join('');
 status.textContent=`${name} · ${count} meshes · ${network?network.routes.length+' walking routes':'walking metadata pending'}`;exterior();history.replaceState(null,'','?model='+name);localStorage.setItem('neighborhood-review-model',name);}
document.querySelector('#model').onchange=e=>load(e.target.value).catch(e=>status.textContent=e.message);
document.querySelector('#view').onchange=e=>{const c=spec.camera_roster.find(c=>c.name===e.target.value);if(c){view(c.location,c.target,c.lens);status.textContent=document.querySelector('#model').value+' - '+c.name}};
document.querySelector('#exterior').onclick=exterior;document.querySelector('#toggle').onclick=()=>{model.visible=!model.visible;status.textContent=model.visible?'3D model visible':'3D model hidden'};
document.querySelector('#walk').onclick=()=>{if(!network)return;camera.fov=55;camera.updateProjectionMatrix();position=[...network.entrance];yaw=0;walking=true;controls.enabled=false;updateWalk()};
document.querySelector('#forward').onclick=()=>stepWalk(1);document.querySelector('#back').onclick=()=>stepWalk(-1);
function stepWalk(sign){if(!walking)return;for(let i=0;i<5;i++)position=advanceParkWalk(network,position,[position[0]+Math.sin(yaw)*.1*sign,position[1]+Math.cos(yaw)*.1*sign]);updateWalk();}
function updateWalk(){camera.position.copy(v([position[0],position[1],position[2]+1.65]));camera.lookAt(v([position[0]+Math.sin(yaw),position[1]+Math.cos(yaw),position[2]+1.65]));status.textContent='Walking · '+position.map(n=>n.toFixed(2)).join(', ')+' m';}
addEventListener('keydown',e=>keys.add(e.key.toLowerCase()));addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));
document.querySelector('#test').onclick=()=>{if(!network)return;const results=[];
 for(const route of network.routes){let p=[...route.points[0]],worst=0;const startZ=parkWalkHeight(network,p[0],p[1],p[2]);if(startZ===null){results.push({name:route.name,pass:false,reason:'start blocked'});continue;}p[2]=startZ;
  for(const target of route.points.slice(1)){for(let n=0;n<1500;n++){const dist=Math.hypot(target[0]-p[0],target[1]-p[1]);if(dist<.025)break;const step=Math.min(.1,dist);const next=advanceParkWalk(network,p,[p[0]+(target[0]-p[0])*step/dist,p[1]+(target[1]-p[1])*step/dist]);if(Math.hypot(next[0]-p[0],next[1]-p[1])<.001)break;p=next;}worst=Math.max(worst,Math.hypot(target[0]-p[0],target[1]-p[1],target[2]-p[2]));}
  results.push({name:route.name,pass:worst<.10,maxErrorM:+worst.toFixed(3),end:p});}
 const report={model:document.querySelector('#model').value,results,allPassed:results.every(r=>r.pass)};document.querySelector('#results').textContent=JSON.stringify(report,null,2);status.textContent=report.allPassed?'All walking routes passed':'Walking route correction required';window.reviewResults=report;};
let prior=performance.now();function frame(t){requestAnimationFrame(frame);const dt=Math.min(.05,(t-prior)/1000);prior=t;if(walking){if(keys.has('a'))yaw+=dt*1.3;if(keys.has('d'))yaw-=dt*1.3;const move=(keys.has('w')?1:0)-(keys.has('s')?1:0);if(move)position=advanceParkWalk(network,position,[position[0]+Math.sin(yaw)*dt*2*move,position[1]+Math.cos(yaw)*dt*2*move]);updateWalk();}else controls.update();renderer.render(scene,camera);}requestAnimationFrame(frame);
addEventListener('resize',()=>{camera.aspect=(innerWidth-330)/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth-330,innerHeight)});
const chosen=new URLSearchParams(location.search).get('model')||localStorage.getItem('neighborhood-review-model')||'school-v006';document.querySelector('#model').value=chosen;load(chosen).catch(e=>status.textContent=e.message);
