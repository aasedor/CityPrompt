# Vancouver Laneway House: Garage Suite

RLASM 6.1 architectural clay for the exact variant
`vancouver_laneway_house` / `laneway_garden_studio` (variant 3, "Garage Suite",
catalogued until 2026-11-19 as "Garden Studio").
This is a **local pilot**. It is not in the catalogue, not seeded, and not
activated. Only a person can activate a clay delivery.

No model of this archetype existed before. The picker's "Infill homes" card
(`calgary_modern_infill_house`) has a variant described as a house with a
laneway suite, but its pictures show a rowhouse block, so it could not be built
from them. This variant's three pictures agree on one laneway house over a
garage, which is the type asked for.

Status of candidate **laneway-garden-studio-clay-v006**:

| Checkpoint | Status |
|---|---|
| Deterministic delivery checks | Pass, 77 checks. `evidence/delivery-verification.json` |
| Builder pixel review | Pass, with open notes. `evidence/builder-pixel-review.json` |
| Independent architectural-clay review | **Not done.** RLASM Gate G is open |
| Runtime integration | NOT REVIEWED. No part of it has been run. `integration/runtime-review.md` |
| Publication or activation | Not authorized |

Earlier candidates, none of which may be used:

- **v001.** The corner window was a box on the street face only, with a separate
  narrow window round the corner; the panel band was too narrow and too far back;
  the brick and roof colours were off; the balcony end was too tall; the downpipes
  were on the back wall.
- **v002.** Comparison cameras fitted to matched points left about 20 px RMS. The
  garage door, brick block and corner window were 0.3 to 0.45 m out, the eaves
  0.15 m too deep and the roof about 0.45 m too low.
- **v003.** The corner window's box ran along the lane face to the panel band,
  because the lane pane's height was read as its width. The brick had no coursing.
- **v004.** Went to independent review and was refused, with three P1 and ten P2
  findings. `evidence/independent-review-v004.json` holds that review:
  - the ridge was 0.7 m where both roof views show about 2 m;
  - the corner window's lane glass sat 0.33 m inside its box and read as a black
    return;
  - the lane ground window and the band slots were half to a third of their
    reference widths.
- **v005.** A rework of all three. The builder's own check found the lane glass
  still 0.145 m inside the box.

## The catalogue text described a different building

The variant was named **Garden Studio**, and its catalogue text described a
single storey with no garage, a dark fibre-cement skin and a green roof. All
three of its images show a two-storey laneway house over a double garage, in
brick and cedar under a hipped metal roof. RLASM lets the images govern, so the
model follows them.

**Ruled 2026-11-19:** a person decided that the images govern. The variant is
renamed **Garage Suite**, and its description, facade, roof and palette text in
`buildingArchetypes.json` now describe the house the images show. Its id,
`laneway_garden_studio`, is unchanged. The decision is recorded under
`human_decisions` in `integration/promotion.json`. Candidate v004's own build
records still carry the old title, because they were written before the ruling.

## What the building is

A two-storey laneway house of the kind Vancouver has allowed on back lanes since
2009, with its garage below and its home above. Calgary allows the same type as
a backyard suite over a garage.

| Part | Built as |
|---|---|
| Plan | Main volume 7.9 m wide and 8.6 m deep. The brick garage block, with the balcony on its roof, and the porch canopy stand 1.5 m in front of it. Over its eaves, apron and garden step the model is 9.04 m by 12.25 m |
| Storeys | Garage and entry at grade, the floor band at 2.85 to 3.25 m, the upper floor at 3.15 m, the wall plate at 5.78 m, the eaves at 6.0 m and the ridge at 7.83 m |
| Garage | A 14 by 8 ft sectional door, four lites in its top section, between brick piers with a wall lamp on each and a mailbox |
| Porch | A cedar entry wall with a glass door and sidelight under a flat canopy, a cedar post, and a concrete stoop of two risers: a lower step in front of the post and a landing level with the door at 0.34 m |
| Balcony | On the garage roof: a glass guard on dark posts with a dark top rail 1.09 m above the deck, returning at the porch end, and a solid cedar-clad end at the west |
| Upper storey | Cedar with a shadow line at every board. Four-panel sliding doors onto the balcony, and a corner window in a dark box that wraps onto the lane face |
| Lane face | The corner window's lane pane, and directly beneath it a ground-floor window as wide. Then a dark band of four vertical panels from grade to the soffit, standing proud of the cedar, with a 0.5 m slot window on each storey |
| Roof | Hipped, with a 2 m ridge front to back: side faces at 5 in 12, front and back faces steeper, about 26 degrees. Standing seams 0.43 m apart, hip and ridge caps, a dark fascia, a gutter round all four eaves, a cedar soffit and a downpipe at the back corner of each side |
| Back and west | Inferred: a glazed garden door with a step, a window to the back room and two upper windows at the back; one window on each storey on the west |
| Inside | A garage, a back room and an entry hall with a straight stair along the lane wall; upstairs a living room across the front and a bedroom and bath behind. Every window has a room behind it |

