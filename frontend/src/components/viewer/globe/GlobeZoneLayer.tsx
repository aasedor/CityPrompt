/**
 * GlobeZoneLayer.tsx — Renders SiteForge zones on the 3D tile globe.
 *
 * Uses EastNorthUpFrame to position zones at their geographic centroid,
 * then renders geometry in local ENU meters (X=East, Y=Up, Z=-North).
 * This avoids ECEF vertex manipulation entirely.
 */

import { useMemo } from 'react';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import {
  resolveZoneColor,
  resolveZoneLabel,
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { createStencilVolume } from './StencilMaskPlugin';

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
): { fillGeo: THREE.BufferGeometry; outlineGeo: THREE.BufferGeometry } | null {
  if (coords.length < 3) return null;
  const flatLift = 0.5; // Base height for thin slab extrusion

  const mPerDegLon = metersPerDegLon(centroidLat);

  // Convert to local ENU meters relative to centroid
  // X = East, Y = North, Z = Up
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
    // Extruded geometry: bottom at Z=0 (ground), top at Z=extrudeHeight
    const baseZ = 0;
    const n = localPts.length;
    const allVerts: number[] = [];
    const allIdx: number[] = [];

    // Bottom face vertices (0..n-1) at Z=baseZ
    for (const p of localPts) allVerts.push(p.x, p.y, baseZ);
    // Top face vertices (n..2n-1) at Z=extrudeHeight
    for (const p of localPts) allVerts.push(p.x, p.y, extrudeHeight);

    // Bottom face triangles
    for (const tri of indices) allIdx.push(tri[0], tri[1], tri[2]);
    // Top face triangles (reversed winding for outward normals)
    for (const tri of indices) allIdx.push(tri[0] + n, tri[2] + n, tri[1] + n);

    // Side walls
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

    // Outline at top of extrusion
    const outlineVerts: number[] = [];
    for (const p of localPts) outlineVerts.push(p.x, p.y, extrudeHeight + 0.05);
    outlineVerts.push(localPts[0].x, localPts[0].y, extrudeHeight + 0.05);
    const outlineGeo = new THREE.BufferGeometry();
    outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

    return { fillGeo, outlineGeo, flatTopGeo: undefined as THREE.BufferGeometry | undefined };
  }

  // Flat zone: create a polygon at Z=0.5 (will be rendered with depthTest=false)
  const flatVerts: number[] = [];
  for (const p of localPts) flatVerts.push(p.x, p.y, flatLift);

  const fillGeo = new THREE.BufferGeometry();
  fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(flatVerts, 3));
  const idxArray: number[] = [];
  for (const tri of indices) idxArray.push(tri[0], tri[1], tri[2]);
  fillGeo.setIndex(idxArray);
  fillGeo.computeVertexNormals();
  fillGeo.computeBoundingSphere();

  // Outline for flat zone
  const outlineVerts: number[] = [];
  for (const p of localPts) outlineVerts.push(p.x, p.y, flatLift + 0.2);
  outlineVerts.push(localPts[0].x, localPts[0].y, flatLift + 0.2);
  const outlineGeo = new THREE.BufferGeometry();
  outlineGeo.setAttribute('position', new THREE.Float32BufferAttribute(outlineVerts, 3));

  return { fillGeo, outlineGeo, flatTopGeo: fillGeo };
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
  // Buildings get real extrusion; flat zones stay at 0 (use separate flatTopGeo for rendering)
  const extrudeHeight = isBuilding ? Math.max(buildingHeight, 10) : 0;

  const geoData = useMemo(() => {
    return createLocalGeometry(
      zone.coordinates, centroid[0], centroid[1], extrudeHeight,
    );
  }, [zone.coordinates, centroid, extrudeHeight]);

  // Stencil volume for building zones — cuts Google 3D buildings inside the zone
  const stencilMesh = useMemo(() => {
    if (!isBuilding || zone.coordinates.length < 3) return null;
    const mPerDegLon = metersPerDegLon(centroid[1]);
    const pts = zone.coordinates.map(c => ({
      x: (c[0] - centroid[0]) * mPerDegLon,
      y: (c[1] - centroid[1]) * METERS_PER_DEG_LAT,
    }));
    return createStencilVolume(pts, Math.max(extrudeHeight * 2, 200));
  }, [zone.coordinates, centroid, isBuilding, extrudeHeight]);

  console.log(`[ZoneMesh] ${zone.name || zone.zone_type}: isBuilding=${isBuilding}, extrudeHeight=${extrudeHeight}, terrainH=${zoneTerrainHeight}, storedTerrain=${storedTerrain}, coords=${zone.coordinates.length}, geoData=${!!geoData}`);

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

      {/* Fill — for flat zones, use a separate high-Z geometry with depthTest=false */}
      {!isBuilding && geoData.flatTopGeo && (
        <mesh
          geometry={geoData.flatTopGeo}
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
            opacity={0.5}
            side={THREE.DoubleSide}
            depthTest={false}
            depthWrite={false}
          />
        </mesh>
      )}

      {/* Fill — buildings use standard depth-tested extrusion */}
      {isBuilding && (
        <mesh
          geometry={geoData.fillGeo}
          renderOrder={100}
          frustumCulled={false}
        onPointerDown={(e) => {
          e.stopPropagation();
          onZoneClick?.(zone.id);
        }}
      >
        <meshBasicMaterial
          color={color}
          transparent
          opacity={isBuilding ? 0.85 : 0.5}
          side={THREE.DoubleSide}
          depthTest
          depthWrite={false}
          polygonOffset
          polygonOffsetFactor={-1}
          polygonOffsetUnits={-1}
        />
      </mesh>
      )}

      {/* Outline */}
      {/* @ts-expect-error R3F line vs SVG line type conflict */}
      <line geometry={geoData.outlineGeo} renderOrder={isBuilding ? 101 : 201} frustumCulled={false} onPointerDown={(e) => {
        e.stopPropagation();
        onZoneClick?.(zone.id);
      }}>
        <lineBasicMaterial
          color={isSelected ? '#ffffff' : color}
          linewidth={isSelected ? 3 : 1.5}
          depthTest
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
