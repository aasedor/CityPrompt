import {describe,expect,it} from 'vitest';
import type {SiteZone} from '@/types';
import {PATHWAY_ASSETS,STREET_ASSETS} from './assetRegistry';
import {placementProblem,rectangleAt} from './geometry';
import {bufferLineToPolygon} from '@/utils/roadGeometry';
import {streetDrawingGeometry} from './streetDrawingGeometry';
import {snapStreetBoundaryPlacement} from './streetBoundaryPlacement';
import {snapPlacement} from './snapPlacement';
import {nativeStreetPilot} from '@/components/viewer/globe/nativeStreetPilot';
import {buildNativeStreetProgram} from '@/components/viewer/globe/nativeStreetProgram';

const ll=(x:number,y:number)=>[-114+x/(111320*Math.cos(51*Math.PI/180)),51+y/111320];
const zone=(id:string,zone_type:SiteZone['zone_type'],coordinates:number[][],properties:SiteZone['properties']={}):SiteZone=>({
  id,zone_type,coordinates,properties,project_id:'test',color:'#aaa',sort_order:0,created_at:'today',updated_at:'today',
});
const site=zone('site','site_boundary',rectangleAt(ll(0,0),150,150),{terrain_elevation_m:1000,community_3d_mask_existing_tiles:true});
const objects=['building','green_space'].map(type=>zone(type,type as SiteZone['zone_type'],rectangleAt(ll(0,0),30,30)));

describe('nonexclusive ground pathways',()=>{
  it.each(PATHWAY_ASSETS)('$label remains visible above a level building foundation without raising walls or steps',asset=>{
    const pilot=nativeStreetPilot(asset.model.variantId)!;
    const meshes=buildNativeStreetProgram(pilot.program!,pilot.widthM,pilot.fixtureLengthM,[{x:0,y:0},{x:0,y:20}]);
    // The shared level-site building contact caps its shallow footing at +4 cm.
    // Every path surface must clear that cap and remain within ground-finish scale.
    for(const {geometry} of meshes){
      geometry.computeBoundingBox();
      expect(geometry.boundingBox!.min.z).toBeGreaterThan(.04);
      expect(geometry.boundingBox!.max.z).toBeLessThan(.15);
      geometry.dispose();
    }
    expect(meshes.length).toBeGreaterThan(0);
  });
  it.each(PATHWAY_ASSETS)('$label can draw through building and park plots without moving the route',asset=>{
    const points=[ll(-40,0),ll(40,0)];
    const path=zone('path','road',bufferLineToPolygon(points,asset.sectionWidth),{...asset.properties,plan_centerline:points});
    for(const object of objects){
      expect(placementProblem(path.coordinates,[object],site,undefined,{allowStreetIntersections:true,properties:path.properties})).toBeNull();
      const drawn={...path,...streetDrawingGeometry(points,asset.properties,[site,object])};
      const result=snapStreetBoundaryPlacement(drawn,[site,object],site);
      expect(result.problem).toBeNull();
      expect(result.coordinates).toEqual(drawn.coordinates);
      const saved=JSON.parse(JSON.stringify({...drawn,coordinates:result.coordinates,properties:result.properties}));
      expect(snapStreetBoundaryPlacement(saved,[site,object,saved],site).problem).toBeNull();
    }
  });

  it.each(PATHWAY_ASSETS)('$label does not reserve a building or park plot when drawn first',asset=>{
    const line=[ll(-40,0),ll(40,0)];
    const path=zone('path','road',bufferLineToPolygon(line,asset.sectionWidth),{...asset.properties,plan_centerline:line});
    for(const object of objects){
      expect(placementProblem(object.coordinates,[path],site)).toBeNull();
      const snapped=snapPlacement(object.coordinates,[path],site,undefined,object.properties,object.zone_type);
      expect(snapped.problem).toBeNull();
      expect(snapped.coordinates).toEqual(object.coordinates);
    }
  });

  it('keeps the site boundary and real street footprints protected',()=>{
    const path=PATHWAY_ASSETS[0],road=STREET_ASSETS.find(a=>a.model.variantId==='student_quiet_residential_street_v1')!;
    const outside=bufferLineToPolygon([ll(-90,0),ll(40,0)],path.sectionWidth);
    expect(placementProblem(outside,objects,site,undefined,{properties:path.properties})).toContain('boundary');
    const coordinates=bufferLineToPolygon([ll(-40,0),ll(40,0)],road.sectionWidth);
    expect(placementProblem(coordinates,objects,site,undefined,{allowStreetIntersections:true,properties:road.properties})).toContain('overlaps');
    expect(placementProblem(objects[0].coordinates,[zone('road','road',coordinates,road.properties)],site)).toContain('sidewalks');
    // A label or zero-lane flag does not make a vehicle section a surface path.
    expect(placementProblem(coordinates,objects,site,undefined,{properties:{...road.properties,lane_count:0}})).toContain('overlaps');
  });
});
