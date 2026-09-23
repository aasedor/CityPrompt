# Runtime integration review — Calgary local v0

**Continuation:** [ground/export review](CLASSROOM_GROUND_EXPORT_2026-09-22.md)
supersedes the public-road and download omissions below for the same exact
variant. A further UI endpoint extension, street Undo/Redo, reload, low view from
inside the site and actual PNG download passed. Shared outside masking and
measured cut/fill faces were repaired. C5/S3 now have a bounded concept visual
pass; fine curb/accessibility design and close-view tile seams remain follow-up.
The original table below records the earlier checkpoint, not the final state.

Exact parent `calgary_local`, variant `calgary_local_v0`, 16 m metric section,
revision `draft-4.0-figure-2`. Reviewer: Codex, 22 September 2026.
Source hashes, project, environment and evidence are in the
[pilot record](CLASSROOM_CATALOGUE_PILOT_2026-09-22.md) and its JSON manifest.
This is a conceptual draft-manual section, not an approved construction standard.

| Gate | Status | Evidence / limit |
| --- | --- | --- |
| C1 Exact identity | PASS | Persisted selected variant and metric recipe |
| C2 Dimensions / transforms | PASS | Three-point UI route; width remains 16 m |
| C3 Ground support | PASS, scoped | Final street ground ready, including proposed extension |
| C4 Freshness / late results | NOT TESTED | No forced race |
| C5 Pedestrian / public-road continuity | NOT TESTED, partial evidence | Buildings/garden connect; public endpoint saved, low junction review outstanding |
| C6 Edit / save / reopen | PASS, scoped | Endpoint drag and reload; street-specific Undo/Redo not run |
| C7 Failure / recovery | NOT TESTED | No forced conflict |
| C8 Views / capture | PASS, scoped | Top/oblique and exact PNG; download action OPEN |
| C9 Student controls | PASS, assisted | Draw route, select, public-road toggle and endpoint drag |
| S1 Metric section | PASS, scoped | 16 m: 2×(0.3 setback + 1.8 sidewalk + 2.65 boulevard + 3.25 lane); reversed/asymmetric cases not run |
| S2 Route / junction topology | PASS, scoped | Bent route renders; full junction topology not reviewed |
| S3 Shared grade / public connection | NOT TESTED | Ready status is not proof of final curb/junction grade |
| S4 Clearance / target identity | PASS, scoped | Two building approaches and garden entrance survive reload; deletion target recovery not run |
| B1–B5 / P1–P4 | N/A | Street variant |

All remaining template matrix cases are NOT TESTED in this run, including
natural slopes, junction arm combinations, forced failures and paid images.
Free landscape respects the street and entrance paths. Decision: useful bounded
street runtime evidence; public-junction acceptance remains open. No scale-up or
construction approval follows from this review.
