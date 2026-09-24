import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { placeAsset } from './catalogue';
import { rectangleAt, rectangleDimensions, resizeRectangleCorner, placementProblem } from './geometry';

const center=[-114.04677,51.04542];
const zone=(coords:number[][],type='building',id='z')=>({id,zone_type:type,coordinates:coords} as SiteZone);
describe('pick and reshape geometry',()=>{
  it.each([0,37,90,175])('keeps metre dimensions at latitude 51 at %s degrees',angle=>{
    const d=rectangleDimensions(rectangleAt(center,36,16,angle));
    expect(d.width).toBeCloseTo(36,4);expect(d.depth).toBeCloseTo(16,4);
    expect(d.degrees).toBeCloseTo(angle,4);
  });
  it.each([0,1,2,3])('corner %s keeps its opposite fixed and cannot flatten a house',corner=>{
    const coords=rectangleAt(center,36,16,35),fixed=coords[(corner+2)%4];
    const resized=resizeRectangleCorner(coords,corner,fixed,placeAsset('infill_home'));
    const d=rectangleDimensions(resized);
    expect(d.width).toBeCloseTo(12,3);expect(d.depth).toBeCloseTo(16,3);
    expect(d.degrees).toBeCloseTo(35,3);
    expect(resized[(corner+2)%4][0]).toBeCloseTo(fixed[0],8);
    expect(resized[(corner+2)%4][1]).toBeCloseTo(fixed[1],8);
  });
  it('prevents crossing a concave boundary even if every corner fits',()=>{
    const c=rectangleAt(center,100,100);
    const inset=rectangleAt(center,10,100);
    const notch=[c[0],c[1],c[2],[inset[2][0],c[2][1]],[inset[2][0],center[1]],[inset[3][0],center[1]],[inset[3][0],c[3][1]],c[3]];
    expect(placementProblem(rectangleAt(center,40,40),[],zone(notch,'site_boundary'))).toMatch(/boundary/);
  });
  it('rejects overlaps, allows movement of the same object, and permits clear space',()=>{
    const coords=rectangleAt(center,12,16),boundary=zone(rectangleAt(center,90,93),'site_boundary');
    expect(placementProblem(coords,[zone(coords)],boundary)).toMatch(/overlaps/);
    expect(placementProblem(coords,[zone(coords)],boundary,'z')).toBeNull();
    expect(placementProblem(coords,[],boundary)).toBeNull();
    expect(placementProblem(rectangleAt(center,100,100),[],boundary)).toMatch(/boundary/);
  });
  it('identifies the overlapping neighbour by its saved name or catalogue label',()=>{
    const coords=rectangleAt(center,20,20);
    expect(placementProblem(coords,[{...zone(coords),name:'Corner homes'}])).toContain('overlaps Corner homes');
    expect(placementProblem(coords,[{...zone(coords,'green_space'),properties:{pick_place_asset:'neighbourhood_park'}}])).toContain('overlaps Neighbourhood park');
  });
});
