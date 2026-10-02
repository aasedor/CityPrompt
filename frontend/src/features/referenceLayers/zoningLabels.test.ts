import { afterEach, describe, expect, it, vi } from 'vitest';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { districtLabels, fetchZoningLabels, zoningAnchor, zoningCoverageProblem, ZONING_LIMIT } from './zoningLabels';

const site: [number, number][] = [[-114.12, 51.01], [-114.119, 51.01], [-114.119, 51.011], [-114.12, 51.011]];
const geometry = { type: 'MultiPolygon', coordinates: [[ [...site, site[0]] ]] };
afterEach(() => vi.unstubAllGlobals());

describe('district zoning labels without parcel data', () => {
  it('uses the published code and clips large districts to the site', async () => {
    const result = await districtLabels([{ label: 'R-CG', multipolygon: geometry }], site);
    expect(result).toHaveLength(1);
    expect(result[0].label).toBe('R-CG');
    expect(booleanPointInPolygon(result[0].anchor, { type: 'Polygon', coordinates: [[...site, site[0]]] })).toBe(true);
    expect(site).toHaveLength(4);
  });
  it('keeps labels inside concave areas and outside holes', () => {
    const polygon: [number, number][][] = [[[0, 0], [8, 0], [8, 8], [5, 8], [5, 3], [0, 3], [0, 0]], [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]];
    expect(booleanPointInPolygon(zoningAnchor(polygon)!, { type: 'Polygon', coordinates: polygon })).toBe(true);
  });
  it('labels every disjoint district piece and ignores areas outside the actual boundary', async () => {
    const district = { type: 'MultiPolygon', coordinates: [[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]], [[[2, 0], [3, 0], [3, 1], [2, 1], [2, 0]]]] };
    expect(await districtLabels([{ lu_code: 'S-SPR', multipolygon: district }], [[0, 0], [3, 0], [3, 2], [0, 2]])).toHaveLength(2);
    // This triangle's bounding box touches the second square, but its interior does not.
    expect(await districtLabels([{ lu_code: 'S-SPR', multipolygon: district }], [[0, 0], [3, 2], [0, 2]])).toHaveLength(1);
  });
  it('rejects bad geometry, missing codes and cancellation safely', async () => {
    await expect(districtLabels([{ label: 'R-CG', multipolygon: { type: 'MultiPolygon', coordinates: [null] } }], site)).rejects.toThrow(/geometry/);
    await expect(districtLabels([{ multipolygon: geometry }], site)).rejects.toThrow(/without a zoning code/);
    const controller = new AbortController(); controller.abort();
    await expect(districtLabels([{ label: 'R-CG', multipolygon: geometry }], site, controller.signal)).rejects.toThrow();
  });
  it('requires a bounded Calgary site', () => {
    expect(zoningCoverageProblem(null)).toMatch(/Draw/);
    expect(zoningCoverageProblem([-123.2, 49.1, -123.1, 49.2])).toMatch(/Calgary/);
    expect(zoningCoverageProblem([-114.3, 50.9, -114, 51.1])).toMatch(/smaller/);
  });
  it('makes one bounded zoning request with no parcel service calls', async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [{ label: 'R-CG', multipolygon: geometry }] });
    vi.stubGlobal('fetch', fetch);
    expect((await fetchZoningLabels(site, new AbortController().signal)).districts).toHaveLength(1);
    expect(fetch).toHaveBeenCalledOnce();
    const url = new URL(fetch.mock.calls[0][0]);
    expect(url.pathname).toBe('/resource/qe6k-p9nh.json');
    expect(url.searchParams.get('$where')).toContain('intersects(multipolygon');
    expect(url.searchParams.get('$limit')).toBe('1501');
  });
  it('rejects truncation, source failures and unavailable coverage', async () => {
    const fetch = vi.fn(); vi.stubGlobal('fetch', fetch);
    for (const [response, message] of [
      [{ ok: true, json: async () => Array(ZONING_LIMIT + 1).fill({}) }, /too many/],
      [{ ok: false }, /could not load/],
      [{ ok: true, json: async () => ({ error: true }) }, /unexpected/],
      [{ ok: true, json: async () => [] }, /city limits/],
    ] as const) {
      fetch.mockResolvedValueOnce(response);
      await expect(fetchZoningLabels(site, new AbortController().signal)).rejects.toThrow(message);
    }
  });
});
