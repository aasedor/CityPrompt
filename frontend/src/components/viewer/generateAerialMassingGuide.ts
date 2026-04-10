/**
 * generateAerialMassingGuide — renders a color-coded 3D massing model from the
 * aerial camera's perspective to guide Gemini on building facade orientation.
 *
 * Orange-red faces labeled "FRONT" = main entrance facade
 * Steel blue faces labeled "REAR" = service/back wall
 * Amber faces = side walls
 * Gray = roof / zones without orientation
 *
 * Only generated when at least one zone has `entrance_facing` set.
 */
import * as THREE from 'three';
import type { SiteZone } from '@/types';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GUIDE_WIDTH = 1024;
const GUIDE_HEIGHT = 1024;
const DEG_TO_RAD = Math.PI / 180;
const METERS_PER_DEG_LAT = 110_540;
const FLOOR_HEIGHT_M = 3.2;

// Orientation color scheme
const COLOR_FRONT = '#FF4400';   // orange-red — entrance facade
const COLOR_REAR = '#4466AA';    // steel blue — back wall
const COLOR_SIDE = '#FFAA00';    // amber — side walls
const COLOR_ROOF = '#CCCCCC';    // light gray — roof
const COLOR_GROUND = '#444444';  // dark gray — ground
const COLOR_NEUTRAL = '#B0B0B0'; // neutral — zones without orientation
const COLOR_PARK = '#4CAF50';    // green — parks
const COLOR_ROAD = '#757575';    // gray — roads

const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use', 'development_area'];

// ---------------------------------------------------------------------------
// Canvas-texture material with baked text label
// ---------------------------------------------------------------------------

function createLabeledMaterial(text: string, bgColor: string): THREE.MeshBasicMaterial {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;

  // Fill background
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, 256, 256);

  // Draw text label if provided
  if (text) {
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 44px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    // Black outline for readability
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 4;
    ctx.strokeText(text, 128, 128);
    ctx.fillText(text, 128, 128);
  }

  const texture = new THREE.CanvasTexture(canvas);
  return new THREE.MeshBasicMaterial({ map: texture });
}

function createFlatMaterial(color: string): THREE.MeshBasicMaterial {
  return new THREE.MeshBasicMaterial({ color: new THREE.Color(color) });
}

// ---------------------------------------------------------------------------
// Build 6-material array for an oriented building box
// BoxGeometry groups: 0=+X, 1=-X, 2=+Y(roof), 3=-Y(ground), 4=+Z, 5=-Z
// ---------------------------------------------------------------------------

function buildOrientedMaterials(): THREE.MeshBasicMaterial[] {
  return [
    createFlatMaterial(COLOR_SIDE),            // 0: +X side
    createFlatMaterial(COLOR_SIDE),            // 1: -X side
    createFlatMaterial(COLOR_ROOF),            // 2: +Y roof
    createFlatMaterial(COLOR_GROUND),          // 3: -Y ground
    createLabeledMaterial('FRONT', COLOR_FRONT), // 4: +Z entrance
    createLabeledMaterial('REAR', COLOR_REAR),   // 5: -Z rear
  ];
}

function buildNeutralMaterials(): THREE.MeshBasicMaterial[] {
  const mat = createFlatMaterial(COLOR_NEUTRAL);
  return [mat, mat, createFlatMaterial(COLOR_ROOF), createFlatMaterial(COLOR_GROUND), mat, mat];
}

// ---------------------------------------------------------------------------
// Main generator
// ---------------------------------------------------------------------------

