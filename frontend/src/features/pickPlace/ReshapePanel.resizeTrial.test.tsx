import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { ReshapePanel } from './ReshapePanel';
import { placeAsset, placementProperties } from './catalogue';
import { rectangleAt, rectangleDimensions } from './geometry';
import { parkOutlineDimensions } from './parkOutline';
import { exactModelProperties, resizeTrialFamilyForAsset, shapeFreelyProperties } from './buildingResizeTrial';

vi.mock('@/features/legoAssembly/legoAssemblyApi', async importOriginal => ({
  ...await importOriginal<typeof import('@/features/legoAssembly/legoAssemblyApi')>(),
  legoAssemblyApi: { plan: vi.fn() },
}));

const ll = (x: number, y: number) => [-114 + x / metersPerDegLon(51), 51 + y / METERS_PER_DEG_LAT];
const asset = () => placeAsset('final_seniors_apartments');
const building = (properties: SiteZoneProperties, coordinates: number[][]) => ({
  id: 'midrise', project_id: 'project', zone_type: 'building', updated_at: 'now', coordinates, properties,
} as SiteZone);
const site = { id: 'site', project_id: 'project', zone_type: 'site_boundary', is_active_boundary: true, updated_at: 'now',
  coordinates: rectangleAt(ll(0, 0), 100, 100), properties: {} } as SiteZone;
const show = (zone: SiteZone, zones: SiteZone[] = [site, zone]) => {
  const onReshape = vi.fn(), onUpdateDesign = vi.fn();
  render(<ReshapePanel zone={zone} zones={zones} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={onUpdateDesign} />);
  return { onReshape, onUpdateDesign };
};
afterEach(() => { cleanup(); vi.unstubAllEnvs(); });

it('keeps the mid-rise a fixed native footprint while the flag is off', () => {
  show(building(placementProperties(asset()), rectangleAt(ll(0, 0), 36.4, 22)));
  expect(screen.getByText('Fixed native footprint: move and rotate only.')).toBeInTheDocument();
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByRole('radiogroup', { name: 'Building shape' })).not.toBeInTheDocument();
  expect(screen.queryByRole('status', { name: 'Building figures' })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Add outline point' })).not.toBeInTheDocument();
});

