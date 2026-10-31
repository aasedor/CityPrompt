import { describe, expect, it } from 'vitest';
import { Matrix4, Vector3, BufferGeometry, Float32BufferAttribute } from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS } from '@/components/viewer/globe/publicRealmDepthPolicy';
import { detailAsset } from './detailCatalogue';
import { detailPlacementMatrix } from './detailInstances';
import { detailPlacementGroundHeight } from './detailGround';
import { detailPlacementSupport } from './safetyPlacement';
import { registerSafetySurface } from './safetySupport';

const pose = { lng: -114, lat: 51, angle: 0 };
const site: SiteZone = { id: 'site', project_id: 'p', zone_type: 'site_boundary',
  is_active_boundary: true, coordinates: rectangleAt([-114, 51], 100, 100),
  properties: { terrain_elevation_m: 1103, community_3d_mask_existing_tiles: true },
  color: '#aaa', sort_order: 0, created_at: 'now', updated_at: 'now' };
const paint = ['crosswalk_brick_infill_concept_6m_r1', 'crosswalk_continental_white_6m_r1',
  'crosswalk_diagonal_hatch_generic_6m_r1', 'crosswalk_ladder_white_6m_r1'];

function placedSourceHeight(id: string, sourceY: number, zones: SiteZone[], supportHeight?: number) {
  const model = detailAsset(id);
  const height = detailPlacementGroundHeight(model, zones, pose.lng, pose.lat, 1099, supportHeight);
  const inverse = WGS84_ELLIPSOID.getEastNorthUpFrame(pose.lat * Math.PI / 180,
    pose.lng * Math.PI / 180, 1103, new Matrix4()).invert();
  return new Vector3(0, sourceY, 0).applyMatrix4(detailPlacementMatrix({ ...pose, height }, inverse, model.offset, model.datumLift)).z;
}

describe('detail ground contact', () => {
  it.each(paint)('seats %s paint 4 mm above the visible prepared surface', id => {
    expect(placedSourceHeight(id, .004, [site])).toBeCloseTo(PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + .004, 6);
  });

  it('preserves the foot datum of tall safety objects and legacy furniture without double lifting', () => {
    expect(placedSourceHeight('calgary_delineator_illustrative_r1', 0, [site])).toBeCloseTo(.08, 6);
    expect(placedSourceHeight('timber-bench', 0, [site])).toBeCloseTo(.084, 6);
  });

  it('uses exact authored road support without adding the site lift a second time', () => {
    const geometry = new BufferGeometry().setAttribute('position', new Float32BufferAttribute([
      -10,-10,.1, 10,-10,.1, 10,10,.1, -10,-10,.1, 10,10,.1, -10,10,.1,
    ], 3));
    const remove = registerSafetySurface({ id: 'road', ...pose, height: 1103, geometries: [geometry] });
    try {
      const support = detailPlacementSupport(paint[0], pose, ['road']);
      expect(support.ok).toBe(true);
      if (!support.ok) throw new Error('Expected road support');
      expect(placedSourceHeight(paint[0], .004, [site], support.height)).toBeCloseTo(.104, 6);
    } finally { remove(); geometry.dispose(); }
  });

  it('leaves off-site, natural terrain and retained Google ground at the measured height', () => {
    const asset = detailAsset(paint[0]);
    expect(detailPlacementGroundHeight(asset, [], pose.lng, pose.lat, 1099)).toBe(1099);
    expect(detailPlacementGroundHeight(asset, [site], -113, 51, 1099)).toBe(1099);
    for (const properties of [{ terrain_strategy: 'landscape' }, { community_3d_mask_existing_tiles: false }]) {
      expect(detailPlacementGroundHeight(asset, [{ ...site, properties: { ...site.properties, ...properties } }],
        pose.lng, pose.lat, 1099)).toBe(1099);
    }
  });

  it('seats details on a containing named finish and invalidates that lift when it is removed or moved', () => {
    const surface = { ...site, id: 'finish', zone_type: 'development_area' as const,
      is_active_boundary: false, properties: { ground_surface_material: 'red_brick' } };
    const asset = detailAsset(paint[0]);
    expect(detailPlacementGroundHeight(asset, [surface], pose.lng, pose.lat, 1103)).toBeCloseTo(1103.08);
    expect(detailPlacementGroundHeight(asset, [surface], -113, 51, 1103)).toBe(1103);
    expect(detailPlacementGroundHeight(asset, [], pose.lng, pose.lat, 1103)).toBe(1103);
  });

  it('keeps raised terrace contact rather than reverting to the boundary datum', () => {
    const terrace = { ...site, id: 'terrace', zone_type: 'building' as const, is_active_boundary: false,
      properties: { proposed_terrace: { version: 1, offsetM: 1 } } };
    expect(detailPlacementGroundHeight(detailAsset(paint[0]), [site, terrace], pose.lng, pose.lat, 1099)).toBe(1104);
  });
});
