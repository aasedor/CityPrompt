# Ten new buildings for the student catalogue: batch report, 2026-10-10

Branch `claude/ten-new-buildings`. Method: RLASM v6.1 architectural clay
(`docs/RLASM_LATEST_METHOD.md`), mirroring the completed pilot in
`tools/pilot_brownstone_rowhouse/`. Nine of the ten buildings were built; each ran
through source lock, measurement contract, construction with the shared `clay_core`,
`geometry` and `assemblies` modules, a 1440 px / 32 spp roster of 18 views plus four
phone boards, and an independent holistic review by a separate reviewer agent that saw
only the locked sources, the renders and the boards. The brief permits at most three
versions per building; every building used all three and stops here with its open
findings recorded. Nothing is keeper-approved, enrolled, published or activated, and
`buildingArchetypes.json` was not touched.

## Results

Version shown is the final one. Triangles and GLB bytes are from the final build report
and the preserved GLB in `tools/<family>/candidates/`. Open P0/P1 are the independent
reviewer's counts on that version.

| # | brief | archetype / variant (catalogue variant id) | family | version | triangles | GLB bytes | review verdict | open P0 / P1 |
|---|---|---|---|---|---|---|---|---|
| 1 | compact two-storey neighbourhood office | corporate_office_campus_headquarters / variant_3 (industrial_warehouse_campus_hq) | `tools/clay_campus_shed_office` | v003 | 18,872 | 1,011,064 | VISUAL_REWORK_REQUIRED | 0 / 3 |
| 2 | indoor vertical farm | vertical_farm_indoor_agriculture / variant_1 (dark_panel_led_grow_block) | `tools/clay_led_grow_block` | v003 | 19,622 | 975,684 | VISUAL_REWORK_REQUIRED | 1 / 2 |
| 3 | fire station | modern_fire_station / variant_2 (fire_cantilevered_modern) | `tools/clay_cantilever_fire_station` | v003 | 11,484 | 607,452 | VISUAL_REWORK_REQUIRED | 1 / 3 |
| 4 | elementary school with gym | ecole_republicaine / variant_3 (ecole-republicaine-art-deco; pixels show a contemporary courtyard school) | `tools/clay_courtyard_primary_school` | v003 | 18,768 | 1,019,148 | VISUAL_REWORK_REQUIRED | 1 / 1 |
| 5 | second hotel / motel (limited service) | highway_motor_hotel / variant_2 (hotel_limited_service) | `tools/clay_limited_service_hotel` | v003 | 20,634 | 979,764 | VISUAL_REWORK_REQUIRED | 0 / 3 |
| 6 | three-unit rowhouse with grade entrances | brick_rowhouse_terrace / variant_2 (queen_anne_bay_window_terrace) | `tools/clay_queen_anne_rowhouse_trio` | v003 | 17,948 | 974,268 | VISUAL_REWORK_REQUIRED | 0 / 6 |
| 7 | heavy industrial with outdoor yard | early_20c_megastructure_industrial / variant_1 (heavy_craneway_hall) | `tools/clay_craneway_hall` | v003 | 15,972 | 861,808 | VISUAL_REWORK_REQUIRED | 1 / 3 |
| 8 | utility / district energy | central_utilities_plant_energy_centre / variant_1 (transparent_plant_showcase_urban) | `tools/clay_energy_centre` | v003 | 11,320 | 589,096 | VISUAL_REWORK_REQUIRED | 2 / 2 |
| 9 | small place of worship | none with three locked views | not built | - | - | - | blocked | - |
| 10 | large-format supermarket with parking court | commercial_strip_mall / variant_1 (strip_anchored_l_plaza) | `tools/clay_anchored_plaza_supermarket` | v003 | 9,256 | 498,924 | VISUAL_REWORK_REQUIRED | 0 / 2 |

Every GLB is under the 1 MiB ordinary-blob limit. Every carrier aperture audit passed
and every vertex sits at or above grade in every delivered version.

### Trajectory per building (v002 review to v003 review)

| # | v002 P0 / P1 / P2 | v003 P0 / P1 / P2 | v002 blockers verified fixed in the v003 pixels |
|---|---|---|---|
| 1 office | 2 / 3 / 6 | 0 / 3 / 6 | all five: no brace pierces a canopy, door not split by a column, two west bays, dock canopy on the south only, braces only in corner and end bays |
| 2 farm | 2 / 4 / 4 | 1 / 2 / 6 | glasshouses inside the parapet, one-storey penthouse, recessed corner entrance, four rack tiers, slot proportion; magenta depth only in elevations |
| 3 fire | 1 / 5 / 8 | 1 / 3 / 7 | continuous hall curtain wall, east lobby, tower height, cap, clock and band; the corner void moved rather than closed |
| 4 school | 2 / 6 / 5 | 1 / 1 / 6 | both wing-junction through-slots closed, columns meet the canopy, entrance block on the street line, west-wing windows, roof hierarchy |
| 5 hotel | 1 / 7 / 5 | 0 / 3 / 9 | L legs joined under one membrane, north wing colour and band, coursed stone piers, parking stripes; road and verges partly |
| 6 rowhouse | 1 / 7 / 4 | 0 / 6 / 6 | closed dormer solid, first-floor windows, cut gable windows, two chimneys, stepped stoops, brick banding, interior camera |
| 7 crane | 2 / 5 / 7 | 1 / 3 / 7 | monitors on the nave roof, switchback stair, monitor corner bars, interior camera inside the nave |
| 8 energy | 3 / 2 / 8 | 2 / 2 / 8 | south face enclosed, concrete corner panels on both faces, entrance present, differentiated bays, parapet meets the roof |
| 10 plaza | 0 / 7 / 8 | 0 / 2 / 13 | tower faces, cafe wing, storefront continuity, canopy mitre, volumetric tower, sign panel |

