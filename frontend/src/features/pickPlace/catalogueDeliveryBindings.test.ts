import { expect, it } from 'vitest';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import { CATALOGUE_ASSETS } from './assetRegistry';

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
