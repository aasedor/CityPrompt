import type { SiteZone } from '@/types';
import { envelopesOverlap } from '@/components/viewer/globe/neighborhoodParkLayout';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { isSpecialistStreet } from '@/components/viewer/globe/specialistStreetProgram';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { isFixedSectionStreet } from './streetPlacement';

/** Only accept overlaps that the shared junction renderer can actually join. */
export function streetConnectionProblem(candidate: Pick<SiteZone, 'coordinates'|'properties'> & Partial<SiteZone>, zones: SiteZone[]): string | null {
  const draft = {...candidate, id:candidate.id ?? 'draft-street', zone_type:candidate.zone_type ?? 'road',
    properties: {...candidate.properties, junction_preview_candidate: true}} as SiteZone;
  if (!isFixedSectionStreet(draft) || isSpecialistStreet(draft.properties?.road_selected_variant_id) || draft.properties?.validation_fixed_fixture) return null;
  const origin=draft.coordinates[0]; if(!origin)return null;
  const sx=metersPerDegLon(origin[1]);
  const local=(ring:number[][])=>ring.map(p=>({x:(p[0]-origin[0])*sx,y:(p[1]-origin[1])*METERS_PER_DEG_LAT}));
  for(const other of zones){
    if(other.id===draft.id || !isFixedSectionStreet(other) || isSpecialistStreet(other.properties?.road_selected_variant_id) || other.properties?.validation_fixed_fixture)continue;
    if(!envelopesOverlap(local(draft.coordinates),local(other.coordinates)))continue;
    const pair=[other,draft];
    if(detectConnectedStreetIntersections(pair,true).some(node=>resolveStreetJunctionLayout(node,pair)))continue;
    // A flush collinear end connection needs no junction patch. Require
    // opposite outward directions so overlapping duplicate routes cannot pass.
    const a=extractZoneCenterline(draft),b=extractZoneCenterline(other);
    const ends=(line:number[][])=>[[line[0],line[1]],[line[line.length-1],line[line.length-2]]];
    const aligned=a.length>=2 && b.length>=2 && ends(a).some(([p,q])=>ends(b).some(([r,s])=>{
      if(Math.hypot((p[0]-r[0])*sx,(p[1]-r[1])*METERS_PER_DEG_LAT)>.25)return false;
      const ax=(q[0]-p[0])*sx,ay=(q[1]-p[1])*METERS_PER_DEG_LAT,bx=(s[0]-r[0])*sx,by=(s[1]-r[1])*METERS_PER_DEG_LAT;
      return (ax*bx+ay*by)/Math.hypot(ax,ay)/Math.hypot(bx,by)<-.999;
    }));
    if(!aligned)return 'This overlap cannot form a complete junction. Use a 45–135° crossing with longer straight approaches, align the endpoints, or separate the streets.';
  }
  const network = [...zones.filter(zone => zone.id !== draft.id), draft];
  if (detectConnectedStreetIntersections(network, true).some(node =>
    node.zoneIds.includes(draft.id) && !resolveStreetJunctionLayout(node, network))) {
    return 'These streets cannot share one complete junction. Separate the nearby connections and leave longer straight approaches.';
  }
  return null;
}
