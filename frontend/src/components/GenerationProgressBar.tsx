import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, X, CheckCircle2, Wand2, Square, Ban } from 'lucide-react';
import { useGenerationStore } from '@/store/generationStore';

const STEP_LABELS: Record<string, string> = {
  calling_meshy: 'Initializing AI...',
  calling_tripo: 'Initializing AI...',
  polling: 'Generating 3D model...',
  polling_tripo: 'Generating 3D model...',
  refining: 'Refining textures...',
  smart_low_poly: 'Optimizing mesh...',
  downloading: 'Downloading model...',
  uploading: 'Uploading to storage...',
  updating: 'Finalizing...',
};

function getStepLabel(step: string): string {
  if (!step) return 'Queued...';
  return STEP_LABELS[step] || 'Processing...';
}

export function GenerationProgressBar() {
  const navigate = useNavigate();
  const [dismissed, setDismissed] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const store = useGenerationStore();
  const isActive = store.isActive();
  const activeCount = store.activeCount();
  const completedCount = store.completedCount();
  const totalCount = store.totalCount();
  const overallProgress = store.overallProgress();
  const projectId = store.projectId;
  const startedAt = store.startedAt;
  const cancelling = store.cancelling;

  const handleStop = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    await store.cancelAll();
  }, [store]);

  // Reset dismissed state when a new batch starts
  useEffect(() => {
    if (isActive) setDismissed(false);
  }, [isActive]);

  // Elapsed time ticker
  useEffect(() => {
    if (!startedAt) {
      setElapsedSeconds(0);
      return;
    }
    setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    const tick = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => clearInterval(tick);
  }, [startedAt]);

  const allBuildings = Array.from(store.buildings.values());
  const hasCancelled = allBuildings.some((b) => b.status === 'cancelled');

  // Auto-dismiss after cancellation
  useEffect(() => {
    if (hasCancelled && !isActive) {
      const timer = setTimeout(() => setDismissed(true), 3000);
      return () => clearTimeout(timer);
    }
  }, [hasCancelled, isActive]);

  if ((!isActive && !hasCancelled) || dismissed) return null;
  if (allBuildings.length === 0) return null;

  const currentStep = allBuildings.find((b) => b.status === 'generating')?.step || '';

  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 flex justify-center pointer-events-none">
      <div
        onClick={() => {
          if (projectId) navigate(`/projects/${projectId}/viewer`);
        }}
        className="pointer-events-auto mb-6 w-full max-w-lg cursor-pointer rounded-2xl border border-purple-500/30 bg-primary-950/95 shadow-[0_0_60px_-12px_rgba(139,92,246,0.4)] backdrop-blur-2xl transition-all hover:shadow-[0_0_80px_-12px_rgba(139,92,246,0.5)]"
      >
        {/* Animated gradient top bar */}
        <div className="h-1 w-full overflow-hidden rounded-t-2xl bg-white/5">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-700"
            style={{ width: `${Math.max(overallProgress, 3)}%` }}
          />
        </div>

        <div className="p-5">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 ring-1 ring-purple-500/30">
                <Wand2 size={20} className="text-purple-400 animate-pulse" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">
                  {hasCancelled && !isActive ? 'Generation Stopped' : 'Generating 3D Models'}
                </h3>
                <p className="text-xs text-purple-300">
                  {hasCancelled && !isActive ? `${completedCount} of ${totalCount} completed` : getStepLabel(currentStep)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="tabular-nums text-sm font-medium text-purple-300">
                {minutes}:{seconds.toString().padStart(2, '0')}
              </span>
              <button
                onClick={handleStop}
                disabled={cancelling}
                className="flex items-center gap-1.5 rounded-lg bg-red-500/15 px-2.5 py-1.5 text-xs font-medium text-red-300 ring-1 ring-red-500/30 hover:bg-red-500/25 hover:text-red-200 disabled:opacity-50 transition-colors"
                title="Stop all generation"
              >
                <Square size={10} fill="currentColor" />
                {cancelling ? 'Stopping...' : 'Stop'}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setDismissed(true);
                }}
                className="rounded-lg p-1.5 text-neutral-500 hover:bg-white/10 hover:text-white"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mb-3 flex items-center gap-3">
            <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-white/[0.08]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-700 ease-out"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
            <span className="shrink-0 text-sm font-semibold tabular-nums text-white">
              {completedCount}/{totalCount}
            </span>
          </div>

          {/* Building list */}
          {allBuildings.length > 0 && allBuildings.length <= 12 && (
            <div className="grid grid-cols-2 gap-1.5 max-h-32 overflow-y-auto">
              {allBuildings.map((b) => (
                <div
                  key={b.buildingId}
                  className={`flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs ${
                    b.status === 'completed'
                      ? 'bg-emerald-500/10 text-emerald-300'
                      : b.status === 'failed'
                      ? 'bg-red-500/10 text-red-300'
                      : b.status === 'cancelled'
                      ? 'bg-amber-500/10 text-amber-300'
                      : 'bg-white/[0.04] text-neutral-300'
                  }`}
                >
                  {b.status === 'completed' ? (
                    <CheckCircle2 size={12} className="shrink-0 text-emerald-400" />
                  ) : b.status === 'failed' ? (
                    <X size={12} className="shrink-0 text-red-400" />
                  ) : b.status === 'cancelled' ? (
                    <Ban size={12} className="shrink-0 text-amber-400" />
                  ) : (
                    <Loader2 size={12} className="shrink-0 animate-spin text-purple-400" />
                  )}
                  <span className="truncate">{b.buildingName}</span>
                </div>
              ))}
            </div>
          )}
          {allBuildings.length > 12 && (
            <p className="text-xs text-neutral-400 text-center">
              {activeCount} generating, {completedCount} completed of {totalCount} total
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
