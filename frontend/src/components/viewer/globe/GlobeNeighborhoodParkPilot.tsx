import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { useGLTF, useTexture } from '@react-three/drei';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { neighborhoodParkLayoutForZone, distanceToSegment, envelopeFits, pointInPark, type ParkPoint, type ParkModule } from './neighborhoodParkLayout';
import { getDerivedParkAccess } from './parkAccessConnections';
import { drapeSharedGroundGeometry, type SharedGroundTriangulation } from './sharedGroundGeometry';
import { parkApproachGround, parkPadDatum, roundedParkPad } from './neighborhoodParkGeometry';
import { createMeadowPatch } from './parkPlantingGeometry';

const ROOT = '/landscape-pilots/neighborhood-rustic-v5';
const SKIN = '/park-skins/neighborhood-park-rustic-v0/adaptive-v1';
const OBJECTS = { pavilion: 'gable-pavilion', tower: 'timber-play-tower', swing: 'timber-swing' };
const LIFT = .084;
type Ground = (x: number, y: number) => number;

function polygonGeometry(ring: readonly ParkPoint[], z = LIFT): THREE.BufferGeometry {
  const shape = new THREE.Shape(ring.map(p => new THREE.Vector2(p.x, p.y)));
  const geometry = new THREE.ShapeGeometry(shape);
  geometry.translate(0, 0, z);
  const position = geometry.getAttribute('position');
  const uv = geometry.getAttribute('uv');
  for (let i = 0; i < position.count; i++) uv.setXY(i, position.getX(i) / 3, position.getY(i) / 3);
  return geometry;
}
function pathGeometry(points: readonly ParkPoint[], width: number, closed: boolean): THREE.BufferGeometry {
  const coords: number[] = [], uv: number[] = [];
  const sides=points.map((p,i)=>{
    const before=points[i===0?(closed?points.length-1:0):i-1],after=points[i===points.length-1?(closed?0:i):i+1];
    const direction=(a:ParkPoint,b:ParkPoint)=>{const length=Math.hypot(b.x-a.x,b.y-a.y)||1;return{x:(b.x-a.x)/length,y:(b.y-a.y)/length};};
    const incoming=i===0&&!closed?direction(p,after):direction(before,p),outgoing=i===points.length-1&&!closed?incoming:direction(p,after);
    const nx=-incoming.y-outgoing.y,ny=incoming.x+outgoing.x,length=Math.hypot(nx,ny)||1;
    const bx=nx/length,by=ny/length,denominator=Math.max(.4,bx*(-outgoing.y)+by*outgoing.x),distance=width/2/denominator;
    return[{x:p.x+bx*distance,y:p.y+by*distance},{x:p.x-bx*distance,y:p.y-by*distance}];
  });
  for (let i = 0; i < points.length - (closed ? 0 : 1); i++) {
    const a = points[i], b = points[(i + 1) % points.length], d = Math.hypot(b.x - a.x, b.y - a.y);
    if (d < .001) continue;
    const p = [sides[i][0],sides[i][1],sides[(i+1)%points.length][1],sides[(i+1)%points.length][0]];
    for (const n of [0, 1, 2, 0, 2, 3]) { coords.push(p[n].x, p[n].y, LIFT + .004); uv.push(p[n].x / 3, p[n].y / 3); }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(coords, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  geometry.computeVertexNormals();
  return geometry;
}

export function Surface({ ring, pathWidth, closed = false, role, terrainZ, grid, tint, extraLift = 0 }: {
  ring: readonly ParkPoint[]; pathWidth?: number; closed?: boolean;
  role: 'lawn' | 'safety' | 'paver'; terrainZ: Ground; grid?: SharedGroundTriangulation | null;
  tint?: string;
  extraLift?: number;
}) {
  const loaded = useTexture(`${SKIN}/${role}/albedo.jpg`);
  const texture = useMemo(() => { const t = loaded.clone(); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }, [loaded]);
  const geometry = useMemo(() => {
    const source = pathWidth ? pathGeometry(ring, pathWidth, closed) : polygonGeometry(ring);
    source.translate(0, 0, extraLift);
    const draped = drapeSharedGroundGeometry(source, terrainZ, 3, 100000, grid ?? undefined);
    source.dispose(); return draped;
  }, [ring, pathWidth, closed, terrainZ, grid, extraLift]);
  useEffect(() => () => { texture.dispose(); }, [texture]);
  useEffect(() => () => { geometry?.dispose(); }, [geometry]);
  return geometry ? <mesh geometry={geometry} receiveShadow renderOrder={150} userData={{ parkPilot: true, semanticRole: role }}>
    <meshStandardMaterial map={texture} color={tint ?? (role === 'lawn' ? '#d1cab1' : '#ded7c7')} roughness={.94}
      customProgramCacheKey={() => role === 'lawn' ? 'park-grass-v2' : 'park-gravel-v2'}
      onBeforeCompile={shader => {
        if (role !== 'lawn') return;
        shader.fragmentShader = shader.fragmentShader.replace('#include <map_fragment>', `
          #ifdef USE_MAP
          vec2 q = vMapUv;
          vec4 grass = texture2D(map,q)*0.4 + texture2D(map,mat2(.73,.68,-.68,.73)*q*.71+vec2(.37,.63))*.3 + texture2D(map,q.yx*.43+vec2(.18,.72))*.3;
          grass.rgb *= 1.0 + .055*sin(q.x*.63+sin(q.y*.47)) + .035*sin(q.y*.79+cos(q.x*.37));
          diffuseColor *= grass;
          #endif
        `);
      }} />
  </mesh> : null;
}

function RusticDetail({ asset, point, yaw, terrainZ }: {asset: 'timber-bench' | 'boulders' | 'split-rail'; point: ParkPoint; yaw: number; terrainZ: Ground}) {
  const {scene} = useGLTF(`${ROOT}/${asset}.glb`);
  const clone = useMemo(() => { const c = scene.clone(true); c.traverse(o => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; } }); return c; }, [scene]);
  return <group position={[point.x,point.y,terrainZ(point.x,point.y)+LIFT]} rotation={[0,0,yaw]} userData={{parkPilot: true,semanticRole:asset,fixedMetricObject:true}}>
    <group rotation={[Math.PI/2,0,0]}><primitive object={clone}/></group>
  </group>;
}

