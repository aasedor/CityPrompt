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

function publicRealmZone(
  name: string,
  kind: 'park' | 'street',
  archetypeId: string,
  variantId: string,
): SiteZone {
  return {
    id: `zone-${name}`,
    name,
    zone_type: kind === 'park' ? 'green_space' : 'road',
    properties: kind === 'park'
      ? {
          green_space_archetype_id: archetypeId,
          green_space_selected_variant_id: variantId,
          public_realm_lego: {
            target: { width_m: 79.85, depth_m: 8.716, area_m2: 695.94 },
          },
        }
      : {
          road_archetype_id: archetypeId,
          road_selected_variant_id: variantId,
          public_realm_lego: {
            target: { row_width_m: 4, length_m: 69.869 },
          },
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

  it('binds a building to the exact selected variant instead of the parent hero', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const candidate = zone('Nordic Block', 'scandinavian_urban_residential');
    candidate.properties = {
      ...candidate.properties,
      development_selected_variant_id: 'scandi_urban_dark_brick',
    };
    const references = await collectDirect3DArchetypeReferences([candidate]);

    expect(references).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith(
      '/archetypes/buildings/scandinavian_urban_residential/variant_1.png',
    );
    expect(references[0].label).toContain('Dark Brick Functionalist');
    expect(references[0].label).toContain('overrides generic material examples');
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

  it('attaches exact park and street appearances with size-aware fit rules', async () => {
    const fetchMock = vi.fn(async () => imageResponse());
    vi.stubGlobal('fetch', fetchMock);

    const references = await collectDirect3DArchetypeReferences([
      publicRealmZone('Courtyard Rain Garden', 'park', 'urban_pocket_park', 'urban_pocket_park_v2'),
      publicRealmZone('Green Spine', 'street', 'multi_use_trail', 'multi_use_trail_v1'),
    ]);

    expect(references).toHaveLength(2);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/archetypes/openspaces/urban-pocket-park/variant_2.png',
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/archetypes/streets/multi-use-trail/variant_1.png',
    );
    expect(references[0].label).toContain('Natural Meadow');
    expect(references[0].label).toContain('79.8 by 8.7 metre polygon');
    expect(references[0].label).toContain('one complete facility or one landscape room');
    expect(references[1].label).toContain('Green Corridor');
    expect(references[1].label).toContain('Keep the compiled cross-section exact');
    expect(references.every((reference) => reference.label.length <= 600)).toBe(true);
  });
});
