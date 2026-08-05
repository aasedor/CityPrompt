import { describe, expect, it } from 'vitest';

import {
  resolveParkBenchStyle,
  resolveParkTreeVariant,
} from './publicRealmPropPalettes';

describe('public-realm archetype-weighted prop palettes', () => {
  it('keeps deterministic tree identity while varying trees across placement seeds', () => {
    const first = resolveParkTreeVariant('english_pastoral', 'park-1:tree-4');
    expect(resolveParkTreeVariant('english_pastoral', 'park-1:tree-4')).toBe(first);
    const variants = new Set(Array.from({ length: 24 }, (_, index) => (
      resolveParkTreeVariant('english_pastoral', `park-1:tree-${index}`)
    )));
    expect(variants.size).toBeGreaterThan(1);
    expect([...variants].every((variant) => (
      ['mature_oak', 'maple', 'honey_locust'].includes(variant)
    ))).toBe(true);
    expect(variants.has('mature_oak')).toBe(true);
  });

  it('uses tropical palms and selects family-specific bench construction', () => {
    const tropicalTrees = new Set(Array.from({ length: 20 }, (_, index) => (
      resolveParkTreeVariant('tropical_lush', `tropical:${index}`)
    )));
    expect(tropicalTrees.has('tropical_palm')).toBe(true);
    expect(resolveParkBenchStyle('modern_minimal')).toBe('minimal_slab');
    expect(resolveParkBenchStyle('urban_pavers')).toBe('heritage_cast_iron');
    expect(resolveParkBenchStyle('native_meadow')).toBe('backless_timber');
  });
});
