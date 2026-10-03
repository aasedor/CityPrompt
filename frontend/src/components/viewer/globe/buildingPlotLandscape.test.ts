import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { CATALOGUE_ASSETS, type PlaceAsset } from '@/features/pickPlace/assetRegistry';
import { placementProperties } from '@/features/pickPlace/catalogue';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { landscapeKeepClear } from '@/features/siteLandscape/siteLandscape';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { buildingGardenEnvelope, buildingGardenStyle, buildingPlotLandscapes } from './buildingPlotLandscape';
import { buildingLandscapeNotes } from './buildingLandscapeNotes';
import { pointInResidualGeometry } from './residualLandscape';
import { landscapedFoundationGeometry } from './BuildingFoundationSurface';
import { resolveBuildingGroundContact } from './buildingGroundContact';
import * as THREE from 'three';

const center = [-114, 51];
const buildings = CATALOGUE_ASSETS.filter((a): a is PlaceAsset => a.kind === 'object' && a.zoneType === 'building');
const zone = (id: string, width: number, depth: number, properties = {}, degrees = 0): SiteZone => ({
  id, project_id: 'test', zone_type: 'building', coordinates: rectangleAt(center, width, depth, degrees),
  properties, color: '#fff', sort_order: 0, created_at: '', updated_at: '',
});
const boundary: SiteZone = { ...zone('site', 500, 500, { community_3d_mask_existing_tiles: true, terrain_elevation_m: 1000 }), zone_type: 'site_boundary', is_active_boundary: true };
const home = buildings.find(a => a.id === 'validation_reference_charcoal_gable_fourplex_v1')!;
const homeZone = (width = home.width, depth = home.depth, degrees = 0) => zone('home', width, depth, placementProperties(home), degrees);

