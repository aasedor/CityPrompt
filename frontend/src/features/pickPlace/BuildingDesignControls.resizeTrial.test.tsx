import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { legoAssemblyApi } from '@/features/legoAssembly/legoAssemblyApi';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { BuildingDesignControls } from './BuildingDesignControls';
import { placeAsset, placementProperties } from './catalogue';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { rectangleAt, rectangleDimensions } from './geometry';
import {
  RESIZE_TRIAL_PROGRAM_ID, exactModelProperties, resizeTrialFamilyForAsset, shapeFreelyProperties,
} from './buildingResizeTrial';

vi.mock('@/features/legoAssembly/legoAssemblyApi', async importOriginal => ({
  ...await importOriginal<typeof import('@/features/legoAssembly/legoAssemblyApi')>(),
  legoAssemblyApi: { plan: vi.fn() },
}));

const NATIVE_W = 32.36000061035156, NATIVE_D = 17.980000495910645;
const asset = () => placeAsset('final_seniors_apartments');
const centre = [-114, 51];
const building = (properties: SiteZoneProperties = placementProperties(asset()),
  coordinates = rectangleAt(centre, 36.4, 22, 15)) => ({
  id: 'midrise', project_id: 'project', zone_type: 'building', updated_at: 'now', coordinates, properties,
} as SiteZone);
/** What the server returns for an accepted stretch. */
const stretched = (width: number, depth: number) => ({ fit: { resize_trial: {
  program_id: RESIZE_TRIAL_PROGRAM_ID, width_scale: width, depth_scale: depth, vertical_scale: 1 } } }) as never;
const show = (zone = building()) => {
  const onSave = vi.fn();
  render(<BuildingDesignControls zone={zone} disabled={false} onSave={onSave} />);
  return onSave;
};
const type = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });
const apply = () => fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));

beforeEach(() => { vi.mocked(legoAssemblyApi.plan).mockReset().mockResolvedValue({} as never); });
afterEach(() => { cleanup(); vi.unstubAllEnvs(); });

describe('flag off (the default)', () => {
  it('shows no pilot control and saves the building exactly as before', () => {
    const onSave = show();
    expect(screen.queryByRole('radiogroup', { name: 'Building shape' })).toBeNull();
    expect(screen.queryByLabelText('Building width (m)')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Fit building to plot' })).toBeNull();
    apply();
    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onSave.mock.calls[0]).toHaveLength(1);
    for (const key of ['building_footprint_program_id', 'building_footprint_mode', 'building_footprint_width_scale']) {
      expect(onSave.mock.calls[0][0]).not.toHaveProperty(key);
    }
    expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  });

  it('does not act on trial state saved while the flag was on', () => {
    vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL', 'true');
    const saved = exactModelProperties(placementProperties(asset()), resizeTrialFamilyForAsset(asset())!, 1.2, 0.9, asset());
    vi.unstubAllEnvs();
    show(building(saved));
    expect(screen.queryByLabelText('Building width (m)')).toBeNull();
    expect(screen.queryByText(/Shape freely/)).toBeNull();
  });
});

