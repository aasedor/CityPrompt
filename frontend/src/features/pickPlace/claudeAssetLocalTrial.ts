import type { PlaceAsset } from './assetRegistry';
import trial from '@/data/claudeAssetLocalTrial.json';

/** A finite local review, never production activation or keeper approval. */
export function localClaudeAssets(enabled: boolean, includeRetired = false): PlaceAsset[] {
  return enabled ? trial.models.filter(row => includeRetired || !row.retired)
    .map(row => row.asset as unknown as PlaceAsset) : [];
}
export function isLocalClaudeTrialEnvironment(isDev: boolean, mode: string): boolean {
  return isDev && mode === 'development';
}
// Keep the build-time condition visible to tree shaking: calling a helper with
// false still retains the trial JSON through its filter/map implementation.
export const LOCAL_CLAUDE_ASSETS = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localClaudeAssets(true) : [];
/** Retired versions resolve saved scenes but cannot be newly selected. */
export const LOCAL_CLAUDE_SAVED_ASSETS = import.meta.env.DEV && import.meta.env.MODE === 'development'
  ? localClaudeAssets(true, true) : [];
