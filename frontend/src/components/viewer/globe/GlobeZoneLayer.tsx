/**
 * GlobeZoneLayer.tsx — Renders SiteForge zones on the 3D tile globe.
 *
 * Uses EastNorthUpFrame to position zones at their geographic centroid,
 * then renders geometry in local ENU meters (X=East, Y=North, Z=Up).
 * Buildings are extruded along Z (up). Flat zones (parks, roads) use
 * terrain draping via raycast to sit precisely on the tile mesh.
 */

import { useMemo, useContext, useRef, useEffect, useCallback, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import {
  resolveZoneColor,
  resolveZoneLabel,
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import {
  createStencilVolume,
  getTileStencilVolumeHeight,
  shouldCreateTileStencilMask,
} from './StencilMaskPlugin';
import { useGlobeDragRef } from './useGlobeDragRef';
import {
  getObjectFilteredTerrainHeight,
  getRepresentativeTerrainHeight,
  resolveZoneTerrainHeight,
  shouldFilterObjectTerrainHeight,
} from './globeTerrainUtils';

const DEG_TO_RAD = Math.PI / 180;
const OBJECT_FILTER_SAMPLE_RADIUS_METERS = 8;
const FLAT_ZONE_SURFACE_LIFT_METERS = 1.4;
const FLAT_ZONE_OUTLINE_LIFT_METERS = 1.9;
const FLAT_ZONE_MAX_EDGE_LENGTH_METERS = 6;
const FLAT_ZONE_MAX_RENDER_VERTICES = 260;
const FLAT_ZONE_DEPTH_OFFSET_FACTOR = -4;
const FLAT_ZONE_DEPTH_OFFSET_UNITS = -8;
const GLOBE_SCENE_HTML_Z_INDEX_RANGE: [number, number] = [1, 0];

interface GlobeZoneLayerProps {
  zones: SiteZone[];
  selectedZoneId: string | null;
  terrainHeight?: number;
  onZoneClick?: (zoneId: string) => void;
  selectionEnabled?: boolean;
}

function coordinatesNearlyEqual(a: number[], b: number[]): boolean {
  return Math.abs(a[0] - b[0]) < 1e-7 && Math.abs(a[1] - b[1]) < 1e-7;
}

function coordinateDistanceMeters(a: number[], b: number[]): number {
  const avgLat = (a[1] + b[1]) / 2;
  const dx = (b[0] - a[0]) * metersPerDegLon(avgLat);
  const dy = (b[1] - a[1]) * METERS_PER_DEG_LAT;
  return Math.hypot(dx, dy);
}

function densifyFlatZoneCoordinates(coords: number[][]): number[][] {
  const ring: number[][] = [];
  for (const coord of coords) {
    if (!coord || coord.length < 2) continue;
    if (ring.length === 0 || !coordinatesNearlyEqual(ring[ring.length - 1], coord)) {
      ring.push(coord);
    }
  }

  if (ring.length > 1 && coordinatesNearlyEqual(ring[0], ring[ring.length - 1])) {
    ring.pop();
  }

  if (ring.length < 3) return ring;

  const perimeter = ring.reduce((sum, coord, index) => (
    sum + coordinateDistanceMeters(coord, ring[(index + 1) % ring.length])
  ), 0);
  const maxEdgeLength = Math.max(
    FLAT_ZONE_MAX_EDGE_LENGTH_METERS,
    perimeter / FLAT_ZONE_MAX_RENDER_VERTICES,
  );
  const densified: number[][] = [];

  ring.forEach((coord, index) => {
    const next = ring[(index + 1) % ring.length];
    densified.push(coord);

    const segmentCount = Math.max(1, Math.ceil(coordinateDistanceMeters(coord, next) / maxEdgeLength));
    for (let step = 1; step < segmentCount; step += 1) {
      const t = step / segmentCount;
      densified.push([
        coord[0] + (next[0] - coord[0]) * t,
        coord[1] + (next[1] - coord[1]) * t,
      ]);
    }
  });

  return densified;
}

/**
 * Create polygon geometry in the ENU local frame.
 *
 * EastNorthUpFrame axes (from 3d-tiles-renderer):
 *   X = East
 *   Y = North
 *   Z = Up
 *
 * Ground plane = XY, height = Z.
 */
function createLocalGeometry(
  coords: number[][],
  centroidLng: number,
  centroidLat: number,
  extrudeHeight: number,
  useTerrainGridFlat: boolean,
): {
  fillGeo: THREE.BufferGeometry;
  fillCoords: number[][];
  outlineGeo: THREE.BufferGeometry;
  flatTopGeo?: THREE.BufferGeometry;
  localPts: { x: number; y: number }[];
} | null {
  if (coords.length < 3) return null;
  const mPerDegLon = metersPerDegLon(centroidLat);

  // Convert to local ENU meters relative to centroid
  const localPts = coords.map(c => ({
    x: (c[0] - centroidLng) * mPerDegLon,           // East
    y: (c[1] - centroidLat) * METERS_PER_DEG_LAT,   // North
  }));

  // Triangulate the 2D polygon (XY ground plane)
  const indices = THREE.ShapeUtils.triangulateShape(
    localPts.map(p => new THREE.Vector2(p.x, p.y)),
    [],
  );

  if (extrudeHeight > 0) {
    const baseZ = 0;
    const n = localPts.length;
    const allVerts: number[] = [];
    const allIdx: number[] = [];

    for (const p of localPts) allVerts.push(p.x, p.y, baseZ);
    for (const p of localPts) allVerts.push(p.x, p.y, extrudeHeight);

    for (const tri of indices) allIdx.push(tri[0], tri[1], tri[2]);
    for (const tri of indices) allIdx.push(tri[0] + n, tri[2] + n, tri[1] + n);

    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      allIdx.push(i, j, j + n);
      allIdx.push(i, j + n, i + n);
    }

    const fillGeo = new THREE.BufferGeometry();
    fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(allVerts, 3));
    fillGeo.setIndex(allIdx);
    fillGeo.computeVertexNormals();
    fillGeo.computeBoundingSphere();

    const outlineVerts: number[] = [];
    for (const p of localPts) outlineVerts.push(p.x, p.y, extrudeHeight + 0.05);
    outlineVerts.push(localPts[0].x, localPts[0].y, extrudeHeight + 0.05);
    const outlineGeo = new THREE.BufferGeometry();
    outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

    return { fillGeo, fillCoords: coords, outlineGeo, localPts };
  }

  // Flat zone
  if (!useTerrainGridFlat) {
    const flatVerts: number[] = [];
    for (const p of localPts) flatVerts.push(p.x, p.y, FLAT_ZONE_SURFACE_LIFT_METERS);

    const fillGeo = new THREE.BufferGeometry();
    fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
    const idxArray: number[] = [];
    for (const tri of indices) idxArray.push(tri[0], tri[1], tri[2]);
    fillGeo.setIndex(idxArray);
    fillGeo.computeVertexNormals();
    fillGeo.computeBoundingSphere();

    const outlineVerts: number[] = [];
    for (const p of localPts) outlineVerts.push(p.x, p.y, FLAT_ZONE_OUTLINE_LIFT_METERS);
    outlineVerts.push(localPts[0].x, localPts[0].y, FLAT_ZONE_OUTLINE_LIFT_METERS);
    const outlineGeo = new THREE.BufferGeometry();
    outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

    return { fillGeo, fillCoords: coords, outlineGeo, flatTopGeo: fillGeo, localPts };
  }

  const flatVerts: number[] = [];
  const fillCoords: number[][] = [];
  const idxArray: number[] = [];
  const ringScales = [1, 0.72, 0.44, 0.18];
  const ringCount = ringScales.length;
  const vertexCountPerRing = localPts.length;

  for (const scale of ringScales) {
    for (const p of localPts) {
      const x = p.x * scale;
      const y = p.y * scale;
      flatVerts.push(x, y, FLAT_ZONE_SURFACE_LIFT_METERS);
      fillCoords.push([
        centroidLng + x / mPerDegLon,
        centroidLat + y / METERS_PER_DEG_LAT,
      ]);
    }
  }

  const centerIndex = fillCoords.length;
  flatVerts.push(0, 0, FLAT_ZONE_SURFACE_LIFT_METERS);
  fillCoords.push([centroidLng, centroidLat]);

  for (let ring = 0; ring < ringCount - 1; ring += 1) {
    const outerOffset = ring * vertexCountPerRing;
    const innerOffset = (ring + 1) * vertexCountPerRing;
    for (let i = 0; i < vertexCountPerRing; i += 1) {
      const next = (i + 1) % vertexCountPerRing;
      idxArray.push(outerOffset + i, outerOffset + next, innerOffset + next);
      idxArray.push(outerOffset + i, innerOffset + next, innerOffset + i);
    }
  }

  const innerOffset = (ringCount - 1) * vertexCountPerRing;
  for (let i = 0; i < vertexCountPerRing; i += 1) {
    const next = (i + 1) % vertexCountPerRing;
    idxArray.push(innerOffset + i, innerOffset + next, centerIndex);
  }

  const fillGeo = new THREE.BufferGeometry();
  fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
  fillGeo.setIndex(idxArray);
  fillGeo.computeVertexNormals();
  fillGeo.computeBoundingSphere();

  const outlineVerts: number[] = [];
  for (const p of localPts) outlineVerts.push(p.x, p.y, FLAT_ZONE_OUTLINE_LIFT_METERS);
  outlineVerts.push(localPts[0].x, localPts[0].y, FLAT_ZONE_OUTLINE_LIFT_METERS);
  const outlineGeo = new THREE.BufferGeometry();
  outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

  return { fillGeo, fillCoords, outlineGeo, flatTopGeo: fillGeo, localPts };
}

