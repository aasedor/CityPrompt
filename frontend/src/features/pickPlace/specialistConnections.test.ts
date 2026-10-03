import {describe,it,expect} from 'vitest';
import type {SiteZone} from '@/types';
import {bufferLineToPolygon} from '@/utils/roadGeometry';
import {specialistConnectionProblem} from './specialistConnections';
import {CANAL_VARIANT,BRIDGE_VARIANT} from '@/components/viewer/globe/specialistStreetProgram';
function street(id:string,line:number[][],variant:string,width=36):SiteZone{
  const coords=line.map(([x,y])=>[x/111320,y/111320]);
  return {id,project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:bufferLineToPolygon(coords,width),properties:{width,plan_centerline:coords,road_selected_variant_id:variant}} as SiteZone;
}
describe('specialist topology',()=>{
  const canal=street('c',[[0,0],[0,160]],CANAL_VARIANT),bridge=street('b',[[0,0],[0,260]],BRIDGE_VARIANT);
  it('permits outer bank edge access and rejects an asphalt crossing',()=>{
    expect(specialistConnectionProblem(street('r',[[60,90],[18,90]],'local',8),[canal])).toBeNull();
    expect(specialistConnectionProblem(street('r',[[60,90],[17.7,90]],'local',8),[canal])).toBeNull();
    expect(specialistConnectionProblem(street('r',[[60,90],[16,90]],'local',8),[canal])).toMatch(/outer bank/);
    expect(specialistConnectionProblem(street('r',[[-60,90],[60,90]],'local',8),[canal])).toMatch(/outer bank/);
    expect(specialistConnectionProblem(canal,[street('r',[[-60,90],[60,90]],'local',8)])).toMatch(/outer bank/);
  });
  it('allows an underpass in the clear opening but rejects abutment/approach collisions',()=>{
    expect(specialistConnectionProblem(street('r',[[-60,130],[60,130]],'local',18),[bridge])).toBeNull();
    expect(specialistConnectionProblem(street('r',[[-60,85],[60,85]],'local',18),[bridge])).toMatch(/abutments/);
    expect(specialistConnectionProblem(street('r',[[0,-70],[0,0]],'local',18),[bridge])).toBeNull();
  });
  it('rejects two intersecting rigid bridges instead of removing either structure',()=>{
    const crossing=street('b2',[[-130,130],[130,130]],BRIDGE_VARIANT);
    expect(specialistConnectionProblem(crossing,[bridge])).toMatch(/Bridge-to-bridge/);
    expect(specialistConnectionProblem(bridge,[crossing])).toMatch(/Bridge-to-bridge/);
    expect(specialistConnectionProblem(street('end',[[0,-260],[0,0]],BRIDGE_VARIANT),[bridge])).toBeNull();
  });
});
