import { describe, expect, it } from 'vitest';
import {
  LEGO_STACK_RENDER_BUDGET,
  partitionLegoStacksByDistance,
  selectDetailedLegoStacks,
} from './legoStackBudget';

describe('selectDetailedLegoStacks', () => {
  it('keeps every supported stack in the 96-building mixed QA project', () => {
    const entries = Array.from({ length: 96 }, (_, index) => `building-${index}`);

    expect(LEGO_STACK_RENDER_BUDGET).toBeGreaterThanOrEqual(entries.length);
    expect(selectDetailedLegoStacks(entries)).toEqual(entries);
  });

  it('retains deterministic ordering when the safety budget is exceeded', () => {
    const entries = Array.from({ length: 120 }, (_, index) => index);

    expect(selectDetailedLegoStacks(entries, 3)).toEqual([0, 1, 2]);
    expect(selectDetailedLegoStacks(entries, -1)).toEqual([]);
  });

  it('keeps every district stack in exactly one LOD tier and details the nearest', () => {
    const entries = [
      { id: 'a', distance: 90 },
      { id: 'b', distance: 10 },
      { id: 'c', distance: 40 },
      { id: 'd', distance: 10 },
    ];

    const selection = partitionLegoStacksByDistance(
      entries,
      (entry) => entry.distance * entry.distance,
      2,
    );

    // Equal-distance ties are stable, while each tier retains source order.
    expect(selection.detailed.map((entry) => entry.id)).toEqual(['b', 'd']);
    expect(selection.simplified.map((entry) => entry.id)).toEqual(['a', 'c']);
    expect(new Set([...selection.detailed, ...selection.simplified])).toEqual(new Set(entries));
  });
});
