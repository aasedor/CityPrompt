# Wave G: ten catalogue additions and the Calgary RiverWalk, report, 2026-10-20

Wave G built ten more catalogue types the user approved: eight buildings and two open spaces. It
also built the Calgary RiverWalk as a street option, which the user asked for afterwards. Each
family locks the three views (front, oblique, top) of one catalogue variant. All work is on branch
`claude/ten-new-buildings`.

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

Nothing here is enrolled, published, runtime-integrated or keeper-approved. Each README says
`keeper_claimed=False` and `runtime_seed_allowed=False`.

## Results

Four of the eleven reached PASS_ZERO_P0_P1. The other seven stopped with one to five P1s open and
no P0.

| model | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| London mews coach house | london_mews_house / london-mews-house-original-stable | `tools/clay_mews_coach_house` | **PASS_ZERO_P0_P1** at v006 | v006 | 49,888 | 2,708,724 | 0 / 0 |
| Halifax waterfront stone warehouse | halifax_waterfront_warehouse / warehouse_privateers_wharf | `tools/clay_halifax_waterfront_warehouse` | **PASS_ZERO_P0_P1** at v006 | v006 | 16,521 | 845,444 | 0 / 0 |
| Outdoor ice rink in a market square | outdoor_ice_rink / outdoor_ice_rink_v0 | `tools/clay_ice_rink_market_square` | **PASS_ZERO_P0_P1** at v007 | v007 | 80,784 | 3,989,984 | 0 / 0 |
| Calgary RiverWalk (street option) | bow_river_pathway / bow_river_pathway_v0 | `tools/clay_calgary_riverwalk` | **PASS_ZERO_P0_P1** at v003 | v003 | 59,876 | 3,766,080 | 0 / 0 |
| Georgian terrace house with a slate mansard | georgian_terrace_house / georgian-terrace-house-early | `tools/clay_georgian_terrace_house` | stopped: v004 and v005 did not lower v003's count | v003 | 10,360 | 569,680 | 0 / 1 |
| Regency stucco terrace | regency_stucco_terrace / regency-stucco-terrace-nash | `tools/clay_regency_stucco_terrace` | stopped: v005 and v006 did not lower v004's count | v004 | 70,818 | 3,738,368 | 0 / 1 |
| Calgary sandstone heritage block | calgary_sandstone_heritage / sandstone_romanesque_revival | `tools/clay_calgary_sandstone_heritage` | stopped: v004 and v005 did not lower v003's count | v003 | 82,120 | 3,910,356 | 0 / 1 |
| Amsterdam twin-gabled canal warehouse | amsterdam_canal_warehouse / canal_warehouse_spice | `tools/clay_amsterdam_canal_warehouse` | stopped: the valley finding survived two fixes | v003 | 23,762 | 1,151,356 | 0 / 3 |
| Stepped terraced plaza | stepped_terraced_plaza / stepped_terraced_plaza_v0 | `tools/clay_stepped_terraced_plaza` | stopped: the bougainvillea finding survived two fixes | v003 | 44,282 | 2,734,476 | 0 / 3 |
| Amsterdam step-gable canal house | amsterdam_step_gable_house / step_gable_gothic | `tools/clay_step_gable_canal_house` | stopped: the brick-siding finding survived two fixes | v003 | 26,826 | 1,465,984 | 0 / 5 |
| Montreal Plateau triplex with an iron stair | montreal_plateau_triplex / montreal_triplex_classic_iron | `tools/clay_plateau_stair_triplex` | stopped: the cornice-return and console findings survived two fixes | v003 | 10,340 | 573,924 | 0 / 5 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder. Every
candidate is under the 4 MiB ordinary-blob cap.

### Trajectory (P0 / P1 per independent review)

| model | v001 | v002 | v003 | v004 | v005 | v006 | v007 |
|---|---|---|---|---|---|---|---|
| mews coach house | 2 / 6 | 0 / 4 | 0 / 4 | 0 / 3 | 0 / 3 | **0 / 0** | |
| Halifax warehouse | 1 / 5 | 0 / 4 | 0 / 3 | 0 / 1 | 0 / 1 | **0 / 0** | |
| ice rink | 4 / 9 | 0 / 4 | 0 / 4 | 0 / 3 | 0 / 1 | 0 / 1 | **0 / 0** |
| RiverWalk | 1 / 8 | 0 / 2 | **0 / 0** | | | | |
| Georgian terrace | 1 / 10 | 0 / 2 | 0 / 1 | 0 / 1 | 0 / 1 | (stopped) | |
| Regency terrace | 1 / 7 | 0 / 2 | 0 / 4 | 0 / 1 | 0 / 2 | 0 / 2 | (stopped) |
| sandstone block | 0 / 10 | 1 / 2 | 0 / 1 | 0 / 2 | 0 / 1 | (stopped) | |
| canal warehouse | 0 / 9 | 0 / 4 | 0 / 3 | (stopped) | | | |
| stepped plaza | 3 / 9 | 0 / 5 | 0 / 3 | (stopped) | | | |
| step-gable house | 2 / 12 | 0 / 8 | 0 / 5 | (stopped) | | | |
| Plateau triplex | 0 / 7 | 0 / 6 | 0 / 5 | (stopped) | | | |

