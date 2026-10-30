import clipping, { type Pair } from 'polygon-clipping';
import type { SiteZone } from '@/types';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';
import { isSurfacePath } from './surfacePath';

/** The exact timber end headstock extends 5/3 m past its nominal module seam.
 * Ground paths can pass beneath the clear middle, never through those supports. */
export function modularBridgeConnectionProblem(bridge: Pick<SiteZone,'coordinates'|'properties'>, other: SiteZone): string | null {
  const program=modularBridgeProgramFor(bridge.properties?.road_selected_variant_id);
  if (!program) return null;
  try {
    const route=extractZoneCenterline(bridge),a=route[0],b=route[route.length-1];
    if (!a || !b) return 'Choose two valid bridge endpoints.';
    const sx=111320*Math.cos(a[1]*Math.PI/180);
    const local=(ring:number[][]):Pair[]=>ring.map(p=>[(p[0]-a[0])*sx,(p[1]-a[1])*111320]);
    const overlap=clipping.intersection([local(bridge.coordinates)],[local(other.coordinates)]);
    const area=(ring:Pair[])=>Math.abs(ring.reduce((sum,p,i)=>{
      const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1];
    },0))/2;
    if (overlap.reduce((sum,polygon)=>sum+area(polygon[0])-polygon.slice(1).reduce((holes,ring)=>holes+area(ring),0),0)<=1e-6) return null;
    if (other.properties?.lane_count !== 0 || !isSurfacePath(other))
      return 'Keep other bridges and vehicle streets clear of this bridge. Connect at a ground-level endpoint.';
    const dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*111320,length=Math.hypot(dx,dy);
    const reserve=program.bridge.approachM+program.bridge.endM+5/3;
    const stations=overlap.flat(2).map(p=>(p[0]*dx+p[1]*dy)/length);
    if (stations.some(station=>station<reserve-.01 || station>length-reserve+.01))
      return 'Keep pathways clear of the bridge stairs and end supports. Cross beneath the clear middle span.';
    return null;
  } catch { return 'Check the bridge endpoints and keep its stairs and supports clear.'; }
}
