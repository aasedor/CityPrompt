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

Seven of the ten reached PASS_ZERO_P0_P1, three of them in second passes the user reopened: the CBE
headquarters (cameras re-aimed), and the Halifax Public Gardens and Prince's Island Park with the shared
planting kit. The other three stopped with one to three P1s open and no P0.

| model | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| Road-diet complete street | road_diet_complete_street / variant_0 | `tools/clay_road_diet_complete_street` | **PASS_ZERO_P0_P1** at v003 | v003 | 86,810 | 3,189,736 | 0 / 0 |
| Toronto bay-and-gable house | toronto_bay_and_gable_house / variant_0 | `tools/clay_toronto_bay_and_gable` | **PASS_ZERO_P0_P1** at v004 | v004 | 17,326 | 911,108 | 0 / 0 |
| Old Montreal limestone commercial | old_montreal_limestone_commercial / variant_0 | `tools/clay_old_montreal_limestone_commercial` | **PASS_ZERO_P0_P1** at v004 | v004 | 66,776 | 3,423,736 | 0 / 0 |
| Inglewood main street | inglewood_main_street / variant_0 | `tools/clay_inglewood_main_street` | **PASS_ZERO_P0_P1** at v004 | v004 | 36,632 | 1,910,720 | 0 / 0 |
| Calgary Board of Education HQ | calgary_cbe_brutalist_hq / variant_0 | `tools/clay_calgary_cbe_brutalist_hq` | **PASS_ZERO_P0_P1** at v004 (second pass) | v004 | 35,078 | 1,717,448 | 0 / 0 |
| Halifax Public Gardens | halifax_public_gardens / variant_0 | `tools/clay_halifax_public_gardens` | **PASS_ZERO_P0_P1** at v005 (planting-kit second pass) | v005 | 1,587,314 rendered (instanced) | 4,126,476 | 0 / 0 |
| Prince's Island Park | calgary_princes_island / variant_0 | `tools/clay_princes_island_park` | **PASS_ZERO_P0_P1** at v005 (planting-kit second pass) | v005 | 4,022,316 rendered (instanced) | 4,184,552 | 0 / 0 |
| Toronto streetcar street | toronto_streetcar_street / variant_0 | `tools/clay_toronto_streetcar_street` | stopped: v003 and v004, then v005 and v006 in a second pass, did not lower v002's count | v002 | 53,836 | 2,795,968 | 0 / 1 |
| Market square | market_square / variant_0 | `tools/clay_market_square` | stopped: the tier-band finding survived two fixes | v004 | 59,968 | 3,239,284 | 0 / 2 |
| Vancouver Special | vancouver_special / variant_0 | `tools/clay_vancouver_special` | stopped: v002 and v003 did not lower v001's count | v001 | 32,456 | 1,865,808 | 0 / 3 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder. Every
candidate is under the 4 MiB ordinary-blob cap. Prince's Island Park, at 4,184,552 bytes, is the
closest. The planting-kit parks render several times more triangles than they store, because each plant
prototype is stored once and placed as glTF node instances.

### Trajectory (P0 / P1 per independent review)

| model | v001 | v002 | v003 | v004 | v005 | v006 |
|---|---|---|---|---|---|---|
| road-diet street | 0 / 6 | 0 / 1 | **0 / 0** | | | |
| bay-and-gable | 0 / 6 | 0 / 2 | 0 / 2 | **0 / 0** | | |
| Old Montreal | 0 / 2 | 0 / 2 | 0 / 1 | **0 / 0** | | |
| Inglewood | 0 / 5 | 0 / 1 | 0 / 1 | **0 / 0** | | |
| CBE HQ | 0 / 3 | 0 / 1 | 0 / 1 | **0 / 0** (second pass) | | |
| Halifax Public Gardens | 0 / 3 | 0 / 1 | 0 / 1 | 0 / 2 (second pass) | **0 / 0** | |
| Prince's Island Park | 0 / 5 | 0 / 2 | 0 / 1 | 0 / 4 (second pass) | **0 / 0** | |
| streetcar street | 0 / 4 | 0 / 1 | 0 / 2 | 0 / 1 | 0 / 1 (second pass) | 0 / 1 (stopped) |
| market square | 1 / 3 | 0 / 3 | 0 / 3 | 0 / 2 | 0 / 4 | |
| Vancouver Special | 0 / 3 | 0 / 3 | 0 / 3 | (stopped) | | |

