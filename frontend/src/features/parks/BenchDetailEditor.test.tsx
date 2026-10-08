import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { BenchDetailControls } from './BenchDetailEditor';
const zone = {
  id: 'park',
  project_id: 'trial',
  color: '#769952',
  sort_order: 0,
  created_at: '2026-10-08',
  updated_at: '2026-10-08',
  name: 'Trial park',
  zone_type: 'green_space',
  coordinates: rectangleAt([-114, 51], 70, 55),
  properties: {
    green_space_archetype_id: 'neighborhood_park',
    green_space_selected_variant_id: 'neighborhood_park_v0',
    neighborhood_park_layout: 'adaptive_rustic_v1',
  },
} as SiteZone;
describe('isolated bench editor', () => {
  it('pauses scene editing, keeps focus after keyboard deletion and restores the scene on close', () => {
    const onEditingChange = vi.fn();
    const root = document.createElement('div');
    root.id = 'root';
    document.body.append(root);
    render(
      <BenchDetailControls
        zone={zone}
        disabled={false}
        onSave={vi.fn()}
        onEditingChange={onEditingChange}
      />,
    );
    fireEvent.click(
      screen.getByRole('button', { name: 'Edit details · benches' }),
    );
    expect(onEditingChange).toHaveBeenLastCalledWith(true);
    expect(root).toHaveAttribute('inert');
    const before = screen.getAllByRole('button', {
      name: /^Select bench /,
    }).length;
    fireEvent.click(
      screen.getAllByRole('button', { name: /^Select bench / })[0],
    );
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Delete' });
    expect(
      screen.getAllByRole('button', { name: /^Select bench / }),
    ).toHaveLength(before - 1);
    expect(screen.getByRole('dialog')).toHaveFocus();
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'z', ctrlKey: true });
    expect(
      screen.getAllByRole('button', { name: /^Select bench / }),
    ).toHaveLength(before);
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' });
    expect(onEditingChange).toHaveBeenLastCalledWith(false);
    expect(root).not.toHaveAttribute('inert');
    root.remove();
  });
  it('exposes bench selection only inside the editor and keeps unsaved removal reversible', () => {
    const onSave = vi.fn();
    render(
      <BenchDetailControls zone={zone} disabled={false} onSave={onSave} />,
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    fireEvent.click(
      screen.getByRole('button', { name: 'Edit details · benches' }),
    );
    const before = screen.getAllByRole('button', {
      name: /^Select bench /,
    }).length;
    fireEvent.click(
      screen.getAllByRole('button', { name: /^Select bench / })[0],
    );
    fireEvent.click(screen.getByRole('button', { name: 'Remove bench' }));
    expect(
      screen.getAllByRole('button', { name: /^Select bench / }),
    ).toHaveLength(before - 1);
    fireEvent.click(screen.getByRole('button', { name: 'Undo detail edit' }));
    expect(
      screen.getAllByRole('button', { name: /^Select bench / }),
    ).toHaveLength(before);
    fireEvent.click(
      screen.getByRole('button', { name: 'Close detail editor' }),
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(onSave).not.toHaveBeenCalled();
  });
  it('adds, moves and saves benches through the existing zone save callback', async () => {
    const onSave = vi.fn().mockResolvedValue({});
    render(
      <BenchDetailControls zone={zone} disabled={false} onSave={onSave} />,
    );
    fireEvent.click(
      screen.getByRole('button', { name: 'Edit details · benches' }),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Add bench' }));
    fireEvent.click(screen.getByRole('button', { name: 'Move bench east' }));
    fireEvent.click(screen.getByRole('button', { name: 'Save details' }));
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    expect(
      onSave.mock.calls[0][0].bench_details.items.some((b: { id: string }) =>
        b.id.startsWith('bench-'),
      ),
    ).toBe(true);
  });
  it('retains the draft if saving fails', async () => {
    render(
      <BenchDetailControls
        zone={zone}
        disabled={false}
        onSave={vi.fn().mockRejectedValue(new Error('offline'))}
      />,
    );
    fireEvent.click(
      screen.getByRole('button', { name: 'Edit details · benches' }),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Add bench' }));
    fireEvent.click(screen.getByRole('button', { name: 'Save details' }));
    expect(await screen.findByText(/Could not save/)).toBeInTheDocument();
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});
