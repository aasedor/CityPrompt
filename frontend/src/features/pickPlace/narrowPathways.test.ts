import { describe, expect, it } from 'vitest';
import { PATHWAY_ASSETS, validateRegistry } from './assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from './canonicalCatalogue';
import { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } from '@/components/viewer/globe/nativeStreetPilot';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';
import { bufferLineToPolygon, effectiveRoadWidth } from '@/utils/roadGeometry';
import { streetConnectionProblem } from './streetConnectionProblem';
import type { SiteZone } from '@/types';

describe('narrow, surface-only pathways', () => {
  it('registers unique searchable exact choices with their own photographic previews', () => {
    expect(PATHWAY_ASSETS).toHaveLength(5);
    expect(validateRegistry(PATHWAY_ASSETS)).toEqual([]);
    for (const asset of PATHWAY_ASSETS) {
      const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === asset.id))!;
      expect(choice.option.photoUrl).toBe(asset.thumbnail);
      expect(filterCanonicalChoices('street_pathway', asset.label, 'active')).toContain(choice);
      expect(asset.properties.road_standard_citation).toContain('not a Calgary');
    }
  });
  it.each(PATHWAY_ASSETS)('$label preserves its narrow walking section without motor lanes', asset => {
    const profile = resolvePilotStreetSectionProfile({properties: asset.properties})!;
    expect(profile.rowM).toBe(asset.sectionWidth);
    expect(effectiveRoadWidth(asset.properties)).toBe(asset.sectionWidth);
    expect(profile.bands.every(b => b.kind === 'path' || b.kind === 'sidewalk')).toBe(true);
    expect(profile.markings).toEqual([]);
    expect(profile.renderCurbs).toBe(false);
    expect(profile.treeOffsetsM).toEqual([]);
  });
  it.each(PATHWAY_ASSETS)('$label follows straight, reversed and winding routes without extra occupied width', asset => {
    const pilot = nativeStreetPilot(asset.model.variantId)!;
    const winding = roundMetricStreetCenterline([[0,0],[0,14],[9,26],[2,40]], asset.sectionWidth).map(([x,y])=>({x,y}));
    for (const route of [[{x:0,y:0},{x:0,y:30}], [{x:0,y:30},{x:0,y:0}], winding, [{x:0,y:0},{x:0,y:300}]]) {
      expect(nativeStreetLocalRouteProblem(pilot, route)).toBeNull();
      expect(placeNativeStreetModules(pilot, route)).toEqual([]);
      const meshes = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, route);
      expect(meshes.length).toBeGreaterThan(0);
      expect(meshes.reduce((sum, mesh) => sum + mesh.geometry.attributes.position.count, 0)).toBeLessThan(200_000);
      for (const {geometry, material} of meshes) {
        expect(pilot.program!.palette[material]).toHaveLength(3);
        expect([...geometry.attributes.position.array].every(Number.isFinite)).toBe(true);
        geometry.computeBoundingBox();
        expect(geometry.boundingBox!.min.z).toBeGreaterThanOrEqual(.0249);
        expect(geometry.boundingBox!.max.z).toBeLessThan(.03);
        if (route.length === 2) {
          expect(geometry.boundingBox!.min.x).toBeGreaterThanOrEqual(-pilot.widthM/2-.0001);
          expect(geometry.boundingBox!.max.x).toBeLessThanOrEqual(pilot.widthM/2+.0001);
        }
        geometry.dispose();
      }
    }
    expect(nativeStreetLocalRouteProblem(pilot,[{x:0,y:0},{x:0,y:1}])).not.toBeNull();
    expect(nativeStreetLocalRouteProblem(pilot,[{x:0,y:0},{x:0,y:301}])).not.toBeNull();
  });
  it.each(PATHWAY_ASSETS)('$label can form a perpendicular path junction through the shared geometry contract', asset => {
    const road = (id:string, points:number[][]):SiteZone => {
      const line=points.map(([x,y])=>[x/111320,y/111320]);
      return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:bufferLineToPolygon(line,asset.sectionWidth),
        properties:{...asset.properties,plan_centerline:line,junction_preview_candidate:true}};
    };
    expect(streetConnectionProblem(road('branch',[[0,0],[0,25]]),[road('through',[[-25,0],[25,0]])])).toBeNull();
  });
});
