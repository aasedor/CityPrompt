import registry from '@/data/nativeParks.json';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { envelopeFits, envelopesOverlap } from '@/components/viewer/globe/neighborhoodParkLayout';

export type NativeParkLayout = typeof registry.layouts[number];
export interface NativeParkSelection {
  layout_id: string;
  content_revision: string;
  frame: { longitude: number; latitude: number; yaw: number };
}
export const nativeParkLayouts = registry.layouts;
export const hasNativePark = (zone: Pick<SiteZone, 'properties'>) => zone.properties?.green_space_native_layout != null;
export function readNativePark(zone: Pick<SiteZone, 'properties'>): { layout: NativeParkLayout; selection: NativeParkSelection } | null {
  const selection = zone.properties?.green_space_native_layout as NativeParkSelection | undefined;
  if (!selection?.frame || ![selection.frame.longitude, selection.frame.latitude, selection.frame.yaw].every(Number.isFinite)) return null;
  const layout = nativeParkLayouts.find(p => p.id === selection.layout_id && p.contentRevision === selection.content_revision);
  if (!layout || layout.archetypeId !== zone.properties?.green_space_archetype_id || layout.variantId !== zone.properties?.green_space_selected_variant_id) return null;
  return { layout, selection };
}
/** The browser validates the same finite contract before offering a paid capture.
 * The backend additionally recomputes the canonical recipe hash at submission. */
export function hasExecutableNativeParkRecipe(zone: Pick<SiteZone,'properties'>): boolean {
  const resolved=readNativePark(zone),recipe=zone.properties?.public_realm_lego as Record<string,unknown>|undefined;
  if(!resolved || !recipe || zone.properties?.public_realm_fallback!=null)return false;
  const {layout,selection}=resolved,frame=recipe.frame as NativeParkSelection['frame']|undefined;
  const hashes=recipe.asset_hashes as Record<string,string>|undefined;
  return recipe.schema_version===2 && recipe.kind==='park' && recipe.generator==='park_kit'
    && recipe.family_id==='native_park' && recipe.family_version===1 && recipe.terrain_policy==='prepared_level'
    && recipe.archetype_id===layout.archetypeId && recipe.variant_id===layout.variantId && recipe.mode===layout.mode
    && recipe.layout_id===selection.layout_id && recipe.content_revision===selection.content_revision
    && !!frame && frame.longitude===selection.frame.longitude && frame.latitude===selection.frame.latitude && frame.yaw===selection.frame.yaw
    && !!hashes && Object.keys(hashes).length===Object.keys(layout.assets).length
    && Object.entries(layout.assets).every(([key,asset])=>asset && hashes[key]===asset.sha256)
    && typeof recipe.recipe_hash==='string' && /^[a-f0-9]{64}$/.test(recipe.recipe_hash);
}
export function parkSelection(layout: NativeParkLayout, coordinates: number[][]): NativeParkSelection {
  const [longitude, latitude] = computeCentroid(coordinates);
  const [a,b] = coordinates;
  return { layout_id: layout.id, content_revision: layout.contentRevision, frame: { longitude, latitude,
    yaw: Math.atan2((b[1]-a[1])*METERS_PER_DEG_LAT, (b[0]-a[0])*metersPerDegLon(latitude)) } };
}
export function nativeParkProperties(properties: SiteZoneProperties, layout: NativeParkLayout, coordinates: number[][]): SiteZoneProperties {
  const next = { ...properties };
  for (const key of ['public_realm_trial_asset','validation_fixed_fixture','validation_native_url','park_trio_layout','public_realm_lego','public_realm_fallback']) delete next[key];
  return { ...next, green_space_archetype_id: layout.archetypeId, green_space_selected_variant_id: layout.variantId,
    green_space_native_layout: parkSelection(layout, coordinates), pick_place_automatic_3d: true };
}
export function nativeParkFootprint(selection: NativeParkSelection, layout: NativeParkLayout): number[][] {
  const f = selection.frame, c = Math.cos(f.yaw), s = Math.sin(f.yaw);
  return [[-1,-1],[1,-1],[1,1],[-1,1]].map(([x,y]) => [
    f.longitude + (x*layout.widthM/2*c-y*layout.depthM/2*s)/metersPerDegLon(f.latitude),
    f.latitude + (x*layout.widthM/2*s+y*layout.depthM/2*c)/METERS_PER_DEG_LAT]);
}
/** Reuse the polygon predicate, never infer fit from an axis-aligned box. */
export function nativeParkFitProblem(zone: Pick<SiteZone,'coordinates'|'properties'>): string | null {
  if (!hasNativePark(zone)) return null;
  const resolved = readNativePark(zone);
  if (!resolved) return 'This park layout revision is unavailable. Keep the previous layout.';
  const { layout, selection } = resolved, f = selection.frame;
  const local = (ring: number[][]) => ring.map(p=>({x:(p[0]-f.longitude)*metersPerDegLon(f.latitude), y:(p[1]-f.latitude)*METERS_PER_DEG_LAT}));
  // Shrink only the numerical fit envelope by 2 cm, never the model.
  const footprint = local(nativeParkFootprint(selection,{...layout,widthM:layout.occupiedWidthM-.04,depthM:layout.occupiedDepthM-.04}));
  const holes = zone.properties?.park_exclusion_rings as number[][][] | undefined;
  if (!envelopeFits(footprint,local(zone.coordinates)) || (holes ?? []).some(ring=>envelopesOverlap(footprint,local(ring))))
    return `Keep the complete ${layout.widthM} × ${layout.depthM} m ${layout.label} layout inside the park. Enlarge the parcel or keep the previous layout.`;
  return null;
}
/** Moving/rotating a parcel moves its frame; resizing alone does not scale it. */
export function nativeParkEditProperties(zone: Pick<SiteZone,'coordinates'|'properties'>, coordinates: number[][]): SiteZoneProperties {
  const resolved = readNativePark(zone);
  if (!resolved) return zone.properties ?? {};
  const old = parkSelection(resolved.layout,zone.coordinates).frame, next = parkSelection(resolved.layout,coordinates).frame;
  const delta = next.yaw-old.yaw, c=Math.cos(delta), s=Math.sin(delta), f=resolved.selection.frame;
  const rigid=zone.coordinates.length===coordinates.length && zone.coordinates.every((point,i)=>{
    const x=(point[0]-old.longitude)*metersPerDegLon(old.latitude),y=(point[1]-old.latitude)*METERS_PER_DEG_LAT;
    const nx=(coordinates[i][0]-next.longitude)*metersPerDegLon(next.latitude),ny=(coordinates[i][1]-next.latitude)*METERS_PER_DEG_LAT;
    return Math.hypot(nx-(x*c-y*s),ny-(x*s+y*c))<.05;
  });
  if (!rigid) return zone.properties ?? {};
  const x=(f.longitude-old.longitude)*metersPerDegLon(old.latitude), y=(f.latitude-old.latitude)*METERS_PER_DEG_LAT;
  return {...zone.properties,green_space_native_layout:{...resolved.selection,frame:{
    longitude:next.longitude+(x*c-y*s)/metersPerDegLon(next.latitude), latitude:next.latitude+(x*s+y*c)/METERS_PER_DEG_LAT,yaw:f.yaw+delta}}};
}
