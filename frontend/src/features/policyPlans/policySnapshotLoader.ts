import type { PolicySnapshot } from './rileyPolicy';

/** JSON assets stay lazy and cacheable, while a failed request remains retryable.
 * Browsers permanently cache rejected dynamic module imports for the page. */
export async function loadPolicySnapshot(url: URL): Promise<PolicySnapshot> {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Policy map unavailable');
  const data = await response.json() as PolicySnapshot;
  if (!data || typeof data.snapshot !== 'string' || !Array.isArray(data.features)
    || !Array.isArray(data.bounds) || !data.boundary?.coordinates) {
    throw new Error('Invalid policy map');
  }
  return data;
}
