/**
 * Persistent stencil volumes for loaded replacement buildings.
 *
 * This layer intentionally lives outside the zone-overlay visibility group:
 * clean screenshots hide planning overlays, but the Google photogrammetry
 * beneath a mounted GLB/LEGO stack must remain clipped in every capture mode.
 */

import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { EastNorthUpFrame, TilesRendererContext } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import {
  createStencilVolume,
  getTileStencilVolumeHeight,
  resolveTileStencilAnchorHeight,
  shouldCreateTileStencilMask,
} from './StencilMaskPlugin';
import {
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';
import { raycastTerrainHeightAtLatLng } from './GlobeZoneLayer';
import { createTileSpatialMaskSetConfig } from './TileSpatialMaskPlugin';

const DEG_TO_RAD = Math.PI / 180;
const TERRAIN_SAMPLE_FRAME_INTERVAL = 30;
const TERRAIN_SAMPLE_MAX_ATTEMPTS = 20;

interface GlobeTileMaskLayerProps {
  zones: SiteZone[];
  terrainHeight: number;
}

function TileMaskVolume({ zone, terrainHeight }: { zone: SiteZone; terrainHeight: number }) {
  const tiles = useContext(TilesRendererContext);
  const raycasterRef = useRef(new THREE.Raycaster());
  const frameCountRef = useRef(0);
  const attemptsRef = useRef(0);
  const frozenRef = useRef(false);
  const [sampledAnchor, setSampledAnchor] = useState<number | null>(null);
  const centroid = useMemo(() => computeCentroid(zone.coordinates), [zone.coordinates]);
  const buildingHeight = Number(
    zone.properties?.height_m
    ?? zone.properties?.height
    ?? Number(zone.properties?.floors ?? 0) * 3.2,
  );
  const zoneProperties = zone.properties as Record<string, unknown> | undefined;
  const storedTerrain = Number(
    zoneProperties?.terrain_elevation_m
    ?? zoneProperties?.terrain_height
    ?? zoneProperties?.terrainElevation,
  );
  const storedAnchor = Number.isFinite(storedTerrain) ? storedTerrain : null;
  const anchorHeight = sampledAnchor
    ?? storedAnchor
    ?? terrainHeight;

  useEffect(() => {
    frameCountRef.current = 0;
    attemptsRef.current = 0;
    frozenRef.current = false;
    setSampledAnchor(null);
  }, [terrainHeight, zone.coordinates, zone.updated_at]);

  useFrame(() => {
    if (frozenRef.current || attemptsRef.current >= TERRAIN_SAMPLE_MAX_ATTEMPTS) return;
    frameCountRef.current += 1;
    if (frameCountRef.current % TERRAIN_SAMPLE_FRAME_INTERVAL !== 0) return;
    const group = tiles?.group;
    if (!group || group.children.length === 0) return;
    attemptsRef.current += 1;
    const step = Math.max(1, Math.ceil(zone.coordinates.length / 6));
    const edgeProbes = zone.coordinates.filter((_, index) => index % step === 0);
    const mPerLon = Math.max(1, Math.abs(metersPerDegLon(centroid[1])));
    const outsideProbes = edgeProbes.map(([lng, lat]) => {
      const east = (lng - centroid[0]) * mPerLon;
      const north = (lat - centroid[1]) * METERS_PER_DEG_LAT;
      const length = Math.hypot(east, north) || 1;
      const outwardM = 3;
      return [
        lng + (east / length) * outwardM / mPerLon,
        lat + (north / length) * outwardM / METERS_PER_DEG_LAT,
      ];
    });
    const probes = [centroid, ...edgeProbes, ...outsideProbes];
    const samples = probes.map(([lng, lat]) => (
      raycastTerrainHeightAtLatLng(lng, lat, group, raycasterRef.current)
    ));
    if (!samples.some(Number.isFinite)) return;
    setSampledAnchor(resolveTileStencilAnchorHeight(samples, storedAnchor, terrainHeight));
    frozenRef.current = true;
  });

  const mesh = useMemo(() => {
    if (!shouldCreateTileStencilMask(zone.zone_type) || zone.coordinates.length < 3) {
      return null;
    }
    const metersPerLongitudeDegree = metersPerDegLon(centroid[1]);
    const points = zone.coordinates.map((coordinate) => ({
      x: (coordinate[0] - centroid[0]) * metersPerLongitudeDegree,
      y: (coordinate[1] - centroid[1]) * METERS_PER_DEG_LAT,
    }));
    return createStencilVolume(
      points,
      getTileStencilVolumeHeight(
        zone.zone_type,
        Number.isFinite(buildingHeight) ? Math.max(buildingHeight, 10) : 10,
      ),
    );
  }, [buildingHeight, centroid, zone.coordinates, zone.zone_type]);

  useEffect(
    () => () => {
      mesh?.geometry.dispose();
      const materials = Array.isArray(mesh?.material) ? mesh.material : [mesh?.material];
      materials.forEach((material) => material?.dispose());
    },
    [mesh],
  );

  if (!mesh) return null;

  return (
    <EastNorthUpFrame
      lat={centroid[1] * DEG_TO_RAD}
      lon={centroid[0] * DEG_TO_RAD}
      height={anchorHeight}
    >
      <primitive object={mesh} />
    </EastNorthUpFrame>
  );
}

export function GlobeTileMaskLayer({ zones, terrainHeight }: GlobeTileMaskLayerProps) {
  const spatialMask = useMemo(() => {
    const siteBoundary = zones.find((zone) => zone.zone_type === 'site_boundary');
    return createTileSpatialMaskSetConfig(
      siteBoundary ? [siteBoundary] : zones,
      terrainHeight,
    );
  }, [terrainHeight, zones]);

  // These footprints are clipped in true world coordinates by
  // TileStencilPatcher. Mounting the old projected stencil volumes as well
  // would reintroduce pale camera-facing wedges around authored buildings.
  if (spatialMask) return null;
  return (
    <>
      {zones.map((zone) => (
        <TileMaskVolume key={zone.id} zone={zone} terrainHeight={terrainHeight} />
      ))}
    </>
  );
}
