import type { Location, SiteZone } from '@/types';
import {
  benchContext,
  type BenchContext,
  type DetailBench,
} from './benchDetails';
import { rectangleAt } from '@/features/pickPlace/geometry';
import {
  metersPerDegLon,
  METERS_PER_DEG_LAT,
} from '@/components/viewer/mapEngine/geoUtils';

export interface ProjectBench {
  id: string;
  lng: number;
  lat: number;
  angle: number;
}
export interface ProjectDetails {
  version: 1;
  revision: number;
  benches: ProjectBench[];
  can_edit: boolean;
}

/** A viewport only: never persisted as a zone and never a placement boundary. */
export function projectBenchFrame(
  zones: SiteZone[],
  benches: ProjectBench[],
  location?: Location,
): SiteZone {
  const points = [
    ...zones.flatMap((z) => z.coordinates),
    ...benches.map((b) => [b.lng, b.lat]),
  ];
  if (!points.length)
    points.push([
      location?.longitude ?? -114.0719,
      location?.latitude ?? 51.0447,
    ]);
  const minLng = Math.min(...points.map((p) => p[0])),
    maxLng = Math.max(...points.map((p) => p[0]));
  const minLat = Math.min(...points.map((p) => p[1])),
    maxLat = Math.max(...points.map((p) => p[1]));
  const center: [number, number] = [
    (minLng + maxLng) / 2,
    (minLat + maxLat) / 2,
  ];
  return {
    id: 'detail-editor-viewport',
    project_id: '',
    name: 'Community details',
    zone_type: 'site_boundary',
    color: '#ddd',
    sort_order: 0,
    created_at: '',
    updated_at: '',
    coordinates: rectangleAt(
      center,
      Math.max(100, (maxLng - minLng) * metersPerDegLon(center[1]) + 40),
      Math.max(100, (maxLat - minLat) * METERS_PER_DEG_LAT + 40),
    ),
    properties: {},
  };
}
export const projectBenchContext = (frame: SiteZone) =>
  benchContext(frame, undefined, 'project');
export const readProjectBenches = (
  benches: ProjectBench[],
  context: BenchContext,
): DetailBench[] =>
  benches.map((b) => ({
    id: b.id,
    point: context.fromWorld([b.lng, b.lat]),
    yaw: (b.angle * Math.PI) / 180,
  }));
export const saveProjectBenches = (
  benches: DetailBench[],
  context: BenchContext,
): ProjectBench[] =>
  benches.map((b) => {
    const [lng, lat] = context.toWorld(b.point);
    return {
      id: b.id,
      lng: Number(lng.toFixed(10)),
      lat: Number(lat.toFixed(10)),
      angle: Number(
        (
          (Math.atan2(Math.sin(b.yaw), Math.cos(b.yaw)) * 180) /
          Math.PI
        ).toFixed(6),
      ),
    };
  });
