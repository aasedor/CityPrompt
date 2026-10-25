# Housing forms and introductory teaching classifications

This finite batch addresses two forms absent by ID/title search from the
252-family building-source inventory: a wartime/Victory house and a postwar
side-split. Earlier Vancouver Special, laneway and brick walk-up packages already
exist. Their picker availability needs reconciliation, not duplicate modelling.

The existing classification snapshot has 196 exact local choices, of which 188
are classified and eight remain held for contradictory reference/model identity.
The broader family index stays separate from exact-variant evidence. Source-only
families do not inherit dates, style or approval from one reviewed sibling.

## Basic teaching labels

| Archetype | Use / form | Style / aesthetic | Approximate association | Planning connections |
| --- | --- | --- | --- | --- |
| Wartime / Victory house | Residential; detached, one full storey plus occupied attic | Wartime small-house vernacular | 1940s to early 1950s | Wartime/postwar housing delivery; standardized small houses; later neighbourhood adaptation |
| Postwar side-split | Residential; staggered living, lower and raised sleeping levels | Mid-century suburban vernacular | Postwar, broadly 1950s–1970s | Suburban expansion; household space; adapting existing housing |

Each card has a brief explanation, three visible clues and one discussion
question. These are original teaching designs, not named historic-property
replicas. Dates describe design associations, not construction years. Tenure,
provider and affordability need their own evidence and are not inferred.

The federal [Victory Housing inventory entry](https://veterans.gc.ca/en/remembrance/memorials/canada/victory-housing)
provides local wartime/veteran housing context; it is a community memorial
inventory account, not an exhaustive national typology. The primary
[CMHC 1954 small-house catalogue](https://publications.gc.ca/site/eng/9.821302/publication.html)
includes split-level designs. Vancouver Heritage Foundation's own
[split-level guide](https://www.vancouverheritagefoundation.org/house-styles/split-level/)
connects the form to postwar housing and CMHC brochures. Regional histories
overlap; neither reference is claimed as the exact plan of these new models.

## Exact architectural-clay evidence

RLASM v6.1, fixed native scale, texture-free source-palette architectural clay.
The QA ground is green and excluded from each GLB. Only the native foundations
and modest entry steps remain; no enclosing grey site rectangle is exported.

| Candidate | Native dimensions, m | Triangles | GLB bytes | Independent state |
| --- | --- | --- | --- | --- |
| Victory clay-v004 | 8.34 ×7.20 ×6.12 | 13,648 | 783,000 | PASS: zero P0/P1; one P2 guard-foot/end-anchor finish |
| Side-split clay-v003 | 14.535 ×9.12 ×5.7225 | 14,572 | 826,444 | PASS: zero P0/P1/P2 |

Victory GLB SHA256:
`4b0df5c7fecb6b4a48002da119096b964fd03570503df1cb5fca91ae000fa2bb`.
Independent review SHA256:
`f542c010629a3930e97e1016c28bd6f8c573e47de7b30489b0d53dd3861a24ce`.

Side-split GLB SHA256:
`e5b80f45a78909bd0910f29bf0587d99c4bcb3225e7418e8d06e94c4dbfdf00f`.
Independent review SHA256:
`abdd14e52b1f7909554e50505ced1d09a7df748d8b0ee3f7c4f146f08a8dd4c5`.

Victory has 17 full-resolution 1600×1200 exact-GLB reimport renders, four enrolled
compatible source roles and three 1080×1920 phone boards. Its original side stair
camera is partly occluded; preserved clear-flight and upper-join supplements
close that proof duty. Exact mesh samples verify continuous attic arrival.

The side-split has 19 fresh 1600×1200 exact-GLB renders, five compatible source
roles and three 1080×1920 phone boards. The low wing is 6m deep and raised wing 8m,
preserving a source-derived depth ratio around 1.33 and stepped rear outline.
Known front faces stay registered. Its limited side-context stair view is paired
with an axial full-flight view and upper arrival. Both lower and upper stair
landings have positive destination-floor bearing; rear entrance arrival remains
clear after the shorter wing and descending stair move.

Exact metres, concealed structure, interior arrangements and unequal floor
offsets are declared architectural inferences. The source top is a near-vertical
high aerial, not surveyed orthography. Split-level lower/living/upper floors are
.10/.53/2.30m; this keeps occupied clear heights above the native zero datum.
It is not a measured historical half-storey plan or a code-compliance claim.

## Preserved failures and lessons

Victory v001 exposed a gable/roof intersection and an inspection emitter crossing
the roof. v002 lighting did not adequately expose the attic. Independent v003
review then found a 0.19m arrival gap after the stair changed from 15 to 14 steps,
an inadequate flight camera and missing source sash crossbars. v004 derives
landing length from actual endpoints, restores the six-light upper sashes and
supplies exact-GLB stair proof. Prior attempts and reviews remain intact.

Side-split v001 had coincident shared-wall corner faces, descending rail/post
separation and inadequate full-flight evidence. v002 corrected those but
independent review rejected equal-depth wings that lost the source plan shape.
v003 shortens the low wing, continues the newly exposed side, seats the vent on
its changed roof and moves furniture/stairs/entry evidence with the geometry.

Split reference generation also drifted. The prior top's ridge orientation and
both proposed rear-left views are rejected explicitly. The latter add a second
left-end window and low opening absent from both compatible front-left views.
All complete original boards remain preserved. Five compatible front/oblique/top
roles are locked; unseen rear/right elevations are inferred, not copied from the
incompatible proposal. Source pixels override conflicting generation prose.

## Delivery and remaining work

External candidates, editable Blender files, exact script/input snapshots,
rejected history, image originals and comparisons are retained under
`C:/dev-artifacts/CityPrompt/housing-teaching-20261025`.
Snapshots are repository-shaped overlays requiring the recorded real Git base,
Blender and Python/Pillow; no turnkey application or byte-identical rendering
across hardware is claimed.

The dated [Drive review batch](https://drive.google.com/drive/folders/1XqW1KTtuRDdrD54B1Ty1qiCIarX3Tl69)
receives full-resolution originals and complete per-version archives. Its local
`delivery-manifest.json` records IDs, local hashes and Drive metadata verification.
Delivery counts and final checks are recorded after readback.

## Verification

- Housing, planning-history and catalogue-teaching Python suites: 50 passed.
- Narrow RLASM method, delivery-contract and quality-memory suites: 26 passed.
- Catalogue teaching, history and palette facet/category Vitest suites: 50 passed.
- Frontend TypeScript: `npm run type-check` passed.
- Local browser: 196-choice catalogue retained; postwar filter returned nine
  building choices and the missing-middle filter returned ten. The bungalow and
  fourplex details kept form, aesthetic, approximate era and planning connections
  separate. No browser warnings or errors were captured. The project was not
  modified and its token balance stayed at 476.
- Both final GLBs, independent review hashes, every inspected image hash and all
  full-resolution/phone dimensions were rechecked. The source-family coverage
  CSV is byte-identical to the preceding reviewed snapshot.

Both models remain outside the seed/runtime catalogue. All applicable exact-byte
runtime placement, terrain, route, resizing, edit/recovery, save/reload, capture
and performance cases remain **NOT TESTED**. Offline visual acceptance does not
grant human activation, textured-keeper approval or engineering certification.
No paid City Prompt image/video jobs, saved-project polygon comparison, catalogue
publication, push or deployment is part of this batch.

The next useful work is to reconcile the eight held current identities and the
existing archived housing forms, then choose the next evidence-backed form gap.
Tenure, Indigenous authority and neighbourhood outcomes need sourced cases or
composed scenes; they cannot be filled by applying an aesthetic to another house.
