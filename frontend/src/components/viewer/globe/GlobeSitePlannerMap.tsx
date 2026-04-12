/**
 * GlobeSitePlannerMap.tsx — Google Earth-style 3D globe with SiteForge tools.
 *
 * Full-screen globe with drawing handled at the DOM level (not inside R3F).
 * GlobeControls always enabled — drawing uses click vs drag detection.
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import { Canvas, useThree } from '@react-three/fiber';
import {
  TilesRenderer,
  TilesPlugin,
  GlobeControls,
  TilesAttributionOverlay,
  EastNorthUpFrame,
} from '3d-tiles-renderer/r3f';
import {
  GoogleCloudAuthPlugin,
  TileCompressionPlugin,
  UpdateOnChangePlugin,
  UnloadTilesPlugin,
  TilesFadePlugin,
  GLTFExtensionsPlugin,
} from '3d-tiles-renderer/plugins';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { Html } from '@react-three/drei';
import type { SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { useViewerStore } from '@/store';
import { GlobeZoneLayer } from './GlobeZoneLayer';
import { GlobeEditMode } from './GlobeEditMode';
import { GlobePegman } from './GlobePegman';
import { SceneSettledMonitor } from './useSceneSettled';
import { TileStencilPatcher } from './TileStencilPatcher';
import {
  getToolDisplayLabel,
  isLinearTool,
  minPointsForTool,
  smoothPolyline,
  bufferLineToPolygon,
  computeCentroid,
  geodesicArea,
  polylineLength,
  formatDistance,
  formatArea,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { polygon as turfPolygon, point as turfPoint } from '@turf/helpers';

import { elevationApi } from '@/services/api';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

// Default fallback elevation (Calgary) — used until dynamic fetch completes
const DEFAULT_TERRAIN_ELEVATION = 1045;

import { Ellipsoid } from '3d-tiles-renderer';

/** Create a terrain-adjusted ellipsoid for accurate raycasting at a given elevation */
function createTerrainEllipsoid(elevation: number): Ellipsoid {
  return new Ellipsoid(
    6378137.0 + elevation,
    6378137.0 + elevation,
    6356752.3142 + elevation,
  );
}

function sanitizeCoords(coords: number[][]): number[][] {
  const cleaned: number[][] = [];
  for (const c of coords) {
    if (!Array.isArray(c) || c.length < 2) continue;
    const lng = Number(c[0]);
    const lat = Number(c[1]);
    if (!Number.isFinite(lng) || !Number.isFinite(lat)) continue;
    if (Math.abs(lng) > 180 || Math.abs(lat) > 90) continue;
    if (
      cleaned.length === 0
      || Math.abs(lng - cleaned[cleaned.length - 1][0]) > 1e-7
      || Math.abs(lat - cleaned[cleaned.length - 1][1]) > 1e-7
    ) {
      cleaned.push([lng, lat]);
    }
  }
  return cleaned;
}

/** Expose R3F camera to parent via ref */
function CameraExposer({ cameraRef }: { cameraRef: React.MutableRefObject<THREE.Camera | null> }) {
  const { camera } = useThree();
  useEffect(() => { cameraRef.current = camera; }, [camera, cameraRef]);
  return null;
}

/** Monitor camera pitch angle (0=top-down, 90=horizon) */
function PitchMonitor({ onPitchChange }: { onPitchChange: (pitch: number) => void }) {
  const { camera } = useThree();
  const lastPitchRef = useRef(-1);

  useEffect(() => {
    const interval = setInterval(() => {
      // Compute pitch: angle between camera look direction and surface normal
      const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
      const camPos = camera.position.clone().normalize(); // Surface normal at camera position
      const dot = dir.dot(camPos);
      // dot ≈ -1 means looking straight down (0° pitch), dot ≈ 0 means looking at horizon (90°)
      const pitch = Math.round(Math.acos(Math.min(1, Math.max(-1, -dot))) * (180 / Math.PI));
      if (pitch !== lastPitchRef.current) {
        lastPitchRef.current = pitch;
        onPitchChange(pitch);
      }
    }, 200); // Update 5x per second
    return () => clearInterval(interval);
  }, [camera, onPitchChange]);

  return null;
}

