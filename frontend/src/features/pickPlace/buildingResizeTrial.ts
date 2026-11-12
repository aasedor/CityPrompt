import contract from '@/data/buildingResizeTrial.json';
import type { SiteZoneProperties } from '@/types';
import { computeCentroid, METERS_PER_DEG_LAT, metersPerDegLon, polygonAreaM2 } from '@/components/viewer/mapEngine/geoUtils';
import type { CatalogueAsset, PlaceAsset } from './assetRegistry';
import { parkOutlineDimensions } from './parkOutline';

/**
 * Building resize pilot. One mid-rise apartment block, two ways to fit it:
 *
 *  - Exact model: the reviewed GLB stretched independently in width and depth
 *    inside a bounded band. Height is never scaled.
 *  - Shape freely: the student draws the outline; the building compiles to
 *    planned massing dressed with floor lines and repeating window bays.
 *
 * Everything is behind VITE_ENABLE_BUILDING_RESIZE_TRIAL (default off). With
 * the flag off every function here reports "no trial" and callers keep their
 * existing behaviour. The server validates every saved state again.
 */
export const RESIZE_TRIAL_PROGRAM_ID = contract.id;

/**
 * Every tunable of the pilot, named. The values live in ONE file,
 * src/data/buildingResizeTrial.json, which the backend mirrors byte for byte
 * (run `python scripts/building_resize_trial.py --write-mirror` after editing).
 */
export const RESIZE_TRIAL_SETTINGS = {
  /** Exact model: smallest and largest stretch per axis (0.70 = 70%). */
  scaleMin: contract.stretch.minimum_scale,
  scaleMax: contract.stretch.maximum_scale,
  /** Exact model: step of the width/depth controls, as a fraction. */
  scaleStep: contract.stretch.step,
  /** Fit building to plot: clear space kept on each side, in metres.
   *  null keeps the model's own authored plot margin. */
  fitPlotMarginM: contract.stretch.fit_plot_margin_m as number | null,
  /** Shape freely: smallest outline a student may draw. */
  minWidthM: contract.shape_freely.minimum_width_m,
  minDepthM: contract.shape_freely.minimum_depth_m,
  minAreaM2: contract.shape_freely.minimum_area_m2,
  /** Shape freely: largest outline extent and corner count. */
  maxSizeM: contract.shape_freely.maximum_size_m,
  maxOutlinePoints: contract.shape_freely.maximum_outline_points,
  /** Massing dressing: fixed window bay module. Bays repeat; they never stretch. */
  bayModuleM: contract.massing.bay_module_m,
  windowWidthM: contract.massing.window_width_m,
  windowHeightM: contract.massing.window_height_m,
  /** Window sill height above each floor line. */
  windowSillM: contract.massing.window_sill_m,
  /** Solid wall kept at both ends of every facade before the first bay. */
  wallEndMarginM: contract.massing.wall_end_margin_m,
  /** Floor line spacing in metres. null draws one line per storey at the
   *  building's own floor height. */
  floorLineSpacingM: contract.massing.floor_line_spacing_m as number | null,
  /** Height of each floor line band. */
  floorLineHeightM: contract.massing.floor_line_height_m,
  /** How far lines and windows stand off the wall (avoids z-fighting). */
  surfaceOffsetM: contract.massing.surface_offset_m,
  floorLineColor: contract.massing.floor_line_color,
  windowColor: contract.massing.window_color,
} as const;

export type ResizeTrialMode = 'exact_model' | 'shape_freely';
export type ResizeTrialReason = 'stretch_out_of_band';

export interface ResizeTrialFamily {
  assetId: string;
  label: string;
  archetypeId: string;
  variantId: string;
  candidate: string;
  nativeWidthM: number;
  nativeDepthM: number;
  nativeHeightM: number;
  nativeStoreys: number;
  /** The catalogue's placement plot around the unscaled model. */
  plotWidthM: number;
  plotDepthM: number;
}

