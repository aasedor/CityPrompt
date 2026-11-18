import { renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { useSiteLandscapeTexture } from './useSiteLandscapeTexture';

const boundary: SiteZone = {
  id: 'site', project_id: 'project', zone_type: 'site_boundary',
  coordinates: [[-114, 51], [-113.999, 51], [-113.999, 51.001], [-114, 51.001]],
  color: '#ef4444', sort_order: 0, created_at: '2026-11-18', updated_at: '2026-11-18',
};

describe('prepared site texture', () => {
  it('uses the saved custom colour and restores the original texture on reset', () => {
    const { result, rerender } = renderHook(
      ({ zone }) => useSiteLandscapeTexture(zone, null, true),
      { initialProps: { zone: boundary } },
    );
    const defaultTexture = result.current!;
    expect(defaultTexture.image.width).toBe(256);

    rerender({ zone: { ...boundary, properties: { site_boundary_surface: '#b89671' } } });
    const colourTexture = result.current!;
    expect(colourTexture.image.width).toBe(1);
    expect(colourTexture.image.data).toEqual(new Uint8Array([184, 150, 113, 255]));

    rerender({ zone: { ...boundary, properties: { site_boundary_surface: 'default' } } });
    expect(result.current?.image.data).toEqual(defaultTexture.image.data);
    defaultTexture.dispose();
    colourTexture.dispose();
    result.current?.dispose();
  });
});
