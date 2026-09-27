import type { Object3D } from 'three';
import type { SiteZone } from '@/types';
import { nativeStreetPilot } from './nativeStreetPilot';
export const expectsNativeStreet = (zone: SiteZone) => zone.zone_type==='road'
  && !!nativeStreetPilot(String(zone.properties?.road_selected_variant_id));
export const nativeStreetRevision = (zone: SiteZone) => JSON.stringify([
  zone.coordinates, zone.properties?.plan_centerline, zone.properties?.road_selected_variant_id,
  zone.properties?.public_realm_lego, zone.properties?.community_3d,
]);
export function assertNativeStreetsReady(scene: Object3D|null, zones: SiteZone[]) {
  for (const zone of zones.filter(expectsNativeStreet)) {
    let ready=false;
    scene?.traverse(object=>{
      if(object.userData.nativeStreetZone!==zone.id || object.userData.nativeStreetRevision!==nativeStreetRevision(zone))return;
      let count=0,verified=false,failed=false;
      object.traverse(child=>{
        if(child.userData.nativeStreetStatus==='ready')verified=true;
        if(['loading','error'].includes(child.userData.nativeStreetStatus))failed=true;
        count+=child.userData.nativeStreetMountedCount ?? 0;
      });
      ready=verified && !failed && Number.isInteger(object.userData.nativeStreetExpectedCount)
        && count===object.userData.nativeStreetExpectedCount;
    });
    if(!ready)throw new Error('Your street is still updating or a required component is missing. Wait for loading, or choose Retry 3D update.');
  }
}
export async function waitForNativeStreetsReady(scene:Object3D|null,zones:SiteZone[],timeoutMs=15000) {
  const deadline=Date.now()+timeoutMs;
  for(;;) {
    try {assertNativeStreetsReady(scene,zones);return;} catch(error) {
      let failed=false;
      scene?.traverse(object=>{if(object.userData.nativeStreetStatus==='error')failed=true;});
      if(failed || Date.now()>=deadline)throw error;
      await new Promise(resolve=>setTimeout(resolve,100));
    }
  }
}
