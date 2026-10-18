# Wave F: five catalogue-gap buildings, report, 2026-10-18

Wave F added the five building types offered to replace the Beltline mid-rise slot, which duplicated
an existing model. All were built from their locked catalogue views on branch
`claude/ten-new-buildings`.

Every version followed the same process as waves D and E:

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

None had a model. The only near match was the Barcelona superblock open space, which is a different
category: a street network, not a building. Each family locks the three views of catalogue
`variant_0`.

Nothing here is enrolled, published or keeper-approved. Each README says `keeper_claimed=False` and
`runtime_seed_allowed=False`.

## Results

| building | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| Mid-century CMU distribution warehouse | mid_century_distribution_warehouse / variant_0 (cmu_dock_utilitarian) | `tools/clay_cmu_dock_warehouse` | **PASS_ZERO_P0_P1** at v006 | v006 | 20,340 | 1,115,380 | 0 / 0 |
| High-tech research laboratory | research_laboratory / variant_0 (high_tech_exoskeleton) | `tools/clay_exoskeleton_research_lab` | stopped: v004 and v005 did not lower v003's count | v003 | 18,732 | 1,007,100 | 0 / 3 |
| Campus lecture hall under a vault | campus_lecture_hall_complex / variant_0 (parametric_vaulted_pavilion) | `tools/clay_vaulted_lecture_hall` | stopped: the roof-mass and white-mass findings survived two fixes, and v003 did not lower the count | v003 (see below) | 23,190 | 1,210,444 | 0 / 6 |
| Steel and ETFE stadium bowl | outdoor_sports_stadium / variant_0 (contemporary_steel_etfe_bowl) | `tools/clay_etfe_truss_stadium` | stopped: the steel-joint finding survived two fixes | v003 | 63,087 | 2,906,576 | 0 / 6 |
| Sculptural white residential superblock | residential_superblock / variant_0 (parametric_sculptural_white) | `tools/clay_sculptural_superblock` | stopped: the tower-crown and cleft-edge findings survived two fixes | v003 | 60,970 | 2,801,576 | 1 / 6 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder. Every
candidate is under the 4 MiB ordinary-blob cap.

**Lecture hall candidate choice.** v002 has the lower combined count (1 P0 + 4 P1 = 5, against
v003's 0 + 6). It was not taken as the candidate because its P0 is a source-identity defect: the four
louvred roof masses do not read as a pinwheel. v003 carries no P0, so it stays the candidate. This
follows the call made for the terraced tower in wave E. It is recorded here and in the family README.

### Trajectory (P0 / P1 per independent review)

| building | v001 | v002 | v003 | v004 | v005 | v006 |
|---|---|---|---|---|---|---|
| warehouse | 0 / 9 | 0 / 3 | 0 / 2 | 1 / 2 | 0 / 1 | **0 / 0** |
| research lab | 1 / 8 | 0 / 4 | 0 / 3 | 0 / 6 | 0 / 4 | (stopped) |
| lecture hall | 2 / 8 | 1 / 4 | 0 / 6 | (stopped) | | |
| stadium | 1 / 10 | 1 / 6 | 0 / 6 | (stopped) | | |
| superblock | 2 / 12 | 1 / 8 | 1 / 6 | (stopped) | | |

## Open findings on the candidates that did not pass

Each family README lists these under "Open blockers after vNNN", and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Research laboratory v003 (0 / 3)

- **Open P1s:**
  - black blocks where the door portal's post meets its head, at the cantilever's north-west corner,
    and on the exoskeleton column tops;
  - a deep white band above the top floor, which hides the perforated roof screen in the front view;
  - from the front, the east louvres read as narrow recessed strips, and the steel is chunkier than
    the source.
- **What happened after v003:** v004 and v005 fixed all three. Their reviews then raised other
  elements:
  - roof plant scale and detail;
  - a cantilever about half the source depth;
  - the south-front bay rhythm at the south-east corner;
  - coloured services that read as a uniform plaid.

### Lecture hall v003 (0 / 6)

- **Survived two fixes (P1):**
  - the four louvred roof masses are too small, too little turned and mostly under the vault;
  - the white mass still reads as a flat box with shallow slots.
- **Other open P1s:**
  - the front view shows no dark louvred faces;
  - the louvre panels warp into the vault rim;
  - a black band runs along the soffit line;
  - the oblique cameras look from the south-east, but the source oblique is from the south-west.
- **Resolved along the way:**
  - the black interior;
  - the semicircular closed vault;
  - the flat cushions;
  - the squat base;
  - the node holes;
  - the kinked end ribs;
  - the blank vault soffit;
  - the short fin return.

### Stadium v003 (0 / 6)

- **Survived two fixes (P1):** black slits remain where the exposed diagonals cross and at the column
  feet.
- **Other open P1s:**
  - a ragged ETFE band end;
  - roof structure that does not read in the top view;
  - black holes behind the facade at the bowl corners;
  - stand undersides that read as planks with black slots;
  - a bowl that still reads hollow from above.
- **Resolved along the way:**
  - the front camera now catches the rounded south-west ETFE corner;
  - the pitch runs along the bowl's long axis;
  - the cushions are soft 2.2:1 domes on an outward-bowing band;
  - the facade has steep full-height diagonals;
  - the perimeter truss has single alternating diagonals.

### Superblock v003 (1 / 6)

- **Survived two fixes (P0):** the tower crown is a ring around a closed roof cap, not the source's
  open loop.
- **Survived two fixes (P1):** stair-stepped band ends and pier stubs remain along the south cleft.
- **Other open P1s:**
  - the tower reads as a coil spring rather than many steep blades;
  - the dip is still a pointed V;
  - there are blank funnel surfaces in the cleft;
  - the retail piers read as a row of wedges;
  - there is one roof trench, not an S-band with skylights;
  - the court reads as a rounded rectangle from above.
- **Resolved along the way:**
  - the east wing is at full height;
  - the street faces have punched windows;
  - the balconies have glass balustrades;
  - the roof streaks are gone;
  - the tower now has spiralling ribbons inside the building line;
  - the retail arches are smooth.

## What carried over between buildings

These fixes recurred across buildings and are worth reusing:

- **Black faces are coplanar faces, every time.** Wave F added these causes:
  - the corner posts of a screen drawn twice, once by each run;
  - the overlapping V-legs of a piloti;
  - a portal head and posts sharing a front plane;
  - column tops level with a ring beam;
  - glass walls whose top met the roof slab's top;
  - crossing mullion and transom boxes with the same front face;
  - a fin screen whose fins were rotated so neighbours overlapped.

  The fix was to butt, offset or cap one part. Recolouring never helped.
- **Gaps read as black too.** A 2 cm gap between a soffit and a slab, or under a carrier at a
  corner, renders as a black hairline. Bed one part into the other instead.
- **Swept members.** Arch ribs and long curved bands built from straight box segments kink and leave
  black wedges at each joint. Loft them as one continuous swept section along the surface normal.
- **Match the camera to the source first.** Mirrored or distant cameras cost the warehouse, lab,
  lecture hall and stadium a version each. Check the locked front and oblique for the viewing corner,
  eye height, horizon height and frame fill before the first full build.
- **Size budget.** GLB size tracks vertex count (positions and normals), not triangles: count bytes
  from the buffer views. The stadium's facade lattice and cushion field fit under the cap once the
  frame lines were drawn as flat quads.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under
4 MiB. Superseded candidate GLBs were removed from tracking as each new candidate replaced them.
Untracked local copies were pruned from the `candidates/` folders.
