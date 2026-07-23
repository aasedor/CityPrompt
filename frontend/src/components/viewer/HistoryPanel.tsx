import { useMemo, useState, useCallback } from 'react';
import { X, Undo2, Redo2, ChevronDown, Clock, MapPin, ArrowRight } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useZoneHistory } from '@/hooks/useZoneHistory';
import { zoneHistoryApi } from '@/services/api';
import { useViewerStore } from '@/store';
import {
  getUndoableActionZoneId,
  selectCanRedoForZone,
  selectCanUndoForZone,
  type UndoableAction,
  useUndoRedoStore,
} from '@/store/undoRedo';
import type { ZoneHistoryEntry, SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';

interface HistoryPanelProps {
  projectId: string;
  siteZones: SiteZone[];
  onClose: () => void;
}

const ACTION_CONFIG = {
  create: { label: 'Created', color: 'text-green-700', bg: 'bg-green-100', dot: 'bg-green-500' },
  update: { label: 'Updated', color: 'text-blue-700', bg: 'bg-blue-100', dot: 'bg-blue-500' },
  delete: { label: 'Deleted', color: 'text-red-700', bg: 'bg-red-100', dot: 'bg-red-500' },
} as const;

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatFullDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
  });
}

// ---------------------------------------------------------------------------
// Diff: compare previous_snapshot → snapshot
// ---------------------------------------------------------------------------

interface DiffLine {
  label: string;
  from?: string;
  to?: string;
  kind: 'changed' | 'added' | 'removed' | 'info';
}

function fmtVal(v: unknown): string {
  if (v == null) return '—';
  if (typeof v === 'number') return String(Math.round(v * 100) / 100);
  if (typeof v === 'string') return v;
  return JSON.stringify(v);
}

const DISPLAY_KEYS: Record<string, string> = {
  height: 'Height',
  floors: 'Floors',
  floor_height: 'Floor height',
  width: 'Width',
  tree_density: 'Tree density',
  roof_style: 'Roof style',
  unit_count: 'Units',
  description_text: 'Description',
};

function computeDiff(entry: ZoneHistoryEntry): DiffLine[] {
  const prev = entry.previous_snapshot;
  const cur = entry.snapshot;

  if (entry.action === 'create') {
    const lines: DiffLine[] = [{ label: 'Zone created', kind: 'added' }];
    const p = cur.properties;
    if (p?.height != null) lines.push({ label: 'Height', to: `${p.height}m`, kind: 'info' });
    if (p?.floors != null) lines.push({ label: 'Floors', to: `${p.floors}`, kind: 'info' });
    if (cur.coordinates?.length)
      lines.push({ label: 'Vertices', to: `${cur.coordinates.length}`, kind: 'info' });
    return lines;
  }

  if (entry.action === 'delete') {
    const lines: DiffLine[] = [{ label: 'Zone deleted', kind: 'removed' }];
    if (cur.name) lines.push({ label: 'Was', to: cur.name, kind: 'info' });
    return lines;
  }

  if (!prev) return [{ label: 'Properties updated', kind: 'changed' }];

  const lines: DiffLine[] = [];

  if ((cur.name ?? '') !== (prev.name ?? ''))
    lines.push({ label: 'Name', from: prev.name || '(none)', to: cur.name || '(none)', kind: 'changed' });

  if (cur.color !== prev.color)
    lines.push({ label: 'Color', from: prev.color, to: cur.color, kind: 'changed' });

  const curCoords = cur.coordinates ?? [];
  const prevCoords = prev.coordinates ?? [];
  if (JSON.stringify(curCoords) !== JSON.stringify(prevCoords)) {
    if (curCoords.length !== prevCoords.length)
      lines.push({ label: 'Vertices', from: `${prevCoords.length}`, to: `${curCoords.length}`, kind: 'changed' });
    else
      lines.push({ label: 'Position', to: 'moved', kind: 'changed' });
  }

  const curProps = cur.properties ?? {};
  const prevProps = prev.properties ?? {};
  for (const [key, label] of Object.entries(DISPLAY_KEYS)) {
    const pv = prevProps[key];
    const cv = curProps[key];
    if (fmtVal(pv) !== fmtVal(cv)) {
      const unit = key === 'height' || key === 'floor_height' || key === 'width' ? 'm' : '';
      if (pv == null && cv != null)
        lines.push({ label, to: `${fmtVal(cv)}${unit}`, kind: 'added' });
      else if (pv != null && cv == null)
        lines.push({ label, from: `${fmtVal(pv)}${unit}`, kind: 'removed' });
      else
        lines.push({ label, from: `${fmtVal(pv)}${unit}`, to: `${fmtVal(cv)}${unit}`, kind: 'changed' });
    }
  }

  return lines.length > 0 ? lines : [{ label: 'Properties updated', kind: 'changed' }];
}

