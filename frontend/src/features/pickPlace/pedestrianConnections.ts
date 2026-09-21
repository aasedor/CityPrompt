import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { effectiveRoadWidth, extractRenderableStreetCenterline } from '@/utils/roadGeometry';
import { pedestrianAccessBands, resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import { corridorInside, corridorOverlaps, pointInside } from '@/components/viewer/globe/parkAccessConnections';
import { rectangleDimensions } from './geometry';
import { resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';

export type Point = [number, number];
/** Door coordinates are in the plot's rotating local metre frame. Native houses
 * can keep metre offsets; envelope-fitted buildings can scale with the plot. */
export interface BuildingEntrance {
  version: 1; xM: number; yM: number; referenceWidthM: number; referenceDepthM: number;
  scaleWithPlot: boolean; streetId: string; widthM: number;
  /** Vertical offset of the authored foot-of-steps anchor, never plot-scaled. */
  heightAboveBaseM?: number;
  automatic?: boolean;
  sourceVariantId?: string;
}
export interface StreetCrossing { id: string; position: number; widthM: number }
export interface PedestrianStrip {
  id: string; ownerId: string; start: Point; end: Point; widthM: number;
  startLiftM: number; endLiftM: number; color: string;
}
export interface ConnectionResult {
  ownerId: string; kind: 'building' | 'crossing'; id: string;
  status: 'connected' | 'unresolved'; reason: string; strips: PedestrianStrip[];
}
const finite = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x);
const validRing = (z: SiteZone) => z.coordinates.length >= 3 && z.coordinates.length <= 512
  && z.coordinates.every(p => p.length >= 2 && finite(p[0]) && finite(p[1]) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 85);
const sub = (a: Point, b: Point): Point => [a[0] - b[0], a[1] - b[1]];
const add = (a: Point, b: Point): Point => [a[0] + b[0], a[1] + b[1]];
const mul = (a: Point, n: number): Point => [a[0] * n, a[1] * n];
const length = (p: Point) => Math.hypot(...p);
const mix = (a: Point, b: Point, t: number) => add(a, mul(sub(b, a), t));
const project = (p: Point, a: Point, b: Point) => {
  const d = sub(b, a); const q = sub(p, a);
  return mix(a, b, Math.max(0, Math.min(1, (q[0] * d[0] + q[1] * d[1]) / Math.max(1e-8, length(d) ** 2))));
};
const frame = (origin: number[]) => ({
  local: (p: number[]): Point => [(p[0] - origin[0]) * metersPerDegLon(origin[1]), (p[1] - origin[1]) * METERS_PER_DEG_LAT],
  world: (p: Point): Point => [origin[0] + p[0] / metersPerDegLon(origin[1]), origin[1] + p[1] / METERS_PER_DEG_LAT],
});
export function readBuildingEntrance(zone: SiteZone, zones?: readonly SiteZone[]): BuildingEntrance | null {
  const v = zone.properties?.pedestrian_building_entrance as BuildingEntrance | undefined;
  const valid = v?.version === 1 && finite(v.xM) && finite(v.yM) && Math.abs(v.xM) <= 500 && Math.abs(v.yM) <= 500
    && finite(v.referenceWidthM) && v.referenceWidthM > 0 && finite(v.referenceDepthM) && v.referenceDepthM > 0
    && typeof v.scaleWithPlot === 'boolean' && typeof v.streetId === 'string' && finite(v.widthM) && v.widthM >= 1.2 && v.widthM <= 4
    && (v.heightAboveBaseM === undefined || (finite(v.heightAboveBaseM) && v.heightAboveBaseM >= 0 && v.heightAboveBaseM <= 3));
  if (!valid) return null;
  if (!v.automatic || !zones) return v;
  if (!validRing(zone) || zone.coordinates.length !== 4) return null;
  if (v.sourceVariantId && v.sourceVariantId !== zone.properties?.development_selected_variant_id) return null;
  const d = rectangleDimensions(zone.coordinates);
  // Multiple repeated houses need a per-instance entrance contract; do not
  // attach their shared plot centre to an imaginary doorway.
  if (!v.scaleWithPlot && (Math.abs(d.width-v.referenceWidthM) > .05 || Math.abs(d.depth-v.referenceDepthM) > .05)) return null;
  const anchor = entranceWorldPoint(zone, v);
  if (!anchor) return null;
  const f = frame(anchor);
  let best: { id: string; distance: number } | null = null;
  for (const street of [...zones].filter(z => z.zone_type === 'road' && !z.id.startsWith('temp-')).sort((a,b)=>a.id.localeCompare(b.id))) {
    const section = resolvePilotStreetSectionProfile(street);
    if (!section) continue;
    const scale = section.metricWidthLocked ? (section.targetRowM ?? section.rowM)/section.rowM : effectiveRoadWidth(street.properties)/section.rowM;
    const line = extractRenderableStreetCenterline(street).map(f.local);
    for (let i=1;i<line.length;i++) {
      const a=line[i-1], b=line[i], size=length(sub(b,a));
      if (size < .01) continue;
      const n: Point = [-(b[1]-a[1])/size,(b[0]-a[0])/size];
      for (const band of pedestrianAccessBands(section)) {
        const target=project([0,0],add(a,mul(n,band.centerM*scale)),add(b,mul(n,band.centerM*scale)));
        const distance=length(target);
        if (distance <= 30 && (!best || distance < best.distance)) best={id:street.id,distance};
      }
    }
  }
  return best ? {...v,streetId:best.id} : null;
}
export function entranceWorldPoint(zone: SiteZone, entrance: BuildingEntrance): Point | null {
  if (!validRing(zone) || zone.coordinates.length !== 4) return null;
  const d = rectangleDimensions(zone.coordinates), r = d.degrees * Math.PI / 180;
  const x = entrance.xM * (entrance.scaleWithPlot ? d.width / entrance.referenceWidthM : 1);
  const y = entrance.yM * (entrance.scaleWithPlot ? d.depth / entrance.referenceDepthM : 1);
  return frame(d.center).world([x * Math.cos(r) - y * Math.sin(r), x * Math.sin(r) + y * Math.cos(r)]);
}
export function readCrossings(zone: SiteZone): StreetCrossing[] {
  const raw = zone.properties?.pedestrian_crossings;
  if (!Array.isArray(raw) || raw.length > 8) return [];
  const ids = new Set<string>();
  return raw.filter((v: StreetCrossing) => {
    if (!v || typeof v.id !== 'string' || ids.has(v.id) || !finite(v.position) || v.position < 0 || v.position > 1
      || !finite(v.widthM) || v.widthM < 1.8 || v.widthM > 5) return false;
    ids.add(v.id); return true;
  });
}
export function crossingStation(zone: SiteZone, position: number) {
  if (!validRing(zone) || !finite(position) || position < 0 || position > 1) return null;
  const f = frame(zone.coordinates[0]);
  const line = extractRenderableStreetCenterline(zone).map(f.local);
  const lengths = line.slice(1).map((p, i) => length(sub(p, line[i])));
  let remaining = lengths.reduce((a, b) => a + b, 0) * position;
  for (let i = 0; i < lengths.length; i++) {
    const size = lengths[i];
    if (size < 0.01) continue;
    if (remaining <= size || i === lengths.length - 1) {
      const tangent = mul(sub(line[i + 1], line[i]), 1 / size);
      return { point: f.world(mix(line[i], line[i + 1], remaining / size)), tangent,
        distanceToBendM: Math.min(remaining, size - remaining) };
    }
    remaining -= size;
  }
  return null;
}
export function resolvePedestrianConnections(zones: readonly SiteZone[], visibleIds?: readonly string[]): ConnectionResult[] {
  const boundary = getActiveSiteBoundary([...zones]);
  const visible = new Set(visibleIds ?? zones.map(z => z.id));
  const results: ConnectionResult[] = [];
  const inventoryValid = zones.length <= 256 && zones.every(validRing);
  for (const owner of zones.filter(z => visible.has(z.id))) {
    const configured = owner.properties?.pedestrian_building_entrance as BuildingEntrance | undefined;
    const rawEntrance = configured?.automatic ? readBuildingEntrance(owner, zones) : configured;
    const entries = owner.zone_type === 'road' ? readCrossings(owner) : [];
    const configs = rawEntrance && ['building', 'residential'].includes(owner.zone_type) ? [null] : entries;
    for (const crossing of configs) {
      const result: ConnectionResult = { ownerId: owner.id, kind: crossing ? 'crossing' : 'building',
        id: crossing?.id ?? owner.id, status: 'unresolved', reason: 'A valid shared site boundary is needed.', strips: [] };
      results.push(result);
      if (!inventoryValid || !boundary) continue;
      const f = frame(owner.coordinates[0]); const border = boundary.coordinates.map(f.local);
      const obstacles = zones.filter(z => z.id !== owner.id && ['building','residential','green_space','parking','water'].includes(z.zone_type));
      const safe = (a: Point, b: Point, width: number, ignoredRoad: string) => corridorInside(a, b, border, width / 2)
        && ![...obstacles, ...zones.filter(z => z.zone_type === 'road' && z.id !== ignoredRoad)]
          .some(z => corridorOverlaps(a, b, z.coordinates.map(f.local), width / 2 + 0.15));
      if (crossing) {
        const section = resolvePilotStreetSectionProfile(owner), station = crossingStation(owner, crossing.position);
        result.reason = 'Choose a straight section with sidewalks on both sides, away from bends and intersections.';
        if (!section || !station || station.distanceToBendM < crossing.widthM / 2 + 2) continue;
        const sidewalks = section.bands.filter(b => b.kind === 'sidewalk').sort((a,b) => a.centerM-b.centerM);
        if (sidewalks.length < 2 || sidewalks[0].centerM >= 0 || sidewalks[sidewalks.length-1].centerM <= 0) continue;
        const scale = section.metricWidthLocked ? (section.targetRowM ?? section.rowM) / section.rowM : effectiveRoadWidth(owner.properties) / section.rowM;
        const normal: Point = [-station.tangent[1], station.tangent[0]], centre = f.local(station.point);
        const first = sidewalks[0], last = sidewalks[sidewalks.length-1];
        const at = (offset: number) => add(centre, mul(normal, offset * scale));
        const overlapsCrossing = entries.some(other=>{
          if(other.id===crossing.id)return false;
          const otherStation=crossingStation(owner,other.position);
          return otherStation && length(sub(f.local(otherStation.point),centre)) < (crossing.widthM+other.widthM)/2+3;
        });
        if(overlapsCrossing){result.reason='Crossings are too close together. Move or remove one.';continue;}
        if (!safe(at(first.startM), at(last.endM), crossing.widthM+3, owner.id)) { result.reason = 'This crossing overlaps another object or leaves the site. Move it along the street.'; continue; }
        // Physical raised crossing: continuous surface at sidewalk level through
        // boulevards, with short vehicle ramps added by the rendering layer.
        const lift = Math.max(first.liftM, last.liftM);
        result.strips.push({ id: `${crossing.id}:surface`, ownerId: owner.id, start: f.world(at(first.startM)), end: f.world(at(last.endM)),
          widthM: crossing.widthM, startLiftM: lift, endLiftM: lift, color: '#b7b0a2' });
        for (const band of section.bands.filter(b => ['motor','cycle'].includes(b.kind))) {
          for (let offset = band.startM * scale + 0.15; offset + 0.45 < band.endM * scale; offset += 0.85) {
            result.strips.push({ id: `${crossing.id}:${band.startM}:${offset}`, ownerId: owner.id,
              start: f.world(add(centre, mul(normal, offset))), end: f.world(add(centre, mul(normal, offset + 0.45))),
              widthM: crossing.widthM - 0.4, startLiftM: lift + 0.012, endLiftM: lift + 0.012, color: '#fffdf0' });
          }
          for (const sign of [-1, 1]) {
            const edge = add(centre, mul(station.tangent, sign * crossing.widthM / 2));
            const mid = (band.startM + band.endM) / 2 * scale;
            result.strips.push({ id: `${crossing.id}:ramp:${band.startM}:${sign}`, ownerId: owner.id,
              start: f.world(add(edge, mul(normal, mid))), end: f.world(add(add(edge, mul(station.tangent, sign * 1.5)), mul(normal, mid))),
              widthM: band.widthM * scale, startLiftM: lift, endLiftM: band.liftM, color: '#88857e' });
          }
        }
        result.status = 'connected'; result.reason = 'Raised crossing joins both sidewalks. Review its location and slopes.';
      } else {
        const entrance = readBuildingEntrance(owner, zones), anchor = entrance && entranceWorldPoint(owner, entrance);
        result.reason = 'Set the entrance position and choose a sidewalk target.';
        if (!entrance || !anchor) continue;
        const street = zones.find(z => z.id === entrance.streetId && z.zone_type === 'road' && visible.has(z.id));
        if (!street) { result.reason = 'The chosen street is missing or hidden. Choose another target.'; continue; }
        const ownerLevel=resolvePreparedSiteTerrainForZone(owner,[...zones],0),streetLevel=resolvePreparedSiteTerrainForZone(street,[...zones],0);
        if(ownerLevel!==null&&streetLevel!==null&&Math.abs(ownerLevel-streetLevel)>.02){
          result.reason='This sidewalk connection changes terrace level. Design a graded approach and retaining-edge opening; the terrace pilot currently connects building and park plots only.';
          continue;
        }
        const section = resolvePilotStreetSectionProfile(street);
        if (!section) { result.reason = 'The chosen street has no supported pedestrian section.'; continue; }
        const scale = section.metricWidthLocked ? (section.targetRowM ?? section.rowM) / section.rowM : effectiveRoadWidth(street.properties) / section.rowM;
        const line = extractRenderableStreetCenterline(street).map(f.local), door = f.local(anchor);
        if (!pointInside(door, owner.coordinates.map(f.local))) { result.reason = 'Keep the entrance inside its building plot.'; continue; }
        const dimensions=rectangleDimensions(owner.coordinates), angle=dimensions.degrees*Math.PI/180;
        const sideX=Math.abs(entrance.xM/entrance.referenceWidthM)>Math.abs(entrance.yM/entrance.referenceDepthM);
        const outward:Point=sideX ? [Math.sign(entrance.xM)*Math.cos(angle),Math.sign(entrance.xM)*Math.sin(angle)]
          : [-Math.sign(entrance.yM)*Math.sin(angle),Math.sign(entrance.yM)*Math.cos(angle)];
        const options: Array<{ point: Point; lift: number; distance: number }> = [];
        let sidewalkBehindEntrance = false, sidewalkInFrontOfEntrance = false;
        for (let i=1;i<line.length;i++) {
          const a=line[i-1], b=line[i], size=length(sub(b,a)); if(size < 0.01) continue;
          const n: Point = [-(b[1]-a[1])/size,(b[0]-a[0])/size];
          for(const band of pedestrianAccessBands(section)) {
            const target=project(door,add(a,mul(n,band.centerM*scale)),add(b,mul(n,band.centerM*scale)));
            const toward=sub(target,door);
            // A front approach cannot pass back through its own building.
            if(!pointInside(target,street.coordinates.map(f.local))) continue;
            if(toward[0]*outward[0]+toward[1]*outward[1]<=0){sidewalkBehindEntrance=true;continue;}
            sidewalkInFrontOfEntrance=true;
            if(length(sub(target,door)) > 30 || !safe(door,target,entrance.widthM,street.id)) continue;
            const crossesOtherBand=line.slice(1).some((end,j)=>{
              const start=line[j], l=length(sub(end,start)); if(l<0.01)return false;
              const normal:Point=[-(end[1]-start[1])/l,(end[0]-start[0])/l];
              return section.bands.filter(v=>v!==band&&v.sourceType!=='setback').some(v=>corridorOverlaps(door,target,[
                add(start,mul(normal,v.startM*scale)),add(end,mul(normal,v.startM*scale)),
                add(end,mul(normal,v.endM*scale)),add(start,mul(normal,v.endM*scale))],entrance.widthM/2));
            });
            if(!crossesOtherBand)options.push({point:target,lift:band.liftM,distance:length(sub(target,door))});
          }
        }
        options.sort((a,b)=>a.distance-b.distance);
        if(!options.length){
          result.reason=!sidewalkInFrontOfEntrance&&sidewalkBehindEntrance
            ? 'This entrance faces away from the selected sidewalk. Choose a step on the street-facing side of the model, or rotate the plot toward the street.'
            : 'No clear approach within 30 m reaches that sidewalk. Check the entrance position or street target.';
          continue;
        }
        const best=options[0];
        result.strips=[{id:`entrance:${owner.id}`,ownerId:owner.id,start:f.world(best.point),end:anchor,widthM:entrance.widthM,
          startLiftM:best.lift,endLiftM:0.025,color:'#c3baa8'}];
        result.status='connected';result.reason='Route reaches the selected sidewalk in plan. Ground and entrance height are checked in 3D.';
      }
    }
  }
  return results;
}
