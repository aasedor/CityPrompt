import type { LegoGroundingIssue } from './buildingGroundContact';
import { buildingGroundProblemMessage } from './buildingGroundProblemMessage';

// Known optional access checks stay visible in Connections without vetoing a
// faithful capture. Unknown reasons remain hard failures.
const ACCESS_ADVISORIES=new Set([
  'entrance_anchor_not_at_edge','entrance_connection_required','entrance_approach_obstructed',
  'entrance_approach_too_short','entrance_landing_run_too_short','entrance_terrain_intersection',
  'entrance_height_invalid','entrance_clear_width_too_small','entrance_ground_unavailable',
]);

export function isBuildingAccessAdvisory(reason: string) { return ACCESS_ADVISORIES.has(reason); }

export function buildingCaptureIssues(issues: readonly LegoGroundingIssue[]) {
  return issues.filter(issue=>!isBuildingAccessAdvisory(issue.reason));
}

export function buildingCaptureProblem(pending: readonly string[], issues: readonly LegoGroundingIssue[]): string | null {
  const blockers=buildingCaptureIssues(issues);
  if (!pending.length && !blockers.length) return null;
  if (blockers.some(issue=>issue.reason==='foundation_exceeds_3m'))
    return 'The site is too uneven beneath a building for automatic grounding. Choose a flatter placement before rendering.';
  const repair=blockers.find(issue=>issue.reason.startsWith('entrance_') || issue.reason==='review_model_revision_unavailable');
  return repair ? buildingGroundProblemMessage(repair.reason)
    : `These buildings are not ready at ground level: ${pending.join(', ') || 'check the marked building'}. Check their placement before rendering.`;
}
