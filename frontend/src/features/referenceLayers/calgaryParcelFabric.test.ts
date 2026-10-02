import { describe, expect, it } from 'vitest';
import type { MultiPolygon } from 'polygon-clipping';
import { fabricTiles, mergeParcelFragments, polygonArea } from './calgaryParcelFabric';

const rectangle = (w: number, s: number, e: number, n: number): MultiPolygon => [[[[w, s], [e, s], [e, n], [w, n], [w, s]]]];
describe('full parcel fabric', () => {
  it('rejoins buffered tile fragments without dissolving adjacent parcel boundaries', async () => {
    const parcels = await mergeParcelFragments([
      rectangle(0, 0, 1.2, 1), rectangle(0.8, 0, 2, 1), // one parcel split across tiles
      rectangle(2, 0, 3, 1), // a different adjoining lot
      rectangle(2, 0, 3, 1), // duplicate tile buffer
    ], [0, 0, 3, 1]);
    expect(parcels).toHaveLength(2);
    expect(parcels.map(polygonArea).sort()).toEqual([1, 2]);
  });
  it('keeps holes and clips display to the requested site extent', async () => {
    const park: MultiPolygon = [
      [[[-1, -1], [4, -1], [4, 4], [-1, 4], [-1, -1]], [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]],
    ];
    const parcels = await mergeParcelFragments([park], [0, 0, 3, 3]);
    expect(parcels).toHaveLength(1);
    expect(polygonArea(parcels[0])).toBe(8);
  });
  it('bounds map requests and respects cancellation', async () => {
    expect(fabricTiles([-114.1247, 51.0172, -114.121, 51.0211]).length).toBeLessThan(8);
    expect(() => fabricTiles([-115, 50, -113, 52])).toThrow(/smaller/);
    const controller = new AbortController(); controller.abort();
    await expect(mergeParcelFragments([rectangle(0, 0, 1, 1)], [0, 0, 1, 1], controller.signal)).rejects.toThrow();
  });
});