/** Render drawing preview dots inside R3F */
function DrawingPreviewFill({ points, terrainHeight }: { points: number[][]; terrainHeight: number }) {
  const geo = useMemo(() => {
    if (points.length < 3) return null;
    const centroid = computeCentroid(points);
    const mPerDegLon = metersPerDegLon(centroid[1]);
    // ENU: X=East, Y=North, Z=Up
    const localPts = points.map(c => new THREE.Vector2(
      (c[0] - centroid[0]) * mPerDegLon,
      (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
    ));
    const indices = THREE.ShapeUtils.triangulateShape(localPts, []);
    const verts: number[] = [];
    for (const p of localPts) verts.push(p.x, p.y, 3); // Z=3m above ground
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    const idx: number[] = [];
    for (const tri of indices) idx.push(tri[0], tri[1], tri[2]);
    g.setIndex(idx);
    return { geo: g, centroid };
  }, [points]);

  if (!geo) return null;
  return (
    <EastNorthUpFrame lat={geo.centroid[1] * DEG_TO_RAD} lon={geo.centroid[0] * DEG_TO_RAD} height={terrainHeight}>
      <mesh geometry={geo.geo} renderOrder={98} frustumCulled={false}>
        <meshBasicMaterial color="#f59e0b" transparent opacity={0.25} side={THREE.DoubleSide} depthTest={false} depthWrite={false} />
      </mesh>
    </EastNorthUpFrame>
  );
}

function DrawingDots({ points, terrainHeight }: { points: number[][]; terrainHeight: number }) {
  if (points.length === 0) return null;
  return (
    <>
      {/* Preview fill polygon */}
      <DrawingPreviewFill points={points} terrainHeight={terrainHeight} />

      {/* Vertex dots */}
      {points.map((pt, i) => (
        <EastNorthUpFrame key={`dot-${i}-${pt[0]}-${pt[1]}`} lat={pt[1] * DEG_TO_RAD} lon={pt[0] * DEG_TO_RAD} height={terrainHeight}>
          <mesh renderOrder={999}>
            <sphereGeometry args={[5, 12, 12]} />
            <meshBasicMaterial color="#f59e0b" depthTest={false} depthWrite={false} />
          </mesh>
          <Html center style={{ pointerEvents: 'none' }}>
            <div className="h-3 w-3 rounded-full border-2 border-white bg-amber-500 shadow-lg" />
          </Html>
        </EastNorthUpFrame>
      ))}

      {/* Outline connecting dots */}
      {points.length >= 2 && (() => {
        const centroid = computeCentroid(points);
        const mPerDegLon = metersPerDegLon(centroid[1]);
        const outVerts: number[] = [];
        for (const c of points) {
          outVerts.push(
            (c[0] - centroid[0]) * mPerDegLon,
            (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
            3.5,
          );
        }
        // Close the loop for polygons (3+ points)
        if (points.length >= 3) {
          outVerts.push(
            (points[0][0] - centroid[0]) * mPerDegLon,
            (points[0][1] - centroid[1]) * METERS_PER_DEG_LAT,
            3.5,
          );
        }
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outVerts, 3));
        return (
          <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={terrainHeight}>
            {/* @ts-expect-error R3F line type conflict */}
            <line geometry={lineGeo} renderOrder={999} frustumCulled={false}>
              <lineBasicMaterial color="#f59e0b" linewidth={2} depthTest={false} depthWrite={false} />
            </line>
          </EastNorthUpFrame>
        );
      })()}
    </>
  );
}

interface GlobeSitePlannerMapProps {
  latitude?: number;
  longitude?: number;
  siteZones: SiteZone[];
  massingFeatures?: unknown[];
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
  onZoneSelected: (zoneId: string | null) => void;
  onZoneDeleted?: (zoneId: string) => void;
  /** Expose canvas + camera + terrain height for AI render panel */
  onGlobeReady?: (refs: { canvas: HTMLCanvasElement; camera: THREE.Camera; terrainHeight: number; isSettled?: boolean }) => void;
}

