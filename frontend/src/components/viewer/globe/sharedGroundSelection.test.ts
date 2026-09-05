import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { createGroundSelection } from './sharedGroundSelection';
import { createSharedSiteGroundLayout, sharedSiteGroundGridPoint } from './sharedSiteGround';
import type { SiteZone } from '@/types';

const boundary: SiteZone = { id: 'site', project_id: 'project', zone_type: 'site_boundary', color: '#fff',
  sort_order: 0, created_at: 'today', updated_at: 'today', is_active_boundary: true,
  properties: { community_3d_mask_existing_tiles: false },
  coordinates: [[-114.047,51.045],[-114.0455,51.045],[-114.0455,51.046],[-114.047,51.046]],
};
describe('site-bounded ground tile selection', () => {
  it('covers every sampling point without depending on the viewing camera', () => {
    const layout = createSharedSiteGroundLayout(boundary)!;
    const {camera,resolution} = createGroundSelection(layout,1030);
    const world = new THREE.Vector3();
    for(let i=0;i<layout.grid.columns*layout.grid.rows;i++) {
      const [lng,lat]=sharedSiteGroundGridPoint(layout,i);
      WGS84_ELLIPSOID.getCartographicToPosition(lat*Math.PI/180,lng*Math.PI/180,1030,world);
      world.project(camera);
      expect(Math.abs(world.x)).toBeLessThan(1); expect(Math.abs(world.y)).toBeLessThan(1);
      expect(Math.abs(world.z)).toBeLessThan(1);
    }
    expect(Math.max(...resolution)).toBeLessThanOrEqual(1024);
  });
  it('ignores known remote geometry but retains relevant and unknown geometry', () => {
    const selection=createGroundSelection(createSharedSiteGroundLayout(boundary)!,1030);
    const mesh=new THREE.Mesh(new THREE.BoxGeometry(10,10,10));
    WGS84_ELLIPSOID.getCartographicToPosition(51.0455*Math.PI/180,-114.04625*Math.PI/180,1030,mesh.position);
    expect(selection.intersects(mesh)).toBe(true);
    const remote=mesh.clone();remote.position.addScalar(10000);
    expect(selection.intersects(remote)).toBe(false);
    expect(selection.intersects(new THREE.Group())).toBe(true);
    mesh.geometry.dispose();
  });
});
