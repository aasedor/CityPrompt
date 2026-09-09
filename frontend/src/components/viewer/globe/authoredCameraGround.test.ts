import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { authoredCameraGround } from './authoredCameraGround';

const boundary: SiteZone = { id:'site', project_id:'test', zone_type:'site_boundary',
  coordinates:rectangleAt([-114,51],100,100), is_active_boundary:true,
  properties:{terrain_elevation_m:1103,community_3d_mask_existing_tiles:true},
  color:'#aaa',sort_order:0,created_at:'now',updated_at:'now' };
describe('camera ground for authored communities',()=>{
  it('uses the redevelopment level even when Google terrain is below or above it',()=>{
    expect(authoredCameraGround([boundary],-114,51,1099)).toBe(1103);
    expect(authoredCameraGround([boundary],-114,51,1110)).toBe(1103);
    expect(authoredCameraGround([boundary],-113,51,1099)).toBe(1099);
  });
  it('does not flatten landscape or retained sites',()=>{
    expect(authoredCameraGround([{...boundary,properties:{...boundary.properties,terrain_strategy:'landscape'}}],-114,51,1099)).toBe(1099);
    expect(authoredCameraGround([{...boundary,properties:{...boundary.properties,community_3d_mask_existing_tiles:false}}],-114,51,1099)).toBe(1099);
  });
  it('respects an explicit terrace inside the prepared site',()=>{
    const plot={...boundary,id:'house',zone_type:'building' as const,is_active_boundary:false,coordinates:rectangleAt([-114,51],15,20),properties:{proposed_terrace:{version:1,offsetM:1}}};
    expect(authoredCameraGround([boundary,plot],-114,51,1099)).toBe(1104);
  });
});
