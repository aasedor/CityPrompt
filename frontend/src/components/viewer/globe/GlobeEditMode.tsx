/**
 * GlobeEditMode.tsx — Zone editing UI for the 3D globe.
 *
 * When a zone is selected in Select mode, renders:
 * - Draggable vertex handles at each polygon vertex
 * - Drag to reshape the zone boundary
 *
 * Uses the terrain-adjusted ellipsoid raycast for vertex snapping.
 */

import { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import { Html } from '@react-three/drei';
import { Ellipsoid, WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { useGlobeDragRef } from './useGlobeDragRef';
import { getRepresentativeTerrainHeight, resolveZoneTerrainHeight } from './globeTerrainUtils';

const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

interface GlobeEditModeProps {
  zone: SiteZone;
  terrainHeight: number;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
  globeControlsRef?: React.RefObject<any>;
  onInteractionStart?: () => void;
}

function coordsMatch(a: number[][], b: number[][], epsilon = 1e-7): boolean {
  if (a.length !== b.length) return false;
  return a.every((coord, index) => (
    Math.abs(coord[0] - b[index][0]) <= epsilon
    && Math.abs(coord[1] - b[index][1]) <= epsilon
  ));
}

function pointToLngLat(
  point: THREE.Vector3,
  fallbackEllipsoid: Ellipsoid,
): [number, number] {
  const ellipsoidWithCartographic = WGS84_ELLIPSOID as Ellipsoid & {
    getPositionToCartographic?: (
      point: THREE.Vector3,
      target: unknown,
    ) => { lon: number; lat: number };
  };
  const cartographicSource = typeof ellipsoidWithCartographic.getPositionToCartographic === 'function'
    ? ellipsoidWithCartographic
    : fallbackEllipsoid;
  const cartographic = cartographicSource.getPositionToCartographic(point, {} as never);
  return [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG];
}

function raycastTerrainHeightAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): number | null {
  const origin = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, 50000, origin);
  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(lat * DEG_TO_RAD, lng * DEG_TO_RAD, normal);
  raycaster.set(origin, normal.negate());
  raycaster.far = 100000;

  const hit = raycaster.intersectObjects(tilesGroup.children, true)[0]?.point;
  return hit ? WGS84_ELLIPSOID.getPositionElevation(hit) : null;
}

function getTerrainProbePoints(
  coords: number[][],
  centroid: [number, number],
): Array<[number, number]> {
  const probes: Array<[number, number]> = [centroid];
  if (coords.length === 0) {
    return probes;
  }

  const step = Math.max(1, Math.ceil(coords.length / 8));
  for (let index = 0; index < coords.length; index += step) {
    probes.push([coords[index][0], coords[index][1]]);
  }

  const last = coords[coords.length - 1];
  if (last) {
    probes.push([last[0], last[1]]);
  }

  return probes;
}

