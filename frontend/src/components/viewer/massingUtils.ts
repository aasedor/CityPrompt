/**
 * massingUtils.ts
 *
 * Converts SiteMassingOption data into GeoJSON FeatureCollections
 * suitable for Mapbox GL fill-extrusion rendering.
 *
 * Building center_x / center_y are degree offsets from the zone centroid.
 * We reconstruct the rectangular footprint polygon using meter-to-degree math.
 */

import type { SiteMassingOption, SiteZone } from '@/types';
import type { FeatureCollection, Feature, Polygon } from 'geojson';

const METERS_PER_DEG_LAT = 111320;

function metersPerDegLon(lat: number): number {
  return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180);
}

/** Zone type → default color for massing blocks */
const ZONE_COLORS: Record<string, string> = {
  building: '#9b59b6',
  residential: '#e91e8a',
  commercial: '#3498db',
  mixed_use: '#e67e22',
  development_area: '#8e44ad',
  green_space: '#27ae60',
  parking: '#95a5a6',
  road: '#444444',
};

function zoneColor(zoneType: string): string {
  return ZONE_COLORS[zoneType] ?? '#9b59b6';
}

/**
 * Build a rectangular polygon (GeoJSON coords) for a building footprint.
 * center is [lng, lat] in absolute coordinates.
 */
function buildingFootprintCoords(
  centerLng: number,
  centerLat: number,
  widthM: number,
  depthM: number,
  rotationDeg: number,
): number[][] {
  const mPerDegLon = metersPerDegLon(centerLat);
  const hw = widthM / 2; // half-width in meters
  const hd = depthM / 2; // half-depth in meters
  const rad = (rotationDeg * Math.PI) / 180;
  const cosR = Math.cos(rad);
  const sinR = Math.sin(rad);

  // 4 corners in local meters, then rotate
  const corners = [
    [-hw, -hd],
    [hw, -hd],
    [hw, hd],
    [-hw, hd],
  ];

  const coords = corners.map(([x, y]) => {
    const rx = x * cosR - y * sinR;
    const ry = x * sinR + y * cosR;
    return [
      centerLng + rx / mPerDegLon,
      centerLat + ry / METERS_PER_DEG_LAT,
    ];
  });

  // Close the ring
  coords.push([...coords[0]]);
  return coords;
}

/**
 * Convert a SiteMassingOption into a GeoJSON FeatureCollection of
 * extruded building polygons and flat green space polygons.
 *
 * @param option  One of the 3 massing options from the API
 * @param zones   The project's SiteZone array (for centroid lookup)
 */
export function massingOptionToGeoJSON(
  option: SiteMassingOption,
  zones: SiteZone[],
): FeatureCollection {
  const features: Feature<Polygon>[] = [];

  // Build a centroid lookup by zone id
  const zoneCentroidMap = new Map<string, [number, number]>();
  for (const z of zones) {
    if (z.coordinates && z.coordinates.length >= 3) {
      const lngs = z.coordinates.map((c) => c[0]);
      const lats = z.coordinates.map((c) => c[1]);
      const cLng = lngs.reduce((a, b) => a + b, 0) / lngs.length;
      const cLat = lats.reduce((a, b) => a + b, 0) / lats.length;
      zoneCentroidMap.set(z.id, [cLng, cLat]);
    }
  }

  for (const mz of option.zones) {
    const centroid = zoneCentroidMap.get(mz.zone_id);
    if (!centroid) continue;
    const [cLng, cLat] = centroid;
    const color = zoneColor(mz.zone_type);

    // Buildings → extruded polygons
    for (const bldg of mz.buildings) {
      const absLng = cLng + bldg.center_x;
      const absLat = cLat + bldg.center_y;
      const height = bldg.height_m ?? 15;

      const coords = buildingFootprintCoords(
        absLng,
        absLat,
        bldg.width_m,
        bldg.depth_m,
        bldg.rotation_deg,
      );

      features.push({
        type: 'Feature',
        properties: {
          type: 'building',
          zone_id: mz.zone_id,
          zone_type: mz.zone_type,
          height,
          color,
          building_type: bldg.building_type,
        },
        geometry: {
          type: 'Polygon',
          coordinates: [coords],
        },
      });
    }

    // Green spaces → flat polygons (height = 0.5 so they show slightly)
    for (const gs of mz.green_spaces) {
      if (!gs.polygon || gs.polygon.length < 3) continue;

      // Convert offset coords to absolute
      const absCoords = gs.polygon.map(([dx, dy]) => [
        cLng + dx, // already in degrees offset from centroid
        cLat + dy,
      ]);
      // Close ring if needed
      if (
        absCoords[0][0] !== absCoords[absCoords.length - 1][0] ||
        absCoords[0][1] !== absCoords[absCoords.length - 1][1]
      ) {
        absCoords.push([...absCoords[0]]);
      }

      features.push({
        type: 'Feature',
        properties: {
          type: 'green_space',
          zone_id: mz.zone_id,
          zone_type: 'green_space',
          height: 0.5,
          color: '#27ae60',
          space_type: gs.space_type,
        },
        geometry: {
          type: 'Polygon',
          coordinates: [absCoords],
        },
      });
    }
  }

  return {
    type: 'FeatureCollection',
    features,
  };
}
