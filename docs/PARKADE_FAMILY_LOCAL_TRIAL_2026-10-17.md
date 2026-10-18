# Five parkades: completed local trial

Branch: `codex/parkade-family-pilot`, based on parking-lot checkpoint
`0ff598dfe`. The original Classic Concrete pilot was saved as `0330a4fa9`.
This is a local architectural-clay design trial, not a production publication
or a textured RLASM keeper approval. The user approved two conventional and
three innovative original parkades. The existing production catalogue and
production database have not been changed.

## Try the models

- Local saved scene: <http://127.0.0.1:5184/projects/060a2f62-af41-4670-b4a9-0da25d2b10cc>.
  Title: **Parkades · five design local trial**. It contains all five models on
  one prepared vacant-field site. It uses the existing local QA account.
- In Design, open **Buildings → Parkades**, or **Streets → Browse parkade buildings**.
  The Streets link opens those same building cards; it does not create a second
  placement system. Parking-lot drawing remains in Streets.
- Standalone inspection and 1/5/20-copy measurement page:
  <http://127.0.0.1:5184/parkade-review.html>.
- The frontend must run in DEV. The API must start with
  `CITYPROMPT_LOCAL_PARKADE_TRIAL=true`, `APP_ENV=development` or `test`, and a
  loopback database. Production mode and remote databases refuse this identity
  overlay even if the flag is accidentally set.

With the configured isolated local DB/MinIO environment in `backend/.env`:

```powershell
py -3.12 tools/parkade_family/local_trial_install.py          # dry run
py -3.12 tools/parkade_family/local_trial_install.py --apply  # explicit local seed
py -3.12 tools/parkade_family/local_trial_install.py --verify # DB and object bytes
```

The wrapper refuses any database except loopback port 55432,
`cityprompt_repairs_20261004`, or storage except loopback port 19003. It requires
the existing local QA owner. The finite manifest, parent definitions and native
identity overlay are versioned independently of the global catalogues. A fresh
empty database bootstrap on a second computer has **not** been tested; do not
describe the convenience wrapper as a complete new-machine setup.

