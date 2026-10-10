# Towers and mixed-use buildings for the student catalogue: batch report, 2026-10-10

Branch `claude/ten-new-buildings`, second batch after
`docs/showcase/TEN_BUILDINGS_REPORT_2026-10-10.md`. Method: RLASM v6.1 architectural
clay (`docs/RLASM_LATEST_METHOD.md`), mirroring the completed pilot in
`tools/pilot_brownstone_rowhouse/`. Three towers and three mixed-use buildings were
built; each ran through source lock, measurement contract, construction with the shared
`clay_core`, `geometry` and `assemblies` modules, a 1440 px / 32 spp roster of 18 views
plus four phone boards, and an independent holistic review by a separate reviewer agent
that saw only the locked sources, the renders and the boards. The brief permits at most
three versions per building; every building used all three and stops here with its open
findings recorded. Nothing is keeper-approved, enrolled, published or activated, and
`buildingArchetypes.json` was not touched.

## Results

Version shown is the final one. Triangles and GLB bytes are from the final build report
and the preserved GLB in `tools/<family>/candidates/`. Open P0/P1 are the independent
reviewer's counts on that version.

| # | brief | archetype / variant (catalogue variant id) | family | version | triangles | GLB bytes | review verdict | open P0 / P1 |
|---|---|---|---|---|---|---|---|---|
| T1 | tower: mid-century slab with balconies | west_end_mid_century_tower / variant_0 (midcentury_concrete_slab) | `tools/clay_slab_balcony_tower` | v003 | 18,884 | 975,632 | VISUAL_REWORK_REQUIRED | 0 / 4 |
| T2 | tower: brick podium with a glass condo tower | condo_podium_tower / variant_0 (brick_podium_glass_tower) | `tools/clay_brick_podium_condo_tower` | v003 | 18,214 | 979,320 | VISUAL_REWORK_REQUIRED | 0 / 5 |
| T3 | tower: contemporary glass office with a Plus 15 bridge | calgary_plus_15_connected_tower / variant_2 (plus15_contemporary_glass) | `tools/clay_plus15_glass_office_tower` | v003 | 10,832 | 575,680 | VISUAL_REWORK_REQUIRED | 0 / 4 |
| M1 | mixed use: arched brick mill with shops and lofts | industrial_brick_mixed_use / variant_0 (industrial_brick_original_mill) | `tools/clay_arched_mill_mixed_use` | v003 | 14,028 | 744,292 | VISUAL_REWORK_REQUIRED | 1 / 4 |
| M2 | mixed use: courtyard mid-rise over street retail | rndsqr_terraced_mixed_use_midrise / variant_0 (rndsqr_midrise_courtyard) | `tools/clay_courtyard_mixed_use_midrise` | v003 | 16,800 | 895,624 | VISUAL_REWORK_REQUIRED | 2 / 4 |
| M3 | mixed use: chamfered corner block with a dome | barcelona_corner_chamfer / variant_0 (chamfer_classic) | `tools/clay_chamfer_corner_dome_block` | v003 | 15,860 | 830,468 | VISUAL_REWORK_REQUIRED | 3 / 6 |

Every GLB is under the 1 MiB ordinary-blob limit. Every carrier aperture audit passed
and every vertex sits at or above grade in every delivered version.

### Trajectory per building (v001 review to v003 review)

| # | v001 P0 / P1 / P2 | v002 P0 / P1 / P2 | v003 P0 / P1 / P2 | earlier blockers verified fixed in the v003 pixels |
|---|---|---|---|---|
| T1 slab | 0 / 4 / 9 | 0 / 4 / 9 | 0 / 4 / 6 | window-to-spandrel ratio, centre-bay width, duplicate ground plate, brick parapet band, canopy rods; corner caps shrunk but not removed |
| T2 condo | 3 / 2 / 8 | 1 / 2 / 7 | 0 / 5 / 6 | curtain-wall void at the terrace, balconies above the cornice, interior camera out of the core, columns no longer bisect podium openings, no grade wedges, identity view from the south-east |
| T3 Plus 15 | 1 / 5 / 8 | 0 / 5 / 7 | 0 / 4 / 7 | interior legible, bridge lands on a stub block, spandrel slot and junction squares, penthouse fins, lower-floor transparency (moved to the furnished floor), interior exposure |
| M1 mill | 2 / 3 / 6 | 1 / 1 / 7 | 1 / 4 / 6 | plan mirror, chimney end, four bays per face, pavilion length with a railed north deck, framed rear door |
| M2 courtyard | 2 / 7 / 6 | 4 / 5 / 7 | 2 / 4 / 6 | stair no longer roofed, rear bar four storeys with a tan top, cameras re-aimed, penthouse-base band, framed penthouse glazing, inner-corner and jamb slots |
| M3 chamfer | 3 / 7 / 5 | 3 / 5 / 8 | 3 / 6 / 6 | storey count (then disputed again, see below), drum-window boxes, solid parapet, soffit blocks, cuboid oculi, wing bay count, flat shop heads, brick first floor |

The counts do not fall monotonically because each rework exposes the next layer of
fidelity findings once the geometric blockers are gone, and because two reviewers read
the same sources differently (the chamfer storey count and the Plus 15 mechanical deck
side). Both disagreements are recorded rather than resolved.

### Open P0 and P1 per building (recorded, not fixed; v003 was the last permitted version)

- **T1 slab**: black band along the entrance canopy fascia (two-shell canopy with an
  unassigned slot); black caps still at the four parapet corners; fin stubs proud of the
  coping so the roofline reads crenellated; rear roller door split by a fin.