const FAMILIES: ResizeTrialFamily[] = contract.families.map(row => ({
  assetId: row.asset_id, label: row.label, archetypeId: row.archetype_id,
  variantId: row.variant_id, candidate: row.candidate,
  nativeWidthM: row.native_dimensions_m[0], nativeDepthM: row.native_dimensions_m[1],
  nativeHeightM: row.native_dimensions_m[2], nativeStoreys: row.native_storeys,
  plotWidthM: row.placement_plot_m[0], plotDepthM: row.placement_plot_m[1],
}));

/** Read at call time so a test can switch the flag without reloading modules. */
export function buildingResizeTrialEnabled(): boolean {
  return import.meta.env.VITE_ENABLE_BUILDING_RESIZE_TRIAL === 'true';
}

/** The exact asset, variant and revision the pilot covers. Nothing else. */
export function resizeTrialFamilyForAsset(
  asset: Pick<CatalogueAsset, 'id' | 'model'> | undefined,
  enabled = buildingResizeTrialEnabled(),
): ResizeTrialFamily | undefined {
  if (!enabled || !asset) return undefined;
  return FAMILIES.find(family => family.assetId === asset.id
    && family.variantId === asset.model.variantId && family.candidate === asset.model.revision);
}

export function resizeTrialFamilyForProperties(
  properties: SiteZoneProperties | null | undefined,
  enabled = buildingResizeTrialEnabled(),
): ResizeTrialFamily | undefined {
  if (!enabled || !properties) return undefined;
  return FAMILIES.find(family => family.assetId === properties.pick_place_asset
    && family.variantId === properties.development_selected_variant_id
    && family.candidate === properties.pick_place_model_revision);
}

export interface ResizeTrialState {
  family: ResizeTrialFamily;
  mode: ResizeTrialMode;
  widthScale: number;
  depthScale: number;
  /** False until the student first applies a trial control. An undeclared
   *  building is saved, planned and rendered exactly as before the pilot. */
  declared: boolean;
  reason?: ResizeTrialReason;
}

export const roundResizeTrialScale = (scale: number) => Math.round(scale * 10000) / 10000;

export function resizeTrialScaleInBand(scale: unknown): boolean {
  const value = Number(scale);
  return typeof scale !== 'boolean' && scale != null && scale !== '' && Number.isFinite(value)
    && value >= RESIZE_TRIAL_SETTINGS.scaleMin - 1e-9 && value <= RESIZE_TRIAL_SETTINGS.scaleMax + 1e-9;
}

/** The saved trial state of a building, or null when the pilot does not apply. */
export function readResizeTrialState(
  properties: SiteZoneProperties | null | undefined,
  enabled = buildingResizeTrialEnabled(),
): ResizeTrialState | null {
  const family = resizeTrialFamilyForProperties(properties, enabled);
  if (!family || !properties) return null;
  if (properties.building_footprint_program_id !== RESIZE_TRIAL_PROGRAM_ID) {
    return { family, mode: 'exact_model', widthScale: 1, depthScale: 1, declared: false };
  }
  if (properties.building_footprint_mode === 'shape_freely') {
    return { family, mode: 'shape_freely', widthScale: 1, depthScale: 1, declared: true,
      ...(properties.building_footprint_mode_reason === 'stretch_out_of_band'
        ? { reason: 'stretch_out_of_band' as const } : {}) };
  }
  const width = properties.building_footprint_width_scale, depth = properties.building_footprint_depth_scale;
  return { family, mode: 'exact_model', declared: true,
    widthScale: resizeTrialScaleInBand(width) ? Number(width) : 1,
    depthScale: resizeTrialScaleInBand(depth) ? Number(depth) : 1 };
}

/** True when the saved building is an explicit freely shaped massing. */
export function isResizeTrialShapeFreely(
  properties: SiteZoneProperties | null | undefined, enabled = buildingResizeTrialEnabled(),
): boolean {
  return readResizeTrialState(properties, enabled)?.mode === 'shape_freely';
}

/** A declared Exact model stretch: its target is the stretched building. */
export function resizeTrialStretch(
  properties: SiteZoneProperties | null | undefined, enabled = buildingResizeTrialEnabled(),
): { programId: string; widthM: number; depthM: number; widthScale: number; depthScale: number } | null {
  const state = readResizeTrialState(properties, enabled);
  if (!state?.declared || state.mode !== 'exact_model') return null;
  return { programId: RESIZE_TRIAL_PROGRAM_ID, widthScale: state.widthScale, depthScale: state.depthScale,
    ...resizeTrialBuildingSize(state.family, state.widthScale, state.depthScale) };
}

