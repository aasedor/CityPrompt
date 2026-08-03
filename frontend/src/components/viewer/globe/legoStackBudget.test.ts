import { describe, expect, it } from 'vitest';
import {
  LEGO_DISTINCT_FAMILY_RENDER_BUDGET,
  LEGO_STACK_RENDER_BUDGET,
  partitionLegoStacksByDistance,
  partitionLegoStacksByDistanceAndFamily,
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

describe('partitionLegoStacksByDistanceAndFamily', () => {
  it('admits the nearest distinct families and keeps later stacks from admitted families detailed', () => {
    const entries = [
      { id: 'a-near', family: 'a', distance: 1 },
      { id: 'b-near', family: 'b', distance: 2 },
      { id: 'c-near', family: 'c', distance: 3 },
      { id: 'd-near', family: 'd', distance: 4 },
      { id: 'a-far', family: 'a', distance: 5 },
    ];

    const selection = partitionLegoStacksByDistanceAndFamily(
      entries,
      (entry) => entry.family,
      (entry) => entry.distance,
      96,
      3,
    );

    expect(LEGO_DISTINCT_FAMILY_RENDER_BUDGET).toBe(LEGO_STACK_RENDER_BUDGET);
    expect(selection.detailed.map((entry) => entry.id)).toEqual([
      'a-near',
      'b-near',
      'c-near',
      'a-far',
    ]);
    expect(selection.simplified.map((entry) => entry.id)).toEqual(['d-near']);
  });

  it('honors zero and explicit stack budgets', () => {
    const entries = [
      { family: 'a', distance: 1 },
      { family: 'a', distance: 2 },
      { family: 'b', distance: 3 },
    ];

    expect(partitionLegoStacksByDistanceAndFamily(
      entries,
      (entry) => entry.family,
      (entry) => entry.distance,
      2,
      2,
    ).detailed).toEqual(entries.slice(0, 2));
    expect(partitionLegoStacksByDistanceAndFamily(
      entries,
      (entry) => entry.family,
      (entry) => entry.distance,
      2,
      0,
    ).detailed).toEqual([]);
  });

  it('keeps every distinct family detailed under the default stack budget', () => {
    const entries = Array.from({ length: 12 }, (_value, index) => ({
      id: `building-${index}`,
      family: `family-${index}`,
      distance: index,
    }));

    const selection = partitionLegoStacksByDistanceAndFamily(
      entries,
      (entry) => entry.family,
      (entry) => entry.distance,
    );

    expect(selection.detailed).toEqual(entries);
    expect(selection.simplified).toEqual([]);
  });
});
