import type { AxiosInstance } from 'axios';

const ROOT = '/api/v1/render/direct-3d-attempts';
export interface ImageAttempt {
  id: string; project_id: string; idempotency_key: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'unknown';
  model: string; style: string; created_at: string; finished_at: string | null;
  error: { message: string; billed?: boolean } | null;
}
export interface RecoveredImage<T> {
  response: T; source_image_base64: string; style: string;
  fidelity_policy: 'precise' | 'balanced' | 'expressive'; attempt: ImageAttempt;
}
type Pending = { key: string; attemptId?: string };

/** Store identity only. The server retains the original image/control bytes. */
export function createDirect3DAttemptClient(options: {
  api: AxiosInstance; storage: () => Storage; account: () => string | null;
  wait?: (milliseconds: number) => Promise<void>; now?: () => number;
}) {
  const { api } = options;
  const now = options.now ?? Date.now;
  const wait = options.wait ?? (milliseconds => new Promise(resolve => window.setTimeout(resolve, milliseconds)));
  const identity = (projectId: string) => {
    const userId = options.account();
    if (!userId) throw new Error('Sign in again to recover or generate an image.');
    return `cityprompt:image-attempt:${userId}:${projectId}`;
  };
  const clear = (projectId: string, key: string) => {
    const name = identity(projectId);
    const current = JSON.parse(options.storage().getItem(name) ?? 'null') as Pending | null;
    if (current?.key === key) options.storage().removeItem(name);
  };
  const capabilities = async () => (await api.get<{ enabled: boolean; images_enabled: boolean; classroom_release?: boolean; video_enabled?: boolean }>(`${ROOT}/capabilities`)).data;
  const list = async (projectId: string) => (await api.get<ImageAttempt[]>(ROOT, { params: { project_id: projectId } })).data;
  const recover = async <T>(attempt: ImageAttempt): Promise<RecoveredImage<T>> => {
    const expected = options.account();
    const { data } = await api.get<RecoveredImage<T>>(`${ROOT}/${attempt.id}/result`, { timeout: 120_000 });
    if (options.account() !== expected) throw new Error('The signed-in account changed. Open the image again after signing in.');
    clear(attempt.project_id, attempt.idempotency_key);
    return data;
  };
  const generate = async <T>(request: { project_id: string }): Promise<T> => {
    const mode = await capabilities();
    if (!mode.images_enabled) throw new Error('AI images are paused. You can still download your exact 3D view.');
    if (!mode.enabled) {
      // Explicit compatibility for deployments without migration/worker 030.
      // An unavailable capability endpoint never falls back to a paid route.
      return (await api.post<T>('/api/v1/render/generate-direct-3d', request, { timeout: 420_000 })).data;
    }
    const name = identity(request.project_id);
    const stored = options.storage();
    const pending = JSON.parse(stored.getItem(name) ?? 'null') as Pending | null;
    if (pending?.attemptId) throw new Error('An image attempt is saved. Open “Recover recent images” before generating another.');
    const key = pending?.key ?? crypto.randomUUID();
    // On an ambiguous submission, reuse this key on the next explicit click.
    // A changed capture conflicts if the original reached the server; it can
    // never create a second attempt with the same key.
    stored.setItem(name, JSON.stringify({ key }));
    let attempt: ImageAttempt;
    try {
      attempt = (await api.post<ImageAttempt>(ROOT, request, { headers: { 'Idempotency-Key': key }, timeout: 120_000 })).data;
    } catch (error) {
      const status = (error as { response?: { status?: number } }).response?.status;
      if (status && status >= 400 && status < 500 && status !== 409) clear(request.project_id, key);
      throw error;
    }
    stored.setItem(name, JSON.stringify({ key, attemptId: attempt.id }));
    const deadline = now() + 420_000;
    while (attempt.status === 'queued' || attempt.status === 'running') {
      if (identity(request.project_id) !== name) throw new Error('Sign in again to recover the saved image.');
      if (now() >= deadline) throw new Error('Your image attempt is saved and may still be running. Use “Recover recent images” to check it; no new image is requested.');
      await wait(2000);
      try { attempt = (await api.get<ImageAttempt>(`${ROOT}/${attempt.id}`)).data; }
      catch { throw new Error('The connection stopped, but your image attempt is saved. Use “Recover recent images” after reconnecting.'); }
    }
    if (identity(request.project_id) !== name) throw new Error('Sign in again to recover the saved image.');
    if (attempt.status === 'completed') return (await recover<T>(attempt)).response;
    clear(request.project_id, key);
    throw new Error(attempt.error?.message ?? 'The image did not finish. This attempt will not retry automatically.');
  };
  return { capabilities, list, recover, generate, acknowledge: (attempt: ImageAttempt) => {
    if (attempt.status === 'failed' || attempt.status === 'unknown') clear(attempt.project_id, attempt.idempotency_key);
  } };
}
