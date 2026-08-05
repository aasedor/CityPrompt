/**
 * Exact reusable equipment placements derived from fitted metric park guides.
 *
 * These are not generic scatter objects: a regulation hoop must remain tied
 * to the court baseline when the court rotates, shifts, or is omitted because
 * the parcel is too small.
 */

import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { ParkPropId, PropPlacement } from './parkScatter';
import {
  fitParkGroundGuides,
  resolveParkGroundProfile,
} from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

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

function cleanCoordinates(coordinates: number[][]): number[][] {
  if (coordinates.length < 2) return coordinates;
  const first = coordinates[0];
  const last = coordinates[coordinates.length - 1];
  return first[0] === last[0] && first[1] === last[1]
    ? coordinates.slice(0, -1)
    : coordinates;
}

function buildProgramFrame(rawCoordinates: number[][]): ProgramFrame | null {
  const coordinates = cleanCoordinates(rawCoordinates);
  if (coordinates.length < 3) return null;
  const centroid = coordinates.reduce(
    (result, coordinate) => ({ lng: result.lng + coordinate[0], lat: result.lat + coordinate[1] }),
    { lng: 0, lat: 0 },
  );
  centroid.lng /= coordinates.length;
  centroid.lat /= coordinates.length;
  const metersPerLongitudeDegree = metersPerDegLon(centroid.lat);
  const points = coordinates.map(([lng, lat]) => ({
    x: (lng - centroid.lng) * metersPerLongitudeDegree,
    y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
  }));
  const minX = Math.min(...points.map(({ x }) => x));
  const maxX = Math.max(...points.map(({ x }) => x));
  const minY = Math.min(...points.map(({ y }) => y));
  const maxY = Math.max(...points.map(({ y }) => y));
  const width = maxX - minX;
  const height = maxY - minY;
  if (!(width > 0) || !(height > 0)) return null;
  return {
    centroid,
    minX,
    maxY,
    width,
    height,
    metersPerLongitudeDegree,
    normalizedRing: points.map(({ x, y }) => [
      (x - minX) / width,
      (maxY - y) / height,
    ]),
  };
}

function localPlacement(
  frame: ProgramFrame,
  propId: ParkPropId,
  center: { x: number; y: number },
  rotationZ: number,
  offsetX: number,
  offsetY: number,
  yawOffset: number,
): PropPlacement {
  const cos = Math.cos(rotationZ);
  const sin = Math.sin(rotationZ);
  const x = center.x + offsetX * cos - offsetY * sin;
  const y = center.y + offsetX * sin + offsetY * cos;
  return {
    propId,
    lng: frame.centroid.lng + x / frame.metersPerLongitudeDegree,
    lat: frame.centroid.lat + y / METERS_PER_DEG_LAT,
    yawRad: rotationZ + yawOffset,
    scale: 1,
    surfaceOffsetM: PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS,
  };
}

export function computeParkProgramAssetPlacements(zone: ParkProgramZone): PropPlacement[] {
  const profile = resolveParkGroundProfile(zone);
  if (!profile.archetypeId.startsWith('basketball_court')) return [];
  const frame = buildProgramFrame(zone.coordinates);
  if (!frame) return [];
  const court = fitParkGroundGuides(
    profile.guides,
    { width: frame.width, height: frame.height },
    frame.normalizedRing,
  ).guides.find((guide) => guide.kind === 'basketball_court');
  if (!court) return [];
  const center = {
    x: frame.minX + frame.width * court.x,
    y: frame.maxY - frame.height * court.y,
  };
  const rotationZ = -((court.rotationDeg ?? 0) * Math.PI) / 180;
  // The court guide is a 32 x 19 m play-and-runoff envelope around a centered
  // 28 x 15 m playing rectangle. Pole bases sit 1.2 m beyond each baseline;
  // the authored support arm points inward from its metric post-base origin.
  return [
    localPlacement(frame, 'basketball_hoop_regulation', center, rotationZ, -15.2, 0, 0),
    localPlacement(frame, 'basketball_hoop_regulation', center, rotationZ, 15.2, 0, Math.PI),
  ];
}
