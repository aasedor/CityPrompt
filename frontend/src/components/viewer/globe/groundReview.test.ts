import { describe, expect, it } from 'vitest';
import { describeGround, validPreparedLevel } from './groundReview';
import type { SharedSiteGroundLayout } from './sharedSiteGround';
import { validateSharedSiteGroundPass } from './sharedSiteGround';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

const layout: SharedSiteGroundLayout = { boundaryId: 'site', boundaryUpdatedAt: '', sourceSignature: 'test',
  boundaryCoordinates: [[0,0],[1,0],[1,1],[0,1]], grid: { west: 0, south: 0, columns: 3, rows: 2, stepLng: 1, stepLat: 1 } };
describe('ground review', () => {
  it('excludes off-site roof heights from the site range, but retains diagnostic samples', () => {
    const result = describeGround({ layout, heights: [100,101,150,100,101,150] });
    expect(result.min).toBe(100); expect(result.max).toBe(101);
    expect(result.cells[2]).toMatchObject({ inside: false, height: 150, jump: false });
  });
  it('highlights rejected bumps and slopes below the old two-metre diagnostic threshold', () => {
    const dx=2.5/metersPerDegLon(51),dy=2.5/METERS_PER_DEG_LAT;
    const grid:SharedSiteGroundLayout={...layout,boundaryCoordinates:[[-114,51],[-114+4*dx,51],[-114+4*dx,51+4*dy],[-114,51+4*dy]],
      grid:{west:-114,south:51,columns:5,rows:5,stepLng:dx,stepLat:dy}};
    const heights=Array(25).fill(100);heights[12]=100.8;
    expect(validateSharedSiteGroundPass(grid,heights).reason).toBe('discontinuity');
    expect(describeGround({layout:grid,heights}).cells[12].jump).toBe(true);
    heights[12]=100;
    expect(validateSharedSiteGroundPass(grid,heights).valid).toBe(true);
    expect(describeGround({layout:grid,heights}).cells.some(cell=>cell.jump)).toBe(false);
    const steep=heights.map((height,index)=>height+(index%5)*1.25);
    expect(validateSharedSiteGroundPass(grid,steep)).toMatchObject({valid:false,reason:'discontinuity'});
    expect(validateSharedSiteGroundPass(grid,steep).maxLocalResidualM).toBeCloseTo(0);
    expect(describeGround({layout:grid,heights:steep}).cells[12].jump).toBe(true);
  });
  it('does not invent missing heights or treat implausible samples as selectable levels', () => {
    const result = describeGround({ layout, heights: [null,NaN,200, -28000,null,200] });
    expect(result.min).toBeNull(); expect(result.max).toBeNull();
    expect(validPreparedLevel(NaN)).toBe(false); expect(validPreparedLevel(-28000)).toBe(false);
    expect(validPreparedLevel(1024.5)).toBe(true);
  });
});
