import { expect, it } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { canonicalParkAsset, canonicalParkById } from './canonicalParkPlacement';
import { assetForZone, placementProperties, placeAsset } from './catalogue';
import { fitSkateParkV0Program } from '@/components/viewer/globe/skateParkFit';

it('provides resolvable placement for every eligible park variant without certifying geometry', () => {
  for (const choice of CANONICAL_CHOICES.filter(c => c.domain === 'park_plaza')) {
    for (const variant of choice.option.variants ?? [undefined]) {
      const asset = canonicalParkAsset({ choice, variant });
      expect(placeAsset(asset.id)).toBe(asset);
      expect(assetForZone({ properties: placementProperties(asset) })).toBe(asset);
      expect(asset.model.method).toBe('canonical_design');
      expect(asset.properties.public_realm_lego).toBeUndefined();
    }
  }
});
it('receives the reviewed skate programme at its real size including edge clearance', () => {
  const choice = CANONICAL_CHOICES.find(c => c.domain === 'park_plaza' && c.option.id === 'skate_park')!;
  const asset = canonicalParkAsset({ choice, variant: choice.option.variants![0] });
  const { width: w, depth: d } = asset;
  expect(fitSkateParkV0Program([{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: d }, { x: 0, y: d }])?.scale).toBe(1);
  expect(canonicalParkById('canonical-park:skate_park:unknown')).toBeUndefined();
});