describe('shared building plot landscaping', () => {
  it('covers every current building choice without changing its model, plot or persisted properties', () => {
    expect(buildings).toHaveLength(32);
    for (const asset of buildings) {
      const placed = zone(asset.id, asset.width, asset.depth, placementProperties(asset));
      const before = JSON.stringify(placed);
      const plans = buildingPlotLandscapes([boundary, placed], 0);
      expect(plans, asset.label).toHaveLength(1);
      expect(plans[0].surface.length, asset.label).toBeGreaterThan(0);
      expect(plans[0].height).toBe(1000);
      expect(plans[0].design.archetypeId, asset.label).toBeTruthy();
      expect(plans[0].design.source, asset.label).toBe(plans[0].design.notes.length ? 'archetype_ground_notes' : 'conservative_fallback');
      expect(JSON.stringify(placed)).toBe(before);
    }
  });
  it('uses exact ground-level archetype cues without borrowing another variant or roof planting', () => {
    const notes = (id: string, variant: string) => buildingLandscapeNotes({ properties: {
      building_archetype_id: id, development_selected_variant_id: variant,
    } });
    const library = notes('university_library', 'mass_timber_biophilic_barn');
    expect(library.variantId).toBe('mass_timber_biophilic_barn');
    expect(library.planting).toBe('grasses');
    expect(library.notes.join(' ')).toContain('native planting beds at grade');
    expect(library.notes.join(' ')).not.toContain('fire circle');
    const infill = notes('minimalist_infill_townhouse', 'minimalist_infill_brick_monolith');
    expect(infill.planting).toBe('evergreen');
    expect(infill.notes.join(' ')).not.toContain('roof terrace');
    expect(notes('reference_charcoal_gable_fourplex', 'reference_charcoal_gable_fourplex_v1').planting).toBe('flowering');
  });
  it('keeps narrow plots clear and fits low gardens only outside the full native envelope and circulation strip', () => {
    expect(buildingPlotLandscapes([boundary, homeZone()], 0)[0].shrubs).toEqual([]);
    const placed = homeZone(36, 25), contract = buildingGardenEnvelope(placed)!;
    const plan = buildingPlotLandscapes([boundary, placed], 0)[0];
    expect(plan.shrubs.length).toBeGreaterThan(0);
    for (const [x, y] of plan.shrubs) {
      expect(Math.abs(x) - .42).toBeGreaterThan(contract.width / 2 + 1.2);
      expect(Math.abs(x) + .42).toBeLessThan(18);
      expect(Math.abs(y) + .42).toBeLessThan(contract.depth / 2);
    }
  });
  it('clips neighbouring roads and plots out of both ground cover and planting', () => {
    const road = { ...zone('road', 4, 100), zone_type: 'road' as const,
      coordinates: rectangleAt([center[0] + 15 / (111320 * Math.cos(51 * Math.PI / 180)), center[1]], 4, 100) };
    const plan = buildingPlotLandscapes([boundary, homeZone(36, 25), road], 0)[0];
    expect(pointInResidualGeometry([15, 0], { type: 'MultiPolygon', coordinates: plan.surface })).toBe(false);
    expect(plan.shrubs.every(([x]) => x < 12.58 || x > 17.42)).toBe(true);
  });
  it('follows rotation, movement and undo deterministically', () => {
    const original = homeZone(36, 25), rotated = homeZone(36, 25, 90);
    const a = buildingPlotLandscapes([boundary, original], 0)[0];
    const b = buildingPlotLandscapes([boundary, rotated], 0)[0];
    expect(b.shrubs.length).toBe(a.shrubs.length);
    b.shrubs.forEach(([x, y], i) => { expect(x).toBeCloseTo(-a.shrubs[i][1], 4); expect(y).toBeCloseTo(a.shrubs[i][0], 4); });
    expect(buildingPlotLandscapes([boundary, original], 0)[0]).toEqual(a);
    expect(buildingPlotLandscapes([boundary], 0)).toEqual([]);
  });
  it('keeps a saved side entrance corridor clear through an otherwise plantable bed', () => {
    const ll = (x: number, y: number) => [-114 + x / (111320 * Math.cos(51 * Math.PI / 180)), 51 + y / 111320];
    const line = [ll(31, -50), ll(31, 50)];
    const street = { ...zone('street', 12, 100), zone_type: 'road' as const, coordinates: bufferLineToPolygon(line, 12),
      properties: { road_archetype_id: 'calgary_local', road_selected_variant_id: 'calgary_local_v0', width: 12, plan_centerline: line } };
    const placed = homeZone(40, 25);
    placed.properties = { ...placed.properties, pedestrian_building_entrance: { version: 1, xM: 11.7, yM: 0,
      referenceWidthM: 40, referenceDepthM: 25, scaleWithPlot: false, streetId: 'street', widthM: 1.8 } };
    const zones = [boundary, placed, street];
    expect(landscapeKeepClear(zones).length).toBeGreaterThan(0);
    const plan = buildingPlotLandscapes(zones, 0)[0];
    expect(pointInResidualGeometry([15, 0], { type: 'MultiPolygon', coordinates: plan.beds })).toBe(false);
    expect(plan.shrubs.every(([x, y]) => x < 0 || Math.abs(y) > 2)).toBe(true);
  });
  it('does not guess model clearance for unknown or repeated houses', () => {
    const unknown = zone('old', 40, 40, { building_archetype_id: 'custom' });
    const repeated = { ...homeZone(40, 40), properties: { ...homeZone().properties, native_home_plot: true } };
    for (const placed of [unknown, repeated]) expect(buildingPlotLandscapes([boundary, placed], 0)[0].shrubs).toEqual([]);
  });
  it('preserves natural terrain, missing preparation, invalid polygons and deliberate custom ground artwork', () => {
    expect(buildingPlotLandscapes([homeZone()], 0)).toEqual([]);
    expect(buildingPlotLandscapes([{ ...boundary, properties: { ...boundary.properties, terrain_strategy: 'landscape' } }, homeZone()], 0)).toEqual([]);
    expect(buildingPlotLandscapes([boundary, { ...homeZone(), coordinates: [[NaN, 0]] }], 0)).toEqual([]);
    const coordinates = [...boundary.coordinates, boundary.coordinates[0]];
    const custom = { ...boundary, properties: { ...boundary.properties, community_3d_landscape: {
      schema_version: 1, state: 'compiled', generator: 'residual_landscape', boundary_id: 'site', compiled_at: '', source_hash: 'a', metric_crs: 'EPSG:32612',
      area_sqm: 100, occupied_area_sqm: 10, geometry: { type: 'Polygon', coordinates: [coordinates] }, regions: [], placements: [],
      surface_mode: 'site_base', surface_image_url: '/api/v1/files/projects/test/landscape/test.png',
    } } } as SiteZone;
    expect(buildingPlotLandscapes([custom, homeZone()], 0)).toEqual([]);
  });
  it('uses the actual building use even when an old card has a generic category', () => {
    expect(buildingGardenStyle({ properties: { building_archetype_id: 'earth_sheltered_museum' } })).toBe('civic');
    expect(buildingGardenStyle({ properties: { building_archetype_id: 'industrial_warehouse' } })).toBe('service');
    expect(buildingGardenStyle({ properties: { building_archetype_id: 'parisian_corner_cafe_culture' } })).toBe('urban');
    expect(buildingGardenStyle(homeZone())).toBe('residential');
  });
});

it('changes only the finish of foundation caps, preserving measured support geometry and vertical concrete', () => {
  const contact = resolveBuildingGroundContact([[[-5, -5], [5, -5], [5, 5], [-5, 5]]], -114, 51,
    { status: 'ready', contains: () => true, heightAt: (lng: number) => 1000 + (lng + 114) * 1000 });
  if (contact.status !== 'ready') throw new Error('fixture must be supported');
  const source = new THREE.BufferGeometry();
  source.setAttribute('position', new THREE.Float32BufferAttribute(contact.positions, 3)); source.setIndex(contact.indices);
  const landscaped = landscapedFoundationGeometry(source);
  expect(Array.from(landscaped.getAttribute('position').array)).toEqual(contact.positions.map(Math.fround));
  expect(Array.from(landscaped.getIndex()!.array)).toEqual(contact.indices);
  expect(new Set(landscaped.groups.map(g => g.materialIndex))).toEqual(new Set([0, 1]));
  expect(source.groups).toEqual([]);
  source.dispose(); landscaped.dispose();
});
