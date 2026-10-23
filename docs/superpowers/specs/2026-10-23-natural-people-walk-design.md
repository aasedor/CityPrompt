# Natural people walking — local correction

User request: people walk robotically. Preserve existing models, actions, saved placements and editing performance. Test locally; no paid generations or publication.

Evidence: current Walk raises ankle centres by 24–30 cm through a cycle; the source Formal walk uses the same leg motion. Source body sway and opposite arm swing are already present. Capture offsets use the array index within each model batch, so different models' first actors are synchronized; reordering changes phase.

Approaches: swapping Formal cannot address the legs. Replacing/retargeting all source assets would enlarge the scope and invalidate approved model hashes. A bounded runtime correction retains immutable GLBs: reduce only excess swing-foot height with a two-bone leg solve, preserve foot orientation and source contact poses, and derive pace/phase from stable placement identity. This is the selected implementation judgement for the authorized bug fix.

Constraints: walk only; running retains its disclosed sped-up Walk approximation. No per-frame editing loop, pathfinding, collision avoidance, new dependencies, morphs, random state, scene serialization change, paid AI trial or promises of photoreal motion. Preserve absolute-time seeks, capture restore, ECEF-local skinning, source geometry/material sharing and actor-owned pose state. Verify actual skinned feet across all 23 models; reject the correction if it causes penetration, unstable joints or visible discontinuities.

Acceptance: deterministic independent actors; stable motion after reorder/reload; gait cycle and translation use the same speed; correct local/ECEF transformations; reasonable swing clearance with original stance contact retained; browser side-by-side sample/recording and all-model checks. Naturalness remains a visual judgement, not established by a passing unit test. AI output has not been re-tested by this change.
