import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { fetchParcelZoning, labelParcels, normalizeParcels, parcelAnchor, parcelCoverageProblem, PARCEL_LIMIT } from './parcelZoning';

import { fetchParcelFabric } from './calgaryParcelFabric';
vi.mock('./calgaryParcelFabric', async original => ({ ...await original<object>(), fetchParcelFabric: vi.fn() }));
beforeEach(() => vi.mocked(fetchParcelFabric).mockResolvedValue(rectangle().map(p => [p])));

const rectangle = (w = -114.12, s = 51.01, e = -114.119, n = 51.011): [number, number][][][] => [[[[w, s], [e, s], [e, n], [w, n], [w, s]]]];
const row = { cpid: 'one', multipolygon: { type: 'MultiPolygon', coordinates: rectangle() }, land_use_designation: 'OLD', roll_year: '2026' };
const bounds: [number, number, number, number] = [-114.12, 51.01, -114.119, 51.011];
afterEach(() => vi.unstubAllGlobals());

describe('parcel geometry and published zoning', () => {
  it('rejects malformed geometry and deduplicates assessment rows without changing inputs', () => {
    const original = JSON.stringify(row);
    const parcels = normalizeParcels([null, {}, { multipolygon: { type: 'MultiPolygon', coordinates: [null] } }, row, row]);
    expect(parcels).toHaveLength(1);
    expect(JSON.stringify(row)).toBe(original);
  });
  it('places labels inside concave parcels and outside courtyard holes', () => {
    const polygon: [number, number][][] = [[[0, 0], [8, 0], [8, 8], [5, 8], [5, 3], [0, 3], [0, 0]], [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]];
    const anchor = parcelAnchor(polygon)!;
    expect(booleanPointInPolygon(anchor, { type: 'Polygon', coordinates: polygon })).toBe(true);
  });
  it('uses land-use polygons instead of old assessment codes and preserves split zoning', async () => {
    const parcels = normalizeParcels([row]);
    const districts = [
      { label: 'R-CG', multipolygon: { type: 'MultiPolygon', coordinates: rectangle(-114.12, 51.01, -114.1195, 51.011) } },
      { label: 'M-CG d72', multipolygon: { type: 'MultiPolygon', coordinates: rectangle(-114.1195, 51.01, -114.119, 51.011) } },
      { label: 'NEIGHBOUR', multipolygon: { type: 'MultiPolygon', coordinates: rectangle(-114.119, 51.01, -114.118, 51.011) } },
    ];
    expect((await labelParcels(parcels, districts))[0].label).toBe('M-CG d72 / R-CG');
    expect(parcels[0].label).toBe('OLD');
  });
  it('keeps unknown designations explicit and respects cancellation', async () => {
    expect((await labelParcels(normalizeParcels([row]), []))[0].label).toBe('Unknown');
    const controller = new AbortController(); controller.abort();
    await expect(labelParcels(normalizeParcels([row]), [], controller.signal)).rejects.toThrow();
  });
  it('requires a bounded Calgary site', () => {
    expect(parcelCoverageProblem(null)).toMatch(/Draw/);
    expect(parcelCoverageProblem([-123.2, 49.1, -123.1, 49.2])).toMatch(/Calgary/);
    expect(parcelCoverageProblem([-114.3, 50.9, -114, 51.1])).toMatch(/smaller/);
    expect(parcelCoverageProblem(bounds)).toBeNull();
  });
  it('fetches only intersecting parcels and joins a bounded zoning query', async () => {
    const fetch = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => [{ label: 'R-CG', multipolygon: row.multipolygon }] });
    vi.stubGlobal('fetch', fetch);
    const result = await fetchParcelZoning(bounds, new AbortController().signal);
    expect(result.parcels[0].label).toBe('R-CG');
    expect(fetch).toHaveBeenCalledOnce();
    expect(fetchParcelFabric).toHaveBeenCalledWith(bounds, expect.any(AbortSignal));
    for (const [url, options] of fetch.mock.calls) {
      expect(new URL(url).searchParams.get('$where')).toContain('intersects(multipolygon');
      expect(new URL(url).searchParams.get('$limit')).toBe('1501');
      expect(options.signal).toBeInstanceOf(AbortSignal);
    }
  });
  it('rejects truncation, network errors and invalid response shapes instead of showing partial coverage', async () => {
    const fetch = vi.fn(); vi.stubGlobal('fetch', fetch);
    fetch.mockResolvedValueOnce({ ok: true, json: async () => Array(PARCEL_LIMIT + 1).fill(row) });
    await expect(fetchParcelZoning(bounds, new AbortController().signal)).rejects.toThrow(/too many/);
    fetch.mockResolvedValueOnce({ ok: false });
    await expect(fetchParcelZoning(bounds, new AbortController().signal)).rejects.toThrow(/could not load/);
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ error: true }) });
    await expect(fetchParcelZoning(bounds, new AbortController().signal)).rejects.toThrow(/unexpected/);
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    await expect(fetchParcelZoning(bounds, new AbortController().signal)).rejects.toThrow(/city limits/);
  });
});
