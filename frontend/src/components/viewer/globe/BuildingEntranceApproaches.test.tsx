import { renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { ReactNode } from 'react';
import type { SiteZone } from '@/types';
import type { ConnectionResult } from '@/features/pickPlace/pedestrianConnections';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolveBuildingGroundContact, type GroundPoint } from './buildingGroundContact';
import { BuildingEntranceApproaches, useBuildingEntranceApproach } from './BuildingEntranceApproaches';

const ground=vi.hoisted(()=>({status:'ready',contains:()=>true,heightAt:(x:number)=>100+Math.max(0,5-(x+114)*111320*Math.cos(51*Math.PI/180))*.2}));
vi.mock('./SharedSiteGroundProvider',()=>({useSharedSiteGround:()=>ground}));
const lng=-114,lat=51,geo=([x,y]:number[]):GroundPoint=>[lng+x/metersPerDegLon(lat),lat+y/METERS_PER_DEG_LAT];
const footprints:GroundPoint[][]=[[[-5,-4],[5,-4],[5,4],[-5,4]]];
const frame={centroidLng:lng,centroidLat:lat,bearingRad:0,longDim:10,shortDim:8,rectCenterLocal:[0,0] as GroundPoint};
const contact=resolveBuildingGroundContact(footprints,lng,lat,ground);
const house:SiteZone={id:'house',project_id:'project',building_id:'model',zone_type:'building',coordinates:footprints[0].map(geo),
  properties:{},color:'#aaa',sort_order:0,created_at:'today',updated_at:'today'};
const street:SiteZone={...house,id:'street',building_id:undefined,zone_type:'road',coordinates:[],properties:{}};
const connected:ConnectionResult={ownerId:'house',kind:'building',id:'house',status:'connected',reason:'Plan connection',
  strips:[{id:'approach',ownerId:'house',start:geo([11,0]),end:geo([5,0]),widthM:1.8,startLiftM:.025,endLiftM:.025,color:'#aaa'}]};
const configured={...house,properties:{pedestrian_building_entrance:{version:1,xM:5,yM:0,referenceWidthM:10,referenceDepthM:8,
  scaleWithPlot:false,streetId:'street',widthM:1.8,heightAboveBaseM:0}}};

describe('foundation and entrance ownership',()=>{
  it('reports an unconnected raised foundation while keeping the building contact ready',()=>{
    const wrapper=({children}:{children:ReactNode})=><BuildingEntranceApproaches zones={[house,street]} results={[]}>{children}</BuildingEntranceApproaches>;
    const {result}=renderHook(()=>useBuildingEntranceApproach(contact,footprints,frame,'model'),{wrapper});
    expect(contact.status).toBe('ready');
    expect(result.current.reason).toBe('entrance_connection_required');
    expect(result.current.geometry).toBeNull();
  });
  it('publishes valid approach geometry as its street, without changing the building identity',()=>{
    const wrapper=({children}:{children:ReactNode})=><BuildingEntranceApproaches zones={[configured,street]} results={[connected]}>{children}</BuildingEntranceApproaches>;
    const {result}=renderHook(()=>useBuildingEntranceApproach(contact,footprints,frame,'model'),{wrapper});
    expect(result.current.reason).toBeNull();
    expect(result.current.geometry?.getAttribute('position').count).toBeGreaterThan(0);
    expect(result.current.railGeometry?.getAttribute('position').count).toBeGreaterThan(0);
    expect(result.current.supportGeometry?.getAttribute('position').count).toBeGreaterThan(0);
    expect(result.current.userData).toMatchObject({pedestrianOwnerZoneId:'house',siteforgeDirect3DInstance:{zone_id:'street',semantic_class:'street'}});
    expect(result.current.userData?.entranceApproachDetails.clearWidthM).toBeCloseTo(1.64);
  });
  it('retires geometry and reports the missing target after an edit',()=>{
    let zones=[configured,street];
    const wrapper=({children}:{children:ReactNode})=><BuildingEntranceApproaches zones={zones} results={[connected]}>{children}</BuildingEntranceApproaches>;
    const {result,rerender}=renderHook(()=>useBuildingEntranceApproach(contact,footprints,frame,'model'),{wrapper});
    expect(result.current.geometry).not.toBeNull();
    zones=[configured];rerender();
    expect(result.current.geometry).toBeNull();
    expect(result.current.reason).toBe('entrance_approach_obstructed');
    expect(result.current.railGeometry).toBeNull();
    expect(result.current.supportGeometry).toBeNull();
  });
  it('does not introduce warnings on a level supported foundation without an authored entrance',()=>{
    const flat=resolveBuildingGroundContact(footprints,lng,lat,{...ground,heightAt:()=>100});
    const wrapper=({children}:{children:ReactNode})=><BuildingEntranceApproaches zones={[house]} results={[]}>{children}</BuildingEntranceApproaches>;
    const {result}=renderHook(()=>useBuildingEntranceApproach(flat,footprints,frame,'model'),{wrapper});
    expect(result.current.reason).toBeNull();
  });
});
