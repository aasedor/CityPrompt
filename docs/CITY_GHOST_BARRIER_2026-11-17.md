# City Ghost on a barrier for Add details

## Scope

Add two models of the City Ghost sculpture sitting astride a 3 m road barrier:
one on a plain concrete barrier, as on its concept sheet, and one on a barrier
painted pink, as it was installed. They extend `calgary-details-v1` (now 155
objects, IDs prefixed `detail-yyc-`) and sit in **Water & landmarks** beside the
existing public art sculpture. Searching `ghost` lists them.

| Item | W × D × H (m) | Triangles |
|---|---:|---:|
| City Ghost on a barrier | 3.0 × 0.7 × 2.1 | 2,938 |
| City Ghost on a pink barrier | 3.0 × 0.7 × 2.1 | 2,950 |

## The artwork belongs to its artist

City Ghost is a real sculpture, made for the painted barrier program. It was
modelled here on request from the program that built it. The design is the
artist's work, and nothing in this repository grants a right to use it. Before
this catalogue is published or merged for general use, the artist should agree
to the sculpture appearing in the product and be credited as they wish. The
material supplied did not name the artist, so no credit is given yet.

Until then the two items are easy to leave out: removing their two entries from
`SPECS` in `tools/detail_catalogue/build_calgary_details.py` and re-registering
drops them.

Like the [district barriers](DISTRICT_LOGO_BARRIERS_2026-11-17.md), this is a
deliberate exception to the kit's rule against reproducing real artworks. The
rule still holds for the murals, which remain original designs. The pink barrier
in the photograph carries the artist's hand-drawn characters in white; those
were not copied, so the pink barrier here is plain.

## What it was modelled from

Three images supplied by the program:

- a photograph of the installed sculpture at night, from the front, on a pink
  barrier;
- the concept sheet, with renders of the ghost on a grey barrier, the hat
  fastening, the eye cups and the design process;
- a photograph of the sculpture being lowered onto a barrier, from behind and
  to one side.

The concept sheet gives the height: the ghost "floats at just under 2 m tall"
and is "approximately a person's height". Every other dimension was measured
from the front photograph, using the barrier's 0.81 m height as the scale, so
they are estimates.

| Feature | In the images | In the model |
|---|---|---|
| Height | Head tops out just under 2 m; the hat sits above | Head at 1.94 m, hat to 2.07 m |
| Body | About 0.87 m wide, straight sides, a rounded head | 0.87 m wide and 0.66 m deep, with a slight flare toward the skirt |
| Skirt | Rounded lobes with sharp notches between, hanging about 0.3 m below the top of the barrier on both sides | Eight lobes, three across the front, down to 0.46 m above the ground |
| Eyes | Two tall oval cups set into the head, about 0.23 m by 0.68 m, 8 cm apart | Two cups 0.23 m by 0.67 m, 8 cm apart, 4.5 cm deep, a shade darker inside |
| Mouth | A small smile below the eyes | A crescent 0.24 m wide, a shade darker |
| Arms | A stubby teardrop on each side at mid height | An egg shape on each side, tilted out at the bottom |
| Hat | A tan cowboy hat, brim about 0.6 m wide and curled up at the sides, slightly askew | The same, turned and tilted a little |
| Colour | Blue, for the Blue Sky City branding | `#27a8d2` |
| Fit | A slot in the base drops over the top of the barrier | The body passes through the barrier, which gives the same look |

The depth of the body, the back, and the exact shape of the arms come from the
one photograph from behind, so they are the least certain.

## Method

`build_calgary_details.py` gained the ghost as plain geometry, in the kit's
convention: linear vertex colours, flat normals, one matte mesh, no textures.

- **Body.** One skin over 20 rings of a rounded section, 48 points to a ring.
  Rings are few on the straight sides and close together over the head.
- **Eyes.** A dent pressed into a regular grid has a ragged edge. So each eye
  is a block of the skin rebuilt around its oval: a rim from the block's edge to
  the oval, then the cup inside it. The oval has a clean edge and the cup is
  truly set into the head.
- **Skirt.** Two more rings whose height follows eight lobes, tucked under at
  the tips. Each lobe is six columns wide, so every notch falls on a column.
- **Smile, arms, hat.** The smile is a strip a few millimetres proud of the
  skin. The arms are egg shapes set into the sides. The hat is a brim that
  curls up at both sides, a band and a creased crown.

The sculpture has a satin finish; the model is matte like the rest of the kit.
The two models total 673,628 bytes and 5,888 triangles. The 153 earlier models
and their card images are byte-identical.

## Verification

- Rendered at eye level, oblique and card size, and compared with the three
  images ([sheet](calgary-details-v1/city-ghost-review.jpg)). Changed after the
  first review: the skirt's notches were falling between columns and read as
  shallow waves, so the skin was given six columns to a lobe; the hat was
  raised so the head no longer showed through its brim. Agent review passed;
  independent human visual acceptance, and the artist's own review, are open.
- Placed on the test street through the app's own placement code
  ([on a pink barrier](calgary-details-v1/scene-city-ghost-pink.jpg),
  [on a concrete barrier beside a boardwalk](calgary-details-v1/scene-city-ghost.jpg)).
  All 240 local models passed the datum, size and anchor checks.
- A tools test requires the head to top out between 1.9 m and 2.0 m, the skirt
  to hang below the top of the barrier, the body to be the same left and right,
  each eye to lie on the front of the head, and each description to say the
  artwork belongs to its artist. A frontend test checks the two names.
- In the real project page with a mocked backend, in a temporary browser trial
  that was not committed: both are found by searching `ghost`, load from their
  static card images without requesting a model file, and choosing one arms
  placement ([screenshot](calgary-details-v1/app-city-ghost.jpg)).
- The whole CI list was run locally: lint with zero warnings, dead-code and type
  checks; `npx vitest run` with 512 files and 4,542 tests passed; the 135
  catalogue delivery tests; the asset and manifest checks, with 5,989 required
  runtime files; tools, hosted-asset and backend detail tests with 240 local
  rows and 395 extras; and the browser tests, 13 passed plus the startup test,
  run one at a time as CI runs them.
- Production build with CI settings, then `check-budget`: 8,433.4 KB of
  8,448 KB.

Not done here: placing them on the live map, which needs a real map key, and
the full backend suite, which needs a database.