/**
 * Raycast from high altitude straight down onto the tile mesh at a given lat/lng.
 * Returns the hit point in ECEF, or null if no hit.
 */
function raycastTerrainAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): THREE.Vector3 | null {
  const origin = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat * DEG_TO_RAD, lng * DEG_TO_RAD, 50000, origin);
  const normal = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToNormal(lat * DEG_TO_RAD, lng * DEG_TO_RAD, normal);
  raycaster.set(origin, normal.negate());
  raycaster.far = 100000;

  const hits = raycaster.intersectObjects(tilesGroup.children, true);
  return hits.length > 0 ? hits[0].point.clone() : null;
}

function raycastTerrainHeightAtLatLng(
  lng: number,
  lat: number,
  tilesGroup: THREE.Object3D,
  raycaster: THREE.Raycaster,
): number | null {
  const hit = raycastTerrainAtLatLng(lng, lat, tilesGroup, raycaster);
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

function ZoneMesh({ zone, isSelected, terrainHeight, onZoneClick, selectionEnabled }: {
  zone: SiteZone;
  isSelected: boolean;
  terrainHeight: number;
  onZoneClick?: (zoneId: string) => void;
  selectionEnabled?: boolean;
}) {
  const color = resolveZoneColor(zone);
  const label = resolveZoneLabel(zone);
  const centroid = computeCentroid(zone.coordinates);
  const tiles = useContext(TilesRendererContext);
  const zoneProps = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProps?.terrain_elevation_m
    ?? zoneProps?.terrain_height
    ?? zoneProps?.terrainElevation,
  );
  const storedTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : null;

  const buildingHeight = (zone.properties?.height_m as number)
    || (zone.properties?.height as number)
    || ((zone.properties?.floors as number) || 0) * 3.2
    || 0;
  const isBuilding = zone.zone_type === 'building' || zone.zone_type === 'residential';
  const isSiteBoundary = zone.zone_type === 'site_boundary';
  const shouldRespectTileDepth = isBuilding || zone.zone_type === 'green_space';
  const shouldMaskTileGeometry = shouldCreateTileStencilMask(zone.zone_type);
  const filterObjectHeights = shouldFilterObjectTerrainHeight(zone.zone_type);
  const extrudeHeight = isBuilding ? Math.max(buildingHeight, 10) : 0;
  const useTerrainGridFlat = zone.zone_type === 'green_space';
  const renderCoordinates = useMemo(
    () => (useTerrainGridFlat && zone.coordinates.length >= 3
      ? densifyFlatZoneCoordinates(zone.coordinates)
      : zone.coordinates),
    [useTerrainGridFlat, zone.coordinates],
  );

  const geoData = useMemo(() => {
    return createLocalGeometry(
      renderCoordinates, centroid[0], centroid[1], extrudeHeight, useTerrainGridFlat,
    );
  }, [renderCoordinates, centroid, extrudeHeight, useTerrainGridFlat]);

  // --- Terrain draping for flat zones ---
  // Raycast each vertex onto the tile mesh to get precise ground elevation offsets
  const flatMeshRef = useRef<THREE.Mesh>(null);
  const flatOutlineRef = useRef<any>(null);
  const buildingMeshRef = useRef<THREE.Mesh>(null);
  const buildingOutlineRef = useRef<any>(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const drapedRef = useRef(false);
  const drapeAttemptRef = useRef(0);
  const [sampledTerrainHeight, setSampledTerrainHeight] = useState<number | null>(null);
  const zoneTerrainHeight = resolveZoneTerrainHeight(
    sampledTerrainHeight,
    storedTerrainHeight,
    terrainHeight,
  );

  // ── Drag performance: useFrame-based geometry update ──
  // Reads the shared drag ref and updates BufferGeometry positions directly,
  // bypassing React state to avoid re-rendering the entire scene.
  const dragRef = useGlobeDragRef();
  const lastDragVersionRef = useRef(0);

  const sampleZoneTerrainHeight = useCallback(() => {
    const tilesGroup = tiles?.group;
    if (!tilesGroup || tilesGroup.children.length === 0) return false;

    const raycaster = raycasterRef.current;
    const sampledHeight = getRepresentativeTerrainHeight(
      getTerrainProbePoints(zone.coordinates, centroid).map(([lng, lat]) => (
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
  }, [centroid, filterObjectHeights, tiles, zone.coordinates, zoneTerrainHeight]);

  useFrame(() => {
    const drag = dragRef.current;
    if (drag.zoneId !== zone.id) return;
    if (drag.version === lastDragVersionRef.current) return;
    lastDragVersionRef.current = drag.version;

    // Recompute local ENU positions from drag coords
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const coords = drag.coords;
    const n = coords.length;

    // Update fill geometry
    const meshRef = isBuilding ? buildingMeshRef : flatMeshRef;
    const outRef = isBuilding ? buildingOutlineRef : flatOutlineRef;
    const renderDragCoords = isBuilding ? coords : densifyFlatZoneCoordinates(coords);
    const renderN = renderDragCoords.length;

    if (meshRef.current && !useTerrainGridFlat) {
      const posAttr = meshRef.current.geometry.attributes.position;
      if (posAttr) {
        for (let i = 0; i < renderN && i < posAttr.count; i++) {
          const localX = (renderDragCoords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (renderDragCoords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
          posAttr.setX(i, localX);
          posAttr.setY(i, localY);
          // For extruded buildings, also update the top ring (indices n..2n-1)
          if (isBuilding && i + n < posAttr.count) {
            posAttr.setX(i + n, localX);
            posAttr.setY(i + n, localY);
          }
        }
        posAttr.needsUpdate = true;
        meshRef.current.geometry.computeBoundingSphere();
      }
    }

    // Update outline geometry
    if (outRef.current) {
      const outPos = outRef.current.geometry.attributes.position;
      if (outPos) {
        for (let i = 0; i < renderN && i < outPos.count; i++) {
          const localX = (renderDragCoords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (renderDragCoords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
          outPos.setX(i, localX);
          outPos.setY(i, localY);
        }
        // Close-loop vertex
        if (outPos.count > renderN) {
          outPos.setX(renderN, outPos.getX(0));
          outPos.setY(renderN, outPos.getY(0));
        }
        outPos.needsUpdate = true;
      }
    }
  });

  const drapeToTerrain = useCallback(() => {
    if (!tiles?.group || !geoData || isBuilding || drapedRef.current) return;
    if (!flatMeshRef.current) return;
    drapeAttemptRef.current++;

    const raycaster = raycasterRef.current;
    let hitCount = 0;

    // For each vertex, raycast to find terrain Z in ENU frame
    const posAttr = flatMeshRef.current.geometry.attributes.position;
    if (!posAttr) return;

    for (let i = 0; i < geoData.fillCoords.length && i < posAttr.count; i++) {
      const coord = geoData.fillCoords[i];
      const hitElev = filterObjectHeights
        ? raycastObjectFilteredTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster, zoneTerrainHeight)
        : raycastTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster);
      if (hitElev !== null) {
        // Z offset in ENU = hitElev - zoneTerrainHeight (the ENU frame origin elevation)
        const zOffset = hitElev - zoneTerrainHeight + FLAT_ZONE_SURFACE_LIFT_METERS;
        posAttr.setZ(i, zOffset);
        hitCount++;
      }
    }

    if (hitCount > 0) {
      posAttr.needsUpdate = true;
      flatMeshRef.current.geometry.computeBoundingSphere();

      // Also update outline
      if (flatOutlineRef.current) {
        const outPos = flatOutlineRef.current.geometry.attributes.position;
        if (outPos) {
          for (let i = 0; i < renderCoordinates.length && i < outPos.count - 1; i++) {
            const coord = renderCoordinates[i];
            const hitElev = filterObjectHeights
              ? raycastObjectFilteredTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster, zoneTerrainHeight)
              : raycastTerrainHeightAtLatLng(coord[0], coord[1], tiles.group, raycaster);
            if (hitElev !== null) {
              const zOffset = hitElev - zoneTerrainHeight + FLAT_ZONE_OUTLINE_LIFT_METERS;
              outPos.setZ(i, zOffset);
            }
          }
          // Close the loop vertex
          if (outPos.count > renderCoordinates.length) {
            outPos.setZ(renderCoordinates.length, outPos.getZ(0));
          }
          outPos.needsUpdate = true;
        }
      }

      if (hitCount >= geoData.fillCoords.length * 0.5) {
        drapedRef.current = true;
      }
    }
  }, [tiles, geoData, isBuilding, filterObjectHeights, renderCoordinates, zoneTerrainHeight]);

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

  // Progressive drape: try at 2s, 5s, 10s after mount (tiles need time to load)
  useEffect(() => {
    if (isBuilding || !tiles) return;
    drapedRef.current = false;
    drapeAttemptRef.current = 0;
    const timers = [
      setTimeout(drapeToTerrain, 2000),
      setTimeout(drapeToTerrain, 5000),
      setTimeout(drapeToTerrain, 10000),
    ];
    return () => timers.forEach(clearTimeout);
  }, [tiles, drapeToTerrain, isBuilding, zoneTerrainHeight]);

  // Periodic re-drape for LOD updates (low frequency)
  useFrame(() => {
    if (sampledTerrainHeight === null && tiles?.group && Math.random() < 0.003) {
      sampleZoneTerrainHeight();
    }
    if (isBuilding || drapedRef.current || drapeAttemptRef.current >= 15) return;
    if (!tiles?.group) return;
    if (Math.random() < 0.005) drapeToTerrain(); // ~0.5% chance per frame
  });

  // Stencil volume for zones that should clear existing Google tile geometry.
  const stencilMesh = useMemo(() => {
    if (!shouldMaskTileGeometry || zone.coordinates.length < 3) return null;
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const pts = zone.coordinates.map(c => ({
      x: (c[0] - centroid[0]) * mPerDegLon,
      y: (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
    }));
    return createStencilVolume(
      pts,
      getTileStencilVolumeHeight(zone.zone_type, extrudeHeight),
    );
  }, [zone.coordinates, centroid, shouldMaskTileGeometry, zone.zone_type, extrudeHeight]);

  const handleZonePointerDown = useCallback((e: { stopPropagation: () => void }) => {
    // When the zone is already selected, let the edit surface behind it
    // receive the pointer event so body dragging can start.
    if (isSelected || selectionEnabled === false) return;
    e.stopPropagation();
    onZoneClick?.(zone.id);
  }, [isSelected, onZoneClick, selectionEnabled, zone.id]);

  if (!geoData) return null;

  return (
    <EastNorthUpFrame
      lat={centroid[1] * DEG_TO_RAD}
      lon={centroid[0] * DEG_TO_RAD}
      height={zoneTerrainHeight}
    >
      {/* Stencil volume — invisible, writes to stencil buffer */}
      {stencilMesh && (
        <primitive object={stencilMesh} />
      )}

      {/* Fill — flat zones with terrain draping */}
      {/* Fill — flat zones: layered by type */}
      {/* Render order: site_boundary(100) < green_space(110) < road(120) < buildings(200) */}
      {!isBuilding && geoData.flatTopGeo && (
        <mesh
          ref={flatMeshRef}
          geometry={geoData.flatTopGeo.clone()}
          renderOrder={isSiteBoundary ? 100 : zone.zone_type === 'green_space' ? 110 : 120}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
        >
          <meshBasicMaterial
            color={isSiteBoundary ? '#ffffff' : color}
            transparent
            opacity={isSiteBoundary ? 0.15 : 1.0}
            side={THREE.DoubleSide}
            depthTest={shouldRespectTileDepth}
            depthWrite={false}
            polygonOffset={shouldRespectTileDepth}
            polygonOffsetFactor={isBuilding ? -1 : FLAT_ZONE_DEPTH_OFFSET_FACTOR}
            polygonOffsetUnits={isBuilding ? -1 : FLAT_ZONE_DEPTH_OFFSET_UNITS}
          />
        </mesh>
      )}

      {/* Fill — buildings on top of everything */}
      {isBuilding && (
        <mesh
          ref={buildingMeshRef}
          geometry={geoData.fillGeo}
          renderOrder={200}
          frustumCulled={false}
          onPointerDown={handleZonePointerDown}
        >
          <meshBasicMaterial
            color={color}
            transparent
            opacity={1.0}
            side={THREE.DoubleSide}
            depthTest
            depthWrite={false}
            polygonOffset
            polygonOffsetFactor={-1}
            polygonOffsetUnits={-1}
          />
        </mesh>
      )}

      {/* Outline geometry is spread because JSX line resolves to SVG typings here. */}
      <line
        ref={isBuilding ? buildingOutlineRef : flatOutlineRef as any}
        {...({ geometry: !isBuilding ? geoData.outlineGeo.clone() : geoData.outlineGeo } as any)}
        renderOrder={isBuilding ? 201 : isSiteBoundary ? 101 : zone.zone_type === 'green_space' ? 111 : 121}
        frustumCulled={false}
        onPointerDown={handleZonePointerDown}
      >
        <lineBasicMaterial
          color={isSelected ? '#ffffff' : color}
          linewidth={isSelected ? 3 : 1.5}
          depthTest={shouldRespectTileDepth}
          depthWrite={false}
        />
      </line>

      {/* Label — positioned above the zone */}
      <group position={[0, 0, extrudeHeight + 8]}>
        <Html
          center
          zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
          style={{ pointerEvents: 'none' }}
        >
          <div className="whitespace-nowrap rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-medium text-white backdrop-blur-sm">
            {label}
          </div>
        </Html>
      </group>
    </EastNorthUpFrame>
  );
}

export function GlobeZoneLayer({
  zones,
  selectedZoneId,
  terrainHeight = 1045,
  onZoneClick,
  selectionEnabled = true,
}: GlobeZoneLayerProps) {
  return (
    <>
      {zones.map(zone => (
        <ZoneMesh
          key={zone.id}
          zone={zone}
          isSelected={zone.id === selectedZoneId}
          terrainHeight={terrainHeight}
          onZoneClick={onZoneClick}
          selectionEnabled={selectionEnabled}
        />
      ))}
    </>
  );
}
