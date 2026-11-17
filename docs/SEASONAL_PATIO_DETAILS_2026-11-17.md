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

## Added later the same day: boardwalk modules in feet, with steel railings

Six more pieces, built to requested module sizes in feet, each in red and in
black. The red set:

| Item | Size | Railings | W × D × H (m) | Triangles |
|---|---|---|---:|---:|
| Boardwalk module · 6 × 9 ft | 6 ft wide, 9 ft long | both long sides | 2.743 × 1.829 × 1.15 | 302 |
| Boardwalk module · 6 × 12 ft | 6 ft wide, 12 ft long | both long sides | 3.658 × 1.829 × 1.15 | 398 |
| Boardwalk corner · 6 × 6 ft | 6 ft square | two outer sides | 1.829 × 1.829 × 1.15 | 266 |
| Boardwalk corner · approach | 6 ft square | two outer sides, with hazard marker | 1.829 × 1.829 × 1.15 | 286 |
| Boardwalk module · 6 × 9 ft · road-side rail | 6 ft wide, 9 ft long | road side only | 2.743 × 1.829 × 1.15 | 182 |
| Boardwalk module · 6 × 12 ft · road-side rail | 6 ft wide, 12 ft long | road side only | 3.658 × 1.829 × 1.15 | 230 |

### Railing and deck

The railing and deck follow the boardwalk photographed on page 16 of the
guidelines, the one with red railings. What was taken from those photographs:

| In the photographs | In these models |
|---|---|
| Red welded steel panels with a square top rail and square end posts | 50 mm square top rail and stiles, top 1.0 m above the deck |
| Thin upright bars about a foot apart; five in the panel across the 6 ft end | Uprights at about 1 ft; five in a 6 ft panel |
| A solid band along the bottom of each panel | A 120 mm kick band 20 mm above the deck, which is also the cane-detectable edge |
| Two posts side by side where panels meet | A stile just inside each end, so joined modules and corners show paired stiles |
| Grey decking laid along the path of travel, with a metal seam at each joint | Grey boards laid lengthwise, a metal edge strip at each end and a metal frame below |
| Railing on the road side and across the end; the sidewalk side is open, with a metal threshold | The road-side-rail modules and the corner pieces, with a metal strip on the open edge |

The railing is a generic welded panel. It carries no lettering, logo or sign,
and the bicycle racks in the photographs were not copied.

### How they go together

- **Straight modules** are open at both ends, so they run on from one to the
  next. The standard module has a railing on both long sides. The road-side-rail
  module has one railing and is open to the sidewalk, as in the photographs,
  for a boardwalk that runs beside a patio fence.
- **Corner pieces** have railings on the road side and across the outer end,
  and are open toward the run and toward the sidewalk. One corner serves either
  end, because it is square: turn it a quarter to suit. The approach version
  adds a hazard marker on the end railing and goes at the end traffic reaches
  first.
- **Exact footprints.** Sizes are exact conversions (1 ft = 0.3048 m) and
  nothing overhangs the deck, so a run does not drift.
- The deck is 150 mm high, level with the sidewalk, and the top of the railing
  is 1.15 m above the street.

The first version of these modules, earlier the same day, had timber guards
like the metric sections above. It was replaced by this one on request. The
metric sections, patios and parklets keep their timber guards.

**Clear width to check.** A 6 ft module is 1.83 m wide. With railings on both
sides it has about 1.73 m clear between them; with a railing on the road side
only it has about 1.78 m to the open edge. The published guidance asks for a
2 m pedestrian detour, so these modules are narrower than that figure. They are
modelled to the requested size; the 2.5 m metric section above remains for a
2 m clear walkway.

Checked the same way as the rest:

- rendered at eye level, oblique and card size and reviewed
  ([sheet](calgary-details-v1/boardwalk-feet-review.jpg));
- placed on the test street through the app's own placement code. A 45 ft run
  of an approach corner, two 12 ft and one 9 ft road-side-rail modules and a
  turned far corner sits beside a sidewalk patio
  ([run](calgary-details-v1/scene-boardwalk-feet-run.jpg),
  [corner entrance](calgary-details-v1/scene-boardwalk-feet-corner.jpg),
  [walking along it](calgary-details-v1/scene-boardwalk-feet-walk.jpg)), and a
  second run with railings on both sides stands alone
  ([two-sided run](calgary-details-v1/scene-boardwalk-feet-short.jpg)). All 221
  local models passed the datum, size and anchor checks;
- a tools test requires the six footprints to be exact conversions, the
  height to be 1.15 m, a stile inside each end and no bay longer than 6 ft, and
  a frontend test checks the catalogue order and the sizes in feet;
- in the real project page with a mocked backend, in a temporary browser trial
  that was not committed: searching `boardwalk` in **Access & levels** lists all
  sixteen boardwalk pieces, the twelve new ones load from their static card images
  without requesting a model file, and choosing a road-side-rail module arms
  placement ([screenshot](calgary-details-v1/app-boardwalk-feet.jpg)).

### The same pieces with black railings

All six pieces also come with black steel railings, for streets where red does
not suit. They are the same models in another colour, so the sizes, the grey
deck and the way they join are identical, and a run should use one colour
throughout. Their names end in `· black`:

| Item | Railings |
|---|---|
| Boardwalk module · 6 × 9 ft · black | both long sides |
| Boardwalk module · 6 × 12 ft · black | both long sides |
| Boardwalk corner · 6 × 6 ft · black | two outer sides |
| Boardwalk corner · approach · black | two outer sides, with hazard marker |
| Boardwalk module · 6 × 9 ft · road-side rail · black | road side only |
| Boardwalk module · 6 × 12 ft · road-side rail · black | road side only |

They were rendered and reviewed
([sheet](calgary-details-v1/boardwalk-feet-black-review.jpg)) and placed on the
test street as a run beside a sidewalk patio
([run](calgary-details-v1/scene-boardwalk-feet-black-run.jpg),
[walking along it](calgary-details-v1/scene-boardwalk-feet-black-walk.jpg)).
A tools test requires each black piece to match its red counterpart in size and
triangle count while being a different file.

The kit is now 136 objects and the 130 earlier models, and their card images,
are byte-identical. The whole CI list was run again locally: lint with zero
warnings, dead-code and type checks; `npx vitest run` with 512 files and 4,542
tests passed; the 135 catalogue delivery tests; the asset and manifest checks,
with 5,951 required runtime files; tools, hosted-asset and backend detail tests
with 221 local rows and 376 extras; and the browser tests, 13 passed plus the
startup test. Not done here: placing these on the live map, which needs a real
map key, and the full backend suite, which needs a database.

## Bundle budget after this work

The eleven patio pieces left 5.3 KB of the 8,448 KB JavaScript budget. Before
adding the modules in feet, every packed catalogue was moved to the
shared-decoder transport, in its own commit, which freed 13.2 KB. A test now
walks the source tree and requires every packed catalogue to decode to its
exact source. With the twelve new rows the total is 8,430.9 KB, leaving 17.1 KB.

## Verification of the first eleven pieces

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
