import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { streetFacingDegrees } from './streetFacing';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

const origin = [-114, 51];
const point = (x: number, y: number) => [origin[0] + x / metersPerDegLon(origin[1]), origin[1] + y / METERS_PER_DEG_LAT];
const context = (routes: number[][][], type = 'residential') => [{ properties: { _osm_context: {
  roads: routes.map((coordinates, osm_id) => ({ coordinates, osm_id, road_type: type })),
} } }] as SiteZone[];

describe('street-facing placement', () => {
  it.each([
    [[point(-40, -20), point(40, -20)], 0],
    [[point(-40, 20), point(40, 20)], 180],
    [[point(20, -40), point(20, 40)], 90],
    [[point(-20, -40), point(-20, 40)], 270],
  ] as const)('turns the native front toward the nearest street', (line, expected) => {
    expect(streetFacingDegrees(origin, context([[...line]]))).toBeCloseTo(expected, 4);
  });
  it('is stable under context order and ignores remote or inaccessible roads', () => {
    const zones = context([[point(-40, -20), point(40, -20)], [point(-40, 20), point(40, 20)]]);
    expect(streetFacingDegrees(origin, zones)).toBe(streetFacingDegrees(origin, [...zones].reverse()));
    expect(streetFacingDegrees(origin, context([[point(-40, 150), point(40, 150)]]), 37)).toBe(37);
    expect(streetFacingDegrees(origin, context([[point(-40, 10), point(40, 10)]], 'motorway'), 37)).toBe(37);
  });
  it('retains manual rotation without usable streets', () => {
    expect(streetFacingDegrees(origin, [], 24)).toBe(24);
    expect(streetFacingDegrees(origin, context([[point(0, 0), point(0, 0)]]), 24)).toBe(24);
  });
  it('prioritizes the authored neighbourhood street over a nearer mapped proposed road',()=>{
    const road={id:'street',zone_type:'road',coordinates:[],properties:{plan_centerline:[point(20,-40),point(20,40)]}} as unknown as SiteZone;
    expect(streetFacingDegrees(origin,[road,...context([[point(-40,-3),point(40,-3)]],'proposed')])).toBeCloseTo(90,4);
  });
  it('faces the street even when a footpath passes closer to the building', () => {
    const road = context([[point(-40, -20), point(40, -20)]]);
    const path = context([[point(5, -40), point(5, 40)]], 'footway');
    expect(streetFacingDegrees(origin, [...road, ...path])).toBeCloseTo(0, 4);
  });
});
