import { describe, expect, it } from 'vitest';

import {
  GENERATED_BUILDING_DETAIL_BUDGET,
  desiredGeneratedBuildingLodLevel,
  partitionGeneratedBuildingLod,
  partitionGeneratedBuildingLodWithPins,
  resolveGeneratedBuildingLodUrl,
} from './generatedBuildingLod';

describe('partitionGeneratedBuildingLod', () => {
  it('keeps every generated building in exactly one 3D tier', () => {
    const entries = Array.from({ length: 53 }, (_, index) => ({ id: `building-${index}`, distance: 53 - index }));
    const selection = partitionGeneratedBuildingLod(entries, (entry) => entry.distance ** 2);

    expect(selection.detailed).toHaveLength(GENERATED_BUILDING_DETAIL_BUDGET);
    expect(selection.simplified).toHaveLength(53 - GENERATED_BUILDING_DETAIL_BUDGET);
    expect(new Set([...selection.detailed, ...selection.simplified].map((entry) => entry.id)).size).toBe(53);
    expect(selection.detailed.some((entry) => entry.id === 'building-52')).toBe(true);
    expect(selection.simplified.some((entry) => entry.id === 'building-0')).toBe(true);
  });

  it('uses source order as the deterministic distance tie-breaker', () => {
    const entries = ['a', 'b', 'c', 'd'];
    const selection = partitionGeneratedBuildingLod(entries, () => 25, 2);

    expect(selection.detailed).toEqual(['a', 'b']);
    expect(selection.simplified).toEqual(['c', 'd']);
  });
});

describe('generated building asset LOD', () => {
  it('selects distance-aware levels and pins captures to the source LOD', () => {
    const urls = { '0': 'source.glb', '1': 'near.glb', '2': 'mid.glb', '3': 'far.glb' };
    expect(desiredGeneratedBuildingLodLevel(100)).toBe('0');
    expect(desiredGeneratedBuildingLodLevel(500)).toBe('1');
    expect(desiredGeneratedBuildingLodLevel(1_000)).toBe('2');
    expect(desiredGeneratedBuildingLodLevel(2_000)).toBe('3');
    expect(resolveGeneratedBuildingLodUrl(urls, null, 2_000, true)).toEqual({
      level: '0',
      url: 'source.glb',
    });
  });

  it('keeps every capture-pinned building detailed beyond the navigation budget', () => {
    const entries = Array.from({ length: 25 }, (_, index) => ({ id: index, distance: index }));
    const selection = partitionGeneratedBuildingLodWithPins(
      entries,
      (entry) => entry.distance ** 2,
      (entry) => entry.id >= 20,
      3,
    );
    expect(selection.detailed.map((entry) => entry.id)).toEqual([20, 21, 22, 23, 24]);
    expect(selection.simplified).toHaveLength(20);
  });

  it('falls back to the nearest available authored LOD', () => {
    expect(resolveGeneratedBuildingLodUrl({ '0': 'source.glb', '2': 'mid.glb' }, null, 500)).toEqual({
      level: '2',
      url: 'mid.glb',
    });
  });
});