## Open findings on the candidates that did not pass

Each family README lists the blockers of its last review, and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Calgary Board of Education HQ: passed at v004 in a second pass

- **Before:** v002 (0 / 1) was the candidate. Its glass sat too small and deep, so the east face read blank at
  oblique angles. v003 enlarged the glass to match the source head-on, but its front_corner camera looked almost
  along the east face.
- **Second pass:** the user reopened the family. v004 keeps the v003 geometry and re-aims front, front_corner and
  a new west_side camera to the locked views' angles.
- **Result:** PASS_ZERO_P0_P1 (P2 = 6). At the source oblique's angle every east-face cell shows a dark pane.

### Halifax Public Gardens and Prince's Island Park: passed at v005 with the shared planting kit

- **Before:** both stopped on close-up planting: the Halifax beds read as faceted gems, and Prince's Island read
  as cone heads, straw ribbons and bare fill.
- **The kit:** at the user's request, a shared planting kit was built and reviewed once in
  `tools/clay_planting_kit_showcase` (stopped at v003, 0 / 2: shrub bodies still show between leaves). It
  instances each plant prototype once, so dense beds fit the 4 MiB cap.
- **Second pass, Halifax Public Gardens:** v004 (kit plants) fixed the gem finding, but its review (0 / 2) found
  tube-like pink rims and sparse fill; v005 replaced the rims with dark mulch edges and filled the beds and the
  bandstand ring with white and mauve drifts. PASS_ZERO_P0_P1 (P2 = 11).
- **Second pass, Prince's Island Park:** v004 (kit drifts) fixed the primitive look, but its review (0 / 4)
  found bare margins, a thinned grove bed and black holes at paving joints, benches, doors and the footbridge
  (the holes present but unrecorded in v003); v005 fixed all four. PASS_ZERO_P0_P1 (P2 = 10), 9.7 KB under the
  cap.

### Toronto streetcar street v002 (0 / 1)

- **Open P1:** the cab noses read as vertical boxes with a flat cap.
- **What happened after v002:**
  - v003 fixed the rake and dome but opened a dark seam at the cab-to-roof junction and showed
    open-sided balconies;
  - v004 fixed both, but its review found black slots in the coping of the west Romanesque gable.
- **Second pass, reopened by the user:**
  - v005 rebuilt the gable coping as buried solid prisms and fixed it. Its review found a black stripe in the
    top view from a 1 m open gap between the west glass slab and the brick condominium wing.
  - v006 closed that gap, and the gaps around the slab's base and the west context block. Its review found a
    dark slot from a 0.6 m gap behind the east corner block.

  Both scored 0 / 1, so the stopping rule ended the family with v002 as the candidate.
- **Caveat for the user:** the v006 reviewer found that both the slab stripe and the east-block slot are already
  in v002's top render; neither was recorded in its review. Like for like, v006 is the most complete model. Closing
  the 0.6 m gap is a small fix if the user wants a v007 or prefers v006 as the candidate.

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

- **Planting was the systematic weak point, and a shared kit fixed it.** All three parks in this wave, and
  the green bridge in wave H, first stopped on close-up planting: faceted primitives at the segment counts
  the 4 MiB cap allows read as gems and cones at eye level. The shared planting kit
  (`tools/clay_planting_kit_showcase`) instances smooth-shaded prototypes (flower heads, arching grasses,
  leaf-card shrubs, groundcover, clipped carpet bands, wall drapes, pots) and checks every canopy against
  kerbs and obstacles. With it, both wave I parks and the wave G stepped plaza passed in their second passes.
  Its open weakness is shrubs (the body shows between leaves), so kit parks keep shrubs few and behind
  perennials; the green bridge has not yet been reworked with it.
- **Cameras decide findings.** The CBE east face and the Vancouver Special side wall were both
  geometry that matched the source but was judged through a camera that did not. The CBE passed in
  its second pass with only its cameras re-aimed. Matching the front and front_corner cameras to the
  locked views before v001 saves a version.
- **Open air gaps between volumes read as black stripes from above.** A 0.6 to 1 m gap between two
  blocks is in deep shadow in a nadir view. Butt or overlap neighbouring volumes, and check every
  version's top view for pixels below about 15% luminance; earlier reviews can miss these.
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
