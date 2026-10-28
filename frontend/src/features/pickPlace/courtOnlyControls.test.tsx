import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { placeAsset, placementProperties } from './catalogue';
import { rectangleAt } from './geometry';
import { PlacementControls } from './PlacementControls';
import { ReshapePanel } from './ReshapePanel';
import { PlacementPalette } from './PlacementPalette';

afterEach(cleanup);
const asset = placeAsset('native-park:court_only_basketball_v1--native-v1');

it.each([
  ['Basketball court', 'basketball'], ['Tennis court', 'tennis'],
  ['Pickleball court', 'pickleball'], ['Beach volleyball court', 'beach_volleyball'],
])('finds and places the court-only design under %s through the actual student catalogue', (label, variant) => {
  const onPick=vi.fn();
  render(<PlacementPalette selected={null} onPick={onPick} onPickCanonical={vi.fn()}
    onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Parks'}));
  fireEvent.change(screen.getByLabelText('Search objects or district code'),{target:{value:'court only'}});
  expect(screen.getAllByRole('article')).toHaveLength(4);
  fireEvent.click(screen.getByRole('button',{name:`${label} · Choose & place`}));
  expect(onPick).toHaveBeenCalledWith(`native-park:court_only_${variant}_v1--native-v1`);
});

it('offers rotation with disabled court dimensions before placement', () => {
  render(<PlacementControls draft={{assetId:asset.id,width:asset.width,depth:asset.depth,degrees:0}} onChange={vi.fn()}/>);
  expect(screen.getByLabelText('Placement width')).toBeDisabled();
  expect(screen.getByLabelText('Placement depth')).toBeDisabled();
  expect(screen.getByLabelText('Placement degrees')).toBeEnabled();
});

it('offers repeat and rotation without misleading outline or resize controls after placement', () => {
  const coordinates=rectangleAt([-114,51],asset.width,asset.depth);
  const zone={id:'court',zone_type:'green_space',coordinates,properties:placementProperties(asset,1040,coordinates)} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onReshape={vi.fn()} onClose={vi.fn()}
    onDelete={vi.fn()} onDuplicate={vi.fn()} onMore={vi.fn()} onTerrace={vi.fn()} onUpdateParkLayout={vi.fn()}/>);
  expect(screen.getByLabelText('Plot width (m)')).toBeDisabled();
  expect(screen.getByLabelText('Plot depth (m)')).toBeDisabled();
  expect(screen.getByLabelText('Rotation (degrees)')).toBeEnabled();
  expect(screen.getByRole('button',{name:'Place another'})).toBeEnabled();
  expect(screen.queryByRole('combobox',{name:'Park outline'})).toBeNull();
  expect(screen.getByRole('combobox',{name:'Park layout'})).toHaveValue('court_only_basketball_v1--native-v1');
  expect(screen.queryByText(/Enlarging the parcel/)).toBeNull();
  expect(screen.queryByRole('button',{name:'Terrace & path'})).toBeNull();
});
