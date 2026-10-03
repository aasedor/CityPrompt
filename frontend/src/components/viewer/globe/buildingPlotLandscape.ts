import polygonClipping, { type MultiPolygon, type Pair } from 'polygon-clipping';
import type { SiteZone } from '@/types';
import { assetForZone } from '@/features/pickPlace/catalogue';
import { buildingEdgeContract } from '@/features/pickPlace/buildingPlacementEdges';
import { rectangleAt, rectangleDimensions } from '@/features/pickPlace/geometry';
import { landscapeKeepClear } from '@/features/siteLandscape/siteLandscape';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '../mapEngine/geoUtils';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { getResidualLandscapeRecipe } from './residualLandscape';
import { buildingLandscapeNotes } from './buildingLandscapeNotes';

export type BuildingGardenStyle = 'residential' | 'urban' | 'civic' | 'service';
export interface BuildingPlotLandscape {
  zoneId: string;
  style: BuildingGardenStyle;
  design: ReturnType<typeof buildingLandscapeNotes>;
  drawSurface: boolean;
  origin: [number, number];
  height: number;
  /** Local east/north metres, clipped to the plot and neighbouring objects. */
  surface: MultiPolygon;
  beds: MultiPolygon;
  shrubs: Pair[];
}

/** Some historic review cards have a generic housing category. Resolve their
 * explicit building use before using that broad catalogue grouping. */
export function buildingGardenStyle(zone: Pick<SiteZone, 'properties'>): BuildingGardenStyle {
  const p = zone.properties ?? {};
  const identity = `${p.building_archetype_id ?? ''} ${p.development_selected_variant_id ?? ''}`;
  if (/industrial|warehouse|logistics|workshop/i.test(identity)) return 'service';
  if (/museum|library|school|hall|station|cinema|aquatic|civic/i.test(identity)) return 'civic';
  if (/cafe|café|market|brewhouse|office|loft|mixed|tower|midrise|mid_rise|hotel|moderne/i.test(identity)) return 'urban';
  const group = assetForZone(zone)?.calgaryGuide?.groupId;
  if (group === 'civic' || group === 'infrastructure') return 'civic';
  if (['offices', 'shops', 'mixed', 'towers', 'apartments', 'hotels'].includes(group ?? '')) return 'urban';
  return 'residential';
}

function closed(ring: Pair[]): Pair[] {
  return ring.length ? [...ring, ring[0]] : ring;
}
function rect(x0: number, y0: number, x1: number, y1: number): Pair[] {
  return closed([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]);
}
function validRing(ring: number[][]): boolean {
  return ring.length >= 3 && ring.every(p => p.length >= 2 && Number.isFinite(p[0]) && Number.isFinite(p[1]));
}

export function buildingGardenEnvelope(zone: SiteZone): { width: number; depth: number } | null {
  const edge = buildingEdgeContract(zone);
  if (edge) return edge;
  // Fixed review models have measured complete envelopes but do not all have
  // an abutment contract. Match the exact binding and rectangular native axes.
  const asset = assetForZone(zone), p = zone.properties;
  if (!asset?.nativeDimensions || asset.reshapeMode !== 'fixed_native' || p?.validation_fixed_fixture !== true
    || p.native_plot_axes !== true || p.native_home_plot === true || zone.coordinates.length !== 4
    || p.development_selected_variant_id !== asset.model.variantId || p.pick_place_model_revision !== asset.model.revision
    || Number(p.building_footprint_scale ?? 1) !== 1) return null;
  const frame = rectangleDimensions(zone.coordinates);
  const expected = rectangleAt(frame.center, frame.width, frame.depth, frame.degrees);
  if (zone.coordinates.some((p, i) => Math.hypot((p[0] - expected[i][0]) * metersPerDegLon(frame.center[1]),
    (p[1] - expected[i][1]) * METERS_PER_DEG_LAT) > .01)) return null;
  return { width: asset.nativeDimensions[0], depth: asset.nativeDimensions[1] };
}

/** Shared display landscaping, derived from the current plot on each edit.
 * It never changes model bounds, saved geometry, terrain or access contracts.
 * Unknown/repeated models receive ground cover only: no guessed shrub layout.
 */
