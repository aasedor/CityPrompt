import { expect, it } from 'vitest';
import { preparedStreetElevation } from './preparedStreetTransition';
const site={ring:[[0,0],[100/111320,0],[100/111320,100/111320],[0,100/111320]] as [number,number][],elevation:105};
it('keeps the inside road at the declared site level and meets outside ground continuously',()=>{
  expect(preparedStreetElevation(site,50/111320,50/111320,100)).toBe(105);
  expect(preparedStreetElevation(site,100/111320,50/111320,100)).toBeCloseTo(105,5);
  expect(preparedStreetElevation(site,105/111320,50/111320,100)).toBeCloseTo(102.5,5);
  expect(preparedStreetElevation(site,112/111320,50/111320,100)).toBe(100);
  expect(preparedStreetElevation(undefined,50/111320,50/111320,100)).toBe(100);
});