### Open P0 and P1 per building (recorded, not fixed; v003 was the last permitted version)

- **1 office**: west face bays composed in mirror order against both elevation sources;
  entrance canopy spans one bay where the sources show one thin canopy across both;
  canopy tie rods anchor into the upper window.
- **2 farm**: P0 roof programme rotated 90 degrees relative to the plinth entrance (the
  sources put the glasshouse flanks, beds and penthouse over the entrance face); magenta
  rack light fades at oblique and aerial angles; north shutter with a slit cut through it.
- **3 fire**: P0 black slot at the south-west corner between the corner pier and the red
  leg; loggia too shallow and short; red leg on the south face instead of the north end
  of the west face; bay doors span half the south face instead of three quarters.
- **4 school**: P0 full-height black void at the entrance block's junction with the
  passage overhang; black band under the canopy fascia.
- **5 hotel**: guest-room windows and floor plates continue inside the glazed lobby
  tower; low wing still a ribbon window; no kerbs or raised sidewalks.
- **6 rowhouse**: unit B's door sits in the source's paired-window run (the brief's
  three-grade-entrance requirement against a source showing door, window, window, door;
  a decision for the user); middle gable a set-back dormer instead of a wall gable; black
  eaves slot on both end walls; void under the east chimney; black pentagons at every
  gable apex; rear cross gables half height.
- **7 crane**: P0 side_doors camera still misses the roller door; open gable frame only
  over the nave; lattice columns half the source proportion; monitor_close framed low.
- **8 energy**: P0 entrance threshold slab floating above the pavement; P0 riser pipes
  stopping short of the slab; invented entrance fin and canopy; service bay flush with
  no door leaf.
- **10 plaza**: black sliver at the tower's south-west corner; tower and sign band placed
  mid-anchor instead of hard against the cafe wing with a lower tier behind it.

Each family's `README.md` carries the same list under "Open blockers after v003" with
the finite fix, and `VERSIONS.md` carries the full v001 to v003 history.

## Recurring defect classes worth a method note

- **Face-relative coordinates.** Two families (plaza v002 carriers, energy v002 south
  face) passed absolute x where `clay_core.Face` expects u relative to the face centre.
  The energy centre's open south face and detached-looking frames were entirely this.
- **Coplanar faces render black.** Tower piers inside a tower volume, stoop step boxes,
  roof plates ending flush with gable walls, pots seated exactly on a cap, panels
  flush inside solid brick. Every instance needs an overlap or an inset, never a shared
  plane.
- **Butted carriers.** Side carriers inset by the wall thickness at a hidden junction
  leave a through-slot (school, hotel); they must run flush through the junction line.
- **Camera roles.** Reviewers failed several views for not showing their named target
  (interior views taken from outside, side_doors behind a boxcar). Aim every detail
  camera at a checked landmark and verify it in the quick subset before the roster.
- **Source conflicts recorded, not averaged.** Farm (four versus five slot rows), school
  (catalogue label versus pixels), rowhouse (continuing terrace, three doors), fire
  (north face unseen) are all recorded in the measurement contracts.

## Building 9: small place of worship was not built

The brief asks for each building to come from a catalogue archetype whose front, oblique
and top views exist. No such source exists for a place of worship:

- `frontend/src/data/buildingArchetypes.json` carries no worship, church, chapel, temple,
  mosque or synagogue entry.
- `frontend/public/archetypes/buildings/` holds only `gothic_community_church`
  (`reference-board-v1.png`, `roof-reference-v1.png`) and `timber_sanctuary_church`
  (`reference-board-v1.png`): single composite reference boards for two large generated
  churches, not the three locked catalogue views, and both are large-church concepts
  rather than the small place of worship the brief names.
- The connected Google Drive `snapshots` folder was searched by title for church, chapel,
  worship, temple, mosque and synagogue and returned nothing.

Locking a reference board as a "front view" or mixing the two church concepts would
violate Phase A of the method, so the building is recorded as blocked. Unblocking it
needs the user to nominate (or generate and lock) a small worship archetype with its
front, oblique and top views in the authoritative buildings root.

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
4. **Keeper decision**: every candidate ends VISUAL_REWORK_REQUIRED or with open P1s after
   its third permitted version. The user decides whether a further version is worth the
   cost for any of them, or whether the open findings are acceptable concept limitations
   to keep visible in the classroom.
5. **Place of worship source**: nominate or generate the small worship archetype with
   three locked views so building 9 can be built with the same pipeline.

## How the evidence is laid out

Every family lives in `tools/<family>/` with `lock_sources.py`, `sources.json`,
`family_*.py`, `build.py`, `phone_board.py`, `README.md` and `VERSIONS.md`.
`evidence/<version>/` holds the build report, source entry, prework manifest, carrier
aperture audit, reviewer brief, independent review and JPEG copies of every render and
phone board under 950 KB. `candidates/` holds the delivered GLB as an ordinary Git blob
under 1 MiB (Git LFS uploads are refused from the build host). Full-resolution renders,
sources and the GLB were sent to the user as a zip per version (compact JPEG zips where
the PNG zip exceeded the 30 MiB upload limit). `tools/clay_evidence_preserve.py` is the
shared preservation step.
