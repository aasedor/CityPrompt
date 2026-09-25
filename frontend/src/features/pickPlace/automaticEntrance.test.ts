import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { rectangleAt } from './geometry';
import { placeAsset, placementProperties } from './catalogue';
import { readBuildingEntrance, resolvePedestrianConnections } from './pedestrianConnections';
import { streetConnectionCaptureUserData } from '@/components/viewer/globe/pedestrianCapture';
import { streetFacingDegrees } from './streetFacing';
import { snapBuildingMove, snapPlacement } from './snapPlacement';
const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const zone=(id:string,zone_type:SiteZone['zone_type'],coordinates:number[][],properties:SiteZone['properties']={}):SiteZone=>
  ({id,zone_type,coordinates,properties,project_id:'test',created_at:'now',updated_at:'now',color:'#aaa',sort_order:0});
const street=(id:string,x:number)=>{
  const line=[ll(x,-50),ll(x,50)];
  return zone(id,'road',bufferLineToPolygon(line,16),{road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',width:16,plan_centerline:line});
};
const site={...zone('site','site_boundary',rectangleAt(ll(0,0),160,160)),is_active_boundary:true};
const home=(x:number,streets:SiteZone[])=>zone('home','building',rectangleAt(ll(x,0),12,16,streetFacingDegrees(ll(x,0),streets)),placementProperties(placeAsset('infill_home')));
describe('automatic native entrance connections',()=>{
  it.each([-20,20])('connects a freshly placed home on side %s without opening Connections',x=>{
    const road=street('road',0), house=home(x,[road]), zones=[site,road,house];
    expect(readBuildingEntrance(house,zones)?.streetId).toBe('road');
    expect(resolvePedestrianConnections(zones).find(p=>p.ownerId==='home')?.status).toBe('connected');
    expect(streetConnectionCaptureUserData(house,zones)).not.toBeNull();
  });
  it('retargets after a move and restoring coordinates restores the original route',()=>{
    const a=street('a',-35),b=street('b',35),house=home(-15,[a,b]);
    const zones=[site,a,b,house];
    expect(readBuildingEntrance(house,zones)?.streetId).toBe('a');
    const moved={...house,coordinates:rectangleAt(ll(15,0),12,16,90)};
    expect(readBuildingEntrance(moved,[site,a,b,moved])?.streetId).toBe('b');
    expect(readBuildingEntrance(house,zones)?.streetId).toBe('a');
  });
  it('snaps away from the carriageway and preserves a neighbour’s existing walkway',()=>{
    const road=street('road',0),house=home(-20,[road]),zones=[site,road,house];
    const moved=home(-19,[road]);moved.id='moving';
    const result=snapBuildingMove(moved,rectangleAt(ll(-18,0),12,16),[...zones,moved],site);
    expect(result.problem).toBeNull();
    const plans=resolvePedestrianConnections([...zones,{...moved,coordinates:result.coordinates}]);
    expect(plans.every(plan=>plan.status==='connected')).toBe(true);
    const onRoad=snapPlacement(rectangleAt(ll(0,20),12,16,90),zones,site);
    expect(onRoad.problem).toBeNull();
    const center=onRoad.coordinates.reduce((a,p)=>[a[0]+p[0]/4,a[1]+p[1]/4],[0,0]);
    expect(Math.abs((center[0]+114)*metersPerDegLon(51))).toBeGreaterThan(18);
  });
  it('waits for a nearby sidewalk and responds when a street is added',()=>{
    const house=home(20,[]),road=street('road',0);
    expect(readBuildingEntrance(house,[site,house])).toBeNull();
    expect(readBuildingEntrance(house,[site,house,road])?.streetId).toBe('road');
  });
  it('preserves manually chosen targets and does not invent entrances for other variants or repetitions',()=>{
    const road=street('road',0),house=home(20,[road]);
    const existing=readBuildingEntrance(house)!;
    const manual={...house,properties:{...house.properties,pedestrian_building_entrance:{...existing,automatic:false,streetId:'chosen'}}};
    expect(readBuildingEntrance(manual,[site,road,manual])?.streetId).toBe('chosen');
    const changed={...house,properties:{...house.properties,development_selected_variant_id:'other'}};
    expect(readBuildingEntrance(changed,[site,road,changed])).toBeNull();
    const repeated={...house,properties:{...house.properties,native_home_plot:true},coordinates:rectangleAt(ll(20,0),36,16)};
    expect(readBuildingEntrance(repeated,[site,road,repeated])).toBeNull();
    expect(placementProperties(placeAsset('craftsman_bungalow')).pedestrian_building_entrance).toBeUndefined();
  });
});
