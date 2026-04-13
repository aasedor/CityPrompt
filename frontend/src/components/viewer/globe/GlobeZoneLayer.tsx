/**
 * GlobeZoneLayer.tsx — Renders SiteForge zones on the 3D tile globe.
 *
 * Uses EastNorthUpFrame to position zones at their geographic centroid,
 * then renders geometry in local ENU meters (X=East, Y=North, Z=Up).
 * Buildings are extruded along Z (up). Flat zones (parks, roads) use
 * terrain draping via raycast to sit precisely on the tile mesh.
 */

import { useMemo, useContext, useRef, useEffect, useCallback } from 'react';
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
import { createStencilVolume } from './StencilMaskPlugin';
import { useGlobeDragRef } from './useGlobeDragRef';

const DEG_TO_RAD = Math.PI / 180;

interface GlobeZoneLayerProps {
  zones: SiteZone[];
  selectedZoneId: string | null;
  terrainHeight?: number;
  onZoneClick?: (zoneId: string) => void;
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
): {
  fillGeo: THREE.BufferGeometry;
  outlineGeo: THREE.BufferGeometry;
  flatTopGeo?: THREE.BufferGeometry;
  localPts: { x: number; y: number }[];
} | null {
  if (coords.length < 3) return null;
  const flatLift = 0.5;

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

    return { fillGeo, outlineGeo, localPts };
  }

  // Flat zone
  const flatVerts: number[] = [];
  for (const p of localPts) flatVerts.push(p.x, p.y, flatLift);

  const fillGeo = new THREE.BufferGeometry();
  fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
  const idxArray: number[] = [];
  for (const tri of indices) idxArray.push(tri[0], tri[1], tri[2]);
  fillGeo.setIndex(idxArray);
  fillGeo.computeVertexNormals();
  fillGeo.computeBoundingSphere();

  const outlineVerts: number[] = [];
  for (const p of localPts) outlineVerts.push(p.x, p.y, flatLift + 0.2);
  outlineVerts.push(localPts[0].x, localPts[0].y, flatLift + 0.2);
  const outlineGeo = new THREE.BufferGeometry();
  outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

  return { fillGeo, outlineGeo, flatTopGeo: fillGeo, localPts };
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

