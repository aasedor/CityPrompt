# Waves D and E: catalogue-gap buildings and three residential towers, report, 2026-10-16

Wave D filled five gaps in the catalogue: building types with no clay, runtime or seed-library
model. Wave E added three residential towers, because the catalogue had only one. All were built
from their locked catalogue views on branch `claude/ten-new-buildings`.

Every version followed the same process:

- **Build:** rendered from the actual optimised GLB, 18 views at 1440 px and 32 samples.
- **Review:** reviewed by a separate agent that had not built it.
- **Evidence:** preserved as JPEG evidence in `tools/<family>/evidence/<version>/`.

Each building then went through the stopping rule in `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`.
A building stops at the first of these:

- the review returns PASS_ZERO_P0_P1;
- two consecutive reviews fail to lower P0 + P1;
- the same finding survives two targeted fixes.

The best-reviewed version stays the candidate, and a tie keeps the earlier version.

Before building, each type was checked against these sources to make sure it was not already modelled:

- the RLASM seed library;
- the model library;
- the runtime families;
- the clay `sources.json` files;
- the object list on `origin/main`.

Nothing here is enrolled, published or keeper-approved. Each README says `keeper_claimed=False` and
`runtime_seed_allowed=False`.

## Results

| building | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| Downtown elevated CTrain station | calgary_ctrain_station / variant_0 | `tools/clay_ctrain_elevated_station` | **PASS_ZERO_P0_P1** at v004 | v004 | 20,602 | 1,094,572 | 0 / 0 |
| Garden-court senior residence | senior_living_complex / variant_0 | `tools/clay_garden_court_senior_residence` | **PASS_ZERO_P0_P1** at v006 | v006 | 77,642 | 4,030,900 | 0 / 0 |
| Brick campus parking structure | campus_parking_structure / variant_0 | `tools/clay_brick_parkade` | stopped: the south-face opening finding survived two fixes | v003 | 20,842 | 1,117,916 | 0 / 1 |
| Braced-frame regional hospital | regional_hospital_medical_center / variant_0 | `tools/clay_braced_frame_hospital` | stopped: v004 and v005 did not lower v003's count | v003 | 78,760 | 4,184,528 | 0 / 1 |
| Student residence tower | student_residence_tower / variant_0 | `tools/clay_student_residence_tower` | stopped: the roof-garden finding survived two fixes | v002 (tie with v003, the earlier version kept) | 46,258 | 3,001,876 | 0 / 4 |
| New York pre-war apartment tower | new_york_pre_war_apartment / variant_0 | `tools/clay_prewar_apartment_tower` | stopped: the cornice-corner and south-east corner findings survived two fixes | v003 | 80,512 | 4,161,296 | 0 / 3 |
| Terraced stepped tower | terraced_stepped_building / variant_0 | `tools/clay_terraced_stepped_tower` | stopped: the terrace and court planting findings survived two fixes | v001 (see below) | 77,666 | 4,124,608 | 0 / 5 |
| Beltline brick mid-rise | (Beltline mid-rise variant) | `tools/clay_beltline_brick_midrise` | stopped after v001: the archetype already has a model | v001 | 24,164 | 1,292,372 | 1 / 4 |

The candidate GLB of each family is the only file in its `candidates/` folder. Every candidate is
under the 4 MiB ordinary-blob cap.

The Vancouverism point tower was dropped before it was built, because the catalogue already has an
exact model of it. The student residence tower replaced it. The Beltline mid-rise still needs a
replacement building type. Five suggestions are offered, and the user has not yet chosen:

- residential superblock;
- campus lecture hall;
- research lab;
- outdoor stadium;
- mid-century distribution warehouse.

