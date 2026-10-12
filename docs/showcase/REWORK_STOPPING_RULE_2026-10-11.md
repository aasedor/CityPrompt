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

## Limit lifted, 2026-10-12

The user lifted the GLB size limit. The candidate cap in `tools/clay_evidence_preserve.py`
rises from 1 MiB to 4 MiB per GLB, still as an ordinary git blob (about 75,000 triangles,
four times the previous budget). Git LFS was tried first: the LFS batch negotiation and the
storage upload both succeed from the build host, but the final verify call to
`lfs.github.com` is refused by the environment's network policy, so an LFS push fails. If
that host is added to the environment's allowed domains, `tools/clay_*/candidates/*.glb`
can move to LFS with a 16 MiB cap, which is Victorian-station scale. The "Budget limits"
exemption above no longer applies at the 4 MiB cap except for detail that needs more
than about 75,000 triangles.

Consequences for the rule:

- The four buildings that passed stay as they are unless the user asks for a detail pass.
- The eleven that stopped or reached the cap are reopened. Because the constraint that
  shaped their stops has changed, each one's rule-2 counter resets, and the hard cap for
  the reopened run is two further versions per building.
- Renders and boards stay JPEGs under 950 KB in `evidence/`; only the candidate GLB
  grows. Nothing here grants keeper approval.
