import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { publicRoadConnectionFits } from './publicRoadConnection';

const ll = (x:number,y:number) => [x/111320,y/111320];
const boundary = {coordinates:[ll(0,0),ll(100,0),ll(100,100),ll(0,100)]} as SiteZone;
const zone = {id:'road',project_id:'project',zone_type:'road',coordinates:[],color:'#888',sort_order:0,
  created_at:'',updated_at:'',properties:{connect_to_public_road:true}} as SiteZone;
it('allows an explicit short one-ended public connection, not an unrelated outside road',()=>{
  const coords = (a:number,b:number) => bufferLineToPolygon([ll(a,50),ll(b,50)],20);
  expect(publicRoadConnectionFits(zone,coords(10,110),boundary)).toBe(true);
  expect(publicRoadConnectionFits(zone,coords(10,140),boundary)).toBe(false);
  expect(publicRoadConnectionFits(zone,coords(-10,110),boundary)).toBe(false);
  expect(publicRoadConnectionFits({...zone,zone_type:'building'},coords(10,110),boundary)).toBe(false);
  expect(publicRoadConnectionFits({...zone,properties:{}},coords(10,110),boundary)).toBe(false);
});
