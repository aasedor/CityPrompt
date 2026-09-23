# Catalogue restart — 22 September 2026

Later user direction: construct the models with Astra, then switch to Sol for
runtime testing. See [the model inventory and Sol handoff](ASTRA_MODEL_BUILD_SOL_HANDOFF_2026-09-22.md).
Montreal has a fresh model review; the brick courtyard building has a new bounded
build. Townhouse and timber-apartment source conflicts await a design choice.
This changes task ordering, not the outstanding runtime acceptance gates below.

The accepted target remains **18 starter choices across nine collections**, then
64 choices across 32 collections. This resumes the
[September 5 priorities](CATALOGUE_BUILDOUT_PLAN_2026_09_05.md), not a new list.
Use the vacant Currie parcel for local trials; the earlier Fort Calgary fixture
in the September 5 plan is superseded by the user's Currie instruction.

## Queue

| Order | Choice | Exact identity | Current action |
| --- | --- | --- | --- |
| 1 | Side-by-side duplex | `calgary_modern_infill_house / infill_duplex` | Existing v004 independently re-reviewed; installed as a local-only trial. Complete paired entrance integration and remaining runtime checks before activation. |
| 2 | Stacked Montreal duplex | `montreal_duplex / montreal_duplex_plateau` | Next source lock and one-model clay pilot. |
| 3 | Contemporary townhouse row | `rndsqr_missing_middle_townhomes / rndsqr_townhome_dark_wood_metal` | Follow the duplex's multiple-entrance contract. |
| 4 | Timber-and-glass apartments | `contemporary_midrise_residential / contemporary_midrise_variant_timber_glass` | One independently reviewed pilot. |
| 5 | Courtyard apartments | `courtyard_family_housing / courtyard_family_brick_modern` | Preserve courtyard topology and access. |

Reuse nominations remain modern infill, Craftsman bungalow, Siheyuan courtyard
housing, corner shop and retail strip. Verify each exact existing delivery before
calling it student-ready. The other starter priorities remain pastoral community
park, formal civic plaza, market/event square, the 21 m high-activity local street,
green-corridor multiuse pathway and protected two-way cycle track, alongside the
existing rustic neighbourhood park and 16 m local street work. Keep each domain
in a separate bounded initiative. This restart does not publish either historical
Wave 2 or other unapproved models.

## Completed local duplex checkpoint

- Branch: `codex/catalogue-priority-recovery`, based on `b7c074b41`.
- Model: `calgary-side-by-side-duplex-clay-v004`, SHA-256
  `1414b17d3ebec4aa87529da16dcc3a8f10305b51eaa3d129fb5a5c6c0d296f92`.
- A separate reviewer performed a fresh holistic review of the unchanged model,
  three sources, thirteen individual views and four boards. Clay review passed;
  this is not runtime acceptance or human activation.
- Exact GLB, review and generated picker entry installed through
  `tools.catalogue_promotion trial`, following its successful dry run. One model
  seeded and verified in the isolated database/storage. No paid calls or push.
- Disposable project: `76903dbe-238f-432b-bfdc-e5f08e7c381b`,
  `http://127.0.0.1:5175/projects/76903dbe-238f-432b-bfdc-e5f08e7c381b`.
  Prepared boundary and street copied via API from the prior rehearsal; duplex
  placement, plot resize and Undo used the UI. This is an assisted integration
  trial, not a new-student empty-project usability test.
- Runtime compiler selected the exact `infill_duplex` family with one instance,
  scale `[1,1,1]`, dimensions 13.34 × 21.472 × 9 m and two storeys.
  Downloaded runtime model bytes matched the reviewed hash (3,110,128 bytes).
- A 17 × 25 m plot placed facing the nearby street. Widening to 20 m saved;
  Undo restored 17 m, and subsequent reload retained the exact original
  coordinates, variant and plot dimensions. No house repetition was installed.
- Fixed shared discovery: parent archetypes can now appear under a detailed
  variant's category; searching a variant opens that variant instead of the
  parent's first design. The card's Calgary guide follows the selected model.
  Browser search confirmed the duplex thumbnail, name, selected variant and
  two-home classification together.

Evidence remains outside the source tree:
`C:/dev-artifacts/CityPrompt/catalogue-priority-2026-09-22/`.
Key files: `independent-duplex-review.json`, `runtime-model.json`,
`verification.json`, `placed-zones.json`, `resized-zones.json`, `undo-zones.json`,
`duplex-search.png`, `duplex-framed.png`. Only the intentional model (Git LFS),
review, manifest, picker, discovery fix and records belong in the commit.

## Remaining gates and reusable lessons

The local-only marker intentionally blocks ordinary publication validation.
Use `check(root, allow_trials=True)` for this checkpoint; do not remove the marker
to make a production check green.

The duplex has **two separate front entrances**. Current automatic metadata
supports a single entrance per plot. No copied infill anchor or invented central
door was installed. Extend the shared connection representation to measured
multiple entrances and test both approaches, rotation, move and reload before
claiming automatic access for this model or townhouse rows.

Runtime C1/B1 exact identity/native placement passed. C6 resize/Undo/reload passed
for the bounded sequence above. C2/C9 are partial: minimum plot, wider plot and
street-facing placement ran; independent rotation and upper-size cases remain.
C3/C5/B2–B5 ground/entrance acceptance remains open. C4/C7 asynchronous failure
cases and C8 low/occluded saved-file capture remain untested for this variant.
Street/park-specific S/P gates are N/A to this building delivery. A scene-level
aerial screenshot is not evidence that those open gates passed.

For every later variant, search by its ordinary name and browse its real housing
category; do not assume the parent category is correct. Lock whole-model native
scale and complete exterior dimensions, including steps/projections. Count actual
entrances before choosing a connection contract. Reuse the shared runtime review
template and preserve explicit NOT TESTED states instead of inheriting passes
from an earlier house.

Validation: 22 tests across canonical catalogue, catalogue and asset registry
passed; TypeScript checking and targeted ESLint passed. Hydrated local-trial
validation passed for all ten manifest entries. Permanent activation is not
requested until the local trial is ready.
