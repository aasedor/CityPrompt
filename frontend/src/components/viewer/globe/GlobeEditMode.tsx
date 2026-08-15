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
import {
  getObjectFilteredTerrainHeight,
  getRepresentativeTerrainHeight,
  resolveZoneTerrainHeight,
  shouldFilterObjectTerrainHeight,
} from './globeTerrainUtils';

const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;
const OBJECT_FILTER_SAMPLE_RADIUS_METERS = 8;
const GLOBE_SCENE_HTML_Z_INDEX_RANGE: [number, number] = [1, 0];
const ROTATION_HANDLE_LIFT_METERS = 4;

function isBuildableZoneType(zoneType: string | null | undefined): boolean {
  return zoneType === 'building' || zoneType === 'residential' || zoneType === 'development_area';
}

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

function localMetersFromLngLat(
  lngLat: [number, number],
  centroid: [number, number],
  metersPerLon: number,
): [number, number] {
  return [
    (lngLat[0] - centroid[0]) * metersPerLon,
    (lngLat[1] - centroid[1]) * METERS_PER_DEG_LAT,
  ];
}

function rotateCoordsAroundCentroid(
  coords: number[][],
  centroid: [number, number],
  metersPerLon: number,
  deltaRad: number,
): number[][] {
  const cos = Math.cos(deltaRad);
  const sin = Math.sin(deltaRad);

  return coords.map((coord) => {
    const [east, north] = localMetersFromLngLat([coord[0], coord[1]], centroid, metersPerLon);
    const nextEast = east * cos - north * sin;
    const nextNorth = east * sin + north * cos;
    return [
      centroid[0] + nextEast / metersPerLon,
      centroid[1] + nextNorth / METERS_PER_DEG_LAT,
    ];
  });
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

function raycastObjectFilteredTerrainHeightAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
  fallback: number | null | undefined,
): number | null {
  const mPerDegLon = Math.max(1, Math.abs(metersPerDegLon(lat)));
  const diagonal = OBJECT_FILTER_SAMPLE_RADIUS_METERS * 0.7;
  const offsets: Array<[number, number]> = [
    [0, 0],
    [OBJECT_FILTER_SAMPLE_RADIUS_METERS, 0],
    [-OBJECT_FILTER_SAMPLE_RADIUS_METERS, 0],
    [0, OBJECT_FILTER_SAMPLE_RADIUS_METERS],
    [0, -OBJECT_FILTER_SAMPLE_RADIUS_METERS],
    [diagonal, diagonal],
    [diagonal, -diagonal],
    [-diagonal, diagonal],
    [-diagonal, -diagonal],
  ];
  const samples = offsets.map(([eastMeters, northMeters]) => (
    raycastTerrainHeightAtLatLng(
      lng + eastMeters / mPerDegLon,
      lat + northMeters / METERS_PER_DEG_LAT,
      tilesGroup,
      raycaster,
    )
  ));

  return getObjectFilteredTerrainHeight(samples, samples[0] ?? fallback);
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
  const [isRotating, setIsRotating] = useState(false);
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
  const rotationDragRef = useRef<{
    centroid: [number, number];
    coords: number[][];
    metersPerLon: number;
    startAngle: number;
  } | null>(null);
  const zoneProps = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProps?.terrain_elevation_m
    ?? zoneProps?.terrain_height
    ?? zoneProps?.terrainElevation,
  );
  const storedTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : null;
  const filterObjectHeights = shouldFilterObjectTerrainHeight(zone.zone_type);
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
        filterObjectHeights
          ? raycastObjectFilteredTerrainHeightAtLatLng(lng, lat, tilesGroup, raycaster, null)
          : raycastTerrainHeightAtLatLng(lng, lat, tilesGroup, raycaster)
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
  }, [filterObjectHeights, tiles, zone.coordinates, zoneCentroid, zoneTerrainHeight]);

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
  const pointerToLatLng = useCallback((e: PointerEvent | MouseEvent): [number, number] | null => {
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

  const pointerToRotationPlaneLocal = useCallback((
    e: PointerEvent | MouseEvent,
    centroid: [number, number],
  ): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

    const latRad = centroid[1] * DEG_TO_RAD;
    const lonRad = centroid[0] * DEG_TO_RAD;
    const origin = new THREE.Vector3();
    const east = new THREE.Vector3();
    const north = new THREE.Vector3();
    const up = new THREE.Vector3();
    WGS84_ELLIPSOID.getCartographicToPosition(latRad, lonRad, zoneTerrainHeight, origin);
    WGS84_ELLIPSOID.getCartographicToNormal(latRad, lonRad, up);
    WGS84_ELLIPSOID.getEastNorthUpAxes(latRad, lonRad, east, north, new THREE.Vector3());

    const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(up, origin);
    const hit = new THREE.Vector3();
    if (!raycaster.ray.intersectPlane(plane, hit)) return null;

    const offset = hit.sub(origin);
    return [offset.dot(east), offset.dot(north)];
  }, [camera, gl, zoneTerrainHeight]);

  // --- Body drag state ---
  const [isDraggingBody, setIsDraggingBody] = useState(false);
  const bodyDragStartRef = useRef<[number, number] | null>(null);
  const bodyDragCoordsRef = useRef<number[][] | null>(null);

  useEffect(() => {
    if (isDraggingBody || isRotating || dragIndex !== null || !pendingCommitCoords) return;
    if (coordsMatch(zone.coordinates, pendingCommitCoords)) {
      setLiveCoords(null);
      setPendingCommitCoords(null);
    }
  }, [dragIndex, isDraggingBody, isRotating, pendingCommitCoords, zone.coordinates]);

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
  }, [dragRef, gl, onInteractionStart, onZoneUpdated, pointerToLatLng, renderedCoords, setControlsEnabled, zone]);

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

  const rotationHandle = useMemo(() => {
    if (!isBuildableZoneType(zone.zone_type) || renderedCoords.length < 3) return null;

    const centroid = computeCentroid(renderedCoords);
    const metersPerLon = Math.max(1, Math.abs(metersPerDegLon(centroid[1])));
    const localPts = renderedCoords.map((coord) => localMetersFromLngLat([coord[0], coord[1]], centroid, metersPerLon));
    const first = localPts[0];
    const second = localPts[1 % localPts.length];
    if (!first || !second) return null;

    const faceMid: [number, number] = [
      (first[0] + second[0]) / 2,
      (first[1] + second[1]) / 2,
    ];
    const faceDistance = Math.hypot(faceMid[0], faceMid[1]);
    if (faceDistance < 0.001) return null;

    const direction: [number, number] = [
      faceMid[0] / faceDistance,
      faceMid[1] / faceDistance,
    ];
    const maxDistance = Math.max(
      ...localPts.map(([east, north]) => Math.hypot(east, north)),
      faceDistance,
    );
    const handleDistance = Math.max(maxDistance * 1.45, faceDistance + 8, 10);
    const northDistance = Math.max(maxDistance * 2.4, handleDistance + 34, 34);
    const handleLocal: [number, number] = [
      direction[0] * handleDistance,
      direction[1] * handleDistance,
    ];
    const northLocal: [number, number] = [0, northDistance];

    const makeLine = (
      points: Array<[number, number, number]>,
      color: string,
      opacity: number,
    ) => {
      const geometry = new THREE.BufferGeometry().setFromPoints(
        points.map(([x, y, z]) => new THREE.Vector3(x, y, z)),
      );
      const material = new THREE.LineBasicMaterial({
        color,
        transparent: opacity < 1,
        opacity,
        depthTest: false,
        depthWrite: false,
      });
      const line = new THREE.Line(geometry, material);
      line.renderOrder = 950;
      return line;
    };

    return {
      centroid,
      metersPerLon,
      handleLocal,
      northLocal,
      stemLine: makeLine(
        [
          [faceMid[0], faceMid[1], ROTATION_HANDLE_LIFT_METERS],
          [handleLocal[0], handleLocal[1], ROTATION_HANDLE_LIFT_METERS],
        ],
        '#f59e0b',
        0.95,
      ),
      northLine: makeLine(
        [
          [0, 0, ROTATION_HANDLE_LIFT_METERS + 0.25],
          [northLocal[0], northLocal[1], ROTATION_HANDLE_LIFT_METERS + 0.25],
        ],
        '#ef4444',
        0.9,
      ),
    };
  }, [renderedCoords, zone.zone_type]);

  const handleRotationPointerDown = useCallback((e: any) => {
    if (!rotationHandle) return;
    e.stopPropagation?.();
    e.preventDefault?.();
    if (rotationDragRef.current) return;

    const pe = e.nativeEvent ?? e;
    const pointerLocal = pointerToRotationPlaneLocal(pe as PointerEvent, rotationHandle.centroid);
    const startAngle = pointerLocal
      ? Math.atan2(pointerLocal[1], pointerLocal[0])
      : Math.atan2(rotationHandle.handleLocal[1], rotationHandle.handleLocal[0]);
    const ownerWindow = gl.domElement.ownerDocument?.defaultView ?? window;

    onInteractionStart?.();
    setPendingCommitCoords(null);
    rotationDragRef.current = {
      centroid: rotationHandle.centroid,
      coords: renderedCoords.map(coord => [...coord]),
      metersPerLon: rotationHandle.metersPerLon,
      startAngle,
    };
    setIsRotating(true);
    setControlsEnabled(false);
    gl.domElement.style.cursor = 'grabbing';

    const target = pe.target as Element | null | undefined;
    if (typeof pe.pointerId === 'number' && target && 'setPointerCapture' in target) {
      try {
        (target as Element & { setPointerCapture: (pointerId: number) => void }).setPointerCapture(pe.pointerId);
      } catch {
        // Pointer capture is best-effort; window listeners still carry the drag.
      }
    }

    const handlePointerMove = (moveEv: PointerEvent | MouseEvent) => {
      const drag = rotationDragRef.current;
      const currentLocal = drag ? pointerToRotationPlaneLocal(moveEv, drag.centroid) : null;
      if (!drag || !currentLocal) return;

      const currentAngle = Math.atan2(currentLocal[1], currentLocal[0]);
      const deltaAngle = currentAngle - drag.startAngle;
      const newCoords = rotateCoordsAroundCentroid(
        drag.coords,
        drag.centroid,
        drag.metersPerLon,
        deltaAngle,
      );

      dragRef.current.zoneId = zone.id;
      dragRef.current.type = 'body';
      dragRef.current.coords = newCoords as [number, number][];
      dragRef.current.version++;
      setLiveCoords(newCoords);
    };

    const handlePointerUp = () => {
      if (typeof pe.pointerId === 'number' && target && 'releasePointerCapture' in target) {
        try {
          (target as Element & { releasePointerCapture: (pointerId: number) => void }).releasePointerCapture(pe.pointerId);
        } catch {
          // Ignore capture cleanup failures from cancelled or already-ended drags.
        }
      }
      const finalCoords = dragRef.current.zoneId === zone.id && dragRef.current.coords.length > 0
        ? dragRef.current.coords.map((coord) => [...coord])
        : null;

      if (finalCoords) {
        setPendingCommitCoords(finalCoords);
        onZoneUpdated(zone.id, finalCoords);
      } else {
        setPendingCommitCoords(null);
        setLiveCoords(null);
      }

      dragRef.current.zoneId = null;
      dragRef.current.type = null;
      dragRef.current.vertexIndex = -1;
      dragRef.current.coords = [];
      dragRef.current.version++;

      rotationDragRef.current = null;
      setIsRotating(false);
      setControlsEnabled(true);
      gl.domElement.style.cursor = '';
      ownerWindow.removeEventListener('pointermove', handlePointerMove);
      ownerWindow.removeEventListener('mousemove', handlePointerMove);
      ownerWindow.removeEventListener('pointerup', handlePointerUp);
      ownerWindow.removeEventListener('mouseup', handlePointerUp);
      ownerWindow.removeEventListener('pointercancel', handlePointerUp);
      ownerWindow.removeEventListener('blur', handlePointerUp);
    };

    ownerWindow.addEventListener('pointermove', handlePointerMove);
    ownerWindow.addEventListener('mousemove', handlePointerMove);
    ownerWindow.addEventListener('pointerup', handlePointerUp);
    ownerWindow.addEventListener('mouseup', handlePointerUp);
    ownerWindow.addEventListener('pointercancel', handlePointerUp);
    ownerWindow.addEventListener('blur', handlePointerUp);
  }, [
    dragRef,
    gl,
    onInteractionStart,
    onZoneUpdated,
    pointerToRotationPlaneLocal,
    renderedCoords,
    rotationHandle,
    setControlsEnabled,
    zone.id,
  ]);

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
  }, [dragRef, gl, onInteractionStart, onZoneUpdated, pointerToLatLng, renderedCoords, setControlsEnabled, zone]);

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
      {rotationHandle && (
        <EastNorthUpFrame
          lat={rotationHandle.centroid[1] * DEG_TO_RAD}
          lon={rotationHandle.centroid[0] * DEG_TO_RAD}
          height={zoneTerrainHeight}
        >
          <primitive object={rotationHandle.stemLine} />
          {isRotating && <primitive object={rotationHandle.northLine} />}

          <mesh
            position={[rotationHandle.handleLocal[0], rotationHandle.handleLocal[1], ROTATION_HANDLE_LIFT_METERS]}
            renderOrder={960}
            onPointerDown={handleRotationPointerDown}
            onPointerEnter={() => { if (!isRotating) gl.domElement.style.cursor = 'grab'; }}
            onPointerLeave={() => { if (!isRotating && dragIndex === null) gl.domElement.style.cursor = ''; }}
          >
            <sphereGeometry args={[2.8, 16, 16]} />
            <meshBasicMaterial
              color="#f59e0b"
              transparent
              opacity={0.18}
              depthTest={false}
              depthWrite={false}
            />
          </mesh>

          <Html
            center
            position={[rotationHandle.handleLocal[0], rotationHandle.handleLocal[1], ROTATION_HANDLE_LIFT_METERS + 0.8]}
            zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
          >
            <div
              className={`h-6 w-6 rounded-full border-2 border-white bg-amber-500 shadow-lg ring-2 ring-amber-300/40 transition-transform ${
                isRotating ? 'scale-125 cursor-grabbing' : 'cursor-grab hover:scale-110'
              }`}
              title="Drag to rotate building"
              onPointerDown={(event) => {
                event.stopPropagation();
                handleRotationPointerDown(event as any);
              }}
              onMouseDown={(event) => {
                event.stopPropagation();
                handleRotationPointerDown(event as any);
              }}
              onPointerEnter={() => { if (!isRotating) gl.domElement.style.cursor = 'grab'; }}
              onPointerLeave={() => { if (!isRotating && dragIndex === null) gl.domElement.style.cursor = ''; }}
            />
          </Html>

          {isRotating && (
            <Html
              center
              position={[rotationHandle.northLocal[0], rotationHandle.northLocal[1], ROTATION_HANDLE_LIFT_METERS + 1.3]}
              zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
              style={{ pointerEvents: 'none' }}
            >
              <div className="pointer-events-none rounded-full border-2 border-white bg-red-500 px-2 py-0.5 text-[11px] font-black uppercase text-white shadow-lg">
                N
              </div>
            </Html>
          )}
        </EastNorthUpFrame>
      )}

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
          <Html center zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}>
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
