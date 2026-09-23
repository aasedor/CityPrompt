import type { ParkGroundGuide } from './parkGroundProfiles';
import { distanceToSegment, envelopeFits, type ParkPoint } from './neighborhoodParkLayout';
import type { ParkMicrodetailPlacement } from './parkMicrodetailFamilies';

/** Fill the two authored meadow rooms, not the lawn. Complete clump footprints
 * stay inside the boundary and outside the real path widths and fixed objects. */
export function meadowPlantingDrifts(boundary: ParkPoint[], guides: ParkGroundGuide[], obstacles: Array<ParkPoint & { radius: number }>): ParkMicrodetailPlacement[] {
  if (boundary.length < 3) return [];
  const minX = Math.min(...boundary.map(p=>p.x)), maxX = Math.max(...boundary.map(p=>p.x));
  const minY = Math.min(...boundary.map(p=>p.y)), maxY = Math.max(...boundary.map(p=>p.y));
  const w = maxX-minX, h = maxY-minY;
  const local = ([x,y]: number[]): ParkPoint => ({x:minX+x*w,y:maxY-y*h});
  const paths = guides.filter(g=>g.kind==='polyline').map(g=>({points:(g.points ?? []).map(local),width:g.strokeWidthM ?? 3}));
  const result: ParkMicrodetailPlacement[] = [];
  for (const bed of guides.slice(5,7).filter(g=>g.kind==='ellipse')) {
    const center=local([bed.x,bed.y]), rx=bed.width*w/2-.65, ry=bed.height*h/2-.65;
    if (rx <= 0 || ry <= 0) continue;
    const count=Math.min(48,Math.floor(Math.PI*rx*ry/1.2));
    for (let i=0;i<count;i++) {
      const angle=i*2.399963, radius=Math.sqrt((i+.5)/count);
      const p={x:center.x+Math.cos(angle)*rx*radius,y:center.y+Math.sin(angle)*ry*radius};
      const r=.55;
      if (!envelopeFits([{x:p.x-r,y:p.y-r},{x:p.x+r,y:p.y-r},{x:p.x+r,y:p.y+r},{x:p.x-r,y:p.y+r}],boundary,.1)) continue;
      if (paths.some(path=>path.points.some((q,j)=>j>0&&distanceToSegment(p,path.points[j-1],q)<path.width/2+r+.2))) continue;
      if (obstacles.some(o=>Math.hypot(p.x-o.x,p.y-o.y)<o.radius+r)) continue;
      if (result.some(o=>Math.hypot(p.x-o.x,p.y-o.y)<1)) continue;
      result.push({...p,id:`meadow-drift-${result.length}`,familyId:'park_neighborhood_community',kind:i%3===0?'perennial':'ornamental_grass',yawRad:angle,footprintRadiusM:r,scale:1,elementCount:8});
    }
  }
  return result;
}
