# Seasonal patio pieces for Add details: boardwalk sections, on-street patios and parklets

## Scope

Add eleven fixed-size items for scenes that show a seasonal patio on a street:
modular boardwalk sections for the parking lane, complete on-street patios and
parklets in one and two parking stalls, a sidewalk patio, a free-standing guard
panel and a low-profile traffic barrier. They extend `calgary-details-v1` (now
124 objects, IDs prefixed `detail-yyc-`). They pair with the
[painted road barriers](MURAL_BARRIERS_2026-11-17.md), which protect the
road end of a patio.

## Source for the dimensions

The dimensions follow the City of Calgary's published guidance, read on
2026-11-17:

- the seasonal patio page, `calgary.ca/roads/permits/seasonal-patio.html`;
- *Guidelines for Seasonal Patios located on public property*, linked from it.

That guidance describes three patio styles: a patio on part of a sidewalk, a
patio in the curbside parking lane, and a patio on the sidewalk with a
pedestrian detour built in the parking lane, which it calls a boardwalk. The
points these models take from it:

| Requirement in the guidance | In these models |
|---|---|
| Platform floor at sidewalk grade, level with the curb | Every deck is 150 mm high, with a metal transition strip at the curb |
| Pedestrian detour at least 2 m wide; 2.3 m recommended | Boardwalk sections are 2.5 m wide with 2.3 m clear inside the guard |
| Guard 1 m to 1.2 m high between patio and road, and never more than 1.2 m above the street; 1 m preferred | Guard is 1.0 m, so its handrail is 1.19 m above the street |
| A fixed, continuous cane-detectable edge within 100 mm of the ground | A bottom rail 40 mm above the walking surface on every guard |
| Supports must not project into the walkway; nothing drilled into the road or sidewalk | Free-standing guards have weighted feet that reach to the patio side only |
| A hazard marker on the corner facing approaching traffic; reflective tape along the fencing | Yellow and black marker on the approach corner, mounted under the handrail; a yellow strip on the road face |
| Umbrella canopies at least 2.1 m above the walking surface, weighted, not fixed to railings | Free-standing umbrellas on weighted bases, canopy edge at 2.13 m, kept inside the platform |
| Planters no taller than 1.2 m above the street | Planter and plant together are about 0.95 m above the deck |
| Barrier-free entrance; the sample drawing shows a 2 m opening | On-street patios have a 2 m opening on the sidewalk side |
| Sample curbside patio: 11 m long with 16 seats | The two-stall patio is 11 m long with four tables and sixteen seats |
| Low-profile barriers and planters at the ends | A low-profile barrier item, and the painted and plain barriers |

The guidance also says the floor must be within 6 mm of the sidewalk, which it
glosses as no ramps, so no ramp section was made. The catalogue already has an
accessible ramp and a tactile curb ramp for other uses.

**These are concept models for site visualization.** They are not permit
drawings, and a real patio needs the City's review, including spacing from
hydrants, intersections, bus stops and utilities that a model cannot check.
The catalogue text names no program and carries no City wording or logo.

## Duplicate scan

Before building, the existing catalogue was searched for parklets, patios,
boardwalks, decks, cafe furniture, umbrellas, planters, railings, ramps and
barriers. It already has three generic parklet modules, a cafe table set, a
cafe parasol, a cafe windbreak barrier, a street planter box and a boardwalk
railing. So this set does **not** add a loose table, umbrella or planter. It
adds what was missing: sidewalk-grade platforms, a guard built to the cane and
height rules, complete patios, and the low-profile barrier.

## New choices

| Item | Category | W × D × H (m) | Triangles |
|---|---|---:|---:|
| Boardwalk section | Access & levels | 3.0 × 2.5 × 1.2 | 158 |
| Boardwalk section · 1.5 m | Access & levels | 1.5 × 2.5 × 1.2 | 124 |
| Boardwalk end · approach | Access & levels | 3.0 × 2.5 × 1.2 | 298 |
| Boardwalk end · far | Access & levels | 3.0 × 2.5 × 1.2 | 266 |
| On-street patio · one stall | Seating | 6.0 × 2.5 × 2.8 | 1,660 |
| On-street patio · two stalls | Seating | 11.0 × 2.5 × 2.8 | 2,582 |
| Parklet · one stall | Seating | 6.0 × 2.5 × 2.8 | 1,382 |
| Parklet · two stalls | Seating | 11.0 × 2.5 × 2.8 | 1,788 |
| Sidewalk patio | Seating | 6.1 × 2.3 × 2.6 | 1,572 |
| Patio guard panel | Edges & gates | 2.4 × 0.5 × 1.0 | 96 |
| Low-profile barrier | Traffic & safety | 3.0 × 0.6 × 0.5 | 120 |

