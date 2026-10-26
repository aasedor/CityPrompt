import { describe, expect, it } from 'vitest';
import { browseAssets, courtOnlySportsAssets } from './assetRegistry';
import { assetForZone, placementProperties, placeAsset } from './catalogue';
import { rectangleAt, resizeRectangleCorner } from './geometry';
import { isFixedNativeScene } from './fixedNativeScene';
import { nativeParkEditProperties, nativeParkFitProblem, readNativePark } from '@/features/parks/nativeParkRegistry';
import type { SiteZone } from '@/types';
import { CANONICAL_CHOICES, filterCanonicalChoices, preferredCatalogueVariant } from './canonicalCatalogue';

describe('court-only student building blocks', () => {
  it.each([
    ['basketball', 'basketball_court'], ['tennis', 'tennis_court_cluster'],
    ['pickleball', 'pickleball_courts'], ['beach_volleyball', 'beach_volleyball_courts'],
  ])('offers %s court-only geometry once under its base sport', (sport, parent) => {
    const id = `native-park:court_only_${sport}_v1--native-v1`;
    const matches = CANONICAL_CHOICES.filter(choice => choice.placements.some(asset => asset.id === id));
    expect(matches).toHaveLength(1);
    const choice = matches[0];
    expect(choice.option.id).toBe(parent);
    expect(choice.option.variants?.filter(variant => variant.id === `court_only_${sport}_v1`)).toHaveLength(1);
    expect(CANONICAL_CHOICES.some(choice => choice.option.id.startsWith('court_only_'))).toBe(false);
    expect(filterCanonicalChoices('park_plaza', `${sport.replace(/_/g, ' ')} court only`, 'play_sport')).toContain(choice);
    expect(preferredCatalogueVariant(choice, 'court only')).toBe(`court_only_${sport}_v1`);
    // Grouping is presentation only: the stored parent, native layout and dimensions stay exact.
    const asset = choice.placements.find(asset => asset.id === id)!;
    expect(asset.properties.green_space_archetype_id).toBe(`court_only_${sport}`);
    expect(asset).toBe(placeAsset(id));
  });
  it('withholds unapproved pilots from production discovery while retaining saved identities', () => {
    const saved = courtOnlySportsAssets(false);
    expect(saved).toHaveLength(4);
    expect(browseAssets('court only', 'play_sport', saved)).toHaveLength(0);
    expect(saved.every(a => a.id.startsWith('native-park:court_only_'))).toBe(true);
  });
  it('offers four separate court-only choices in play and sport', () => {
    const courts = browseAssets('court only', 'play_sport');
    expect(courts).toHaveLength(4);
    expect(courts.every(c => c.kind === 'object' && c.reshapeMode === 'fixed_native')).toBe(true);
    expect(browseAssets('basketball', 'play_sport').length).toBeGreaterThan(1);
  });

  it.each(['basketball', 'tennis', 'pickleball', 'beach_volleyball'])('keeps %s native through rotation, movement and reload', sport => {
    const asset = placeAsset(`native-park:court_only_${sport}_v1--native-v1`);
    const coordinates = rectangleAt([-114.05,51.04],asset.width,asset.depth,35);
    const zone = {id:'court',zone_type:'green_space',coordinates,properties:placementProperties(asset,1040,coordinates)} as SiteZone;
    expect(isFixedNativeScene(zone.properties)).toBe(true);
    expect(nativeParkFitProblem(zone)).toBeNull();
    expect(resizeRectangleCorner(coordinates,0,coordinates[2],asset)).toEqual(coordinates);
    const moved = rectangleAt([-114.049,51.04],asset.width,asset.depth,82);
    const saved = JSON.parse(JSON.stringify({...zone,coordinates:moved,properties:nativeParkEditProperties(zone,moved)}));
    expect(assetForZone(saved)?.id).toBe(asset.id);
    expect(isFixedNativeScene(saved.properties)).toBe(true);
    expect(readNativePark(saved)?.layout.assets.assembly?.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(readNativePark(saved)?.layout.contentRevision).toBe(asset.model.revision);
    expect(nativeParkFitProblem(saved)).toBeNull();
    expect(nativeParkFitProblem({...saved,coordinates:rectangleAt([-114.049,51.04],2,2,82)})).toContain('complete');
    expect(asset.maxWidth).toBe(asset.width);
    expect(asset.maxDepth).toBe(asset.depth);
  });
});
