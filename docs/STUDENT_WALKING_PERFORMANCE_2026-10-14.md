# Student walking performance — local quality-preserving pass

Status: local pilot on `codex/student-walking-performance`, based on
`d32558d54`. Not deployed or pushed. The separate terrain-contact experiment
remains deferred on `codex/terrain-placement-pilot`.

## Changes

- Ordinary architectural meshes with valid, finite bounds can now use camera
  frustum culling instead of disabling it for every imported object. Meshes
  outside the camera are skipped; visible geometry is not simplified.
- Explicit source no-cull flags, instancing, skinning, morph targets, custom
  shaders and displacement maps retain conservative drawing. Bias-only
  displacement is also excluded.
- Native PBR clones retain source material sharing within one placed model.
  Each placement still owns separate mutable materials. Legacy glazing retains
  per-mesh materials because its near/far pairing depends on mesh context.
- Shared owned materials are disposed once; cached geometry/textures are not
  disposed by this path.

No geometry, texture resolution, glass response, shadows, global scale,
working-view resolution, catalogue metadata or source assets changed.

## Measured local browser comparison

Edge on this desktop, Balanced, foreground tab, 1420 × 1151 screen buffer.
Project `6ecad402-d416-4400-a708-d453e34c193d` contains five native Claude
buildings and decorative trees. Focus plan, enter Walk, click `[760,850]`.
The same walking starting view was used before and after.

| Measurement | Baseline | Final |
| --- | ---: | ---: |
| Draw calls | 681 | 671 |
| Triangles submitted | 1,894,156 | 1,890,780 |
| Monitor frame rate | 57 fps | 57 fps |
| Monitor frame interval | 18 ms | 18 ms |

This is a **small reduction in drawing work, not a demonstrated FPS gain**.
Large joined meshes spanning the camera retain conservative whole-mesh bounds.
The five tested GLBs each have one unique material per mesh, so this scene
does not exercise material-sharing savings. The sharing/isolation/disposal
regression tests cover repeated source references; no runtime-memory saving
has been measured or claimed.

The culling-only screenshot's building region `[270,180,1420,730]` was
pixel-identical to baseline. Final combined changes produced mean absolute
RGB difference 0.0000411/255 in that region (a tiny 8 × 8 difference extent),
with no visible building change. Full screenshots are retained for review.

An initial turn trace concentrated CPU samples in renderer program/material
setup. Its camera route was not identical to the final comparison, so it is
diagnostic evidence only, not an FPS benchmark. Background-tab readings around
1 fps were discarded as browser throttling, not application performance.

## Verification

- Narrow Vitest: 6 files, 100 tests passed (material preparation, native
  placement, direct 3D capture, walking, inspection and measured doors).
- `npm run type-check`: passed.
- `git diff --check`: passed.
- Browser: walking entry, turning and movement, model visibility and free
  deterministic street-view preview succeeded. Captured browser error log: empty.
- Independent code review: no remaining P0/P1/P2 findings. Review caught the
  displacement-bias exception; a witnessed red/green regression test covers it.
- No paid image/video calls; account remained at 628 application tokens.

Evidence stays outside Git at
`D:/CityPrompt-student-performance-2026-10-14/`: baseline/final monitor text and
screenshots, walking views, final turned view, free street capture and diagnostic
traces. No generated binaries are part of this commit.

## Limits and follow-up

Student-laptop performance, long-session GPU memory and multi-device frame-time
percentiles remain untested. These results do not certify laptop suitability or
all catalogue models. Paid AI output and video output were not regenerated;
the deterministic input capture and its regression tests passed.

Keep further work evidence-led: repeat this project on the affected laptop,
measure sustained walking/turning, then target the largest measured cost.
Do not silently simplify authored buildings or lower final render quality.
