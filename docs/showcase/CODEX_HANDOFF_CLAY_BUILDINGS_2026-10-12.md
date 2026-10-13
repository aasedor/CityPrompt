# Handoff prompt for Codex: the fifteen RLASM clay buildings

Copy everything below the line into Codex as its first message. Fill in the Google Drive
folder link where marked. The fifteen GLB files you copy into Drive are the same files as
`tools/clay_*/candidates/*.glb` on the `claude/ten-new-buildings` branch of
https://github.com/aasedor/CityPrompt, so Codex can work from either place.

---

You are taking over fifteen architectural-clay building models for City Prompt, an
AI-assisted site-planning app (React/TypeScript/Vite with Three.js on the front end,
Python FastAPI on the back end). The models were built from locked catalogue views with a
Blender-driven Python toolchain and each one was carried through independent visual
reviews. Read this whole brief before touching anything.

## 1. Where the models are

- **Google Drive folder:** <PASTE THE DRIVE FOLDER LINK HERE>. It holds the fifteen candidate
  GLBs listed in section 2, each named `clay-<family-slug>-clay-vNNN.glb`, plus the three
  reports named in section 7.
- **Repository:** https://github.com/aasedor/CityPrompt, branch `claude/ten-new-buildings`.
  The same GLBs are ordinary git blobs at `tools/clay_*/candidates/*.glb` (one per family, at
  most 4 MiB each; git LFS is not used). Every family folder also has the generator source,
  the locked source images, per-version renders, boards and reviews.
- The GLBs are plain glTF binaries with flat-colour PBR materials, Z up in the generator
  but exported Y up as standard glTF, 1 unit = 1 metre, the building footprint centred on
  the origin at grade z = 0. They have no textures: colour comes from a small palette of
  materials (brick, stone, glass, trim, roof, copper and so on) named per family.

## 2. The fifteen candidates

The "candidate" is the best-reviewed version of each family, which is not always the latest.
P0 / P1 are the open blocker counts from that version's independent review (P0 = identity or
geometry failure, P1 = clear source mismatch, P2 = polish). Nine are at zero / zero.

| family folder | GLB file | catalogue archetype / variant | review |
|---|---|---|---|
| `tools/clay_campus_shed_office` | `clay-campus-shed-office-clay-v009.glb` | corporate_office_campus_headquarters / variant_3 | PASS, 0 / 0 |
| `tools/clay_led_grow_block` | `clay-led-grow-block-clay-v007.glb` | vertical_farm_indoor_agriculture / variant_1 | PASS, 0 / 0 |
| `tools/clay_cantilever_fire_station` | `clay-cantilever-fire-station-clay-v009.glb` | modern_fire_station / variant_2 | 0 / 1 |
| `tools/clay_courtyard_primary_school` | `clay-courtyard-primary-school-clay-v009.glb` | ecole_republicaine / variant_3 (pixels show a contemporary courtyard school) | PASS, 0 / 0 |
| `tools/clay_limited_service_hotel` | `clay-limited-service-hotel-clay-v007.glb` | highway_motor_hotel / variant_2 | 0 / 1 |
| `tools/clay_queen_anne_rowhouse_trio` | `clay-queen-anne-rowhouse-trio-clay-v009.glb` | brick_rowhouse_terrace / variant_2 | 0 / 2 |
| `tools/clay_craneway_hall` | `clay-craneway-hall-clay-v007.glb` | early_20c_megastructure_industrial / variant_1 | 0 / 2 |
| `tools/clay_energy_centre` | `clay-energy-centre-clay-v010.glb` | central_utilities_plant_energy_centre / variant_1 | PASS, 0 / 0 |
| `tools/clay_anchored_plaza_supermarket` | `clay-anchored-plaza-supermarket-clay-v010.glb` | commercial_strip_mall / variant_1 | 0 / 1 (interior only) |
| `tools/clay_slab_balcony_tower` | `clay-slab-balcony-tower-clay-v007.glb` | west_end_mid_century_tower / variant_0 | PASS, 0 / 0 |
| `tools/clay_brick_podium_condo_tower` | `clay-brick-podium-condo-tower-clay-v006.glb` | condo_podium_tower / variant_0 | PASS, 0 / 0 |
| `tools/clay_plus15_glass_office_tower` | `clay-plus15-glass-office-tower-clay-v006.glb` | calgary_plus_15_connected_tower / variant_2 | PASS, 0 / 0 |
| `tools/clay_arched_mill_mixed_use` | `clay-arched-mill-mixed-use-clay-v005.glb` | industrial_brick_mixed_use / variant_0 | PASS, 0 / 0 |
| `tools/clay_courtyard_mixed_use_midrise` | `clay-courtyard-mixed-use-midrise-clay-v009.glb` | rndsqr_terraced_mixed_use_midrise / variant_0 | 0 / 1 |
| `tools/clay_chamfer_corner_dome_block` | `clay-chamfer-corner-dome-block-clay-v006.glb` | barcelona_corner_chamfer / variant_0 | 0 / 2 |