/** Independent axes are never expressed through the uniform house-pilot field. */
export function resizeTrialChangesEnvelope(properties: SiteZoneProperties | null | undefined): boolean {
  if (properties?.building_footprint_program_id !== RESIZE_TRIAL_PROGRAM_ID) return false;
  if (properties.building_footprint_mode !== 'exact_model') return true;
  const width = Number(properties.building_footprint_width_scale ?? 1);
  const depth = Number(properties.building_footprint_depth_scale ?? 1);
  return !(width === 1 && depth === 1);
}

export function resizeTrialBuildingSize(family: ResizeTrialFamily, widthScale: number, depthScale: number) {
  return { widthM: family.nativeWidthM * widthScale, depthM: family.nativeDepthM * depthScale };
}

/** Clear space kept on each side of the building inside its plot. */
export function resizeTrialPlotMargins(family: ResizeTrialFamily) {
  const override = RESIZE_TRIAL_SETTINGS.fitPlotMarginM;
  if (override != null) return { widthM: override, depthM: override };
  return { widthM: Math.max(0, (family.plotWidthM - family.nativeWidthM) / 2),
    depthM: Math.max(0, (family.plotDepthM - family.nativeDepthM) / 2) };
}

/** The smallest plot that still holds a building at the given stretch. */
export function resizeTrialPlotFor(family: ResizeTrialFamily, widthScale: number, depthScale: number) {
  const margin = resizeTrialPlotMargins(family), size = resizeTrialBuildingSize(family, widthScale, depthScale);
  return { widthM: size.widthM + 2 * margin.widthM, depthM: size.depthM + 2 * margin.depthM };
}

/** A saved plot drifts by millimetres when it is moved or turned on the globe.
 *  Within this distance the building still counts as fitting its plot. */
const PLOT_FIT_TOLERANCE_M = 0.05;

/** Stretch that fills a plot, keeping the margin. Rounded down so the
 *  building never overruns; deliberately NOT clamped to the band. */
export function fitResizeTrialScalesToPlot(family: ResizeTrialFamily, plotWidthM: number, plotDepthM: number) {
  const margin = resizeTrialPlotMargins(family);
  const fit = (plotM: number, marginM: number, nativeM: number) => {
    const raw = (plotM - 2 * marginM) / nativeM;
    // A plot that is the model's own size (give or take drift) is exactly 100%.
    if (Math.abs(raw - 1) * nativeM <= PLOT_FIT_TOLERANCE_M) return 1;
    return Math.floor(raw * 10000 + 1e-3) / 10000;
  };
  return { widthScale: fit(plotWidthM, margin.widthM, family.nativeWidthM),
    depthScale: fit(plotDepthM, margin.depthM, family.nativeDepthM) };
}

export type ResizeTrialStretchDecision =
  | { kind: 'exact_model'; widthScale: number; depthScale: number }
  | { kind: 'shape_freely'; widthM: number; depthM: number; reason: ResizeTrialReason };

/** Inside the band the exact model stretches. Outside it the building hands
 *  over to Shape freely at the requested size, and says why. */
export function decideResizeTrialStretch(family: ResizeTrialFamily, widthM: number, depthM: number): ResizeTrialStretchDecision {
  const widthScale = roundResizeTrialScale(widthM / family.nativeWidthM);
  const depthScale = roundResizeTrialScale(depthM / family.nativeDepthM);
  if (resizeTrialScaleInBand(widthScale) && resizeTrialScaleInBand(depthScale)) {
    return { kind: 'exact_model', widthScale, depthScale };
  }
  return { kind: 'shape_freely', widthM, depthM, reason: 'stretch_out_of_band' };
}