export function GlobeEditMode({
  zone,
  terrainHeight,
  onZoneUpdated,
  globeControlsRef,
  onInteractionStart,
}: GlobeEditModeProps) {
  const { camera, gl } = useThree();
  const tiles = useContext(TilesRendererContext);
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [liveCoords, setLiveCoords] = useState<number[][] | null>(null);
  const [pendingCommitCoords, setPendingCommitCoords] = useState<number[][] | null>(null);
  const [sampledTerrainHeight, setSampledTerrainHeight] = useState<number | null>(null);
  const dragRef = useGlobeDragRef();
  const renderedCoords = liveCoords ?? zone.coordinates;
  const zoneCentroid = useMemo(() => computeCentroid(zone.coordinates), [zone.coordinates]);

  // Disable/enable GlobeControls during drag
  const setControlsEnabled = useCallback((enabled: boolean) => {
    const controls = globeControlsRef?.current;
    const target = controls?.controls ?? controls;
    if (target && typeof target === 'object' && 'enabled' in target) {
      target.enabled = enabled;
    }
  }, [globeControlsRef]);
  const originalCoordsRef = useRef<number[][] | null>(null);
  const zoneProps = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProps?.terrain_elevation_m
    ?? zoneProps?.terrain_height
    ?? zoneProps?.terrainElevation,
  );
  const storedTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : null;
  const zoneTerrainHeight = resolveZoneTerrainHeight(
    sampledTerrainHeight,
    storedTerrainHeight,
    terrainHeight,
  );
  const terrainEllipsoid = useRef(new Ellipsoid(
    6378137.0 + zoneTerrainHeight,
    6378137.0 + zoneTerrainHeight,
    6356752.3142 + zoneTerrainHeight,
  ));

  useEffect(() => {
    terrainEllipsoid.current = new Ellipsoid(
      6378137.0 + zoneTerrainHeight,
      6378137.0 + zoneTerrainHeight,
      6356752.3142 + zoneTerrainHeight,
    );
  }, [zoneTerrainHeight]);

  const sampleZoneTerrainHeight = useCallback(() => {
    const tilesGroup = tiles?.group;
    if (!tilesGroup?.children?.length) return false;

    const raycaster = new THREE.Raycaster();
    const sampledHeight = getRepresentativeTerrainHeight(
      getTerrainProbePoints(zone.coordinates, zoneCentroid).map(([lng, lat]) => (
        raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycaster)
      )),
      zoneTerrainHeight,
    );

    if (!Number.isFinite(sampledHeight)) {
      return false;
    }

    setSampledTerrainHeight((previousHeight) => (
      previousHeight !== null && Math.abs(previousHeight - sampledHeight) < 0.01
        ? previousHeight
        : sampledHeight
    ));
    return true;
  }, [tiles, zone.coordinates, zoneCentroid, zoneTerrainHeight]);

  useEffect(() => {
    setSampledTerrainHeight(null);
    if (sampleZoneTerrainHeight()) return undefined;

    const timers = [
      setTimeout(sampleZoneTerrainHeight, 1500),
      setTimeout(sampleZoneTerrainHeight, 4000),
      setTimeout(sampleZoneTerrainHeight, 8000),
    ];

    return () => timers.forEach(clearTimeout);
  }, [sampleZoneTerrainHeight, zone.id, zone.updated_at]);

  // Raycast to get lat/lng from pointer event
  const pointerToLatLng = useCallback((e: PointerEvent): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

    const tilesGroup = tiles?.group;
    if (tilesGroup?.children?.length) {
      const hit = raycaster.intersectObjects(tilesGroup.children, true)[0]?.point;
      if (hit) {
        return pointToLngLat(hit, terrainEllipsoid.current);
      }
    }

    const hit = new THREE.Vector3();
    const result = terrainEllipsoid.current.intersectRay(raycaster.ray, hit);
    if (!result) return null;

    return pointToLngLat(hit, terrainEllipsoid.current);
  }, [camera, gl, tiles]);

  // --- Body drag state ---
  const [isDraggingBody, setIsDraggingBody] = useState(false);
  const bodyDragStartRef = useRef<[number, number] | null>(null);
  const bodyDragCoordsRef = useRef<number[][] | null>(null);

  useEffect(() => {
    if (isDraggingBody || dragIndex !== null || !pendingCommitCoords) return;
    if (coordsMatch(zone.coordinates, pendingCommitCoords)) {
      setLiveCoords(null);
      setPendingCommitCoords(null);
    }
  }, [dragIndex, isDraggingBody, pendingCommitCoords, zone.coordinates]);

  // Start dragging the zone body
  const handleBodyPointerDown = useCallback((e: any) => {
    e.stopPropagation();
    const pe = e.nativeEvent ?? e;
    const startLatLng = pointerToLatLng(pe as PointerEvent);
    if (!startLatLng) return;
    const ownerWindow = gl.domElement.ownerDocument?.defaultView ?? window;

    onInteractionStart?.();
    setPendingCommitCoords(null);
    bodyDragStartRef.current = startLatLng;
    bodyDragCoordsRef.current = renderedCoords.map(c => [...c]);
    setIsDraggingBody(true);
    setControlsEnabled(false); // Disable globe orbit during body drag
    gl.domElement.style.cursor = 'grabbing';

    const handlePointerMove = (moveEv: PointerEvent) => {
      const currentLatLng = pointerToLatLng(moveEv);
      if (!currentLatLng || !bodyDragStartRef.current || !bodyDragCoordsRef.current) return;

      const dlng = currentLatLng[0] - bodyDragStartRef.current[0];
      const dlat = currentLatLng[1] - bodyDragStartRef.current[1];

      const newCoords = bodyDragCoordsRef.current.map(c => [c[0] + dlng, c[1] + dlat]);

      // Write to drag ref (no React state update — useFrame reads this)
      dragRef.current.zoneId = zone.id;
      dragRef.current.type = 'body';
      dragRef.current.coords = newCoords as [number, number][];
      dragRef.current.version++;
      setLiveCoords(newCoords);
    };

    const handlePointerUp = () => {
      const finalCoords = dragRef.current.zoneId === zone.id && dragRef.current.coords.length > 0
        ? dragRef.current.coords.map((coord) => [...coord])
        : null;

      // Commit final coordinates to React state (one re-render)
      if (finalCoords) {
        setPendingCommitCoords(finalCoords);
        onZoneUpdated(zone.id, finalCoords);
      } else {
        setPendingCommitCoords(null);
        setLiveCoords(null);
      }
      // Clear drag state
      dragRef.current.zoneId = null;
      dragRef.current.type = null;
      dragRef.current.vertexIndex = -1;
      dragRef.current.coords = [];
      dragRef.current.version++;

      setIsDraggingBody(false);
      bodyDragStartRef.current = null;
      bodyDragCoordsRef.current = null;
      setControlsEnabled(true);
      gl.domElement.style.cursor = '';
      ownerWindow.removeEventListener('pointermove', handlePointerMove);
      ownerWindow.removeEventListener('pointerup', handlePointerUp);
      ownerWindow.removeEventListener('pointercancel', handlePointerUp);
      ownerWindow.removeEventListener('blur', handlePointerUp);
    };

    ownerWindow.addEventListener('pointermove', handlePointerMove);
    ownerWindow.addEventListener('pointerup', handlePointerUp);
    ownerWindow.addEventListener('pointercancel', handlePointerUp);
    ownerWindow.addEventListener('blur', handlePointerUp);
  }, [gl, onInteractionStart, onZoneUpdated, pointerToLatLng, renderedCoords, setControlsEnabled, zone]);

  // --- Build drag surface geometry (same shape as zone, invisible) ---
  // ENU frame: X=East, Y=North, Z=Up. Ground plane = XY.
  const dragSurfaceGeo = useMemo(() => {
    if (renderedCoords.length < 3) return null;
    const centroid = computeCentroid(renderedCoords);
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const localPts = renderedCoords.map(c => new THREE.Vector2(
      (c[0] - centroid[0]) * mPerDegLon,       // East (X)
      (c[1] - centroid[1]) * METERS_PER_DEG_LAT, // North (Y)
    ));
    // Triangulate in XY ground plane
    const indices = THREE.ShapeUtils.triangulateShape(localPts, []);
    const verts: number[] = [];
    for (const p of localPts) verts.push(p.x, p.y, 1.5); // Z = slight lift above ground
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    const idx: number[] = [];
    for (const tri of indices) idx.push(tri[0], tri[1], tri[2]);
    geo.setIndex(idx);
    return { geo, centroid };
  }, [renderedCoords]);

  // Start dragging a vertex
  const handleVertexPointerDown = useCallback((index: number, e: any) => {
    e.stopPropagation();
    onInteractionStart?.();
    setDragIndex(index);
    setControlsEnabled(false); // Disable globe orbit during vertex drag
    gl.domElement.style.cursor = 'grabbing';
    setPendingCommitCoords(null);
    originalCoordsRef.current = renderedCoords.map(c => [...c]);
    const ownerWindow = gl.domElement.ownerDocument?.defaultView ?? window;

    const handlePointerMove = (pe: PointerEvent) => {
      const lngLat = pointerToLatLng(pe);
      if (!lngLat || !originalCoordsRef.current) return;

      const newCoords = originalCoordsRef.current.map((c, i) =>
        i === index ? [...lngLat] : [...c]
      );

      // Write to drag ref (no React state update)
      dragRef.current.zoneId = zone.id;
      dragRef.current.type = 'vertex';
      dragRef.current.vertexIndex = index;
      dragRef.current.coords = newCoords as [number, number][];
      dragRef.current.version++;
      setLiveCoords(newCoords);
    };

    const handlePointerUp = () => {
      const finalCoords = dragRef.current.zoneId === zone.id && dragRef.current.coords.length > 0
        ? dragRef.current.coords.map((coord) => [...coord])
        : null;

      // Commit final coordinates to React state
      if (finalCoords) {
        setPendingCommitCoords(finalCoords);
        onZoneUpdated(zone.id, finalCoords);
      } else {
        setPendingCommitCoords(null);
        setLiveCoords(null);
      }
      // Clear drag state
      dragRef.current.zoneId = null;
      dragRef.current.type = null;
      dragRef.current.vertexIndex = -1;
      dragRef.current.coords = [];
      dragRef.current.version++;

      setDragIndex(null);
      originalCoordsRef.current = null;
      setControlsEnabled(true);
      gl.domElement.style.cursor = '';
      ownerWindow.removeEventListener('pointermove', handlePointerMove);
      ownerWindow.removeEventListener('pointerup', handlePointerUp);
      ownerWindow.removeEventListener('pointercancel', handlePointerUp);
      ownerWindow.removeEventListener('blur', handlePointerUp);
    };

    ownerWindow.addEventListener('pointermove', handlePointerMove);
    ownerWindow.addEventListener('pointerup', handlePointerUp);
    ownerWindow.addEventListener('pointercancel', handlePointerUp);
    ownerWindow.addEventListener('blur', handlePointerUp);
  }, [gl, onInteractionStart, onZoneUpdated, pointerToLatLng, renderedCoords, setControlsEnabled, zone]);

  return (
    <>
      {/* Invisible drag surface for body drag */}
      {dragSurfaceGeo && (
        <EastNorthUpFrame
          lat={dragSurfaceGeo.centroid[1] * DEG_TO_RAD}
          lon={dragSurfaceGeo.centroid[0] * DEG_TO_RAD}
          height={zoneTerrainHeight}
        >
          <mesh
            geometry={dragSurfaceGeo.geo}
            renderOrder={99}
            frustumCulled={false}
            onPointerDown={handleBodyPointerDown}
            onPointerEnter={() => { if (!isDraggingBody) gl.domElement.style.cursor = 'grab'; }}
            onPointerLeave={() => { if (!isDraggingBody) gl.domElement.style.cursor = ''; }}
          >
            <meshBasicMaterial transparent opacity={0} side={THREE.DoubleSide} depthTest={false} />
          </mesh>
        </EastNorthUpFrame>
      )}

      {/* Vertex handles — HTML-based for reliable click/drag */}
      {renderedCoords.map((coord, i) => (
        <EastNorthUpFrame
          key={`edit-v-${i}`}
          lat={coord[1] * DEG_TO_RAD}
          lon={coord[0] * DEG_TO_RAD}
          height={zoneTerrainHeight}
        >
          {/* Invisible 3D fallback hit target.
              Keep this close to the visible dot size so small buildings still
              have a selectable body area between vertices. */}
          <mesh
            renderOrder={900}
            onPointerDown={(e) => handleVertexPointerDown(i, e)}
            onPointerEnter={() => { setHoveredIndex(i); gl.domElement.style.cursor = 'grab'; }}
            onPointerLeave={() => { if (hoveredIndex === i) setHoveredIndex(null); if (dragIndex === null) gl.domElement.style.cursor = ''; }}
          >
            <sphereGeometry args={[2, 10, 10]} />
            <meshBasicMaterial
              color={dragIndex === i ? '#f59e0b' : '#ffffff'}
              transparent
              opacity={0.01}
              depthTest={false}
              depthWrite={false}
            />
          </mesh>
          {/* Visible dot via HTML — pointer events ENABLED for reliable click-through */}
          <Html center>
            <div
              className={`rounded-full border-2 shadow-lg transition-transform duration-150 ${
                dragIndex === i
                  ? 'h-6 w-6 border-amber-400 bg-amber-500 scale-125'
                  : hoveredIndex === i
                    ? 'h-6 w-6 border-white bg-white scale-110'
                    : 'h-5 w-5 border-white bg-white/90'
              }`}
              style={{ cursor: dragIndex === i ? 'grabbing' : 'grab' }}
              onPointerDown={(e) => {
                e.stopPropagation();
                handleVertexPointerDown(i, e as any);
              }}
              onPointerEnter={() => { setHoveredIndex(i); gl.domElement.style.cursor = 'grab'; }}
              onPointerLeave={() => { if (hoveredIndex === i) setHoveredIndex(null); if (dragIndex === null) gl.domElement.style.cursor = ''; }}
            />
          </Html>
        </EastNorthUpFrame>
      ))}
    </>
  );
}
