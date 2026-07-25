import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { buildingsApi } from '@/services/api';
import { useGenerationStore } from '@/store/generationStore';

const POLL_INTERVAL = 5000;

export function useGenerationPolling() {
  const queryClient = useQueryClient();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const poll = async () => {
      const { buildings, projectId, updateBuilding, markCompleted, markFailed } =
        useGenerationStore.getState();

      const active = Array.from(buildings.values()).filter((b) => b.status === 'generating');
      if (active.length === 0) {
        // Stop polling when nothing is generating
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        return;
      }

      for (const b of active) {
        try {
          const status = await buildingsApi.getGenerationStatus(b.buildingId);

          if (status.status === 'completed') {
            markCompleted(b.buildingId);
            if (projectId) {
              queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            }
          } else if (status.status === 'failed') {
            markFailed(b.buildingId);
            toast.error(`${b.buildingName} generation failed`);
          } else {
            const prevStep = b.step;
            updateBuilding(b.buildingId, status.progress ?? 0, status.step ?? '');
            // When preview model becomes available, refresh so 3D viewer shows it
            if (status.preview_model_url && prevStep !== 'preview_ready' && status.step === 'preview_ready' && projectId) {
              queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            }
            // Also refresh when refining starts (preview model is saved at that point)
            if (status.preview_model_url && prevStep !== 'refining' && status.step === 'refining' && projectId) {
              queryClient.invalidateQueries({ queryKey: ['project', projectId] });
            }
          }
        } catch {
          // Ignore individual polling errors
        }
      }
    };

    // Start/restart polling whenever store changes
    const unsub = useGenerationStore.subscribe((state) => {
      const hasActive = Array.from(state.buildings.values()).some((b) => b.status === 'generating');

      if (hasActive && !intervalRef.current) {
        // Do an immediate poll, then start interval
        poll();
        intervalRef.current = setInterval(poll, POLL_INTERVAL);
      } else if (!hasActive && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    });

    // Check on mount
    const hasActive = Array.from(useGenerationStore.getState().buildings.values()).some(
      (b) => b.status === 'generating',
    );
    if (hasActive) {
      poll();
      intervalRef.current = setInterval(poll, POLL_INTERVAL);
    }

    return () => {
      unsub();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [queryClient]);
}
