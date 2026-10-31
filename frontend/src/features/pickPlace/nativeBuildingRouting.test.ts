import { expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { nativeBuildingRoutes } from './nativeBuildingRouting';
import { placeAsset, placementProperties } from './catalogue';

const zone: SiteZone = {id:'plot',project_id:'project',color:'#fff',sort_order:0,created_at:'before',updated_at:'before',
  zone_type:'building',building_id:'model',coordinates:[[-114,51],[-113.999,51],[-113.999,51.001],[-114,51.001]]};
it('retains a saved local identity even when development trial discovery is unavailable', () => {
  // Ordinary Vitest/production discovery omits the seven local choices.
  const saved = {...zone,properties:{pick_place_asset:'local_teaching_wartime_victory_house',
    validation_fixed_fixture:true,validation_native_url:'/saved.glb',pick_place_model_revision:'unavailable'}};
  const routes = nativeBuildingRoutes([saved],[{id:'model'}]);
  expect(routes.unavailableZones).toEqual([saved]);
  expect(routes.otherBuildings).toEqual([]);
});

it('preserves the compiled route for supported edits to a non-trial authored assembly', () => {
  const edited = {...zone,properties:{...placementProperties(placeAsset('validation_clapboard_north_end')),
    floor_count:1,floors:1,height:7.34,height_m:7.34,development_height_override_m:7.34}};
  const model = {id:'model'};
  const routes = nativeBuildingRoutes([edited],[model]);
  expect(routes.reviewZones).toEqual([]);
  expect(routes.otherBuildings).toEqual([model]);
});

it('does not divert parks or unrelated unmodeled buildings into revision recovery', () => {
  const park = {...zone,zone_type:'green_space',properties:{pick_place_asset:'local_teaching_fake'}} as SiteZone;
  const routes = nativeBuildingRoutes([park,zone],[{id:'model'}]);
  expect(routes.reviewZones).toEqual([]);
  expect(routes.otherBuildings).toEqual([{id:'model'}]);
});
