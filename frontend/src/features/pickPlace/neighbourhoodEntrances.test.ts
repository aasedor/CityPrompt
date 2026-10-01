import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { placeAsset, placementProperties } from './catalogue';
import { reviewedEntranceForAsset } from './reviewedEntrances';
import { entranceWorldPoint, readBuildingEntrance } from './pedestrianConnections';
import { rectangleAt } from './geometry';

describe('neighbourhood building entrance measurements', () => {
  it('keeps the library approach on its native threshold when its plot grows', () => {
    const library = placeAsset('clay_mass_timber_biophilic_barn');
    const original = { id: 'library', zone_type: 'building', coordinates: rectangleAt([-114,51],40,37,15),
      properties: placementProperties(library) } as SiteZone;
    const larger = {...original, coordinates: rectangleAt([-114,51],48,43,15)};
    const before = readBuildingEntrance(original)!;
    const after = readBuildingEntrance(larger)!;
    expect(before).toMatchObject({xM:0,yM:-16.3,widthM:2.4,fixedNative:true,scaleWithPlot:false});
    const a=entranceWorldPoint(original,before)!;const b=entranceWorldPoint(larger,after)!;
    expect(b[0]).toBeCloseTo(a[0],8);expect(b[1]).toBeCloseTo(a[1],8);
    expect(reviewedEntranceForAsset({...library,model:{...library.model,revision:'unreviewed'}})).toBeUndefined();
    expect(reviewedEntranceForAsset({...library,model:{...library.model,variantId:'sibling'}})).toBeUndefined();
  });
  it('locks the clear café threshold to the measured complete-assembly centre', () => {
    const cafe = placeAsset('clay_parisian_corner_cafe_culture');
    const original = {id:'cafe',zone_type:'building',coordinates:rectangleAt([-114,51],49,48,20),
      properties:placementProperties(cafe)} as SiteZone;
    const larger = {...original,coordinates:rectangleAt([-114,51],58,56,20)};
    const before=readBuildingEntrance(original)!;const after=readBuildingEntrance(larger)!;
    expect(before).toMatchObject({xM:-1.976301193,yM:-19.448032379,widthM:2.4,fixedNative:true,scaleWithPlot:false});
    const a=entranceWorldPoint(original,before)!;const b=entranceWorldPoint(larger,after)!;
    expect(b[0]).toBeCloseTo(a[0],8);expect(b[1]).toBeCloseTo(a[1],8);
    expect(reviewedEntranceForAsset({...cafe,model:{...cafe.model,revision:'unreviewed'}})).toBeUndefined();
  });
});
