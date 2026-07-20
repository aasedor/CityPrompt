type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

const availabilityByUrl = new Map<string, Promise<boolean>>();

/**
 * Return false only for a definitive missing immutable model object.
 *
 * Other failures deliberately fall through to the GLTF loader: an older
 * backend may not support HEAD yet, and a transient network error must not
 * permanently hide a valid building.
 */
export function modelAssetAvailable(
  url: string,
  fetcher: FetchLike = globalThis.fetch,
): Promise<boolean> {
  if (!url) return Promise.resolve(false);
  const cached = availabilityByUrl.get(url);
  if (cached) return cached;

  const check = fetcher(url, {
    method: 'HEAD',
    cache: 'force-cache',
    credentials: 'same-origin',
  })
    .then((response) => response.status !== 404 && response.status !== 410)
    .catch(() => true);
  availabilityByUrl.set(url, check);
  return check;
}

export function clearModelAssetAvailabilityCacheForTests(): void {
  availabilityByUrl.clear();
}