/** Same rectangle maths as geometry.rectangleAt, kept local to avoid a cycle. */
export function resizeTrialRectangle(center: number[], widthM: number, depthM: number, degrees: number): number[][] {
  const yaw = degrees * Math.PI / 180, c = Math.cos(yaw), s = Math.sin(yaw);
  return [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([x, y]) => [
    center[0] + (x * widthM / 2 * c - y * depthM / 2 * s) / metersPerDegLon(center[1]),
    center[1] + (x * widthM / 2 * s + y * depthM / 2 * c) / METERS_PER_DEG_LAT,
  ]);
}

/** Width along the first drawn edge, depth across it, plus centre and turn.
 *  The server measures a freely shaped outline in this same frame. */
export function resizeTrialOutlineFrame(coordinates: number[][]) {
  if (coordinates.length === 4) {
    // A rectangle reads back exactly what resizeTrialRectangle wrote, so
    // repeated edits never creep in size, position or rotation.
    const center = computeCentroid(coordinates), east = metersPerDegLon(center[1]);
    const dx = (coordinates[1][0] - coordinates[0][0]) * east;
    const dy = (coordinates[1][1] - coordinates[0][1]) * METERS_PER_DEG_LAT;
    return { widthM: Math.hypot(dx, dy), degrees: Math.atan2(dy, dx) * 180 / Math.PI, center,
      depthM: Math.hypot((coordinates[2][0] - coordinates[1][0]) * east, (coordinates[2][1] - coordinates[1][1]) * METERS_PER_DEG_LAT) };
  }
  const { width, depth, degrees, center } = parkOutlineDimensions(coordinates);
  return { widthM: width, depthM: depth, degrees, center };
}

type Entrance = { xM?: unknown; yM?: unknown; referenceWidthM?: unknown; referenceDepthM?: unknown; fixedNative?: unknown };

/** The entrance anchor is fixed to the model, so it moves with a stretch.
 *  Its reference plot becomes the smallest plot that holds the new size. */
function stretchedEntrance(entrance: unknown, family: ResizeTrialFamily,
  from: { widthScale: number; depthScale: number }, to: { widthScale: number; depthScale: number }): unknown {
  const value = entrance as Entrance | null | undefined;
  if (!value || typeof value !== 'object' || !Number.isFinite(Number(value.xM)) || !Number.isFinite(Number(value.yM))) return entrance;
  const round = (number: number) => Math.round(number * 1000) / 1000;
  const plot = resizeTrialPlotFor(family, to.widthScale, to.depthScale);
  return { ...value,
    xM: round(Number(value.xM) * to.widthScale / from.widthScale),
    yM: round(Number(value.yM) * to.depthScale / from.depthScale),
    ...(value.fixedNative === true ? { referenceWidthM: plot.widthM, referenceDepthM: plot.depthM } : {}) };
}

/** The reviewed automatic entrance for the unscaled model, as first placed. */
function reviewedEntrance(asset: PlaceAsset | undefined) {
  const snap = asset?.entranceSnap;
  if (!asset || !snap) return undefined;
  return { version: 1, automatic: true, sourceVariantId: asset.model.variantId,
    ...(asset.model.revision ? { sourceRevision: asset.model.revision } : {}), xM: snap.xM, yM: snap.yM,
    referenceWidthM: snap.plotWidthM, referenceDepthM: snap.plotDepthM, widthM: snap.widthM,
    scaleWithPlot: false, streetId: '', heightAboveBaseM: 0, fixedNative: true };
}

/** Saved properties for an Exact model stretch. `asset` supplies the reviewed
 *  entrance when the building returns from Shape freely, which has none. */
export function exactModelProperties(properties: SiteZoneProperties, family: ResizeTrialFamily,
  widthScale: number, depthScale: number, asset?: PlaceAsset): SiteZoneProperties {
  const previous = readResizeTrialState(properties, true);
  const from = previous?.mode === 'exact_model' ? previous : { widthScale: 1, depthScale: 1 };
  const to = { widthScale: roundResizeTrialScale(widthScale), depthScale: roundResizeTrialScale(depthScale) };
  const entrance = previous?.mode === 'shape_freely' || properties.pedestrian_building_entrance == null
    ? stretchedEntrance(reviewedEntrance(asset), family, { widthScale: 1, depthScale: 1 }, to)
    : stretchedEntrance(properties.pedestrian_building_entrance, family, from, to);
  return { ...properties,
    building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID,
    building_footprint_mode: 'exact_model',
    building_footprint_width_scale: to.widthScale,
    building_footprint_depth_scale: to.depthScale,
    building_footprint_mode_reason: undefined,
    building_geometry_basis: 'placement_plot',
    native_plot_axes: true,
    pedestrian_building_entrance: entrance ?? undefined };
}

