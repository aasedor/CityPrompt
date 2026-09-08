import { describe, expect, it } from 'vitest';
import { Group, Object3D } from 'three';
import { pedestrianCaptureUserData, streetConnectionCaptureUserData } from './pedestrianCapture';
import type { SiteZone } from '@/types';
import { direct3DProposalUserData, getDirect3DInstanceDescriptor, getDirect3DProposalRole } from './direct3dCapture';

describe('pedestrian capture ownership',()=>{
  const street:SiteZone={id:'street',project_id:'test',zone_type:'road',coordinates:[],color:'#aaa',sort_order:0,created_at:'2026-09-07',updated_at:'2026-09-07',properties:{}};
  const house:SiteZone={...street,id:'house',zone_type:'building',properties:{pedestrian_building_entrance:{version:1,xM:0,yM:-6,referenceWidthM:12,referenceDepthM:16,scaleWithPlot:false,streetId:'street',widthM:1.8}}};
  it('attributes a house approach to its saved destination without relabelling the building',()=>{
    const mesh=new Object3D();
    mesh.userData=streetConnectionCaptureUserData(house,[house,street])!;
    expect(getDirect3DInstanceDescriptor(mesh)).toMatchObject({instance_id:'zone:street:street',semantic_class:'street',zone_id:'street'});
    expect(mesh.userData.pedestrianOwnerZoneId).toBe('house');
  });
  it('does not capture an approach to a deleted or non-street target',()=>{
    expect(streetConnectionCaptureUserData(house,[house])).toBeNull();
    expect(streetConnectionCaptureUserData(house,[house,{...street,zone_type:'green_space'}])).toBeNull();
  });
  it('preserves crossing ownership on the road',()=>{
    const mesh=new Object3D();mesh.userData=streetConnectionCaptureUserData(street,[street])!;
    expect(getDirect3DInstanceDescriptor(mesh)).toMatchObject({zone_id:'street',semantic_class:'street'});
  });
  it('keeps street semantics under a differently labelled parent and retains the source owner',()=>{
    const parent=new Group(),connection=new Group(),mesh=new Object3D();
    parent.userData=direct3DProposalUserData('park');
    connection.userData=pedestrianCaptureUserData('house');
    parent.add(connection);connection.add(mesh);
    expect(getDirect3DProposalRole(mesh)).toBe('street');
    expect(getDirect3DInstanceDescriptor(mesh)).toMatchObject({semantic_class:'street',zone_id:'house'});
  });
});