export function generateAerialMassingGuide(
  mapCenter: [number, number],  // [lng, lat]
  mapBearing: number,           // degrees (0=north, clockwise)
  mapPitch: number,             // degrees (0=top-down, 60=oblique)
  mapZoom: number,
  zones: SiteZone[],
): string {
  // --- Renderer ---
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: false,
    preserveDrawingBuffer: true,
  });
  renderer.setSize(GUIDE_WIDTH, GUIDE_HEIGHT);
  renderer.setClearColor(0xe8e8e8, 1); // light gray background

  const scene = new THREE.Scene();

  // --- Camera: match Mapbox aerial viewpoint ---
  const pitchRad = mapPitch * DEG_TO_RAD;
  const bearingRad = mapBearing * DEG_TO_RAD;

  // Approximate camera altitude from zoom level
  // At zoom 0, world = 512px = ~40075km. Camera altitude scales with zoom.
  const metersPerPixel = 40_075_016 / (512 * Math.pow(2, mapZoom));
  const sceneExtent = GUIDE_HEIGHT * metersPerPixel; // approximate scene size in meters
  const cameraAltitude = Math.max(sceneExtent * 0.8, 100); // ensure minimum altitude

  const camera = new THREE.PerspectiveCamera(45, GUIDE_WIDTH / GUIDE_HEIGHT, 1, cameraAltitude * 4);

  // Position camera above and behind based on pitch and bearing
  const horizontalDist = cameraAltitude * Math.tan(pitchRad);
  const camX = -horizontalDist * Math.sin(bearingRad);
  const camZ = -horizontalDist * Math.cos(bearingRad);
  const camY = cameraAltitude * Math.cos(pitchRad);

  camera.position.set(camX, camY, camZ);
  camera.lookAt(0, 0, 0);

  // --- Lighting (simple, just for edge definition) ---
  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
  dirLight.position.set(-30, 80, -20);
  scene.add(dirLight);

  // --- Ground plane ---
  const groundSize = cameraAltitude * 3;
  const groundGeo = new THREE.PlaneGeometry(groundSize, groundSize);
  const groundMat = new THREE.MeshBasicMaterial({ color: 0x9e9e9e });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.1;
  scene.add(ground);

  // --- Coordinate conversion ---
  const [centerLng, centerLat] = mapCenter;
  const metersPerDegLng = METERS_PER_DEG_LAT * Math.cos(centerLat * DEG_TO_RAD);

  function toLocal(lng: number, lat: number): [number, number] {
    const x = (lng - centerLng) * metersPerDegLng;
    const z = -(lat - centerLat) * METERS_PER_DEG_LAT;
    return [x, z];
  }

  function getPolygonCentroid(coords: number[][]): [number, number] {
    let sumLng = 0, sumLat = 0;
    for (const c of coords) { sumLng += c[0]; sumLat += c[1]; }
    return [sumLng / coords.length, sumLat / coords.length];
  }

  function getPolygonExtent(coords: number[][]): { minLng: number; maxLng: number; minLat: number; maxLat: number } {
    let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
    for (const c of coords) {
      if (c[0] < minLng) minLng = c[0];
      if (c[0] > maxLng) maxLng = c[0];
      if (c[1] < minLat) minLat = c[1];
      if (c[1] > maxLat) maxLat = c[1];
    }
    return { minLng, maxLng, minLat, maxLat };
  }

  // --- Build zone meshes ---
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;

    const centroid = getPolygonCentroid(zone.coordinates);
    const [cx, cz] = toLocal(centroid[0], centroid[1]);

    const extent = getPolygonExtent(zone.coordinates);
    const [minLocalX, minLocalZ] = toLocal(extent.minLng, extent.maxLat);
    const [maxLocalX, maxLocalZ] = toLocal(extent.maxLng, extent.minLat);
    const widthM = Math.abs(maxLocalX - minLocalX);
    const depthM = Math.abs(maxLocalZ - minLocalZ);

    if (widthM < 1 && depthM < 1) continue;

    const isBuilding = BUILDING_TYPES.includes(zone.zone_type);

    if (isBuilding) {
      const floors = Number(zone.properties?.floors) || Number(zone.properties?.max_floors) || 4;
      const heightM = floors * FLOOR_HEIGHT_M;
      const entranceFacing = typeof zone.properties?.entrance_facing === 'number'
        ? zone.properties.entrance_facing
        : null;

      const geo = new THREE.BoxGeometry(
        Math.max(widthM, 5),
        heightM,
        Math.max(depthM, 5),
      );

      let mesh: THREE.Mesh;
      if (entranceFacing !== null) {
        // Oriented building — color-coded faces with labels
        const materials = buildOrientedMaterials();
        mesh = new THREE.Mesh(geo, materials);
        // Rotate so +Z face (FRONT) points toward entrance_facing direction
        // entrance_facing: 0=North, 90=East, etc.
        // Three.js: +Z default is "south" in our coord system (negative lat direction)
        // To align +Z with north (0°), we need rotation.y = Math.PI
        // To align +Z with east (90°), rotation.y = Math.PI/2
        // General: rotation.y = Math.PI - (entrance_facing * DEG_TO_RAD)
        mesh.rotation.y = Math.PI - (entranceFacing * DEG_TO_RAD);
      } else {
        // No orientation set — neutral gray, let Gemini choose
        const materials = buildNeutralMaterials();
        mesh = new THREE.Mesh(geo, materials);
      }

      mesh.position.set(cx, heightM / 2, cz);
      scene.add(mesh);

      // Edge lines for definition
      const edges = new THREE.EdgesGeometry(geo);
      const lineMat = new THREE.LineBasicMaterial({ color: 0x333333, opacity: 0.6, transparent: true });
      const lineSegments = new THREE.LineSegments(edges, lineMat);
      lineSegments.position.copy(mesh.position);
      lineSegments.rotation.copy(mesh.rotation);
      scene.add(lineSegments);

    } else if (['green_space', 'park', 'plaza'].includes(zone.zone_type as string)) {
      // Parks: flat green plane
      const pw = Math.max(widthM, 5);
      const pd = Math.max(depthM, 5);
      const parkGeo = new THREE.BoxGeometry(pw, 0.3, pd);
      const parkMat = createFlatMaterial(COLOR_PARK);
      const parkMesh = new THREE.Mesh(parkGeo, parkMat);
      parkMesh.position.set(cx, 0.15, cz);
      scene.add(parkMesh);

    } else if (['road', 'street', 'path'].includes(zone.zone_type as string)) {
      // Roads: flat gray plane
      const rw = Math.max(widthM, 3);
      const rd = Math.max(depthM, 3);
      const roadGeo = new THREE.BoxGeometry(rw, 0.1, rd);
      const roadMat = createFlatMaterial(COLOR_ROAD);
      const roadMesh = new THREE.Mesh(roadGeo, roadMat);
      roadMesh.position.set(cx, 0.05, cz);
      scene.add(roadMesh);
    }
  }

  // --- Render and capture ---
  renderer.render(scene, camera);
  const dataUrl = renderer.domElement.toDataURL('image/png');

  // --- Cleanup ---
  renderer.dispose();
  scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.geometry.dispose();
      if (Array.isArray(obj.material)) {
        obj.material.forEach((m: THREE.Material) => {
          if ((m as THREE.MeshBasicMaterial).map) {
            (m as THREE.MeshBasicMaterial).map!.dispose();
          }
          m.dispose();
        });
      } else {
        if ((obj.material as THREE.MeshBasicMaterial).map) {
          (obj.material as THREE.MeshBasicMaterial).map!.dispose();
        }
        obj.material.dispose();
      }
    }
  });

  console.log(`[AIRender] Orientation guide generated — ${zones.filter(z => typeof z.properties?.entrance_facing === 'number').length} oriented zones`);

  return dataUrl.split(',')[1]; // raw base64
}
