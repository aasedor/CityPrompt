import { describe, expect, it } from 'vitest';
import { meadowPlantScale, selectMeadowTrees } from './meadowVegetationPlacement';

const boundary = [{ x: -10, y: -10 }, { x: 10, y: -10 }, { x: 10, y: 10 }, { x: -10, y: 10 }];
describe('meadow vegetation integration', () => {
  it('preserves authored transforms and cycles the three identities', () => {
    const p = [0, 1, 2].map(x => ({ x, y: 0, z: 2, yawRad: .7, scale: 1 }));
    const result = selectMeadowTrees(p, boundary);
    expect(result.map(x => x.kind)).toEqual(['shade_tree', 'grove_tree', 'ornamental_tree']);
    expect(result.map(x => x.placement)).toEqual(p);
  });
  it('uses a narrower crown near an edge without reducing native scale', () => {
    expect(selectMeadowTrees([{ x: 7, y: 0, scale: 1 }], boundary)[0].kind).toBe('grove_tree');
    expect(selectMeadowTrees([{ x: 9, y: 0, scale: 1 }], boundary)).toEqual([]);
  });
  it('rejects crown intersections with fixed programs and invalid scales', () => {
    expect(selectMeadowTrees([{ x: 0, y: 0, scale: 1 }], boundary, [{ x: 1, y: 0, radius: 3 }])).toEqual([]);
    expect(selectMeadowTrees([{ x: 0, y: 0, scale: NaN }], boundary)).toEqual([]);
  });
  it('keeps all plant prototypes within the original clump reserve', () => {
    expect(meadowPlantScale('meadow_grass', .65)).toBe(1);
    expect(meadowPlantScale('silver_shrub', .425)).toBe(.5);
    expect(meadowPlantScale('flowering_perennial', .325)).toBe(.5);
  });
});
