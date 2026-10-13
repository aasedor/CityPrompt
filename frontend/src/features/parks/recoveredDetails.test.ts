import { describe, expect, it } from 'vitest';
import { DETAIL_CATALOGUE, searchDetails } from './detailCatalogue';

describe('recovered detail pilot', () => {
  it('offers the exact metric urn through the existing catalogue', () => {
    const urn = searchDetails('formal fluted urn')[0];
    expect(urn).toBeDefined();
    expect(urn.id).toBe('detail-recovered-botanical-garden-formal-fluted-urn-v1');
    expect(urn.dimensions[2]).toBeCloseTo(1.75008, 4);
    expect(urn.kind).toBe('object');
    expect(urn.offset).toHaveLength(3);
  });
  it('does not expose known seating holds or rejected vegetation', () => {
    expect(DETAIL_CATALOGUE.some(m => m.id.includes('corten-planter-bench-v1'))).toBe(false);
    expect(DETAIL_CATALOGUE.some(m => m.id.includes('urban-pocket-park-concrete-timber-seat'))).toBe(false);
    expect(DETAIL_CATALOGUE.some(m => m.id.includes('50_tree_white_spruce'))).toBe(false);
  });
});
