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
const localTrialEnabled = isLocalClaudeTrialEnvironment(import.meta.env.DEV, import.meta.env.MODE);
export const LOCAL_CLAUDE_ASSETS = localClaudeAssets(localTrialEnabled);
/** Retired versions resolve saved scenes but cannot be newly selected. */
export const LOCAL_CLAUDE_SAVED_ASSETS = localClaudeAssets(localTrialEnabled, true);
