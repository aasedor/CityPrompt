# Wave J: five catalogue additions, report, 2026-10-23

The user asked for five more archetypes, chosen by Claude ("Do 5 more archetypes after this. You
pick."). Wave J picked five catalogue types that had quality reference images but no 3D model
(`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`), favouring Canadian city types:

- **Buildings (4):**
  - the Gastown heritage commercial block (Vancouver);
  - a Halifax Georgian colonial house;
  - a Vancouver laneway house;
  - the Halifax ferry terminal.
- **Street (1):** a Montreal Plateau residential rue.

The Toronto urban square was considered and dropped: its reference views show mostly surrounding towers rather
than the square itself. Each family locks the three views (front, oblique, top) of catalogue `variant_0`. All
work is on branch `claude/ten-new-buildings`.

Every version followed the RLASM v6.1 process used since wave D:

- **Build:** rendered from the actual optimised GLB, 18 views at 1440 px and 32 samples.
- **Review:** reviewed by a separate agent that had not built it.
- **Evidence:** preserved as JPEG evidence in `tools/<family>/evidence/<version>/`.

Each family then went through the stopping rule in `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`. A family
stops at the first of these:

- the review returns PASS_ZERO_P0_P1;
- two consecutive reviews fail to lower P0 + P1;
- the same finding survives two targeted fixes.

The best-reviewed version stays the candidate, and a tie keeps the earlier version.

Nothing here is enrolled, published, runtime-integrated or keeper-approved. Each README states that nothing in the
family is keeper-approved, runtime-integrated, enrolled in a catalogue or activated, and that those remain
separate checkpoints for the user's decision.

## Results

| model | catalogue archetype | family | outcome | candidate | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|
| Gastown heritage commercial block | gastown_heritage_commercial | `tools/clay_gastown_heritage_commercial` | **PASS_ZERO_P0_P1** at v003 | v003 | 2,083,784 | 0 / 0 |
| Halifax Georgian colonial house | halifax_georgian_colonial | `tools/clay_halifax_georgian_colonial` | **PASS_ZERO_P0_P1** at v003 | v003 | 1,378,820 | 0 / 0 |
| Montreal Plateau residential rue | montreal_plateau_residential_rue | `tools/clay_montreal_plateau_rue` | **PASS_ZERO_P0_P1** at v003 | v003 | 4,027,580 | 0 / 0 |
| Halifax ferry terminal | halifax_ferry_terminal | `tools/clay_halifax_ferry_terminal` | v004 under review (v003 tied v002) | v002 | 2,638,692 | 0 / 1 |
| Vancouver laneway house | vancouver_laneway_house | `tools/clay_vancouver_laneway_house` | stopped: the planting finding survived two fixes | v002 | 2,087,620 | 0 / 1 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder, and every candidate is
under the 4 MiB ordinary-blob cap. The Plateau rue, at 4,027,580 bytes, is the closest.

### Trajectory (P0 / P1 per independent review)

| model | v001 | v002 | v003 | v004 |
|---|---|---|---|---|
| Gastown | 0 / 5 | 0 / 3 | **0 / 0** | |
| Halifax Georgian colonial | 0 / 3 | 0 / 1 | **0 / 0** | |
| Plateau rue | 0 / 6 | 0 / 1 | **0 / 0** | |
| Halifax ferry terminal | 0 / 7 | 0 / 1 | 0 / 1 | under review |
| Vancouver laneway house | 0 / 8 | 0 / 1 | 0 / 2 (stopped) | |

## What each family needed

### Gastown heritage commercial block: passed at v003

- **v001 (0 / 5):** the building, bay rhythm, frieze, shopfronts and roof plan were right from the start. It
  failed on:
  - black slots in a shop jamb;
  - a pediment rake overshooting into a dark wedge;
  - an undersized steam clock too close to the facade;
  - three missing standard close views;
  - side and rear cameras blocked by neighbours.
- **v002 (0 / 3):** fixed all five. Its review found black recessed door floors (present but unrecorded in v001),
  north-wall windows buried in the neighbour by a mirrored coordinate, and a missing locked front source. The
  last was a pipeline error: a disk cleanup deleted the copied source from the build folder while it was in use.
  The source was restored before evidence preservation.
- **v003 (0 / 0):** lit stone floor liners and proud thresholds in the door recesses, and the north-wall windows
  moved onto the exposed wall.

### Halifax Georgian colonial house: passed at v003

- **v001 (0 / 3):**
  - the east camera sat at ground level in a 3.5 m gap;
  - there were black slits at the entrance pilaster heads;
  - the street railing ran past the open front lawns the sources show.
- **v002 (0 / 1):** fixed all three. The east elevation uses a near-clip cutaway past the close stone neighbour
  in that one view, which the reviewer accepted as a valid whole-side proof. A black slot at the portico
  entablature end remained (present but unrecorded in v001).
- **v003 (0 / 0):** the entablature ends lapped into the pavilion, and the lintels and sills moved off the reveal
  planes.

### Montreal Plateau residential rue: passed at v003

- **v001 (0 / 6):**
  - stair stringers rose through the gallery decks;
  - the stair curl and newel did not read;
  - a turret/parapet slit;
  - flat rear windows;
  - boarded-up context rows;
  - a cropped corner camera.
- **v002 (0 / 1):** fixed five of them. The wall-side handrail head ended free in mid-air and read as a black bar
  rising through each deck.
- **v003 (0 / 0):** capped stair-head newels end both handrails.

### Halifax ferry terminal: v004 under review, v002 is the candidate

- **v001 (0 / 7):**
  - black voids at open member ends;
  - an east-wall ground slit;
  - an 8-bay glass box where the sources show 5;
  - opaque doors;
  - flat rear windows;
  - cropped side views.
- **v002 (0 / 1):** fixed all seven. A 7 × 2 px black slot at an interior bench joint remained (present but
  unrecorded in v001).
- **v003 (0 / 1):** closed the bench joint. Its review found the upper-lounge seating rows floating 0.4 m above the
  floor with no legs (present but unrecorded in v001 and v002). It ties v002, so v002 stays the candidate.
- under review_LINE

### Vancouver laneway house: stopped, v002 is the candidate

- **v001 (0 / 8):**
  - black wedges and squares at the side entry, the glazing crossings and the fin base;
  - side-entry door and lining;
  - a garage roof turned 90°;
  - missing ferns and a bare side bed;
  - two framing errors.
- **v002 (0 / 1):** fixed seven. The front beds were low fern rosettes only, without the tall feather-reed and
  fescue the sources show.
- **v003 (0 / 2):** restored the reed and fescue at the glazed bay but lost the side-street fern hedge, and the
  enlarged fern read as bare thorny canes. The planting finding survived two targeted fixes, so the family stops.
  Its README records the likely fix: scale the fern leaflets with the frond and restore the west-wall hedge.

## What carried over

- **Earlier reviews miss small defects; later reviews find them.** In four of the five families a later review
  found a defect that was already present in an earlier version but unrecorded:
  - Gastown: recess floors;
  - Georgian colonial: portico slot;
  - ferry terminal: bench joint and floating seats;
  - Plateau rue: the stair-head bar, which v001 had flagged only partly.

  Each new finding is real, but the count makes a version look worse than it is.
- **Coincident faces are still the cause of every black slot.** This wave added:
  - a threshold top on the floor plane;
  - a curb face on the sidewalk face;
  - a backrest end flush with a seat end;
  - an entablature return in a pavilion side plane;
  - a lintel underside on an opening head.

  The fix was always to lap one member 1–7 cm past or into the other.
- **Name the standard views from v001.** Gastown lost a P1 to missing `facade_close`, `architecture_close` and
  `glass_close` renders. Every later family was renamed before its first build.
- **Do not prune build folders that are still in use.** A disk cleanup removed a locked source from a running
  build, and the reviewer correctly flagged it. Clean only folders whose evidence is already preserved.
- **Planting from scratch is still the weak point.** The laneway house was the only wave J family to stop, and it
  stopped on planting. It used the shared planting kit, but with a family-specific fern prototype that did not
  hold up when enlarged.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under 4 MiB. Superseded
candidate GLBs were removed from tracking as each new candidate replaced them.
