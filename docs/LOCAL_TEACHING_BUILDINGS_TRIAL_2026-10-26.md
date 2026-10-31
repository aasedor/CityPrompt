# Seven teaching buildings — local trial, 26 October 2026

The seven independently reviewed architectural-clay candidates are now selectable
in the development app at <http://localhost:5174>. They add seven buildings to
the existing local roster: **203 choices, 104 buildings, 46 parks and 53 streets**.
The historical 196-choice teaching audit remains unchanged; seven additive
lessons are bound to the exact local trial identities and candidate revisions.

Use **Buildings**, then search a name below, or browse its style/era. Each card
includes basic use/form, architectural style, approximate design era and
planning context. Dates describe design associations, not construction years.

| Building | Exact candidate | Reserved plot (m) | Native envelope W × D × H (m) |
| --- | --- | --- | --- |
| Prairie School house | prairie-school-house-clay-v004 | 21.4 × 15.4 | 18.40 × 12.40 × 5.80 |
| Postmodern neighbourhood library | postmodern-neighbourhood-library-clay-v002 | 23.4 × 15.7 | 20.36 × 12.665 × 5.85 |
| Bauhaus-inspired design workshop | bauhaus-design-workshop-clay-v003 | 23.9 × 13.2 | 20.82 × 10.19 × 7.75 |
| De Stijl artist studio | destijl-artist-studio-clay-v004 | 18.6 × 12.0 | 15.55 × 8.975 × 5.76 |
| Mughal-inspired reading pavilion | mughal-reading-pavilion-clay-v002 | 17.7 × 18.2 | 14.60 × 15.10 × 8.30 |
| Wartime / Victory house | wartime-victory-house-clay-v004 | 11.4 × 10.2 | 8.34 × 7.20 × 6.12 |
| Postwar side-split house | postwar-side-split-house-clay-v003 | 17.6 × 12.2 | 14.535 × 9.12 × 5.7225 |

All seven retain their native dimensions and complete authored geometry. Width,
depth and added floors are unavailable. Move and rotation remain available.
The Victory card explicitly describes one full storey plus an occupied attic;
the side-split describes staggered levels. Neither is presented as a generic
multi-storey extrusion. The unfinished Montréal shoebox is excluded.

## Installation and ordinary-control trial

Source implementation checkpoint: `060114abda81903277a2f45510139b33ba021eae`.
Trial project: <http://localhost:5174/projects/f97ec3a3-ce7d-4547-a392-14ac1676651c>.
Tester: Codex operating ordinary Edge controls as Student Stress Tester.
Viewport: 3120 × 1189 CSS pixels, Windows mouse/pointer, 26 October 2026.

The disposable boundary was drawn and adjusted through normal controls onto
an open field north of the Fort Calgary buildings, clear of buildings and water.
Its prepared level surface is approximately 139 × 55 m / 7,541 m². This is a
visualization test parcel, not a development proposal or surveyed site boundary.

The finite installer dry run validated all seven exact models, original
independent reviews, metric envelopes and front/oblique/top references. Victory
was installed and trialed first: search/card, placement, disabled size controls,
30-degree rotation, Move handle, Undo, Redo, save and full reload. Its authored
roof, windows, chimney, siding and native steps appeared at close range.

After that pilot, the remaining six were installed. All seven were selected
and placed through Buildings → search → Choose & place → canvas click. Each
opened its fixed-native inspector and reached **3D saved**. An aerial view
showed seven distinct footprints/roof forms; an oblique view showed all seven
authored buildings, with close inspection of the glazed workshop and studio.
No persistent generic blocks or browser warnings/errors appeared in this trial.
The complete project was then fully reloaded: all seven retained their authored
models. The Architectural style menu includes all seven new style labels; choosing
Prairie School produced its single exact house and introductory explanation.

The database readback contains seven exact placement IDs/revisions, plus the
boundary. Localhost HTTP readback verified **35/35 original files by SHA-256**,
including all seven GLBs, seven independent reviews and 21 locked references.
The installer preserves existing matching files and refuses different source
or destination bytes. No existing catalogue rows/models were replaced.

The shared native renderer centres complete GLB bounds without scaling; the
side-split's asymmetric origin is retained in the manifest and its occupied
envelope is checked against actual transformed GLB geometry. This installation
uses direct local GLBs, so it creates no Model Library rows or storage objects.

## Evidence and limits

The versioned runtime manifest is `frontend/src/data/localTeachingBuildings.json`.
Repeat the finite dry run/install with `python -m tools.local_teaching_buildings
--candidate <exact-candidate>` and then `--apply`. It reads the active local
public directory from `artifacts/local-runtime.json`; explicit overrides and
source-root selection are available in `--help`.

Local installation/HTTP/database receipts are under `artifacts/local-dev/`:
`teaching-dry-run-20261026.json`, `teaching-all-install-20261026.json`,
`teaching-all-http-20261026.json`, `teaching-trial-saved-20261026.json`.
Full-resolution UI screenshots and per-variant follow-up runtime checklists are
kept externally in `C:/dev-artifacts/CityPrompt/local-teaching-trial-20261026`.
These screenshots document interactive QA; they are not exported AI originals.
Earlier independent source/model review deliveries remain unchanged.

This is a **bounded prepared-level local trial**, not full runtime acceptance.
Natural slopes, unsupported ground holes, all-side close ground review, automatic
and manual entrance paths, landscape application/invalidation, failure/conflict
recovery, mixed street/park scenes, touch and exact export remain NOT TESTED for
these seven variants. Victory's move/rotate/Undo/Redo does not certify each of
those operations individually for the other six. The two measured house entry
anchors do not establish a verified continuous pedestrian route. No accessibility,
structural or code-compliance claim is made.

The original independent architectural-clay reviews remain the asset evidence.
This trial does not upgrade them to textured keepers. Production builds omit
these trial choices and their teaching payload; the production seed, live
catalogue and cityprompt.ca were not changed. No paid generations, credit
purchases, push or deployment were performed.

The independent source review found one recovery defect: an unavailable saved
trial revision could expose the backend's generic planned-massing representation.
The correction retains native ownership for those saved trial plots, suppresses
their generic models, blocks capture and shows the required model revision with
restore/replacement guidance. A selection button keeps the original plot editable.
Consumer-level routing, visible notice, capture-blocking and recovery-message
regressions were observed RED, then GREEN. The combined affected frontend suite
now passes **183 tests across 12 files**; no second review was used as a substitute
for regression verification. Natural terrain, routes and export retain their
separate untested status above.

Verification: focused registry/catalogue/native-contract/teaching Vitest tests,
the production tree-shaking check, the finite installer pytest tests, and
`npm run type-check`. Exact results are recorded in the implementation ledger.
