import { describe, expect, it } from 'vitest';
import { Group } from 'three';
import type { SiteZone } from '@/types';
import { assertNativeStreetsReady, nativeStreetRevision } from './nativeStreetReadiness';

const zone:SiteZone={id:'street',project_id:'test',color:'#aaa',sort_order:0,created_at:'1',updated_at:'1',zone_type:'road',coordinates:[[0,0],[0,1]],properties:{road_selected_variant_id:'student_main_street_v1'}};
describe('native street capture inventory',()=>{
  it('rejects an entirely absent model, a stale revision and a missing component',()=>{
    const scene=new Group();
    expect(()=>assertNativeStreetsReady(scene,[zone])).toThrow('street');
    const parent=new Group(),batch=new Group();scene.add(parent);parent.add(batch);
    parent.userData={nativeStreetZone:zone.id,nativeStreetRevision:nativeStreetRevision(zone),nativeStreetExpectedCount:30};
    batch.userData={nativeStreetStatus:'ready',nativeStreetMountedCount:29};
    expect(()=>assertNativeStreetsReady(scene,[zone])).toThrow('missing');
    batch.userData.nativeStreetMountedCount=30;
    expect(()=>assertNativeStreetsReady(scene,[zone])).not.toThrow();
    const moved={...zone,coordinates:[[1,0],[1,1]]};
    expect(()=>assertNativeStreetsReady(scene,[moved])).toThrow();
    batch.userData.nativeStreetStatus='error';
    expect(()=>assertNativeStreetsReady(scene,[zone])).toThrow();
    expect(()=>assertNativeStreetsReady(scene,[])).not.toThrow();
  });
});
