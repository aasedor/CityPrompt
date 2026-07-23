import { describe, expect, it } from 'vitest';

import {
  GENERATED_BUILDING_DETAIL_BUDGET,
  partitionGeneratedBuildingLod,
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
