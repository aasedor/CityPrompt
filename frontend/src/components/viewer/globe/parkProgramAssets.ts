/**
 * Exact live-3D placements derived from authoritative park ground guides.
 *
 * Unlike the generic park scatter, these objects are part of a regulation
 * program. Their positions therefore come from the same fitted metric guide
 * used to paint the drape, so a court can rotate or move without its standing
 * equipment drifting away from the linework.
 */

import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { ParkPropId, PropPlacement } from './parkScatter';
import {
  fitParkGroundGuides,
  resolveParkGroundProfile,
} from './parkGroundProfiles';
import { PARK_DRAPE_SURFACE_LIFT_METERS } from './parkSurfaceContract';

type ParkProgramZone = Pick<SiteZone, 'coordinates' | 'properties'>
  & Partial<Pick<SiteZone, 'zone_type'>>;

interface ProgramFrame {
  centroid: { lng: number; lat: number };
  minX: number;
  maxY: number;
  width: number;
  height: number;
  metersPerLongitudeDegree: number;
  normalizedRing: Array<[number, number]>;
}

function buildProgramFrame(coordinates: number[][]): ProgramFrame | null {
  if (coordinates.length < 3) return null;
  let lng = 0;
  let lat = 0;
  for (const coordinate of coordinates) {
    lng += coordinate[0];
    lat += coordinate[1];
  }
  lng /= coordinates.length;
  lat /= coordinates.length;
  const metersPerLongitudeDegree = metersPerDegLon(lat);
  const points = coordinates.map(([pointLng, pointLat]) => ({
    x: (pointLng - lng) * metersPerLongitudeDegree,
    y: (pointLat - lat) * METERS_PER_DEG_LAT,
  }));
  const minX = Math.min(...points.map((point) => point.x));
  const maxX = Math.max(...points.map((point) => point.x));
  const minY = Math.min(...points.map((point) => point.y));
  const maxY = Math.max(...points.map((point) => point.y));
  const width = maxX - minX;
  const height = maxY - minY;
  if (!(width > 0) || !(height > 0)) return null;
  return {
    centroid: { lng, lat },
    minX,
    maxY,
    width,
    height,
    metersPerLongitudeDegree,
    normalizedRing: points.map((point) => ([
      (point.x - minX) / width,
      (maxY - point.y) / height,
    ])),
  };
}

function basketballPlacements(
  frame: ProgramFrame,
  center: { x: number; y: number },
  rotationZ: number,
): PropPlacement[] {
  const placements: PropPlacement[] = [];
  const add = (
    propId: ParkPropId,
    offsetX: number,
    offsetY: number,
    yawOffset: number,
  ) => {
    const cos = Math.cos(rotationZ);
    const sin = Math.sin(rotationZ);
    const x = center.x + offsetX * cos - offsetY * sin;
    const y = center.y + offsetX * sin + offsetY * cos;
    placements.push({
      propId,
      lng: frame.centroid.lng + x / frame.metersPerLongitudeDegree,
      lat: frame.centroid.lat + y / METERS_PER_DEG_LAT,
      yawRad: rotationZ + yawOffset,
      scale: 1,
      surfaceOffsetM: PARK_DRAPE_SURFACE_LIFT_METERS,
    });
  };

  // The 28 x 15 m playing court is centered in the authored 32 x 19 m
  // run-off envelope. Pole origins sit beyond the baselines; each arm points
  // inward toward its rim and the playing surface.
  add('basketball_hoop', -15.2, 0, 0);
  add('basketball_hoop', 15.2, 0, Math.PI);

  // Two exact 32 m sides: eight reusable four-metre panels per side.
  for (const offsetY of [-9.5, 9.5]) {
    for (const offsetX of [-14, -10, -6, -2, 2, 6, 10, 14]) {
      add('chainlink_fence_4m', offsetX, offsetY, 0);
    }
  }
  // Two exact 19 m ends: 4 + 4 + 3 m gate + 4 + 4.
  const endSegments: Array<{ offsetY: number; propId: ParkPropId }> = [
    { offsetY: -7.5, propId: 'chainlink_fence_4m' },
    { offsetY: -3.5, propId: 'chainlink_fence_4m' },
    { offsetY: 0, propId: 'chainlink_gate_3m' },
    { offsetY: 3.5, propId: 'chainlink_fence_4m' },
    { offsetY: 7.5, propId: 'chainlink_fence_4m' },
  ];
  for (const offsetX of [-16, 16]) {
    for (const segment of endSegments) {
      add(segment.propId, offsetX, segment.offsetY, Math.PI / 2);
    }
  }

  // Integrated corner standards remain inside the complete fitted envelope.
  for (const [offsetX, offsetY] of [
    [-15.5, -9.0],
    [-15.5, 9.0],
    [15.5, -9.0],
    [15.5, 9.0],
  ] as const) {
    add(
      'basketball_floodlight',
      offsetX,
      offsetY,
      Math.atan2(-offsetY, -offsetX),
    );
  }
  return placements;
}

export function computeParkProgramAssetPlacements(zone: ParkProgramZone): PropPlacement[] {
  const profile = resolveParkGroundProfile(zone);
  if (!profile.archetypeId.startsWith('basketball_court')) return [];
  const frame = buildProgramFrame(zone.coordinates);
  if (!frame) return [];
  const fitted = fitParkGroundGuides(
    profile.guides,
    { width: frame.width, height: frame.height },
    frame.normalizedRing,
  ).guides;
  const court = fitted.find((guide) => guide.kind === 'rectangle');
  if (!court) return [];
  const center = {
    x: frame.minX + frame.width * court.x,
    y: frame.maxY - frame.height * court.y,
  };
  return basketballPlacements(
    frame,
    center,
    -((court.rotationDeg ?? 0) * Math.PI) / 180,
  );
}
