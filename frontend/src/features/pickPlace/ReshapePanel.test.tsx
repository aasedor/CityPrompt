import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import { reshapeParkOutline, parkOutlineDimensions } from './parkOutline';
import type { SiteZone } from '@/types';
import { ReshapePanel } from './ReshapePanel';
import { rectangleAt, rectangleDimensions } from './geometry';
import { placeAsset, placementProperties } from './catalogue';
import release from '@/data/publicRealmRelease20261023.json';
vi.mock('./publicRealmRelease', async () => {
 const actual=await vi.importActual<typeof import('./publicRealmRelease')>('./publicRealmRelease');
 const assets=actual.publicRealmReleaseRows(true).map(row=>row.asset);
 return {...actual,PUBLIC_REALM_RELEASE_ASSETS:assets,PUBLIC_REALM_RELEASE_SAVED_ASSETS:assets};
});
afterEach(cleanup);

it('keeps a brick podium tower footprint fixed while retaining its storey controls', () => {
  const asset = placeAsset('claude_trial_brick_podium_condo_tower');
  const zone = {id:'tower', zone_type:'building', properties:placementProperties(asset),
    coordinates:rectangleAt([-114,51],asset.width + 0.04,asset.depth + 0.04)} as SiteZone;
  const onReshape = vi.fn();
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={vi.fn()}/>);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.getByText(/footprint.*move and rotate/i)).toBeTruthy();
  expect(screen.getByLabelText('Storeys')).toBeEnabled();
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), {target:{value:'5'}});
  fireEvent.click(screen.getByRole('button',{name:'Apply shape'}));
  const actual = rectangleDimensions(onReshape.mock.calls[0][0]);
  expect(actual.width).toBeCloseTo(57.04,5);
  expect(actual.depth).toBeCloseTo(47.04,5);
});

it('keeps a flexible park recognisable without offering an incompatible fixed layout', () => {
  const asset = placeAsset('flexible_pocket_park_v1');
  // Shape-first drawing previously saved the programme without its picker ID.
  const zone = {id:'flexible', zone_type:'green_space', properties:{...asset.properties},
    coordinates:rectangleAt([-114,51],36,30)} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateParkLayout={vi.fn()}/>);
  expect(screen.getByRole('heading',{name:/Flexible Pocket Park/i})).toBeTruthy();
  expect(screen.queryByRole('combobox',{name:'Park layout'})).toBeNull();
  expect(screen.getByLabelText('Plot width (m)')).toBeEnabled();
});

it('shows move and rotation instructions without unsupported native-house plot controls', () => {
  const asset=placeAsset('infill_home');
  const zone={id:'infill',zone_type:'building',properties:placementProperties(asset),coordinates:rectangleAt([-114,51],12,16)} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()}/>);
  expect(screen.getByText(/Fixed native footprint: move and rotate only/)).toBeInTheDocument();
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Rotation (degrees)')).toBeEnabled();
  expect(screen.queryByText(/Drag the object to move it/)).toBeNull();
});

it('keeps Vancouver storey controls while hiding unsupported plot resizing', () => {
  const asset = placeAsset('clay_vancouver_balcony_podium_tower');
  const zone = { id: 'vancouver', zone_type: 'building', properties: placementProperties(asset),
    coordinates: rectangleAt([-114, 51], asset.width, asset.depth) } as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={vi.fn()} />);
  expect(screen.getByText(/Fixed native footprint: move and rotate only/)).toBeInTheDocument();
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Storeys')).toBeEnabled();
});

it('keeps the reviewed building footprint slider available independently of plot resizing', () => {
  const asset = placeAsset('trial_postwar_bungalow');
  const zone = { id: 'bungalow', zone_type: 'building', properties: placementProperties(asset),
    coordinates: rectangleAt([-114, 51], asset.width, asset.depth) } as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={vi.fn()} />);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Building footprint (%)')).toBeEnabled();
  fireEvent.change(screen.getByLabelText('Building footprint (%)'), { target: { value: '95' } });
  expect(screen.getByLabelText('Building footprint (%)')).toHaveValue('95');
});

