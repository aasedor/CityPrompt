# Wave K: the climbing wall building and the covered passage, report, 2026-10-23

The user picked the climbing wall building ("I really like the climbing wall building"), then asked for all four
of its catalogue variants and the covered passage ("Can we do all 4? And the covered passage"). Wave K built:

- **Buildings (4):** the four variants of `climbing_wall_building`, each locked from its own three catalogue
  views:
  - The Crucible (`variant_0`), a wedge block with a charcoal climbing wall and Corten ends;
  - The Overhang (`variant_1`), a white recreation centre with a leaning timber climbing shell;
  - The Spine (`variant_2`), a bronze-glass tower with a full-height sculpted climbing strip;
  - The Reef (`variant_3`), a four-lobed teal bouldering shell.
- **Street (1):** the Barcelona passatge (`barcelona_passatge` / `variant_0`), a glass-roofed pedestrian passage
  through a block. It was chosen over the Paris passage couvert building because it is a clean passage that can
  be placed as a street option.

All work is on branch `claude/ten-new-buildings`. Every version followed the RLASM v6.1 process used since wave D:

- **Build:** rendered from the actual optimised GLB, 18 views at 1440 px and 32 samples.
- **Review:** reviewed by a separate agent that had not built it.
- **Evidence:** preserved as JPEG evidence in `tools/<family>/evidence/<version>/`.

Each family then went through the stopping rule in `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`: it stops at
the first PASS_ZERO_P0_P1, two consecutive reviews that fail to lower P0 + P1, or the same finding surviving two
targeted fixes. The best-reviewed version stays the candidate, and a tie keeps the earlier version.

Nothing here is enrolled, published, runtime-integrated or keeper-approved. Each README says so and lists the
open findings of its latest review.

## Results

None of the five reached PASS_ZERO_P0_P1. All five stopped under the stopping rule with no P0 open; the best
candidates have one or two P1 findings.

| model | catalogue archetype | family | outcome | candidate | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|
| The Reef | climbing_wall_building / variant_3 | `tools/clay_climbing_reef` | stopped: the climbing-pocket finding survived two fixes | v002 | 3,337,072 | 0 / 1 |
| The Crucible | climbing_wall_building / variant_0 | `tools/clay_climbing_crucible` | stopped: the east curtain-wall finding recurred after two fixes | v003 | 3,294,576 | 0 / 2 |
| The Overhang | climbing_wall_building / variant_1 | `tools/clay_climbing_overhang` | stopped: v003 and v004 did not lower v002's count | v002 | 2,951,656 | 0 / 2 |
| Barcelona passatge | barcelona_passatge / variant_0 | `tools/clay_barcelona_passatge` | stopped: the upper-bay finding survived two fixes | v002 | 3,593,652 | 0 / 2 |
| The Spine | climbing_wall_building / variant_2 | `tools/clay_climbing_spine` | stopped: v002 and v003 did not lower v001's count | v001 | 3,319,248 | 0 / 4 |

Every candidate GLB is the only tracked file in its `candidates/` folder and is under the 4 MiB ordinary-blob cap.

### Trajectory (P0 / P1 per independent review)

| model | v001 | v002 | v003 | v004 |
|---|---|---|---|---|
| The Reef | 0 / 6 | **0 / 1** | 0 / 2 (stopped) | |
| The Crucible | 0 / 5 | 0 / 5 | **0 / 2** (stopped) | |
| The Overhang | 0 / 5 | **0 / 2** | 0 / 2 | 1 / 1 (stopped) |
| Barcelona passatge | 0 / 4 | **0 / 2** | 0 / 2 (stopped) | |
| The Spine | **0 / 4** | 1 / 4 | 0 / 4 (stopped) | |

## What each family needed

### The Reef: stopped, v002 is the candidate

- **v001 (0 / 6):** the plan, four-lobed envelope, dome layout, apron, curb and ring path matched from the start.
  It failed on warped dome bubbles, shallow glazed entrances, interior boulders blocking two doorways, skylight
  wells clipping the ceiling, hard-edged pockets with slit artifacts, and paths that matched the ring path.
- **v002 (0 / 1):** fixed all six. The pockets were now faint soft smudges.
- **v003 (0 / 2):** the pockets overshot: about three times the source's count, evenly spread with identical sharp
  rims, and the lined pockets on the pale roll-over read as flat stickers. The pocket finding survived two
  targeted fixes, so the family stops with v002.

### The Crucible: stopped, v003 is the candidate

- **v001 (0 / 5):** a broken LED route line on the east facet, half the source's east curtain-wall bays, the
  warehouses on the wrong side, a black corner seam, and a stray interior partition outside the north wall.
