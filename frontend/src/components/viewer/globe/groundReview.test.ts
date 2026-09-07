import { describe, expect, it } from 'vitest';
import { describeGround, validPreparedLevel } from './groundReview';
import type { SharedSiteGroundLayout } from './sharedSiteGround';

const layout: SharedSiteGroundLayout = { boundaryId: 'site', boundaryUpdatedAt: '', sourceSignature: 'test',
  boundaryCoordinates: [[0,0],[1,0],[1,1],[0,1]], grid: { west: 0, south: 0, columns: 3, rows: 2, stepLng: 1, stepLat: 1 } };
describe('ground review', () => {
  it('excludes off-site roof heights from the site range, but retains diagnostic samples', () => {
    const result = describeGround({ layout, heights: [100,101,150,100,101,150] });
    expect(result.min).toBe(100); expect(result.max).toBe(101);
    expect(result.cells[2]).toMatchObject({ inside: false, height: 150, jump: true });
  });
  it('does not invent missing heights or treat implausible samples as selectable levels', () => {
    const result = describeGround({ layout, heights: [null,NaN,200, -28000,null,200] });
    expect(result.min).toBeNull(); expect(result.max).toBeNull();
    expect(validPreparedLevel(NaN)).toBe(false); expect(validPreparedLevel(-28000)).toBe(false);
    expect(validPreparedLevel(1024.5)).toBe(true);
  });
});
