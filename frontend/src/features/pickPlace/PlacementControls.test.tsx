import { useState } from 'react';
import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { PlacementControls } from './PlacementControls';
import type { PlacementDraft } from './GlobePlacementPreview';
import { PLACE_ASSETS } from './catalogue';
import { generatedPlacementDraft } from './generatedPlacement';

const asset = PLACE_ASSETS[0];
const vancouver = PLACE_ASSETS.find(candidate => candidate.id === 'clay_vancouver_balcony_podium_tower')!;
function Harness() {
  const [draft, setDraft] = useState<PlacementDraft>({ assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 0 });
  return <><PlacementControls draft={draft} onChange={setDraft} /><pre data-testid="draft">{JSON.stringify(draft)}</pre></>;
}
function VancouverHarness() {
  const [draft, setDraft] = useState<PlacementDraft>({ assetId: vancouver.id, width: vancouver.width, depth: vancouver.depth, degrees: 0 });
  return <><PlacementControls draft={draft} onChange={setDraft} /><pre data-testid="draft">{JSON.stringify(draft)}</pre></>;
}
function GeneratedHarness() {
  const [draft, setDraft] = useState<PlacementDraft>(() => generatedPlacementDraft({
    id: 'my-house', project_id: 'original', name: 'My house', preview_url: null,
    model_url: '/api/v1/files/projects/original/models/my-house.glb',
    floor_count: 2, height_meters: 7.5, width_m: 12, depth_m: 16, size_estimated: false,
  }));
  return <><PlacementControls draft={draft} onChange={setDraft} /><pre data-testid="draft">{JSON.stringify(draft)}</pre></>;
}
const current = () => JSON.parse(screen.getByTestId('draft').textContent!) as PlacementDraft;
afterEach(cleanup);
describe('pre-placement reshaping', () => {
  it('updates the actual placement immediately without another button or blur', () => {
    render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: String(asset.minWidth + 1.5) } });
    expect(current().width).toBe(asset.minWidth + 1.5);
    expect(current().inputError).toBeUndefined();
    expect(screen.queryByText('Update placement preview')).toBeNull();
  });
  it.each(['', '0', String(asset.maxSize + 1)])('marks invalid width %j as unplaceable and recovers when corrected', value => {
    render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value } });
    expect(current().inputError).toBeTruthy();
    expect(screen.getByRole('status').textContent).toContain('Enter dimensions');
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: String(asset.minWidth) } });
    expect(current().inputError).toBeUndefined();
    expect(current().width).toBe(asset.minWidth);
  });
  it('keeps invalid depth unplaceable even while another valid field changes', () => {
    render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement depth'), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: String(asset.minWidth + 1) } });
    expect(current().inputError).toBeTruthy();
    fireEvent.change(screen.getByLabelText('Placement depth'), { target: { value: String(asset.minDepth + 2) } });
    expect(current()).toMatchObject({ width: asset.minWidth + 1, depth: asset.minDepth + 2 });
  });
  it('preserves the typed negative angle while normalizing the placement and rejects a blank angle', () => {
    render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '-90' } });
    expect(current().degrees).toBe(270);
    expect((screen.getByLabelText('Placement degrees') as HTMLInputElement).value).toBe('-90');
    fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '' } });
    expect(current().inputError).toBeTruthy();
    fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '450' } });
    expect(current().degrees).toBe(90);
    expect(current().inputError).toBeUndefined();
  });
  it('restores unfinished entries if the placement controls are temporarily hidden', () => {
    const first = render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: '' } });
    const draft = current();
    first.unmount();
    render(<PlacementControls draft={draft} onChange={() => {}} />);
    expect((screen.getByLabelText('Placement width') as HTMLInputElement).value).toBe('');
    expect(screen.getByRole('status').textContent).toContain('Enter dimensions');
  });
  it('uses Vancouver’s reviewed per-axis footprint limits before placement', () => {
    render(<VancouverHarness />);
    expect(screen.getByLabelText('Placement width')).toMatchObject({ min: '51.1', max: '57.5' });
    expect(screen.getByLabelText('Placement depth')).toMatchObject({ min: '43.1', max: '47.5' });
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: '58' } });
    expect(current().inputError).toBeTruthy();
  });
  it('lets a saved model resize and rotate before click placement', () => {
    render(<GeneratedHarness />);
    expect(screen.getByText('My house')).toBeTruthy();
    expect(screen.getByText(/starting size matches the original plot/)).toBeTruthy();
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: '14' } });
    fireEvent.change(screen.getByLabelText('Placement degrees'), { target: { value: '45' } });
    expect(current()).toMatchObject({ width: 14, depth: 16, degrees: 45 });
    fireEvent.change(screen.getByLabelText('Placement depth'), { target: { value: '101' } });
    expect(current().inputError).toBeTruthy();
  });
});