The model is 6,624 triangles in 17 flat-coloured parts, with no textures or
images. Nothing lies below grade.

## What it was measured from

Three reference images, locked by hash in `prework-manifest.json`:
`variant_3.png` (street), `variant_3_angle_60.jpg` (oblique) and
`variant_3_angle_90.jpg` (roof plan), under
`frontend/public/archetypes/buildings/vancouver-laneway-house/`. None carries a
scale. Scale is set by the garage door, taken as a 14 by 8 ft door.

The other proportions were checked by fitting one pinhole camera to each of the
street and oblique views, using 18 and 16 points that can be found in both the
image and the model. v002's fit left about 20 px RMS, with a consistent pattern
that showed which dimensions were wrong; v003 corrected them and brought it down
to 12.4 and 13.9 px. The roof plan is a perspective from above, so its match view
is fitted orthographically to the roof outline only.

Colours were sampled from the street view.

**Inferred, because no image shows it:** the back and west faces, the brick on
the west and back of the garage block, the west downpipe, and the interiors.

**Left out on purpose:** brick head joints (bed joints are modelled), people,
cars, planting, the lane, the street and neighbours.

## Files

| File | Purpose |
|---|---|
| `build.py` | The building. Every dimension is a named constant at the top. It uses `clay_kit.py` from `tools/catalogue_plus15_concrete_pilot/` |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the exact GLB in headless Chromium, 18 views; the three match cameras are fitted |
| `boards.py` | Four 1080 x 1920 phone boards |
| `verify.py` | Delivery checks, including that every whole view keeps the building in frame; writes `delivery-verification.json` |
| `test_laneway.py` | 15 tests: the generator still produces the recorded bytes; the ridge is 2 m and the side faces 5 in 12; the roof is one hipped sheet, lowest of its four planes everywhere; the lane windows match the corner pane and the slots are 0.5 m; seams stand on it; the corner box stops at its lane pane; no room surface stands in an opening; board and mortar lines never cross one; every opening has glass in its reveal; guard height; stair risers; downpipes; doors |
| `prework-manifest.json`, `candidate.json` | The measured contract and the candidate's hashes |
| `evidence/` | Builder review and delivery verification |
| `integration/runtime-review.md` | The runtime review template, filled in honestly: nothing was run |
| `integration/promotion.json` | An **unapproved** promotion package: identity, references, plot and picker text, with the approval and trial records left blank |

The GLB, renders and boards are review material and stay outside Git, under the
ignored `artifacts/` directory. **The GLB is reproducible:** the generator is
deterministic, and `candidate.json` records the SHA-256 it must produce.

## Reproduce

Needs Python 3.11 or later. Renders also need the frontend dependencies
installed and the repository served locally.

```bash
python3 tools/catalogue_laneway_house_pilot/build.py --output <new directory> --version <n>
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/catalogue_laneway_house_pilot/render.cjs <new directory>/<candidate>.glb <new directory>/renders
python3 tools/catalogue_laneway_house_pilot/boards.py <new directory>      # needs Pillow
python3 tools/catalogue_laneway_house_pilot/verify.py <new directory>
python3 -m pytest tools/catalogue_laneway_house_pilot
```

`build.py` refuses to write into an existing directory, and the render and board
scripts refuse to replace a file: RLASM never overwrites a candidate.

## Before this can be offered to students

1. An independent architectural-clay review with zero P0 and zero P1 findings
   (RLASM Gate G). The promotion tool's trial preflight refuses the package until
   that review is saved beside it as `independent-review.json`.
2. Done 2026-11-19: a person ruled on the variant's name and text. It is now
   Garage Suite.
3. A person looks at the renders and boards and accepts or rejects the model.
4. Local install and student trial, as `docs/BUILDING_CATALOGUE_WORKFLOW.md`
   describes, on a plot of at least 11 m by 14 m.
5. The runtime review in `integration/runtime-review.md`, row by row, in the
   running app.
6. A recorded human approval, then `python -m tools.catalogue_promotion prepare`.

`integration/promotion.json` is ready for those steps, in the `detached` group
(Low density), fixed native. Each step is a separate decision. Passing one does
not grant the next.
