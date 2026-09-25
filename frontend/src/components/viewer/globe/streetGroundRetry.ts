/** Retry a failed measurement only after different, non-empty tile geometry
 * has settled. Two recoveries per authored route keep missing coverage bounded. */
export function createStreetGroundRetry(maxRetries = 2, stableMs = 900) {
  let retries = 0;
  let failed = new Set<unknown>();
  let candidate = new Set<unknown>();
  let stableSince = 0;
  const same = (a: Set<unknown>, b: Set<unknown>) => a.size === b.size && [...a].every(tile => b.has(tile));
  return {
    failed(visible: Iterable<unknown> = []) {
      failed = new Set(visible);
      candidate = new Set();
      stableSince = 0;
    },
    shouldRetry(visible: Iterable<unknown> | undefined, now: number) {
      const current = new Set(visible);
      if (retries >= maxRetries) return false;
      if (!current.size || same(current, failed)) { candidate = new Set(); return false; }
      if (!same(current, candidate)) { candidate = current; stableSince = now; return false; }
      if (now - stableSince < stableMs) return false;
      retries++;
      failed = current;
      return true;
    },
  };
}
