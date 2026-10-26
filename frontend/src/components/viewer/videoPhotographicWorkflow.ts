import type {createDirect3DAttemptClient} from '@/services/direct3DAttempts';
import type {PhotographicGuide,PhotographicGuideRequest} from './PhotographicVideoGuide';

// Private evidence is canonical JSON; key insertion order is not source identity.
const canonicalJson = (value:unknown) => JSON.stringify(value, (_key, item:unknown) =>
  item && typeof item === 'object' && !Array.isArray(item)
    ? Object.fromEntries(Object.entries(item).sort(([left],[right]) => left < right ? -1 : left > right ? 1 : 0))
    : item);
/** Called only by an explicit paid Generate action. Failed lookups stop spend. */
export async function preparePhotographicVideo(client:ReturnType<typeof createDirect3DAttemptClient>,request:PhotographicGuideRequest,sceneSha:string):Promise<Omit<PhotographicGuide,'signature'>> {
  const attempts = await client.list(request.project_id, 'video_appearance');
  for (const attempt of attempts) {
    if (!['completed','queued','running'].includes(attempt.status)) continue;
    const saved = attempt.status === 'completed'
      ? await client.recover<Omit<PhotographicGuide,'signature'>>(attempt)
      : await client.resume<Omit<PhotographicGuide,'signature'>>(attempt);
    if (saved.response.source_video_sha256 === request.source_video_sha256
      && saved.response.scene_revision_sha256 === sceneSha
      && canonicalJson(saved.source_request) === canonicalJson(request.source_request)) return saved.response;
  }
  return client.generate<Omit<PhotographicGuide,'signature'>>(request);
}
