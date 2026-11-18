# London Crescent Terrace: Bath Stone Grand

RLASM 6.1 architectural clay for the exact variant
`london_crescent_terrace` / `london-crescent-terrace-bath-stone` (variant 0,
"Bath Stone Grand"). This is a **local pilot**. It is not in the catalogue, not
seeded, and not activated. Only a person can activate a clay delivery.

No model of this archetype existed before: not in the clay library, the textured
families, the model library, the native model contract, the validation
catalogue, the teaching buildings or the picker.

Status of candidate **crescent-terrace-bath-stone-clay-v004**:

| Checkpoint | Status |
|---|---|
| Deterministic delivery checks | Pass, 70 checks. `evidence/delivery-verification.json` |
| Builder pixel review | Pass, with open notes. `evidence/builder-pixel-review.json` |
| Independent architectural-clay review | Not yet reviewed. v002 is with the reviewer; no result yet |
| Runtime integration | NOT REVIEWED. No part of it has been run. `integration/runtime-review.md` |
| Publication or activation | Not authorized |

Earlier candidates: v001 had chimney stacks too low to read from the street. v002
went to independent review; while it was there the builder's own audit found a
spine wall running out to the face of each end and floors short of the convex
wall, both fixed in v003. A second pass found five smaller faults, in the sills,
the iron guards, the railing returns, the capitals and the column band, all
fixed in v004.

## What the building is

A Georgian crescent of the Royal Crescent type: twenty houses on half an
ellipse, three storeys, with a giant Ionic order standing on a plain ground
storey and carrying one continuous entablature and balustrade.

| Part | Built as |
|---|---|
| Plan | The concave front follows half an ellipse 104 m by 34 m. The range is 13.8 m deep. Over its paved strip the model is 135.4 m wide and 51.4 m deep |
| Houses | Twenty, each three bays and about 6.8 m wide on the front |
| Storeys | Ground storey 4.4 m, then two storeys behind the columns. Cornice at 13.0 m, balustrade at 14.1 m, ridge at 15.9 m, chimney pots at 19.2 m |
| Order | 132 engaged Ionic columns, 7.2 m tall and 0.66 m across, one at every bay line on all four sides: 61 on the concave front. Each stands on a plinth block and carries a capital with two scrolls |
| Entablature | Architrave, frieze and a modillion cornice, then a balustrade with a pedestal over every column |
| Windows | One sash to a bay on each storey, with glazing bars: 1.95 m at street level, 2.35 m behind the columns with an iron guard, 1.70 m above |
| Doors | A six-panel door under a fanlight to each house on the front, a garden door to each on the convex side, and one at each end: 42 in all, each 35 mm above grade |
| Roof | Two slate ranges with a lead flat between them, behind lead gutters. A stone upstand and two stacks with seven pots at every party wall. Dormers behind the balustrade. Hipped ends |
| Railings | Spear-headed iron railings on a stone kerb round the building, opening at each door |
| Inside | Three floors, a spine wall and party walls to every house, so each window has a room behind it |

The model is 175,306 triangles in 12 flat-coloured parts, with no textures or
images. Nothing sits below grade.

## What it was measured from

Three reference images, locked by hash in `prework-manifest.json`:
`variant_0.png` (street), `variant_0_angle_60.jpg` (oblique) and
`variant_0_angle_90.jpg` (roof plan) under
`frontend/public/archetypes/buildings/london-crescent-terrace/`. None carries a
scale. Scale is set by the column at 7.2 m, and the other heights are measured
against it in the street view.

**The references disagree, and the roof plan shows a different building.** Each
disagreement is recorded in the manifest with the choice made:

- **Plan and length.** The roof plan shows about ten houses in a short block
  that is concave on both long sides. The street view and the oblique agree with
  each other on a long sweep of about twenty houses. Those two govern. The roof
  plan is used only for the character of the roof.
- **Column count.** The catalogue text says 114 columns. Counted on the oblique,
  the concave front has about sixty bays, so 61 columns stand there.
- **Catalogue plot.** The catalogue lists a 6 m by 12 m plot, one house. All
  three images show a whole crescent, so the whole crescent is built.
- **Window bars.** One large pane over another in the street view; small panes
  in the oblique. Built with small panes.
- **First-floor sash.** About 2.05 m in the street view and 2.4 m in the
  oblique. Built 2.35 m.
- **Columns on the convex side.** The oblique shows them. A real crescent of
  this kind has a plain back. Built as drawn.

**The three comparison cameras are approximate.** Because the images do not
agree on the plan, no camera registers the model exactly against the oblique or
the roof plan.

**Inferred, because no image shows it:** the far end, most of the convex side,
the interiors, and that the crescent is symmetrical. Bays on the convex side
widen from 2.7 m at the middle to 3.7 m toward the ends, because party walls
stand square to the front.

**Left out on purpose:**

- The sunken areas, their steps and the bridges to the doors. Nothing may lie
  below grade, so railings stand at grade and each door has a level stone path.
- Ashlar coursing and joints, as surface texture.
- The lead-covered additions between the roof ranges in the roof plan.
- People, cars, lawn, streets and neighbours, which belong to the site.

## Size

At 135 m by 51 m this is a large fixed-size building, and at 175,306 triangles
it sits just under the 180,000 that the building memory gives as the usual
ceiling. It needs a plot of at least 139 m by 55 m. It cannot be stretched, and
a shorter crescent would be a different candidate: `HOUSES` is one constant.

## Files

| File | Purpose |
|---|---|
| `build.py` | The building. Every dimension is a named constant at the top. It uses `clay_kit.py` from `tools/catalogue_plus15_concrete_pilot/` |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the exact GLB in headless Chromium |
| `boards.py` | Four 1080 x 1920 phone boards |
| `verify.py` | Delivery checks; writes `delivery-verification.json` |
| `test_crescent.py` | 17 tests, including that the generator still produces the recorded bytes, that every swept piece faces outward, that the roof covers the building and that no room reaches an outside face |
| `prework-manifest.json`, `candidate.json` | The measured contract and the candidate's hashes |
| `evidence/` | Builder review, delivery verification and independent reviews |
| `integration/runtime-review.md` | The runtime review template, filled in honestly: nothing was run. It lists all 42 doors |

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

1. A person looks at the renders and boards and accepts or rejects the model,
   knowing the differences listed above.
2. Local install and student trial, as `docs/BUILDING_CATALOGUE_WORKFLOW.md`
   describes. This needs the local database and storage, which the session that
   built the model did not have.
3. The runtime review in `integration/runtime-review.md`, row by row, in the
   running app. Which of the forty-two doors is the plot's entrance is undecided.
4. A recorded human approval, then `python -m tools.catalogue_promotion prepare`.

Each of those is a separate decision. Passing one does not grant the next.
