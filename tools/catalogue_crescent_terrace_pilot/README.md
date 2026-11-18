# London Crescent Terrace: Bath Stone Grand

RLASM 6.1 architectural clay for the exact variant
`london_crescent_terrace` / `london-crescent-terrace-bath-stone` (variant 0,
"Bath Stone Grand"). This is a **local pilot**. It is not in the catalogue, not
seeded, and not activated. Only a person can activate a clay delivery.

No model of this archetype existed before: not in the clay library, the textured
families, the model library, the native model contract, the validation
catalogue, the teaching buildings or the picker.

Status of candidate **crescent-terrace-bath-stone-clay-v006**:

| Checkpoint | Status |
|---|---|
| Deterministic delivery checks | Pass, 86 checks. `evidence/delivery-verification.json` |
| Builder pixel review | Pass, with open notes. `evidence/builder-pixel-review.json` |
| Independent architectural-clay review | **Pass**, zero P0 and zero P1, ten P2 notes. `evidence/independent-review-v006.json`. An AI reviewer with no builder context, not a person |
| Runtime integration | NOT REVIEWED. No part of it has been run. `integration/runtime-review.md` |
| Publication or activation | Not authorized |

Earlier candidates, none of which may be used:

- **v001.** Chimney stacks too low to read from the street.
- **v002.** Went to independent review and was refused, with one P0 and four P1
  findings. `evidence/independent-review-v002.json` holds the review. The end
  roofs were stacked slate planes and not hips, a partition ran through each
  end, the last windows of two faces met behind one corner column, stacks hung
  over the slopes, and one review view was cropped.
- **v003.** The builder's own audit, made while v002 was with the reviewer,
  found a spine wall running out to the face of each end and floors short of
  the convex wall.
- **v004.** A second audit found five smaller faults, in the sills, the iron
  guards, the railing returns, the capitals and the column band.

- **v005.** A rework that answered every finding of the v002 review. It went to
  a second independent review and was refused with two P1 findings, both at the
  corners. `evidence/independent-review-v005.json` holds that review. The corner
  column and its two partners ran through each other, and the pavement railings
  had no bars for 1.6 m either side of each corner.

v006 answers the review of v005, and **passed** independent review with zero P0,
zero P1 and ten P2 notes. `evidence/builder-pixel-review.json` lists the answer to
each finding of the earlier reviews.

The reviewer's ten notes, none blocking: the corner shafts meet the wall only at
its edge, leaving a hairline near their tops from one raking direction; corner
capitals show a scroll end to each end elevation; end-bay windows sit tight
between the columns; door reveals have no floor; the convex bays widen toward the
ends; dormers have no attic; shafts are twelve-sided; the fitted oblique is
approximate; two end windows read as bright panes in one view; and the roof-plan
reference shows a different building.

## What the building is

A Georgian crescent of the Royal Crescent type: eighteen houses on half an
ellipse, three storeys, with a giant Ionic order standing on a plain ground
storey and carrying one continuous entablature and balustrade.

| Part | Built as |
|---|---|
| Plan | The concave front follows half an ellipse 95 m by 31 m. The range is 13.8 m deep. Over its paved strip the model is 126.3 m wide and 48.4 m deep |
| Houses | Eighteen, each three bays and 6.8 m wide on the front |
| Storeys | Ground storey 4.4 m, then two storeys behind the columns. Cornice at 13.0 m, balustrade at 14.1 m, ridge at 15.9 m, chimney pots at 19.2 m |
| Order | 128 engaged Ionic columns, 7.2 m tall and 0.66 m across: 57 on the concave front and 9 across each end. Each stands on a plinth block and carries a capital with two scrolls. At the four corners each capital faces the long front or back, so the two ends mirror |
| Corners | A corner column with a partner 1.30 m along each face on the concave side and 1.35 m on the convex side. Every pair stands 1.38 to 1.42 diameters apart, centre to centre, with blind wall between, so no window stands near a corner |
| Entablature | Architrave, frieze and a modillion cornice, then a balustrade with a pedestal over every column |
| Windows | One sash to a window bay on each storey, six panes over six: 1.95 m at street level, 2.35 m behind the columns with an iron guard, 1.70 m above |
| Doors | A six-panel door under a fanlight, with a knob on the centre stile, in the middle bay of sixteen houses on the front, one at each end for the two end houses, and a garden door to each house on the convex side: 36 in all, each 35 mm above grade |
| Roof | Two slate ranges with a lead flat between them, behind lead gutters, hipped at both ends. A stone upstand and two stacks with seven pots at every party wall. Dormers behind the balustrade |
| Railings | Spear-headed iron railings on a stone kerb round the building, with bars no more than 0.16 m apart all the way round each corner, opening at each door |
| Inside | Three floors, a spine wall and party walls to every house, so each window has a room behind it |

