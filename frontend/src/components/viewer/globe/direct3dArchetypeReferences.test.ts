import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { collectDirect3DArchetypeReferences } from './direct3dArchetypeReferences';

function zone(name: string, archetypeId: string | null, zoneType = 'building'): SiteZone {
  return {
    id: `zone-${name}`,
    name,
    zone_type: zoneType,
    properties: archetypeId ? { development_archetype_id: archetypeId } : {},
  } as unknown as SiteZone;
}

function variantZone(name: string, archetypeId: string, selectedVariantId: string): SiteZone {
  return {
    ...zone(name, archetypeId),
    properties: {
      development_archetype_id: archetypeId,
      development_selected_variant_id: selectedVariantId,
    },
  } as unknown as SiteZone;
}

function imageResponse(type = 'image/jpeg') {
  return {
    ok: true,
    blob: async () => new Blob([new Uint8Array([1, 2, 3])], { type }),
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('collectDirect3DArchetypeReferences', () => {
  it('prefers the authored facade elevation sheet and binds it to the building name', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const references = await collectDirect3DArchetypeReferences([
      zone('Boulevard Block', 'parisian_midrise_block'),
      zone('Central Park', null, 'green_space'),
    ]);

    expect(references).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith('/families/parisian-midrise-block/elevation.jpg');
    expect(references[0].label).toContain('FACADE SOURCE');
    expect(references[0].label).toContain('"Boulevard Block"');
    expect(references[0].label).toContain('AUTHORED IDENTITY');
    expect(references[0].label.length).toBeLessThanOrEqual(600);
    expect(references[0].image_base64.length).toBeGreaterThan(0);
  });

  it('resolves planner card-variant suffixes to the base archetype', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const references = await collectDirect3DArchetypeReferences([
      zone('Tower', 'parisian_midrise_block_variant_2'),
    ]);

    expect(references).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith('/families/parisian-midrise-block/elevation.jpg');
  });

  it('prefers an authored Sticker for the separately selected catalogue variant', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const references = await collectDirect3DArchetypeReferences([
      variantZone(
        'Gothic Hall',
        'collegiate_gothic_education',
        'collegiate_gothic_perpendicular',
      ),
    ]);

    expect(references).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith('/families/collegiate-gothic-perpendicular/elevation.jpg');
    expect(references[0].label).toContain('Collegiate Gothic / Perpendicular Revival');
    expect(references[0].label).toContain('giant traceried windows');
  });

  it('keeps the parent Sticker fallback when a selected variant has none', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const references = await collectDirect3DArchetypeReferences([
      variantZone('Boulevard Block', 'parisian_midrise_block', 'unregistered_variant'),
    ]);

    expect(references).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith('/families/parisian-midrise-block/elevation.jpg');
  });

  it('skips non-image responses instead of poisoning the provider request', async () => {
    // Dev-server HTML fallback for every URL: no reference should survive.
    vi.stubGlobal('fetch', vi.fn(async () => imageResponse('text/html')));

    const references = await collectDirect3DArchetypeReferences([
      zone('Boulevard Block', 'parisian_midrise_block'),
    ]);

    expect(references).toHaveLength(0);
  });

  it('deduplicates repeated archetypes and names each styled building', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => imageResponse()));

    const references = await collectDirect3DArchetypeReferences([
      zone('Block A', 'parisian_midrise_block'),
      zone('Block B', 'parisian_midrise_block_variant_1'),
    ]);

    expect(references).toHaveLength(1);
    expect(references[0].label).toContain('"Block A"');
    expect(references[0].label).toContain('"Block B"');
  });
});
