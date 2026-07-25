import { describe, expect, it } from 'vitest';

import { PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';
import type { StreetParkedVehiclePlacement } from './streetFamilyFurniture';
import { buildStreetVehicleInstanceParts } from './GlobeStreetVehicleInstances';

function vehicle(
  vehicleType: 'sedan' | 'suv',
  x: number,
  yawRad = 0,
): StreetParkedVehiclePlacement {
  return {
    vehicleType,
    x,
    y: 2.5,
    z: 3,
    yawRad,
    stationIndex: 4,
    stationM: 16,
    tangentX: 1,
    tangentY: 0,
    normalX: 0,
    normalY: 1,
    offsetM: 2.5,
    lengthM: vehicleType === 'suv' ? 4.75 : 4.45,
    widthM: 1.28,
    heightM: vehicleType === 'suv' ? 1.72 : 1.48,
    bodyColor: vehicleType === 'suv' ? '#34506a' : '#6f2f2d',
    bandStartM: 1.8,
    bandEndM: 3.2,
  };
}

describe('street vehicle instance assembly', () => {
  it('builds deterministic low-draw-call sedan and SUV assemblies', () => {
    const placements = [vehicle('sedan', 10), vehicle('suv', 22)];
    const first = buildStreetVehicleInstanceParts(placements);
    expect(buildStreetVehicleInstanceParts(placements)).toEqual(first);
    expect(first.bodies).toHaveLength(2);
    expect(first.cabins).toHaveLength(2);
    expect(first.roofs).toHaveLength(2);
    expect(first.wheels).toHaveLength(8);
    expect(first.bodies.map((part) => part.color)).toEqual(['#6f2f2d', '#34506a']);
    expect(first.cabins.every((part) => part.color === '#26323a')).toBe(true);
    expect(first.wheels.every((part) => part.color === '#202427')).toBe(true);
  });

  it('keeps every vehicle part seated above the authored road datum', () => {
    const placement = vehicle('sedan', 10);
    const parts = buildStreetVehicleInstanceParts([placement]);
    const roadZ = placement.z + PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS;
    [...parts.bodies, ...parts.cabins, ...parts.roofs, ...parts.wheels]
      .forEach((part) => expect(part.z - part.scaleZ / 2).toBeGreaterThanOrEqual(roadZ - 1e-8));
  });

  it('gives the SUV a longer and taller glazed cabin than the sedan', () => {
    const parts = buildStreetVehicleInstanceParts([
      vehicle('sedan', 10),
      vehicle('suv', 22),
    ]);
    expect(parts.cabins[1].scaleX).toBeGreaterThan(parts.cabins[0].scaleX);
    expect(parts.cabins[1].scaleZ).toBeGreaterThan(parts.cabins[0].scaleZ);
    expect(parts.roofs[1].scaleX).toBeGreaterThan(parts.roofs[0].scaleX);
  });

  it('rotates wheel offsets with a parallel-parked vehicle heading', () => {
    const placement = vehicle('sedan', 10, Math.PI / 2);
    const { wheels } = buildStreetVehicleInstanceParts([placement]);
    expect(new Set(wheels.map((wheel) => wheel.x.toFixed(6))).size).toBe(2);
    expect(new Set(wheels.map((wheel) => wheel.y.toFixed(6))).size).toBe(2);
    expect(wheels.every((wheel) => wheel.yawRad === Math.PI / 2)).toBe(true);
  });
});
