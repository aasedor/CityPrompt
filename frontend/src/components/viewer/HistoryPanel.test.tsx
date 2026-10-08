import { beforeEach, describe, expect, it, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HistoryPanel } from './HistoryPanel';
import { useUndoRedoStore } from '@/store/undoRedo';
import { zoneHistoryApi } from '@/services/api';
import type { SiteZone, ZoneHistoryEntry } from '@/types';
const fixture = vi.hoisted(() => ({ history: [] as ZoneHistoryEntry[] }));
vi.mock('@/hooks/useZoneHistory', () => ({ useZoneHistory: () => ({ history: fixture.history, total: 1, isLoading: false, hasMore: false, loadMore: vi.fn() }) }));
vi.mock('@/services/api', () => ({ zoneHistoryApi: { revert: vi.fn(), restoreSnapshot: vi.fn() } }));
const zone = { id: 'z', project_id: 'p', name: 'House', zone_type: 'building', properties: { height: 20 }, coordinates: [[0,0],[1,0],[1,1]], color: '#777', sort_order: 0, created_at: '2026-10-01', updated_at: '2026-10-01' } as SiteZone;
beforeEach(() => { vi.clearAllMocks(); useUndoRedoStore.getState().clearHistory(); useUndoRedoStore.getState().setProjectScope('p'); });
function show(action: ZoneHistoryEntry['action']) {
  fixture.history = [{ id: 'h', zone_id: 'z', project_id: 'p', action, snapshot: { ...zone }, previous_snapshot: { ...zone, properties: { height: 10 } }, created_at: '2026-10-01' }];
  render(<QueryClientProvider client={new QueryClient()}><HistoryPanel projectId="p" siteZones={action === 'delete' ? [] : [zone]} onClose={() => {}} /></QueryClientProvider>);
  fireEvent.click(screen.getByText(action === 'create' ? 'Created' : action === 'delete' ? 'Deleted' : 'Updated'));
}
describe('history action semantics', () => {
  it.each(['create', 'update', 'delete'] as const)('restores the displayed %s snapshot and can undo that restoration', async action => {
    vi.mocked(zoneHistoryApi.restoreSnapshot).mockResolvedValue({ zone_id: 'z', deleted: false, zone });
    show(action);
    fireEvent.click(screen.getByRole('button', { name: action === 'delete' ? 'Restore deleted object' : 'Restore this version' }));
    await waitFor(() => expect(zoneHistoryApi.restoreSnapshot).toHaveBeenCalledWith('p', 'z', zone));
    expect(zoneHistoryApi.revert).not.toHaveBeenCalled();
    await waitFor(() => expect(useUndoRedoStore.getState().undoStack).toHaveLength(1));
    await act(async () => useUndoRedoStore.getState().undo());
    expect(zoneHistoryApi.restoreSnapshot).toHaveBeenLastCalledWith('p', 'z', action === 'delete' ? null : zone);
  });
  it('labels undoing creation explicitly and allows recovering the removed object', async () => {
    vi.mocked(zoneHistoryApi.revert).mockResolvedValue(zone);
    show('create');
    expect(screen.getByText(/Undoing this change removes/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Undo this change' }));
    await waitFor(() => expect(zoneHistoryApi.revert).toHaveBeenCalledWith('h'));
    await waitFor(() => expect(useUndoRedoStore.getState().undoStack).toHaveLength(1));
    await act(async () => useUndoRedoStore.getState().undo());
    expect(zoneHistoryApi.restoreSnapshot).toHaveBeenCalledWith('p', 'z', zone);
  });
});
