import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import type { SiteZone, SiteZoneProperties } from '@/types';
import contract from '@/data/buildingResizeTrial.json';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { placedNativeFootprints } from '@/components/viewer/globe/buildingGroundContact';
import { legoInstanceTransform } from '@/components/viewer/globe/legoGlobePlacement';
import { buildPlanRequestForItem, deriveItems } from '@/features/legoAssembly/communityCompiler';
import { isNativeClayPlan, isResizeTrialPlan } from '@/features/legoAssembly/nativeClayPlacement';
import type { LegoAssemblyPlan } from '@/features/legoAssembly/legoAssemblyApi';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { assetForZone, placeAsset, placementProperties } from './catalogue';
import { hasFixedBuildingFootprint } from './buildingFootprintProgram';
import { buildingEdgeContract, buildingPlacementEnvelope } from './buildingPlacementEdges';
import { rectangleAt, rectangleDimensions } from './geometry';
import { nativeBuildingContract } from './nativeBuildingContract';
import { entranceWorldPoint, readBuildingEntrance, resolvePedestrianConnections, type BuildingEntrance } from './pedestrianConnections';
import { representationNotice } from './representationNotice';
import { streetFacingDegrees } from './streetFacing';
import edges from '@/data/buildingPlacementEdges.json';
import {
  RESIZE_TRIAL_PROGRAM_ID, RESIZE_TRIAL_SETTINGS, buildingResizeTrialEnabled, decideResizeTrialStretch,
  exactModelProperties, fitResizeTrialScalesToPlot, isResizeTrialShapeFreely, readResizeTrialState,
  resizeTrialChangesEnvelope, resizeTrialFamilyForAsset, resizeTrialFigures, resizeTrialMassingDressing,
  resizeTrialOutlineProblem, resizeTrialPlotFor, resizeTrialPlotMargins, resizeTrialPlotReshape,
  resizeTrialRectangle, resizeTrialStretch, shapeFreelyProperties, withResizeTrial,
} from './buildingResizeTrial';

const ASSET_ID = 'final_seniors_apartments';
const NATIVE_W = 32.36000061035156, NATIVE_D = 17.980000495910645;
const ll = (x: number, y: number) => [-114 + x / metersPerDegLon(51), 51 + y / METERS_PER_DEG_LAT];
const asset = () => placeAsset(ASSET_ID);
const placed = (properties: SiteZoneProperties = placementProperties(asset()),
  coordinates = rectangleAt(ll(0, 0), 36.4, 22, 0)): SiteZone => ({
  id: 'midrise', project_id: 'project', zone_type: 'building', coordinates, properties,
  name: 'Mid-rise', color: '#fff', sort_order: 0, created_at: 'now', updated_at: 'now',
} as SiteZone);
const on = () => vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL', 'true');
afterEach(() => vi.unstubAllEnvs());

describe('flag off (the default)', () => {
  it('leaves the chosen mid-rise exactly as the catalogue published it', () => {
    expect(buildingResizeTrialEnabled()).toBe(false);
    const zone = placed();
    expect(readResizeTrialState(zone.properties)).toBeNull();
    const resolved = assetForZone(zone)!;
    expect(resolved).toBe(asset());
    expect(resolved.reshapeMode).toBe('fixed_native');
    expect(resolved.footprintProgram).toBeUndefined();
    expect(hasFixedBuildingFootprint(resolved)).toBe(true);
    expect([resolved.minWidth, resolved.minDepth]).toEqual([36.4, 22]);
  });

  it('ignores saved trial properties everywhere a building is planned or drawn', () => {
    on();
    const stretched = exactModelProperties(placementProperties(asset()), resizeTrialFamilyForAsset(asset())!, 0.8, 1.2, asset());
    const freely = shapeFreelyProperties(placementProperties(asset()));
    vi.unstubAllEnvs();
    for (const properties of [stretched, freely]) {
      const zone = placed(properties, rectangleAt(ll(0, 0), 40, 30, 0));
      expect(readResizeTrialState(properties)).toBeNull();
      expect(resizeTrialStretch(properties)).toBeNull();
      expect(isResizeTrialShapeFreely(properties)).toBe(false);
      expect(resizeTrialMassingDressing(properties)).toBeNull();
      expect(assetForZone(zone)).toBe(asset());
      const item = deriveItems([zone])[0];
      expect(item.explicitMassing).toBeUndefined();
      // The drawn plot stays the target, as for any unknown programme.
      expect([item.targets.width_m, item.targets.depth_m]).toEqual([40, 30]);
      expect(buildPlanRequestForItem(item)).not.toHaveProperty('footprint_program_id');
    }
  });
});

