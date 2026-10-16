import { afterEach, describe, expect, it, vi } from 'vitest';
import rows from './calgarySafetyCatalogue.json';

afterEach(() => { vi.unstubAllEnvs(); vi.resetModules(); });
describe('Calgary concept catalogue release', () => {
  it('exposes all ten reviewed stable variants with rigid source datums', async () => {
    vi.stubEnv('DEV', true); vi.stubEnv('VITE_CALGARY_SAFETY_PREVIEW', 'true'); vi.resetModules();
    const { DETAIL_CATALOGUE, detailAsset } = await import('./detailCatalogue');
    expect(new Set(rows.map(r => r.safety.family)).size).toBe(8);
    expect(rows).toHaveLength(10);
    for (const row of rows) {
      expect(detailAsset(row.id)?.url).toBe(row.url);
      expect(row.datumLift).toBe(0);
      expect(row.safety.transforms).toEqual(['translation', 'yaw']);
      expect(row.runtimeApproved).toBe(true);
    }
    expect(new Set(DETAIL_CATALOGUE.map(r => r.id)).size).toBe(DETAIL_CATALOGUE.length);
  });
  it.each([false, true])('includes reviewed variants in production independently of preview flags (flag %s)', async flag => {
    vi.stubEnv('DEV', false); vi.stubEnv('VITE_CALGARY_SAFETY_PREVIEW', String(flag)); vi.resetModules();
    const { DETAIL_CATALOGUE } = await import('./detailCatalogue');
    expect(rows.every(row=>DETAIL_CATALOGUE.some(r=>r.id===row.id))).toBe(true);
  });
});