function MetricObject({ module, terrainZ }: { module: ParkModule; terrainZ: Ground }) {
  const { scene } = useGLTF(`${ROOT}/${OBJECTS[module.kind]}.glb`);
  const sourceTexture=useTexture(`${SKIN}/${module.kind==='pavilion'?'paver':'safety'}/albedo.jpg`);
  const padTexture=useMemo(()=>{const texture=sourceTexture.clone();texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;return texture;},[sourceTexture]);
  useEffect(()=>()=>padTexture.dispose(),[padTexture]);
  const clone = useMemo(() => { const c = scene.clone(true); c.traverse(o => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; } }); return c; }, [scene]);
  const {high,low} = parkPadDatum(module,terrainZ);
  const padRing = useMemo(() => roundedParkPad(module), [module]);
  // The module stays rigid. A small, explicit graded pad meets the terrain;
  // deep grading is recorded for review rather than silently losing equipment.
  const pad = useMemo(() => {
    const indexed = polygonGeometry(padRing, high + LIFT + .01);
    const top = indexed.toNonIndexed();
    const coords = Array.from(top.getAttribute('position').array);
    top.dispose(); indexed.dispose();
    padRing.forEach((a, i) => {
      const b = padRing[(i + 1) % padRing.length];
      const z0 = terrainZ(a.x, a.y) + .07, z1 = terrainZ(b.x, b.y) + .07, z = high + LIFT + .01;
      coords.push(a.x, a.y, z0, b.x, b.y, z1, b.x, b.y, z, a.x, a.y, z0, b.x, b.y, z, a.x, a.y, z);
    });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(coords, 3));
    const uv:number[]=[];for(let i=0;i<coords.length;i+=3)uv.push(coords[i]/3,coords[i+1]/3);
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals(); return g;
  }, [padRing, high, terrainZ]);
  useEffect(() => () => pad.dispose(), [pad]);
  return <group name={module.id} userData={{ parkPilot: true, fixedMetricObject: true, nonuniformScalingAllowed: false, semanticRole: module.kind, gradingDepthM: high - low, gradingReviewRequired: high - low > .8 }}>
    <mesh geometry={pad} receiveShadow><meshStandardMaterial map={padTexture} color="#ddd3bd" roughness={.96} /></mesh>
    <group position={[module.center.x, module.center.y, high + LIFT + .013]} rotation={[0, 0, module.yaw]}>
      <group rotation={[Math.PI / 2, 0, 0]}><primitive object={clone} /></group>
    </group>
  </group>;
}