describe('flag on', () => {
  beforeEach(() => vi.stubEnv('VITE_ENABLE_BUILDING_RESIZE_TRIAL', 'true'));

  it('lets the exact model’s plot be resized down to its smallest stretch', () => {
    const { onReshape } = show(building(placementProperties(asset()), rectangleAt(ll(0, 0), 36.4, 22, 20)));
    expect(screen.getByText(/a smaller plot squeezes the exact model to fit/)).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Exact model' })).toBeChecked();
    const width = screen.getByLabelText('Plot width (m)') as HTMLInputElement;
    expect(width).toBeEnabled();
    // Rounded up to the 0.1 m the plot inputs step in.
    expect(width.min).toBe('26.7');
    expect((screen.getByLabelText('Plot depth (m)') as HTMLInputElement).min).toBe('16.7');
    fireEvent.change(width, { target: { value: '30' } });
    fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
    const plot = rectangleDimensions(onReshape.mock.calls[0][0]);
    expect(plot.width).toBeCloseTo(30, 5);
    expect(plot.depth).toBeCloseTo(22, 5);
    expect(plot.degrees).toBeCloseTo(20, 5);
    // Below the smallest stretch the plot is refused, not the building crushed.
    fireEvent.change(width, { target: { value: '20' } });
    expect(screen.getByRole('button', { name: 'Apply shape' })).toBeDisabled();
  });

  it('shows live footprint area, storeys, floor area and FAR for a freely shaped building', () => {
    const outline = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    show(building(shapeFreelyProperties(placementProperties(asset())), outline));
    const figures = within(screen.getByRole('status', { name: 'Building figures' }));
    expect(figures.getByText('Footprint area').nextSibling).toHaveTextContent('1,125 m²');
    expect(figures.getByText('Storeys').nextSibling).toHaveTextContent('5');
    expect(figures.getByText('Floor area').nextSibling).toHaveTextContent('5,625 m²');
    // 5,625 m² of floor on a 10,000 m² site.
    expect(figures.getByText('FAR').nextSibling).toHaveTextContent('0.56');
    expect(screen.getByText(/drag the white corners to fit any space/)).toBeInTheDocument();
    // The figures follow the size being typed, before it is applied.
    fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '80' } });
    expect(figures.getByText('Footprint area').nextSibling).toHaveTextContent('1,800 m²');
    expect(figures.getByText('Floor area').nextSibling).toHaveTextContent('9,000 m²');
    expect(figures.getByText('FAR').nextSibling).toHaveTextContent('0.90');
    // An apartment block has no courtyard to report.
    expect(figures.queryByText('Courtyard')).not.toBeInTheDocument();
    expect(screen.getByText(/Floor area is the outline × storeys/)).toBeInTheDocument();
    expect(screen.queryByText(/too small for a courtyard/)).not.toBeInTheDocument();
  });

  it('reports a courtyard block’s open courtyard and leaves it out of the floor area', () => {
    const block = placeAsset('final_courtyard_block');
    show(building(shapeFreelyProperties(placementProperties(block)), rectangleAt(ll(0, 0), 30, 24.4)));
    const figures = within(screen.getByRole('status', { name: 'Building figures' }));
    // 732 m² outline less a 19.2 × 13.6 m courtyard.
    expect(figures.getByText('Footprint area').nextSibling).toHaveTextContent('471 m²');
    expect(figures.getByText('Courtyard').nextSibling).toHaveTextContent('261 m²');
    expect(figures.getByText('Storeys').nextSibling).toHaveTextContent('4');
    expect(figures.getByText('Floor area').nextSibling).toHaveTextContent('1,884 m²');
    expect(figures.getByText('FAR').nextSibling).toHaveTextContent('0.19');
    expect(screen.getByText(/The open courtyard is not counted/)).toBeInTheDocument();
    expect(screen.queryByText(/too small for a courtyard/)).not.toBeInTheDocument();
    // Typed too narrow for a courtyard, the block becomes solid and says so by dropping the row.
    fireEvent.change(screen.getByLabelText('Plot depth (m)'), { target: { value: '14' } });
    expect(figures.queryByText('Courtyard')).not.toBeInTheDocument();
    expect(figures.getByText('Footprint area').nextSibling).toHaveTextContent('420 m²');
    expect(screen.getByText(/Floor area is the outline × storeys/)).toBeInTheDocument();
    expect(screen.getByText(/too small for a courtyard, so the block is built solid.*at least 18\.8 m across/)).toBeInTheDocument();
  });

  it('offers the courtyard block the same stretch controls on its own dimensions', () => {
    const block = placeAsset('final_courtyard_block');
    show(building(placementProperties(block), rectangleAt(ll(0, 0), 34.4, 30.3)));
    expect(screen.getByRole('radio', { name: 'Exact model' })).toBeChecked();
    expect(screen.getByLabelText('Building width (m)')).toHaveValue(30.38);
    expect(screen.getByLabelText('Building depth (m)')).toHaveValue(26.3);
    expect(screen.getByText(/stretches 21\.27–42\.53 m wide and 18\.41–36\.82 m deep/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Building width (m)'), { target: { value: '48' } });
    expect(screen.getByText('This size is outside the exact model’s range. Applying switches this building to Shape freely.')).toBeInTheDocument();
  });

  it('asks for a site boundary instead of inventing a FAR', () => {
    const zone = building(shapeFreelyProperties(placementProperties(asset())), rectangleAt(ll(0, 0), 30, 18));
    show(zone, [zone]);
    expect(within(screen.getByRole('status', { name: 'Building figures' })).getByText('FAR').nextSibling)
      .toHaveTextContent('Draw a site boundary');
  });

  it('reuses the outline editor: add a point, resize the outline, keep its shape', () => {
    const outline = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    const { onReshape } = show(building(shapeFreelyProperties(placementProperties(asset())), outline));
    expect(screen.getByText('Building width (m)')).toBeInTheDocument();
    expect(screen.getByText('Building depth (m)')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Add outline point' }));
    expect(onReshape.mock.calls[0][0]).toHaveLength(7);
    fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '60' } });
    fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
    const reshaped = onReshape.mock.calls[1][0] as number[][];
    expect(reshaped).toHaveLength(6);
    const frame = parkOutlineDimensions(reshaped);
    expect(frame.width).toBeCloseTo(60, 4);
    expect(frame.depth).toBeCloseTo(30, 4);
  });

  it('enforces the minimum width and depth before a freely shaped outline is applied', () => {
    const { onReshape } = show(building(shapeFreelyProperties(placementProperties(asset())), rectangleAt(ll(0, 0), 30, 18)));
    fireEvent.change(screen.getByLabelText('Plot depth (m)'), { target: { value: '6' } });
    expect(screen.getByRole('button', { name: 'Apply shape' })).toBeDisabled();
    // Wide and deep enough on each axis, yet too small a floor plate overall.
    fireEvent.change(screen.getByLabelText('Plot depth (m)'), { target: { value: '9.5' } });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '10' } });
    expect(screen.getByRole('alert')).toHaveTextContent(/footprint of at least 100 m²/);
    expect(screen.getByRole('button', { name: 'Apply shape' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '12' } });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
    expect(onReshape).toHaveBeenCalledTimes(1);
  });

  it('stops offering new outline points at the corner limit', () => {
    const ring = Array.from({ length: 24 }, (_, index) => ll(Math.cos(index / 24 * Math.PI * 2) * 30, Math.sin(index / 24 * Math.PI * 2) * 30));
    show(building(shapeFreelyProperties(placementProperties(asset())), ring));
    expect(screen.getByRole('button', { name: 'Add outline point' })).toBeDisabled();
  });

  it('places another as a fresh exact model on its catalogue plot, never on a squeezed one', () => {
    const squeezed = exactModelProperties(placementProperties(asset()), resizeTrialFamilyForAsset(asset())!, 0.8, 0.8, asset());
    for (const zone of [building(squeezed, rectangleAt(ll(0, 0), 30, 18.4, 20)),
      building(shapeFreelyProperties(placementProperties(asset())), rectangleAt(ll(0, 0), 12, 10, 20))]) {
      const onDuplicate = vi.fn();
      render(<ReshapePanel zone={zone} zones={[site, zone]} disabled={false} onDuplicate={onDuplicate} onReshape={vi.fn()}
        onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={vi.fn()} />);
      fireEvent.click(screen.getByRole('button', { name: 'Place another' }));
      expect(onDuplicate.mock.calls[0].slice(0, 3)).toEqual(['final_seniors_apartments', 36.4, 22]);
      expect(onDuplicate.mock.calls[0][3]).toBeCloseTo(20, 2);
      cleanup();
    }
  });

  it('passes a pilot save through with its outline', () => {
    const saved = exactModelProperties(placementProperties(asset()), resizeTrialFamilyForAsset(asset())!, 1.2, 0.9, asset());
    const { onUpdateDesign } = show(building(saved, rectangleAt(ll(0, 0), 44, 22, 20)));
    fireEvent.click(screen.getByRole('radio', { name: 'Shape freely' }));
    fireEvent.click(screen.getByRole('button', { name: 'Apply building' }));
    expect(onUpdateDesign).toHaveBeenCalledTimes(1);
    const [properties, coordinates] = onUpdateDesign.mock.calls[0];
    expect(properties.building_footprint_mode).toBe('shape_freely');
    expect(rectangleDimensions(coordinates).width).toBeCloseTo(32.36000061035156 * 1.2, 5);
  });
});
