import { describe, expect, it } from 'vitest';
import { DISTRICT_RULES, matchCatalogue, matchPark, PARK_PROGRAMS } from './matching';
import { ZONING_CATALOGUE_PARKS } from './ZoningCatalogueCard';
import type { ZoneInspection } from './types';
import { PUBLIC_REALM_RELEASE_ASSETS } from '@/features/pickPlace/publicRealmRelease';

const releaseParkIds = [
  'claude_public_realm:halifax-public-gardens-park-only:9282a9ffd6a3',
  'claude_public_realm:ice-rink-market-square-park-only:6a578c3c8e3c',
  'claude_public_realm:princes-island-park:498a973435fc',
];

const zone = (designation: string): ZoneInspection => ({ id: 'park-zone', label: designation, source: 'Test', district: { designation } });
const park = (variant: string) => ZONING_CATALOGUE_PARKS.find(a => a.id.startsWith('native-park:') && a.model.variantId === variant)!;
const result = (variant: string, code: string) => matchPark(park(variant), zone(code));

describe('park land-use screening', () => {
  it('preserves every reviewed native and flexible layout while adding the exact released parks', () => {
    expect(ZONING_CATALOGUE_PARKS).toHaveLength(45);
    const courts = ZONING_CATALOGUE_PARKS.filter(asset => asset.properties.court_only_native);
    expect(courts.map(asset => asset.model.variantId).sort()).toEqual([
      'court_only_basketball_v1', 'court_only_beach_volleyball_v1', 'court_only_pickleball_v1', 'court_only_tennis_v1',
    ]);
    // Native sport geometry does not itself certify a land-use programme.
    for (const court of courts) {
      expect(PARK_PROGRAMS[court.id]).toBeUndefined();
      expect(matchPark(court, zone('S-SPR'))).toMatchObject({ status: 'review', program: undefined, uses: [] });
    }
    const reviewed = ZONING_CATALOGUE_PARKS.filter(asset => !releaseParkIds.includes(asset.id) && !asset.properties.court_only_native);
    expect(reviewed).toHaveLength(38);
    expect(Object.keys(PARK_PROGRAMS).sort()).toEqual(reviewed.map(a => a.id).sort());
    for (const asset of reviewed) {
      expect(PARK_PROGRAMS[asset.id]).toMatchObject({ variantId: asset.model.variantId, revision: asset.model.revision });
      expect(PARK_PROGRAMS[asset.id].components.length).toBeGreaterThan(0);
    }
    const pocket = ZONING_CATALOGUE_PARKS.filter(a => a.model.variantId === 'urban_pocket_park_v0');
    expect(pocket).toHaveLength(2);
    expect(new Set(pocket.map(a => a.model.revision)).size).toBe(2);
    expect(matchCatalogue(pocket, zone('R-CG')).map(m => m.status)).toEqual(['permitted', 'permitted']);
  });
  it('keeps the three exact released park layouts under use review in every district', () => {
    const released = PUBLIC_REALM_RELEASE_ASSETS.filter(asset => asset.zoneType === 'green_space');
    expect(released.map(asset => asset.id).sort()).toEqual([...releaseParkIds].sort());
    expect(ZONING_CATALOGUE_PARKS.filter(asset => releaseParkIds.includes(asset.id)).map(asset => ({
      id: asset.id, variantId: asset.model.variantId, revision: asset.model.revision,
    }))).toEqual(released.map(asset => ({ id: asset.id, variantId: asset.model.variantId, revision: asset.model.revision })));
    for (const asset of released) {
      expect(asset.readiness).toBe('ready');
      expect(PARK_PROGRAMS[asset.id]).toBeUndefined();
      for (const code of Object.keys(DISTRICT_RULES)) {
        const match = matchPark(asset, zone(code));
        expect(match).toMatchObject({ status: 'review', program: undefined, uses: [] });
        expect(match.reasons).toContain('This exact park layout needs a use classification.');
        expect(match.height).toBeUndefined();
        expect(match.limit).toBeUndefined();
      }
    }
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
  it('distinguishes the new informal gardens from active sports facilities using the cited uses', () => {
    for (const variant of ['student_prairie_picnic_grove_v1', 'student_sensory_wellness_garden_v1']) {
      expect(result(variant, 'R-CG')).toMatchObject({ status: 'permitted', uses: [{ use: 'Park', definition: '249' }] });
    }
    for (const variant of ['student_neighbourhood_sports_green_v1', 'student_bicycle_pump_track_park_v1', 'student_urban_skate_plaza_v1']) {
      expect(result(variant, 'S-SPR')).toMatchObject({ status: 'permitted', uses: [{ use: 'Outdoor Recreation Area', definition: '248' }] });
      expect(result(variant, 'S-R').status).toBe('discretionary');
      expect(result(variant, 'R-CG').status).toBe('outside');
    }
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
