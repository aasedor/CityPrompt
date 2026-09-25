import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import assets from './publicRealmTrialAssets.json';
import { buildNativeStreetJunctionGround, nativeLocalJunction, nativeStreetJunctions } from './nativeStreetJunction';
import { clipStreetGeometryOutsideJunction } from './streetJunctionGeometry';
import { trimNativeStreetModel } from './nativeStreetModelTrim';

const origin = [-114.12, 51.0184];
const east = 111320 * Math.cos(origin[1] * Math.PI / 180);
const ring = (w: number, d: number, yaw = 0, shiftX = 0, shiftY = 0) =>
  [[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]].map(([x,y]) =>
    [origin[0] + (shiftX+x*Math.cos(yaw)-y*Math.sin(yaw))/east,
      origin[1] + (shiftY+x*Math.sin(yaw)+y*Math.cos(yaw))/111320]);
const common = { project_id: 'test', color: '#777', sort_order: 0,
  created_at: '2026-09-23', updated_at: '2026-09-23', is_active_boundary: false };
const boundary: SiteZone = { ...common, id: 'site', zone_type: 'site_boundary', is_active_boundary: true,
  coordinates: ring(150, 150), properties: { community_3d_mask_existing_tiles: true, terrain_elevation_m: 1098.2 } };
const street = (asset: (typeof assets)[number], yaw: number, id = asset.id): SiteZone => ({
  ...common, id, zone_type: 'road', coordinates: ring(asset.dimensions[0], asset.dimensions[1], yaw),
  properties: { public_realm_trial_asset: asset.id },
});
const market = assets.find((asset) => asset.id === 'student_market_street_v1')!;

