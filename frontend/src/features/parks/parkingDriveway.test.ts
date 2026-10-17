import { describe, expect, it } from 'vitest';
import { parkingDriveway, nearestParkingRoad, parkingRoads, type ParkingRoad } from './parkingDriveway';
import type { PavingSurface } from './pavingSurfaces';
import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';

const ll=(x:number,y:number)=>[-114+x/metersPerDegLon(51),51+y/METERS_PER_DEG_LAT];
const rect=(x:number,y:number,w:number,h:number)=>[[x,y],[x+w,y],[x+w,y+h],[x,y+h]].map(([a,b])=>ll(a,b));
const lot:PavingSurface={id:'lot',material:'asphalt',coordinates:rect(0,0,40,35),parking:{version:1,rowAngle:0}};
const road:ParkingRoad={id:'road',label:'Local access road',source:'authored',compatible:true,coordinates:rect(-15,-30,6,100)};
const link=(x=-9,y=9)=>({...lot,parking:{...lot.parking!,driveway:{version:1 as const,source:'authored' as const,roadPoint:ll(x,y),streetId:'road'}}});

describe('parking driveway connection',()=>{
  it('connects the clear side aisle to the complete six-metre road edge',()=>{
    const result=parkingDriveway(link(),[road]);
    expect(result.problem).toBeNull();
    expect(result.coordinates).toHaveLength(4);
    const p=result.coordinates.map(([x,y])=>[(x+114)*metersPerDegLon(51),(y-51)*METERS_PER_DEG_LAT]);
    expect(Math.hypot(p[0][0]-p[3][0],p[0][1]-p[3][1])).toBeCloseTo(6);
    expect(Math.min(...p.map(p=>p[0]))).toBeLessThan(-9); // tiny overlap prevents a visible seam
  });
  it('selects the nearest compatible road and preserves its target after moving the lot',()=>{
    const chosen=nearestParkingRoad(lot,[{...road,id:'far',coordinates:rect(-100,-30,6,100)},road]);
    expect(chosen?.streetId).toBe('road');
    const moved={...lot,coordinates:rect(4,0,40,35),parking:{...lot.parking!,driveway:chosen!}};
    expect(parkingDriveway(moved,[road]).problem).toBeNull();
    expect(moved.parking.driveway.roadPoint).toEqual(chosen?.roadPoint);
  });
  it('rejects a building, another lot, furniture or parked bays in the connection',()=>{
    for(const obstacle of [rect(-7,4,3,10),rect(-6,8,1,1)])
      expect(parkingDriveway(link(),[road],[obstacle]).problem).toMatch(/blocked/);
    const wrongSide={...road,coordinates:rect(45,-30,6,100)};
    expect(parkingDriveway({...link(45),parking:{...lot.parking!,driveway:{...link(45).parking.driveway,roadPoint:ll(45,9)}}},[wrongSide]).problem).toBeTruthy();
  });
  it('rejects missing, curbed, too-short or remote targets instead of painting over them',()=>{
    expect(parkingDriveway(link(),[]).problem).toMatch(/missing/);
    expect(parkingDriveway({...link(),parking:{...lot.parking!,driveway:{...link().parking.driveway,source:'mapped'}}},[]).problem).toMatch(/missing/);
    expect(parkingDriveway(link(),[{...road,compatible:false}]).problem).toMatch(/curb|supported/);
    expect(nearestParkingRoad(lot,[{...road,coordinates:rect(-15,5,6,4)}])).toBeNull();
    expect(parkingDriveway({...link(),parking:{...lot.parking!,driveway:{version:1,source:'manual',roadPoint:ll(-200,9)}}},[]).problem).toBeTruthy();
  });
  it('allows an explicit concept road-edge point without inventing a mapped street',()=>{
    const manual={...link(),parking:{...lot.parking!,driveway:{version:1 as const,source:'manual' as const,roadPoint:ll(-9,9)}}};
    expect(parkingDriveway(manual,[]).problem).toBeNull();
    expect(parkingDriveway(lot,[]).coordinates).toEqual([]);
  });
  it('does not mutate input recipes, coordinates or road geometry',()=>{
    const source=link(),before=JSON.stringify([source,road]);
    parkingDriveway(source,[road]);
    expect(JSON.stringify([source,road])).toBe(before);
  });
  it('resolves a manual edge when road context loads, while retaining curb checks',()=>{
    const manual={...lot,parking:{...lot.parking!,driveway:{version:1 as const,source:'manual' as const,roadPoint:ll(-9,9)}}};
    expect(parkingDriveway(manual,[]).problem).toBeNull();
    expect(parkingDriveway(manual,[road]).problem).toBeNull();
    expect(parkingDriveway(manual,[{...road,compatible:false}]).problem).toMatch(/curb/);
  });
  it('derives mapped road outlines and keeps authored curb limitations explicit',()=>{
    const zone={id:'yield',name:'Shared road',zone_type:'road',coordinates:road.coordinates,project_id:'test',color:'#aaa',sort_order:0,created_at:'now',updated_at:'now',
      properties:{road_archetype_id:'yield_street',road_selected_variant_id:'yield_street_v0',width:6}} as SiteZone;
    const roads=parkingRoads([zone],{source:'OpenStreetMap',fetched_at:'now',blockers:[],roads:[{id:'osm',label:'Range road',widthM:6,points:[ll(-30,-30),ll(-30,70)]}]});
    expect(roads.find(r=>r.id==='yield')?.compatible).toBe(true);
    expect(roads.find(r=>r.id==='mapped:osm')?.coordinates.length).toBeGreaterThanOrEqual(4);
  });
});
