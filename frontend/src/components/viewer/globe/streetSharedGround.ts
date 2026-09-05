import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { LocalPt, StreetStationTerrain } from './streetMesh3D';
import { drapeSharedGroundGeometry, type SharedGroundTriangulation } from './sharedGroundGeometry';
import type { StreetFamilyFixturePlacements, StreetFixturePose } from './streetFamilyFurniture';

export type StreetGroundOffset = (x: number, y: number) => number | null;

export function createStreetGroundOffset(
  longitude: number, latitude: number, frameElevation: number,
  heightAt: (longitude: number, latitude: number) => number | null,
): StreetGroundOffset {
  const east = metersPerDegLon(latitude);
  return (x, y) => {
    const height = heightAt(longitude + x / east, latitude + y / METERS_PER_DEG_LAT);
    return height !== null && Number.isFinite(height) ? height - frameElevation : null;
  };
}

/** Flat authored Z values are construction lifts. Add the SAME site's sampled
 * height to every vertex; never fit another plane or move an unavailable mesh. */
export function applySharedStreetGround(
  geometry: THREE.BufferGeometry, offsetAt: StreetGroundOffset, originX = 0, originY = 0,
  grid?: SharedGroundTriangulation,
): boolean {
  const localGrid = grid ? { ...grid, westX: grid.westX - originX, southY: grid.southY - originY } : undefined;
  const draped = drapeSharedGroundGeometry(geometry, (x, y) => offsetAt(x + originX, y + originY), 4, 60000, localGrid);
  if (!draped) return false;
  geometry.copy(draped);
  draped.dispose();
  return true;
}

export function sharedStreetStationTerrain(
  points: LocalPt[], normals: LocalPt[], halfWidthM: number, offsetAt: StreetGroundOffset,
): StreetStationTerrain[] | null {
  const result: StreetStationTerrain[] = [];
  for (const [i, point] of points.entries()) {
    const normal = normals[i];
    const centerZ = offsetAt(point.x, point.y);
    const leftZ = offsetAt(point.x + normal.x * halfWidthM, point.y + normal.y * halfWidthM);
    const rightZ = offsetAt(point.x - normal.x * halfWidthM, point.y - normal.y * halfWidthM);
    if (centerZ === null || leftZ === null || rightZ === null) return null;
    result.push({ centerZ, leftZ, rightZ, halfWidthM });
  }
  return result;
}

/** Seat a rigid fixture at its own point; its dimensions/rotation stay intact. */
export function seatStreetFixture<T extends { x: number; y: number; z: number }>(pose: T, offsetAt: StreetGroundOffset): T | null {
  const height = offsetAt(pose.x, pose.y);
  return height === null ? null : { ...pose, z: pose.z + height };
}

/** Only placement collections are movable. Preserve stationCount and any
 * future metadata rather than assuming every property is an array of poses. */
export function seatStreetFamilyFixtures(fixtures: StreetFamilyFixturePlacements, offsetAt: StreetGroundOffset): StreetFamilyFixturePlacements {
  const seat = <T extends StreetFixturePose>(poses: T[]): T[] => poses.flatMap((pose) => {
    const seated = seatStreetFixture(pose, offsetAt);
    return seated ? [seated] : [];
  });
  return { ...fixtures,
    trees: seat(fixtures.trees), benches: seat(fixtures.benches), lights: seat(fixtures.lights),
    drains: seat(fixtures.drains), sidewalkJoints: seat(fixtures.sidewalkJoints), wasteBins: seat(fixtures.wasteBins),
    bikeRacks: seat(fixtures.bikeRacks), bollards: seat(fixtures.bollards), plantingCells: seat(fixtures.plantingCells),
    parkedVehicles: seat(fixtures.parkedVehicles), transitShelters: seat(fixtures.transitShelters),
  };
}
