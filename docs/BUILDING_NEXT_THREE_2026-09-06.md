# Three more architectural-clay buildings

Three exact catalogue variants passed independent RLASM 6.1 clay review and
local student trials. They are available in the default building picker. The
promotion manifest owns their model hashes, measured envelopes, approval and
trial records; the JSON beside this document records the batch lifecycle.

| Choice | Catalogue group | Complete native envelope | Initial plot | GLB |
| --- | --- | --- | --- | --- |
| Rammed-earth timber infill | Detached homes | 13.375 × 19.60 × 10.15 m | 18 × 24 m | 1.49 MB |
| Classic courtyard motel | Hotels & visitor accommodation | 24.88 × 37.74 × 7.22 m | 29 × 42 m | 1.30 MB |
| Beltline brick mixed-use mid-rise | Homes over shops & mixed use | 34.16 × 34.16 × 20.43 m | 39 × 39 m | 5.02 MB |

These complete buildings remain at authored scale. Resizing changes their plot;
it does not stretch rooms, balconies or the motel sign. The Calgary groups are
form references, not a claim that these exact designs comply with a district.

## Visual review

Each final GLB was exported, reimported unchanged and inspected against the
three locked source images in 13 full views and phone comparison/construction
boards. An independent reviewer recorded zero unresolved P0/P1 issues for all
three. These are architectural-clay approvals, not textured-keeper approvals.

- [Infill comparison](showcase/building-next-three/infill-source-comparison.png)
- [Motel comparison](showcase/building-next-three/motel-source-comparison.png)
- [Mid-rise comparison](showcase/building-next-three/beltline-source-comparison.png)

The initial infill, motel and mid-rise candidates were rejected and rebuilt.
Corrections include infill pier proportions and connected side landings;
motel courtyard width, roof ends and sign lettering; and actual recessed
mid-rise balconies, continuous glazing frames and full-height metal ribbing.
Rejected and superseded evidence remains in the external batch directory.

## Student trial and correction

The local project is **Three new buildings — September pilot**, project ID
`3b3953e7-00b3-4fa5-8f55-4abb0e3e3486`, served on port 5177. All three were
selected from catalogue cards and placed in the Fort Calgary open field.
The mid-rise was moved through the map controls into clear ground. Overlapping
plot moves correctly produced a constraint message.

Resized plots were 24 × 30 m, 35 × 48 m and 48 × 48 m respectively. Saved
recipes after reload have the exact three GLB URLs, one instance each and
scale `[1, 1, 1]`. Grounding diagnostics reported no issues. Free close-capture
checks passed with other objects partially outside the frame. The motel's
near wing naturally conceals parts of its courtyard. No paid image/video
generation or final AI-fidelity test was performed.

A 180-degree rotation exposed a directionless rectangle fit. Fixed-native
placements now preserve the authored first edge in frontend geometry, server
planning and world orientation. The source hash also includes that edge, so a
half-turn invalidates an old recipe. Repeated detached homes remain a separate
mode. The two initial pilot zones were stamped with the new axis contract in
this isolated project; no production project migration was performed. The
motel's 25/205-degree screenshots demonstrate the corrected front/rear swap.

The existing flat plot apron can expose a pale support edge against uneven
Google terrain. This is a landscape-integration limitation, not a missing
building floor. Full ground blending, more distant LODs and paid AI rendering
are follow-up work. Camera framing used both student controls and the existing
equivalent debug focus helper for repeatable captures.

## Checks and reproducibility

- Native placement backend tests: 27 passed; landscape/source-scope: 24 passed.
- Native orientation/compiler/globe frontend tests: 55 passed.
- Promotion and published-library backend/tool checks: 19 passed.
- Catalogue frontend checks: 16 passed; TypeScript type-check passed.
- Hydrated promotion check: six published buildings, including the prior three.
- Isolated object storage: exact model hashes and public variant bindings verified.
- Browser error log: empty at completion of the three-building trial.

Builders and proof commands live in `tools/catalogue_next_three/README.md`.
Use a new immutable output directory for every rebuild. Native delivery bounds
include overhangs; nominal design dimensions are recorded separately. Candidate
identifiers accept the repository's existing underscore parents without
allowing path separators.

Only exact GLBs, independent reviews and selected source-comparison boards are
published. The full Blender scenes, render experiments and trial screenshots
remain under `C:/dev-artifacts/CityPrompt/building-next3-2026-09-06` and have not
been backed up to shared artifact storage. The infill source PNG is unchanged;
this release normalizes its storage to the existing Git LFS policy.