The archetype ids are the keys used in `frontend/src/data/buildingArchetypes.json`; the
variant index is the catalogue variant whose three locked views (front, oblique, top) the
model was built from. Each family's `sources.json` and `evidence/vNNN/source-entry.json`
record the exact source image paths and hashes.

## 3. What each family folder contains

```
tools/clay_<family>/
  family_<name>.py     the whole building as parametric Python (constants at the top,
                       one function per elevation or assembly, build() at the bottom)
  build.py             CLI: renders the roster and writes the GLB and audit for a version
  lock_sources.py      copies and hashes the three locked catalogue views
  phone_board.py       builds the source-vs-render phone boards for a version
  sources.json         the locked source paths and hashes
  README.md            measurement contract, construction notes, version history and an
                       "Open blockers after vNNN" section listing exactly what is still wrong
  VERSIONS.md          one row per version: purpose, triangles, bytes, review counts
  candidates/          the one candidate GLB
  evidence/vNNN/       per version: build-report.json, carrier-aperture-audit.json,
                       prework-manifest.json, preservation.json, renders/*.jpg (18 views),
                       boards/*.jpg (4 phone boards), brief.md, independent-review.md
```

The generators share three helper modules found through `build.py`'s `sys.path`:
`tools/catalogue_services_batch/clay_core.py` (Blender primitives: `Face.wall/part/panel/
window/door/cut`, `box/prism/rod/beam/mesh/railing`, the aperture audit and the delivery
step), `tools/final_five_buildings/geometry.py` (`camera_roster`, `brick_courses`, `stair`)
and `tools/catalogue_affordable_five/assemblies.py` (`faces`, furniture, foliage).

To rebuild a family you need Blender 4.2 importable as the `bpy` module in a Python 3.11
environment (the previous sessions used a venv with the `bpy` wheel). Commands:

```
# quick check: three views, low samples, about two minutes
python tools/clay_energy_centre/build.py --version 11 --output /tmp/energy-v011 \
  --resolution 800 --samples 4 --cameras front,left_side,front_corner
# full roster: 18 views at 1440 px, 32 samples, about 40 minutes per building
python tools/clay_energy_centre/build.py --version 11 --output /tmp/energy-v011 \
  --resolution 1440 --samples 32
```

The output directory must not exist beforehand. `--cameras` must include `front_corner`
or the delivery step raises a KeyError. An exit code of 139 after `BUILD_COMPLETE` is
Blender's normal segfault on shutdown, not a failure. The build report's
`carrier_aperture_audit` must read `PASS_CARRIER_APERTURES`. After a full roster,
`python tools/clay_evidence_preserve.py --candidate <output dir> --family tools/clay_<family>`
copies the GLB into `candidates/` and the renders as JPEGs under 950 KB into `evidence/`.

## 4. Method and rules you must keep

The models follow the canonical building method in `docs/RLASM_LATEST_METHOD.md` and
`tools/archetype_compiler/rlasm_method.json` (RLASM v6.1 architectural clay). The working
rules that shaped every version:

- Judge only rendered pixels against the locked source pixels. Never take a build report,
  a triangle count or the builder's notes as proof that something looks right.
- Every version gets an independent review (a separate agent or person who did not build it)
  that writes `evidence/vNNN/review/independent-review.md` with a verdict
  (`PASS_ZERO_P0_P1` or `VISUAL_REWORK_REQUIRED`), counts, a findings table with pixel
  regions, and a line per earlier finding saying whether it is resolved in the pixels.
- The stopping rule is `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`: stop at
  PASS_ZERO_P0_P1, or after two consecutive reviews that fail to lower the P0 + P1 count, or
  when the same finding survives two targeted fixes. The best-reviewed version stays as the
  candidate; later versions are evidence only. Record reviewer disagreements, do not chase
  them.
- Never `json.dump` the archetype catalogues (`buildingArchetypes.json`,
  `streetPathArchetypes.json`, `openSpaceArchetypes.json`): a dump corrupts the thumbnail
  paths. Any catalogue edit is a text-level splice.
