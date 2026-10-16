import { CALGARY_TRANSPORT_ROOT } from './existingTransport';
import { zoningBounds, type Position } from './zoningLabels';

export type StreetName = { id: string; label: string; anchor: Position };
export type StreetBounds = [number, number, number, number];
export const STREET_NAME_LIMIT = 100;
function validBounds(b: StreetBounds): boolean {
  const [w,s,e,n] = b;
  return b.every(Number.isFinite) && w < e && s < n && w >= -114.35 && e <= -113.85
    && s >= 50.8 && n <= 51.25 && e-w <= .04 && n-s <= .025;
}

/** Include adjacent roads, not just the interior of the proposed site. */
export function streetNameBounds(coordinates: number[][]): StreetBounds | null {
  const b = zoningBounds(coordinates);
  if (!b || !validBounds(b)) return null;
  const padded: StreetBounds = [b[0]-.002,b[1]-.0013,b[2]+.002,b[3]+.0013];
  return validBounds(padded) ? padded : b;
}

/** Clip each segment before choosing an anchor: long roads may cross the view
 * with both original endpoints outside it. Liang–Barsky clipping keeps names
 * on real road geometry instead of the feature's bounding-box centre. */
function clip(a: Position, b: Position, bounds: StreetBounds): [Position, Position] | null {
  const dx=b[0]-a[0], dy=b[1]-a[1];
  let lo=0, hi=1;
  for (const [p,q] of [[-dx,a[0]-bounds[0]],[dx,bounds[2]-a[0]],[-dy,a[1]-bounds[1]],[dy,bounds[3]-a[1]]]) {
    if (p===0) { if (q<0) return null; continue; }
    const t=q/p;
    if (p<0) lo=Math.max(lo,t); else hi=Math.min(hi,t);
    if (lo>hi) return null;
  }
  return [[a[0]+lo*dx,a[1]+lo*dy],[a[0]+hi*dx,a[1]+hi*dy]];
}

export function streetNameLabels(features: unknown[], bounds: StreetBounds): StreetName[] {
  const names = new Map<string, StreetName & { length: number }>();
  for (const raw of features.slice(0,600)) {
    if (!raw || typeof raw !== 'object') continue;
    const feature = raw as { properties?: { FULL_NAME?: unknown; BUILT_STATUS?: unknown }; geometry?: { type?: string; coordinates?: unknown } };
    const name = feature.properties?.FULL_NAME;
    if (typeof name !== 'string' || !name.trim() || String(feature.properties?.BUILT_STATUS).toUpperCase() !== 'BUILT') continue;
    const label=name.trim().slice(0,100), key=label.toUpperCase();
    const geometry=feature.geometry;
    const paths=geometry?.type==='LineString' ? [geometry.coordinates] : geometry?.type==='MultiLineString' && Array.isArray(geometry.coordinates) ? geometry.coordinates : [];
    for (const path of paths) {
      if (!Array.isArray(path) || path.length>2000 || path.some(p=>!Array.isArray(p) || p.length<2 || !Number.isFinite(p[0]) || !Number.isFinite(p[1]) || Math.abs(p[0])>180 || Math.abs(p[1])>90)) continue;
      for (let i=1;i<path.length;i++) {
        const segment=clip(path[i-1] as Position,path[i] as Position,bounds);
        if (!segment) continue;
        const [a,b]=segment;
        const length=Math.hypot((b[0]-a[0])*Math.cos(a[1]*Math.PI/180),b[1]-a[1]);
        if (length<=0 || length<=(names.get(key)?.length ?? 0)) continue;
        names.set(key,{ id:`street:${key}`,label,anchor:[(a[0]+b[0])/2,(a[1]+b[1])/2],length });
      }
    }
  }
  return [...names.values()].sort((a,b)=>b.length-a.length || a.id.localeCompare(b.id))
    .slice(0,STREET_NAME_LIMIT).map(({ id,label,anchor })=>({ id,label,anchor }));
}

export async function fetchStreetNames(bounds: StreetBounds, signal?: AbortSignal): Promise<StreetName[]> {
  if (!validBounds(bounds)) throw new Error('Street names are available for Calgary neighbourhoods. Choose a smaller area.');
  const query=new URLSearchParams({where:"BUILT_STATUS = 'BUILT'",geometry:bounds.join(','),geometryType:'esriGeometryEnvelope',
    inSR:'4326',outSR:'4326',spatialRel:'esriSpatialRelIntersects',outFields:'FULL_NAME,BUILT_STATUS',
    returnGeometry:'true',returnZ:'false',resultRecordCount:'600',f:'geojson'});
  const response=await fetch(`${CALGARY_TRANSPORT_ROOT}/Street_Centreline/FeatureServer/0/query?${query}`,{signal});
  if (!response.ok) throw new Error('Street names could not load. Try again.');
  const data=await response.json();
  if (data.error || data.type!=='FeatureCollection' || !Array.isArray(data.features)) throw new Error('Street names are temporarily unavailable. Try again.');
  if (data.exceededTransferLimit || data.properties?.exceededTransferLimit || data.features.length>=600) throw new Error('Choose a smaller site to see street names.');
  return streetNameLabels(data.features,bounds);
}