export function buildingPlotLandscapes(zones: SiteZone[], terrainHeight: number): BuildingPlotLandscape[] {
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary || boundary.properties?.community_3d_mask_existing_tiles === false
    || boundary.properties?.terrain_strategy === 'landscape') return [];
  const recipe = getResidualLandscapeRecipe(boundary);
  // An explicitly authored continuous site image already owns these pixels.
  if (recipe?.surface_image_url && recipe.surface_mode === 'site_base') return [];
  const corridors = landscapeKeepClear(zones).filter(validRing);
  const physical = zones.filter(z => resolveCommunity3DKind(z) !== null && validRing(z.coordinates));
  return physical.flatMap(zone => {
    if (resolveCommunity3DKind(zone) !== 'building') return [];
    const height = resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight);
    if (height === null) return [];
    const origin: Pair = [zone.coordinates.reduce((s, p) => s + p[0], 0) / zone.coordinates.length,
      zone.coordinates.reduce((s, p) => s + p[1], 0) / zone.coordinates.length];
    const east = metersPerDegLon(origin[1]);
    const local = (ring: number[][]): Pair[] => closed(ring.map(p => [(p[0] - origin[0]) * east, (p[1] - origin[1]) * METERS_PER_DEG_LAT]));
    try {
      const plot: MultiPolygon = [[local(zone.coordinates)]];
      // Released edge padding may overlap a neighbouring road, park or plot.
      // Use full polygons (including intersections), never only corner tests.
      const exclusions = [...physical.filter(z => z.id !== zone.id).map(z => local(z.coordinates)), ...corridors.map(local)];
      const surface = exclusions.length ? polygonClipping.difference(plot, ...exclusions.map(r => [r])) : plot;
      if (!surface.length) return [];
      const style = buildingGardenStyle(zone);
      const result: BuildingPlotLandscape = { zoneId: zone.id, style, design: buildingLandscapeNotes(zone),
        drawSurface: !recipe, origin, height, surface, beds: [], shrubs: [] };
      const contract = buildingGardenEnvelope(zone);
      if (!contract || style === 'service') return [result];
      const frame = rectangleDimensions(zone.coordinates), angle = frame.degrees * Math.PI / 180;
      const c = Math.cos(angle), s = Math.sin(angle);
      const rotate = ([x, y]: Pair): Pair => [x * c - y * s, x * s + y * c];
      // Protect the complete authored model, including stairs/canopies, plus
      // a continuous 1.2 m circulation strip on every side. Front/rear ends
      // stay open for entrances whose exact positions have not been measured.
      const inner = contract.width / 2 + 1.2, outer = frame.width / 2 - .25;
      const halfRun = Math.min(contract.depth / 2 - 1.5, frame.depth / 2 - 2);
      if (outer - inner < .65 || halfRun < 1) return [result];
      const bands = [-1, 1].map(side => rect(side === 1 ? inner : -outer, -halfRun,
        side === 1 ? outer : -inner, halfRun).map(rotate));
      result.beds = polygonClipping.intersection(surface, bands.map(r => [r]));
      // Sparse, low planting, bounded per building. Check the complete canopy
      // and an extra margin against clipped beds and shared access corridors.
      const spacing = result.design.planting === 'grasses' ? 1.1 : result.design.planting === 'evergreen' ? 1.35 : 1.5;
      for (const side of [-1, 1]) for (let y = -halfRun + .55; y <= halfRun - .55 && result.shrubs.length < 64; y += spacing) {
        const point = rotate([side * (inner + Math.min(outer - inner, 1.5) / 2), y]);
        const disk = Array.from({ length: 16 }, (_, i): Pair => [point[0] + .42 * Math.cos(i * Math.PI / 8), point[1] + .42 * Math.sin(i * Math.PI / 8)]);
        if (polygonClipping.difference([closed(disk)], result.beds).length === 0) result.shrubs.push(point);
      }
      return [result];
    } catch {
      // Malformed legacy geometry retains its original surface and remains editable.
      return [];
    }
  });
}
