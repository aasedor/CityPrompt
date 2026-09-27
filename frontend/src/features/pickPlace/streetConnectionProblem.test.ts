import { describe,it,expect } from 'vitest';
import type { SiteZone } from '@/types';
import { CLASSROOM_CHOICES } from './canonicalCatalogue';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { streetConnectionProblem } from './streetConnectionProblem';
const street=(id:string,variant:string,points:number[][]):SiteZone=>{
  const asset=CLASSROOM_CHOICES.flatMap(c=>c.placements).find(a=>a.model.variantId===variant)!;
  const line=points.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:bufferLineToPolygon(line,Number(asset.properties.width)),properties:{...asset.properties,plan_centerline:line}};
};
describe('ordinary route junction preflight',()=>{
  const main=street('main','student_main_street_v1',[[-120,0],[120,0]]);
  it.each(['student_quiet_residential_street_v1','student_planted_shared_lane_v1','student_market_street_v1'])('accepts complete native T and X joins for %s',variant=>{
    expect(streetConnectionProblem(street('a',variant,[[0,0],[0,100]]),[main])).toBeNull();
    expect(streetConnectionProblem(street('a',variant,[[0,-100],[0,100]]),[main])).toBeNull();
  });
  it('rejects shallow crossings, short arms and overlapping parallel duplicates',()=>{
    expect(streetConnectionProblem(street('a','student_quiet_residential_street_v1',[[-100,-20],[100,20]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_quiet_residential_street_v1',[[115,-100],[115,100]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[-120,3],[120,3]]),[main])).toMatch(/junction/);
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[120,0],[240,0]]),[main])).toBeNull();
    expect(streetConnectionProblem(street('a','student_main_street_v1',[[-120,50],[120,50]]),[main])).toBeNull();
  });
  it('checks the complete node when individually valid pairs have incompatible opposing sections',()=>{
    const north=street('north','student_planted_shared_lane_v1',[[0,0],[0,100]]);
    const south=street('south','student_quiet_residential_street_v1',[[0,-100],[0,0]]);
    expect(streetConnectionProblem(north,[main])).toBeNull();
    expect(streetConnectionProblem(south,[main])).toBeNull();
    expect(streetConnectionProblem(south,[main,north])).toMatch(/junction/);
  });
});
