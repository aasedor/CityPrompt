import type { SiteZone } from '@/types';
import type { WalkPose } from './walkNavigation';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { isElevatedRail, hasElevatedStation, elevatedRailPierStations, RAIL_LIFT_X_M, RAIL_LIFT_Y_M, RAIL_PLATFORM_HEIGHT_M, type RailStation } from './elevatedRailProgram';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';

/** Only a person at a visible lift landing can change levels. This keeps
 * walking elsewhere on the corridor and stair behavior unchanged. */
export function elevatedRailLiftDestination(zones: SiteZone[], pose: WalkPose): WalkPose | null {
  for (const zone of zones) {
    if (zone.zone_type !== 'road' || !hasElevatedStation(zone.properties?.road_selected_variant_id)) continue;
    const line = extractZoneCenterline(zone); if (line.length < 2) continue;
    const a=line[0],b=line[line.length-1],sx=metersPerDegLon(a[1]);
    const dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*METERS_PER_DEG_LAT,length=Math.hypot(dx,dy);
    if (!Number.isFinite(length) || !Number.isFinite(sx) || sx===0 || length < 48 || length > 288.01) continue;
    const x=(pose.lng-a[0])*sx,y=(pose.lat-a[1])*METERS_PER_DEG_LAT;
    const cross=(x*dy-y*dx)/length,station=(x*dx+y*dy)/length;
    const stops=zone.properties?.road_native_stops;
    if (!Array.isArray(stops)) continue;
    for (const stop of stops as Array<RailStation|null>) {
      if (!stop || typeof stop!=='object' || !Number.isFinite(stop.stationM) || Math.abs(station-stop.stationM-RAIL_LIFT_Y_M)>1.25
        || Math.abs(Math.abs(cross)-RAIL_LIFT_X_M)>1.15) continue;
      const level=resolvePreparedSiteTerrainForZone(zone,zones,pose.groundHeight);
      if (level === null) continue;
      const relative=pose.groundHeight-level;
      if (Math.abs(relative-.025)>.45 && Math.abs(relative-RAIL_PLATFORM_HEIGHT_M)>.45) continue;
      return {...pose,groundHeight:level+(relative>4?.025:RAIL_PLATFORM_HEIGHT_M)};
    }
  }
  return null;
}

/** Sweep the pedestrian around the solid columns, allowing side-sliding and
 * immediate retreat. The broad public paths stay clear of these footprints. */
export function constrainElevatedRailWalk(zones: SiteZone[], previous: WalkPose, proposed: WalkPose): WalkPose {
  let result=proposed;
  for(const zone of zones){
    if(zone.zone_type!=='road'||!isElevatedRail(zone.properties?.road_selected_variant_id)||zone.properties?.validation_fixed_fixture)continue;
    const line=extractZoneCenterline(zone);if(line.length<2)continue;
    const a=line[0],b=line[line.length-1],sx=metersPerDegLon(a[1]);
    const dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*METERS_PER_DEG_LAT,length=Math.hypot(dx,dy);
    if(length<48||length>288.01)continue;
    const local=(p:WalkPose)=>{const x=(p.lng-a[0])*sx,y=(p.lat-a[1])*METERS_PER_DEG_LAT;return {x:(x*dy-y*dx)/length,y:(x*dx+y*dy)/length};};
    const from=local(previous),to=local(result);
    if(Math.min(Math.abs(from.x),Math.abs(to.x))>13&&Math.sign(from.x)===Math.sign(to.x))continue;
    const stations=elevatedRailPierStations(length);
    const blocked=(x:number,y:number)=>Math.abs(x)<1.2&&stations.some(station=>Math.abs(y-station)<1.45);
    // A saved entry inside a column must be able to leave it.
    if(blocked(from.x,from.y))continue;
    const steps=Math.max(1,Math.ceil(Math.hypot(to.x-from.x,to.y-from.y)/.1));
    const ux=(to.x-from.x)/steps,uy=(to.y-from.y)/steps;
    let x=from.x,y=from.y;
    for(let i=0;i<steps;i++){
      if(!blocked(x+ux,y+uy)){x+=ux;y+=uy;}
      else if(!blocked(x+ux,y))x+=ux;
      else if(!blocked(x,y+uy))y+=uy;
    }
    result={...result,lng:a[0]+(x*dy+y*dx)/length/sx,lat:a[1]+(-x*dx+y*dy)/length/METERS_PER_DEG_LAT};
  }
  return result;
}