function Instances({ geometry, material, points, terrainZ, size = 1 }: {
  geometry: THREE.BufferGeometry; material: THREE.Material | THREE.Material[];
  points: readonly ParkPoint[]; terrainZ: Ground; size?: number;
}) {
  const ref = useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(() => {
    if (!ref.current) return;
    const dummy = new THREE.Object3D();
    points.forEach((p, i) => {
      dummy.position.set(p.x, p.y, terrainZ(p.x, p.y) + LIFT);
      dummy.rotation.set(0, 0, i * 2.39996);
      dummy.scale.setScalar(size * (.9 + (i % 5) * .045)); dummy.updateMatrix();
      ref.current!.setMatrixAt(i, dummy.matrix);
    });
    ref.current.instanceMatrix.needsUpdate = true;
    ref.current.computeBoundingSphere();
  }, [points, terrainZ, size]);
  return <instancedMesh ref={ref} args={[geometry, material, points.length]} castShadow receiveShadow />;
}

export function Woodland({ points, variant, terrainZ }: { points: readonly ParkPoint[]; variant: number; terrainZ: Ground }) {
  const { scene } = useGLTF(`${ROOT}/oak-${variant}.glb`);
  const parts = useMemo(() => {
    scene.updateMatrixWorld(true);
    const result: Array<{ geometry: THREE.BufferGeometry; material: THREE.Material | THREE.Material[] }> = [];
    scene.traverse(o => {
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      const geometry = mesh.geometry.clone().applyMatrix4(mesh.matrixWorld).rotateX(Math.PI / 2);
      result.push({ geometry, material: mesh.material });
    }); return result;
  }, [scene]);
  useEffect(() => () => parts.forEach(part => part.geometry.dispose()), [parts]);
  return <group name={`woodland-${variant}`}>{parts.map((part, i) => <Instances key={i} {...part} points={points} terrainZ={terrainZ} />)}</group>;
}

function Wildflowers({ points, terrainZ }: { points: readonly ParkPoint[]; terrainZ: Ground }) {
  const geometry = useMemo(createMeadowPatch, []);
  const material = useMemo(() => new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: .9 }), []);
  useEffect(() => () => { geometry.dispose(); material.dispose(); }, [geometry, material]);
  return <Instances geometry={geometry} material={material} points={points} terrainZ={terrainZ} />;
}

