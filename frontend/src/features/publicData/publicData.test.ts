import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchPublicLayer, publicDataBounds, PUBLIC_DATA_LIMITS } from './publicData';

const bounds: [number, number, number, number] = [-114.08, 51.04, -114.075, 51.045];
const point = { type: 'Point', coordinates: [-114.078, 51.042] };
const respond = (rows: unknown) => vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify(rows))));
afterEach(() => vi.unstubAllGlobals());

describe('optional public data requests', () => {
  it('requires a small Calgary area and buffers an ordinary site', () => {
    expect(publicDataBounds([]).problem).toMatch(/site|area/i);
    expect(publicDataBounds([[0, 0], [1, 0], [1, 1]]).problem).toMatch(/Calgary/);
    expect(publicDataBounds([[-114.2, 51], [-114, 51], [-114, 51.1]]).problem).toMatch(/smaller/);
    const result = publicDataBounds([[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041]]);
    expect(result.problem).toBeNull();
    expect(result.bounds![0]).toBeLessThan(-114.08);
  });

  it('requests only local, finite, curated permit data and keeps source facts', async () => {
    respond([{ point, permitnum: 'BP001', statuscurrent: 'Issued', applicantname: 'Private person', estprojectcost: '250000' }]);
    const layer = await fetchPublicLayer('building-permits', bounds, new AbortController().signal);
    const url = new URL(vi.mocked(fetch).mock.calls[0][0] as string);
    expect(url.origin).toBe('https://data.calgary.ca');
    expect(url.searchParams.get('$limit')).toBe(String(PUBLIC_DATA_LIMITS.rows + 1));
    expect(url.searchParams.get('$where')).toContain('intersects(point');
    expect(url.searchParams.get('$where')).toContain('applieddate');
    expect(url.searchParams.get('$select')).not.toContain('applicant');
    expect(layer.feature_collection.features[0].properties).toMatchObject({ name: 'BP001', 'Status': 'Issued', 'Estimated construction value (CAD)': '250000' });
    expect(JSON.stringify(layer)).not.toContain('Private person');
    expect(layer.description).toMatch(/completion/i);
    expect(layer.source_url).toContain('c2es-76ed');
  });

  it('clips polygons locally and preserves exact roll identifiers and dated values', async () => {
    const multipolygon = { type: 'MultiPolygon', coordinates: [[[[-114.2, 51], [-114, 51], [-114, 51.1], [-114.2, 51.1], [-114.2, 51]]]] };
    respond([{ multipolygon, roll_number: '00012', roll_year: '2025', assessed_value: '500000' },
      { multipolygon, roll_number: '00012', roll_year: '2024', assessed_value: '450000' },
      { multipolygon, roll_number: '12', roll_year: '2025', assessed_value: '200000' }]);
    const layer = await fetchPublicLayer('assessments', bounds, new AbortController().signal);
    expect(layer.feature_count).toBe(2);
    expect(layer.feature_collection.features[0].properties).toMatchObject({ 'Roll number': '00012', 'Assessment history (CAD)': '2025: 500000; 2024: 450000' });
    const coordinates = JSON.stringify(layer.feature_collection.features[0].geometry);
    expect(coordinates).not.toContain('-114.2');
    expect(coordinates).toContain('-114.08');
  });

  it('marks truncated, invalid and empty results without claiming complete coverage', async () => {
    respond(Array.from({ length: PUBLIC_DATA_LIMITS.rows + 1 }, (_, i) => ({ point, name: `School ${i}` })));
    const limited = await fetchPublicLayer('schools', bounds, new AbortController().signal);
    expect(limited.feature_count).toBeLessThanOrEqual(PUBLIC_DATA_LIMITS.rows);
    expect(limited.warnings.join(' ')).toMatch(/partial/i);
    expect(limited.warnings.join(' ')).not.toMatch(/zoom/i);
    respond([{ point: { type: 'Point', coordinates: [Infinity, 51] }, name: 'Broken' }]);
    const invalid = await fetchPublicLayer('schools', bounds, new AbortController().signal);
    expect(invalid.feature_count).toBe(0);
    expect(invalid.warnings.join(' ')).toMatch(/skipped/i);
    respond([]);
    const empty = await fetchPublicLayer('schools', bounds, new AbortController().signal);
    expect(empty.warnings.join(' ')).toMatch(/No .*published|No .*found/i);
  });

  it('rejects oversized and unexpected responses, and invalid caller bounds before traffic', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('x', { headers: { 'content-length': String(PUBLIC_DATA_LIMITS.bytes + 1) } })));
    await expect(fetchPublicLayer('schools', bounds, new AbortController().signal)).rejects.toThrow(/large|smaller/i);
    respond({ error: 'not rows' });
    await expect(fetchPublicLayer('schools', bounds, new AbortController().signal)).rejects.toThrow(/unexpected/i);
    vi.mocked(fetch).mockClear();
    await expect(fetchPublicLayer('schools', [-120, 0, 120, 80], new AbortController().signal)).rejects.toThrow();
    expect(fetch).not.toHaveBeenCalled();
  });

  it('budgets the renderer’s ten-metre line subdivisions, not just source coordinates', async () => {
    const longLine = Array.from({ length: 200 }, (_, i) => [i % 2 ? -114.0751 : -114.0799, 51.042]);
    respond([{ multilinestring: { type: 'MultiLineString', coordinates: [longLine] }, globalid: 'huge' },
      { multilinestring: { type: 'MultiLineString', coordinates: [[[-114.079, 51.042], [-114.0789, 51.042]]] }, globalid: 'small' }]);
    const layer = await fetchPublicLayer('water-mains', bounds, new AbortController().signal);
    expect(layer.feature_count).toBe(1);
    expect(layer.feature_collection.features[0].properties.name).toBe('small');
    expect(layer.warnings.join(' ')).toMatch(/budget/);
  });

  it('limits concurrent requests and cancels queued work before it reaches the network', async () => {
    const releases: (() => void)[] = [];
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>(resolve => releases.push(() => resolve(new Response('[]'))))));
    const controllers = [new AbortController(), new AbortController(), new AbortController()];
    const jobs = controllers.map(c => fetchPublicLayer('schools', bounds, c.signal));
    const outcome = Promise.allSettled(jobs);
    await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    controllers[2].abort();
    releases.forEach(release => release());
    const results = await outcome;
    expect(results[2].status).toBe('rejected');
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
