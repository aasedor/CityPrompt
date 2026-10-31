import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { placeAsset, placementProperties } from './catalogue';
import { rectangleAt, rectangleDimensions } from './geometry';
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

it('offers rotation with hidden fixed court dimensions before placement', () => {
  const onChange = vi.fn();
  render(<PlacementControls draft={{assetId:asset.id,width:asset.width,depth:asset.depth,degrees:0}} onChange={onChange}/>);
  expect(screen.queryByLabelText('Placement width')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Placement depth')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Placement degrees')).toBeEnabled();
  fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '45' } });
  expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 45 }));
});

it('offers repeat and rotation without misleading outline or resize controls after placement', () => {
  const coordinates=rectangleAt([-114,51],asset.width,asset.depth);
  const zone={id:'court',zone_type:'green_space',coordinates,properties:placementProperties(asset,1040,coordinates)} as SiteZone;
  const onReshape = vi.fn(), onDuplicate = vi.fn();
  const originalProperties = JSON.stringify(zone.properties);
  render(<ReshapePanel zone={zone} disabled={false} onReshape={onReshape} onClose={vi.fn()}
    onDelete={vi.fn()} onDuplicate={onDuplicate} onMore={vi.fn()} onTerrace={vi.fn()} onUpdateParkLayout={vi.fn()}/>);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Rotation (degrees)')).toBeEnabled();
  expect(screen.getByRole('button',{name:'Place another'})).toBeEnabled();
  expect(screen.queryByRole('combobox',{name:'Park outline'})).toBeNull();
  expect(screen.getByRole('combobox',{name:'Park layout'})).toHaveValue('court_only_basketball_v1--native-v1');
  expect(screen.queryByText(/Enlarging the parcel/)).toBeNull();
  expect(screen.queryByRole('button',{name:'Terrace & path'})).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Place another' }));
  expect(onDuplicate).toHaveBeenCalledWith(asset.id, asset.width, asset.depth, 0);
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), { target: { value: '45' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  expect(onReshape).toHaveBeenCalledOnce();
  const dimensions = rectangleDimensions(onReshape.mock.calls[0][0]);
  expect(dimensions.width).toBeCloseTo(asset.width, 3);
  expect(dimensions.depth).toBeCloseTo(asset.depth, 3);
  expect(dimensions.degrees).toBeCloseTo(45, 3);
  expect(JSON.stringify(zone.properties)).toBe(originalProperties);
});