/** Saved properties for Shape freely. Archetype, variant, storeys, floor
 *  height and height are untouched; only the footprint contract changes. */
export function shapeFreelyProperties(properties: SiteZoneProperties, reason?: ResizeTrialReason): SiteZoneProperties {
  return { ...properties,
    building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID,
    building_footprint_mode: 'shape_freely',
    building_footprint_width_scale: undefined,
    building_footprint_depth_scale: undefined,
    building_footprint_mode_reason: reason,
    // The drawn outline is now the floor plate itself, not a plot around a model.
    building_geometry_basis: 'drawn_footprint',
    native_plot_axes: true,
    // Massing has no reviewed doorway. The reviewed entrance returns with Exact model.
    pedestrian_building_entrance: undefined };
}

/** Immediate feedback; the server measures the saved outline again. */
export function resizeTrialOutlineProblem(coordinates: number[][]): string | null {
  const settings = RESIZE_TRIAL_SETTINGS;
  if (coordinates.length < 3 || coordinates.some(point => !Number.isFinite(point[0] + point[1]))) {
    return 'A freely shaped building needs at least three corners.';
  }
  if (coordinates.length > settings.maxOutlinePoints) {
    return `A freely shaped building can have at most ${settings.maxOutlinePoints} corners.`;
  }
  const { widthM, depthM } = resizeTrialOutlineFrame(coordinates);
  if (widthM < settings.minWidthM - 0.005 || depthM < settings.minDepthM - 0.005) {
    return `A freely shaped building must be at least ${settings.minWidthM} m wide and ${settings.minDepthM} m deep.`;
  }
  if (polygonAreaM2(coordinates) < settings.minAreaM2 - 0.005) {
    return `A freely shaped building needs a footprint of at least ${settings.minAreaM2} m².`;
  }
  if (Math.max(widthM, depthM) > settings.maxSizeM + 0.005) {
    return `A freely shaped building can be at most ${settings.maxSizeM} m across.`;
  }
  return null;
}

export interface ResizeTrialFigures {
  footprintAreaM2: number;
  storeys: number;
  floorAreaM2: number;
  /** Floor area ÷ site area. null without a site boundary. */
  far: number | null;
}

/** Live figures for a freely shaped building: the outline is its floor plate. */
export function resizeTrialFigures(coordinates: number[][], storeys: unknown, siteAreaM2?: number | null): ResizeTrialFigures {
  const count = Number(storeys);
  const floors = Number.isInteger(count) && count > 0 ? count : 0;
  const footprintAreaM2 = coordinates.length >= 3 ? polygonAreaM2(coordinates) : 0;
  const floorAreaM2 = footprintAreaM2 * floors;
  return { footprintAreaM2, storeys: floors, floorAreaM2,
    far: siteAreaM2 && siteAreaM2 > 0 ? floorAreaM2 / siteAreaM2 : null };
}

