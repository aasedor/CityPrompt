# Street Manual intersection trial — 1 October 2026

All twelve Draft 3 choices saved at the browser trial crossing with their exact
variant, width and `public_realm_lego` identity. A separately drawn 6 m alley
also formed a T into the 16 m local street. The final three-road scene survived
reopening. This is a bounded local runtime checkpoint; human visual approval
remains pending and no publication is authorized.

## Reproducer and repair

New manual sections were rejected as junction candidates because the shared
graph and capture validation recognized older families only. Placement and
connected section replacement also run before the server creates a recipe.

The graph now recognizes validated manual recipes. During preflight, the exact
finite picker selection, archetype and width may preview a junction without a
recipe. The preview marker is placed on a copy of the candidate; neighbours and
saved properties remain unchanged. Invalid recipes cannot use that fallback,
and ordinary runtime detection still requires a recipe. The manual alley uses
the same supported junction path. Backend capture validation retains canonical
recipe identity and component locks while admitting the manual families.

## Browser matrix

Project: `http://127.0.0.1:5183/projects/60db592e-2d49-4cfb-8d53-fb8004c25784`.
Browser: agent-browser `street-intersections`, Chrome, 1264 × 625, mouse/keyboard.
Reviewer: Codex simulation, continuing the September 30 session. Site: disposable
prepared-level Currie parcel. Only this project was used.

All rows below passed ordinary **Apply street**, save and read-only API identity
comparison at the same crossing. The local/local row is the same type; the other
eleven rows pair different types. This is not twelve separately drawn networks.
The matrix also exists in `STREET_MANUAL_DRAFT3_REVIEW_2026-09-30.json`.

