// Install at frontend/src/features/pickPlace/neighbourhoodStreets.test.ts.
import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } from '@/components/viewer/globe/nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { effectiveRoadWidth } from '@/utils/roadGeometry';
import front from '@/data/nativeStreetPilots.json';
import type { StreetAsset } from './assetRegistry';

const expected = [
 ['student_rain_garden_residential_street_v1',15,2],
 ['student_compact_one_way_shopping_street_v1',15.5,1],
 ['student_neighbourhood_cycle_street_v1',13,2],
 ['student_separated_walking_cycling_greenway_v1',10,0],
 ['student_neighbourhood_transit_stop_street_v1',17,2],
] as const;

describe('five neighbourhood street native bindings', () => {
 it('has five unique ordinary cards and exact photographic choices', () => {
  const assets=CATALOGUE_ASSETS.filter(a=>expected.some(([id])=>a.id===id));
  expect(assets).toHaveLength(5);expect(validateRegistry(assets)).toEqual([]);
  for(const asset of assets){
   const choice=CANONICAL_CHOICES.find(c=>c.placements.some(a=>a.id===asset.id));
   expect(choice).toBeDefined();expect(choice!.option.photoUrl).toBe(asset.thumbnail);
   expect(asset.thumbnail).toMatch(/^\/archetypes\/streets\/neighbourhood-five\//);
  }
 });
 it.each(expected)('%s keeps exact width, parent and declared motor access', (id,width,lanes) => {
  const asset=CATALOGUE_ASSETS.find(a=>a.id===id) as StreetAsset;
  const pilot=nativeStreetPilot(id)!;const row=front.find(p=>p.id===id)!;
  expect(asset.kind).toBe('street');expect(asset.properties.lane_count).toBe(lanes);
  expect(asset.sectionWidth).toBe(width);expect(effectiveRoadWidth(asset.properties)).toBe(width);
  expect(resolvePilotStreetSectionProfile({properties:asset.properties})!.rowM).toBe(width);
  expect(asset.properties.road_archetype_id).toBe(pilot.sourceArchetypeId);
  expect(asset.model.revision).toBe(row.sourceRecipeSha256);
  if(id==='student_neighbourhood_transit_stop_street_v1')expect(asset.calgaryGuide.groupId).toBe('transit');
  expect(pilot.program!.preparedLevelOnly).toBe(true);
 });
 it.each(expected)('%s uses finite native modules and surfaces on a bounded route', (id) => {
  const pilot=nativeStreetPilot(id)!;const route=[{x:0,y:0},{x:0,y:60}];
  expect(nativeStreetLocalRouteProblem(pilot,route)).toBeNull();
  expect(nativeStreetLocalRouteProblem(pilot,[{x:0,y:0},{x:0,y:39}])).not.toBeNull();
  expect(nativeStreetLocalRouteProblem(pilot,[{x:0,y:0},{x:0,y:301}])).not.toBeNull();
  const poses=placeNativeStreetModules(pilot,route);expect(poses.length).toBeGreaterThan(0);
  expect(poses.length).toBeLessThanOrEqual(pilot.placements.length*2);
  for(const pose of poses){expect(pose.url).toContain('/street-kits/pilots/'+id+'/');expect(pose.sha256).toMatch(/^[a-f0-9]{64}$/);}
  const meshes=buildNativeStreetProgram(pilot.program!,pilot.widthM,pilot.fixtureLengthM,route);
  expect(meshes.length).toBeGreaterThan(0);
  for(const {geometry,material} of meshes){
   expect(pilot.program!.palette[material]).toHaveLength(3);
   expect([...geometry.attributes.position.array].every(Number.isFinite)).toBe(true);
   geometry.dispose();
  }
 });
});
