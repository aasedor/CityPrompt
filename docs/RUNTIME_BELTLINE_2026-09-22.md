# Runtime integration review — Beltline brick modern v003

Exact parent `calgary_beltline_mid_rise`, variant `beltline_brick_modern`, asset
`clay_beltline_brick_midrise`. Reviewer: Codex, 22 September 2026.
This is a runtime review of the previously activated architectural-clay asset,
not a new keeper decision. SHA-256, entrance measurements, native dimensions,
source revision, project, environment and evidence are in the
[pilot record](CLASSROOM_CATALOGUE_PILOT_2026-09-22.md) and its JSON manifest.

Supported trial: prepared Currie level, rectangular 39/48 m plots, one native
five-storey model, both sides of a bent street, 1.8 m automatic apron approach.

| Gate | Status | Evidence / limit |
| --- | --- | --- |
| C1 Exact identity | PASS | Served bytes match activated v003; both recipes unit scale |
| C2 Dimensions / transforms | PASS | UI placement and 39→48 m plot edit; native geometry unchanged |
| C3 Full ground support | PASS | Prepared scene ready; zero reported grounding issues |
| C4 Freshness / late results | NOT TESTED | No forced race in this run |
| C5 Pedestrian continuity | PASS | Two native apron approaches to local street sidewalks |
| C6 Edit / Undo / save / reopen | PASS | Before/Undo/Redo geometry readback; final reload |
| C7 Failure / recovery | NOT TESTED | No forced save failure |
| C8 Views / capture | PASS, scoped | Low view and exact PNG inspected; download action OPEN; AI not run |
| C9 Student controls | PASS, assisted | Catalogue, resize, Place another; not an independent novice trial |
| B1 Native placement | PASS | Two unscaled instances, one per plot |
| B2 Entrance measurement | PASS | v003 source door and native apron; low live view |
| B3 Entrance authoring | PASS | Both new placements automatic; no coordinate entry |
| B4 Approach / setback recovery | PASS, scoped | Resize snaps clear of street; Undo/Redo restores route |
| B5 Foundation / stair / access design | NOT TESTED | Two-step geometry present; accessibility not certified |
| S1–S4 / P1–P4 | N/A | Building variant |

Unrun matrix cases remain NOT TESTED: natural slope, unsupported-ground inward
recovery, maximum size, concurrent edits, conflicting saves, manual step picking,
and paid image fidelity. Free landscape compatibility passed in the final scene;
custom continuous-image base compatibility was not re-tested with this variant.

Decision: bounded prepared-site runtime pass. Classroom release still requires
the shared edge and download issues in the main report to be resolved. No new
asset activation or publication is authorized by this runtime result.