describe('native street junction ownership', () => {
  it('connects every authored native street through the shared graph', () => {
    const streets = assets.filter((asset) => asset.kind === 'street');
    expect(streets).toHaveLength(12);
    for (const asset of streets) {
      expect(['pavers', 'brick', 'cobble', 'timber']).toContain('junctionSurface' in asset ? asset.junctionSurface : undefined);
      const first = street(asset, 0, 'first');
      const second = street(asset === market ? streets[0] : market, Math.PI / 2, 'second');
      const nodes = nativeStreetJunctions([boundary, first, second], 0);
      expect(nodes, asset.id).toHaveLength(1);
      expect(nodes[0].node.armCount).toBe(4);
      const ground = buildNativeStreetJunctionGround(nodes[0]);
      expect(ground.getAttribute('position').count).toBeGreaterThan(0);
      ground.dispose();
      // Registering a new section must also provide a usable T approach.
      const through = street(market, Math.PI / 2, 'through');
      const stem = { ...street(asset, 0, 'stem'),
        coordinates: ring(asset.dimensions[0], asset.dimensions[1], 0, 0, asset.dimensions[1] / 2) };
      expect(nativeStreetJunctions([boundary, through, stem], 0), `${asset.id} T`).toHaveLength(1);
    }
  });
  it.each([-1, 1])('owns only the three present native arms of a T, stem side %i', (side) => {
    const through = street(market, Math.PI / 2, 'through');
    const alley = assets.find((asset) => asset.id === 'student_green_alley_v1')!;
    const stem = { ...street(alley, 0, 'stem'),
      coordinates: ring(alley.dimensions[0], alley.dimensions[1], 0, 0, side * alley.dimensions[1] / 2) };
    const [junction] = nativeStreetJunctions([boundary, through, stem], 0);
    expect(junction).toBeDefined();
    expect(junction.node.armCount).toBe(3);
    expect(junction.node.approachSides.flat()).toHaveLength(3);
    expect(junction.layout.sidesB).toEqual([side]);
    const ground = buildNativeStreetJunctionGround(junction);
    const positions = ground.getAttribute('position');
    expect(positions.count).toBeGreaterThan(0);
    // The patch cannot paint a fourth road stem beyond the through street.
    const minY = Math.min(...Array.from({ length: positions.count }, (_, i) => positions.getY(i)));
    const maxY = Math.max(...Array.from({ length: positions.count }, (_, i) => positions.getY(i)));
    expect(side === 1 ? maxY : -minY).toBeGreaterThan(junction.layout.rowA);
    expect(side === 1 ? -minY : maxY).toBeLessThanOrEqual(junction.layout.rowA + .05);
    ground.dispose();
  });
  it('cuts both source grounds exactly and keeps the outer street', () => {
    const first = street(assets.find((asset) => asset.id === 'student_main_street_v1')!, 0);
    const second = street(assets.find((asset) => asset.id === 'student_cycle_avenue_v1')!, Math.PI / 2);
    const junction = nativeStreetJunctions([boundary, first, second], 0)[0];
    expect(junction).toBeDefined();
    const local = nativeLocalJunction(junction, junction.streets[0].placement);
    const source = new THREE.PlaneGeometry(23, 48);
    const trimmed = clipStreetGeometryOutsideJunction(source, local.layout, local.centerX, local.centerY);
    const ray = new THREE.Raycaster(new THREE.Vector3(0, 0, 10), new THREE.Vector3(0, 0, -1));
    const mesh = new THREE.Mesh(trimmed, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
    expect(ray.intersectObject(mesh)).toHaveLength(0);
    ray.ray.origin.set(0, 20, 10);
    expect(ray.intersectObject(mesh).length).toBeGreaterThan(0);
    source.dispose(); trimmed.dispose(); (mesh.material as THREE.Material).dispose();
  });
  it('keeps timber character through the boardwalk crossing', () => {
    const boardwalk = street(assets.find((asset) => asset.id === 'student_boardwalk_v1')!, 0);
    const alley = street(assets.find((asset) => asset.id === 'student_green_alley_v1')!, Math.PI / 2);
    const junction = nativeStreetJunctions([boundary, boardwalk, alley], 0)[0];
    const ground = buildNativeStreetJunctionGround(junction);
    const colors = ground.getAttribute('color');
    expect(Array.from({ length: colors.count }, (_, i) =>
      [colors.getX(i), colors.getY(i), colors.getZ(i)]).some(([r, g, b]) =>
      Math.abs(r - .43) < .001 && Math.abs(g - .32) < .001 && Math.abs(b - .22) < .001)).toBe(true);
    ground.dispose();
  });
  it('clears near junction props but retains ones down the street', () => {
    const first = street(market, 0);
    const second = street(assets.find((asset) => asset.id === 'student_green_alley_v1')!, Math.PI / 2);
    const junction = nativeStreetJunctions([boundary, first, second], 0)[0];
    const scene = new THREE.Group();
    const near = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
    const far = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
    far.position.z = -20;
    scene.add(near, far);
    const result = trimNativeStreetModel(scene, junction.streets[0].placement, [junction]);
    const meshes: THREE.Mesh[] = [];
    result.clone.traverse((object) => { if (object instanceof THREE.Mesh) meshes.push(object); });
    expect(meshes[0].geometry.getAttribute('position').count).toBe(0);
    expect(meshes[1].geometry.getAttribute('position').count).toBeGreaterThan(0);
    result.owned.forEach((geometry) => geometry.dispose());
    near.geometry.dispose(); far.geometry.dispose();
  });
  it('does not invent a junction for unprepared or mismatched native plots', () => {
    const a = street(market, 0);
    const b = street(assets.find((asset) => asset.id === 'student_green_alley_v1')!, Math.PI / 2);
    expect(nativeStreetJunctions([a, b], 0)).toHaveLength(0);
    expect(nativeStreetJunctions([{ ...boundary, properties: {} }, a, b], 0)).toHaveLength(0);
    expect(nativeStreetJunctions([boundary, { ...a, coordinates: ring(17, 48) }, b], 0)).toHaveLength(0);
  });
});
