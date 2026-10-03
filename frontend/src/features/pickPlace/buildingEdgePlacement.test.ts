import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { CATALOGUE_ASSETS } from './assetRegistry';
import { placeAsset, placementProperties } from './catalogue';
import { placementProblem, rectangleAt, rectangleDimensions } from './geometry';
import { buildingEdgeContract, buildingPlacementEnvelope } from './buildingPlacementEdges';
import { snapPlacement } from './snapPlacement';
import { storeyProgramHeight } from './buildingStoreyProgram';
import { resolvePedestrianConnections } from './pedestrianConnections';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import edges from '@/data/buildingPlacementEdges.json';

const ll=(x:number,y:number):[number,number]=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const building=(id:string,x=0,y=0,angle=0):SiteZone=>{
  const asset=placeAsset(id);
  return {id:`${id}:${x}:${y}`,zone_type:'building',coordinates:rectangleAt(ll(x,y),asset.width,asset.depth,angle),properties:placementProperties(asset)} as SiteZone;
};
const site={id:'site',zone_type:'site_boundary',coordinates:rectangleAt(ll(0,0),500,500)} as SiteZone;
const soho='validation_cast_iron_italianate';
const check=(z:SiteZone,others:SiteZone[])=>placementProblem(z.coordinates,others,site,z.id,{properties:z.properties});
const xCenter=(ring:number[][])=>(rectangleDimensions(ring).center[0]+114)*metersPerDegLon(51);
const yCenter=(ring:number[][])=>(rectangleDimensions(ring).center[1]-51)*METERS_PER_DEG_LAT;

