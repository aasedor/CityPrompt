import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createSharedSiteGroundLayout, sampleSharedSiteGround } from './sharedSiteGround';
import { measureParkTerrain, readParkTerrain } from './parkTerrain';
import { createSharedGroundTriangulation, drapeSharedGroundGeometry } from './sharedGroundGeometry';
import { getPreparedSiteBoundaryIds, resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { terraceOffset } from './terraceDefinition';

const point = (x: number,y: number) => [-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const park: SiteZone = { id:'park',project_id:'pilot',zone_type:'green_space',coordinates:[point(5,5),point(35,5),point(35,35),point(5,35)],properties:{},color:'#fff',created_at:'',updated_at:'',sort_order:0 };
const site: SiteZone = {...park,id:'site',zone_type:'site_boundary',is_active_boundary:true,coordinates:[point(0,0),point(40,0),point(40,40),point(0,40)],properties:{terrain_elevation_m:1000,community_3d_mask_existing_tiles:false,terrain_strategy:'landscape'}};
function review(slope = .2) {
  const layout = createSharedSiteGroundLayout(site)!;
  const heights = Array.from({length:layout.grid.columns*layout.grid.rows},(_,i)=>1000+(i%layout.grid.columns)*layout.grid.stepLng*metersPerDegLon(51)*slope);
  return {layout,heights,previousHeights:[...heights]};
}
describe('reviewed terrain-following park',()=>{
  it('preserves measured height variation through save/reopen and drapes across grid triangles',()=>{
    const profile=measureParkTerrain(park,review())!;
    const saved={...park,properties:{park_terrain:JSON.parse(JSON.stringify(profile)),proposed_terrace:{version:1,offsetM:2}}};
    const s=readParkTerrain(saved)!;
    expect(s).not.toBeNull(); expect(terraceOffset(saved)).toBeNull();
    expect(resolvePreparedSiteTerrainForZone(saved,[site,saved],999)).toBeNull();
    const a=sampleSharedSiteGround(s,...point(5,5) as [number,number])!,b=sampleSharedSiteGround(s,...point(35,5) as [number,number])!;
    expect(b-a).toBeCloseTo(6,4);
    const source=new THREE.PlaneGeometry(20,20);source.translate(20,20,0);
    const g=drapeSharedGroundGeometry(source,(x,y)=>sampleSharedSiteGround(s,...point(x,y) as [number,number])!-1000,3,100000,createSharedGroundTriangulation(s,-114,51));
    expect(g).not.toBeNull();
    const pos=g!.getAttribute('position');
    for(let i=0;i<pos.count;i++)expect(pos.getZ(i)).toBeCloseTo(pos.getX(i)*.2,3);
    source.dispose();g!.dispose();
  });
  it('permits a reviewed steep natural landscape without pretending it is a walkable path',()=>{
    expect(measureParkTerrain(park,review(.7))?.snapshot.quality.maxSlope).toBeCloseTo(.7,3);
    expect(measureParkTerrain(park,review(1.2))?.snapshot.quality.maxSlope).toBeCloseTo(1.2,3);
  });
  it('rejects missing, unstable and abrupt measurements instead of filling them',()=>{
    const r=review(), i=Math.floor(r.layout.grid.rows/2)*r.layout.grid.columns+Math.floor(r.layout.grid.columns/2);
    r.heights[i]=NaN; expect(measureParkTerrain(park,r)).toBeNull();
    const changed=review();changed.previousHeights[i]+=1;expect(measureParkTerrain(park,changed)).toBeNull();
    const roof=review();roof.heights[i]+=10;roof.previousHeights=[...roof.heights];expect(measureParkTerrain(park,roof)).toBeNull();
  });
  it('invalidates moved/resized footprints, retains local building pads and removes the whole-site table',()=>{
    const saved={...park,properties:{park_terrain:measureParkTerrain(park,review())}};
    expect(readParkTerrain({...saved,coordinates:saved.coordinates.map(p=>[p[0]+.00001,p[1]])})).toBeNull();
    expect(getPreparedSiteBoundaryIds([site,saved]).size).toBe(0);
    const house={...park,id:'house',zone_type:'building' as const,properties:{proposed_terrace:{version:1,offsetM:1}}};
    expect(resolvePreparedSiteTerrainForZone(house,[site,house,saved],999)).toBe(1001);
  });
});
