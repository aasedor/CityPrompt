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
  // This compatibility programme is intentionally absent from student discovery.
  const option = {id:'skate_park',label:'Skate park',description:'Saved-project compatibility fixture',
    photoUrl:'/archetypes/openspaces/skate-park/variant_0.png',variants:[{id:'skate_park_v0',label:'Professional grade'}]};
  const choice = { id:'park_plaza:skate_park',domain:'park_plaza' as const,option,placements:[] };
  const asset = canonicalParkAsset({ choice, variant: choice.option.variants![0] });
  const { width: w, depth: d } = asset;
  expect(fitSkateParkV0Program([{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: d }, { x: 0, y: d }])?.scale).toBe(1);
  expect(canonicalParkById('canonical-park:skate_park:unknown')).toBeUndefined();
});
