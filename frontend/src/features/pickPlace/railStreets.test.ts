import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, validateRegistry, type StreetAsset } from './assetRegistry';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } from '@/components/viewer/globe/nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { effectiveRoadWidth } from '@/utils/roadGeometry';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';

const streets = [
  { id: 'student_median_lrt_avenue_v1', parent: 'light_rail_tram_avenue', width: 34, lanes: 4, minimum: 40,
    kinds: ['boulevard_tree', 'centre_pole', 'median_fence', 'street_light'] },
  { id: 'student_lrt_right_of_way_v1', parent: 'light_rail_tram_avenue', width: 20, lanes: 0, minimum: 40,
    kinds: ['aspen_clump', 'bench', 'litter_bin', 'pathway_light', 'relay_case', 'row_fence', 'side_mast'] },
  { id: 'student_high_speed_rail_line_v1', parent: 'high_speed_rail_corridor', width: 30, lanes: 0, minimum: 50,
    kinds: ['etcs_marker', 'hsr_mast', 'security_fence', 'trackside_cabinet'] },
];

describe.each(streets)('rail street $id', ({ id, parent, width, lanes, minimum, kinds }) => {
  const pilot = nativeStreetPilot(id)!;

  it('is an ordinary drawable street card with a rendered card image', () => {
    const asset = CATALOGUE_ASSETS.find(a => a.id === id) as StreetAsset;
    expect(asset).toBeDefined();
    expect(validateRegistry([asset])).toEqual([]);
    expect(asset.kind).toBe('street');
    expect(asset.reshapeMode).toBe('fixed_section_route');
    expect(asset.properties.lane_count).toBe(lanes);
    expect(asset.sectionWidth).toBe(width);
    expect(effectiveRoadWidth(asset.properties)).toBe(width);
    expect(asset.properties.road_archetype_id).toBe(parent);
    const choice = CANONICAL_CHOICES.find(c => c.placements.some(a => a.id === id));
    expect(choice?.domain).toBe('street_pathway');
    expect(choice!.option.photoUrl).toBe(asset.thumbnail);
    expect(asset.thumbnail).toBe(`/archetypes/streets/${parent.replace(/_/g, '-')}/${id}.png`);
  });

  it('describes its track bed as rail track, not paving or planting', () => {
    const asset = CATALOGUE_ASSETS.find(a => a.id === id) as StreetAsset;
    const profile = resolvePilotStreetSectionProfile({ properties: asset.properties })!;
    expect(profile.rowM).toBe(width);
    const track = profile.bands.filter(band => band.sourceType === 'rail_track');
    expect(track).toHaveLength(1);
    expect(track[0].surface).toMatch(/track/);
    expect(profile.bands.filter(band => band.kind === 'motor')).toHaveLength(lanes ? 2 : 0);
  });

  it(`accepts straight, bent and curved routes from ${minimum} m to 2 km, and nothing shorter`, () => {
    const curved = roundMetricStreetCenterline([[0, 0], [0, 80], [60, 160], [60, 260]], width).map(([x, y]) => ({ x, y }));
    for (const route of [[{ x: 0, y: 0 }, { x: 0, y: minimum }], [{ x: 0, y: 0 }, { x: 0, y: 70 }, { x: 50, y: 130 }],
      curved, [{ x: 0, y: 0 }, { x: 2000, y: 0 }]]) {
      expect(nativeStreetLocalRouteProblem(pilot, route)).toBeNull();
    }
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: minimum - 1 }])).not.toBeNull();
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 2001 }])).not.toBeNull();
  });

  it('repeats every authored module along a long straight route', () => {
    const cycles = 4;
    const poses = placeNativeStreetModules(pilot, [{ x: 0, y: 0 }, { x: 0, y: cycles * pilot.fixtureLengthM }]);
    expect(poses).toHaveLength(pilot.placements.length * cycles);
    expect([...new Set(poses.map(p => p.kind))].sort()).toEqual(kinds);
    for (const pose of poses) expect(pose.url).toBe(`/street-kits/pilots/${id}/${pose.kind}.glb`);
  });

  it('bends continuous rails and wires along a curved route', () => {
    const route = roundMetricStreetCenterline([[0, 0], [0, 80], [60, 160], [60, 260]], width).map(([x, y]) => ({ x, y }));
    const meshes = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, route);
    const byMaterial = Object.fromEntries(meshes.map(m => [m.material, m.geometry]));
    for (const material of ['rail', 'rail_head', 'wire']) expect(byMaterial[material], material).toBeDefined();
    for (const { geometry, material } of meshes) {
      expect(pilot.program!.palette[material], material).toHaveLength(3);
      expect([...geometry.attributes.position.array].every(Number.isFinite)).toBe(true);
    }
    const heads = byMaterial.rail_head;
    heads.computeBoundingBox();
    // the rails reach both ends of the route: from the start near y = 0 to the far end at x = 60
    expect(heads.boundingBox!.min.y).toBeLessThan(1);
    expect(heads.boundingBox!.max.y).toBeGreaterThan(255);
    expect(heads.boundingBox!.max.x).toBeGreaterThan(60);
    const wires = byMaterial.wire;
    wires.computeBoundingBox();
    expect(wires.boundingBox!.max.z).toBeGreaterThan(5.5);
    meshes.forEach(m => m.geometry.dispose());
  });
});
