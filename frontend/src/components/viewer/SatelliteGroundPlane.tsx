import { useRef, useEffect, useMemo } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

const STYLE_URLS: Record<string, string> = {
  satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
  streets: 'mapbox://styles/mapbox/streets-v12',
  terrain: 'mapbox://styles/mapbox/outdoors-v12',
};

// Meters per degree at equator
const METERS_PER_DEG_LAT = 111320;

// Meters per pixel at zoom level 0 at the equator (Web Mercator)
// Mapbox GL v3 uses 512px tiles internally, so effective m/px at z0 is halved
// compared to the classic 256px-tile value (156543.03392).
// Used only for computing a target Mapbox zoom level (tile detail), NOT for mesh scale.
const MAPBOX_METERS_PER_PIXEL_Z0 = 78271.517;

// Offscreen map resolution
const MAP_SIZE = 2048;

// Texture update throttle
const UPDATE_INTERVAL_MS = 100;

// How long camera must be stationary before we stop updating
const IDLE_THRESHOLD_MS = 500;

/**
 * Measure the actual ground-plane width (in meters) that the Mapbox viewport
 * covers at its current zoom/center. Uses map.unproject() so the result is
 * always correct regardless of Mapbox GL version or internal tile size.
 */
function measureGroundSize(map: mapboxgl.Map, cosLat: number): number {
  const left = map.unproject([0, MAP_SIZE / 2]);
  const right = map.unproject([MAP_SIZE, MAP_SIZE / 2]);
  const mPerDegLon = METERS_PER_DEG_LAT * cosLat;
  return (right.lng - left.lng) * mPerDegLon;
}

interface SatelliteGroundPlaneProps {
  projectLat: number;
  projectLng: number;
  mapLayer: string;
}

/**
 * Static ground plane: the mesh NEVER moves from the project origin.
 * The Mapbox texture is ALWAYS centered on (projectLng, projectLat).
 * Only the mesh scale and Mapbox zoom level change based on camera distance.
 *
 * Because the mesh center and texture center are the same fixed geographic
 * point, zones (which are also positioned relative to the same origin)
 * always align perfectly — no drift is possible.
 */