## Open findings on the candidates that did not pass

Each family README lists the blockers of its last review, and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Georgian terrace house v003 (0 / 1)

- **Open P1:** the rear range does not match the top source. The single-storey east rear extension
  has a flat tan top that reads as an open yard. The source shows a grey roof inside a stone-coped
  rim, with a long hipped glazed lantern.
- **What happened after v003:** v004 and v005 fixed the lantern but each raised one new P1. The last
  was a black slot where the extension meets the main house's east wall.

### Regency stucco terrace v004 (0 / 1)

- **Open P1:** each inner roof face falls into the court as a plain slate funnel. The source shows
  four large dormer boxes and rooflights on the inner slopes.
- **What happened after v004:** v005 and v006 rebuilt the court roof and fixed it. Their reviews then
  found that the plan is about 14% too shallow north–south, which makes the court a square well rather
  than the source's long slot. They also found that the new court dormers render as blank pale panels.

### Calgary sandstone heritage block v003 (0 / 1)

- **Open P1:** the clock tower barely clears the main roofs. Its cornice sits below the corner
  pavilions' finials.
- **What happened after v003:** v004 and v005 raised the tower. Their reviews then flagged the south
  entrance: all three sources put it at the centre of the south front, under the big turret-flanked
  gable, but the model follows the brief and puts it in the south-west pavilion.
- **Question for the user:** should the entrance move to the centre of the south front, as the
  sources show? The brief's wording disagrees with the pixels, so this was left for your decision
  rather than changed.

### Amsterdam canal warehouse v003 (0 / 3)

- **Survived two fixes (P1):** a tan strip still shows in the front valley. The inner slopes and the
  hip plate stop short of it, leaving an open channel.
- **Other open P1s:**
  - black triangular gaps between unmitred coping segments on the curved canal parapet;
  - the roof deck is level with the west ridge and fills about 95% of the span, where the sources
    show a sunken deck at about 56%.

### Stepped terraced plaza v003 (0 / 3)

- **Survived two fixes (P1):** both bougainvilleas still read as loose clusters of faceted balloons,
  with no canopy draping from the roof edge.
- **Other open P1s:**
  - the foot of the strip does not widen west as in the source;
  - the pergola stands on the seating terraces instead of on the east house beyond the side stair.

### Amsterdam step-gable canal house v003 (0 / 5)

- **Survived two fixes (P1):** the west wall still reads as siding, with bed joints only and no
  brick bond.
- **Other open P1s:**
  - flush grey west windows with no white frame, sill or reveal;
  - a smooth, lighter rear gable band that reads as render;
  - two dark bands across the street facade at the floor lines;
  - an aerial view that clips the chimney cap.

### Montreal Plateau triplex v003 (0 / 5)

- **Survived two fixes (P1):**
  - the south-east cornice return still reads as stacked slabs with a black slot;
  - the consoles still read as stacked cubes.
- **Other open P1s:**
  - the facade is one flat plane, where the sources show the side bays forward of a recessed
    centre;
  - black holes at both ends of the canopy fascia;
  - a black slot at grade under the west pier.

## What carried over between models

- **Coplanar and coincident faces remain the cause of every black patch.** Wave G added these
  causes:
  - two gusset plates in one short panel;
  - a rake fascia sitting inside the soffit lining's thickness;
  - mortar joints crossing on one plane;
  - two decorative boards meeting at a gable apex.

  The fix was always to offset, bury or merge one part.
- **Elevated views decide decoration.** The ice rink's outward chalet trim existed from v006, but it
  was too thin to read from the aerial cameras, which cost a version. Detail that a source shows
  from above must be sized for the aerial frame, not the close-up.
- **Small gains can stall a family.** The Georgian, Regency and sandstone families each reached
  0 / 1, then spent two versions trading one open finding for another. A family at 0 / 1 needs a fix
  that touches nothing else.
- **Check the brief against the pixels.** The sandstone entrance and, in wave I, the Old Montreal
  pavilion both had brief wording that contradicted the sources. Reviewers follow the pixels, so the
  brief must be corrected before the next build.
- **Size budget.** The ice rink and sandstone block ran within 0.2 MB of the cap. Lower-poly
  ornaments, wider joint spacing and smooth shading recovered room without visible loss.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under
4 MiB. Superseded candidate GLBs were removed from tracking as each new candidate replaced them.
