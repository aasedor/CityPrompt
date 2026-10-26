import { describe,expect,it } from 'vitest';
import { buildingCaptureProblem, buildingCaptureIssues } from './buildingCaptureReadiness';

describe('building capture integrity versus optional access review',()=>{
  it.each(['entrance_anchor_not_at_edge','entrance_connection_required','entrance_approach_obstructed',
    'entrance_approach_too_short','entrance_landing_run_too_short','entrance_terrain_intersection',
    'entrance_height_invalid','entrance_clear_width_too_small','entrance_ground_unavailable'])('permits rendering while keeping %s in the review inventory',reason=>{
    const issues=[{buildingId:'house',reason}],before=JSON.stringify(issues);
    expect(buildingCaptureIssues(issues)).toEqual([]);
    expect(buildingCaptureProblem([],issues)).toBeNull();
    expect(JSON.stringify(issues)).toBe(before);
  });
  it.each(['review_model_revision_unavailable','incomplete_footprint_ground','foundation_exceeds_3m',
    'ground_not_ready','entrance_unknown_integrity_failure','unknown_failure'])('preserves the hard capture failure %s',reason=>{
    const issues=[{buildingId:'house',reason},{buildingId:'house',reason:'entrance_anchor_not_at_edge'}];
    expect(buildingCaptureIssues(issues)).toEqual([{buildingId:'house',reason}]);
    expect(buildingCaptureProblem([],issues)).toBeTruthy();
  });
  it('keeps missing or still-loading models blocking even when entrance review is only advisory',()=>{
    expect(buildingCaptureProblem(['Hill house'],[{buildingId:'house',reason:'entrance_anchor_not_at_edge'}])).toContain('Hill house');
  });
});