export function SatelliteGroundPlane({ projectLat, projectLng, mapLayer }: SatelliteGroundPlaneProps) {
  const { camera } = useThree();
  const meshRef = useRef<THREE.Mesh>(null);
  const matRef = useRef<THREE.MeshStandardMaterial>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const textureRef = useRef<THREE.CanvasTexture | null>(null);
  const lastUpdateTime = useRef(0);
  const lastCamPos = useRef(new THREE.Vector3());
  const lastCamQuat = useRef(new THREE.Quaternion());
  const lastMoveTime = useRef(performance.now());
  const isMapReady = useRef(false);
  const currentStyleRef = useRef(mapLayer);
  const textureAttached = useRef(false);
  const lastZoom = useRef(16);
  const mapRepainted = useRef(false);
  const pendingRepaint = useRef(false);
  const idleFinalUpdate = useRef(false);
  // Ground size measured from actual Mapbox viewport (meters)
  const lastGroundSize = useRef(0);

  const origin = useMemo(() => ({
    lat: projectLat,
    lng: projectLng,
    metersPerDegLon: METERS_PER_DEG_LAT * Math.cos((projectLat * Math.PI) / 180),
  }), [projectLat, projectLng]);

  const cosLat = useMemo(
    () => Math.cos((projectLat * Math.PI) / 180),
    [projectLat],
  );

  // Initialize offscreen Mapbox map
  useEffect(() => {
    if (!MAPBOX_TOKEN) return;

    const container = document.createElement('div');
    container.style.width = `${MAP_SIZE}px`;
    container.style.height = `${MAP_SIZE}px`;
    container.style.position = 'fixed';
    container.style.left = '-9999px';
    container.style.top = '-9999px';
    container.style.pointerEvents = 'none';
    document.body.appendChild(container);
    containerRef.current = container;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container,
      style: STYLE_URLS[mapLayer] || STYLE_URLS.satellite,
      center: [projectLng, projectLat],
      zoom: 16,
      interactive: false,
      attributionControl: false,
      preserveDrawingBuffer: true,
      pitch: 0,
      bearing: 0,
      trackResize: false,
      failIfMajorPerformanceCaveat: false,
      // Force 1:1 pixel ratio so canvas is always MAP_SIZE x MAP_SIZE
      // regardless of system display scaling (125%, 150%, etc.)
      pixelRatio: 1,
    } as mapboxgl.MapOptions & { pixelRatio: number });

    // Track actual Mapbox canvas repaints so we know when needsUpdate is safe
    map.on('render', () => {
      mapRepainted.current = true;
    });

    map.on('load', () => {
      isMapReady.current = true;

      // Measure actual ground size from the live Mapbox viewport
      lastGroundSize.current = measureGroundSize(map, cosLat);

      const mapCanvas = map.getCanvas();
      const texture = new THREE.CanvasTexture(mapCanvas);
      texture.minFilter = THREE.LinearFilter;
      texture.magFilter = THREE.LinearFilter;
      texture.generateMipmaps = false;
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.needsUpdate = true;
      textureRef.current = texture;
      textureAttached.current = false;
    });

    map.on('error', (e) => {
      console.warn('[SatelliteGroundPlane] Mapbox error:', e.error?.message || e);
    });

    mapRef.current = map;
    currentStyleRef.current = mapLayer;

    return () => {
      isMapReady.current = false;
      textureAttached.current = false;
      mapRepainted.current = false;
      pendingRepaint.current = false;
      idleFinalUpdate.current = false;
      if (textureRef.current) {
        textureRef.current.dispose();
        textureRef.current = null;
      }
      map.remove();
      mapRef.current = null;
      if (containerRef.current) {
        document.body.removeChild(containerRef.current);
        containerRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectLat, projectLng]);

  // Handle map style changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    if (currentStyleRef.current === mapLayer) return;

    currentStyleRef.current = mapLayer;
    const styleUrl = STYLE_URLS[mapLayer] || STYLE_URLS.satellite;
    isMapReady.current = false;
    map.setStyle(styleUrl);

    map.once('style.load', () => {
      isMapReady.current = true;
      const mapCanvas = map.getCanvas();
      if (textureRef.current) {
        textureRef.current.image = mapCanvas;
        textureRef.current.needsUpdate = true;
      } else {
        const texture = new THREE.CanvasTexture(mapCanvas);
        texture.minFilter = THREE.LinearFilter;
        texture.magFilter = THREE.LinearFilter;
        texture.generateMipmaps = false;
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.needsUpdate = true;
        textureRef.current = texture;
        textureAttached.current = false;
      }
    });
  }, [mapLayer]);

  useFrame(() => {
    // Attach texture to material once ready
    if (textureRef.current && matRef.current && !textureAttached.current) {
      matRef.current.map = textureRef.current;
      matRef.current.needsUpdate = true;
      textureAttached.current = true;
    }

    // --- Throttled: update Mapbox texture zoom ---
    const map = mapRef.current;
    if (!map || !isMapReady.current || !textureRef.current) return;

    const now = performance.now();

    // Detect camera movement (cheap comparison first)
    const posMoved = camera.position.distanceToSquared(lastCamPos.current) > 0.01;
    const cameraMoved = posMoved || !camera.quaternion.equals(lastCamQuat.current);

    if (cameraMoved) {
      lastMoveTime.current = now;
      lastCamPos.current.copy(camera.position);
      lastCamQuat.current.copy(camera.quaternion);
    }

    // Pick up async Mapbox repaints — only set needsUpdate when canvas actually changed
    if (mapRepainted.current) {
      textureRef.current.needsUpdate = true;
      mapRepainted.current = false;
      pendingRepaint.current = false;
    }

    // After camera goes idle, do one final texture update to capture the last repaint
    const idleMs = now - lastMoveTime.current;
    if (idleMs > IDLE_THRESHOLD_MS && !cameraMoved) {
      if (!idleFinalUpdate.current) {
        textureRef.current.needsUpdate = true;
        idleFinalUpdate.current = true;
      }
      return;
    }
    idleFinalUpdate.current = false;

    // Throttle updates
    if (now - lastUpdateTime.current < UPDATE_INTERVAL_MS) return;
    lastUpdateTime.current = now;

    // Compute desired zoom from camera distance
    const camY = Math.max(1, camera.position.y);
    const camDistXZ = Math.sqrt(
      camera.position.x ** 2 + camera.position.z ** 2,
    );
    const fov = (camera as THREE.PerspectiveCamera).fov || 60;
    const fovRad = (fov * Math.PI) / 180;
    const viewRadius = camY * Math.tan(fovRad / 2) * 2;
    const neededRadius = Math.max(500, camDistXZ + viewRadius * 1.5);
    const neededSize = neededRadius * 2;
    const mpp = Math.max(0.001, neededSize / MAP_SIZE);
    // This formula is only used to pick a Mapbox zoom level (tile detail).
    // The actual mesh scale is set via measureGroundSize() below.
    const zoomLevel = Math.max(1, Math.min(22,
      Math.log2((MAPBOX_METERS_PER_PIXEL_Z0 * cosLat) / mpp),
    ));

    // Only update Mapbox if zoom changed meaningfully
    if (Math.abs(zoomLevel - lastZoom.current) < 0.05) return;
    lastZoom.current = zoomLevel;

    // Mapbox is ALWAYS centered on the project origin — never moves
    map.jumpTo({
      center: [origin.lng, origin.lat],
      zoom: zoomLevel,
      bearing: 0,
      pitch: 0,
    });

    // Measure the ACTUAL ground size from the Mapbox viewport after jumpTo
    // This is always correct regardless of tile size (256 vs 512) or version
    lastGroundSize.current = measureGroundSize(map, cosLat);

    // Try synchronous render, but ALWAYS schedule async repaint as backup.
    // In Mapbox GL v3, _render() can silently no-op, so we never trust it alone.
    const mapAny = map as any;
    try {
      if (typeof mapAny._render === 'function') {
        mapAny._render();
      } else if (typeof mapAny._rerender === 'function') {
        mapAny._rerender();
      }
    } catch {
      // Synchronous render not available
    }

    // Always schedule an async repaint as a safety net and track it
    map.triggerRepaint();
    pendingRepaint.current = true;

    textureRef.current.needsUpdate = true;

    // Immediately sync mesh scale to the measured ground size
    if (meshRef.current) {
      meshRef.current.scale.set(lastGroundSize.current, lastGroundSize.current, 1);
    }
  });

  if (!MAPBOX_TOKEN) return null;

  return (
    <mesh
      ref={meshRef}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, -0.05, 0]}
      receiveShadow
    >
      <planeGeometry args={[1, 1]} />
      <meshStandardMaterial
        ref={matRef}
        roughness={0.95}
        metalness={0}
        polygonOffset
        polygonOffsetFactor={6}
        polygonOffsetUnits={6}
      />
    </mesh>
  );
}
