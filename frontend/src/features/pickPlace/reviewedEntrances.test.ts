import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { placeAsset, placementProperties } from './catalogue';
import { reviewedEntranceForAsset } from './reviewedEntrances';
import { entranceWorldPoint, readBuildingEntrance, resolvePedestrianConnections } from './pedestrianConnections';
import { rectangleAt } from './geometry';
import { streetFacingDegrees } from './streetFacing';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const zone=(id:string,zone_type:SiteZone['zone_type'],coordinates:number[][],properties:SiteZone['properties']={}):SiteZone=>
  ({id,zone_type,coordinates,properties,project_id:'test',created_at:'now',updated_at:'now',color:'#aaa',sort_order:0});
const asset=placeAsset('clay_beltline_brick_midrise');
describe('reviewed native mixed-use entrance',()=>{
  it('requires the exact reviewed revision and keeps other buildings unconfigured',()=>{
    expect(reviewedEntranceForAsset(asset)?.fixedNative).toBe(true);
    expect(reviewedEntranceForAsset({...asset,model:{...asset.model,revision:'new-build'}})).toBeUndefined();
    expect(reviewedEntranceForAsset({...asset,model:{...asset.model,variantId:'sibling'}})).toBeUndefined();
    expect(reviewedEntranceForAsset(placeAsset('trial_sandstone_civic'))).toBeUndefined();
  });
  it.each([-38,38])('connects on side %s of a bent street and preserves native position on plot resize/reload',x=>{
    const line=[ll(0,-80),ll(0,40),ll(15,80)];
    const road=zone('road','road',bufferLineToPolygon(line,16),{road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',width:16,plan_centerline:line});
    const site={...zone('site','site_boundary',rectangleAt(ll(0,0),200,220)),is_active_boundary:true};
    const rotation=streetFacingDegrees(ll(x,0),[road]);
    const building=zone('building','building',rectangleAt(ll(x,0),39,39,rotation),placementProperties(asset));
    const zones=[site,road,building];
    const entrance=readBuildingEntrance(building,zones)!;
    expect(entrance.streetId).toBe('road');
    expect(resolvePedestrianConnections(zones)[0].status).toBe('connected');
    const resized=JSON.parse(JSON.stringify({...building,coordinates:rectangleAt(ll(x,0),48,48,rotation)}));
    const restored=readBuildingEntrance(resized,[site,road,resized])!;
    expect(restored).not.toBeNull();
    const before=entranceWorldPoint(building,entrance)!;
    const after=entranceWorldPoint(resized,restored)!;
    expect(after[0]).toBeCloseTo(before[0],8);expect(after[1]).toBeCloseTo(before[1],8);
    expect(resolvePedestrianConnections([site,road,resized])[0].status).toBe('connected');
    const repeated={...resized,properties:{...resized.properties,native_home_plot:true}};
    expect(readBuildingEntrance(repeated,[site,road,repeated])).toBeNull();
    const sibling={...resized,properties:{...resized.properties,development_selected_variant_id:'sibling'}};
    expect(readBuildingEntrance(sibling,[site,road,sibling])).toBeNull();
  });
});