## How the pieces go together

Every platform has its guard on the road side and is open toward the sidewalk,
so it is placed in the parking lane with its open edge on the curb.

- **Boardwalk detour:** an approach end, as many sections as needed, and a far
  end. The sections are exactly 3.0 × 2.5 m and their posts never sit at a
  joint, so the guard runs through. The approach end carries the hazard marker
  and belongs at the end that traffic in the next lane reaches first.
- **On-street patio and parklet:** one item each, sized to one or two parking
  stalls. The patios are fenced on all four sides with a 2 m entrance; the
  parklets are open to the sidewalk, with built-in benches and no table service.
- **Sidewalk patio:** placed on the sidewalk itself, open toward the building.
  Leave 2 m of clear walkway beside it, or use a boardwalk detour.
- **Barriers:** put a low-profile, plain or painted barrier across the parking
  lane at the approach end.

## Method

`tools/detail_catalogue/build_calgary_details.py` gained a plank deck, a guard
run, a hazard marker, a cafe chair and table set, a weighted umbrella, a box
planter and a built-in bench, and the eleven items are assembled from those.
The files follow the kit convention: linear vertex colours, flat normals, one
matte mesh, no textures. The eleven total 1,157,768 bytes and 10,046 triangles.
The 113 earlier models are byte-identical.

## Verification

- Every item was rendered at eye level, oblique and card size and reviewed:
  [eye level](calgary-details-v1/patio-eye-level.jpg),
  [oblique](calgary-details-v1/patio-oblique.jpg),
  [catalogue cards](calgary-details-v1/patio-cards.jpg). Changed after review:
  umbrellas shrunk and moved so no canopy overhangs the road or the walkway;
  the hazard marker lowered under the handrail so the corner stays below 1.2 m
  above the street, and moved inside the platform edge so sections butt
  exactly; guard feet turned to the patio side. Agent review passed;
  independent human visual acceptance is open.
- A frontend test requires the four boardwalk pieces to share the 2.5 m width,
  to stay at or under 1.2 m high, and the patios and parklets to measure exactly
  6 × 2.5 m and 11 × 2.5 m.
- Tools pytest: the kit rebuilds all 124 objects to byte-identical registry
  rows with a hash-locked card each.
- The whole CI list was run locally: lint with zero warnings, dead-code and
  type checks; `npx vitest run` with 512 files and 4,542 tests passed; the 134
  catalogue delivery tests; the asset and manifest checks; hosted-asset tests
  for all 209 local rows; backend detail tests with 364 extras; the repository
  blob policy; and the browser tests, 13 passed plus the startup test. The full
  backend suite needs a database and was not run here.
- Runtime asset manifest regenerated: 5,927 required files (+22).
- Production build with CI settings, then `check-budget`: 8,442.7 KB of
  8,448 KB.

### Fit, checked in a street scene

A temporary harness ran all 209 local models through the app's real
`detailCatalogue.ts`, `detailThumbnail.ts` and `detailInstances.ts`; all passed
the datum, size and anchor checks. It then placed the patio pieces on a test
street with a 150 mm curb, a 2.5 m parking lane and a 3 m sidewalk:

- [boardwalk detour beside a sidewalk patio](calgary-details-v1/scene-patio-boardwalk-detour.jpg):
  a far end, three sections and an approach end form one 15 m walkway whose
  deck meets the sidewalk level and whose guard runs through without a break;
- [on-street patio in two stalls](calgary-details-v1/scene-patio-on-street.jpg),
  with painted barriers across the lane at both ends;
- [parklet and a one-stall patio](calgary-details-v1/scene-patio-parklet.jpg);
- [the whole street](calgary-details-v1/scene-patio-street.jpg).

The harness was not committed.

### The real project page, with a mocked backend

A temporary browser trial of **Add details**, not committed: all eleven patio
pieces and all eight painted barriers are found by name, each card loads from
its static image, and browsing requested no model files. Searching
[`stall` in Seating](calgary-details-v1/app-patio-stalls.jpg) lists the two
patios and two parklets, and
[`mural barrier`](calgary-details-v1/app-mural-barriers.jpg) lists the eight
painted barriers. Choosing the two-stall patio arms placement.

Not done here: placing these on the live map, which needs a real map key. On a
real street the platform should be checked against the actual curb height and
road cross-fall, since every deck here is a fixed 150 mm.
