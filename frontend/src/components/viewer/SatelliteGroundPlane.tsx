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

// Meters per pixel at zoom level 0 at the equator (Web Mercator, 256px tiles)
const MAPBOX_METERS_PER_PIXEL_Z0 = 156543.03392;

// Offscreen map resolution
const MAP_SIZE = 2048;

// Texture update throttle
const UPDATE_INTERVAL_MS = 100;

// How long camera must be stationary before we stop updating
const IDLE_THRESHOLD_MS = 500;

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
  const { camera, size } = useThree();
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
    });

    map.on('load', () => {
      isMapReady.current = true;

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

    // --- Mesh scale is always derived from the LAST RENDERED zoom level ---
    // This keeps scale and texture content perfectly synchronized:
    // both change together only when a new Mapbox frame is rendered.
    const mppAtZoom = MAPBOX_METERS_PER_PIXEL_Z0 * cosLat / Math.pow(2, lastZoom.current);
    const groundSize = mppAtZoom * MAP_SIZE;

    if (meshRef.current) {
      meshRef.current.scale.set(groundSize, groundSize, 1);
    }

    // --- Throttled: update Mapbox texture zoom ---
    const map = mapRef.current;
    if (!map || !isMapReady.current || !textureRef.current) return;

    const now = performance.now();

    // Detect camera movement
    const posMoved = camera.position.distanceToSquared(lastCamPos.current) > 0.0001;
    const rotChanged = !camera.quaternion.equals(lastCamQuat.current);
    const cameraMoved = posMoved || rotChanged;

    if (cameraMoved) {
      lastMoveTime.current = now;
      lastCamPos.current.copy(camera.position);
      lastCamQuat.current.copy(camera.quaternion);
    }

    // Skip updates when camera has been idle
    const idleMs = now - lastMoveTime.current;
    if (idleMs > IDLE_THRESHOLD_MS && !cameraMoved) return;

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
    const neededRadius = Math.max(250, camDistXZ + viewRadius);
    const neededSize = neededRadius * 2;
    const mpp = Math.max(0.001, neededSize / MAP_SIZE);
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

    // Force synchronous render
    try {
      (map as any)._render();
    } catch {
      map.triggerRepaint();
    }

    textureRef.current.needsUpdate = true;

    // Immediately sync mesh scale to the new zoom (same frame as texture)
    const newMpp = MAPBOX_METERS_PER_PIXEL_Z0 * cosLat / Math.pow(2, zoomLevel);
    const newGroundSize = newMpp * MAP_SIZE;
    if (meshRef.current) {
      meshRef.current.scale.set(newGroundSize, newGroundSize, 1);
    }
  });

  if (!MAPBOX_TOKEN) return null;

  return (
    <mesh
      ref={meshRef}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, -0.02, 0]}
      receiveShadow
    >
      <planeGeometry args={[1, 1]} />
      <meshStandardMaterial
        ref={matRef}
        roughness={0.95}
        metalness={0}
      />
    </mesh>
  );
}
