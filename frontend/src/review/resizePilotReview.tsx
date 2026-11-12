// Building resize pilot · eye-tuning page. A development tool, not part of the app.
//
//   npm run dev, then open /resize-pilot-review.html?view=compare
//   views: compare | stretch | massing | panel-exact | panel-stretched | panel-free-auto | panel-free-l
//   &model=<URL of final-seniors-apartments-clay-v003.glb> shows the exact model.
//
// It runs the real code: the panel components, the plan transform, the rigid
// prop pass and the massing geometry, with values from buildingResizeTrial.json.
// Lighting and ground are this page's own. It is not the app's globe, so it
// tunes proportions and colour; it does not replace a check in the viewer.
import '../index.css';
import { useEffect, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { ReshapePanel } from '@/features/pickPlace/ReshapePanel';
import { placeAsset, placementProperties } from '@/features/pickPlace/catalogue';
import { rectangleAt } from '@/features/pickPlace/geometry';
import {
  buildingResizeTrialEnabled, exactModelProperties, resizeTrialFamilyForAsset, resizeTrialMassingDressing,
  resizeTrialPlotFor, shapeFreelyProperties,
} from '@/features/pickPlace/buildingResizeTrial';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { keepPropsRigidUnderStretch } from '@/features/legoAssembly/resizeTrialRigidProps';
import { legoInstanceTransform } from '@/components/viewer/globe/legoGlobePlacement';
import { prepareArchitecturalClone } from '@/components/viewer/globe/modelMaterialQuality';
import {
  buildLegoMassingDressingData, buildLegoMassingKitData, buildLegoMassingMeshData, legoMassingColor,
  type LegoMassingColoredMesh, type LegoMassingMeshData,
} from '@/components/viewer/globe/legoMassingGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

declare global { interface Window { __ready?: boolean; __error?: string } }
const query = new URLSearchParams(location.search);
const view = query.get('view') ?? 'compare';
const modelUrl = query.get('model');
const REFERENCE = '/archetypes/buildings/final-seniors-apartments';
const asset = placeAsset('final_seniors_apartments');
const family = resizeTrialFamilyForAsset(asset, true)!;
const centre = [-114.0719, 51.0447];
const ll = (x: number, y: number) => [centre[0] + x / metersPerDegLon(centre[1]), centre[1] + y / METERS_PER_DEG_LAT];
const rectangle = (width: number, depth: number) => [ll(-width / 2, -depth / 2), ll(width / 2, -depth / 2), ll(width / 2, depth / 2), ll(-width / 2, depth / 2)];
const L_SHAPE = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];

// Pages render several canvases; the page is ready when every one has drawn.
let pending = 0;
const started = () => { pending += 1; };
const finished = () => { pending -= 1; if (pending <= 0) requestAnimationFrame(() => { window.__ready = true; }); };

// ------------------------------------------------------------------ panels
function Panel({ properties, coordinates }: { properties: SiteZoneProperties; coordinates: number[][] }) {
  const zone = { id: 'midrise', project_id: 'project', zone_type: 'building', name: 'Mid-rise', color: '#fff', sort_order: 0,
    created_at: 'now', updated_at: 'now', coordinates, properties } as SiteZone;
  const site = { ...zone, id: 'site', zone_type: 'site_boundary', is_active_boundary: true, properties: {},
    coordinates: rectangleAt(centre, 100, 100) } as SiteZone;
  const stage = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const last = stage.current!.querySelector('aside')!.lastElementChild as HTMLElement;
    stage.current!.style.height = `${112 + last.offsetTop + last.offsetHeight + 32}px`;
    requestAnimationFrame(() => { window.__ready = true; });
  }, []);
  return <div id="stage" ref={stage} style={{ position: 'relative', width: 340, height: 1500 }}>
    <ReshapePanel zone={zone} zones={[site, zone]} disabled={false} onDuplicate={() => {}} onReshape={() => true}
      onClose={() => {}} onDelete={() => {}} onMore={() => {}} onUpdateDesign={() => {}} />
  </div>;
}
const PANELS: Record<string, () => { properties: SiteZoneProperties; coordinates: number[][] }> = {
  'panel-exact': () => ({ properties: placementProperties(asset), coordinates: rectangleAt(centre, 36.4, 22, 15) }),
  'panel-stretched': () => ({ properties: exactModelProperties(placementProperties(asset), family, 1.2, 0.9, asset),
    coordinates: rectangleAt(centre, 44, 22, 15) }),
  'panel-free-auto': () => ({ properties: shapeFreelyProperties(placementProperties(asset), 'stretch_out_of_band'),
    coordinates: rectangleAt(centre, 50, 17.98, 15) }),
  'panel-free-l': () => ({ properties: shapeFreelyProperties(placementProperties(asset)), coordinates: L_SHAPE }),
};

