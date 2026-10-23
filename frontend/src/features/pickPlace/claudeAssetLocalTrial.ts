import type { PlaceAsset } from './assetRegistry';
import trial from '@/data/claudeAssetLocalTrial.json';

/** A finite local review, never production activation or keeper approval. */
export function localClaudeAssets(enabled: boolean, includeRetired = false): PlaceAsset[] {
  return enabled ? trial.models.filter(row => includeRetired || !row.retired)
    .map(row => row.asset as unknown as PlaceAsset) : [];
}
export const LOCAL_CLAUDE_ASSETS = localClaudeAssets(import.meta.env.DEV);
/** Retired versions resolve saved scenes but cannot be newly selected. */
export const LOCAL_CLAUDE_SAVED_ASSETS = localClaudeAssets(import.meta.env.DEV, true);
