import { describe, expect, it } from 'vitest';
import { nativeStreetPilot, placeNativeStreetModules } from './nativeStreetPilot';
import { buildNativeStreetProgram, type NativeStreetProgram } from './nativeStreetProgram';
import { CATALOGUE_ASSETS, LOCAL_TOWER_ASSETS, validateRegistry } from '@/features/pickPlace/assetRegistry';
import { CANONICAL_CHOICES, filterCanonicalChoices } from '@/features/pickPlace/canonicalCatalogue';
import { CLAUDE_BUILDING_RELEASE_ASSETS } from '@/features/pickPlace/claudeBuildingRelease';
import drawnBridges from '@/data/nativeBridgePilots.json';

describe('three additional native street programs', () => {
  it('offers the consolidated classroom selection with distinct exact identities', () => {
    expect(drawnBridges).toHaveLength(10);
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'street')).toHaveLength(44 + drawnBridges.length);
    expect(CATALOGUE_ASSETS.filter(a => drawnBridges.some(row => row.id === a.model.variantId))
      .map(a => a.model.variantId).sort()).toEqual(drawnBridges.map(row => row.id).sort());
    expect(CLAUDE_BUILDING_RELEASE_ASSETS).toHaveLength(25);
    const buildingReleaseIds = new Set(CLAUDE_BUILDING_RELEASE_ASSETS.map(a => a.id));
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.zoneType === 'building' && !buildingReleaseIds.has(a.id))).toHaveLength(79+LOCAL_TOWER_ASSETS.length);
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.zoneType === 'building')).toHaveLength(104+LOCAL_TOWER_ASSETS.length);
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.zoneType === 'green_space' && a.model.method !== 'fixed_public_realm_v1' && !a.properties.court_only_native)).toHaveLength(38);
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.properties.court_only_native).map(a => a.model.variantId).sort()).toEqual([
      'court_only_basketball_v1', 'court_only_beach_volleyball_v1', 'court_only_pickleball_v1', 'court_only_tennis_v1',
    ]);
    expect(CATALOGUE_ASSETS.filter(a => a.kind === 'object' && a.zoneType === 'green_space')).toHaveLength(45);
    const fixed = CATALOGUE_ASSETS.filter(a => a.model.method === 'fixed_public_realm_v1');
    expect(fixed).toHaveLength(12);
    expect(fixed.filter(a => a.kind === 'object' && a.zoneType === 'road')).toHaveLength(9);
    expect(fixed.filter(a => a.kind === 'object' && a.zoneType === 'green_space')).toHaveLength(3);
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    expect(new Set(CANONICAL_CHOICES.map(c => c.id)).size).toBe(CANONICAL_CHOICES.length);
  });
  it.each([
    ['student_cycle_avenue_v1', 43], ['student_green_alley_v1', 30], ['student_school_street_v1', 28],
  ] as const)('%s retains all native fixtures and reconstructs its distinctive details', (id, count) => {
    const pilot = nativeStreetPilot(id)!;
    expect(filterCanonicalChoices('street_pathway',pilot.title).some(c => c.placements[0].model.variantId === id)).toBe(true);
    for (const multiplier of [1,2]) for (const reversed of [false,true]) {
      const length = pilot.fixtureLengthM * multiplier;
      const route = reversed ? [{x:0,y:length},{x:0,y:0}] : [{x:0,y:0},{x:0,y:length}];
      expect(placeNativeStreetModules(pilot,route)).toHaveLength(count*multiplier);
      const meshes = buildNativeStreetProgram(pilot.program!,pilot.widthM,pilot.fixtureLengthM,route);
      if (id === 'student_school_street_v1') expect(meshes.map(m => m.material)).toContain('paint.school_blue');
      if (id === 'student_cycle_avenue_v1') expect(meshes.map(m => m.material)).toContain('paint');
      for (const item of meshes) {
        item.geometry.computeBoundingBox();
        const box = item.geometry.boundingBox!;
        expect(box.min.y).toBeGreaterThanOrEqual(-.0001);
        expect(box.max.y).toBeLessThanOrEqual(length+.0001);
        expect(box.min.x).toBeGreaterThanOrEqual(-pilot.widthM/2-.001);
        expect(box.max.x).toBeLessThanOrEqual(pilot.widthM/2+.001);
        expect(pilot.program!.palette[item.material]).toHaveLength(3);
        item.geometry.dispose();
      }
    }
  });
  it('clips source detail triangles at route ends and splits them through a bend', () => {
    const program:NativeStreetProgram={schemaVersion:1,adapter:'test',surfaceRegions:[],details:[],
      meshDetails:[{material:'paint',positions:[-1,-10,0,1,10,0,-1,10,0],indices:[0,1,2]}],
      paving:'stone',pavingModuleM:[1,.8],minLengthM:1,maxLengthM:20,preparedLevelOnly:true,baseLiftM:.025,palette:{paint:[1,1,1]}};
    const meshes=buildNativeStreetProgram(program,4,20,[{x:0,y:0},{x:0,y:4},{x:4,y:4}]);
    const paint=meshes.find(m=>m.material==='paint')!.geometry;
    expect(paint.index!.count).toBeGreaterThan(3);
    const positions=Array.from(paint.attributes.position.array);
    expect(positions.every(Number.isFinite)).toBe(true);
    paint.computeBoundingBox();
    expect(paint.boundingBox!.min.y).toBeGreaterThanOrEqual(0);
    expect(paint.boundingBox!.max.x).toBeLessThanOrEqual(4.0001);
    meshes.forEach(m=>m.geometry.dispose());
  });
});