| Exact variant ID | Width | Four-way apply/save | Separate T authoring | Final scene reopened |
| --- | ---: | --- | --- | --- |
| `calgary_local_draft3_v1` | 16 m | PASS | Through street | PASS |
| `calgary_local_industrial_draft3_v1` | 18 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_collector_draft3_v1` | 23 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_arterial_4lane_50_draft3_v1` | 30 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_arterial_4lane_70_draft3_v1` | 36 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_arterial_6lane_draft3_v1` | 46 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_alley_draft3_v1` | 6 m | PASS | PASS | PASS |
| `calgary_local_high_activity_draft3_v1` | 21 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_collector_industrial_draft3_v1` | 26 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_collector_high_activity_draft3_v1` | 27 m | PASS | NOT TESTED | NOT TESTED |
| `calgary_arterial_high_activity_draft3_v1` | 36 m | PASS | NOT TESTED | PASS |
| `calgary_skeletal_draft3_v1` | 60 m | PASS | NOT TESTED | NOT TESTED |

The earlier bent industrial route rejected section replacement while its
approaches were unsuitable. It was replaced through the UI with the straight
trial crossing. Failed attempts remain in the evidence; they are not passes.
Collector/industrial readbacks in the inherited transcript establish their
successful later saves; earlier screenshots with `collector-fixed` in their
names still show the unsuccessful attempt and must not be cited as success.

## Final scene and visual review

Reopened roads:

- Local: `849ec639-d813-49bc-9d6e-d55ad34a5c69`, 16 m.
- High-activity arterial: `c8a25549-8124-4836-b8fc-44512194f034`, 36 m.
- Alley: `992ca00f-6ea0-4c36-9bec-7e8ca209ce09`, 6 m.

All retain two route controls and exact recipe identities. Whole-site graph
readback returns two renderable nodes: `street-four-way-20c51302` (four arms)
and `street-three-way-917234ad` (three arms). Recipe hashes and coordinates are
retained in `intersections-reopened-state.json` outside Git.

Reviewed native overhead, oblique and close browser images. The final four-way
has one open paved centre; planted medians and longitudinal markings stop at
the junction. The alley has an open paved T and crossings without a fourth arm.
Trees remain in planting bands in the reviewed close views. Tree canopies partly
obscure the approaches, so full pedestrian clearance is not certified. The
prepared pad has visible striped shading and a conspicuous edge against the
surrounding tiles; site presentation remains a follow-up. No paid render was run.

The inherited `intersections-mixed-close.png` was still a distant overview.
Final close reviews use the existing DEV camera helper and camera translation;
these change the review camera only. Geometry and street edits were authored
through ordinary controls. Read-only API checks do not constitute authoring.

## Runtime review scope

This supplements each exact variant's existing source/section review using the
[runtime review template](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md). Section hashes
remain in the companion ledger. Runtime base is `b778e50801f8c68626aa6fc30c20bb3b5dff0b17`
plus the commit containing this report; checklist version is 2026-09-24.

| Gate | Status in this intersection trial | Evidence or remaining work |
| --- | --- | --- |
| C1 Exact identity | PASS within apply/save scope | All 12 readbacks; final three also reopened. Capture identity untested live. |
| C2 Dimensions | PASS for fixed width | 6–60 m exact widths; previous section hashes unchanged. Other transforms untested here. |
| C3 Ground | NOT TESTED | Prepared scene reviewed visually; no new full-footprint measurement audit. |
| C4 Freshness | NOT TESTED | No forced asynchronous race. |
| C5 Circulation | NOT TESTED | Internal T/X appearance only; no public-road or full pedestrian-height traversal. |
| C6 Edit/recovery | PASS within section apply/save scope | All 12; final three reopen. Undo/Redo and delete recovery untested here. |
| C7 Failure/recovery | NOT TESTED | No forced conflict or unavailable-ground test. |
| C8 Visibility/export | NOT TESTED as a complete gate | Native final T/X close views reviewed; exact export/download and AI comparison unrun. |
| C9 Controls | PASS within desktop agent simulation | Street selection, Apply and alley drawing. No independent novice/touch trial. |
| S1 Section | PASS for retained metric identity | Existing source dimensions and hashes; no section asset changes. |
| S2 Network | PASS within this T/X scope | All 12 applied to X; alley T drawn; 12-variant T/X automated checks. Skew/curved combinations untested live. |
| S3 Shared grade/public access | NOT TESTED | No slope or external connection trial. |
| S4 Clearance/target recovery | NOT TESTED as a complete gate | Final central junctions visibly clear; no full clearance audit or delete/Undo. |
| B1–B5, P1–P4 | N/A | No building or park authored in this street-only trial. |

All other applicable live-matrix cases in the template remain NOT TESTED in
this follow-up. Full classroom acceptance, asset visual approval and publication
remain separate. The reproduced admission blocker is fixed. Slopes, exact export,
other live junction configurations and full route clearance remain acceptance
gaps; construction curb detail, pad shading and engineering refinement are
recorded follow-ups. Skeletal ditch grades/crown remain unmodelled.

## Verification and evidence

- Frontend: `npx --no-install vitest run src/features/pickPlace/streetConnectionProblem.test.ts src/features/pickPlace/streetEditConnections.test.ts src/components/viewer/globe/streetGraphIntersections.test.ts` — **66 passed**.
- Backend: `python -m pytest backend/tests/test_direct_3d_render.py -q -k 'junction or manual_streets'` — **29 passed**, 155 deselected. Includes all 12 variants in T/X manifest binding and altered-lock rejection.
- `npm run type-check` — PASS. `git diff --check` — PASS.
- Restored browser session: no uncaught page errors and no console warning/error messages. Backend login emitted the existing trapped bcrypt-version warning; authentication succeeded. Slow-request warnings remain (up to 13.44 s in the retained log). This is not a zero-warning backend claim.
- Source changes are the shared graph, preflight/edit checks, capture eligibility, focused regressions and documentation. No asset definitions were changed.
- External evidence: `C:/dev-artifacts/CityPrompt/street-manual-2026-09-30/web-source`. Main images: `intersections-four-way-close-review.png`, `intersections-alley-t-close-review.png`, `intersections-mixed-framed.png`, `intersections-reopened-close.png`.
- The companion ledger records image hashes and raw readback paths. Screenshots, raw logs and the inherited diff backup stay outside Git. These local paths are not a shared evidence backup.

Decision: bounded runtime trial recorded; **human visual approval PENDING**,
**LOCAL PILOT**, **completed false**. No push or publication.