The model is 170,276 triangles in 12 flat-coloured parts, with no textures or
images. Nothing sits below grade. Every point of the model has a partner within
2 mm across the middle of the crescent.

## What it was measured from

Three reference images, locked by hash in `prework-manifest.json`:
`variant_0.png` (street), `variant_0_angle_60.jpg` (oblique) and
`variant_0_angle_90.jpg` (roof plan) under
`frontend/public/archetypes/buildings/london-crescent-terrace/`. None carries a
scale. Scale is set by the column at 7.2 m, and the other heights are measured
against it in the street view.

**The references disagree, and the roof plan shows a different building.** Each
disagreement is recorded in the manifest with the choice made:

- **Plan and length.** The roof plan shows about ten houses in a short block.
  The street view and the oblique agree with each other on a long sweep on half
  an ellipse. Those two govern. The roof plan is used only for the character of
  the roof.
- **House count.** Part of the front is hidden in the oblique, so the count is
  an estimate: about twenty by the builder, about eighteen by the independent
  reviewer. Built eighteen.
- **Catalogue text.** It gives 114 columns, thirty or more houses and a
  rusticated base. The images show about 54 bays on the front and plain ashlar.
  Built as the images show.
- **Catalogue plot.** The catalogue lists a 6 m by 12 m plot, one house. All
  three images show a whole crescent, so the whole crescent is built.
- **Window bars.** One large pane over another in the street view; six panes
  over six in the oblique. Built six over six.
- **First-floor sash.** About 2.05 m in the street view and 2.4 m in the
  oblique. Built 2.35 m.
- **Columns on the convex side.** The oblique shows them. A real crescent of
  this kind has a plain back. Built as drawn.

**The three comparison cameras are approximate.** Because the images do not
agree on the plan, no camera registers the model exactly against the oblique or
the roof plan.

**Inferred, because no image shows it:** the far end, most of the convex side,
the garden doors, the exact bay of each end door, the interiors, and that the
crescent is symmetrical. Bays on the convex side widen from 2.7 m at the middle
to 4.0 m in the end houses, because party walls stand square to the front.

**Left out on purpose:**

- The sunken areas, their steps and the bridges to the doors. Nothing may lie
  below grade, so railings stand at grade and each door has a level stone path.
- Attic rooms. Each dormer has a sash with a blind drawn behind it and nothing
  beyond.
- Ashlar coursing and joints, as surface texture.
- The lead-covered additions between the roof ranges in the roof plan.
- People, cars, lawn, streets and neighbours, which belong to the site.

## How the roof is made

The roof height at any point depends only on how far in that point lies from
the nearest face. `contour()` moves the whole outline in by a given distance,
drops each bay as it shrinks to nothing, and so gives a closed line at one
height. `strip()` joins one line to the next. Each bay still present on the
inner line gets its own face, which lies in that bay's own slope; a bay that
vanishes on the way in gets a triangle closing to the point where its neighbours
meet. Hips then run from each corner of the walls to the ridge with no special
case for the ends. Every choice is made from the bay alone, never from the
direction of travel, so the slate is cut into the same triangles at both ends.
A test samples a grid of points round every corner and requires exactly one
slate face over each.