**Terraced tower candidate choice.** v003 has the lowest combined count (2 P0 + 2 P1 = 4, against
v001's 0 + 5). It was not taken as the candidate because both of its P0s are blocking. One is an
interior camera that cannot see out. The other is an envelope change that its own fix introduced.
v001 carries no P0, so it stays the candidate. This is a judgement call, recorded here and in the
family README.

### Trajectory (P0 / P1 per independent review)

| building | v001 | v002 | v003 | v004 | v005 | v006 |
|---|---|---|---|---|---|---|
| CTrain station | 1 / 6 | 0 / 4 | 0 / 1 | **0 / 0** | | |
| senior residence | 3 / 5 | 0 / 4 | 0 / 2 | 0 / 2 | 0 / 1 | **0 / 0** |
| parking structure | 0 / 6 | 0 / 2 | 0 / 1 | (stopped) | | |
| hospital | 0 / 6 | 0 / 3 | 0 / 1 | 0 / 1 | 0 / 3 | (stopped) |
| student tower | 1 / 8 | 0 / 4 | 0 / 4 | (stopped) | | |
| pre-war tower | 0 / 5 | 0 / 5 | 0 / 3 | (stopped) | | |
| terraced tower | 0 / 5 | 1 / 5 | 2 / 2 | (stopped) | | |
| Beltline mid-rise | 1 / 4 | (stopped: duplicate) | | | | |

## Open findings on the candidates that did not pass

Each family README lists these under "Open blockers after vNNN", and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Parking structure v003 (0 / 1)

- **Open P1:** the south open-deck zone still reads as three stacked per-deck openings, with brick
  bands between the decks and upstands that stand proud. The source shows one brick-framed void
  across decks 2 to 4, under a brick header, with the upstands set back inside it.
- **What was tried:**
  - v002 removed the extra piers;
  - v003 made one wide opening per deck, with recessed columns and pale upstands.

### Hospital v003 (0 / 1)

- **Open P1:** several entrance-canopy hanger rods end on non-structural surfaces.
- **What happened after v003:**
  - v004 anchored the rods on structure, but its review raised the diagonal net that runs across the
    entrance.
  - v005 gave the entrance a vertical-mullion storefront with revolving doors. Its review then raised
    three further elements:
    - the exoskeleton bay rhythm is about twice too fine;
    - the atrium is about two storeys too tall and about 30% too narrow;
    - the frame columns run across the base windows.

### Student residence tower v002 (0 / 4)

The v001 P0 is resolved: the white west-face blade, which leans, widens and rises above the roof. The
open findings are:

- the roof dome, which should be oval with a geodesic net on a storey-high glazed drum;
- the penthouse, which should be a full storey;
- the lattice screen, which should be 1 to 1.5 storeys of triangulated panels;
- the terraces, which should be recessed balconies with set-back glass and white returns.

v003 corrected the plan proportion, the cameras and the roof beds. It did not get past these four.

### Pre-war apartment tower v003 (0 / 3)

v003 moved the entrance group to the south-east corner and closed the cornice gaps with corner
blocks. Its review found three things wrong with those fixes:

- the corner bays became solid limestone piers;
- small stone pieces collide in the corner notch;
- the cornice corner blocks are oversized.

Before that, the tank house, pyramid roof, catwalk, balcony rails and marquee camera had all been
fixed.

### Terraced stepped tower v001 (0 / 5)

The candidate's open findings are:

- the east raking element;
- the court-facing balconies;
- the ground colonnade;
- the birch court;
- the terrace planting.

v002 fixed the raking wall, the balconies and the colonnade. v003 fixed the window rhythm, the
charcoal tone and the plan depth. Both versions still fell short on the terrace and court planting.
They also opened new P0s: the interior camera, and the slab's raked west-face shoulder.

## What carried over between buildings

These fixes recurred across buildings and are worth reusing:

- **Black faces.** Coplanar overlapping faces render pure black. Every black bar, slit, diamond and
  band found here had that cause. Examples:
  - coincident corner columns;
  - a soffit on the roof shell's eave face;
  - a water-table end on the next carrier's face;
  - two edge beams on one line.

  The fix is always to butt, inset or offset one of the parts. Recolouring does not fix it.
- **Shared corners.** When two faces share a corner, draw the corner column, quoin or band once. Let
  the other face stop inside it.
- **Hero cameras.** Hero views matched to street-level sources should be fixed cameras: set
  `whole=False` with a lens near the source's. Auto-fit pushes a whole-envelope camera back to a
  distant overview, or off the building entirely.
- **Size budget.** The 4 MiB cap is reached by planting long before architecture. Multi-trunk small
  trees and four-crown shrubs cost the most. Use soft ellipsoid masses for grasses and underplanting
  to stay within budget.
