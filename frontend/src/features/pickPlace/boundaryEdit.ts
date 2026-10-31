import type {SiteZone} from '@/types';
import {envelopeFits} from '@/components/viewer/globe/neighborhoodParkLayout';
import {METERS_PER_DEG_LAT, metersPerDegLon} from '@/components/viewer/mapEngine/geoUtils';
import {publicRoadConnectionFits} from './publicRoadConnection';
import {assetForZone} from './catalogue';

/** Immediate feedback; the API independently checks the saved, locked project. */
export function boundaryEditProblem(coordinates:number[][], zones:SiteZone[], boundaryId:string):string|null {
  if(coordinates.length<3)return 'Site boundary not changed. Keep at least three corners.';
  const origin=coordinates[0];
  const local=(ring:number[][])=>ring.map(p=>({x:(p[0]-origin[0])*metersPerDegLon(origin[1]),y:(p[1]-origin[1])*METERS_PER_DEG_LAT}));
  const boundary={coordinates} as SiteZone;
  const outside=zones.filter(zone=>zone.id!==boundaryId && zone.zone_type!=='site_boundary'
    && !envelopeFits(local(zone.coordinates),local(coordinates))
    && !publicRoadConnectionFits(zone,zone.coordinates,boundary));
  if(!outside.length)return null;
  const labels=outside.slice(0,3).map(zone=>zone.name?.trim() || assetForZone(zone)?.label
    || (zone.zone_type==='road'?'Street':zone.zone_type==='green_space'?'Park':'Building'));
  return `Site boundary not changed. Keep ${labels.join(', ')}${outside.length>3?` and ${outside.length-3} more objects`:''} inside the site. Move these objects before reducing the boundary.`;
}
