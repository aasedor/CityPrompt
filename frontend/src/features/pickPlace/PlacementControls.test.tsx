import { useState } from 'react';
import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
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
  it.each([asset, PLACE_ASSETS.find(candidate => candidate.zoneType === 'green_space')!])('rotates a $label placement with Q/E and Shift for fine control', selected => {
    function KeyboardHarness() {
      const [draft, setDraft] = useState<PlacementDraft>({ assetId: selected.id, width: selected.width, depth: selected.depth, degrees: 0 });
      return <><PlacementControls draft={draft} onChange={setDraft} /><pre data-testid="draft">{JSON.stringify(draft)}</pre></>;
    }
    render(<KeyboardHarness />);
    fireEvent.keyDown(window, { key: 'q' });
    expect(current().degrees).toBe(15);
    expect(screen.getByLabelText('Placement degrees')).toHaveProperty('value', '15');
    fireEvent.keyDown(window, { key: 'E', shiftKey: true });
    expect(current().degrees).toBe(14);
    fireEvent.keyDown(window, { key: 'e' });
    expect(current().degrees).toBe(359);
    expect(current()).toMatchObject({ width: selected.width, depth: selected.depth });
  });
  it('leaves typing, browser shortcuts and IME composition alone', () => {
    render(<Harness />);
    for (const target of [screen.getByLabelText('Placement width'), document.createElement('textarea'), document.createElement('select')]) {
      if (!target.isConnected) document.body.append(target);
      fireEvent.keyDown(target, { key: 'q' });
      if (target.tagName !== 'INPUT') target.remove();
    }
    const editable = document.createElement('div');
    editable.setAttribute('contenteditable', 'true');
    const child = editable.appendChild(document.createElement('span'));
    document.body.append(editable);
    fireEvent.keyDown(child, { key: 'q' });
    editable.remove();
    for (const modifier of ['ctrlKey', 'metaKey', 'altKey', 'isComposing']) fireEvent.keyDown(window, { key: 'q', [modifier]: true });
    expect(current().degrees).toBe(0);
  });
  it('consumes rotation while active and removes the listener when placement closes', () => {
    const bubble = vi.fn();
    window.addEventListener('keydown', bubble);
    const view = render(<Harness />);
    const key = new KeyboardEvent('keydown', { key: 'q', bubbles: true, cancelable: true });
    fireEvent(window, key);
    expect(key.defaultPrevented).toBe(true);
    expect(bubble).not.toHaveBeenCalled();
    view.unmount();
    fireEvent.keyDown(window, { key: 'q' });
    expect(bubble).toHaveBeenCalledOnce();
    window.removeEventListener('keydown', bubble);
  });
  it('does not clear an unfinished dimension when rotating', () => {
    render(<Harness />);
    fireEvent.change(screen.getByLabelText('Placement width'), { target: { value: '' } });
    fireEvent.keyDown(window, { key: 'q' });
    expect(current().inputError).toBeTruthy();
    expect(screen.getByLabelText('Placement width')).toHaveProperty('value', '');
  });
  it('starts manual rotation from the street-facing preview, then keeps the new angle', () => {
    function StreetHarness() {
      const [draft, setDraft] = useState<PlacementDraft>({ assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 0, faceStreet: true });
      return <><PlacementControls draft={draft} onChange={setDraft} getPreviewDegrees={() => 92} /><pre data-testid="draft">{JSON.stringify(draft)}</pre></>;
    }
    render(<StreetHarness />);
    fireEvent.keyDown(window, { key: 'q' });
    expect(current()).toMatchObject({ degrees: 107, faceStreet: false });
    fireEvent.keyDown(window, { key: 'q' });
    expect(current().degrees).toBe(122);
    fireEvent.change(screen.getByLabelText('Placement depth'), { target: { value: String(asset.depth + 1) } });
    expect(current().degrees).toBe(122);
  });
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
