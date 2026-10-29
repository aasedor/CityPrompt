import { afterAll, expect, it, vi } from 'vitest';
import contracts from '@/features/legoAssembly/buildingOnlyContracts.json';
import { CATALOGUE_BUILDING_ASSETS } from './publishedBuildingAssets';
import type { SiteZone } from '@/types';

// Exercise exact local pilots too; production eligibility has separate release-gate tests.
vi.stubEnv('DEV', true);
vi.stubEnv('MODE', 'development');
const { CATALOGUE_ASSETS } = await import('./assetRegistry');
const { CANONICAL_CHOICES } = await import('./canonicalCatalogue');
const { assetForZone, placementProperties, placeAsset } = await import('./catalogue');
const { buildingOnlySelectionCoordinates } = await import('./buildingOnlySelection');
const { rectangleAt, rectangleDimensions } = await import('./geometry');
afterAll(() => vi.unstubAllEnvs());

it.each(Object.entries(contracts))('fits %s to its retained full architectural envelope', (revision,c) => {
  const asset=CATALOGUE_ASSETS.find(a=>a.model.revision===revision);
  expect(asset?.kind).toBe('object');
  if(!asset || asset.kind!=='object') throw new Error('Missing candidate');
  const size=[c.bounds.max[0]-c.bounds.min[0],c.bounds.max[2]-c.bounds.min[2],c.bounds.max[1]-c.bounds.min[1]];
  expect(asset.nativeDimensions).toEqual(size);
  for(const [plot,extent] of [[asset.width,size[0]],[asset.depth,size[1]]]) {
    expect(plot).toBeGreaterThanOrEqual(extent+.0199);
    expect(plot-extent).toBeLessThan(.1201);
  }
  expect(asset.minWidth).toBe(asset.width); expect(asset.minDepth).toBe(asset.depth);
  const props=placementProperties(asset);
  expect(props.model_native_dimensions_m).toEqual(size);
  expect(assetForZone({properties:props})).toBe(asset);
  const choice=CANONICAL_CHOICES.find(x=>x.placements.some(p=>p.id===asset.id));
  const picked=choice?.placements.find(p=>p.id===asset.id);
  expect(picked?.kind==='object' ? picked.width : undefined).toBe(asset.width);
});

it('does not change older families, imports or the held Mews source',()=>{
  for(const raw of CATALOGUE_BUILDING_ASSETS.filter(a=>!(a.model.revision! in contracts))) {
    const registered=CATALOGUE_ASSETS.find(a=>a.id===raw.id);
    if(registered?.kind==='object' && !registered.footprintProgram) {
      expect(registered.width).toBe(raw.width);expect(registered.depth).toBe(raw.depth);
    }
  }
  expect(placeAsset('claude_trial_mews_coach_house').width).toBe(32);
});

it('fits an explicit new model selection without moving its centre or changing its angle',()=>{
  const target=placeAsset('claude_trial_old_montreal_limestone_commercial');
  const old=placeAsset('claude_trial_calgary_cbe_brutalist_hq');
  const zone={coordinates:rectangleAt([-114,51],150,150,15),properties:placementProperties(old)} as SiteZone;
  const fitted=rectangleDimensions(buildingOnlySelectionCoordinates(zone,target));
  expect(fitted.width).toBeCloseTo(target.width,3);expect(fitted.depth).toBeCloseTo(target.depth,3);
  expect(fitted.degrees).toBeCloseTo(15,2);expect(fitted.center).toEqual(rectangleDimensions(zone.coordinates).center);
  expect(buildingOnlySelectionCoordinates({...zone,properties:placementProperties(target)},target)).toBe(zone.coordinates);
  expect(buildingOnlySelectionCoordinates(zone,old)).toBe(zone.coordinates);
  const legacyProperties={...zone.properties,pick_place_model_revision:undefined};
  expect(buildingOnlySelectionCoordinates({...zone,properties:legacyProperties},old)).toBe(zone.coordinates);
});
