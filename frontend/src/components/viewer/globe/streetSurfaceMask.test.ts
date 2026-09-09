import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { STREET_ASSETS } from '@/features/pickPlace/assetRegistry';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { streetSurfaceMaskZone, streetSectionOwnsGround } from './streetSurfaceMask';

it('retains the source setback outside the constructed collector and does not change its saved width',()=>{
  const asset = STREET_ASSETS.find(a=>a.id==='calgary_collector_street')!;
  const line = [[0,0],[100/111320,0]];
  const zone = {id:'road',project_id:'project',color:'#888',sort_order:0,created_at:'',updated_at:'',
    properties:{...asset.properties,plan_centerline:line},coordinates:bufferLineToPolygon(line,20),zone_type:'road'} as SiteZone;
  const mask=streetSurfaceMaskZone(zone);
  const ys=mask.coordinates.map(p=>p[1]*111320);
  expect(Math.max(...ys)-Math.min(...ys)).toBeCloseTo(19.4,2);
  expect(zone.properties?.width).toBe(20);
  expect(asset.properties.community_3d_mask_existing_tiles).toBe(true);
});

it.each(STREET_ASSETS)('gives $label one ground surface, even before a public-road connection', asset => {
  const line=[[-114,51],[-113.999,51]];
  const zone: SiteZone={id:'road',project_id:'project',color:'#888',sort_order:0,created_at:'',updated_at:'',zone_type:'road',properties:{...asset.properties,plan_centerline:line},coordinates:bufferLineToPolygon(line,asset.sectionWidth)};
  expect(streetSectionOwnsGround(zone)).toBe(true);
  expect(streetSectionOwnsGround({...zone,properties:{}})).toBe(false);
  expect(streetSectionOwnsGround({...zone,coordinates:[]})).toBe(false);
});
