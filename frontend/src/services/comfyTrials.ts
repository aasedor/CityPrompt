import { api } from './api';
import type { SavedRender } from '@/types';
import type { VideoAttempt } from '@/components/viewer/VideoGeneratePanel';

export interface ComfyPreset {
  id: string; label: string; kind: 'image' | 'video'; available: boolean;
  message: string; default_prompt: string; max_edge: number; steps: number;
  duration_seconds: number | null;
}
export interface ComfyJob {
  id: string; request_id: string; source_render_id: string; preset: string;
  kind: 'image' | 'video'; status: string; prompt: string; created_at: string;
  generation_settings: { width: number; height: number; steps: number; seed: number };
  error: string | null; result: SavedRender | VideoAttempt | null;
}
export const comfyTrialsApi = {
  presets: async (): Promise<{ presets: ComfyPreset[]; credit_cost: number }> =>
    (await api.get('/api/v1/local-render/presets')).data,
  list: async (projectId: string): Promise<{ jobs: ComfyJob[] }> =>
    (await api.get(`/api/v1/local-render/projects/${projectId}/jobs`)).data,
  generate: async (request: { project_id: string; source_render_id: string; request_id: string; preset: string; prompt: string }): Promise<ComfyJob> =>
    (await api.post('/api/v1/local-render/jobs', request, { timeout: 60_000 })).data,
  recover: async (projectId: string, jobId: string): Promise<ComfyJob> =>
    (await api.post(`/api/v1/local-render/projects/${projectId}/jobs/${jobId}/recover`, {}, { timeout: 120_000 })).data,
  resolveMissing: async (projectId: string, jobId: string): Promise<ComfyJob> =>
    (await api.post(`/api/v1/local-render/projects/${projectId}/jobs/${jobId}/resolve-missing`)).data,
};
