import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import { reshapeParkOutline, parkOutlineDimensions } from './parkOutline';
import type { SiteZone } from '@/types';
import { ReshapePanel } from './ReshapePanel';
import { rectangleAt } from './geometry';
import { placeAsset, placementProperties } from './catalogue';
afterEach(cleanup);

it('points native-house students to the working Move handle', () => {
  const asset=placeAsset('infill_home');
  const zone={id:'infill',zone_type:'building',properties:placementProperties(asset),coordinates:rectangleAt([-114,51],12,16)} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()}/>);
  expect(screen.getByText(/Drag the Move handle on the selected plot/)).toBeTruthy();
  expect(screen.queryByText(/Drag the object to move it/)).toBeNull();
});

it('preserves an irregular authored park footprint when resizing', () => {
  const asset = placeAsset('native-park:urban_pocket_park_v0--native-v1');
  const onReshape = vi.fn();
  const coordinates = reshapeParkOutline(rectangleAt([-114, 51], 40, 40), 40, 40, 0, 'l_shape');
  const zone = { id: 'pocket-park', zone_type: 'green_space', properties: placementProperties(asset), coordinates } as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '50' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  const result = parkOutlineDimensions(onReshape.mock.calls[0][0]);
  expect(result.width).toBeCloseTo(50, 2);
  expect(result.normalized).toHaveLength(6);
  result.normalized.forEach((p, i) => p.forEach((v, axis) => expect(v).toBeCloseTo(parkOutlineDimensions(coordinates).normalized[i][axis], 5)));
});

it('states that a rejected building rotation was not saved', () => {
  const asset = placeAsset('validation_brewery_crystal_brewhouse');
  const zone = { id: 'brewhouse', zone_type: 'building', properties: placementProperties(asset),
    coordinates: rectangleAt([-114, 51], 52, 68) } as SiteZone;
  const onReshape = vi.fn(() => false);
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), { target: { value: '10' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  expect(onReshape).toHaveBeenCalledOnce();
  expect(screen.getByRole('alert').textContent).toMatch(/Shape not saved.*existing plot is unchanged/);
});

it('duplicates a minimum-size park without floating-point tails or under-minimum input', () => {
  const asset = placeAsset('validation_basketball_court_v1');
  const onDuplicate = vi.fn();
  const zone = { id: 'test', zone_type: 'green_space',
    coordinates: rectangleAt([-114.126, 51.017], 52, 39, 5),
    properties: placementProperties(asset) } as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={onDuplicate}
    onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Place another' }));
  expect(onDuplicate).toHaveBeenCalledWith(asset.id, 52, 39, 5);
});

it('keeps a nonrectangular park when a student changes its dimensions', () => {
  const asset=placeAsset('neighbourhood_park'), onReshape=vi.fn();
  const zone={id:'irregular',zone_type:'green_space',properties:placementProperties(asset),
    coordinates:reshapeParkOutline(rectangleAt([-114.13,51.01],90,80),90,80,0,'l_shape')} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()}/>);
  fireEvent.change(screen.getByLabelText('Plot width (m)'),{target:{value:'105'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply shape'}));
  expect(onReshape.mock.calls[0][0]).toHaveLength(6);
  expect(parkOutlineDimensions(onReshape.mock.calls[0][0]).width).toBeCloseTo(105,2);
  fireEvent.click(screen.getByRole('button',{name:'Add outline point'}));
  expect(onReshape.mock.calls[1][0]).toHaveLength(7);
});
