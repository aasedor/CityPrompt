import { describe, it, expect } from 'vitest';
import type { Building, SiteZone } from '@/types';
import { catalogueZoneForBuilding } from './catalogueDeletion';
const zone = {id:'zone',properties:{pick_place_automatic_3d:true},building_ids:['new']} as unknown as SiteZone;
describe('catalogue model deletion', () => {
  it('resolves the source even when automatic rebuilding replaced the selected model ID', () => {
    const old = {id:'old',specifications:{community3DRepresentation:{schema_version:1,generator:'lego_assembly',zone_id:'zone'}}} as unknown as Building;
    expect(catalogueZoneForBuilding('old', [old], [zone])).toBe(zone);
  });
  it('resolves a current linked model without a marker', () => {
    expect(catalogueZoneForBuilding('new', [], [zone])).toBe(zone);
  });
  it('does not delete unrelated plots or imported buildings', () => {
    expect(catalogueZoneForBuilding('unrelated', [], [zone])).toBeUndefined();
    expect(catalogueZoneForBuilding('new', [], [{...zone,properties:{}}])).toBeUndefined();
  });
});
