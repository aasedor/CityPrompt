import { detailAsset } from './detailCatalogue';
import { safetySurfaceSupport } from './safetySupport';
export interface DetailPose {lng:number;lat:number;angle:number;support_zone_id?:string}
export type DetailSupport = {ok:true;hostId?:string;height?:number}|{ok:false;message:string};
export function detailPlacementSupport(id:string,pose:DetailPose,zoneIds:readonly string[]):DetailSupport {
  const asset=detailAsset(id);
  if(!asset.safety)return {ok:true};
  if(asset.safety.placement==='sidewalk-attachment')return {ok:false,message:'This curb bulb needs a matching 150 mm sidewalk and replacement of the old curb. A compatible attachment host is not available here.'};
  const bounds=asset.safety.supportBoundsXZ;
  if(!bounds)return {ok:false,message:'This item has no verified source-pivot support footprint.'};
  const allowed=pose.support_zone_id?zoneIds.filter(id=>id===pose.support_zone_id):zoneIds;
  return safetySurfaceSupport(pose,bounds,allowed);
}
