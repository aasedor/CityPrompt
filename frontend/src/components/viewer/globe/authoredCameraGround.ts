import { canalRoute, canalWalkingHeight } from './canalRoute';
import { readNativePark, nativeParkFitProblem } from '@/features/parks/nativeParkRegistry';
import { nativePavingProbe } from '@/features/parks/nativeParkAccess';
import { parkWalkHeight, type ParkWalkingNetwork } from '@/features/parks/parkWalking';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { SiteZone } from '@/types';
import { buildingWalkGround } from '@/features/legoAssembly/buildingWalking';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readParkTerrain } from './parkTerrain';
import { sampleSharedSiteGround, sharedSiteGroundContains } from './sharedSiteGround';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { terraceOffset } from './terraceDefinition';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { isSpecialistStreet, specialistWalkingHeight, BRIDGE_VARIANT } from './specialistStreetProgram';
import { hasElevatedStation } from './elevatedRailProgram';
import { stepFreeParkWalkingNetwork } from '@/features/parks/stepFreeParkAccess';

/** Camera feet belong on the authored ground, not the Google mesh hidden
 * underneath it. Unprepared landscape and off-site context keep their hit. */
export function authoredCameraGround(zones: SiteZone[], lng: number, lat: number, measured: number, entrySurfaceHeight?: number): number {
  const buildingHeight = buildingWalkGround(zones, { lng, lat, groundHeight: measured, heading: 0 });
  if (buildingHeight !== null) return buildingHeight;
  const contains = (zone: SiteZone) => sharedSiteGroundContains(zone.coordinates as [number, number][], lng, lat);
  for (const zone of zones.filter(contains)) {
    const variant=String(zone.properties?.road_selected_variant_id);
    if(zone.zone_type==='road' && !zone.properties?.validation_fixed_fixture && isSpecialistStreet(variant)){
      const route=extractZoneCenterline(zone),a=route[0],b=route[route.length-1];
      if(variant==='amsterdam_gracht_v1' && a){
        const sx=metersPerDegLon(a[1]);
        const layout=canalRoute(route.map(p=>({x:(p[0]-a[0])*sx,y:(p[1]-a[1])*METERS_PER_DEG_LAT})));
        const px=(lng-a[0])*sx,py=(lat-a[1])*METERS_PER_DEG_LAT;
        const nearest=layout.segments.map(s=>{
          const dx=(s.to.x-s.from.x)/s.size,dy=(s.to.y-s.from.y)/s.size;
          const along=(px-s.from.x)*dx+(py-s.from.y)*dy;
          const t=Math.max(0,Math.min(s.size,along));
          return {x:(px-s.from.x)*dy-(py-s.from.y)*dx,station:s.start+t,
            distance:Math.hypot(px-s.from.x-dx*t,py-s.from.y-dy*t)};
        }).sort((a,b)=>a.distance-b.distance)[0];
        const level=resolvePreparedSiteTerrainForZone(zone,zones,measured);
        const height=nearest?canalWalkingHeight(nearest.x,nearest.station,layout.length,layout.crossing,layout.original):null;
        if(height!==null && level!==null)return level+height;
        continue;
      }
      if(a&&b){
        const sx=metersPerDegLon(a[1]),dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*METERS_PER_DEG_LAT,length=Math.hypot(dx,dy);
        const x=(lng-a[0])*sx,y=(lat-a[1])*METERS_PER_DEG_LAT;
        const level=resolvePreparedSiteTerrainForZone(zone,zones,measured);
        const upper=level!==null && (measured>level+3 || (entrySurfaceHeight??-Infinity)>level+3);
        const height=specialistWalkingHeight(variant,(x*dy-y*dx)/length,(x*dx+y*dy)/length,length,
          hasElevatedStation(variant)?zone.properties?.road_native_stops??[]:[],upper);
        if(height!==null&&level!==null){
          const station=(x*dx+y*dy)/length,deckStart=(length-100)/2;
          // Retain the lower route when walking through the opening. Entering
          // a ramp or clicking the deck keeps the upper continuous surface.
          // Map picking resolves the underlying terrain, not every instanced
          // deck mesh. A new entry on the bridge chooses its upper walkable
          // plane; arriving from outside underneath retains the lower level.
          const enteredDeck = entrySurfaceHeight !== undefined;
          if(variant===BRIDGE_VARIANT && station>deckStart+8 && station<length-deckStart-8
            && measured<level+height-2 && !enteredDeck)return level;
          return level+height;
        }
      }
    }
    const native = readNativePark(zone);
    if (native && !nativeParkFitProblem(zone)) {
      const level = resolvePreparedSiteTerrainForZone(zone, zones, measured);
      if (level !== null) {
        const f = native.selection.frame, c = Math.cos(f.yaw), s = Math.sin(f.yaw);
        const x = (lng - f.longitude) * metersPerDegLon(f.latitude), y = (lat - f.latitude) * METERS_PER_DEG_LAT;
        const local: [number,number] = [x*c + y*s, -x*s + y*c];
        if (Math.abs(local[0]) <= native.layout.widthM/2 && Math.abs(local[1]) <= native.layout.depthM/2) {
          try {
            const source = (native.layout as typeof native.layout & { walking?: ParkWalkingNetwork }).walking;
            const walking = source && stepFreeParkWalkingNetwork(native.layout.variantId, source);
            const height = walking ? parkWalkHeight(walking, local[0], local[1], walking.version===2?measured-level:undefined, true) : nativePavingProbe(native.layout, true)(local);
            if (height !== null) return level + height;
          } catch {
            // Loading/errors remain owned by NativeParkLayer and its capture guard.
            // Walking can retain site ground while the verified model loads.
          }
        }
      }
    }
    const parkHeight = sampleSharedSiteGround(readParkTerrain(zone), lng, lat);
    if (parkHeight !== null) return parkHeight;
    if (terraceOffset(zone) !== null) {
      const level = resolvePreparedSiteTerrainForZone(zone, zones, measured);
      if (level !== null) return level;
    }
  }
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary || !contains(boundary) || boundary.properties?.terrain_strategy === 'landscape') return measured;
  return resolvePreparedSiteTerrainForZone(boundary, zones, measured) ?? measured;
}
