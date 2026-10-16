import { describe, expect, it } from 'vitest';
import { DETAIL_CATALOGUE, DETAIL_CATEGORIES, searchDetails } from './detailCatalogue';
import { detailPlacementSupport } from './safetyPlacement';

describe('traffic safety uses ordinary detail surfaces', () => {
  const pose = {lng:-114,lat:51,angle:90};
  const enabled = DETAIL_CATALOGUE.filter(a=>a.safety && a.safety.placement!=='sidewalk-attachment');
  it('places all 54 enabled variants without an authored road or site boundary', () => {
    expect(enabled).toHaveLength(54);
    for(const asset of enabled) expect(detailPlacementSupport(asset.id,pose,[]),asset.id).toEqual({ok:true});
  });
  it('keeps saved road-bound items usable when the original road is unavailable', () => {
    for(const asset of enabled) expect(detailPlacementSupport(asset.id,{...pose,support_zone_id:'old-road'},[]),asset.id).toEqual({ok:true});
  });
  it('groups all enabled safety families with existing traffic details', () => {
    const traffic = searchDetails('', 'Traffic & safety');
    expect(traffic.filter(a=>a.safety)).toHaveLength(54);
    expect(traffic.some(a=>a.id==='detail-flexible-bollard')).toBe(true);
    expect(searchDetails('', 'Curb bulbs')).toHaveLength(12);
    expect(searchDetails('RRFB', 'Traffic & safety')).toHaveLength(8);
    for(const category of ['RRFBs','TC curbs','Crosswalks','Overhead pedestrian flashers','Calgary safety additions']) expect(DETAIL_CATEGORIES).not.toContain(category);
  });
  it('retains the curb-bulb attachment block', () => {
    for(const asset of searchDetails('', 'Curb bulbs')) expect(detailPlacementSupport(asset.id,pose,[]).ok).toBe(false);
  });
});
