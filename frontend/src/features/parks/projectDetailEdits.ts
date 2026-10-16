import type { ProjectProp } from './projectBenches';
import type { DetailSupport, DetailPose } from './safetyPlacement';
export function validateDetailEdits(props:ProjectProp[],original:ProjectProp[],validate:(id:string,pose:DetailPose)=>DetailSupport):ProjectProp[] {
  return props.map(prop=>{
    const old=original.find(item=>item.id===prop.id);
    const turn=old?Math.abs(((prop.angle-old.angle+540)%360+360)%360-180):Infinity;
    if(old&&old.variant===prop.variant&&old.support_zone_id===prop.support_zone_id
      &&Math.abs(old.lng-prop.lng)<=1e-10&&Math.abs(old.lat-prop.lat)<=1e-10&&turn<=1e-6)return old;
    const support=validate(prop.variant,{...prop,support_zone_id:undefined});
    if(!support.ok)throw new Error(support.message);
    return support.hostId?{...prop,support_zone_id:support.hostId}:prop;
  });
}
