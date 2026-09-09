import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createSharedSiteGroundLayout, sampleSharedSiteGround } from './sharedSiteGround';
import { measureParkTerrain, readParkTerrain, reuseMeasuredParkTerrain } from './parkTerrain';
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
  it('reuses measured support for a new outline and preserves the original pass quality',()=>{
    const triangle={...park,coordinates:[point(5,5),point(35,5),point(20,35)]};
    const profile=measureParkTerrain(triangle,review())!;
    profile.snapshot.quality.maxPassDeltaM=.03;
    const edited={...park,properties:{park_terrain:profile}};
    const reused=reuseMeasuredParkTerrain(edited)!;
    expect(readParkTerrain({...edited,properties:{park_terrain:reused}})).not.toBeNull();
    expect(reused.snapshot.quality.maxPassDeltaM).toBe(.03);
    expect(sampleSharedSiteGround(reused.snapshot,...point(6,33) as [number,number])).toBeCloseTo(1001.2,3);
    expect(reuseMeasuredParkTerrain({...edited,coordinates:edited.coordinates.map(([x,y])=>[x+.01,y])})).toBeNull();
  });
  it('does not reuse an old grid where expanding a concave outline exposes rough ground',()=>{
    const r=review(),grid=r.layout.grid;
    const x=Math.round((point(7,30)[0]-grid.west)/grid.stepLng),y=Math.round((point(7,30)[1]-grid.south)/grid.stepLat);
    r.heights[y*grid.columns+x]+=5;r.previousHeights=[...r.heights];
    const triangle={...park,coordinates:[point(5,5),point(35,5),point(20,35)]};
    const profile=measureParkTerrain(triangle,r)!;
    expect(profile).not.toBeNull();
    expect(reuseMeasuredParkTerrain({...park,properties:{park_terrain:profile}})).toBeNull();
  });
  it.each([
    [[5.234567,5.123457],[35.134567,5.312345],[20.142857,35.831234]],
    [[5.234567,5.123457],[35.134567,5.123457],[35.134567,18.312345],[18.142857,18.312345],[18.142857,35.831234],[5.234567,35.831234]],
  ])('drapes Float32 irregular outlines without losing the park at a boundary corner', (...ring) => {
    const outline={...park,coordinates:ring.map(([x,y])=>point(x,y))};
    const profile=measureParkTerrain(outline,review())!;
    const source=new THREE.ShapeGeometry(new THREE.Shape(ring.map(([x,y])=>new THREE.Vector2(x,y))));
    const g=drapeSharedGroundGeometry(source,(x,y)=>{
      const height=sampleSharedSiteGround(profile.snapshot,...point(x,y) as [number,number]);
      return height===null?null:height-1000;
    },3,100000,createSharedGroundTriangulation(profile.snapshot,-114,51));
    expect(g).not.toBeNull(); expect(g!.getAttribute('position').count).toBeGreaterThan(3);
    const pos=g!.getAttribute('position');
    for(let i=0;i<pos.count;i++)expect(pos.getZ(i)).toBeCloseTo(pos.getX(i)*.2,3);
    expect(sampleSharedSiteGround(profile.snapshot,...point(5.224,5.113) as [number,number])).toBeNull();
    if(ring.length===6)expect(sampleSharedSiteGround(profile.snapshot,...point(25,25) as [number,number])).toBeNull();
    source.dispose();g!.dispose();
  });
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
