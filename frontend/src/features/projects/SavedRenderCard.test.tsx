import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { SavedRenderCard, savedRenderPreviewUrl } from './SavedRenderCard';

const access = vi.hoisted(() => ({ revision: 0, ticket: 'first', listeners: new Set<() => void>(), refresh: vi.fn().mockResolvedValue(undefined) }));
vi.mock('@/services/api', () => ({
  getAssetTicketRevision: () => access.revision,
  subscribeAssetTicketChanges: (listener: () => void) => { access.listeners.add(listener); return () => access.listeners.delete(listener); },
  refreshAssetTickets: access.refresh,
  resolveApiFileUrl: (url: string) => `${url}?asset_ticket=${access.ticket}`,
}));
const item = { id: 'r', image_url: '/api/v1/files/projects/p/renders/a.png', prompt: 'A park', style: 'photo', created_at: '2026-09-30' };
afterEach(() => { cleanup(); vi.clearAllMocks(); access.ticket = 'first'; access.revision = 0; });

it('loads a smaller preview but opens the unchanged original render', () => {
  const onSelect = vi.fn();
  const { container } = render(<SavedRenderCard render={item} onSelect={onSelect} />);
  const image = container.querySelector('img')!;
  expect(image.src).toContain('thumbnail=true');
  expect(image.src).toContain('asset_ticket=first');
  expect(screen.getByText('Loading preview…')).toBeTruthy();
  fireEvent.load(image);
  expect(screen.queryByRole('status')).toBeNull();
  fireEvent.click(screen.getByRole('button'));
  expect(onSelect).toHaveBeenCalledWith(item);
  expect(item.image_url).not.toContain('thumbnail');
});

it('falls back once then offers an explicit retry instead of a blank tile or loop', async () => {
  const { container } = render(<SavedRenderCard render={item} onSelect={vi.fn()} />);
  fireEvent.error(container.querySelector('img')!);
  await waitFor(() => expect(container.querySelector('img')!.src).not.toContain('thumbnail'));
  expect(access.refresh).toHaveBeenCalledTimes(1);
  fireEvent.error(container.querySelector('img')!);
  expect(screen.getByText('Preview unavailable. Click to retry.')).toBeTruthy();
  expect(access.refresh).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button', { name: 'Retry saved render preview' }));
  await waitFor(() => expect(access.refresh).toHaveBeenCalledTimes(2));
  fireEvent.load(container.querySelector('img')!);
  expect(screen.queryByRole('status')).toBeNull();
});

it('uses a renewed download ticket without reopening the gallery', () => {
  const { container } = render(<SavedRenderCard render={item} onSelect={vi.fn()} />);
  act(() => { access.ticket = 'renewed'; access.revision += 1; access.listeners.forEach(listener => listener()); });
  expect(container.querySelector('img')!.src).toContain('asset_ticket=renewed');
});

it('preserves shared-view access and leaves data images unchanged', () => {
  expect(savedRenderPreviewUrl(`${item.image_url}?share_token=shared`)).toContain('share_token=shared&thumbnail=true');
  expect(savedRenderPreviewUrl('data:image/png;base64,abc')).toBe('data:image/png;base64,abc');
  const remote = `https://example.org${item.image_url}`;
  expect(savedRenderPreviewUrl(remote)).toBe(remote);
});