it('rotates a 40-storey Vancouver tower without changing its plot size or height contract', () => {
  const asset = placeAsset('clay_vancouver_balcony_podium_tower');
  const properties = { ...placementProperties(asset), floors: 40, floor_count: 40,
    height: 135.6, height_m: 135.6, development_height_override_m: 135.6 };
  const zone = { id: 'vancouver', project_id: 'project', zone_type: 'building', properties,
    coordinates: rectangleAt([-114, 51], asset.width, asset.depth), name: 'Vancouver tower',
    color: '#fff', sort_order: 0, created_at: 'now', updated_at: 'now' } as SiteZone;
  const onReshape = vi.fn();
  const onUpdateDesign = vi.fn();
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onUpdateDesign={onUpdateDesign} />);
  expect(screen.getByLabelText('Storeys')).toHaveValue(40);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), { target: { value: '15' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  expect(onReshape).toHaveBeenCalledOnce();
  const result = rectangleDimensions(onReshape.mock.calls[0][0]);
  expect(result.width).toBeCloseTo(asset.width, 5);
  expect(result.depth).toBeCloseTo(asset.depth, 5);
  expect(result.degrees).toBeCloseTo(15, 5);
  expect(onUpdateDesign).not.toHaveBeenCalled();
  expect(properties).toMatchObject({ floors: 40, floor_count: 40, height_m: 135.6,
    development_height_override_m: 135.6 });
});

it('preserves an irregular adaptive park footprint when no native layout is bound', () => {
  const asset = placeAsset('native-park:urban_pocket_park_v0--native-v1');
  const onReshape = vi.fn();
  const coordinates = reshapeParkOutline(rectangleAt([-114, 51], 40, 40), 40, 40, 0, 'l_shape');
  const zone = { id: 'pocket-park', zone_type: 'green_space', properties: placementProperties(asset), coordinates } as SiteZone;
  expect(zone.properties?.green_space_native_layout).toBeUndefined();
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Plot width (m)'), { target: { value: '50' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  const result = parkOutlineDimensions(onReshape.mock.calls[0][0]);
  expect(result.width).toBeCloseTo(50, 2);
  expect(result.normalized).toHaveLength(6);
  result.normalized.forEach((p, i) => p.forEach((v, axis) => expect(v).toBeCloseTo(parkOutlineDimensions(coordinates).normalized[i][axis], 5)));
});

it('hides native park resizing and outline controls while retaining exact rotation', () => {
  const asset = placeAsset('native-park:urban_pocket_park_v0--native-v1');
  const coordinates = rectangleAt([-114, 51], 40.04, 40.04);
  const zone = { id: 'native-park', zone_type: 'green_space',
    properties: placementProperties(asset, undefined, coordinates), coordinates } as SiteZone;
  expect(zone.properties?.green_space_native_layout).toBeDefined();
  const onReshape = vi.fn();
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Park outline')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Add outline point' })).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), { target: { value: '10' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  const result = parkOutlineDimensions(onReshape.mock.calls[0][0]);
  // Local longitude/latitude projection changes by sub-millimetres on rotation;
  // the visible one-decimal controls must still never round away this 4 cm.
  expect(result.width).toBeCloseTo(40.04, 3);
  expect(result.depth).toBeCloseTo(40.04, 3);
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

it('rotates a fixed model without rounding away its saved fractional footprint', () => {
  const asset = placeAsset('validation_brewery_crystal_brewhouse');
  const zone = { id: 'fixed-fractional', zone_type: 'building', properties: placementProperties(asset),
    coordinates: rectangleAt([-114, 51], asset.width + 0.04, asset.depth + 0.04) } as SiteZone;
  const onReshape = vi.fn();
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={onReshape}
    onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} />);
  expect(screen.queryByLabelText('Plot width (m)')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Plot depth (m)')).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Rotation (degrees)'), { target: { value: '5' } });
  fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
  const actual = rectangleDimensions(onReshape.mock.calls[0][0]);
  expect(actual.width).toBeCloseTo(asset.width + 0.04, 5);
  expect(actual.depth).toBeCloseTo(asset.depth + 0.04, 5);
});


it('withholds terrace controls from fixed park and street scenes while retaining ordinary buildings', () => {
 for (const zoneType of ['green_space','road']) {
  const row=release.models.find(row=>(row.status==='ready'||row.status==='runtime_trial')&&row.asset.zoneType===zoneType)!;
  const asset=placeAsset(row.asset.id);
  const zone={id:'fixed-'+zoneType,zone_type:zoneType,properties:placementProperties(asset),coordinates:rectangleAt([-114,51],asset.width,asset.depth)} as SiteZone;
  render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onTerrace={vi.fn()}/>);
  expect(screen.queryByRole('button',{name:'Terrace & path'})).toBeNull();cleanup();
 }
 const asset=placeAsset('infill_home');
 const zone={id:'house',zone_type:'building',properties:placementProperties(asset),coordinates:rectangleAt([-114,51],12,16)} as SiteZone;
 render(<ReshapePanel zone={zone} disabled={false} onDuplicate={vi.fn()} onReshape={vi.fn()} onClose={vi.fn()} onDelete={vi.fn()} onMore={vi.fn()} onTerrace={vi.fn()}/>);
 expect(screen.getByRole('button',{name:'Terrace & path'})).toBeTruthy();
});