export function GlobeNeighborhoodParkPilot({ zone, centroid, terrainZ, groundGrid }: {
  zone: SiteZone; centroid: { lng: number; lat: number }; terrainZ: Ground; groundGrid?: SharedGroundTriangulation | null;
}) {
  const layout = useMemo(() => neighborhoodParkLayoutForZone(zone, centroid), [zone, centroid]);
  const access = getDerivedParkAccess(zone);
  const entryPaths = useMemo(() => (access?.paths ?? []).map(path => path.points.map(([lng, lat]) => ({ x: (lng - centroid.lng) * metersPerDegLon(centroid.lat), y: (lat - centroid.lat) * METERS_PER_DEG_LAT }))), [access, centroid]);
  const approaches = useMemo(() => layout.paths.map((path,i) => parkApproachGround(layout.modules[i],path,terrainZ)), [layout,terrainZ]);
  const clearOfEntrances = (p: ParkPoint, clearance: number) => entryPaths.every(path => path.every((q, i) => i === 0 || distanceToSegment(p, path[i - 1], q) > clearance));
  const trees = layout.trees.filter(p => clearOfEntrances(p, 3));
  const flowers = layout.shrubs.filter(p => clearOfEntrances(p, 2.2));
  const details = useMemo(() => {
    if (!layout.loop.length) return [];
    const center = layout.loop.reduce((a,p) => ({x:a.x+p.x/64,y:a.y+p.y/64}),{x:0,y:0});
    return [7,21,38,52].flatMap((index,i) => {
      const q=layout.loop[index], dx=q.x-center.x,dy=q.y-center.y,d=Math.hypot(dx,dy), offset=i===2?4:2.8;
      const p={x:q.x+dx/d*offset,y:q.y+dy/d*offset}, radius=i===2?3:1.6;
      const envelope=[{x:p.x-radius,y:p.y-radius},{x:p.x+radius,y:p.y-radius},{x:p.x+radius,y:p.y+radius},{x:p.x-radius,y:p.y+radius}];
      if (!envelopeFits(envelope,layout.boundary,.2) || layout.modules.some(m=>envelope.some(v=>pointInPark(v,m.envelope)))) return [];
      return [{asset: i===2?'boulders' as const:'timber-bench' as const, point:p, yaw:Math.atan2(dy,dx)-Math.PI/2}];
    });
  },[layout]);
  return <group name="neighborhood-park-adaptive-rustic-v1" userData={{ parkPilot: true, layoutStatus: layout.status, notes: layout.notes }}>
    <Surface ring={layout.boundary} role="lawn" terrainZ={terrainZ} grid={groundGrid} />
    {layout.lawn.length > 0 && <Surface ring={layout.lawn} role="lawn" tint="#c4d4b0" extraLift={.001} terrainZ={terrainZ} grid={groundGrid} />}
    {layout.loop.length > 0 && <Surface ring={layout.loop} closed pathWidth={layout.pathWidth} role="safety" terrainZ={terrainZ} grid={groundGrid} />}
    {layout.paths.map((path, i) => <Surface key={`approach-${i}`} ring={path} pathWidth={layout.pathWidth} role="safety" terrainZ={approaches[i]} grid={groundGrid} />)}
    {entryPaths.map((path, i) => <Surface key={`entry-${i}`} ring={path} pathWidth={2.2} role="safety" terrainZ={terrainZ} grid={groundGrid} />)}
    {layout.modules.map(module => <MetricObject key={module.id} module={module} terrainZ={terrainZ} />)}
    {layout.modules.filter(m=>m.kind==='tower').flatMap(module=>[-1,1].map(side=> {
      const localArrivalY = module.arrival ? -(module.arrival.x-module.center.x)*Math.sin(module.yaw)+(module.arrival.y-module.center.y)*Math.cos(module.yaw) : -1;
      const x=side*2.35,y=(localArrivalY>0?-1:1)*(module.depth/2-.5);
      const point={x:module.center.x+Math.cos(module.yaw)*x-Math.sin(module.yaw)*y,y:module.center.y+Math.sin(module.yaw)*x+Math.cos(module.yaw)*y};
      const padHeight = parkPadDatum(module, terrainZ).high + .013;
      return <RusticDetail key={`${module.id}-rail-${side}`} asset="split-rail" point={point} yaw={module.yaw} terrainZ={() => padHeight}/>;
    }))}
    {details.filter(detail=>clearOfEntrances(detail.point,3)).map((detail,i)=><RusticDetail key={`detail-${i}`} {...detail} terrainZ={terrainZ}/>)}
    {[0, 1, 2].map(variant => <Woodland key={variant} variant={variant} points={trees.filter((_, i) => i % 3 === variant)} terrainZ={terrainZ} />)}
    <Wildflowers points={flowers} terrainZ={terrainZ} />
  </group>;
}
