import type { SiteZone } from '@/types';

export interface TerraceDefinition { version: 1; offsetM: number }
export function terraceOffset(zone: SiteZone): number | null {
  const value = zone.properties?.proposed_terrace as TerraceDefinition | undefined;
  // Pilot pads use convex plots. Never cut a concave import as a convex hole.
  const ring=zone.coordinates;
  if(ring.length<3||ring.length>64||ring.some(p=>p.length<2||!p.slice(0,2).every(Number.isFinite)))return null;
  let sign=0;
  for(let i=0;i<ring.length;i++){
    const a=ring[i],b=ring[(i+1)%ring.length],c=ring[(i+2)%ring.length];
    const cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]);
    if(Math.abs(cross)<1e-16)continue;
    if(sign&&Math.sign(cross)!==sign)return null;
    sign=Math.sign(cross);
  }
  if(!sign)return null;
  return ['building','residential','green_space'].includes(zone.zone_type) && value?.version === 1
    && typeof value.offsetM === 'number' && Number.isFinite(value.offsetM) && Math.abs(value.offsetM) <= 20
    ? value.offsetM : null;
}