// ------------------------------------------------------------------ 3D stage
interface Shot { azimuth: number; elevation: number; distance: number; lookAt?: [number, number, number]; fov?: number }

function Canvas3D({ build, shot, width = 560, height = 380, grid = false }: {
  build: (scene: THREE.Scene) => void | Promise<void>; shot: Shot; width?: number; height?: number; grid?: boolean;
}) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    started();
    let disposed = false;
    const renderer = new THREE.WebGLRenderer({ canvas: ref.current!, antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(2);
    renderer.setSize(width, height, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.82;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const scene = new THREE.Scene();
    // Late-afternoon light, like the reference photographs.
    const sky = document.createElement('canvas'); sky.width = 4; sky.height = 256;
    const paint = sky.getContext('2d')!, gradient = paint.createLinearGradient(0, 0, 0, 256);
    gradient.addColorStop(0, '#8fb6e0'); gradient.addColorStop(0.55, '#cfe0ee'); gradient.addColorStop(1, '#f1ead9');
    paint.fillStyle = gradient; paint.fillRect(0, 0, 4, 256);
    const background = new THREE.CanvasTexture(sky); background.colorSpace = THREE.SRGBColorSpace;
    scene.background = background;
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.28;
    scene.add(new THREE.HemisphereLight('#cfe0f2', '#8f8672', 0.42));
    const sun = new THREE.DirectionalLight('#ffd9a3', 3.6);
    sun.position.set(-62, 58, 96); sun.castShadow = true;
    sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.12;
    Object.assign(sun.shadow.camera, { left: -80, right: 80, top: 80, bottom: -80, near: 1, far: 320 });
    scene.add(sun);
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), new THREE.MeshStandardMaterial({ color: '#aeb0a2', roughness: 1 }));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -0.02; ground.receiveShadow = true; scene.add(ground);
    if (grid) scene.add(new THREE.GridHelper(200, 40, '#a39f92', '#b9b5a8')); // 5 m squares
    Promise.resolve(build(scene)).then(() => {
      if (disposed) return;
      const camera = new THREE.PerspectiveCamera(shot.fov ?? 30, width / height, 1, 1200);
      const az = shot.azimuth * Math.PI / 180, el = shot.elevation * Math.PI / 180, look = shot.lookAt ?? [0, 8, 0];
      camera.position.set(look[0] + Math.sin(az) * Math.cos(el) * shot.distance, look[1] + Math.sin(el) * shot.distance,
        look[2] + Math.cos(az) * Math.cos(el) * shot.distance);
      camera.lookAt(...look);
      renderer.render(scene, camera); renderer.render(scene, camera);
    }).catch(error => { window.__error = String(error); }).finally(finished);
    return () => { disposed = true; renderer.dispose(); pmrem.dispose(); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps -- one fixed scene per canvas
  return <canvas ref={ref} style={{ width, height, display: 'block', borderRadius: 8 }} />;
}

const shadows = (object: THREE.Object3D) => object.traverse(child => {
  if ((child as THREE.Mesh).isMesh) { child.castShadow = true; child.receiveShadow = true; }
});

const gltf = modelUrl ? new GLTFLoader().loadAsync(modelUrl) : null;
/** The exact model, placed by the same steps as GlobeLegoAssemblyLayer. */
async function addExactModel(scene: THREE.Scene, widthScale: number, depthScale: number, centreOn: 'block' | 'model' = 'block') {
  if (!gltf) throw new Error('Add &model=<URL of the GLB> to see the exact model.');
  const prepared = prepareArchitecturalClone((await gltf).scene.clone(true), { renderOrder: 0, maxAnisotropy: 8,
    ambientOcclusion: 'disable', preserveSourcePbr: true, restyleUntextured: false });
  const model = centreNativeClayClone(prepared);
  keepPropsRigidUnderStretch(model, widthScale, depthScale);
  const transform = legoInstanceTransform({ position: [0, 0, 0], scale: [widthScale, depthScale, 1], rotation_degrees: 0 } as never);
  model.position.set(...transform.position); model.scale.set(...transform.scale); model.rotation.y = transform.rotationYRad;
  // The model's box centre is 4 m right of its main block's centre. 'block'
  // puts the main block in front of the camera, to compare like with like.
  if (centreOn === 'block') model.position.x += 4 * widthScale;
  shadows(model); scene.add(model);
}

/** A freely shaped building, drawn by the same functions as the viewer layer. */
function addMassing(scene: THREE.Scene, ring: number[][], style?: 'archetype_kit' | 'floor_lines_and_windows') {
  const dressing = resizeTrialMassingDressing(shapeFreelyProperties(placementProperties(asset)), true, style)!;
  const group = new THREE.Group(); group.rotation.x = -Math.PI / 2; // viewer frame is Z-up
  const add = (part: LegoMassingMeshData | LegoMassingColoredMesh, color: string | undefined, roughness: number) => {
    if (!part.indices.length) return;
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(part.positions, 3));
    if ('colors' in part) geometry.setAttribute('color', new THREE.Float32BufferAttribute(part.colors, 3));
    geometry.setIndex(part.indices); geometry.computeVertexNormals();
    group.add(new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: color ?? '#ffffff',
      vertexColors: color === undefined, roughness, metalness: 0.02, side: THREE.DoubleSide })));
  };
  let caption = '';
  if (dressing.kind === 'kit') {
    const data = buildLegoMassingKitData(ring, centre[0], centre[1], dressing.kit)!;
    add(data.solid, undefined, 0.78); add(data.glass, undefined, 0.4);
    caption = data.walls.map(wall => wall.bays.map(bay => bay === 'loggia' ? 'B' : 'W').join('') || '–').join(' · ');
  } else {
    add(buildLegoMassingMeshData(ring, centre[0], centre[1], family.nativeHeightM)!, legoMassingColor('final-seniors-apartments:review'), 0.82);
    const data = buildLegoMassingDressingData(ring, centre[0], centre[1], family.nativeHeightM, dressing)!;
    add(data.floorLines, dressing.floorLineColor, 0.9); add(data.windows, dressing.windowColor, 0.35);
    caption = `bays ${data.baysPerWall.join(', ')}`;
  }
  shadows(group); scene.add(group);
  return caption;
}

