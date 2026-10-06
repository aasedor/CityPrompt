import { describe, expect, it } from 'vitest';
import { BUILDING_PROGRAMS, DISTRICT_RULES, matchBuilding, matchCatalogue, parseDesignation } from './matching';
import { ZONING_CATALOGUE_BUILDINGS } from './ZoningCatalogueCard';
import type { ZoneInspection } from './types';
import catalogue from '@/features/referenceLayers/calgaryBylawCatalogue.json';

const zone = (designation: string): ZoneInspection => ({ id: 'z', label: designation, source: 'Test', district: { designation } });
const model = (variant: string) => ZONING_CATALOGUE_BUILDINGS.find(a => a.model.variantId === variant)!;
const result = (variant: string, designation: string) => matchBuilding(model(variant), zone(designation));

describe('catalogue zoning screening', () => {
  it('reviews every exact current building revision without reviving legacy models', () => {
    expect(ZONING_CATALOGUE_BUILDINGS).toHaveLength(34);
    expect(Object.keys(BUILDING_PROGRAMS).sort()).toEqual(ZONING_CATALOGUE_BUILDINGS.map(a => a.model.variantId).sort());
    for (const a of ZONING_CATALOGUE_BUILDINGS) expect(BUILDING_PROGRAMS[a.model.variantId].revision).toBe(a.model.revision);
    expect(Object.keys(DISTRICT_RULES).sort()).toEqual(catalogue.districts.map(d => d.code).sort());
  });
  it('preserves full designations and rejects custom, DC, ambiguous or malformed modifiers', () => {
    expect(parseDesignation('MU-2f3.0h26d150')).toEqual({ code: 'MU-2', height: 26 });
    expect(parseDesignation('R-CGex')?.code).toBe('R-CGex');
    expect(parseDesignation('CR20-C20/R20')?.code).toBe('CR20-C20/R20');
    for (const code of ['DC48Z84', '123DC2020', 'R-CG / M-C1', 'MU-2 h26 h30', 'MU-2 h#', 'MU-2 h0', 'R-CG h100', 'My R-CG garden']) expect(parseDesignation(code)).toBeNull();
    expect(matchBuilding(model('infill_flat_roof_minimal'), { ...zone('R-CG'), custom: true }).status).toBe('review');
  });
  it('allows the same house in multiple districts and retains actual use categories', () => {
    expect(result('infill_flat_roof_minimal', 'R-CG').status).toBe('discretionary');
    expect(result('infill_flat_roof_minimal', 'R-G').status).toBe('permitted');
    expect(result('infill_flat_roof_minimal', 'R-Gm').status).toBe('discretionary');
    expect(result('infill_flat_roof_minimal', 'M-C1 d75').status).toBe('discretionary');
  });
  it('distinguishes side-by-side from stacked dwellings', () => {
    expect(result('infill_duplex', 'R-CG').uses[0].use).toBe('Semi-detached Dwelling');
    expect(result('montreal_duplex_plateau', 'R-CG').uses[0].use).toBe('Duplex Dwelling');
    expect(result('infill_duplex', 'R-C1').status).toBe('outside');
  });
  it('uses amended R-CG height and contextual ranges instead of assigning height from storeys', () => {
    expect(result('detached_infill_rammed_earth', 'R-CG').status).toBe('outside');
    expect(result('detached_infill_rammed_earth', 'R-CG').limit).toBe(10);
    expect(result('infill_duplex', 'R-C2').status).toBe('review');
    expect(result('med_villa_tuscan', 'R-1').status).toBe('review');
    expect(result('infill_flat_roof_minimal', 'R-C1').status).toBe('discretionary');
  });
  it('requires mapped heights and rejects an excessively tall model without silently scaling it', () => {
    expect(result('nordic_timber_mass_timber', 'MU-2').status).toBe('review');
    expect(result('nordic_timber_mass_timber', 'MU-2 h26').status).toBe('discretionary');
    expect(result('nordic_timber_mass_timber', 'MU-2 h20').status).toBe('outside');
    expect(result('glass_tower_blue_reflective', 'C-O h100').status).toBe('discretionary');
    expect(result('glass_tower_blue_reflective', 'C-O h50').status).toBe('outside');
    expect(result('nordic_timber_mass_timber', 'M-H1 h80').status).toBe('review');
  });
  it('requires every component in a mixed-use building', () => {
    expect(result('beltline_brick_modern', 'CC-MH').status).toBe('outside'); // housing yes, retail not listed
    const mixed = result('parisian_corner_cafe_culture', 'MU-2 h26');
    expect(mixed.status).toBe('discretionary');
    expect(mixed.uses.map(r => r.use)).toEqual(['Dwelling Unit', 'Restaurant: Food Service Only']);
  });
  it('does not transfer existing-building permitted uses onto new construction', () => {
    const library = result('mass_timber_biophilic_barn', 'MU-1 h26');
    expect(library.status).toBe('discretionary');
    expect(library.uses[0].section).toBe('1367(1)');
    expect(result('museum_earth_sheltered', 'R-C1').status).toBe('review');
  });
  it('keeps uncertain programs, worship classes and grade access out of confirmed lists', () => {
    expect(result('timber_sanctuary_church_glazed_gable', 'CC-X').status).toBe('review');
    expect(result('reference_charcoal_gable_fourplex_v1', 'R-CG').status).toBe('review');
    expect(result('nordic_timber_mass_timber', 'H-GO').status).toBe('outside');
    const small = { ...model('nordic_timber_mass_timber'), nativeDimensions: [10, 10, 10] as [number, number, number] };
    expect(matchBuilding(small, zone('H-GO')).status).toBe('review');
  });
  it('fails safely when a model changes, lacks dimensions or loses placement eligibility', () => {
    const home = model('infill_flat_roof_minimal');
    expect(matchBuilding({ ...home, model: { ...home.model, revision: 'new' } }, zone('R-G')).status).toBe('review');
    expect(matchBuilding({ ...home, nativeDimensions: undefined }, zone('R-G')).status).toBe('review');
    expect(matchCatalogue([{ ...home, readiness: 'candidate' }], zone('R-G'))).toHaveLength(0);
  });
});