## Size

At 126 m by 48 m this is a large fixed-size building, and at 170,276 triangles
it sits just under the 180,000 that the building memory gives as the usual
ceiling. It needs a plot of at least 130 m by 52 m. It cannot be stretched, and
a shorter crescent would be a different candidate: `HOUSES` is one constant.

## Files

| File | Purpose |
|---|---|
| `build.py` | The building. Every dimension is a named constant at the top. It uses `clay_kit.py` from `tools/catalogue_plus15_concrete_pilot/` |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the exact GLB in headless Chromium |
| `boards.py` | Four 1080 x 1920 phone boards |
| `verify.py` | Delivery checks, including that every whole view keeps the building in frame; writes `delivery-verification.json` |
| `test_crescent.py` | 27 tests, including that the generator still produces the recorded bytes, that every swept piece faces outward, that the roof is one surface with true hips, that no glass stands near a corner, that the corner columns stand clear of their partners, that railing bars turn every corner, that the whole crescent mirrors, that stacks stand through the roof and that no room reaches an outside face |
| `prework-manifest.json`, `candidate.json` | The measured contract and the candidate's hashes |
| `evidence/` | Builder review, delivery verification and the three independent reviews, of v002, v005 and v006 |
| `integration/runtime-review.md` | The runtime review template, filled in honestly: nothing was run. It lists all 36 doors |
| `integration/promotion.json` | An **unapproved** promotion package: identity, references, plot and picker text, with the approval and trial records left blank |

The GLB, renders and boards are review material and stay outside Git, under the
ignored `artifacts/` directory. **The GLB is reproducible:** the generator is
deterministic, and `candidate.json` records the SHA-256 it must produce.

## Reproduce

Needs Python 3.11 or later. Renders also need the frontend dependencies
installed and the repository served locally.

```bash
python3 tools/catalogue_crescent_terrace_pilot/build.py --output <new directory> --version <n>
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/catalogue_crescent_terrace_pilot/render.cjs <new directory>/<candidate>.glb <new directory>/renders
python3 tools/catalogue_crescent_terrace_pilot/boards.py <new directory>      # needs Pillow
python3 tools/catalogue_crescent_terrace_pilot/verify.py <new directory>
python3 -m pytest tools/catalogue_crescent_terrace_pilot
```

`build.py` refuses to write into an existing directory, and the render and board
scripts refuse to replace a file: RLASM never overwrites a candidate.

## Before this can be offered to students

1. **Done 2026-11-18: a person ruled on the roof-plan reference.** The street
   view and the oblique are accepted as the plan authority for this variant; the
   roof-plan image informs roof character only. Recorded under `human_decisions`
   in `integration/promotion.json`. This settles the source question only.
2. A person looks at the renders and boards and accepts or rejects the model,
   knowing the differences listed above.
3. Local install and student trial, as `docs/BUILDING_CATALOGUE_WORKFLOW.md`
   describes. This needs the local database and storage, which the session that
   built the model did not have.
4. The runtime review in `integration/runtime-review.md`, row by row, in the
   running app. Which of the thirty-six doors is the plot's entrance is
   undecided.
5. A recorded human approval, then `python -m tools.catalogue_promotion prepare`.

`integration/promotion.json` is ready for those steps, in the
`Rowhouses & townhomes` group (`ground_housing`), fixed native, on a 130 m by
52 m plot. Put it beside the rebuilt GLB and `evidence/independent-review-v006.json`,
saved as `independent-review.json`. The promotion tool's trial preflight accepts it
without writing anything. Existing library entries were checked by their metadata
only, as CI checks them. The publication preflight refuses it, as it must, until a
person's approval and a student trial are recorded for these exact bytes.

Each of those is a separate decision. Passing one does not grant the next.
