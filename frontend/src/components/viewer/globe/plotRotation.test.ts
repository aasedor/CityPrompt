import { expect, it } from 'vitest';
import { rectangleAt, rectangleDimensions } from '@/features/pickPlace/geometry';
import { assemblyFootprintCoordinates } from '@/features/legoAssembly/detachedPlot';
import { rotateCoordsAroundCentroid } from './plotRotation';

it.each([0, 51, 65])('keeps a fixed building rectangular when keyboard-rotated at latitude %s', latitude => {
  const center: [number, number] = [-114, latitude];
  const original = rectangleAt(center, 101.8, 31.3);
  let rotated = original;
  for (let step = 0; step < 72; step++) {
    rotated = rotateCoordsAroundCentroid(rotated, center, 5 * Math.PI / 180);
    const dimensions = rectangleDimensions(rotated);
    expect(dimensions.width).toBeCloseTo(101.8, 5);
    expect(dimensions.depth).toBeCloseTo(31.3, 5);
    const local = assemblyFootprintCoordinates(rotated, { width_m: 101.8, depth_m: 31.3 }, true)!;
    // The complete native envelope must still fit after every turn.
    expect(local[0][0]).toBeCloseTo(-50.9, 5);
    expect(local[0][1]).toBeCloseTo(15.65, 5);
  }
  rotated.forEach((point, i) => point.forEach((value, axis) => expect(value).toBeCloseTo(original[i][axis], 9)));
});