/** The asset as the editing tools must see it for this saved building. */
export function withResizeTrial(asset: PlaceAsset, properties: SiteZoneProperties | null | undefined,
  enabled = buildingResizeTrialEnabled()): PlaceAsset {
  const family = resizeTrialFamilyForAsset(asset, enabled);
  const state = family ? readResizeTrialState(properties, enabled) : null;
  if (!family || !state) return asset;
  const settings = RESIZE_TRIAL_SETTINGS;
  if (state.mode === 'shape_freely') {
    return { ...asset, reshapeMode: 'authored_footprint', footprintProgram: undefined, entranceSnap: undefined,
      minWidth: settings.minWidthM, minDepth: settings.minDepthM,
      maxSize: Math.max(settings.maxSizeM, asset.maxSize), maxWidth: undefined, maxDepth: undefined,
      reshapeDescription: 'Shape freely: drag the white corners or add an outline point. Storeys and floor height stay as the exact model. Window bays repeat at a fixed width; they never stretch.' };
  }
  // Rounded up to 0.1 m: the plot inputs step in tenths, and a ragged minimum
  // would make the browser refuse round sizes such as 30 m.
  const tenth = (value: number) => Math.ceil(value * 10 - 1e-6) / 10;
  const least = resizeTrialPlotFor(family, settings.scaleMin, settings.scaleMin);
  const smallest = { widthM: tenth(least.widthM), depthM: tenth(least.depthM) };
  return { ...asset,
    footprintProgram: { id: RESIZE_TRIAL_PROGRAM_ID, mode: 'independent_horizontal_scale',
      nativeWidthM: family.nativeWidthM, nativeDepthM: family.nativeDepthM,
      minScale: settings.scaleMin, maxScale: settings.scaleMax, defaultScale: 1, step: settings.scaleStep },
    // The plot may shrink until the model reaches its smallest stretch.
    minWidth: Math.min(asset.minWidth, smallest.widthM), minDepth: Math.min(asset.minDepth, smallest.depthM),
    reshapeDescription: 'Resize the plot, then use Fit building to plot or set the building width and depth. The exact model stretches 70–140%; its height and storeys never change.' };
}

/** A plot edit in Exact model: when the building no longer fits the new plot
 *  it is squeezed to fit, inside the band. Returns the properties to save
 *  with the new coordinates, or null when nothing needs to change. */
export function resizeTrialPlotReshape(zone: { coordinates: number[][]; properties?: SiteZoneProperties | null },
  coordinates: number[][], asset?: PlaceAsset, enabled = buildingResizeTrialEnabled()): SiteZoneProperties | null {
  const state = readResizeTrialState(zone.properties, enabled);
  if (!state || state.mode !== 'exact_model' || coordinates.length !== 4 || !zone.properties) return null;
  const plot = resizeTrialOutlineFrame(coordinates);
  const needed = resizeTrialPlotFor(state.family, state.widthScale, state.depthScale);
  const fit = fitResizeTrialScalesToPlot(state.family, plot.widthM, plot.depthM);
  const clamp = (value: number) => Math.max(RESIZE_TRIAL_SETTINGS.scaleMin, Math.min(RESIZE_TRIAL_SETTINGS.scaleMax, value));
  // Moving or turning a plot must never nudge the building; only a plot that
  // is genuinely too small squeezes that axis.
  const widthScale = plot.widthM + PLOT_FIT_TOLERANCE_M >= needed.widthM ? state.widthScale : clamp(fit.widthScale);
  const depthScale = plot.depthM + PLOT_FIT_TOLERANCE_M >= needed.depthM ? state.depthScale : clamp(fit.depthScale);
  if (widthScale === state.widthScale && depthScale === state.depthScale) return null;
  return exactModelProperties(zone.properties, state.family, widthScale, depthScale, asset);
}

/** Floor lines and window bays for a freely shaped building's massing, or
 *  null for every other building. Storeys come from the saved building, so
 *  the lines sit exactly on its own floor height. */
export function resizeTrialMassingDressing(
  properties: SiteZoneProperties | null | undefined, enabled = buildingResizeTrialEnabled(),
) {
  const state = readResizeTrialState(properties, enabled);
  if (!state || state.mode !== 'shape_freely') return null;
  const saved = Number(properties?.floor_count ?? properties?.floors);
  const settings = RESIZE_TRIAL_SETTINGS;
  return {
    storeys: Number.isInteger(saved) && saved > 0 ? saved : state.family.nativeStoreys,
    floorLineSpacingM: settings.floorLineSpacingM,
    bayModuleM: settings.bayModuleM,
    windowWidthM: settings.windowWidthM,
    windowHeightM: settings.windowHeightM,
    windowSillM: settings.windowSillM,
    wallEndMarginM: settings.wallEndMarginM,
    floorLineHeightM: settings.floorLineHeightM,
    surfaceOffsetM: settings.surfaceOffsetM,
    floorLineColor: settings.floorLineColor,
    windowColor: settings.windowColor,
  };
}
