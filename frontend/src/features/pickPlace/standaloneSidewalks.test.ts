import { describe, expect, it } from 'vitest';
import { PATHWAY_ASSETS, validateRegistry } from './assetRegistry';
import { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } from '@/components/viewer/globe/nativeStreetPilot';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { bufferLineToPolygon, effectiveRoadWidth } from '@/utils/roadGeometry';
import { roundMetricStreetCenterline } from '@/utils/streetRouteCurves';
import { streetConnectionProblem } from './streetConnectionProblem';
import type { SiteZone } from '@/types';

const ids = ['standalone_narrow_sidewalk_v1', 'standalone_neighbourhood_sidewalk_v1', 'standalone_urban_sidewalk_v1'];
describe('standalone sidewalks', () => {
  it('discovers all three exact pedestrian profiles automatically', () => {
    const assets = PATHWAY_ASSETS.filter(asset => ids.includes(asset.model.variantId));
    expect(assets.map(asset => asset.model.variantId)).toEqual(ids);
    expect(assets.map(asset => asset.sectionWidth)).toEqual([1.5, 2, 3]);
    expect(validateRegistry(assets)).toEqual([]);
  });
  it.each(ids)('%s follows fixed-width routes with no vehicle lanes or furniture', id => {
    const asset = PATHWAY_ASSETS.find(a => a.model.variantId === id)!;
    expect(asset).toBeDefined();
    const pilot = nativeStreetPilot(id)!;
    const section = resolvePilotStreetSectionProfile({ properties: asset.properties })!;
    expect(asset.properties.lane_count).toBe(0);
    expect(effectiveRoadWidth(asset.properties)).toBe(asset.sectionWidth);
    expect(section.rowM).toBe(asset.sectionWidth);
    expect(section.bands.every(b => b.kind === 'path' || b.kind === 'sidewalk')).toBe(true);
    expect(section.renderCurbs).toBe(false);
    expect(section.markings).toEqual([]);
    expect(section.treeOffsetsM).toEqual([]);
    const curved = roundMetricStreetCenterline([[0, 0], [0, 14], [9, 26], [2, 40]], asset.sectionWidth).map(([x, y]) => ({ x, y }));
    for (const route of [[{ x: 0, y: 0 }, { x: 0, y: Math.max(2, asset.sectionWidth) }], [{ x: 0, y: 30 }, { x: 0, y: 0 }], curved, [{ x: 0, y: 0 }, { x: 0, y: 300 }]]) {
      expect(nativeStreetLocalRouteProblem(pilot, route)).toBeNull();
      expect(placeNativeStreetModules(pilot, route)).toEqual([]);
      const meshes = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, route);
      expect(meshes.length).toBeGreaterThan(0);
      expect(meshes.reduce((n, mesh) => n + mesh.geometry.attributes.position.count, 0)).toBeLessThan(200000);
      for (const { geometry, material } of meshes) {
        expect(pilot.program!.palette[material]).toHaveLength(3);
        expect([...geometry.attributes.position.array].every(Number.isFinite)).toBe(true);
        geometry.computeBoundingBox();
        expect(geometry.boundingBox!.min.z).toBeGreaterThanOrEqual(.0249);
        expect(geometry.boundingBox!.max.z).toBeLessThan(.03);
        if (route.length === 2) {
          expect(geometry.boundingBox!.min.x).toBeGreaterThanOrEqual(-pilot.widthM / 2 - .0001);
          expect(geometry.boundingBox!.max.x).toBeLessThanOrEqual(pilot.widthM / 2 + .0001);
        }
        geometry.dispose();
      }
    }
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: pilot.program!.minLengthM - .1 }])).not.toBeNull();
    expect(nativeStreetLocalRouteProblem(pilot, [{ x: 0, y: 0 }, { x: 0, y: 2001 }])).not.toBeNull();
  });
  it.each(ids)('%s forms pedestrian junctions through the shared route contract', id => {
    const asset = PATHWAY_ASSETS.find(a => a.model.variantId === id)!;
    expect(asset).toBeDefined();
    const path = (zoneId: string, points: number[][]): SiteZone => {
      const line = points.map(([x, y]) => [x / 111320, y / 111320]);
      return { id: zoneId, project_id: 'test', color: '#aaa', sort_order: 0, created_at: '1', updated_at: '1', zone_type: 'road',
        coordinates: bufferLineToPolygon(line, asset.sectionWidth),
        properties: { ...asset.properties, plan_centerline: line, junction_preview_candidate: true } };
    };
    expect(streetConnectionProblem(path('branch', [[0, 0], [0, 25]]), [path('through', [[-25, 0], [25, 0]])])).toBeNull();
  });
});
