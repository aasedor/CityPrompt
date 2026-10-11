# Rework stopping rule for the fifteen clay buildings, 2026-10-11

The user lifted the three-version cap and asked for quality over speed, with no
endless loop. Each building on branch `claude/ten-new-buildings` stops at the first
of these:

1. **Pass.** An independent review returns PASS_ZERO_P0_P1. The building is done.
2. **No progress.** Two consecutive reviews fail to lower the combined P0 + P1
   count, or the same finding survives two targeted fix attempts. The building
   stops and its open findings go to the user.
3. **Hard cap.** Version v008 is the last version for any building, whatever its
   count.

Findings that are never chased by another version, but recorded for a human:

- **Reviewer disagreement.** A finding that contradicts an earlier reviewer's
  reading of the same locked sources, for example the chamfer drum.
- **Budget limits.** Detail that cannot fit the 1 MiB ordinary-blob GLB limit
  (about 18,500 triangles), which the Victorian station benchmark at about
  234,000 triangles does not face.

A building that stops under rule 2 or 3 ends VISUAL_REWORK_REQUIRED with its
findings in its README. Nothing here grants keeper approval.