describe('flag on', () => {
  beforeEach(() => vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL', 'true'));
  const family = () => resizeTrialFamilyForAsset(asset())!;

  it('offers width, depth, Fit building to plot and the two shapes for the pilot building only', () => {
    show();
    expect(screen.getByRole('radio', { name: 'Exact model' })).toBeChecked();
    expect(screen.getByRole('radio', { name: 'Shape freely' })).not.toBeChecked();
    expect(screen.getByLabelText('Building width (m)')).toHaveValue(32.36);
    expect(screen.getByLabelText('Building depth (m)')).toHaveValue(17.98);
    expect(screen.getAllByText('100% of the model')).toHaveLength(2);
    expect(screen.getByRole('button', { name: 'Fit building to plot' })).toBeEnabled();
    expect(screen.getByText(/stretches 22.65–45.3 m wide and 12.59–25.17 m deep \(70%–140%\)/)).toBeInTheDocument();
    // The uniform house-pilot slider is a different programme and stays away.
    expect(screen.queryByLabelText('Building footprint (%)')).toBeNull();
    cleanup();
    show(building(placementProperties(placeAsset('autumn_timber')), rectangleAt(centre, 24, 23)));
    expect(screen.queryByRole('radiogroup', { name: 'Building shape' })).toBeNull();
  });

  it('leaves an untouched building undeclared', () => {
    const onSave = show();
    apply();
    expect(onSave.mock.calls[0]).toHaveLength(1);
    expect(onSave.mock.calls[0][0]).not.toHaveProperty('building_footprint_program_id');
    expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  });

  it('does not round a saved stretch to the centimetres on display when nothing was typed', () => {
    // 0.9258 x 32.36 m shows as 29.96 m, which alone would read back as a different stretch.
    const saved = exactModelProperties(placementProperties(asset()), family(), 0.9258, 1.3337, asset());
    const onSave = show(building(saved, rectangleAt(centre, 36.4, 30, 15)));
    expect(screen.getByLabelText('Building width (m)')).toHaveValue(29.96);
    apply();
    expect(onSave.mock.calls[0]).toHaveLength(1);
    expect(onSave.mock.calls[0][0]).toMatchObject({ building_footprint_width_scale: 0.9258, building_footprint_depth_scale: 1.3337 });
    expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  });

  it('checks a stretch with the server, then saves it and grows the plot it needs', async () => {
    vi.mocked(legoAssemblyApi.plan).mockResolvedValue(stretched(1.1743, 0.8343));
    const zone = building(), onSave = show(zone);
    type('Building width (m)', '38');
    type('Building depth (m)', '15');
    expect(screen.getByText('117% of the model')).toBeInTheDocument();
    expect(screen.getByText('83% of the model')).toBeInTheDocument();
    apply();
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    const [properties, coordinates] = onSave.mock.calls[0];
    expect(properties).toMatchObject({ building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'exact_model',
      building_footprint_width_scale: 1.1743, building_footprint_depth_scale: 0.8343, floor_count: 5,
      pick_place_asset: 'final_seniors_apartments', pick_place_model_revision: 'final-seniors-apartments-clay-v003' });
    expect(properties.height_m).toBeCloseTo(18.99, 2);
    expect(properties).not.toHaveProperty('building_footprint_scale');
    // The wider building takes the room it needs; the deeper plot is not shrunk.
    const plot = rectangleDimensions(coordinates);
    expect(plot.width).toBeCloseTo(NATIVE_W * 1.1743 + 4.04, 2);
    expect(plot.depth).toBeCloseTo(22, 3);
    expect(plot.degrees).toBeCloseTo(15, 6);
    expect(plot.center[0]).toBeCloseTo(centre[0], 9);
    expect(legoAssemblyApi.plan).toHaveBeenCalledWith(expect.objectContaining({ footprint_program_id: RESIZE_TRIAL_PROGRAM_ID,
      target_floors: 5, archetype_id: 'final-seniors-apartments-v1', model_revision: 'final-seniors-apartments-clay-v003' }));
    const request = vi.mocked(legoAssemblyApi.plan).mock.calls[0][0];
    expect(request.target_width_m).toBeCloseTo(NATIVE_W * 1.1743, 6);
    expect(request.target_depth_m).toBeCloseTo(NATIVE_D * 0.8343, 6);
    // The server is asked about the plot that will actually be saved.
    expect(Math.max(...request.footprint_local_m!.map(point => Math.abs(point[0]))) * 2).toBeCloseTo(plot.width, 3);
  });

  it('keeps the plot when a smaller building still fits it', async () => {
    vi.mocked(legoAssemblyApi.plan).mockResolvedValue(stretched(0.8, 0.9));
    const onSave = show();
    type('Building width (m)', String(NATIVE_W * 0.8));
    type('Building depth (m)', String(NATIVE_D * 0.9));
    apply();
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    expect(onSave.mock.calls[0]).toHaveLength(1);
    expect(onSave.mock.calls[0][0]).toMatchObject({ building_footprint_width_scale: 0.8, building_footprint_depth_scale: 0.9 });
  });

  it('does not save when the server refuses or does not stretch the model', async () => {
    const onSave = show();
    type('Building width (m)', '38');
    apply();
    expect(await screen.findByRole('alert')).toHaveTextContent(/The building was not changed.*resize pilot is switched on for the server/);
    expect(onSave).not.toHaveBeenCalled();
    vi.mocked(legoAssemblyApi.plan).mockRejectedValue(new Error('The stretched building does not fit inside its plot.'));
    apply();
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('does not fit inside its plot'));
    expect(onSave).not.toHaveBeenCalled();
  });

  it('hands over to Shape freely when a typed size leaves the band, and says so first', () => {
    const onSave = show();
    type('Building width (m)', '50');
    expect(screen.getByRole('status')).toHaveTextContent('outside the exact model’s range. Applying switches this building to Shape freely.');
    apply();
    expect(onSave).toHaveBeenCalledTimes(1);
    const [properties, coordinates] = onSave.mock.calls[0];
    expect(properties).toMatchObject({ building_footprint_program_id: RESIZE_TRIAL_PROGRAM_ID, building_footprint_mode: 'shape_freely',
      building_footprint_mode_reason: 'stretch_out_of_band', building_geometry_basis: 'drawn_footprint',
      development_archetype_id: 'final-seniors-apartments', development_selected_variant_id: 'final-seniors-apartments-v1',
      floors: 5, floor_count: 5 });
    expect(properties.height_m).toBeCloseTo(18.99, 2);
    expect(properties.building_footprint_width_scale).toBeUndefined();
    const outline = rectangleDimensions(coordinates);
    expect([outline.width, outline.depth].map(value => Math.round(value * 100) / 100)).toEqual([50, 17.98]);
    expect(outline.degrees).toBeCloseTo(15, 6);
    // Massing needs no detailed model check.
    expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  });

  it('refuses a size too small for any building instead of handing it over', () => {
    const onSave = show();
    type('Building depth (m)', '5');
    expect(screen.getByRole('alert')).toHaveTextContent('at least 9 m wide and 9 m deep');
    expect(screen.getByRole('button', { name: 'Apply building' })).toBeDisabled();
    apply();
    expect(onSave).not.toHaveBeenCalled();
  });

  it('fits the building to a larger plot in one click', async () => {
    vi.mocked(legoAssemblyApi.plan).mockResolvedValue(stretched(1.2657, 1));
    const onSave = show(building(undefined, rectangleAt(centre, 45, 22, 15)));
    fireEvent.click(screen.getByRole('button', { name: 'Fit building to plot' }));
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    expect(onSave.mock.calls[0]).toHaveLength(1);
    expect(onSave.mock.calls[0][0]).toMatchObject({ building_footprint_mode: 'exact_model',
      building_footprint_width_scale: 1.2657, building_footprint_depth_scale: 1 });
    expect(vi.mocked(legoAssemblyApi.plan).mock.calls[0][0].target_width_m).toBeCloseTo(NATIVE_W * 1.2657, 6);
  });

  it('fits past the band by switching to Shape freely automatically', () => {
    const onSave = show(building(undefined, rectangleAt(centre, 65, 22, 15)));
    fireEvent.click(screen.getByRole('button', { name: 'Fit building to plot' }));
    expect(onSave).toHaveBeenCalledTimes(1);
    const [properties, coordinates] = onSave.mock.calls[0];
    expect(properties).toMatchObject({ building_footprint_mode: 'shape_freely', building_footprint_mode_reason: 'stretch_out_of_band' });
    const outline = rectangleDimensions(coordinates);
    expect(outline.width).toBeCloseTo(65 - 4.04, 1);
    expect(outline.depth).toBeCloseTo(NATIVE_D, 2);
    expect(legoAssemblyApi.plan).not.toHaveBeenCalled();
  });

  it('switches to Shape freely by choice, starting from the building on screen', () => {
    const saved = exactModelProperties(placementProperties(asset()), family(), 1.2, 0.9, asset());
    const onSave = show(building(saved, rectangleAt(centre, 44, 22, 15)));
    expect(screen.getByLabelText('Building width (m)')).toHaveValue(38.83);
    fireEvent.click(screen.getByRole('radio', { name: 'Shape freely' }));
    expect(screen.queryByLabelText('Building width (m)')).toBeNull();
    expect(screen.getByText(/replaces the detailed model with an outline you can reshape/)).toBeInTheDocument();
    apply();
    const [properties, coordinates] = onSave.mock.calls[0];
    expect(properties).toMatchObject({ building_footprint_mode: 'shape_freely' });
    expect(properties.building_footprint_mode_reason).toBeUndefined();
    const outline = rectangleDimensions(coordinates);
    expect(outline.width).toBeCloseTo(NATIVE_W * 1.2, 6);
    expect(outline.depth).toBeCloseTo(NATIVE_D * 0.9, 6);
  });

  it('labels an automatic switch after reload and returns to the exact model on request', async () => {
    vi.mocked(legoAssemblyApi.plan).mockResolvedValue(stretched(1.4, 1));
    const saved = shapeFreelyProperties(placementProperties(asset()), 'stretch_out_of_band');
    const onSave = show(building(saved, rectangleAt(centre, 50, 17.98, 15)));
    expect(screen.getByRole('radio', { name: 'Shape freely' })).toBeChecked();
    expect(screen.getByRole('status')).toHaveTextContent(
      'Switched to Shape freely automatically. The size you asked for is outside the exact model’s 70%–140% range.');
    expect(screen.queryByRole('button', { name: 'Fit building to plot' })).toBeNull();
    fireEvent.click(screen.getByRole('radio', { name: 'Exact model' }));
    // The nearest size the exact model can take.
    expect(screen.getByLabelText('Building width (m)')).toHaveValue(45.3);
    expect(screen.getByLabelText('Building depth (m)')).toHaveValue(17.98);
    apply();
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    const [properties, coordinates] = onSave.mock.calls[0];
    expect(properties).toMatchObject({ building_footprint_mode: 'exact_model', building_footprint_width_scale: 1.3999,
      building_footprint_depth_scale: 1, building_geometry_basis: 'placement_plot' });
    expect(properties.building_footprint_mode_reason).toBeUndefined();
    expect(properties.pedestrian_building_entrance).toMatchObject({ automatic: true, fixedNative: true });
    const plot = rectangleDimensions(coordinates);
    expect(plot.width).toBeCloseTo(NATIVE_W * 1.3999 + 4.04, 2);
    expect(plot.depth).toBeCloseTo(22, 2);
  });

  it('a manual Shape freely building says so without claiming an automatic switch', () => {
    show(building(shapeFreelyProperties(placementProperties(asset())), rectangleAt(centre, 30, 17.98, 15)));
    expect(screen.getByRole('status')).toHaveTextContent('This building is shaped freely.');
    expect(screen.getByRole('status')).not.toHaveTextContent('automatically');
  });

  it('leaves the pilot state behind when the student picks a different building', () => {
    const saved = exactModelProperties(placementProperties(asset()), family(), 1.2, 0.9, asset());
    const onSave = show(building(saved, rectangleAt(centre, 44, 22, 15)));
    const other = CANONICAL_CHOICES.find(choice => choice.domain === 'building'
      && choice.placements.some(placement => placement.id === 'autumn_timber'))!;
    fireEvent.change(screen.getByLabelText('Building type'), { target: { value: other.id } });
    expect(screen.queryByRole('radiogroup', { name: 'Building shape' })).toBeNull();
    apply();
    const properties = onSave.mock.calls[0][0];
    for (const key of ['building_footprint_program_id', 'building_footprint_mode', 'building_footprint_width_scale',
      'building_footprint_depth_scale', 'building_footprint_mode_reason']) {
      expect(properties[key]).toBeUndefined();
    }
  });
});