describe('reviewed building contact envelopes',()=>{
  it('locks every current building to its exact measured asset revision',()=>{
    const buildings=CATALOGUE_ASSETS.filter(a=>a.kind==='object'&&a.zoneType==='building');
    expect(new Set(edges.buildings.map(r=>r.assetId)).size).toBe(buildings.length);
    for(const asset of buildings){
      if(asset.kind!=='object')throw new Error('Expected object');
      const contract=buildingEdgeContract(building(asset.id));
      expect(contract,asset.label).not.toBeNull();
      expect(contract?.revision).toBe(asset.model.revision);
      expect(contract?.nativeWidthM).toBeCloseTo(asset.nativeDimensions![0],5);
      expect(contract?.nativeDepthM).toBeCloseTo(asset.nativeDimensions![1],5);
      const stable=(value:unknown)=>JSON.parse(JSON.stringify(value,(_key,v)=>typeof v==='number'?Math.round(v*1e8)/1e8:v));
      expect(stable(contract?.storeyProgram)).toEqual(stable(asset.storeyProgram ?? null));
      expect(stable(contract?.footprintProgram)).toEqual(stable(asset.footprintProgram ?? null));
    }
  });
  it('closes a small gap between attached buildings while keeping plot and model sizes',()=>{
    const other=building(soho),width=buildingEdgeContract(other)!.width;
    const moving=building(soho,width+.4);
    expect(check(moving,[other])).toBeNull();
    const result=snapPlacement(moving.coordinates,[other],site,undefined,moving.properties);
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    expect(xCenter(result.coordinates)).toBeCloseTo(width+.02,2);
    expect(rectangleDimensions(result.coordinates).width).toBeCloseTo(placeAsset(soho).width,5);
    expect(snapPlacement(result.coordinates,[other],site,undefined,moving.properties).snapped).toBe(false);
    expect(check(building(soho,width-.2),[other])).toContain('overlaps');
  });
  it('keeps attached placement accurate when both buildings are rotated',()=>{
    const angle=37,rad=angle*Math.PI/180,other=building(soho,0,0,angle),w=buildingEdgeContract(other)!.width;
    const moving=building(soho,(w+.4)*Math.cos(rad),(w+.4)*Math.sin(rad),angle);
    const result=snapPlacement(moving.coordinates,[other],site,undefined,moving.properties);
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    expect(Math.hypot(xCenter(result.coordinates),yCenter(result.coordinates))).toBeCloseTo(w+.02,2);
    expect(rectangleDimensions(result.coordinates).degrees).toBeCloseTo(angle,4);
  });
  it('retains detached side space and the Montreal duplex left entrance',()=>{
    const detached=building('trial_postwar_bungalow'),d=rectangleDimensions(buildingPlacementEnvelope(detached));
    expect(d.width).toBeCloseTo(placeAsset('trial_postwar_bungalow').width,4);
    expect(check(building('trial_postwar_bungalow',d.width-.2),[detached])).toContain('overlaps');
    const duplex=building('clay_montreal_plateau_duplex'),c=buildingEdgeContract(duplex)!;
    const env=buildingPlacementEnvelope(duplex);
    expect((env[0][0]+114)*metersPerDegLon(51)).toBeCloseTo(-placeAsset('clay_montreal_plateau_duplex').width/2,3);
    expect((env[1][0]+114)*metersPerDegLon(51)).toBeCloseTo(c.width/2,3);
  });
  it.each([0,90,180])('snaps the building front to the full sidewalk edge at %s degrees',angle=>{
    const a=building(soho),depth=buildingEdgeContract(a)!.depth,rad=angle*Math.PI/180;
    const road={id:'road',name:'Main street',zone_type:'road',properties:{width:20},coordinates:rectangleAt(ll(0,0),150,20,angle)} as SiteZone;
    const y=10+depth/2+.4,moving=building(soho,-y*Math.sin(rad),y*Math.cos(rad),angle);
    const result=snapPlacement(moving.coordinates,[road],site,undefined,moving.properties);
    expect(result.problem).toBeNull();expect(result.snapped).toBe(true);
    expect(Math.hypot(xCenter(result.coordinates),yCenter(result.coordinates))).toBeCloseTo(10+depth/2+.02,2);
    expect(check({...moving,coordinates:result.coordinates},[road])).toBeNull();
    const overlap=building(soho,-(y-.6)*Math.sin(rad),(y-.6)*Math.cos(rad),angle);
    expect(check(overlap,[road])).toContain('sidewalks');
    expect(placementProblem(road.coordinates,[{...moving,coordinates:result.coordinates}],site,undefined,{allowStreetIntersections:true})).toBeNull();
  });
  it('uses scaled bounds without changing the saved plot and survives a JSON reload',()=>{
    const original=building('trial_postwar_bungalow'),before=JSON.stringify(original);
    const scaled={...original,properties:{...original.properties,building_footprint_scale:1.15}};
    const contract=buildingEdgeContract(scaled)!;
    expect(contract.depth).toBeCloseTo(buildingEdgeContract(original)!.depth*1.15,5);
    const env=buildingPlacementEnvelope(scaled);
    expect(buildingPlacementEnvelope(JSON.parse(JSON.stringify(scaled)))).toEqual(env);
    expect(JSON.stringify(original)).toBe(before);
    expect(scaled.coordinates).toBe(original.coordinates);
  });
  it('snaps both a side edge and the street frontage in one operation',()=>{
    const c=buildingEdgeContract(building(soho))!;
    const road={id:'road',zone_type:'road',properties:{width:20},coordinates:rectangleAt(ll(0,0),150,20)} as SiteZone;
    const other=building(soho,0,10+c.depth/2+.02),moving=building(soho,c.width+.4,10+c.depth/2+.4);
    const result=snapPlacement(moving.coordinates,[other,road],site,undefined,moving.properties);
    expect(result.problem).toBeNull();
    expect(xCenter(result.coordinates)).toBeCloseTo(c.width+.02,2);
    expect(yCenter(result.coordinates)).toBeCloseTo(10+c.depth/2+.02,2);
  });
  it.each(['trial_postwar_bungalow','trial_edwardian_foursquare','validation_clapboard_north_end','clay_vancouver_balcony_podium_tower'])(
    'keeps %s contact bounds unchanged across its supported heights',id=>{
      const z=building(id),program=placeAsset(id).storeyProgram!;
      for(const floors of [program.minStoreys,program.maxStoreys]){
        const taller={...z,properties:{...z.properties,floor_count:floors,development_height_override_m:storeyProgramHeight(program,floors)}};
        expect(buildingEdgeContract(taller)).not.toBeNull();
        expect(buildingPlacementEnvelope(taller)).toEqual(buildingPlacementEnvelope(z));
      }
    });
  it('rejects a footprint expansion into the street without mutating the saved building',()=>{
    const z=building('trial_postwar_bungalow'),depth=buildingEdgeContract(z)!.depth;
    z.coordinates=rectangleAt(ll(0,10+depth/2+.02),15,20);
    const road={id:'road',zone_type:'road',coordinates:rectangleAt(ll(0,0),100,20),properties:{width:20}} as SiteZone;
    expect(check(z,[road])).toBeNull();
    expect(check({...z,properties:{...z.properties,building_footprint_scale:1.15}},[road])).toContain('sidewalks');
    expect(z.properties?.building_footprint_scale).toBe(1);
  });
  it('accounts for the Vancouver plot-driven horizontal fit, including its largest footprint',()=>{
    const z=building('clay_vancouver_balcony_podium_tower');
    for(const [w,d] of [[51.1,43.1],[52,44],[57.5,47.5]]){
      const resized={...z,coordinates:rectangleAt(ll(0,0),w,d)};
      const contract=buildingEdgeContract(resized)!;
      const scale=Math.round(Math.min(w/contract.nativeWidthM,d/contract.nativeDepthM,1.2)*1e5)/1e5;
      expect(contract.width).toBeCloseTo(contract.nativeWidthM*scale,5);
      expect(contract.depth).toBeCloseTo(contract.nativeDepthM*scale,5);
    }
  });
  it('connects a current native house directly to the sidewalk with no invented 2.5 m gap',()=>{
    const line=[ll(-100,0),ll(100,0)];
    const road:SiteZone={id:'road',project_id:'test',color:'#888',sort_order:0,created_at:'',updated_at:'',zone_type:'road',coordinates:bufferLineToPolygon(line,16),properties:{road_archetype_id:'calgary_local',road_selected_variant_id:'calgary_local_v0',width:16,plan_centerline:line}};
    const z=building('trial_postwar_bungalow',0,8+8.025+.2);
    const boundary={...site,is_active_boundary:true};
    const result=snapPlacement(z.coordinates,[boundary,road],boundary,undefined,z.properties);
    expect(result.problem).toBeNull();
    expect(yCenter(result.coordinates)).toBeCloseTo(8+8.025+.02,2);
    const plan=resolvePedestrianConnections([boundary,road,{...z,coordinates:result.coordinates}]).find(p=>p.ownerId===z.id);
    expect(plan?.status).toBe('connected');
  });
  it('falls back to the saved plot for unverified, repeated or non-rectangular geometry',()=>{
    const z=building(soho);
    for(const p of [{pick_place_model_revision:'unknown'},{native_home_plot:true},{development_selected_variant_id:'unknown'},{development_height_override_m:999},{building_footprint_scale:3}]){
      expect(buildingPlacementEnvelope({...z,properties:{...z.properties,...p}})).toBe(z.coordinates);
    }
    expect(buildingPlacementEnvelope({...z,zone_type:'parking'})).toBe(z.coordinates);
    const custom={...z,coordinates:[z.coordinates[0],ll(50,20),z.coordinates[2],z.coordinates[3]]};
    expect(buildingPlacementEnvelope(custom)).toBe(custom.coordinates);
  });
  it('still requires the complete saved plot to fit the site and preserves failed placements',()=>{
    const z=building(soho),tiny={...site,coordinates:rectangleAt(ll(0,0),10,10)};
    const result=snapPlacement(z.coordinates,[],tiny,undefined,z.properties);
    expect(result.problem).toContain('site boundary');expect(result.coordinates).toEqual(z.coordinates);
    expect(result.snapped).toBe(false);
  });
});
