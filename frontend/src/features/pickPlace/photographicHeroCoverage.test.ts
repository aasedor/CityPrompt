import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { pickerHeroImage } from './pickerHeroImages';
import publicRealm from '@/data/publicRealmRelease20261023.json';

describe('photographic presentation for previously technical picker cards', () => {
  const references = [
    ['halifax-public-gardens-park-only', '/archetypes/openspaces/halifax-public-gardens/variant_0.png'],
    ['ice-rink-market-square-park-only', '/archetypes/openspaces/outdoor-ice-rink/variant_0.png'],
    ['barcelona-passatge', '/archetypes/streets/barcelona-passatge-covered-passage/variant_0.png'],
    ['brick-arch-viaduct', '/archetypes/streets/rail-transit-viaduct/variant_0.png'],
    ['stone-arch-road-bridge-compact-r002', '/archetypes/streets/urban-vehicular-bridge/variant_0.png'],
  ];
  it.each(references)('shows the source photograph for %s while retaining the exact placement', (family, url) => {
    // Trial images are valid presentation metadata even when production
    // correctly excludes their not-yet-activated models from discovery.
    const asset = publicRealm.models.find(row => ['ready', 'runtime_trial'].includes(row.status) && row.asset.id.startsWith(`claude_public_realm:${family}:`))?.asset;
    expect(asset, family).toBeDefined();
    if (!asset) throw new Error(`Missing exact reviewed model: ${family}`);
    expect(pickerHeroImage(asset.id, asset.thumbnail)).toBe(url);
    expect(asset.thumbnail).not.toBe(url);
  });
  it.each(['classic_concrete', 'urban_brick', 'green_terraces', 'solar_ribbon', 'mobility_courtyard'])(
    'uses a photograph instead of a technical board for parkade %s', variant => {
      const id = `parkade_${variant}`;
      expect(CANONICAL_CHOICES.some(c => c.placements.some(a => a.id === id))).toBe(true);
      expect(pickerHeroImage(id, '/technical.png')).toBe(`/archetypes/buildings/classroom-heroes/${id}-photo-v1.webp`);
    },
  );
  it('gives the retained stepped-plaza choice a photographic presentation without activating a new model', () => {
    expect(pickerHeroImage('claude_trial_stepped_terraced_plaza_park_only', '')).toBe('/archetypes/openspaces/stepped-terraced-plaza/variant_0.png');
  });
});
