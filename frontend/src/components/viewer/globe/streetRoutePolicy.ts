import policy from '@/data/streetRoutePolicy.json';
import { modularBridgeProgramFor } from './modularBridgeProgram';

/** Authoring envelope is separate from the immutable source study and its hash.
 * Repeat native modules; never stretch the complete bridge's structural span. */
export const MAX_REPEATABLE_STREET_LENGTH_M = policy.maxRepeatableLengthM;
export function nativeStreetMaxLength(variantId: string): number {
  return modularBridgeProgramFor(variantId)?.maxLengthM
    ?? (policy.fixedSpanMaxLengthM as Record<string, number>)[variantId] ?? MAX_REPEATABLE_STREET_LENGTH_M;
}
