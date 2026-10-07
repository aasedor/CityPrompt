import { describe, expect, it } from 'vitest';
import { matchCatalogue, matchPark, PARK_PROGRAMS } from './matching';
import { ZONING_CATALOGUE_PARKS } from './ZoningCatalogueCard';
import type { ZoneInspection } from './types';

const zone = (designation: string): ZoneInspection => ({ id: 'park-zone', label: designation, source: 'Test', district: { designation } });
const park = (variant: string) => ZONING_CATALOGUE_PARKS.find(a => a.id.startsWith('native-park:') && a.model.variantId === variant)!;
const result = (variant: string, code: string) => matchPark(park(variant), zone(code));

describe('park land-use screening', () => {
  it('classifies every current native and flexible layout by placement, variant and revision', () => {
    expect(ZONING_CATALOGUE_PARKS).toHaveLength(33);
    expect(Object.keys(PARK_PROGRAMS).sort()).toEqual(ZONING_CATALOGUE_PARKS.map(a => a.id).sort());
    for (const asset of ZONING_CATALOGUE_PARKS) {
      expect(PARK_PROGRAMS[asset.id]).toMatchObject({ variantId: asset.model.variantId, revision: asset.model.revision });
      expect(PARK_PROGRAMS[asset.id].components.length).toBeGreaterThan(0);
    }
    const pocket = ZONING_CATALOGUE_PARKS.filter(a => a.model.variantId === 'urban_pocket_park_v0');
    expect(pocket).toHaveLength(2);
    expect(new Set(pocket.map(a => a.model.revision)).size).toBe(2);
    expect(matchCatalogue(pocket, zone('R-CG')).map(m => m.status)).toEqual(['permitted', 'permitted']);
  });
  it('permits the same recreational garden in several districts without inventing Natural Area status', () => {
    for (const code of ['S-SPR', 'R-CG', 'R-C1', 'R-Gm', 'M-G', 'MU-2']) {
      const match = result('urban_pocket_park_v0', code);
      expect(match.status).toBe('permitted');
      expect(match.uses[0]).toMatchObject({ use: 'Park', definition: '249' });
    }
    expect(result('wetland_rain_garden_v0', 'S-UN').status).toBe('outside');
    expect(result('urban_pocket_park_v0', 'S-FUD').status).toBe('outside');
  });
  it('keeps sandy beach screening under review until the operating use is established', () => {
    const match = result('student_sandy_beach_v1', 'S-SPR');
    expect(match.program).toMatchObject({ variantId: 'student_sandy_beach_v1' });
    expect(match.status).toBe('review');
    expect(match.reasons.join(' ')).toMatch(/operator, public access and swimming/);
  });
  it('distinguishes permitted sports, discretionary sports and conditional former-school sites', () => {
    for (const variant of ['basketball_court_v1', 'student_pickleball_garden_v1', 'student_tennis_garden_v2', 'student_bocce_garden_v2']) {
      expect(result(variant, 'S-SPR')).toMatchObject({ status: 'permitted', uses: [{ use: 'Outdoor Recreation Area', section: '1026' }] });
      expect(result(variant, 'S-R')).toMatchObject({ status: 'discretionary', uses: [{ section: '1043(1)' }] });
      expect(result(variant, 'S-FUD').status).toBe('discretionary');
      expect(result(variant, 'R-CG').status).toBe('outside');
      const conditional = result(variant, 'R-C1');
      expect(conditional.status).toBe('review');
      expect(conditional.reasons.join(' ')).toMatch(/existing building or previous site use/);
    }
  });
  it('requires the performance venue use in addition to the landscaped park', () => {
    expect(result('amphitheater_lawn_v0', 'S-R')).toMatchObject({ status: 'discretionary', uses: [
      { use: 'Park' }, { use: 'Performing Arts Centre', definition: '255' },
    ] });
    expect(result('amphitheater_lawn_v0', 'S-SPR').status).toBe('outside');
  });
  it('keeps the cafe unconfirmed until its principal food-service program is established', () => {
    const cafe = result('student_terraced_cafe_court_v1', 'CC-X');
    expect(cafe.status).toBe('review');
    expect(cafe.program?.review).toBeUndefined();
    expect(cafe.program?.classification?.evidence).toMatch(/no restaurant building/);
    expect(cafe.program?.siteReview).toMatch(/does not supply the restaurant/);
    expect(cafe.uses.map(use => use.use)).toEqual(['Park', 'Outdoor Café', 'Restaurant: Food Service Only']);
    expect(cafe.reasons.join(' ')).toMatch(/Outdoor Café cannot be approved by itself/);
    expect(result('student_terraced_cafe_court_v1', 'S-SPR').status).toBe('outside');
  });
  it('does not compare tree envelopes or missing park dimensions against building height', () => {
    const asset = park('urban_pocket_park_v0');
    for (const nativeDimensions of [undefined, [30, 30, 99] as [number, number, number]]) {
      const match = matchPark({ ...asset, nativeDimensions }, zone('R-CG'));
      expect(match.status).toBe('permitted');
      expect(match.height).toBeUndefined();
      expect(match.limit).toBeUndefined();
    }
  });
  it('fails safely on changed or unclassified layouts and excludes unavailable assets', () => {
    const asset = park('urban_pocket_park_v0');
    for (const changed of [
      { ...asset, id: 'unknown' },
      { ...asset, model: { ...asset.model, revision: 'changed' } },
      { ...asset, model: { ...asset.model, variantId: 'different' } },
    ]) {
      const match = matchPark(changed, zone('S-SPR'));
      expect(match.status).toBe('review');
      expect(match.program).toBeUndefined();
      expect(match.uses).toEqual([]);
    }
    expect(matchCatalogue([{ ...asset, readiness: 'candidate' }, { ...asset, zoneType: 'road' }], zone('S-SPR'))).toEqual([]);
    expect(matchPark(asset, zone('DC48Z84')).status).toBe('review');
    expect(matchPark(asset, { ...zone('S-SPR'), custom: true }).status).toBe('review');
  });
});
