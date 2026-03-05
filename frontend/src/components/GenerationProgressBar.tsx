import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, X, CheckCircle2 } from 'lucide-react';
import { useGenerationStore } from '@/store/generationStore';

const STEP_LABELS: Record<string, string> = {
  calling_meshy: 'Initializing AI...',
  calling_tripo: 'Initializing AI...',
  polling: 'Generating 3D preview...',
  polling_tripo: 'Generating 3D preview...',
  refining: 'Refining textures...',
  smart_low_poly: 'Optimizing mesh...',
  downloading: 'Downloading model...',
  uploading: 'Uploading to storage...',
  updating: 'Finalizing...',
};

function getStepLabel(step: string): string {
  if (!step) return 'Processing...';
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

  if (!isActive || dismissed) return null;

  // Find the "most representative" step — the one from the first still-generating building
  const activeBuildings = Array.from(store.buildings.values()).filter(
    (b) => b.status === 'generating',
  );
  const currentStep = activeBuildings[0]?.step || '';

  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;

  return (
    <div
      onClick={() => {
        if (projectId) navigate(`/projects/${projectId}/viewer`);
      }}
      className="fixed bottom-4 right-4 z-50 flex cursor-pointer items-center gap-3 rounded-xl bg-primary-950/90 px-4 py-3 shadow-2xl backdrop-blur-xl transition-all hover:bg-primary-950"
      style={{ minWidth: 280 }}
    >
      {/* Spinner or check */}
      {activeCount > 0 ? (
        <Loader2 size={18} className="shrink-0 animate-spin text-purple-400" />
      ) : (
        <CheckCircle2 size={18} className="shrink-0 text-emerald-400" />
      )}

      {/* Text content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 text-sm font-medium text-white">
          <span className="truncate">{getStepLabel(currentStep)}</span>
          <span className="shrink-0 tabular-nums text-xs text-purple-300">
            {minutes}:{seconds.toString().padStart(2, '0')}
          </span>
        </div>
        <div className="mt-1 flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-purple-500 transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
          <span className="shrink-0 text-xs tabular-nums text-neutral-400">
            {completedCount}/{totalCount}
          </span>
        </div>
      </div>

      {/* Dismiss */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          setDismissed(true);
        }}
        className="shrink-0 rounded-md p-1 text-neutral-500 hover:bg-white/10 hover:text-white"
      >
        <X size={14} />
      </button>
    </div>
  );
}
