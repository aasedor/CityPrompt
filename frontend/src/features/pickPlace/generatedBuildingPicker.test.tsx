import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';

vi.mock('./publishedBuildingAssets', () => {
  const assets = [
    { id: 'generated_ui_ready', readiness: 'ready', label: 'Published UI fixture hall' },
    { id: 'generated_ui_pilot', readiness: 'pilot', label: 'Local UI fixture hall' },
  ].map(({ id, readiness, label }) => ({
    id, readiness, label, kind: 'object', definitionVersion: 1,
    description: 'An authored generated hall.', thumbnail: `/fixtures/${id}.png`,
    zoneType: 'building', reshapeMode: 'fixed_native',
    width: 20, depth: 24, minWidth: 20, minDepth: 24, maxSize: 100,
    nativeDimensions: [16, 20, 9],
    calgaryGuide: { groupId: 'civic', basis: 'form_reference' },
    model: { variantId: `${id}_variant`, revision: `${id}-v003`, method: 'RLASM 6.1' },
    reshapeDescription: 'The authored building keeps its proportions.',
    properties: {
      building_archetype_id: 'generated_ui_fixture_hall',
      development_archetype_id: 'generated_ui_fixture_hall',
      development_selected_variant_id: `${id}_variant`,
      floors: 3, floor_count: 3, native_home_plot: false, native_plot_axes: true,
    },
  }));
  return { CATALOGUE_BUILDING_ASSETS: assets, PUBLISHED_BUILDING_ASSETS: assets.filter(asset => asset.readiness === 'ready') };
});

it.each([
  ['generated_ui_ready', 'Published UI fixture hall'],
  ['generated_ui_pilot', 'Local UI fixture hall'],
])('selects generated exact model %s from the ordinary development picker', (id, label) => {
  const onPick = vi.fn();
  const onPickCanonical = vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickCanonical={onPickCanonical}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  fireEvent.change(screen.getByLabelText('Search objects or district code'), { target: { value: label } });
  const card = screen.getByRole('button', { name: new RegExp(`${label}.*Choose & place`) });
  expect(card.querySelector('img')).toHaveAttribute('src', `/fixtures/${id}.png`);
  fireEvent.click(card);
  expect(onPick).toHaveBeenCalledExactlyOnceWith(id);
  expect(onPickCanonical).not.toHaveBeenCalled();
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