- **v002 (0 / 5):** fixed all five, and gave the hex climbing panels back faces so a single-sided glTF viewer
  does not drop them. Its review found crossing west routes, an LED strip passing behind the panels,
  disconnected roof paths, a disc instead of a sunken half-round seating bowl, and a lit-office look behind the
  east glazing. It tied v001.
- **v003 (0 / 2):** fixed all five. The holds were too small and dark to read, and the east curtain wall again
  read as a near-square grid of about 13 columns where the sources show 20 to 22. The east-wall finding recurred
  after targeted fixes in v002 and v003, so the family stops with v003 as the candidate.

### The Overhang: stopped, v002 is the candidate

- **v001 (0 / 5):** the building block, roof pool and landscape matched. The shell's west face missed the fold at
  the pool-block parapet and left an open seam, two climbers floated off the shell, the crash mat was missing,
  the timber read pale beige instead of honey, and the rear and left_side cameras clipped the building.
- **v002 (0 / 2):** fixed all five. The penthouse read about twice the source height, and the shell's west flare
  met the parapet and spandrel bands with a stepped, intersecting edge.
- **v003 (0 / 2):** a one-storey penthouse and a clean shell-to-facade return fixed both. Its review found 10 west
  fin bays where the sources show 12 to 13, and holds over the shell's upper flare, which the sources show as
  plain timber except a band along the fold. It tied v002.
- **v004 (1 / 1):** 13 bays and holds confined to the fold band fixed both, but the shell now came down to a
  knife-edge point on the plaza where the source shows a broad base along the facade (P0), and a stray plate and
  stepped parapet sat on the wall under the east overhang. Two consecutive reviews did not lower v002's count,
  so the family stops.

### Barcelona passatge: stopped, v002 is the candidate

- **v001 (0 / 4):** the plan, envelope, portal, pavilions, end arch, floor and furniture matched. It lacked the
  openwork lattice brackets and rib crests, showed small punched windows where the source has bay-filling
  arches, and the south mouth looked onto a grey void.
- **v002 (0 / 2):** fixed brackets, crests and the south view. The upper windows still missed the source's tall
  arched French windows, and the south end arch read as an ordinary rib.
- **v003 (0 / 2):** fixed the end arch, but the upper bays became two tiers of stone-framed arched windows on a
  flat wall, adding a storey; the sources show one tall tier of deep recessed brick arches with one balcony each.
  The north portal was also too wide. The upper-bay finding survived two targeted fixes, so the family stops.
  The v003 reviewer noted that the review brief described the facades as three storeys, which contradicts the
  source pixels; the builder had partly followed that text. The sources govern, so the finding stands.

### The Spine: stopped, v001 is the candidate

- **v001 (0 / 4):** the envelope, plan, 15-storey count read from the pixels (the catalogue says 20 to 35),
  notch, amenity block, six balconies and roof terrace matched. The spine outline and carving, the curtain-wall
  fin rhythm, the boulder garden and the right_side camera did not.
- **v002 (1 / 4):** fixed the fins, but the re-aimed right_side camera clipped the tower top (P0), the spine still
  read as a flat strip speckled with about 160 holds, and the boulders read as crystals.
- **v003 (0 / 4):** fixed the camera and cut the holds to about 50. The spine relief and tone, the roof and plaza
  boulders, the boulder garden and the amenity crown still read unlike the sources. Two consecutive reviews did
  not lower v001's count, and the spine-relief finding survived two fixes, so the family stops with v001.

## What carried over

- **Sculpted and organic identity surfaces are the hardest.** Every family that stopped did so on a textured
  identity surface rather than on massing: the Reef's pockets, the Spine's carved rock, the Overhang's shell
  and holds, the passatge's arched bays, the Crucible's curtain-wall rhythm and holds. The massing, plans and
  cameras were right by v001 or v002 in every family.
- **Fixes overshoot.** The Reef went from hard cut-outs to faint smudges to too many crisp pockets. Each fix
  should state the source's count, size and distribution, not only the direction of change.
- **The brief must not contradict the sources.** One wrong storey count in a review brief steered a builder away
  from the source. Briefs should describe only what the locked pixels show.
- **Coincident faces are still the cause of every black slot.** This wave added a corner carrier seam, an LED
  strip behind cladding panels and overlapping wall fillers. The fix was again to lap or offset by a few
  centimetres, or to project trim onto the true surface.
- **Single-sided panels need backs for runtime.** A glTF viewer that culls back faces would drop single-sided
  cladding; the Crucible's hex panels now carry back faces.
- **A recording bug was fixed.** The version recorder had been overwriting each README's open-blockers section
  with a placeholder; 22 earlier READMEs were affected. The section is now generated from the latest review.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under 4 MiB. Superseded
candidate GLBs were removed from tracking as each new candidate replaced them.
