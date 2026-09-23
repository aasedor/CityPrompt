import { expect, it } from 'vitest';
import { completeStreetStation, preparedStreetElevation, preparedStreetPreview } from './preparedStreetTransition';
import { buildRibbonBandGeometry, stationNormals } from './streetMesh3D';
const site={ring:[[0,0],[100/111320,0],[100/111320,100/111320],[0,100/111320]] as [number,number][],elevation:105};
it('keeps the inside road at the declared site level and meets outside ground continuously',()=>{
  expect(preparedStreetElevation(site,50/111320,50/111320,100)).toBe(105);
  expect(preparedStreetElevation(site,100/111320,50/111320,100)).toBeCloseTo(105,5);
  expect(preparedStreetElevation(site,105/111320,50/111320,100)).toBeCloseTo(102.5,5);
  expect(preparedStreetElevation(site,112/111320,50/111320,100)).toBe(100);
  expect(preparedStreetElevation(undefined,50/111320,50/111320,100)).toBe(100);
});

it('seats cold-load pavement and both sidewalk edges on the prepared datum before any raycast', () => {
  const points = [{x:20,y:50},{x:50,y:50},{x:90,y:50}];
  const frame = 100;
  const profile = preparedStreetPreview(site, points, stationNormals(points), {lng:0,lat:0}, 5, frame);
  for (const [start,end] of [[-5,-3],[-3,3],[3,5]]) {
    const geometry = buildRibbonBandGeometry(points,start,end,.025,profile)!;
    const positions = geometry.getAttribute('position');
    for (let index=0;index<positions.count;index++) expect(frame+positions.getZ(index)).toBeCloseTo(105.025,4);
    geometry.dispose();
  }
  const moved = preparedStreetPreview({...site,elevation:108},points,stationNormals(points),{lng:0,lat:0},5,frame);
  expect(moved[0].centerZ).toBe(8);
});

it('requires real finite measurements across the whole outside station', () => {
  expect(completeStreetStation({center:100,left:null,right:100})).toBe(false);
  expect(completeStreetStation({center:100,left:NaN,right:100})).toBe(false);
  expect(completeStreetStation({center:100,left:100.1,right:99.9})).toBe(true);
});
