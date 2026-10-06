import { expect, it } from 'vitest';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS, OCTOBER_BUILDING_ASSETS } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import october from '@/data/catalogueOctober2026.json';

it('keeps every original fixed validation building bound to its exact delivered GLB',()=>{
  const buildings=validation.entries.filter(entry=>entry.domain==='building');
  expect(buildings).toHaveLength(15);
  for(const entry of buildings) {
    const asset=CATALOGUE_ASSETS.find(row=>row.id===entry.placement_id)!;
    expect(asset.properties.validation_native_url).toBe(entry.local_url);
    expect(asset.model.variantId).toBe(entry.variant_id);
    expect(asset.model.revision).toBe(entry.sha256);
  }
});

it('retains the existing Model Library contract for all 19 expansion buildings',()=>{
  const buildings=expansion.entries.filter(entry=>entry.domain==='building');
  expect(buildings).toHaveLength(19);
  for(const entry of buildings) {
    const asset=CATALOGUE_ASSETS.find(row=>row.id===entry.placement_id)!;
    expect(asset.properties.validation_native_url).toBeUndefined();
    expect(asset.model.variantId).toBe(entry.variant_id);
  }
});

it('makes the finite reviewed additions discoverable without duplicate saved variants',()=>{
  expect(october.entries).toHaveLength(25);
  for(const addition of OCTOBER_BUILDING_ASSETS) {
    const matches=CATALOGUE_ASSETS.filter(asset=>asset.properties.development_archetype_id===addition.properties.development_archetype_id && asset.model.variantId===addition.model.variantId);
    expect(matches).toHaveLength(1);
    const choice=CANONICAL_CHOICES.find(row=>row.placements.some(asset=>asset.id===addition.id));
    expect(choice).toBeDefined();
    expect(filterCanonicalChoices('building',addition.label)).toContain(choice);
    expect(matches[0].properties.validation_native_url).toBeUndefined();
    expect(matches[0].readiness).toBe(addition.readiness);
  }
});