- Never enrol or publish a building, never claim keeper approval, never seed the runtime
  from these GLBs. Each README says `keeper_claimed=False`, `runtime_seed_allowed=False`.
  RLASM asset review, runtime acceptance and publication approval are separate human
  checkpoints; `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and
  `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` govern any runtime use.
- Keep the candidate GLB under 4 MiB as an ordinary git blob. Do not commit PNGs or any
  file over 1 MiB other than the candidate GLB. Renders and boards go in as JPEGs under
  950 KB.
- Do not force-push, and do not push to `main`; work on a branch and open a pull request.
- Keep the files the previous session used: a family's `VERSIONS.md` row and README
  "Open blockers" section must be updated for every new version.

## 5. Known defect classes to watch for

- Coplanar faces render as black flicker: offset abutting parts by 1 to 2 cm or make them
  share only an edge.
- The shared window helper in `clay_core.py` bevels its frame bars by 8 mm, which leaves a
  tiny black pocket at every window and door corner at 1440 px. Fixing it in the helper
  (no bevel on frame bars, or mitred corners) would clear it for all fifteen families; the
  rowhouse's proud reveal liners did not.
- Contract text can be wrong about the sources. The crane hall's "ridges across the hall"
  description sent two versions the wrong way; always re-read the source pixels.
- Critical geometry (building height, storey count, tower proportions) must be measured
  in the locked front and top together; the two can disagree by 10 to 15 percent and the
  reviewer will say which one they used.

## 6. Open findings on the six non-passed candidates

These are in each README under "Open blockers". In short:

- Fire station v009: the four apparatus bays have flat black headers where the source shows
  glazed transoms; replace the bay head panels with glazed transoms on the door grid.
- Hotel v007: the glazed lobby tower's banded header still stands proud of the main parapet;
  drop the header and tower roof about 0.9 m below the parapet cap, white membrane on the
  tower roof, carry the parapet and band behind it, taupe header.
- Rowhouse trio v009: the frame-corner voids (section 5) and a double-eave reading below the
  main front eave.
- Crane-way hall v007 (v008 is evidence only): the six aisle-roof monitors need turning 90
  degrees (ridge across the hall, glazed band under the west eave); gallery knee braces end
  in mid-air; the hooded aisle windows need jamb, head and sill returns.
- Courtyard mid-rise v009 (v010 is evidence only): v010 fixed the rear-bar roof plane but
  introduced a cedar band on faces the sources show as taupe and changed the east window
  rhythm; the right next step is v010's roof with v009's walls and eight to nine narrow
  staggered windows per floor on the east face.
- Chamfer dome block v006 (v008 and v009 are evidence only): v009's continuous ribs and
  copper cresting are right; still open are the dormer oculi (the glass disc sits too deep
  to read), the rib and dormer set being half a bay out of step with the source, the lantern
  (needs a glazed copper octagon with entablature, ribbed cupola and ball finial) and the
  rooflights (need a framed four-facet glazed pyramid).

## 7. Reports to read first

- `docs/showcase/TEN_BUILDINGS_REPORT_2026-10-10.md`: the ten civic and commercial
  buildings, their source mapping, review history and the reopened-run outcome.
- `docs/showcase/TOWERS_MIXED_USE_REPORT_2026-10-10.md`: the three towers and three
  mixed-use blocks, same structure.
- `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`: the stopping rule and the
  "Limit lifted" appendix that governs the current 4 MiB cap.
- `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md` and `docs/BUILDING_CATALOGUE_WORKFLOW.md` for
  how finished buildings are meant to reach the catalogue later.

## 8. What I want from you

State which of these you are doing before you start, and do one at a time:

1. Load the fifteen GLBs from the Drive folder (or the repository) and confirm each opens,
   reports its triangle count and bounding box, and matches the table in section 2.
2. If asked to continue a building, start from its family source, make one targeted change
   per open finding, quick-check it, run the full roster, get an independent review, and
   apply the stopping rule. Never silently replace a candidate with a worse-reviewed version.
3. If asked to use a model in City Prompt, follow `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`
   and complete the runtime review template for that exact variant before calling it ready.
   Do not touch `buildingArchetypes.json` without the text-level splice rule.
4. Report outcomes faithfully: say which version was reviewed, by whom, with what counts,
   and what is still open.

## 9. Addendum, 2026-10-13: five more buildings (wave C)

Five more families were added on the same branch after this handoff was written, bringing
the total to twenty. Their candidates and open findings are in
`docs/showcase/WAVE_C_FIVE_BUILDINGS_REPORT_2026-10-13.md`:

| family folder | candidate | catalogue archetype / variant | review |
|---|---|---|---|
| `tools/clay_baronial_railway_hotel` | `clay-baronial-railway-hotel-clay-v006.glb` | chateauesque_grand_railway_hotel / variant_0 | PASS, 0 / 0 |
| `tools/clay_grand_magasin` | `clay-grand-magasin-clay-v004.glb` | grand_magasin / variant_0 | 0 / 2 |
| `tools/clay_modernista_market_hall` | `clay-modernista-market-hall-clay-v003.glb` | barcelona_mercat / variant_0 | 0 / 3 |
| `tools/clay_second_empire_city_hall` | `clay-second-empire-city-hall-clay-v004.glb` | montreal_second_empire_civic / variant_0 | 0 / 3 |
| `tools/clay_zinc_dome_corner_block` | `clay-zinc-dome-corner-block-clay-v004.glb` | parisian_corner_with_dome / variant_0 | 0 / 1 |

These five GLBs run up to the 4 MiB cap (about 80,000 triangles). To try all twenty in a
browser, use `docs/showcase/CODEX_BROWSER_TRIAL_PROMPT_2026-10-13.md`.
