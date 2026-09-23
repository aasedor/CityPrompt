import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { createSharedSiteGroundLayout, sharedSiteGroundGridPoint } from './sharedSiteGround';
import { createPreparedEdgeGeometry, measurePreparedEdges, preparedEdgeSummary, readPreparedEdges } from './preparedSiteEdges';
import * as THREE from 'three';

const origin: [number,number] = [-114,51];
const point = (x: number,y: number) => [origin[0]+x/metersPerDegLon(origin[1]),origin[1]+y/METERS_PER_DEG_LAT];
const site = { id: 'site', coordinates: [point(0,0),point(20,0),point(20,20),point(0,20)], properties: {}, updated_at: 'today' } as SiteZone;
function review(boundary = site) {
  const layout = createSharedSiteGroundLayout(boundary)!;
  const heights = Array.from({length:layout.grid.rows*layout.grid.columns},(_,i)=>100+(sharedSiteGroundGridPoint(layout,i)[0]-origin[0])*metersPerDegLon(51)*0.2);
  return { layout, heights, previousHeights: [...heights] };
}
describe('prepared-site retaining edges', () => {
  it('opens a bent road through cut and fill faces while preserving the rest of the boundary', () => {
    const profile = measurePreparedEdges(site,review())!;
    // Concave L: 4 m opening on the south edge and 4 m on the east edge.
    const opening = [[8,-2],[12,-2],[12,6],[22,6],[22,10],[8,10]].map(([x,y])=>point(x,y));
    const full = createPreparedEdgeGeometry(profile,102,origin);
    const opened = createPreparedEdgeGeometry(profile,102,origin,true,[opening]);
    const area = (geometry: THREE.BufferGeometry) => {
      const p=geometry.getAttribute('position'),a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
      let sum=0;
      for(let i=0;i<p.count;i+=3) {
        a.fromBufferAttribute(p,i);b.fromBufferAttribute(p,i+1);c.fromBufferAttribute(p,i+2);
        sum+=b.sub(a).cross(c.sub(a)).length()/2;
      }
      return sum;
    };
    expect(area(opened)).toBeLessThan(area(full)-8);
    expect(area(opened)).toBeGreaterThan(area(full)-15);
    const material = new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
    const mesh = new THREE.Mesh(opened,material);
    const hits = (x:number,y:number,z:number,dx:number,dy:number) => new THREE.Raycaster(
      new THREE.Vector3(x,y,z),new THREE.Vector3(dx,dy,0),0,3).intersectObject(mesh).length;
    expect(hits(9,-1,-.1,0,1)).toBe(0); // Fill-side road opening.
    expect(hits(21,8,1,-1,0)).toBe(0); // Cut-side road opening.
    expect(hits(3,-1,-.5,0,1)).toBeGreaterThan(0);
    expect(hits(21,13,1,-1,0)).toBeGreaterThan(0);
    opened.dispose();full.dispose();material.dispose();
  });
  it('uses repeatable perimeter measurements, with cut and fill at the proposed level', () => {
    const profile = measurePreparedEdges(site,review())!;
    expect(profile.samples.length).toBeGreaterThan(28);
    const summary = preparedEdgeSummary(profile,102);
    expect(summary.maximumFill).toBeCloseTo(2); expect(summary.maximumCut).toBeCloseTo(2);
    const saved = { ...site, properties: {terrain_edge_profile:profile} };
    expect(readPreparedEdges(saved)).toBe(profile);
  });
  it('never fills missing or unstable support samples and requires two passes', () => {
    const measured = review();
    expect(measurePreparedEdges(site,{...measured,previousHeights:undefined})).toBeNull();
    expect(measurePreparedEdges(site,{...measured,heights:measured.heights.map((h,i)=>i===0?null:h)})).toBeNull();
    expect(measurePreparedEdges(site,{...measured,previousHeights:measured.heights.map(h=>h+0.1)})).toBeNull();
    expect(measurePreparedEdges(site,{...measured,heights:measured.heights.map(()=>NaN)})).toBeNull();
  });
  it('rejects stale or corrupt saved profiles instead of moving old walls', () => {
    const profile = measurePreparedEdges(site,review())!;
    expect(readPreparedEdges({...site,coordinates:site.coordinates.map(([x,y])=>[x+0.0001,y]),properties:{terrain_edge_profile:profile}})).toBeNull();
    expect(readPreparedEdges({...site,properties:{terrain_edge_profile:{...profile,samples:[[0,0,100]]}}})).toBeNull();
    expect(measurePreparedEdges({...site,coordinates:site.coordinates.slice(1)},review())).toBeNull();
  });
  it('bounds work on oversized perimeters', () => {
    const huge = {...site,coordinates:[point(0,0),point(2000,0),point(2000,2000),point(0,2000)]};
    expect(measurePreparedEdges(huge,review())).toBeNull();
  });
  it('builds finite vertical faces on the boundary and splits cut/fill transitions', () => {
    const profile = measurePreparedEdges(site,review())!;
    const geometry = createPreparedEdgeGeometry(profile,101.3,origin);
    const positions = geometry.getAttribute('position');
    expect(positions.count).toBeGreaterThan(0);
    for(let i=0;i<positions.count;i++) {
      const x=positions.getX(i), y=positions.getY(i), z=positions.getZ(i);
      expect(Number.isFinite(z)).toBe(true);
      expect(Math.min(Math.abs(x),Math.abs(x-20),Math.abs(y),Math.abs(y-20))).toBeLessThan(0.001);
    }
    geometry.computeBoundingBox();
    expect(geometry.boundingBox!.min.z).toBeCloseTo(-1.38);
    expect(geometry.boundingBox!.max.z).toBeCloseTo(2.7);
    geometry.dispose();
  });
  it('keeps concave notches and closed rings rather than making a rectangular skirt', () => {
    const coordinates=[point(0,0),point(20,0),point(20,10),point(10,10),point(10,20),point(0,20),point(0,0)];
    const boundary={...site,coordinates};
    const profile=measurePreparedEdges(boundary,review(boundary))!;
    expect(profile.samples.some(([lng,lat])=>Math.abs(lng-point(10,10)[0])<1e-10&&lat>point(10,10)[1])).toBe(true);
    const geo=createPreparedEdgeGeometry(profile,102,origin);
    const p=geo.getAttribute('position');
    for(let i=0;i<p.count;i++) expect(p.getX(i)>10.001&&p.getY(i)>10.001).toBe(false);
    geo.dispose();
  });
});
