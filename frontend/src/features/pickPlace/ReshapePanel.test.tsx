import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import { reshapeParkOutline, parkOutlineDimensions } from './parkOutline';
import type { SiteZone } from '@/types';
import { ReshapePanel } from './ReshapePanel';
import { rectangleAt } from './geometry';
import { placeAsset, placementProperties } from './catalogue';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { canonicalBuildingAsset } from './canonicalBuildingPlacement';
afterEach(cleanup);

it('preserves an older irregular building footprint when resizing', () => {
  const choice = CANONICAL_CHOICES.find(c => c.option.id === 'brownstone_rowhouse_frontage')!;
  const asset = canonicalBuildingAsset({ choice, variant: choice.option.variants![0] });
  const onReshape = vi.fn();
  const coordinates = reshapeParkOutline(rectangleAt([-114, 51], 20, 24), 20, 24, 0, 'l_shape');
  const zone = { id: 'older-building', zone_type: 'building', properties: placementProperties(asset), coordinates } as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '30' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  const result = parkOutlineDimensions(onReshape.mock.calls[0][0]);
  expect(result.width).toBeCloseTo(30, 2);
  expect(result.normalized).toHaveLength(6);
  result.normalized.forEach((p, i) => p.forEach((v, axis) => expect(v).toBeCloseTo(parkOutlineDimensions(coordinates).normalized[i][axis], 5)));
});

it('explains when an irregular sports park cannot contain a complete court', () => {
  const asset=placeAsset('park_trio_basketball');
  const zone={id:'small-triangle',zone_type:'green_space',properties:placementProperties(asset),
    coordinates:reshapeParkOutline(rectangleAt([-114,51],55,40),55,40,0,'triangle')} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()}/>);
  expect(screen.getByRole('status').textContent).toMatch(/fit|usable|outline/i);
});

it('duplicates a minimum-size park without floating-point tails or under-minimum input', () => {
  const asset = placeAsset('park_trio_basketball');
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