function plotOutline(scene: THREE.Scene, widthM: number, depthM: number) {
  const points = [[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]].map(([x, z]) => new THREE.Vector3(x * widthM / 2, 0.05, z * depthM / 2));
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), new THREE.LineBasicMaterial({ color: '#2f6f00' })));
}

function Figure({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return <figure style={{ margin: 0 }}>{children}
    <figcaption style={{ padding: '6px 2px 14px', fontSize: 15 }}><b>{title}</b>{note ? ` — ${note}` : ''}</figcaption></figure>;
}
function Sheet({ title, note, columns = 2, children }: { title: string; note: string; columns?: number; children: React.ReactNode }) {
  return <div id="stage" style={{ padding: 20, width: columns * 580 }}>
    <h1 style={{ margin: '0 0 4px', fontSize: 22 }}>{title}</h1>
    <p style={{ margin: '0 0 14px', fontSize: 14, color: '#444' }}>{note}</p>
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, 560px)`, gap: '0 20px' }}>{children}</div>
  </div>;
}
function Reference({ file }: { file: string }) {
  useEffect(() => { started(); }, []);
  return <img src={`${REFERENCE}/${file}`} alt="" onLoad={finished} onError={finished}
    style={{ width: 560, height: 380, objectFit: 'cover', display: 'block', borderRadius: 8 }} />;
}
const NOTE = 'Review page: real model, real placement and massing code, this page’s own lighting. Not the app’s globe.';
const FRONT: Shot = { azimuth: 0, elevation: 7, distance: 62, lookAt: [0, 8.2, 0], fov: 30 };
const OBLIQUE: Shot = { azimuth: 38, elevation: 27, distance: 70, lookAt: [3, 6, 0], fov: 30 };
const STRETCHES = [[0.7, 1], [1, 1], [1.4, 1], [1, 0.7], [1, 1.4], [0.7, 1.4]];

function App() {
  if (!buildingResizeTrialEnabled()) return <p style={{ padding: 20 }}>Start the dev server with VITE_ENABLE_BUILDING_RESIZE_TRIAL=true.</p>;
  if (PANELS[view]) return <Panel {...PANELS[view]()} />;
  if (view === 'compare') return <Sheet columns={3} title="Reference · Exact model · Shape freely" note={NOTE}>
    <Figure title="Archetype reference" note="front"><Reference file="front.png" /></Figure>
    <Figure title="Exact model, 100%"><Canvas3D shot={FRONT} build={scene => addExactModel(scene, 1, 1)} /></Figure>
    <Figure title="Shape freely, same 24 × 16 m block"><Canvas3D shot={FRONT} build={scene => { addMassing(scene, rectangle(24, 16)); }} /></Figure>
    <Figure title="Archetype reference" note="oblique"><Reference file="oblique.png" /></Figure>
    <Figure title="Exact model, 100%"><Canvas3D shot={OBLIQUE} build={scene => addExactModel(scene, 1, 1)} /></Figure>
    <Figure title="Shape freely, same 24 × 16 m block"><Canvas3D shot={OBLIQUE} build={scene => { addMassing(scene, rectangle(24, 16)); }} /></Figure>
  </Sheet>;
  if (view === 'stretch') return <Sheet title="Exact model · stretched in width and depth"
    note={`${NOTE} Trees and shrubs keep their real proportions. Green line: the plot each stretch needs. 5 m grid.`}>
    {STRETCHES.map(([width, depth]) => <Figure key={`${width}-${depth}`} title={`Width ${Math.round(width * 100)}% · Depth ${Math.round(depth * 100)}%`}
      note={`${(family.nativeWidthM * width).toFixed(1)} × ${(family.nativeDepthM * depth).toFixed(1)} m, height unchanged`}>
      <Canvas3D grid shot={{ azimuth: 30, elevation: 24, distance: 86, lookAt: [0, 6, 0] }} build={async scene => {
        await addExactModel(scene, width, depth, 'model');
        const plot = resizeTrialPlotFor(family, width, depth);
        plotOutline(scene, plot.widthM, plot.depthM);
      }} /></Figure>)}
  </Sheet>;
  if (view === 'massing') return <Sheet title="Shape freely · facade kit on any outline"
    note={`${NOTE} W = window bay, B = balcony bay, per wall from the front. Bays repeat on fixed modules. 5 m grid.`}>
    {([['Model footprint 32.4 × 18.0 m', rectangle(32.36, 17.98), { azimuth: 28, elevation: 22, distance: 84 }],
      ['Automatic handover 50 × 18 m', rectangle(50, 18), { azimuth: 28, elevation: 22, distance: 104 }],
      ['L shape 50 × 30 m', L_SHAPE, { azimuth: -32, elevation: 30, distance: 112 }],
      ['Five-corner outline', [ll(-22, -12), ll(18, -14), ll(24, 4), ll(2, 14), ll(-20, 8)], { azimuth: 24, elevation: 28, distance: 98 }],
      ['Minimum 9 × 12 m', rectangle(9, 12), { azimuth: 28, elevation: 20, distance: 62 }],
      ['Long bar 90 × 12 m', rectangle(90, 12), { azimuth: 24, elevation: 18, distance: 150 }],
    ] as [string, number[][], Omit<Shot, 'lookAt'>][]).map(([title, ring, shot]) => <MassingFigure key={title} title={title} ring={ring} shot={{ ...shot, lookAt: [0, 7, 0] }} />)}
  </Sheet>;
  return <p style={{ padding: 20 }}>Unknown view. Try ?view=compare, stretch, massing or panel-exact.</p>;
}
function MassingFigure({ title, ring, shot }: { title: string; ring: number[][]; shot: Shot }) {
  const caption = useRef<HTMLSpanElement>(null);
  return <figure style={{ margin: 0 }}>
    <Canvas3D grid shot={shot} build={scene => { const text = addMassing(scene, ring); if (caption.current) caption.current.textContent = text; }} />
    <figcaption style={{ padding: '6px 2px 14px', fontSize: 15 }}><b>{title}</b> — <span ref={caption} /></figcaption>
  </figure>;
}
ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
