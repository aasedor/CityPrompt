import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { STREET_ASSETS } from '@/features/pickPlace/assetRegistry';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { preparedPublicRoadMasks } from './preparedPublicRoads';

const ll = (x: number, y: number) => [x / 111320, y / 111320];
const boundary = {id:'site',zone_type:'site_boundary',is_active_boundary:true,
  coordinates:[ll(0,0),ll(100,0),ll(100,100),ll(0,100)],properties:{}} as SiteZone;
const asset = STREET_ASSETS.find(a => a.id === 'calgary_collector_street')!;
const road = (line: number[][]): SiteZone => ({id:'road',zone_type:'road',project_id:'p',color:'#888',sort_order:0,created_at:'',updated_at:'',
  coordinates:bufferLineToPolygon(line,20),properties:{...asset.properties,
    plan_centerline:line,connect_to_public_road:true}} as SiteZone);

it('clears constructed public-road bands beyond a prepared site without changing the saved road', () => {
  const outside = road([ll(50,30),ll(50,70),ll(65,112)]);
  const before = JSON.stringify(outside);
  const masks = preparedPublicRoadMasks([boundary,outside]);
  expect(masks).toHaveLength(1);
  expect(masks[0].id).toBe('road');
  expect(masks[0].coordinates).not.toEqual(outside.coordinates); // Collector setbacks remain Google ground.
  expect(Math.max(...masks[0].coordinates.map(p=>p[1]))).toBeGreaterThan(100/111320);
  expect(JSON.stringify(outside)).toBe(before);
});

it('does not clear interior, unrelated, invalid, opted-out or natural-site roads', () => {
  const crossing = road([ll(50,30),ll(50,112)]);
  for (const candidate of [road([ll(50,30),ll(50,90)]),road([ll(120,30),ll(120,90)]),
    road([ll(50,30),ll(50,145)]),{...crossing,properties:{...crossing.properties,connect_to_public_road:false}},
    {...crossing,properties:{...crossing.properties,community_3d_mask_existing_tiles:false}},
    {...crossing,properties:{connect_to_public_road:true}}]) {
    expect(preparedPublicRoadMasks([boundary,candidate])).toEqual([]);
  }
  expect(preparedPublicRoadMasks([crossing])).toEqual([]);
  expect(preparedPublicRoadMasks([{...boundary,properties:{community_3d_mask_existing_tiles:false}},crossing])).toEqual([]);
});
