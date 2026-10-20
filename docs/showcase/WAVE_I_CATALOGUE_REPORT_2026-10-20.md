# Wave I: ten catalogue additions, report, 2026-10-20

Wave I built the ten types recommended to the user and approved with "Perfect. Please proceed.":

- **Buildings (4):** the Vancouver Special, the Toronto bay-and-gable house, the Calgary Board of
  Education brutalist headquarters and an Old Montreal limestone commercial building.
- **Parks and squares (3):** Prince's Island Park, the Halifax Public Gardens and a market square.
- **Streets (3):** Inglewood main street, a road-diet complete street and a Toronto streetcar street.

Each family locks the three views (front, oblique, top) of catalogue `variant_0`. All work is on
branch `claude/ten-new-buildings`.

Every version followed the RLASM v6.1 process used since wave D:

- **Build:** rendered from the actual optimised GLB, 18 views at 1440 px and 32 samples.
- **Review:** reviewed by a separate agent that had not built it.
- **Evidence:** preserved as JPEG evidence in `tools/<family>/evidence/<version>/`.

Each family then went through the stopping rule in `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`.
A family stops at the first of these:

- the review returns PASS_ZERO_P0_P1;
- two consecutive reviews fail to lower P0 + P1;
- the same finding survives two targeted fixes.

The best-reviewed version stays the candidate, and a tie keeps the earlier version.

Nothing here is enrolled, published, runtime-integrated or keeper-approved. Each README states that nothing in the family is keeper-approved, runtime-integrated, enrolled in a catalogue or activated, and that those remain separate checkpoints for the user's decision.

## Results

Four of the ten reached PASS_ZERO_P0_P1. The other six stopped with one to three P1s open and no
P0.

| model | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| Road-diet complete street | road_diet_complete_street / variant_0 | `tools/clay_road_diet_complete_street` | **PASS_ZERO_P0_P1** at v003 | v003 | 86,810 | 3,189,736 | 0 / 0 |
| Toronto bay-and-gable house | toronto_bay_and_gable_house / variant_0 | `tools/clay_toronto_bay_and_gable` | **PASS_ZERO_P0_P1** at v004 | v004 | 17,326 | 911,108 | 0 / 0 |
| Old Montreal limestone commercial | old_montreal_limestone_commercial / variant_0 | `tools/clay_old_montreal_limestone_commercial` | **PASS_ZERO_P0_P1** at v004 | v004 | 66,776 | 3,423,736 | 0 / 0 |
| Inglewood main street | inglewood_main_street / variant_0 | `tools/clay_inglewood_main_street` | **PASS_ZERO_P0_P1** at v004 | v004 | 36,632 | 1,910,720 | 0 / 0 |
| Calgary Board of Education HQ | calgary_cbe_brutalist_hq / variant_0 | `tools/clay_calgary_cbe_brutalist_hq` | stopped: the facade-glazing finding survived two fixes | v002 | 35,750 | 1,752,132 | 0 / 1 |
| Halifax Public Gardens | halifax_public_gardens / variant_0 | `tools/clay_halifax_public_gardens` | stopped: the bed-plant finding survived two fixes | v002 | 63,266 | 3,852,788 | 0 / 1 |
| Prince's Island Park | calgary_princes_island / variant_0 | `tools/clay_princes_island_park` | stopped: the close-up planting finding survived two fixes | v003 | 141,252 | 4,045,264 | 0 / 1 |
| Toronto streetcar street | toronto_streetcar_street / variant_0 | `tools/clay_toronto_streetcar_street` | stopped: v003 and v004 did not lower v002's count | v002 | 53,836 | 2,795,968 | 0 / 1 |
| Market square | market_square / variant_0 | `tools/clay_market_square` | stopped: the tier-band finding survived two fixes | v004 | 59,968 | 3,239,284 | 0 / 2 |
| Vancouver Special | vancouver_special / variant_0 | `tools/clay_vancouver_special` | stopped: v002 and v003 did not lower v001's count | v001 | 32,456 | 1,865,808 | 0 / 3 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder. Every
candidate is under the 4 MiB ordinary-blob cap. Prince's Island Park, at 4,045,264 bytes, is the
closest.

### Trajectory (P0 / P1 per independent review)

| model | v001 | v002 | v003 | v004 | v005 |
|---|---|---|---|---|---|
| road-diet street | 0 / 6 | 0 / 1 | **0 / 0** | | |
| bay-and-gable | 0 / 6 | 0 / 2 | 0 / 2 | **0 / 0** | |
| Old Montreal | 0 / 2 | 0 / 2 | 0 / 1 | **0 / 0** | |
| Inglewood | 0 / 5 | 0 / 1 | 0 / 1 | **0 / 0** | |
| CBE HQ | 0 / 3 | 0 / 1 | 0 / 1 | (stopped) | |
| Halifax Public Gardens | 0 / 3 | 0 / 1 | 0 / 1 | (stopped) | |
| Prince's Island Park | 0 / 5 | 0 / 2 | 0 / 1 | (stopped) | |
| streetcar street | 0 / 4 | 0 / 1 | 0 / 2 | 0 / 1 | (stopped) |
| market square | 1 / 3 | 0 / 3 | 0 / 3 | 0 / 2 | 0 / 4 |
| Vancouver Special | 0 / 3 | 0 / 3 | 0 / 3 | (stopped) | |

