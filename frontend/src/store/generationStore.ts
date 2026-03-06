import { create } from 'zustand';
import { buildingsApi } from '@/services/api';

interface BuildingGenState {
  buildingId: string;
  buildingName: string;
  status: 'generating' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  step: string; // e.g. "calling_meshy", "polling", "refining"
}

interface GenerationState {
  projectId: string | null;
  buildings: Map<string, BuildingGenState>;
  startedAt: number | null;
  cancelling: boolean;
  // Actions
  startBatch: (projectId: string, buildings: { id: string; name: string }[]) => void;
  updateBuilding: (id: string, progress: number, step: string) => void;
  markCompleted: (id: string) => void;
  markFailed: (id: string) => void;
  cancelAll: () => Promise<void>;
  clearAll: () => void;
  // Derived
  isActive: () => boolean;
  activeCount: () => number;
  completedCount: () => number;
  totalCount: () => number;
  overallProgress: () => number;
}

export const useGenerationStore = create<GenerationState>((set, get) => ({
  projectId: null,
  buildings: new Map(),
  startedAt: null,
  cancelling: false,

  startBatch: (projectId, buildings) => {
    const map = new Map(get().buildings);
    for (const b of buildings) {
      if (!map.has(b.id)) {
        map.set(b.id, {
          buildingId: b.id,
          buildingName: b.name,
          status: 'generating',
          progress: 0,
          step: '',
        });
      }
    }
    set({
      projectId,
      buildings: map,
      startedAt: get().startedAt ?? Date.now(),
    });
  },

  updateBuilding: (id, progress, step) => {
    const map = new Map(get().buildings);
    const entry = map.get(id);
    if (entry && entry.status === 'generating') {
      map.set(id, { ...entry, progress, step });
      set({ buildings: map });
    }
  },

  markCompleted: (id) => {
    const map = new Map(get().buildings);
    const entry = map.get(id);
    if (entry) {
      map.set(id, { ...entry, status: 'completed', progress: 100, step: '' });
      set({ buildings: map });
      // Auto-clear when all done
      const allDone = Array.from(map.values()).every((b) => b.status !== 'generating');
      if (allDone) {
        setTimeout(() => {
          // Only clear if still no generating buildings
          if (Array.from(get().buildings.values()).every((b) => b.status !== 'generating')) {
            set({ buildings: new Map(), projectId: null, startedAt: null });
          }
        }, 5000);
      }
    }
  },

  markFailed: (id) => {
    const map = new Map(get().buildings);
    const entry = map.get(id);
    if (entry) {
      map.set(id, { ...entry, status: 'failed', step: '' });
      set({ buildings: map });
    }
  },

  cancelAll: async () => {
    set({ cancelling: true });
    const generatingIds = Array.from(get().buildings.values())
      .filter((b) => b.status === 'generating')
      .map((b) => b.buildingId);

    if (generatingIds.length > 0) {
      try {
        await buildingsApi.batchCancelGeneration(generatingIds);
      } catch {
        // Best effort — even if API fails, clear local state
      }
    }

    // Mark all generating buildings as cancelled
    const map = new Map(get().buildings);
    for (const [id, entry] of map) {
      if (entry.status === 'generating') {
        map.set(id, { ...entry, status: 'cancelled', step: '' });
      }
    }
    set({ buildings: map, cancelling: false, startedAt: null });
  },

  clearAll: () => set({ buildings: new Map(), projectId: null, startedAt: null, cancelling: false }),

  isActive: () => Array.from(get().buildings.values()).some((b) => b.status === 'generating'),
  activeCount: () => Array.from(get().buildings.values()).filter((b) => b.status === 'generating').length,
  completedCount: () => Array.from(get().buildings.values()).filter((b) => b.status === 'completed').length,
  totalCount: () => get().buildings.size,
  overallProgress: () => {
    const all = Array.from(get().buildings.values());
    if (all.length === 0) return 0;
    return Math.round(all.reduce((sum, b) => sum + b.progress, 0) / all.length);
  },
}));
