import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import type { SiteZoneProperties } from '@/types';

type Programme = 'pocket-v1' | 'greenway-v1' | 'shade-courtyard-v1' | 'meadow-grove-v1';
const POCKET_PROGRAMMES = ['pocket-v1', 'shade-courtyard-v1', 'meadow-grove-v1'];

/** Mirrors the metric minimum-rotated-rectangle and area limits of the two
 * server capabilities, so an unsupported drawing is explained before save. */
export function flexibleParkFitProblem(coordinates: number[][], properties?: SiteZoneProperties): string | null {
  const programme = properties?.pick_place_flexible_park;
  if (!isFlexiblePark(properties)) return null;
  if (coordinates.length < 3 || coordinates.some(point => point.length < 2 || !point.slice(0, 2).every(Number.isFinite))) {
    return 'Draw at least three park corners to make a complete outline.';
  }
  const latitude = coordinates[0][1], east = metersPerDegLon(latitude);
  const points = coordinates.map(([longitude, lat]) => ({
    x: (longitude - coordinates[0][0]) * east, y: (lat - latitude) * METERS_PER_DEG_LAT,
  }));
  const area = Math.abs(points.reduce((sum, point, i) => {
    const next = points[(i + 1) % points.length];
    return sum + point.x * next.y - next.x * point.y;
  }, 0)) / 2;
  const frames = points.map((point, i) => {
    const next = points[(i + 1) % points.length], angle = Math.atan2(next.y - point.y, next.x - point.x);
    const c = Math.cos(angle), s = Math.sin(angle);
    const rotated = points.map(p => ({ x: p.x * c + p.y * s, y: p.y * c - p.x * s }));
    const width = Math.max(...rotated.map(p => p.x)) - Math.min(...rotated.map(p => p.x));
    const depth = Math.max(...rotated.map(p => p.y)) - Math.min(...rotated.map(p => p.y));
    return { long: Math.max(width, depth), short: Math.min(width, depth), boxArea: width * depth };
  });
  const frame = frames.reduce((best, current) => current.boxArea < best.boxArea ? current : best);
  const { long, short } = frame;
  if (POCKET_PROGRAMMES.includes(String(programme))) {
    if (short < 8.05 || long > 99.9 || area < 65 || area > 3590) {
      return 'The flexible pocket park needs an 8–100 m outline and 64–3,600 m² of land. Adjust the corners or choose another park.';
    }
  } else if (long < 60.1 || long > 999.9 || short < 12.05 || short > 59.9
    || area < 760 || area > 59_900 || long / Math.max(short, .001) < 3.02) {
    return 'The greenway needs a connected corridor at least 60 m long, 12–60 m wide and three times longer than wide. Adjust the outline or choose the pocket park.';
  }
  return null;
}

export function isFlexiblePark(properties?: SiteZoneProperties): properties is SiteZoneProperties & { pick_place_flexible_park: Programme } {
  return POCKET_PROGRAMMES.includes(String(properties?.pick_place_flexible_park)) || properties?.pick_place_flexible_park === 'greenway-v1';
}
