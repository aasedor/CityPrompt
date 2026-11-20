import { expect, it } from 'vitest';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS, OCTOBER_BUILDING_ASSETS } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import october from '@/data/catalogueOctober2026.json';
import { placementProperties } from './catalogue';
import { readBuildingEntrance } from './pedestrianConnections';
import type { SiteZone } from '@/types';

it('keeps every original fixed validation building bound to its exact delivered GLB',()=>{
  const buildings=validation.entries.filter(entry=>entry.domain==='building' && !entry.standalone_native);
  expect(buildings).toHaveLength(15);
  for(const entry of buildings) {
    const asset=CATALOGUE_ASSETS.find(row=>row.id===entry.placement_id)!;
    expect(asset.properties.validation_native_url).toBe(entry.local_url);
    expect(asset.model.variantId).toBe(entry.variant_id);
    expect(asset.model.revision).toBe(entry.sha256);
  }
});

it('publishes the five standalone buildings once each with their exact models and picker images', () => {
  const buildings = validation.entries.filter(entry => entry.standalone_native);
  expect(buildings.map(entry => entry.placement_id).sort()).toEqual([
    'london_crescent_terrace_bath_stone',
    'plus15_brutalist_concrete_office',
    'rlasm_folded_roof_market_hall',
    'rlasm_passage_tower',
    'rlasm_terraced_science_centre',
  ]);
  for (const entry of buildings) {
    const asset = CATALOGUE_ASSETS.find(row => row.id === entry.placement_id);
    if (!asset || asset.kind !== 'object') throw new Error('Missing building ' + entry.placement_id);
    expect(asset).toMatchObject({
      readiness: 'ready',
      standaloneNative: true,
      model: { variantId: entry.variant_id, revision: entry.model_revision ?? entry.sha256 },
      properties: { validation_native_url: `/model-revisions/${entry.sha256}.glb` },
    });
    const choices = CANONICAL_CHOICES.filter(choice => choice.placements.some(row => row.id === entry.placement_id));
    expect(choices).toHaveLength(1);
    expect(choices[0].option.photoUrl).toBe(asset.thumbnail);
    expect(filterCanonicalChoices('building', entry.title)).toContain(choices[0]);
    if (!entry.model_revision) {
      const zone = { properties: placementProperties(asset) } as SiteZone;
      expect(readBuildingEntrance(zone)).toMatchObject({ automatic: true, widthM: 3 });
    }
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
