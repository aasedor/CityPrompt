/**
 * GlobeEditMode.tsx — Zone editing UI for the 3D globe.
 *
 * When a zone is selected in Select mode, renders:
 * - Draggable vertex handles at each polygon vertex
 * - Drag to reshape the zone boundary
 *
 * Uses the terrain-adjusted ellipsoid raycast for vertex snapping.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { Html } from '@react-three/drei';
import { Ellipsoid } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

interface GlobeEditModeProps {
  zone: SiteZone;
  terrainHeight: number;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
}

export function GlobeEditMode({ zone, terrainHeight, onZoneUpdated }: GlobeEditModeProps) {
  const { camera, gl } = useThree();
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const originalCoordsRef = useRef<number[][] | null>(null);
  const zoneProps = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProps?.terrain_elevation_m
    ?? zoneProps?.terrain_height
    ?? zoneProps?.terrainElevation,
  );
  const zoneTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : terrainHeight;
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

  // Raycast to get lat/lng from pointer event
  const pointerToLatLng = useCallback((e: PointerEvent): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

    const hit = new THREE.Vector3();
    const result = terrainEllipsoid.current.intersectRay(raycaster.ray, hit);
    if (!result) return null;

    const carto = terrainEllipsoid.current.getPositionToCartographic(hit, {} as any);
    return [carto.lon * RAD_TO_DEG, carto.lat * RAD_TO_DEG];
  }, [camera, gl]);

  // --- Body drag state ---
  const [isDraggingBody, setIsDraggingBody] = useState(false);
  const bodyDragStartRef = useRef<[number, number] | null>(null);
  const bodyDragCoordsRef = useRef<number[][] | null>(null);

  // Start dragging the zone body
  const handleBodyPointerDown = useCallback((e: any) => {
    e.stopPropagation();
    const pe = e.nativeEvent ?? e;
    const startLatLng = pointerToLatLng(pe as PointerEvent);
    if (!startLatLng) return;

    bodyDragStartRef.current = startLatLng;
    bodyDragCoordsRef.current = zone.coordinates.map(c => [...c]);
    setIsDraggingBody(true);
    gl.domElement.style.cursor = 'grabbing';

    const handlePointerMove = (moveEv: PointerEvent) => {
      const currentLatLng = pointerToLatLng(moveEv);
      if (!currentLatLng || !bodyDragStartRef.current || !bodyDragCoordsRef.current) return;

      const dlng = currentLatLng[0] - bodyDragStartRef.current[0];
      const dlat = currentLatLng[1] - bodyDragStartRef.current[1];

      const newCoords = bodyDragCoordsRef.current.map(c => [c[0] + dlng, c[1] + dlat]);
      onZoneUpdated(zone.id, newCoords);
    };

    const handlePointerUp = () => {
      setIsDraggingBody(false);
      bodyDragStartRef.current = null;
      bodyDragCoordsRef.current = null;
      gl.domElement.style.cursor = '';
      gl.domElement.removeEventListener('pointermove', handlePointerMove);
      gl.domElement.removeEventListener('pointerup', handlePointerUp);
    };

    gl.domElement.addEventListener('pointermove', handlePointerMove);
    gl.domElement.addEventListener('pointerup', handlePointerUp);
  }, [zone, gl, pointerToLatLng, onZoneUpdated]);

  // --- Build drag surface geometry (same shape as zone, invisible) ---
  // ENU frame: X=East, Y=North, Z=Up. Ground plane = XY.
  const dragSurfaceGeo = useMemo(() => {
    if (zone.coordinates.length < 3) return null;
    const centroid = computeCentroid(zone.coordinates);
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const localPts = zone.coordinates.map(c => new THREE.Vector2(
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
  }, [zone.coordinates]);

  // Start dragging a vertex
  const handleVertexPointerDown = useCallback((index: number, e: any) => {
    e.stopPropagation();
    setDragIndex(index);
    originalCoordsRef.current = zone.coordinates.map(c => [...c]);

    const canvas = gl.domElement;

    const handlePointerMove = (pe: PointerEvent) => {
      const lngLat = pointerToLatLng(pe);
      if (!lngLat || !originalCoordsRef.current) return;

      // Update this vertex
      const newCoords = originalCoordsRef.current.map((c, i) =>
        i === index ? [...lngLat] : [...c]
      );

      // Live update
      onZoneUpdated(zone.id, newCoords);
    };

    const handlePointerUp = () => {
      setDragIndex(null);
      originalCoordsRef.current = null;
      canvas.removeEventListener('pointermove', handlePointerMove);
      canvas.removeEventListener('pointerup', handlePointerUp);
    };

    canvas.addEventListener('pointermove', handlePointerMove);
    canvas.addEventListener('pointerup', handlePointerUp);
  }, [zone, gl, pointerToLatLng, onZoneUpdated]);

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

      {/* Vertex handles */}
      {zone.coordinates.map((coord, i) => (
        <EastNorthUpFrame
          key={`edit-v-${i}`}
          lat={coord[1] * DEG_TO_RAD}
          lon={coord[0] * DEG_TO_RAD}
          height={zoneTerrainHeight}
        >
          <mesh
            renderOrder={900}
            onPointerDown={(e) => handleVertexPointerDown(i, e)}
          >
            <sphereGeometry args={[4, 12, 12]} />
            <meshBasicMaterial
              color={dragIndex === i ? '#f59e0b' : '#ffffff'}
              depthTest={false}
              depthWrite={false}
            />
          </mesh>
          <Html center style={{ pointerEvents: 'none' }}>
            <div
              className={`h-3 w-3 rounded-full border-2 shadow-md cursor-grab ${
                dragIndex === i ? 'border-amber-500 bg-amber-400' : 'border-white bg-white'
              }`}
            />
          </Html>
        </EastNorthUpFrame>
      ))}
    </>
  );
}
