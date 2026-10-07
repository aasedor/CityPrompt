import { comfyTrialsApi } from './comfyTrials';
import { rendersApi } from './api';
import type { LocalImageModel } from '@/config/imageModels';
import type { SavedRender } from '@/types';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';

/** Capture is persisted before local submission. Recovery never submits again. */
export async function renderLocalImage(options: {
  projectId: string; model: LocalImageModel; imageBase64: string; prompt: string;
}): Promise<SavedRender> {
  if (!import.meta.env.DEV) throw new Error('Local image engines are available in the desktop development app.');
  const source = await rendersApi.save(options.projectId, {
    image_base64: options.imageBase64.replace(/^data:[^,]+,/, ''),
    prompt: 'Original 3D capture for local image rendering',
    style: 'Original 3D view', model: '3d-capture',
  });
  const key = `cityprompt.comfy.v1:${options.projectId}:${source.id}`;
  const history = await comfyTrialsApi.list(options.projectId);
  let job = history.jobs.find(j => j.source_render_id === source.id && !['complete', 'failed'].includes(j.status));
  if (job && job.preset !== options.model) throw new Error('A different local engine is still processing this view. Open Local model trials on the saved source to check it.');
  if (!job) {
    const requestId = readBrowserPreference(key) || crypto.randomUUID();
    writeBrowserPreference(key, requestId);
    job = await comfyTrialsApi.generate({ project_id: options.projectId, source_render_id: source.id,
      request_id: requestId, preset: options.model, prompt: options.prompt });
  }
  // High-quality local inference may offload to RAM; keep the original job
  // recoverable throughout a one-hour UI wait, without automatic resubmission.
  for (let checks = 0; checks < 720; checks++) {
    if (job.status === 'complete' && job.kind === 'image' && job.result && 'image_url' in job.result) {
      writeBrowserPreference(key, null);
      return job.result;
    }
    if (job.status === 'failed') {
      writeBrowserPreference(key, null);
      throw new Error(job.error || 'Local image generation failed.');
    }
    if (job.error) throw new Error(`${job.error} Open Local model trials on the saved source to recover this job.`);
    await new Promise(resolve => setTimeout(resolve, 5000));
    job = await comfyTrialsApi.recover(options.projectId, job.id);
  }
  throw new Error('Local image is still processing. Open Local model trials on the saved source to check the original job.');
}
