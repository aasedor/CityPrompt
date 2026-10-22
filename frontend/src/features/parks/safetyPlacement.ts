import { detailAsset } from './detailCatalogue';
import { safetySurfaceSupport } from './safetySupport';
export interface DetailPose {lng:number;lat:number;angle:number;support_zone_id?:string}
export type DetailSupport = {ok:true;hostId?:string;height?:number}|{ok:false;message:string};
export function detailPlacementSupport(id:string,pose:DetailPose,zoneIds:readonly string[]):DetailSupport {
  const asset=detailAsset(id);
  if (asset.people) {
    // Feet use the rendered sidewalk datum, not the site's unpaved base. This
    // remains an ordinary detail placement when no level authored road exists.
    const pavement = safetySurfaceSupport(pose, [-.08, -.08, .08, .08], zoneIds);
    return pavement.ok ? pavement : { ok: true };
  }
  if(!asset.safety)return {ok:true};
  if(asset.safety.placement==='sidewalk-attachment')return {ok:false,message:'This curb bulb needs a matching 150 mm sidewalk and replacement of the old curb. A compatible attachment host is not available here.'};
  const bounds=asset.safety.supportBoundsXZ;
  if(!bounds)return {ok:true};
  const allowed=pose.support_zone_id?zoneIds.filter(id=>id===pose.support_zone_id):zoneIds;
  // Prefer the exact authored road datum when available. Otherwise use the same
  // shared ground / Google terrain placement as existing bollards and furniture.
  // Source flat-road QA is a visual limitation, not an authoring restriction.
  const road = safetySurfaceSupport(pose,bounds,allowed);
  return road.ok ? road : {ok:true};
}
