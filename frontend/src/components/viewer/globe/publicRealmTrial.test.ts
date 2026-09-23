import { describe, expect, it } from 'vitest';
import { Group } from 'three';
import type { SiteZone } from '@/types';
import assets from './publicRealmTrialAssets.json';
import { assertPublicRealmTrialsReady, publicRealmTrialGroundCells, publicRealmTrialPlacement } from './publicRealmTrial';
const origin = [-114.12, 51.0184];
const east = 111320 * Math.cos(origin[1] * Math.PI / 180);
const ring = (w: number, d: number, yaw = 0) => [[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]].map(([x,y]) => [origin[0]+(x*Math.cos(yaw)-y*Math.sin(yaw))/east,origin[1]+(x*Math.sin(yaw)+y*Math.cos(yaw))/111320]);
const common = { project_id: 'test', color: '#668545', sort_order: 0, created_at: '2026-09-22', updated_at: '2026-09-22', is_active_boundary: false };
const boundary: SiteZone = {...common,id:'site',zone_type:'site_boundary',is_active_boundary:true,coordinates:ring(150,150),properties:{community_3d_mask_existing_tiles:true,terrain_elevation_m:1098.2}};
const zone: SiteZone = {...common,id:'park',zone_type:'green_space',coordinates:ring(34,34),properties:{public_realm_trial_asset:assets[0].id}};
describe('bounded public-realm native trial', () => {
  it('preserves native scale and uses the current prepared site datum', () => {
    const placed = publicRealmTrialPlacement(zone,[boundary,zone],42);
    expect(placed?.height).toBe(1098.2);
    expect(placed?.yaw).toBeCloseTo(0);
    expect(publicRealmTrialPlacement({...zone,coordinates:ring(34,34,.7)},[boundary],42)?.yaw).toBeCloseTo(.7);
  });
  it('rejects stretching, wrong orientation, missing preparation and outside plots', () => {
    expect(publicRealmTrialPlacement({...zone,coordinates:ring(33,34)},[boundary],42)).toBeNull();
    expect(publicRealmTrialPlacement({...zone,coordinates:ring(34,34).reverse()},[boundary],42)).toBeNull();
    expect(publicRealmTrialPlacement(zone,[{...boundary,properties:{community_3d_mask_existing_tiles:false}}],42)).toBeNull();
    expect(publicRealmTrialPlacement(zone,[{...boundary,coordinates:ring(30,30)}],42)).toBeNull();
    expect(publicRealmTrialPlacement(zone,[],42)).toBeNull();
  });
  it('rejects a narrow boundary notch crossing the native plot', () => {
    const points=[[-50,-50],[50,-50],[50,50],[1,50],[1,0],[-1,0],[-1,50],[-50,50]];
    const notched={...boundary,coordinates:points.map(([x,y])=>[origin[0]+x/east,origin[1]+y/111320])};
    expect(publicRealmTrialPlacement(zone,[notched],42)).toBeNull();
  });
  it('reconstructs one ground owner per cell, keeping sports-module openings', () => {
    for (const asset of assets) {
      const cells=publicRealmTrialGroundCells(asset);
      const area=cells.reduce((sum,c)=>sum+c.width*c.depth,0);
      const holes=asset.surfaceRegions.filter(r=>r.material===null).reduce((sum,r)=>sum+r.width*r.depth,0);
      expect(area+holes).toBeCloseTo(asset.dimensions[0]*asset.dimensions[1],5);
      expect(cells.every(c=>c.width>0&&c.depth>0)).toBe(true);
    }
  });
  it('blocks capture while a model is loading, failed or unsupported', () => {
    for (const status of ['loading','unavailable','unsupported']) {
      const scene=new Group(); const model=new Group(); scene.add(model);
      model.userData.publicRealmTrialStatus=status;
      expect(()=>assertPublicRealmTrialsReady(scene)).toThrow('not ready');
      model.userData.publicRealmTrialStatus='ready';
      expect(()=>assertPublicRealmTrialsReady(scene)).not.toThrow();
    }
  });
  it('rebuilds every native tree-well footprint as soil without pavement over its opening', () => {
    let wells = 0;
    for (const asset of assets) {
      const cells = publicRealmTrialGroundCells(asset);
      for (const well of asset.treeWells) {
        wells++;
        const overlaps = cells.filter(cell => Math.abs(cell.x - well.x) < (cell.width + well.width) / 2 - 1e-6
          && Math.abs(cell.y - well.y) < (cell.depth + well.depth) / 2 - 1e-6);
        expect(overlaps.length).toBeGreaterThan(0);
        expect(overlaps.every(cell => cell.material === 'soil')).toBe(true);
        expect(overlaps.reduce((area, cell) => area + cell.width * cell.depth, 0)).toBeCloseTo(well.width * well.depth, 6);
      }
    }
    expect(wells).toBe(8);
  });
});
