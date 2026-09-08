import { expect, it } from 'vitest';
import { alignStreetGroundLayout, anchoredStreetGroundHeight } from './streetGroundExtension';
import { sampleSharedSiteGround, type SharedSiteGroundSnapshot } from './sharedSiteGround';

it('preserves every original grid plane while measuring an external road corridor', () => {
  const anchor = { boundaryId: 'site', boundaryUpdatedAt: '', sourceSignature: 'source', signature: 'stable',
    boundaryCoordinates: [[0,0],[2,0],[2,2],[0,2]], grid: {west:0,south:0,stepLng:1,stepLat:1,columns:3,rows:3},
    heights: [10,11,13,12,15,14,16,17,18] } as SharedSiteGroundSnapshot;
  const extension = alignStreetGroundLayout({...anchor, boundaryCoordinates:[[1.2,0.2],[4.2,0.2],[4.2,1.8],[1.2,1.8]]}, anchor)!;
  expect(extension.grid).toMatchObject({west:1,south:0,columns:5,rows:3,stepLng:1,stepLat:1});
  const heights = Array.from({length:15}, (_, i) => anchoredStreetGroundHeight(anchor, 1+i%5, Math.floor(i/5)) ?? 20);
  const snapshot = {...anchor,...extension,heights};
  for (const [x,y] of [[1.3,0.3],[1.7,0.6],[1.5,1.5]]) expect(sampleSharedSiteGround(snapshot,x,y)).toBeCloseTo(sampleSharedSiteGround(anchor,x,y)!,10);
  expect(anchoredStreetGroundHeight(anchor,3,1)).toBeNull();
  expect(anchoredStreetGroundHeight(anchor,1.2,1)).toBeNull();
});
