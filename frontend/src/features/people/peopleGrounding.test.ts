import { describe, expect, it } from 'vitest';
import { BufferGeometry, Float32BufferAttribute } from 'three';
import { registerSafetySurface } from '@/features/parks/safetySupport';
import { detailPlacementSupport } from '@/features/parks/safetyPlacement';

describe('authored people foot datum', () => {
  it('uses the actual level sidewalk and retains ordinary terrain fallback off a road', () => {
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new Float32BufferAttribute([-1,-1,.025, 1,-1,.025, 1,1,.025, -1,-1,.025, 1,1,.025, -1,1,.025], 3));
    const release = registerSafetySurface({ id: 'people-ground-test', lng: 0, lat: 0, height: 100, geometries: [geometry] });
    try {
      const result = detailPlacementSupport('people-pilot-commuter', { lng: 0, lat: 0, angle: 90 }, ['people-ground-test']);
      expect(result.ok).toBe(true);
      if (result.ok) expect(result.height).toBeCloseTo(100.025);
      expect(detailPlacementSupport('people-pilot-commuter', { lng: 1, lat: 1, angle: 0 }, ['people-ground-test'])).toEqual({ ok: true });
    } finally { release(); geometry.dispose(); }
  });
});
