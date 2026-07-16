/**
 * Persistent stencil volumes for loaded replacement buildings.
 *
 * This layer intentionally lives outside the zone-overlay visibility group:
 * clean screenshots hide planning overlays, but the Google photogrammetry
 * beneath a mounted GLB/LEGO stack must remain clipped in every capture mode.
 */

import { useMemo } from 'react';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import {
  createStencilVolume,
  getTileStencilVolumeHeight,
  shouldCreateTileStencilMask,
} from './StencilMaskPlugin';
import {
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';

const DEG_TO_RAD = Math.PI / 180;

interface GlobeTileMaskLayerProps {
  zones: SiteZone[];
  terrainHeight: number;
}

function TileMaskVolume({ zone, terrainHeight }: { zone: SiteZone; terrainHeight: number }) {
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
  const anchorHeight = Number.isFinite(storedTerrain) ? storedTerrain : terrainHeight;

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
  return (
    <>
      {zones.map((zone) => (
        <TileMaskVolume key={zone.id} zone={zone} terrainHeight={terrainHeight} />
      ))}
    </>
  );
}
