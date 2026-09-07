import { useState } from 'react';
import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { PlacementControls } from './PlacementControls';
import type { PlacementDraft } from './GlobePlacementPreview';
import { PLACE_ASSETS } from './catalogue';

const asset = PLACE_ASSETS[0];
function Harness() {
  const [draft, setDraft] = useState<PlacementDraft>({ assetId: asset.id, width: asset.width, depth: asset.depth, degrees: 0 });
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
});