The current Vite server uses the hydrated public directory at
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public`.
The review page needs the five exact GLBs copied under `models/parkade-pilot/`;
the real app loads the verified Model Library objects through the normal loader.

## Exact deliverables

| Design | Approved candidate | Native envelope W × D × H, metres | Levels | GLB bytes | Mesh triangles | Materials |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Classic Concrete | `parkade-classic-concrete-clay-v005` | 60 × 36 × 12.80 | 4 | 961,992 | 18,120 | 7 |
| Urban Brick | `parkade-urban-brick-clay-v001` | 54 × 36.021 × 16.10 | 5 | 1,789,284 | 33,644 | 9 |
| Green Terraces | `parkade-green-terraces-clay-v003` | 60 × 40 × 12.80 | 4 | 4,757,064 | 77,572 | 12 |
| Solar Ribbon | `parkade-solar-ribbon-clay-v001` | 66 × 36 × 16.10 | 5 | 2,116,728 | 39,360 | 11 |
| Mobility Courtyard | `parkade-mobility-courtyard-clay-v002` | 64 × 48 × 12.80 | 4 | 1,820,900 | 35,204 | 13 |

All five embed zero images/textures. Total GLB bytes: 11,445,968. Runtime copies
are byte-identical to the independently reviewed originals: no further runtime
geometry or material derivative has been substituted. Full SHA-256 hashes,
all four source-role hashes per model, review hashes and measurements are in
`docs/runtime-reviews/parkade-family-local-trial-2026-10-17.json` and the seed manifest.

Authority is original metric CAD front/oblique/top/ramp-section drawings, locked
before authoring. The two earlier AI design sheets are aesthetic studies only.
All models use metres, +Y up, native scale 1, base Y=0 and front +Z (authoring
front -Y/Z up). No bounding-box recentering or global scale changes occur.
Geometry, deck count and height remain fixed while the surrounding plot can
grow. Urban Brick's plot allowance rounds upward to 40.1 m depth so the existing
one-decimal editor does not round below its native fit threshold. Its model
dimensions and bytes were not changed.

Each design includes actual open parking decks, rear ramps, authored stairs and
transparent stair-core glazing. Green Terraces adds planted ledges and roof
garden; Solar Ribbon adds fixed fins, a solar canopy and EV markings; Mobility
Courtyard adds an open court, coloured fins, bicycle spaces and a glazed café.
Solar panels, charging bays and café are visual features, not operational services.

## Checks actually executed

Passed:

- All five exact GLBs independently reviewed against four source roles, 15 full
  actual-GLB reimport views and three phone boards per candidate. Final holistic
  architectural-clay reviews have zero unresolved integer P0/P1 findings.
- 643 actual-GLB geometric probes across the five models: native datum, rear
  ramp/landing joins and sampled headroom, stair/deck joins, glazing clearance
  and signature-specific openings. These samples are not a structural audit.
- Independent code review of frame geometry, staging, identity isolation and
  gallery measurement. Fixed the entrance-striped stall conflict, columns
  intruding into six-metre aisles, Green's disconnected bracket support, source
  role path aliasing and premature/global metadata publication before accepting
  the final candidates. Failed candidates remain immutable external evidence.
- 271 Python tests: parkade tools plus backend local-overlay gating, native
  archetype resolution and LEGO assembly regressions. Latest six staging tests
  include canonical source-role path and exact-byte tamper rejections.
- Final narrow frontend run: 54 Vitest tests across five matching files
  (trial bindings, palette, canonical catalogue, registry and picker categories).
  TypeScript checking and changed review-page/test ESLint passed.
- Production `npm run build` passed with the configured hydrated public/env
  profile. The first plain checkout-public attempt failed because an existing
  recovered urn asset was missing there; the profile used by this local app
  supplies it. Existing bundle-size/mixed-import warnings remain.
- Installer verification passed for all five database records and MinIO keys/
  bytes. All five standalone local HTTP responses were 200, valid GLBs and
  matched the exact approved SHA-256 values.
- Actual ordinary browser workflow: discovered all five via the shared picker,
  placed each on a prepared site, selected and moved each, rotated each to 15°,
  deleted each and restored with Undo. Classic also passed Redo deletion and
  a second Undo restoration. No real user scene was edited.
- Full page reload restored all five. Independent local DB readback verified
  exact revision/variant, native floor count/height and five compiled building
  rows; polygon first-edge yaw was 15° for each.
- Free current-3D-view capture contained all five models. Courtyard pedestrian
  view and short walking/turning trial showed the open deck and café glazing/
  interior. The account stayed at 412 tokens; no paid AI generation was run.

Not tested: paid AI-provider fidelity; automatic driveways/access-route creation
for these new parkades; upper-floor pedestrian navigation; unsupported/sloping
terrain; vehicle swept paths; accessibility/egress/structural compliance; certified
stall capacity; production catalogue/hosted assets; a fresh database installation;
student-laptop or mobile hardware. These are fixed visual models, with no working
doors or editable/repeatable floor metadata.

## Measured desktop cost

RTX 5060 / i5-14400F, 1280 × 569 review buffer, DPR 1, source clay materials and
shadows. Every 1/5/20-copy Oblique screenshot was checked for complete framing.
Two-second frame samples describe browser frame intervals, not GPU render time.
Other browser tabs were open; these are isolated gallery samples, not a full map
benchmark or a station comparison.

| Design | Geometry attributes/index KiB | Draw calls 1 / 5 / 20 | Renderer triangles at 20 | Median interval range | Highest sampled p95 |
| --- | ---: | --- | ---: | --- | --- |
| Classic Concrete | 930 | 17 / 77 / 302 | 751,684 | 17.5 ms | 18.3 ms |
| Urban Brick | 1,736 | 21 / 97 / 382 | 1,379,364 | 17.4–17.6 ms | 21.1 ms |
| Green Terraces | 4,631 | 27 / 127 / 502 | 3,129,764 | 17.4–17.6 ms | 18.2 ms |
| Solar Ribbon | 2,053 | 25 / 117 / 462 | 1,608,004 | 17.5–17.9 ms | 20.5 ms |
| Mobility Courtyard | 1,762 | 29 / 137 / 542 | 1,435,764 | 17.4–17.5 ms | 18.3 ms |

Renderer triangles include ground/shadow/transmission passes, not just GLB mesh
triangles. Geometry counters stayed constant across copy counts for each model,
consistent with geometry sharing; earlier selected models remain in the cache.
Materials belong to each placement. Source models have no texture images;
renderer texture counters include render buffers. Total JS/GPU memory was not
measured. Warm loopback ready/transfer times do not establish cold network cost.
Green Terraces is the largest mesh and still needs target-laptop validation.

## Evidence, changes and publication boundary

Evidence root: `C:/dev-artifacts/CityPrompt/parkade-family-2026-10-17/`.

- `five-designs-reviewed.png`: readable five-design contact sheet, actual GLB renders.
- `catalogue-five.png`, `site-five-final-oblique.png`: local UI and complete scene.
- `site-five-free-capture.png`, `site-five-capture-preview.png`: actual free capture.
- `site-courtyard-walk.png`: pedestrian-height glazing/deck check.
- `browser-performance.json` and 1/5/20-copy screenshots: measurement evidence.
- `site-five-final-readback.json`, `browser-edit-actions.json`: local persistence/actions.
- Per-candidate source locks, build reports, GLB audits, all 15 views and three
  phone boards, exact independent reviews, plus preserved failed predecessors.

Source changes: finite authoring/source/audit/staging tools under
`tools/parkade_family`; a DEV-only frontend roster, category and Streets shortcut;
the opt-in backend identity overlay and tests; standalone review page; the finite
seed package and this report. The global frontend archetype JSON and backend
dimension table are unchanged. No migration or existing scene rewrite was added.

Only the five reviewed GLBs, their five review records, four source PNGs plus one
model preview per design, finite manifests and code/docs are promoted. Binaries
use the repository's existing LFS rules; no LFS policy change. Blender projects,
failed versions and bulk visual evidence stay outside the source tree. The
external evidence folder is not yet a shared backup.

Publication is intentionally pending human visual acceptance and a separate
runtime/storage promotion check. No parkade assets have been pushed or deployed;
the live site is unchanged by this local trial.
