/** Exact request count for the current-view single-shot compare workflow.
 * Each preview is one image request. High-fidelity artistic rendering shares
 * one full-frame restyle across the entire A/B batch rather than paying for a
 * separate restyle per preview. */
export function estimateCurrentViewRenderCalls(
  previewCount: number,
  sharedHighFidelityRestyle: boolean,
): number {
  const normalizedPreviewCount = Number.isFinite(previewCount)
    ? Math.max(0, Math.trunc(previewCount))
    : 0;
  if (normalizedPreviewCount === 0) return 0;
  return normalizedPreviewCount + (sharedHighFidelityRestyle ? 1 : 0);
}