- **T2 condo**: east corner columns pierce the podium cornice and stop in the
  second-storey brick; south balconies a checkerboard on four stacks against five
  continuous stacks; tower footprint too small and pushed south-east on the podium;
  corner grammar (brick pier and south entry against a double-height glazed corner with
  the lobby on the east face under a canopy); interior camera frames only a frosted pane.
- **T3 Plus 15**: the furnished floor 9 renders transparent on all four faces; penthouse
  about 1.8 storeys and 0.55 of the roof against about 2.7 and 0.65; mechanical deck in
  the north-west notch where the pixels put it on the south side inside a fin screen
  (the v002 review wording said north-west); green roof as a four-sided ring instead of
  beds on three sides with an east deck, walkway ring and paths.
- **M1 mill**: P0 chimney breast on the rear eave interpenetrating four sill plates with
  the bay-2 windows abutting it; horizontal dentil cornice and kneelers on the gable faces
  where the sources run pilasters to the raked coping; gable face missing the narrow blank
  end bay with a rear-corner door (plan square instead of about 1.17:1); chimney 1.3 bays
  from the gable as an external breast instead of inside the footprint; pavilion a
  flat-lidded box instead of a lean-to glasshouse.
- **M2 courtyard**: P0 wing top storey built as a set-back pavilion over the front half
  of each wing where the sources show one continuous top storey across both wings into
  the rear bar; P0 black slot between the top tread and the courtyard deck; black band at
  the stair foot; rear bar courtyard materials inverted (dark piers, light slab edges);
  wing street-face rhythm; unframed balcony back-wall openings.
- **M3 chamfer**: P0 storey count disputed (the v003 reviewer reads the sources as ground
  plus two, the v001 reviewer and the builder as ground plus three; recorded for a human
  to settle); P0 black voids where the parapet balustrade meets the bay cornice ring; P0
  interior camera illegible; drum still about 0.85 of the dome height with square windows
  and a flat dome; bow bay about 30 percent glazed against 75; round corner columns added
  in v003 to close the mitres are absent from the sources; dome colour equal to the roof
  tiles; balcony ironwork reduced to a bar on posts; black cube at the kerb mitre.

## Recurring defect classes worth a method note

- **Coplanar faces render black, again.** The Plus 15 penthouse roof (body and fascia
  tops at one height), the courtyard penthouse base flush with the parapet plane, the
  chamfer arch hoods wider than their bay (adjacent hoods overlapping), the stair cheek
  walls sharing the carrier's street plane, and the terrace rails standing in the parapet
  plane were all this class. Every cover piece must abut, never overlap, and every proud
  element must stand clear of the carrier planes.
- **Fixing a mitre with a new element creates a new finding.** The chamfer's corner
  pilasters closed the black wedges at the course ends but added round columns the
  sources do not show; the condo's columns moved up to the podium roof and now stop in
  the second-storey brick. A junction fix has to be checked against the sources, not
  only against the void it closes.
- **Review wording is not source pixels.** The Plus 15 mechanical deck was moved to the
  "north-west notch" named in the v002 review; the v003 reviewer measured the sources and
  found the units on the south side. Reworks should re-measure the source before acting
  on a reviewer's location words.
- **Reviewer disagreement is recorded, not averaged.** The chamfer storey count and the
  mill arches (the v002 reviewer read flat heads, the sources show segmental arches)
  stay in the measurement contracts and the READMEs as open questions.
- **Cameras that look at blank walls.** Two courtyard cameras and the chamfer and condo
  interior cameras failed their roles; every detail camera needs a checked landmark in the
  quick subset before the roster.

## What the user has to do next

Nothing in this branch is keeper-approved, enrolled, published or activated. Each
candidate stops at the independent review. The steps that only the user can take:

1. **Runtime acceptance on localhost:5174** for every candidate the user wants to carry
   forward: load the GLB from `tools/<family>/candidates/`, complete
   `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` per variant and record the measured
   evidence (terrain, entrances, routes, edit/recovery, capture).
2. **Zoning use programs**: decide the use program and development type each candidate
   is enrolled under in `frontend/src/features/zoningCatalogue/buildingPrograms.json`
   before any catalogue splice.
3. **Activation quotes**: the exact-byte activation and picker-card generation in
   `docs/BUILDING_CATALOGUE_WORKFLOW.md` needs the user's activation quote per archetype;
   `python -m tools.catalogue_promotion check` was deliberately not run as a gate here.
4. **Keeper decision**: every candidate ends VISUAL_REWORK_REQUIRED after its third
   permitted version. The user decides whether a further version is worth the cost for
   any of them, or whether the open findings are acceptable concept limitations to keep
   visible in the classroom. The two reviewer disagreements (chamfer storey count, mill
   arches) need a human reading of the locked sources.
5. **Google Drive sync**: `tools/drive_sync/` holds the script and GitHub Action that
   copy every `tools/<family>/candidates/*.glb` to the Drive folder; it runs once the
   OAuth client id, secret and refresh token are stored as repository secrets and the
   folder id as a repository variable, as described in `tools/drive_sync/README.md`.

## How the evidence is laid out

Every family lives in `tools/<family>/` with `lock_sources.py`, `sources.json`,
`family_*.py`, `build.py`, `phone_board.py`, `README.md` and `VERSIONS.md`.
`evidence/<version>/` holds the build report, source entry, prework manifest, carrier
aperture audit, reviewer brief, independent review and JPEG copies of every render and
phone board under 950 KB. `candidates/` holds the final GLB as an ordinary Git blob
under 1 MiB (Git LFS uploads are refused from the build host; earlier versions' GLBs
were removed from the tree once superseded and remain in the branch history). Full-
resolution renders, boards and the GLB were sent to the user as a compact JPEG zip per
version. `tools/clay_evidence_preserve.py` is the shared preservation step.
