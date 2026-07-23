/**
 * Deterministic PRNG utilities — stable scatter layouts across re-renders
 * and sessions. Seed with a stable string (e.g. zone.id); intentionally NOT
 * salted with updated_at, so editing one vertex doesn't reshuffle a whole
 * park.
 */

/** FNV-1a 32-bit string hash. */
export function fnv1aHash(str: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** mulberry32 — fast, well-distributed 32-bit PRNG. Returns () => [0,1). */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Convenience: seeded RNG straight from a string. */
export function seededRandom(seed: string): () => number {
  return mulberry32(fnv1aHash(seed));
}
