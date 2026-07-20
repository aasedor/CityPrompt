export interface RenderLabelCandidate {
  id: string;
  groupKey: string;
  priority: number;
  area: number;
}

function compareCandidates(left: RenderLabelCandidate, right: RenderLabelCandidate): number {
  return right.priority - left.priority
    || right.area - left.area
    || left.groupKey.localeCompare(right.groupKey)
    || left.id.localeCompare(right.id);
}

/**
 * Select a deterministic, bounded set of zone labels for a render capture.
 * Every visible polygon still receives its border and remains in the mask; this
 * budget only prevents district-scale text from obscuring the source image.
 * One representative from each program group is selected before spare label
 * slots are filled with the remaining highest-priority zones.
 */
export function selectRenderLabelIds(
  candidates: RenderLabelCandidate[],
  limit = 80,
): Set<string> {
  const safeLimit = Number.isFinite(limit) ? Math.max(0, Math.floor(limit)) : 0;
  if (safeLimit === 0 || candidates.length === 0) return new Set();

  const ranked = candidates
    .filter(candidate => Boolean(candidate.id))
    .sort(compareCandidates);
  if (ranked.length <= safeLimit) return new Set(ranked.map(candidate => candidate.id));

  const representatives: RenderLabelCandidate[] = [];
  const representedGroups = new Set<string>();
  for (const candidate of ranked) {
    if (representedGroups.has(candidate.groupKey)) continue;
    representedGroups.add(candidate.groupKey);
    representatives.push(candidate);
  }

  const selected = new Set(
    representatives
      .sort(compareCandidates)
      .slice(0, safeLimit)
      .map(candidate => candidate.id),
  );
  if (selected.size >= safeLimit) return selected;

  for (const candidate of ranked) {
    if (selected.has(candidate.id)) continue;
    selected.add(candidate.id);
    if (selected.size >= safeLimit) break;
  }
  return selected;
}