export function GlobeSitePlannerMap({
  latitude: _latitude = 51.045,
  longitude: _longitude = -114.07,
  siteZones,
  onZoneCreated,
  onZoneUpdated,
  onZoneSelected,
  onZoneDeleted: _onZoneDeleted,
  onGlobeReady,
}: GlobeSitePlannerMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.Camera | null>(null);
  const globeControlsRef = useRef<any>(null);
  const {
    selectedZoneId, activeSitePlannerTool, activeToolProperties,
    streetViewPegman, setStreetViewPosition, setStreetViewAngle, setStreetViewActive,
  } = useViewerStore();

  const isDrawing = activeSitePlannerTool !== null;
  const linear = isLinearTool(activeSitePlannerTool);

  // LOD settlement state — true when 3D tiles have fully loaded
  const [isSceneSettled, setIsSceneSettled] = useState(false);
  // Camera pitch angle (0=top-down, 90=horizon)
  const [pitchAngle, setPitchAngle] = useState(0);

  // Dynamic terrain elevation — fetched from Google Elevation API on mount
  const [terrainElevation, setTerrainElevation] = useState(DEFAULT_TERRAIN_ELEVATION);
  const terrainEllipsoidRef = useRef(createTerrainEllipsoid(DEFAULT_TERRAIN_ELEVATION));

  useEffect(() => {
    let cancelled = false;
    elevationApi.get(_latitude, _longitude)
      .then((data) => {
        if (!cancelled && Number.isFinite(data.ellipsoidal_height)) {
          const lowFidelityFallback = data.elevation === 0 && data.resolution >= 900;
          if (lowFidelityFallback) {
            console.warn(
              '[Globe] Elevation fallback detected; keeping default terrain elevation:',
              DEFAULT_TERRAIN_ELEVATION,
            );
            return;
          }
          // 3D tiles are positioned in WGS84/ECEF space, so ellipsoidal height
          // grounds overlays better than orthometric (MSL) height.
          const terrainHeight = data.ellipsoidal_height;
          console.log('[Globe] Elevation fetched:', terrainHeight, 'm for', _latitude, _longitude);
          setTerrainElevation(terrainHeight);
          terrainEllipsoidRef.current = createTerrainEllipsoid(terrainHeight);
        }
      })
      .catch((err) => {
        console.warn('[Globe] Elevation API failed, using default:', DEFAULT_TERRAIN_ELEVATION, err);
      });
    return () => { cancelled = true; };
  }, [_latitude, _longitude]);

  // Drawing state — managed at DOM level
  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const drawingPointsRef = useRef<number[][]>([]);
  const handleCanvasClickRef = useRef<((e: MouseEvent) => void) | null>(null);
  const finishDrawingRef = useRef<(() => void) | null>(null);
  const cleanupCanvasListenersRef = useRef<(() => void) | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const ignoreNextCanvasClickRef = useRef(false);
  const pointerDownRef = useRef<{ x: number; y: number } | null>(null);
  const draggedSincePointerDownRef = useRef(false);

  // Sync ref
  useEffect(() => { drawingPointsRef.current = drawingPoints; }, [drawingPoints]);

  // Clear drawing when tool changes
  useEffect(() => {
    setDrawingPoints([]);
    drawingPointsRef.current = [];
  }, [activeSitePlannerTool]);

  // Disable globe orbit controls while drawing so click placement is reliable.
  useEffect(() => {
    const controls = globeControlsRef.current;
    const target = controls?.controls ?? controls;
    if (target && typeof target === 'object' && 'enabled' in target) {
      target.enabled = !isDrawing;
    }
  }, [isDrawing]);

  // Cursor styling based on mode
  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs) return;
    cvs.style.cursor = isDrawing ? 'crosshair' : '';
    return () => { cvs.style.cursor = ''; };
  }, [isDrawing]);

  // Keep AI render refs synced after async terrain updates.
  useEffect(() => {
    if (!onGlobeReady || !canvasRef.current || !cameraRef.current) return;
    onGlobeReady({
      canvas: canvasRef.current,
      camera: cameraRef.current,
      terrainHeight: terrainElevation,
    });
  }, [onGlobeReady, terrainElevation]);

  // Prevent page scroll
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => { e.preventDefault(); };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, []);

  // Finish drawing
  const finishDrawing = useCallback(() => {
    const pts = sanitizeCoords(drawingPointsRef.current);
    if (!activeSitePlannerTool || pts.length < minPointsForTool(activeSitePlannerTool)) return;

    let finalCoords: number[][];
    if (linear) {
      const smoothed = smoothPolyline(pts);
      const width = (activeToolProperties?.width as number) || 10;
      finalCoords = sanitizeCoords(bufferLineToPolygon(smoothed, width));
    } else {
      finalCoords = [...pts];
    }

    if (finalCoords.length < 3) {
      console.warn('[Globe] Zone create skipped: not enough valid unique vertices', finalCoords.length);
      return;
    }

    // Zone creation logged for debugging
    const propsWithTerrain = {
      ...(activeToolProperties || {}),
      terrain_elevation_m:
        (activeToolProperties as Record<string, unknown> | null)?.terrain_elevation_m
        ?? terrainElevation,
    } as SiteZoneProperties;
    onZoneCreated(finalCoords, activeSitePlannerTool, propsWithTerrain);
    setDrawingPoints([]);
    drawingPointsRef.current = [];
  }, [activeSitePlannerTool, activeToolProperties, linear, onZoneCreated, terrainElevation]);
  finishDrawingRef.current = finishDrawing;

  // Keyboard handler for drawing
  useEffect(() => {
    if (!isDrawing) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') finishDrawing();
      else if (e.key === 'Escape') { setDrawingPoints([]); drawingPointsRef.current = []; }
      else if (e.key === 'Backspace' && drawingPointsRef.current.length > 0) {
        const newPts = drawingPointsRef.current.slice(0, -1);
        drawingPointsRef.current = newPts;
        setDrawingPoints(newPts);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDrawing, finishDrawing]);

  // Clipboard for copy/paste
  const clipboardRef = useRef<{ coordinates: number[][]; zoneType: SiteZoneType; properties?: SiteZoneProperties } | null>(null);

  // Keyboard handler for Select mode — Delete, Escape, WASD, Copy/Paste
  useEffect(() => {
    if (isDrawing) return;

    const MOVE_DELTA = 0.0003; // ~30m in degrees

    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      // Delete zone
      if (e.key === 'Delete' || (e.key === 'Backspace' && !e.metaKey && !e.ctrlKey)) {
        if (selectedZoneId) {
          _onZoneDeleted?.(selectedZoneId);
          onZoneSelected(null);
        }
        return;
      }

      // Escape — remove pegman or deselect zone
      if (e.key === 'Escape') {
        if (streetViewPegman?.position) {
          setStreetViewActive(false);
        } else {
          onZoneSelected(null);
        }
        return;
      }

      // Arrow keys rotate street view pegman (when placed)
      if (streetViewPegman?.position) {
        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          setStreetViewAngle((streetViewPegman.angle - 45 + 360) % 360);
          return;
        }
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          setStreetViewAngle((streetViewPegman.angle + 45) % 360);
          return;
        }
      }

      // Copy (Ctrl+C / Cmd+C)
      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        if (selectedZoneId) {
          const zone = siteZones.find(z => z.id === selectedZoneId);
          if (zone) {
            clipboardRef.current = {
              coordinates: zone.coordinates.map(c => [...c]),
              zoneType: zone.zone_type,
              properties: zone.properties ? { ...zone.properties } : undefined,
            };
          }
        }
        return;
      }

      // Paste (Ctrl+V / Cmd+V)
      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        if (clipboardRef.current) {
          const offset = MOVE_DELTA;
          const newCoords = clipboardRef.current.coordinates.map(c => [c[0] + offset, c[1] + offset]);
          onZoneCreated(newCoords, clipboardRef.current.zoneType, clipboardRef.current.properties);
        }
        return;
      }

      // WASD / Arrow keys — move selected zone or pan camera
      const moveKeys: Record<string, [number, number]> = {
        'w': [0, MOVE_DELTA], 'ArrowUp': [0, MOVE_DELTA],
        's': [0, -MOVE_DELTA], 'ArrowDown': [0, -MOVE_DELTA],
        'a': [-MOVE_DELTA, 0], 'ArrowLeft': [-MOVE_DELTA, 0],
        'd': [MOVE_DELTA, 0], 'ArrowRight': [MOVE_DELTA, 0],
      };

      const delta = moveKeys[e.key];
      if (delta && selectedZoneId) {
        e.preventDefault();
        const zone = siteZones.find(z => z.id === selectedZoneId);
        if (zone) {
          const newCoords = zone.coordinates.map(c => [c[0] + delta[0], c[1] + delta[1]]);
          onZoneUpdated(selectedZoneId, newCoords);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDrawing, selectedZoneId, onZoneSelected, _onZoneDeleted, siteZones, onZoneUpdated, onZoneCreated]);

  // Canvas onPointerMissed — fires when click doesn't hit any R3F mesh
  // We use this + onCreated to handle globe clicks at the Canvas level
  const handleCanvasClick = useCallback((e: MouseEvent) => {
    if (ignoreNextCanvasClickRef.current) {
      ignoreNextCanvasClickRef.current = false;
      return;
    }

    const camera = cameraRef.current;
    if (!camera) return;

    // Get canvas rect for NDC calculation
    const canvas = containerRef.current?.querySelector('canvas');
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    // Raycast against terrain-adjusted ellipsoid to get lat/lng
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
    const hit = new THREE.Vector3();
    const result = terrainEllipsoidRef.current.intersectRay(raycaster.ray, hit);
    if (!result) return;

    const clickCarto = terrainEllipsoidRef.current.getPositionToCartographic(hit, {} as any);
    const clickLngLat: [number, number] = [clickCarto.lon * RAD_TO_DEG, clickCarto.lat * RAD_TO_DEG];

    // Street view mode: place pegman on click
    if (!isDrawing && streetViewPegman !== null) {
      setStreetViewPosition(clickLngLat);
      return;
    }

    // In select mode: check if click is inside any zone polygon using turf.js
    if (!isDrawing) {
      const clickPt = turfPoint(clickLngLat);
      let hitZoneId: string | null = null;
      let hitZoneArea = Infinity;

      for (const zone of siteZones) {
        if (!zone.coordinates || zone.coordinates.length < 3) continue;
        try {
          const closed = [...zone.coordinates, zone.coordinates[0]];
          const poly = turfPolygon([closed]);
          if (booleanPointInPolygon(clickPt, poly)) {
            // Pick smallest zone if overlapping
            const area = geodesicArea(zone.coordinates);
            if (area < hitZoneArea) {
              hitZoneArea = area;
              hitZoneId = zone.id;
            }
          }
        } catch { /* skip invalid polygons */ }
      }

      if (hitZoneId) {
        // Zone selected
        onZoneSelected(hitZoneId);
      } else {
        onZoneSelected(null);
      }
      return;
    }

    // Convert back using the terrain ellipsoid (gives same lat/lng, just at terrain height)
    const cartographic = terrainEllipsoidRef.current.getPositionToCartographic(hit, {} as any);
    const lngLat: [number, number] = [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG];

    // Every click adds a point. Double-click finish is handled by the dblclick listener.
    // Point placed — add to drawing
    const newPts = [...drawingPointsRef.current, lngLat];
    drawingPointsRef.current = newPts;
    setDrawingPoints(newPts);
  }, [isDrawing, finishDrawing, onZoneSelected, siteZones]);

  const handleZoneMeshClick = useCallback((zoneId: string) => {
    if (isDrawing) return;
    ignoreNextCanvasClickRef.current = true;
    onZoneSelected(zoneId);
  }, [isDrawing, onZoneSelected]);

  // Keep ref updated so onCreated closure always calls latest version
  handleCanvasClickRef.current = handleCanvasClick;

  // Cleanup canvas listeners on unmount/re-init
  useEffect(() => {
    return () => {
      if (cleanupCanvasListenersRef.current) {
        cleanupCanvasListenersRef.current();
        cleanupCanvasListenersRef.current = null;
      }
    };
  }, []);

  if (!API_KEY) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900 text-white">
        <p className="text-sm text-gray-400">Missing VITE_GOOGLE_MAPS_API_KEY</p>
      </div>
    );
  }

  // Compute initial camera position near the project location
  const initialCameraPosition = (() => {
    const surface = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(_latitude * DEG_TO_RAD, _longitude * DEG_TO_RAD, 0, surface);
    const normal = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToNormal(_latitude * DEG_TO_RAD, _longitude * DEG_TO_RAD, normal);
    const pos = surface.clone().add(normal.multiplyScalar(3000));
    return [pos.x, pos.y, pos.z] as [number, number, number];
  })();

  return (
    <div ref={containerRef} className="relative h-full w-full bg-black" style={{ overflow: 'hidden' }}>
      <Canvas
        camera={{ position: initialCameraPosition, near: 1, far: 1e11 }}
        gl={{ antialias: true, logarithmicDepthBuffer: true, preserveDrawingBuffer: true, stencil: true }}
        onCreated={({ gl, camera }) => {
          // Expose canvas + camera for AI render panel
          canvasRef.current = gl.domElement;
          cameraRef.current = camera;
          onGlobeReady?.({ canvas: gl.domElement, camera, terrainHeight: terrainElevation });

          // Attach pointer handlers directly to WebGL canvas for drawing
          const cvs = gl.domElement;

          // Remove previous listeners first (React StrictMode / hot-reload safety)
          if (cleanupCanvasListenersRef.current) {
            cleanupCanvasListenersRef.current();
            cleanupCanvasListenersRef.current = null;
          }

          const handleClick = (e: MouseEvent) => {
            if (draggedSincePointerDownRef.current) {
              draggedSincePointerDownRef.current = false;
              return;
            }
            // Every click adds a point — dblclick handler will pop the duplicate
            handleCanvasClickRef.current?.(e);
          };

          const handleDblClick = (e: MouseEvent) => {
            const isDrawingNow = useViewerStore.getState().activeSitePlannerTool !== null;
            if (!isDrawingNow) return;
            e.preventDefault();
            e.stopPropagation();
            // Remove the duplicate point added by the first click of the double-click
            if (drawingPointsRef.current.length > 0) {
              drawingPointsRef.current = drawingPointsRef.current.slice(0, -1);
            }
            finishDrawingRef.current?.();
          };

          const handlePointerDown = (e: PointerEvent) => {
            pointerDownRef.current = { x: e.clientX, y: e.clientY };
            draggedSincePointerDownRef.current = false;
          };

          const handlePointerMove = (e: PointerEvent) => {
            const start = pointerDownRef.current;
            if (!start || draggedSincePointerDownRef.current) return;
            const dx = e.clientX - start.x;
            const dy = e.clientY - start.y;
            if ((dx * dx + dy * dy) > 36) draggedSincePointerDownRef.current = true; // 6px threshold — forgiving for globe orbiting
          };

          const handlePointerUp = () => {
            pointerDownRef.current = null;
          };

          cvs.addEventListener('pointerdown', handlePointerDown);
          cvs.addEventListener('pointermove', handlePointerMove);
          cvs.addEventListener('pointerup', handlePointerUp);
          cvs.addEventListener('click', handleClick);
          cvs.addEventListener('dblclick', handleDblClick);

          cleanupCanvasListenersRef.current = () => {
            cvs.removeEventListener('pointerdown', handlePointerDown);
            cvs.removeEventListener('pointermove', handlePointerMove);
            cvs.removeEventListener('pointerup', handlePointerUp);
            cvs.removeEventListener('click', handleClick);
            cvs.removeEventListener('dblclick', handleDblClick);
          };
        }}
      >
        <CameraExposer cameraRef={cameraRef} />
        <PitchMonitor onPitchChange={setPitchAngle} />
        {/* Atmospheric fog — grounds the horizon and hides the infinite void */}
        <fog attach="fog" args={['#b8c8d8', 8000, 80000]} />
        <TilesRenderer>
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <TilesPlugin plugin={GoogleCloudAuthPlugin} args={{ apiToken: API_KEY, useRecommendedSettings: true } as any} />
          <TilesPlugin plugin={TileCompressionPlugin} />
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <TilesPlugin plugin={GLTFExtensionsPlugin} args={{ dracoLoader: new DRACOLoader().setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/') } as any} />
          <TilesPlugin plugin={UpdateOnChangePlugin} />
          <TilesPlugin plugin={UnloadTilesPlugin} />
          <TilesPlugin plugin={TilesFadePlugin} />
          <GlobeControls ref={globeControlsRef} />
          <TilesAttributionOverlay />
          <SceneSettledMonitor onSettledChange={setIsSceneSettled} />
          <TileStencilPatcher zones={siteZones} />
          {/* Camera starts at project location via Canvas camera prop */}

          {/* Zone visualization */}
          <GlobeZoneLayer
            zones={siteZones}
            selectedZoneId={selectedZoneId}
            terrainHeight={terrainElevation}
            onZoneClick={handleZoneMeshClick}
          />

          {/* Drawing preview dots */}
          <DrawingDots points={drawingPoints} terrainHeight={terrainElevation} />

          {/* Edit mode — vertex handles when zone selected in Select mode */}
          {!isDrawing && selectedZoneId && (() => {
            const zone = siteZones.find(z => z.id === selectedZoneId);
            return zone ? (
              <GlobeEditMode
                zone={zone}
                terrainHeight={terrainElevation}
                onZoneUpdated={onZoneUpdated}
                globeControlsRef={globeControlsRef}
              />
            ) : null;
          })()}

          {/* Street view pegman */}
          {streetViewPegman?.position && (
            <GlobePegman
              position={streetViewPegman.position as [number, number]}
              angle={streetViewPegman.angle}
              terrainHeight={terrainElevation}
            />
          )}
        </TilesRenderer>

        {/* Click handling is attached in onCreated (canvas click + dblclick listeners) */}
      </Canvas>

      {/* Context-sensitive hints bar */}
      {isDrawing && (() => {
        const n = drawingPoints.length;
        const tool = activeSitePlannerTool!;
        const label = getToolDisplayLabel(tool);
        const min = minPointsForTool(tool);
        const linear = isLinearTool(tool);

        let measurement = '';
        if (n >= 2 && linear) {
          measurement = formatDistance(polylineLength(drawingPoints));
        } else if (n >= 3 && !linear) {
          measurement = formatArea(geodesicArea(drawingPoints));
        }

        let hint: string;
        if (n === 0) {
          hint = `Click to place first ${label} point`;
        } else if (n < min) {
          hint = `${n} point${n > 1 ? 's' : ''} — need ${min} min — Backspace to undo`;
        } else {
          hint = `${n} points${measurement ? ` · ${measurement}` : ''} — Double-click or Enter to finish — Esc to cancel`;
        }

        return (
          <div className="absolute left-1/2 bottom-24 z-30 -translate-x-1/2 rounded-lg bg-gray-900/90 px-4 py-2 text-center text-xs text-white backdrop-blur-sm border border-amber-500/30">
            {hint}
          </div>
        );
      })()}

      {/* Street view hint */}
      {!isDrawing && streetViewPegman && (
        <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-lg bg-amber-900/80 px-3 py-1.5 text-center text-[11px] text-amber-100 backdrop-blur-sm border border-amber-500/30">
          {streetViewPegman.position
            ? 'Arrow keys to rotate view · Esc to remove pegman'
            : 'Click to place street view camera'}
        </div>
      )}

      {/* Select mode hint */}
      {!isDrawing && !streetViewPegman && (
        <div className="absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-lg bg-gray-900/70 px-3 py-1.5 text-center text-[11px] text-white/70 backdrop-blur-sm">
          {selectedZoneId
            ? 'Drag body to move · Drag vertices to reshape · Del to delete · Ctrl+C to copy'
            : 'Click zone to select · Scroll to zoom · Drag to orbit'}
        </div>
      )}

      {/* 3D Globe badge + pitch + LOD status — offset below back button */}
      <div className="absolute top-14 left-4 z-20 flex items-center gap-2">
        <div className="rounded-lg bg-gray-900/75 px-2.5 py-1.5 backdrop-blur-sm shadow-lg">
          <span className="text-[11px] font-medium text-emerald-400">3D Globe</span>
        </div>
        <div className={`rounded-lg bg-gray-900/75 px-2.5 py-1.5 backdrop-blur-sm shadow-lg text-[11px] font-medium ${
          pitchAngle < 30 ? 'text-red-400' :
          pitchAngle < 50 ? 'text-amber-400' :
          pitchAngle < 70 ? 'text-emerald-400' :
          pitchAngle < 80 ? 'text-amber-400' : 'text-red-400'
        }`}>
          {pitchAngle}° {
            pitchAngle < 20 ? 'flat' :
            pitchAngle < 40 ? 'low' :
            pitchAngle < 60 ? 'good' :
            pitchAngle < 75 ? 'optimal' : 'steep'
          }
        </div>
        {!isSceneSettled && (
          <div className="rounded-lg bg-gray-900/75 px-2.5 py-1.5 backdrop-blur-sm shadow-lg flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[10px] text-amber-300">Loading tiles...</span>
          </div>
        )}
      </div>
    </div>
  );
}