describe('flag on', () => {
  beforeEach(on);
  const family = () => resizeTrialFamilyForAsset(asset())!;

  it('names every tunable once, from the shared tuning file', () => {
    expect(RESIZE_TRIAL_PROGRAM_ID).toBe('building-resize-trial-v001');
    expect([RESIZE_TRIAL_SETTINGS.scaleMin, RESIZE_TRIAL_SETTINGS.scaleMax]).toEqual([0.7, 1.4]);
    expect(RESIZE_TRIAL_SETTINGS).toMatchObject({
      scaleStep: contract.stretch.step, minWidthM: contract.shape_freely.minimum_width_m,
      minDepthM: contract.shape_freely.minimum_depth_m, bayModuleM: contract.massing.bay_module_m,
      windowWidthM: contract.massing.window_width_m, floorLineSpacingM: contract.massing.floor_line_spacing_m,
      floorLineHeightM: contract.massing.floor_line_height_m,
    });
    expect(contract.stretch.vertical_scale).toBe(1);
  });

  it('covers one exact asset, variant and revision and nothing beside it', () => {
    const trial = asset();
    expect(family()).toMatchObject({ assetId: ASSET_ID, variantId: trial.model.variantId, candidate: trial.model.revision,
      nativeStoreys: 5, plotWidthM: trial.width, plotDepthM: trial.depth });
    expect([family().nativeWidthM, family().nativeDepthM, family().nativeHeightM]).toEqual(trial.nativeDimensions);
    expect(resizeTrialFamilyForAsset({ ...trial, model: { ...trial.model, revision: 'final-seniors-apartments-clay-v004' } })).toBeUndefined();
    expect(resizeTrialFamilyForAsset(placeAsset('autumn_timber'))).toBeUndefined();
    expect(readResizeTrialState(placementProperties(placeAsset('autumn_timber')))).toBeNull();
    expect(readResizeTrialState({ ...placementProperties(trial), pick_place_model_revision: 'another' })).toBeNull();
  });

  it('keeps a freshly placed building undeclared and native until a trial control is applied', () => {
    const zone = placed();
    expect(readResizeTrialState(zone.properties)).toMatchObject({ mode: 'exact_model', widthScale: 1, depthScale: 1, declared: false });
    expect(resizeTrialStretch(zone.properties)).toBeNull();
    const item = deriveItems([zone])[0];
    expect(item.targets.width_m).toBeCloseTo(36.4, 6);
    expect(buildPlanRequestForItem(item)).not.toHaveProperty('footprint_program_id');
    expect(zone.properties).not.toHaveProperty('building_footprint_program_id');
  });

  it('offers the exact model an independent width and depth programme and a resizable plot', () => {
    const resolved = assetForZone(placed())!;
    expect(resolved.reshapeMode).toBe('fixed_native');
    expect(resolved.footprintProgram).toMatchObject({ id: RESIZE_TRIAL_PROGRAM_ID, mode: 'independent_horizontal_scale',
      minScale: 0.7, maxScale: 1.4, defaultScale: 1, nativeWidthM: NATIVE_W, nativeDepthM: NATIVE_D });
    expect(hasFixedBuildingFootprint(resolved)).toBe(false);
    const smallest = resizeTrialPlotFor(family(), 0.7, 0.7);
    expect(smallest.widthM).toBeCloseTo(NATIVE_W * 0.7 + 4.04, 2);
    // The plot minimum is the smallest stretch, rounded up to the inputs' 0.1 m step.
    expect([resolved.minWidth, resolved.minDepth]).toEqual([26.7, 16.7]);
    expect(resolved.minWidth).toBeGreaterThanOrEqual(smallest.widthM);
    expect(fitResizeTrialScalesToPlot(family(), 26.7, 16.7).widthScale).toBeGreaterThanOrEqual(0.7);
    expect(fitResizeTrialScalesToPlot(family(), 26.7, 16.7).depthScale).toBeGreaterThanOrEqual(0.7);
    // Still a native building: its exact model contract is intact.
    expect(nativeBuildingContract(placed())?.heightM).toBeCloseTo(18.99, 2);
  });

  it('fits the building to its plot, keeping the authored margin and never overrunning', () => {
    const margin = resizeTrialPlotMargins(family());
    expect(margin.widthM).toBeCloseTo(2.02, 2);
    expect(margin.depthM).toBeCloseTo(2.01, 2);
    expect(fitResizeTrialScalesToPlot(family(), 36.4, 22)).toEqual({ widthScale: 1, depthScale: 1 });
    // A moved plot drifts by millimetres; it is still exactly 100%.
    expect(fitResizeTrialScalesToPlot(family(), 36.3993, 22.0004)).toEqual({ widthScale: 1, depthScale: 1 });
    for (const [width, depth] of [[45, 18], [30.123, 27.777], [26.7, 16.62], [60, 60]]) {
      const fit = fitResizeTrialScalesToPlot(family(), width, depth);
      const needed = resizeTrialPlotFor(family(), fit.widthScale, fit.depthScale);
      expect(needed.widthM).toBeLessThanOrEqual(width + 1e-6);
      expect(needed.depthM).toBeLessThanOrEqual(depth + 1e-6);
      expect(width - needed.widthM).toBeLessThan(NATIVE_W * 1e-4 + 1e-6);
      expect(depth - needed.depthM).toBeLessThan(NATIVE_D * 1e-4 + 1e-6);
    }
  });

  it('stretches inside the band and hands over to Shape freely outside it', () => {
    expect(decideResizeTrialStretch(family(), NATIVE_W * 0.7, NATIVE_D * 1.4)).toEqual({ kind: 'exact_model', widthScale: 0.7, depthScale: 1.4 });
    expect(decideResizeTrialStretch(family(), NATIVE_W, NATIVE_D)).toEqual({ kind: 'exact_model', widthScale: 1, depthScale: 1 });
    for (const [width, depth] of [[NATIVE_W * 0.69, NATIVE_D], [NATIVE_W, NATIVE_D * 1.41], [60, 12]]) {
      expect(decideResizeTrialStretch(family(), width, depth)).toEqual({ kind: 'shape_freely', widthM: width, depthM: depth, reason: 'stretch_out_of_band' });
    }
  });

  it('saves a stretch as its own fields and never through the uniform house-pilot field', () => {
    const base = placementProperties(asset());
    const saved = exactModelProperties(base, family(), 0.85, 1.2, asset());
    expect(saved).toMatchObject({ building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'exact_model',
      building_footprint_width_scale: 0.85, building_footprint_depth_scale: 1.2, native_plot_axes: true,
      pick_place_asset: ASSET_ID, development_selected_variant_id: base.development_selected_variant_id,
      pick_place_model_revision: base.pick_place_model_revision, floor_count: 5, height_m: base.height_m });
    for (const key of ['building_footprint_scale', 'building_footprint_native_width_m', 'building_footprint_native_depth_m']) {
      expect(saved).not.toHaveProperty(key);
    }
    expect(readResizeTrialState(saved)).toMatchObject({ mode: 'exact_model', widthScale: 0.85, depthScale: 1.2, declared: true });
    expect(resizeTrialStretch(saved)).toMatchObject({ programId: RESIZE_TRIAL_PROGRAM_ID,
      widthM: NATIVE_W * 0.85, depthM: NATIVE_D * 1.2 });
    // A corrupt saved scale reads as 100% in the editor; the server fails it closed.
    expect(readResizeTrialState({ ...saved, building_footprint_width_scale: 9 })).toMatchObject({ widthScale: 1, depthScale: 1.2 });
  });

  it('plans the stretched building, not the plot, and names the programme to the server', () => {
    const properties = exactModelProperties(placementProperties(asset()), family(), 0.8, 1.25, asset());
    const coordinates = rectangleAt(ll(0, 0), 44, 30, 20);
    const item = deriveItems([placed(properties, coordinates)])[0];
    expect(item.targets.width_m).toBeCloseTo(NATIVE_W * 0.8, 9);
    expect(item.targets.depth_m).toBeCloseTo(NATIVE_D * 1.25, 9);
    expect(item.targets.floors).toBe(5);
    expect(item.targets.footprint_profile).toBe('rectangle');
    expect(item.explicitMassing).toBeUndefined();
    const request = buildPlanRequestForItem(item);
    expect(request).toMatchObject({ footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, archetype_id: 'final-seniors-apartments-v1',
      model_revision: 'final-seniors-apartments-clay-v003', target_floors: 5, allow_forced_fit: false });
    // The plot the server checks the stretched envelope against is the real plot.
    const plot = request.footprint_local_m!;
    expect(Math.max(...plot.map(point => Math.abs(point[0])))).toBeCloseTo(22, 3);
    expect(Math.max(...plot.map(point => Math.abs(point[1])))).toBeCloseTo(15, 3);
  });

  it('moves the reviewed entrance with the stretch without compounding edits', () => {
    const base = placementProperties(asset());
    const reviewed = base.pedestrian_building_entrance as BuildingEntrance;
    expect([reviewed.xM, reviewed.yM, reviewed.fixedNative]).toEqual([-4, -7.190000057, true]);
    const once = exactModelProperties(base, family(), 0.8, 1.2, asset());
    const twice = exactModelProperties(once, family(), 1.3, 0.75, asset());
    const direct = exactModelProperties(base, family(), 1.3, 0.75, asset());
    const moved = twice.pedestrian_building_entrance as BuildingEntrance;
    expect(moved.xM).toBeCloseTo(-4 * 1.3, 2);
    expect(moved.yM).toBeCloseTo(-7.190000057 * 0.75, 2);
    expect(moved.xM).toBeCloseTo((direct.pedestrian_building_entrance as BuildingEntrance).xM, 2);
    expect(moved).toMatchObject({ automatic: true, fixedNative: true, scaleWithPlot: false, widthM: reviewed.widthM,
      sourceRevision: reviewed.sourceRevision });
    const smallest = resizeTrialPlotFor(family(), 1.3, 0.75);
    expect([moved.referenceWidthM, moved.referenceDepthM]).toEqual([smallest.widthM, smallest.depthM]);
  });

  it('keeps the stretched entrance on the model and connected to the street it faces', () => {
    const line = [ll(0, -80), ll(0, 80)];
    const road = { ...placed({ road_archetype_id: 'calgary_local', road_selected_variant_id: 'calgary_local_v0', width: 16, plan_centerline: line },
      bufferLineToPolygon(line, 16)), id: 'road', zone_type: 'road' } as SiteZone;
    const site = { ...placed({}, rectangleAt(ll(0, 0), 200, 200)), id: 'site', zone_type: 'site_boundary', is_active_boundary: true } as SiteZone;
    const centre = ll(-36, 0), degrees = streetFacingDegrees(centre, [road]);
    for (const [width, depth] of [[1, 1], [0.8, 1.2], [1.35, 0.75]]) {
      const properties = exactModelProperties(placementProperties(asset()), family(), width, depth, asset());
      const plot = resizeTrialPlotFor(family(), width, depth);
      const house = placed(properties, rectangleAt(centre, plot.widthM, plot.depthM, degrees));
      const zones = [site, road, house];
      const entrance = readBuildingEntrance(house, zones);
      expect(entrance?.streetId).toBe('road');
      // The anchor sits where the stretched model's doorway is, in the plot frame.
      const frame = rectangleDimensions(house.coordinates), yaw = frame.degrees * Math.PI / 180;
      const world = entranceWorldPoint(house, entrance!)!;
      const east = (world[0] - frame.center[0]) * metersPerDegLon(frame.center[1]);
      const north = (world[1] - frame.center[1]) * METERS_PER_DEG_LAT;
      expect(east * Math.cos(yaw) + north * Math.sin(yaw)).toBeCloseTo(-4 * width, 2);
      expect(-east * Math.sin(yaw) + north * Math.cos(yaw)).toBeCloseTo(-7.190000057 * depth, 2);
      expect(resolvePedestrianConnections(zones).find(plan => plan.ownerId === house.id)?.status).toBe('connected');
    }
  });

  it('seats and grounds a stretched model on its own scaled footprint', () => {
    const fit = { assembly_mode: 'fixed_landmark', native_scale_locked: false, delivery_format: 'architectural_clay',
      scale_x: 1.2, scale_y: 0.8, score: 100,
      resize_trial: { program_id: RESIZE_TRIAL_PROGRAM_ID, width_scale: 1.2, depth_scale: 0.8, vertical_scale: 1 } } as LegoAssemblyPlan['fit'];
    expect(isResizeTrialPlan({ fit })).toBe(true);
    expect(isNativeClayPlan({ fit })).toBe(true);
    // Without the server's marker an unlocked plan is not treated as native.
    expect(isNativeClayPlan({ fit: { ...fit, resize_trial: undefined } })).toBe(false);
    expect(isNativeClayPlan({ fit: { ...fit, resize_trial: { ...fit.resize_trial!, vertical_scale: 1.1 } } })).toBe(false);
    const bounds = new THREE.Box3(new THREE.Vector3(-NATIVE_W / 2, 0, -NATIVE_D / 2), new THREE.Vector3(NATIVE_W / 2, 18.99, NATIVE_D / 2));
    const transform = legoInstanceTransform({ position: [0, 0, 0], scale: [1.2, 0.8, 1], rotation_degrees: 0 } as never);
    expect(transform.scale).toEqual([1.2, 1, 0.8]);
    const [footprint] = placedNativeFootprints([{ bounds, transform }], 0, [0, 0]);
    const xs = footprint.map(point => point[0]), ys = footprint.map(point => point[1]);
    expect(Math.max(...xs) - Math.min(...xs)).toBeCloseTo(NATIVE_W * 1.2, 6);
    expect(Math.max(...ys) - Math.min(...ys)).toBeCloseTo(NATIVE_D * 0.8, 6);
    // Ground contact is taken at the unscaled base: height is never stretched.
    expect(bounds.min.y * transform.scale[1]).toBe(0);
  });

  it('keeps the whole plot as the neighbour envelope once a building is reshaped', () => {
    const row = edges.buildings.find(entry => (entry.left === 'abut' || entry.right === 'abut') && !entry.plotFit)!;
    const reviewed = placeAsset(row.assetId);
    const coordinates = rectangleAt(ll(0, 0), row.nativeWidthM + 6, row.nativeDepthM + 6, 0);
    const base = placementProperties(reviewed);
    expect(buildingEdgeContract({ coordinates, properties: base })).not.toBeNull();
    const trial = { building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'exact_model' };
    expect(buildingEdgeContract({ coordinates, properties: { ...base, ...trial,
      building_footprint_width_scale: 1, building_footprint_depth_scale: 1 } })).not.toBeNull();
    for (const state of [
      { ...trial, building_footprint_width_scale: 1.2, building_footprint_depth_scale: 1 },
      { ...trial, building_footprint_width_scale: 1, building_footprint_depth_scale: 0.8 },
      { building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'shape_freely' },
    ]) {
      const properties = { ...base, ...state };
      expect(resizeTrialChangesEnvelope(properties)).toBe(true);
      expect(buildingEdgeContract({ coordinates, properties })).toBeNull();
      expect(buildingPlacementEnvelope({ coordinates, properties })).toBe(coordinates);
    }
    // The pilot building has no reviewed side clearance: its plot is its envelope at any stretch.
    const stretched = placed(exactModelProperties(placementProperties(asset()), family(), 1.3, 0.8, asset()));
    expect(buildingEdgeContract(stretched)).toBeNull();
    expect(buildingPlacementEnvelope(stretched)).toBe(stretched.coordinates);
  });

  it('squeezes the building when its plot shrinks and leaves it alone when the plot moves or grows', () => {
    const zone = placed();
    const at = (width: number, depth: number, x = 0, degrees = 0) => rectangleAt(ll(x, 0), width, depth, degrees);
    expect(resizeTrialPlotReshape(zone, at(36.4, 22, 250, 73), asset())).toBeNull();
    expect(resizeTrialPlotReshape(zone, at(36.37, 21.97), asset())).toBeNull();
    expect(resizeTrialPlotReshape(zone, at(50, 30), asset())).toBeNull();
    const squeezed = resizeTrialPlotReshape(zone, at(30, 22), asset())!;
    expect(squeezed).toMatchObject({ building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'exact_model',
      building_footprint_depth_scale: 1 });
    const width = squeezed.building_footprint_width_scale as number;
    expect(width).toBeCloseTo((30 - 4.04) / NATIVE_W, 3);
    expect(NATIVE_W * width + 4.04).toBeLessThanOrEqual(30 + 1e-6);
    expect((squeezed.pedestrian_building_entrance as BuildingEntrance).xM).toBeCloseTo(-4 * width, 2);
    // Never below the band: the plot minimum already stops there.
    expect(resizeTrialPlotReshape(zone, at(10, 5), asset())).toMatchObject({ building_footprint_width_scale: 0.7, building_footprint_depth_scale: 0.7 });
    // An already stretched building keeps its stretch when only the other axis is squeezed.
    const wide = placed(exactModelProperties(placementProperties(asset()), family(), 1.3, 1, asset()), at(48, 22));
    expect(resizeTrialPlotReshape(wide, at(48, 18), asset())).toMatchObject({ building_footprint_width_scale: 1.3 });
    expect(resizeTrialPlotReshape(wide, at(48.2, 22.3), asset())).toBeNull();
  });

  it('turns Shape freely into an editable outline that keeps the building identity', () => {
    const base = placementProperties(asset());
    const freely = shapeFreelyProperties(exactModelProperties(base, family(), 1.2, 0.9, asset()), 'stretch_out_of_band');
    expect(freely).toMatchObject({ building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'shape_freely',
      building_footprint_mode_reason: 'stretch_out_of_band', building_geometry_basis: 'drawn_footprint',
      pick_place_asset: ASSET_ID, development_archetype_id: 'final-seniors-apartments',
      development_selected_variant_id: 'final-seniors-apartments-v1', pick_place_model_revision: 'final-seniors-apartments-clay-v003',
      floors: 5, floor_count: 5, height: base.height, height_m: base.height_m });
    expect(freely.building_footprint_width_scale).toBeUndefined();
    expect(freely.pedestrian_building_entrance).toBeUndefined();
    expect(readResizeTrialState(freely)).toMatchObject({ mode: 'shape_freely', reason: 'stretch_out_of_band', declared: true });
    expect(readResizeTrialState(shapeFreelyProperties(base))?.reason).toBeUndefined();
    const outline = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    const zone = placed(freely, outline);
    const resolved = assetForZone(zone)!;
    expect(resolved.id).toBe(ASSET_ID);
    expect(resolved.reshapeMode).toBe('authored_footprint');
    expect(resolved.footprintProgram).toBeUndefined();
    expect([resolved.minWidth, resolved.minDepth]).toEqual([9, 9]);
    expect(hasFixedBuildingFootprint(resolved)).toBe(false);
    expect(nativeBuildingContract(zone)).toBeUndefined();
    const item = deriveItems([zone])[0];
    expect(item.explicitMassing).toBe(true);
    expect(item.archetypeId).toBe('final-seniors-apartments-v1');
    expect(item.targets.floors).toBe(5);
    // Returning to the exact model restores the reviewed entrance at the new stretch.
    const back = exactModelProperties(freely, family(), 1.1, 1, asset());
    expect(back.building_footprint_mode_reason).toBeUndefined();
    expect(back.building_geometry_basis).toBe('placement_plot');
    expect((back.pedestrian_building_entrance as BuildingEntrance).xM).toBeCloseTo(-4.4, 3);
    expect(withResizeTrial(asset(), back).reshapeMode).toBe('fixed_native');
  });

  it('enforces a sensible minimum outline', () => {
    const rectangle = (width: number, depth: number, degrees = 0) => resizeTrialRectangle(ll(0, 0), width, depth, degrees);
    expect(resizeTrialOutlineProblem(rectangle(9, 12))).toBeNull();
    expect(resizeTrialOutlineProblem(rectangle(9, 12, 37))).toBeNull();
    expect(resizeTrialOutlineProblem(rectangle(8.9, 30))).toMatch(/at least 9 m wide and 9 m deep/);
    expect(resizeTrialOutlineProblem(rectangle(30, 8.9, 61))).toMatch(/at least 9 m wide and 9 m deep/);
    expect(resizeTrialOutlineProblem([ll(0, 0), ll(20, 0), ll(0.5, 9.5)])).toMatch(/at least 100 m²/);
    expect(resizeTrialOutlineProblem(rectangle(121, 30))).toMatch(/at most 120 m/);
    expect(resizeTrialOutlineProblem([ll(0, 0), ll(20, 0)])).toMatch(/three corners/);
    const many = Array.from({ length: 25 }, (_, index) => ll(Math.cos(index / 25 * Math.PI * 2) * 30, Math.sin(index / 25 * Math.PI * 2) * 30));
    expect(resizeTrialOutlineProblem(many)).toMatch(/at most 24 corners/);
  });

  it('reports footprint area, storeys, floor area and FAR for the drawn outline', () => {
    const outline = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    const figures = resizeTrialFigures(outline, 5, 10000);
    expect(figures.footprintAreaM2).toBeCloseTo(1125, 0);
    expect(figures.storeys).toBe(5);
    expect(figures.floorAreaM2).toBeCloseTo(5625, 0);
    expect(figures.far).toBeCloseTo(0.5625, 3);
    expect(resizeTrialFigures(outline, 5).far).toBeNull();
    expect(resizeTrialFigures(outline, 5, 0).far).toBeNull();
    expect(resizeTrialFigures(outline, 'many', 10000)).toMatchObject({ storeys: 0, floorAreaM2: 0 });
  });

  it('dresses only freely shaped massing, at the building’s own storey count', () => {
    const base = placementProperties(asset());
    expect(resizeTrialMassingDressing(base)).toBeNull();
    expect(resizeTrialMassingDressing(exactModelProperties(base, family(), 1.2, 1, asset()))).toBeNull();
    expect(resizeTrialMassingDressing(shapeFreelyProperties(base))).toMatchObject({ storeys: 5, floorLineSpacingM: null,
      bayModuleM: RESIZE_TRIAL_SETTINGS.bayModuleM, windowWidthM: RESIZE_TRIAL_SETTINGS.windowWidthM });
  });

  it('describes Shape freely as a choice, not a missing model', () => {
    const compiled = (properties: SiteZoneProperties) => placed({ ...properties,
      community_3d: { schema_version: 1, state: 'compiled', kind: 'building', generator: 'planned_massing', compiled_at: '2026-11-12' } });
    const freely = compiled(shapeFreelyProperties(placementProperties(asset())));
    expect(representationNotice([freely])).toBe('1 building is set to Shape freely and shown as shaped massing.');
    const fallback = compiled({ development_archetype_id: 'unknown' });
    expect(representationNotice([freely, fallback])).toMatch(/1 building is set to Shape freely.*1 building is shown as design massing/);
  });
});