function ZoneMesh({ zone, isSelected, terrainHeight, onZoneClick }: {
  zone: SiteZone;
  isSelected: boolean;
  terrainHeight: number;
  onZoneClick?: (zoneId: string) => void;
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
  const zoneTerrainHeight = Number.isFinite(storedTerrain) ? storedTerrain : terrainHeight;

  const buildingHeight = (zone.properties?.height_m as number)
    || (zone.properties?.height as number)
    || ((zone.properties?.floors as number) || 0) * 3.2
    || 0;
  const isBuilding = zone.zone_type === 'building' || zone.zone_type === 'residential';
  const isSiteBoundary = zone.zone_type === 'site_boundary';
  const extrudeHeight = isBuilding ? Math.max(buildingHeight, 10) : 0;

  const geoData = useMemo(() => {
    return createLocalGeometry(
      zone.coordinates, centroid[0], centroid[1], extrudeHeight,
    );
  }, [zone.coordinates, centroid, extrudeHeight]);

  // --- Terrain draping for flat zones ---
  // Raycast each vertex onto the tile mesh to get precise ground elevation offsets
  const flatMeshRef = useRef<THREE.Mesh>(null);
  const flatOutlineRef = useRef<any>(null);
  const buildingMeshRef = useRef<THREE.Mesh>(null);
  const buildingOutlineRef = useRef<any>(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const drapedRef = useRef(false);
  const drapeAttemptRef = useRef(0);

  // ── Drag performance: useFrame-based geometry update ──
  // Reads the shared drag ref and updates BufferGeometry positions directly,
  // bypassing React state to avoid re-rendering the entire scene.
  const dragRef = useGlobeDragRef();
  const lastDragVersionRef = useRef(0);

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

    if (meshRef.current) {
      const posAttr = meshRef.current.geometry.attributes.position;
      if (posAttr) {
        for (let i = 0; i < n && i < posAttr.count; i++) {
          const localX = (coords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (coords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
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
        for (let i = 0; i < n && i < outPos.count; i++) {
          const localX = (coords[i][0] - centroid[0]) * mPerDegLon;
          const localY = (coords[i][1] - centroid[1]) * METERS_PER_DEG_LAT;
          outPos.setX(i, localX);
          outPos.setY(i, localY);
        }
        // Close-loop vertex
        if (outPos.count > n) {
          outPos.setX(n, outPos.getX(0));
          outPos.setY(n, outPos.getY(0));
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
    const mPerDegLon = metersPerDegLon(centroid[1]);
    let hitCount = 0;

    // For each vertex, raycast to find terrain Z in ENU frame
    const posAttr = flatMeshRef.current.geometry.attributes.position;
    if (!posAttr) return;

    for (let i = 0; i < zone.coordinates.length && i < posAttr.count; i++) {
      const coord = zone.coordinates[i];
      const hit = raycastTerrainAtLatLng(coord[0], coord[1], tiles.group, raycaster);
      if (hit) {
        // Convert ECEF hit point to elevation
        const hitElev = WGS84_ELLIPSOID.getPositionElevation(hit);
        // Z offset in ENU = hitElev - zoneTerrainHeight (the ENU frame origin elevation)
        const zOffset = hitElev - zoneTerrainHeight + 1.0; // +1m above terrain surface
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
          for (let i = 0; i < zone.coordinates.length && i < outPos.count - 1; i++) {
            const coord = zone.coordinates[i];
            const hit = raycastTerrainAtLatLng(coord[0], coord[1], tiles.group, raycaster);
            if (hit) {
              const hitElev = WGS84_ELLIPSOID.getPositionElevation(hit);
              const zOffset = hitElev - zoneTerrainHeight + 1.2;
              outPos.setZ(i, zOffset);
            }
          }
          // Close the loop vertex
          if (outPos.count > zone.coordinates.length) {
            outPos.setZ(zone.coordinates.length, outPos.getZ(0));
          }
          outPos.needsUpdate = true;
        }
      }

      if (hitCount >= zone.coordinates.length * 0.5) {
        drapedRef.current = true;
      }
    }
  }, [tiles, geoData, isBuilding, zone.coordinates, centroid, zoneTerrainHeight]);

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
  }, [tiles, drapeToTerrain, isBuilding]);

  // Periodic re-drape for LOD updates (low frequency)
  useFrame(() => {
    if (isBuilding || drapedRef.current || drapeAttemptRef.current >= 15) return;
    if (!tiles?.group) return;
    if (Math.random() < 0.005) drapeToTerrain(); // ~0.5% chance per frame
  });

  // Stencil volume for building zones
  const stencilMesh = useMemo(() => {
    if (!isBuilding || zone.coordinates.length < 3) return null;
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const pts = zone.coordinates.map(c => ({
      x: (c[0] - centroid[0]) * mPerDegLon,
      y: (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
    }));
    return createStencilVolume(pts, Math.max(extrudeHeight * 2, 200));
  }, [zone.coordinates, centroid, isBuilding, extrudeHeight]);

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
          onPointerDown={(e) => {
            e.stopPropagation();
            onZoneClick?.(zone.id);
          }}
        >
          <meshBasicMaterial
            color={isSiteBoundary ? '#ffffff' : color}
            transparent
            opacity={isSiteBoundary ? 0.15 : 1.0}
            side={THREE.DoubleSide}
            depthTest={false}
            depthWrite={false}
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
          onPointerDown={(e) => {
            e.stopPropagation();
            onZoneClick?.(zone.id);
          }}
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

      {/* Outline — R3F <line> type conflicts with SVG <line>, suppress with any refs */}
      <line
        ref={isBuilding ? buildingOutlineRef : flatOutlineRef as any}
        geometry={!isBuilding ? geoData.outlineGeo.clone() : geoData.outlineGeo}
        renderOrder={isBuilding ? 201 : isSiteBoundary ? 101 : zone.zone_type === 'green_space' ? 111 : 121}
        frustumCulled={false}
        onPointerDown={(e) => {
          e.stopPropagation();
          onZoneClick?.(zone.id);
        }}
      >
        <lineBasicMaterial
          color={isSelected ? '#ffffff' : color}
          linewidth={isSelected ? 3 : 1.5}
          depthTest={isBuilding}
          depthWrite={false}
        />
      </line>

      {/* Label — positioned above the zone */}
      <group position={[0, 0, extrudeHeight + 8]}>
        <Html center style={{ pointerEvents: 'none' }}>
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
        />
      ))}
    </>
  );
}