## Open findings on the candidates that did not pass

Each family README lists the blockers of its last review, and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Calgary Board of Education HQ v002 (0 / 1)

- **Open P1:** the glass sits too small and too deep in the coffers, so the east face reads blank at
  oblique angles.
- **What happened in v003:** v003 enlarged the glass to about 0.68 of the bay, which matches the
  source head-on. But the front_corner camera looks almost along the east face, so the reviewer
  still saw no panes there.
- **Likely fix:** re-aim front_corner to the source oblique's angle. The geometry is now close to the
  source; the camera is not.

### Halifax Public Gardens v002 (0 / 1)

- **Open P1:** the carpet-bed, ring-bed and strip-bed plants read as faceted gems.
- **What happened in v003:** v003 replaced them with small grounded heads in colour bands. At six
  segments, needed to stay under the size cap, the heads still show hard outlines up close.

### Prince's Island Park v003 (0 / 1)

- **Open P1:** at eye level the planting still reads as primitives: faceted cone flower heads, flat
  straw-ribbon grasses and bare fill between the mounds.
- **What does read correctly:** the planting from the air, the sett paving, the sedum roof, the open
  railings, the wooded far bank and the clear boardwalk.

### Toronto streetcar street v002 (0 / 1)

- **Open P1:** the cab noses read as vertical boxes with a flat cap.
- **What happened after v002:**
  - v003 fixed the rake and dome but opened a dark seam at the cab-to-roof junction and showed
    open-sided balconies;
  - v004 fixed both, but its review found black slots in the coping of the west Romanesque gable.

  Neither beat v002.
- **Likely next step:** v004 is the most complete model, so a v005 that only closes the gable
  coping would probably pass.

### Market square v004 (0 / 2)

- **Open P1s:**
  - the top tier's line reverses its bend into a shallow W;
  - the band-to-walk proportion is inverted, with pale walks wider than the stone seat bands.
- **What happened in v005:** v005 fixed the plan and the proportion in geometry. Its review then
  found:
  - treads and walks so close in value that the bowl still reads as one pale flight;
  - flower beds raised on plateaus behind sheer walls;
  - the stage's side steps missing;
  - step ends overrunning the bed walls.

### Vancouver Special v001 (0 / 3)

- **Open P1s:**
  - black faces on the trim;
  - unresolved rake-to-eave roof corners;
  - side-street window spacing that does not match the sources.
- **What happened after v001:** v002 and v003 fixed all three, but each review raised three new
  P1s:
  - v002: a slot along the front rake, pits at the mortar T-junctions and the front camera;
  - v003: roof pitch, roof value and a slit at a downpipe outlet.

  So the count never went below v001's three.

## What carried over

- **Planting is the systematic weak point.** All three parks in this wave, and the green bridge in
  wave H, stopped on close-up planting. The cause is not effort: faceted primitives at the
  segment counts the 4 MiB cap allows read as gems and cones at eye level. The next park should not
  start until there is one shared planting kit, reviewed once and reused by every family. It needs:
  - smooth-shaded flower heads with real curvature;
  - arching blade grasses;
  - shrub masses built from overlapping lobes;
  - a groundcover layer that hides bare fill.

  `docs/HIGH_QUALITY_3D_PARK_MEMORY.md` should record this.
- **Cameras decide findings.** The CBE east face and the Vancouver Special side wall were both
  geometry that matched the source but was judged through a camera that did not. Matching the
  front and front_corner cameras to the locked views before v001 saves a version.
- **Black slots move rather than disappear.** Inglewood, the Vancouver Special and the streetcar each
  fixed one black slot and revealed another:
  - a pier base short of its neighbour;
  - a fascia sitting inside the soffit;
  - a coping not mitred into its cornice.

  A per-build sweep of every junction where two members meet would catch these before review.
- **Brief wording must follow the pixels.** The Old Montreal brief described the pavilion as the model
  built it rather than as the sources showed it. Once the brief was corrected the family passed.
- **Overshoot is common on proportion fixes.** The market square went from walks too narrow, to
  walks too wide, to bands right but unreadable. Measured targets taken from the source pixels
  worked better than relative instructions.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under
4 MiB. Superseded candidate GLBs were removed from tracking as each new candidate replaced them.