// ---------------------------------------------------------------------------
// Zone labels: "Building #2", "Road #1", etc.
// ---------------------------------------------------------------------------

function useZoneLabels(siteZones: SiteZone[]) {
  return useMemo(() => {
    const counts: Record<string, number> = {};
    const labels: Record<string, string> = {};
    for (const z of siteZones) {
      const typeName = z.zone_type.replace(/_/g, ' ');
      counts[z.zone_type] = (counts[z.zone_type] ?? 0) + 1;
      labels[z.id] = z.name || `${typeName.charAt(0).toUpperCase() + typeName.slice(1)} #${counts[z.zone_type]}`;
    }
    return labels;
  }, [siteZones]);
}

// ---------------------------------------------------------------------------
// Single history entry (read-only timeline row)
// ---------------------------------------------------------------------------

function HistoryEntry({
  entry,
  zoneLabel,
  selected,
  onLocate,
  onSelect,
}: {
  entry: ZoneHistoryEntry;
  zoneLabel: string;
  selected: boolean;
  onLocate: (zoneId: string) => void;
  onSelect: (entry: ZoneHistoryEntry) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const config = ACTION_CONFIG[entry.action];
  const zoneColor = entry.snapshot.color || ZONE_TYPE_CONFIG[entry.snapshot.zone_type as keyof typeof ZONE_TYPE_CONFIG]?.color || '#9b59b6';
  const diffs = useMemo(() => computeDiff(entry), [entry]);

  return (
    <div className={`group relative border-b border-primary-950/[0.06] last:border-b-0 ${selected ? 'bg-blue-500/[0.05]' : ''}`}>
      <div className="absolute left-[18px] top-0 bottom-0 w-px bg-primary-950/[0.08]" />

      <button
        onClick={() => { onSelect(entry); setExpanded(!expanded); }}
        aria-pressed={selected}
        className={`relative flex w-full items-start gap-2.5 px-3 py-2 text-left transition-colors ${
          selected ? 'ring-1 ring-inset ring-blue-500/25' : 'hover:bg-primary-950/[0.03]'
        }`}
      >
        <div className={`relative z-10 mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ring-2 ring-white ${config.dot}`} />

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 shrink-0 rounded-sm border border-primary-950/10"
              style={{ backgroundColor: zoneColor }}
            />
            <span className="truncate text-[11px] font-semibold text-primary-950">
              {zoneLabel}
            </span>
            <span className={`shrink-0 rounded px-1 py-px text-[9px] font-semibold ${config.bg} ${config.color}`}>
              {config.label}
            </span>
          </div>

          <div className="mt-0.5 space-y-px">
            {diffs.slice(0, 2).map((d, i) => (
              <DiffLineInline key={i} diff={d} />
            ))}
            {diffs.length > 2 && !expanded && (
              <span className="text-[10px] text-primary-950/40">+{diffs.length - 2} more</span>
            )}
          </div>

          <div className="mt-0.5 flex items-center gap-1 text-[10px] text-primary-950/40">
            <span title={formatFullDate(entry.created_at)}>{formatTimeAgo(entry.created_at)}</span>
            {entry.user_email && (
              <>
                <span>·</span>
                <span className="truncate">{entry.user_email.split('@')[0]}</span>
              </>
            )}
          </div>
        </div>

        <ChevronDown
          size={11}
          className={`mt-1.5 shrink-0 text-primary-950/30 transition-transform ${expanded ? 'rotate-180' : ''}`}
        />
      </button>

      {expanded && (
        <div className="relative ml-[26px] mr-3 mb-2 rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.02]">
          <div className="space-y-1 px-2.5 py-2">
            {diffs.map((d, i) => (
              <DiffLineInline key={i} diff={d} />
            ))}
          </div>
          {entry.action !== 'delete' && (
            <div className="border-t border-primary-950/[0.06] px-2.5 py-1.5">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onLocate(entry.zone_id);
                }}
                className="flex w-full items-center justify-center gap-1 rounded-md border border-primary-950/10 bg-white px-2 py-1 text-[10px] font-medium text-primary-950/60 transition-colors hover:bg-primary-950/[0.04] hover:text-primary-950"
              >
                <MapPin size={10} />
                Locate on map
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Diff line display
// ---------------------------------------------------------------------------

function DiffLineInline({ diff }: { diff: DiffLine }) {
  if (diff.kind === 'added' && diff.to) {
    return (
      <div className="flex items-center gap-1 text-[10px]">
        <span className="text-primary-950/50">{diff.label}:</span>
        <span className="font-medium text-green-700">{diff.to}</span>
      </div>
    );
  }
  if (diff.kind === 'removed' && diff.from) {
    return (
      <div className="flex items-center gap-1 text-[10px]">
        <span className="text-primary-950/50">{diff.label}:</span>
        <span className="font-medium text-red-700 line-through">{diff.from}</span>
      </div>
    );
  }
  if (diff.kind === 'changed' && diff.from && diff.to) {
    return (
      <div className="flex items-center gap-1 text-[10px]">
        <span className="text-primary-950/50">{diff.label}:</span>
        <span className="text-primary-950/40">{diff.from}</span>
        <ArrowRight size={8} className="shrink-0 text-primary-950/30" />
        <span className="font-medium text-blue-700">{diff.to}</span>
      </div>
    );
  }
  if (diff.kind === 'info') {
    return (
      <div className="flex items-center gap-1 text-[10px]">
        <span className="text-primary-950/50">{diff.label}:</span>
        <span className="text-primary-950/70">{diff.to ?? diff.from}</span>
      </div>
    );
  }
  return <div className="text-[10px] text-primary-950/50">{diff.label}</div>;
}

type ZoneSnapshot = SiteZone | null;

function cloneZoneSnapshot(zone: SiteZone | null | undefined): ZoneSnapshot {
  return zone ? JSON.parse(JSON.stringify(zone)) as SiteZone : null;
}

function getRestoreTargetSnapshot(entry: ZoneHistoryEntry, restoredZone: SiteZone): ZoneSnapshot {
  return entry.action === 'create' ? null : cloneZoneSnapshot(restoredZone);
}

// ---------------------------------------------------------------------------
// Main panel
// ---------------------------------------------------------------------------

export function HistoryPanel({ projectId, siteZones, onClose }: HistoryPanelProps) {
  const [undoTargetId, setUndoTargetId] = useState<string>('');
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [isReverting, setIsReverting] = useState(false);
  const { history, total, isLoading, hasMore, loadMore } = useZoneHistory(projectId);
  const { selectZone } = useViewerStore();
  const zoneLabels = useZoneLabels(siteZones);
  const queryClient = useQueryClient();

  const selectedHistoryEntry = useMemo(
    () => history.find((entry) => entry.id === selectedHistoryId) ?? null,
    [history, selectedHistoryId]
  );
  const effectiveTargetId = selectedHistoryEntry?.zone_id || undoTargetId || null;

  // Client-side undo/redo
  const hasClientUndo = useUndoRedoStore(selectCanUndoForZone(effectiveTargetId));
  const hasClientRedo = useUndoRedoStore(selectCanRedoForZone(effectiveTargetId));
  const undoForZone = useUndoRedoStore((s) => s.undoForZone);
  const redoForZone = useUndoRedoStore((s) => s.redoForZone);
  const pushAction = useUndoRedoStore((s) => s.pushAction);
  const pushRedoAction = useUndoRedoStore((s) => s.pushRedoAction);
  const undoStack = useUndoRedoStore((s) => s.undoStack);
  const redoStack = useUndoRedoStore((s) => s.redoStack);

  // Server-side history fallback: selected entry first, otherwise latest entry for this zone
  const serverUndoEntry = useMemo(() => {
    if (selectedHistoryEntry) return selectedHistoryEntry;
    if (hasClientUndo || !effectiveTargetId) return null;
    return history.find((e) => e.zone_id === effectiveTargetId) ?? null;
  }, [history, effectiveTargetId, hasClientUndo, selectedHistoryEntry]);

  // Zones that have ANY history (client or server)
  const zonesWithHistory = useMemo(() => {
    const ids = new Set<string>();
    for (const e of history) ids.add(e.zone_id);
    for (const action of undoStack) {
      const zoneId = getUndoableActionZoneId(action);
      if (zoneId) ids.add(zoneId);
    }
    for (const action of redoStack) {
      const zoneId = getUndoableActionZoneId(action);
      if (zoneId) ids.add(zoneId);
    }
    return ids;
  }, [history, undoStack, redoStack]);

  const canUndo = !!selectedHistoryEntry || hasClientUndo || !!serverUndoEntry;
  const canRedo = !selectedHistoryEntry && hasClientRedo;

  const applyWorkingSnapshot = useCallback(async (zoneId: string, snapshot: ZoneSnapshot) => {
    await zoneHistoryApi.restoreSnapshot(projectId, zoneId, snapshot);
    queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
    queryClient.invalidateQueries({ queryKey: ['zone-history', projectId] });
  }, [projectId, queryClient]);

  const createSnapshotAction = useCallback((
    zoneId: string,
    undoSnapshot: ZoneSnapshot,
    redoSnapshot: ZoneSnapshot,
    label: string,
  ): UndoableAction => ({
    label,
    zoneId,
    undo: () => applyWorkingSnapshot(zoneId, undoSnapshot),
    redo: () => applyWorkingSnapshot(zoneId, redoSnapshot),
  }), [applyWorkingSnapshot]);

  const getCurrentSnapshot = useCallback((zoneId: string): ZoneSnapshot => {
    return cloneZoneSnapshot(siteZones.find((zone) => zone.id === zoneId));
  }, [siteZones]);

  const handleUndo = useCallback(async () => {
    if (isReverting) return;
    if (selectedHistoryEntry) {
      setIsReverting(true);
      try {
        const beforeSnapshot = getCurrentSnapshot(selectedHistoryEntry.zone_id);
        const restoredZone = await zoneHistoryApi.revert(selectedHistoryEntry.id);
        const targetSnapshot = getRestoreTargetSnapshot(selectedHistoryEntry, restoredZone);
        pushAction(createSnapshotAction(
          selectedHistoryEntry.zone_id,
          beforeSnapshot,
          targetSnapshot,
          'Restore version',
        ));
        queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
        queryClient.invalidateQueries({ queryKey: ['zone-history', projectId] });
        setUndoTargetId(selectedHistoryEntry.zone_id);
        setSelectedHistoryId(null);
        toast.success('Version restored');
      } catch {
        toast.error('Failed to restore selected version');
      } finally {
        setIsReverting(false);
      }
      return;
    }

    if (!effectiveTargetId) return;
    if (hasClientUndo) {
      await undoForZone(effectiveTargetId);
    } else if (serverUndoEntry) {
      setIsReverting(true);
      try {
        const beforeSnapshot = getCurrentSnapshot(serverUndoEntry.zone_id);
        const restoredZone = await zoneHistoryApi.revert(serverUndoEntry.id);
        const targetSnapshot = getRestoreTargetSnapshot(serverUndoEntry, restoredZone);
        pushRedoAction(createSnapshotAction(
          serverUndoEntry.zone_id,
          targetSnapshot,
          beforeSnapshot,
          'History undo',
        ));
        queryClient.invalidateQueries({ queryKey: ['site-zones', projectId] });
        queryClient.invalidateQueries({ queryKey: ['zone-history', projectId] });
        toast.success('Change undone');
      } catch {
        toast.error('Failed to undo');
      } finally {
        setIsReverting(false);
      }
    }
  }, [
    effectiveTargetId,
    hasClientUndo,
    serverUndoEntry,
    selectedHistoryEntry,
    undoForZone,
    pushAction,
    pushRedoAction,
    createSnapshotAction,
    getCurrentSnapshot,
    isReverting,
    queryClient,
    projectId,
  ]);

  const handleRedo = useCallback(async () => {
    if (!effectiveTargetId) return;
    if (hasClientRedo) await redoForZone(effectiveTargetId);
  }, [effectiveTargetId, hasClientRedo, redoForZone]);

  const getLabel = (entry: ZoneHistoryEntry): string => {
    if (zoneLabels[entry.zone_id]) return zoneLabels[entry.zone_id];
    const typeName = (entry.snapshot.zone_type ?? 'zone').replace(/_/g, ' ');
    return entry.snapshot.name || `${typeName.charAt(0).toUpperCase() + typeName.slice(1)} (deleted)`;
  };

  return (
    <div className="glass absolute right-4 top-16 z-20 flex w-80 flex-col rounded-xl shadow-2xl sm:max-h-[calc(100%-5rem)]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-primary-950/[0.08] px-3 py-2.5">
        <div className="flex items-center gap-2">
          <Clock size={14} className="text-primary-950/50" />
          <h3 className="text-xs font-semibold text-primary-950">Version History</h3>
          {total > 0 && (
            <span className="rounded-full bg-primary-950/[0.06] px-1.5 py-0.5 text-[10px] font-medium text-primary-950/50">
              {total}
            </span>
          )}
        </div>
        <button
          onClick={onClose}
          className="rounded-md p-1 text-primary-950/40 transition-colors hover:bg-primary-950/[0.06] hover:text-primary-950"
        >
          <X size={14} />
        </button>
      </div>

      {/* Undo / Redo controls with zone picker */}
      <div className="border-b border-primary-950/[0.06] px-3 py-2 space-y-1.5">
        <select
          value={undoTargetId}
          onChange={(e) => {
            setUndoTargetId(e.target.value);
            setSelectedHistoryId(null);
          }}
          className="w-full rounded-md border border-primary-950/10 bg-white px-2 py-1 text-[11px] text-primary-950 outline-none focus:border-blue-500/50"
        >
          <option value="">Pick a zone to undo/redo...</option>
          {siteZones.map((z) => {
            const label = zoneLabels[z.id] ?? z.zone_type.replace(/_/g, ' ');
            const has = zonesWithHistory.has(z.id);
            return (
              <option key={z.id} value={z.id}>
                {label}{has ? '' : ' (no changes)'}
              </option>
            );
          })}
        </select>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleUndo}
            disabled={!canUndo || isReverting}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-primary-950/10 bg-white px-2.5 py-1.5 text-[11px] font-medium text-primary-950/70 transition-colors hover:bg-primary-950/[0.04] hover:text-primary-950 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Undo2 size={12} />
            {isReverting ? 'Restoring...' : selectedHistoryEntry ? 'Restore' : 'Undo'}
          </button>
          <button
            onClick={handleRedo}
            disabled={!canRedo}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-primary-950/10 bg-white px-2.5 py-1.5 text-[11px] font-medium text-primary-950/70 transition-colors hover:bg-primary-950/[0.04] hover:text-primary-950 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Redo2 size={12} />
            Redo
          </button>
        </div>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 14rem)' }}>
        {isLoading ? (
          <div className="space-y-0 py-1">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-start gap-2.5 px-3 py-2.5 animate-pulse">
                <div className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full bg-primary-950/10" />
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-sm bg-primary-950/10" />
                    <div className="h-3 rounded bg-primary-950/10" style={{ width: `${60 + i * 15}px` }} />
                    <div className="h-3 w-12 rounded bg-primary-950/[0.06]" />
                  </div>
                  <div className="h-2.5 rounded bg-primary-950/[0.06]" style={{ width: `${90 + i * 10}px` }} />
                  <div className="h-2 w-16 rounded bg-primary-950/[0.04]" />
                </div>
              </div>
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="px-3 py-8 text-center text-xs text-primary-950/40">
            No changes recorded yet. Edit zones and changes will appear here automatically.
          </div>
        ) : (
          <div className="py-1">
            {history.map((entry) => (
              <HistoryEntry
                key={entry.id}
                entry={entry}
                zoneLabel={getLabel(entry)}
                selected={selectedHistoryId === entry.id}
                onLocate={(zoneId) => selectZone(zoneId)}
                onSelect={(selectedEntry) => {
                  setSelectedHistoryId(selectedEntry.id);
                  setUndoTargetId(selectedEntry.zone_id);
                }}
              />
            ))}
            {hasMore && (
              <button
                onClick={loadMore}
                className="flex w-full items-center justify-center gap-1 py-2.5 text-[11px] text-primary-950/40 transition-colors hover:text-primary-950"
              >
                <ChevronDown size={12} />
                Load more
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
