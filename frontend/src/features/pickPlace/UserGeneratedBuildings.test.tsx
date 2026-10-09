import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { PlacementPalette } from './PlacementPalette';
import { UserGeneratedBuildings } from './UserGeneratedBuildings';

const list = vi.hoisted(() => vi.fn());
vi.mock('@/services/api', async importOriginal => ({ ...(await importOriginal<typeof import('@/services/api')>()),
  modelLibraryApi: { userGenerated: list },
}));
const home = { id: 'home', project_id: 'private-project', name: 'My red house', preview_url: null,
  model_url: '/api/v1/files/projects/p/models/a.glb', floor_count: 2, height_meters: 7.5,
  width_m: 12, depth_m: 16, size_estimated: false };
afterEach(() => { cleanup(); vi.clearAllMocks(); });

it('separates private creations in the building category and selects a reusable source', async () => {
  list.mockResolvedValue([home]);
  const pick = vi.fn();
  render(<PlacementPalette selected={null} onPick={vi.fn()} onPickCanonical={vi.fn()} onPickGenerated={pick} onCancel={vi.fn()} status="ready" message="" onRetry={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Buildings' }));
  fireEvent.click(screen.getByRole('button', { name: /^Browse all / }));
  fireEvent.change(screen.getByLabelText('Object category'), { target: { value: 'user-generated' } });
  expect(await screen.findByText('My red house')).toBeTruthy();
  expect(screen.queryByText('Halifax clapboard house')).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: /My red house.*Choose & place/ }));
  expect(pick).toHaveBeenCalledWith(home);
  expect(screen.queryByRole('dialog')).toBeNull();
});

it('shows an actionable empty category without sample models from other accounts', async () => {
  list.mockResolvedValue([]);
  render(<UserGeneratedBuildings query="" onPick={vi.fn()} />);
  expect(await screen.findByText(/No user generated buildings yet/)).toBeTruthy();
});

it('recovers a failed listing and searches only the returned personal models', async () => {
  list.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce([home]);
  const { rerender } = render(<UserGeneratedBuildings query="" onPick={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Try again' }));
  expect(await screen.findByText('My red house')).toBeTruthy();
  rerender(<UserGeneratedBuildings query="absent" onPick={vi.fn()} />);
  expect(screen.getByText('No generated buildings match your search.')).toBeTruthy();
  await waitFor(() => expect(list).toHaveBeenCalledTimes(2));
});
