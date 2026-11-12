# Building resize pilot — handoff

Branch: `claude/building-resize-pilot`, cut from `deployment-version`.
Written 2026-11-12 from a cloud sandbox. No 3D viewer, no database and no
`C:\dev-artifacts` were available there. Everything listed under
[Checks not run](#checks-not-run) is still open and is yours to do.

Nothing here is published. No catalogue entry, reviewed GLB byte, seed row or
deployment file changed. The pilot does not change the RLASM 6.1 method and
grants no keeper or runtime acceptance.

## What the pilot does

One building can now be fitted to any space in two ways.

- **Exact model** stretches the reviewed GLB independently in width and depth,
  70–140% per axis. Height scale stays exactly 1.
- **Shape freely** replaces the model with an outline the student draws. It
  compiles to `planned_massing`, keeps archetype, variant, storeys and floor
  heights, and is drawn with the building's own facade kit: window bays,
  recessed balconies, entrance, parapet and roof plant, on fixed modules that
  repeat and never stretch.

A stretch that leaves the band hands over to Shape freely automatically and
says so, before applying and again after reload.

## Gate

One flag pair, both default off.

| Side | Name | Where it is read |
| --- | --- | --- |
| Frontend | `VITE_ENABLE_BUILDING_RESIZE_TRIAL=true` | `buildingResizeTrialEnabled()` in `frontend/src/features/pickPlace/buildingResizeTrial.ts` |
| Backend | `ENABLE_BUILDING_RESIZE_TRIAL=true` | `enable_building_resize_trial` in `backend/app/core/config.py` |

With the flags off the pilot does not exist. The trial programme id is treated
like any unknown programme, and saved trial properties are ignored by the
planner, the editing tools and the viewer. Tests cover that state on both
sides.

Switch both flags together. One flag alone is a misconfiguration: a saved
trial building then fails its 3D update with a recipe-mismatch error.

## Asset chosen

**Aspen Terrace Seniors Apartments**

| Field | Value |
| --- | --- |
| Picker id | `final_seniors_apartments` |
| Archetype / variant | `final-seniors-apartments` / `final-seniors-apartments-v1` |
| Candidate | `final-seniors-apartments-clay-v003` |
| Family | `rlasm-clay-final-seniors-apartments` |
| Model | `seed/model-library/rlasm-architectural-clay/models/final-seniors-apartments-clay-v003.glb` |
| Bytes / sha256 | 3,097,336 / `9721947c0cf2f0ec6813c57e068fb34bd18d07ecbef15ca809b0e549d9823165` |
| Native size | 32.36 × 17.98 × 18.99 m, 5 storeys |
| Catalogue plot | 36.4 × 22.0 m |
| Review | `PASS_INDEPENDENT_ARCHITECTURAL_CLAY`, 0 P0, 0 P1, published `ready` |

Why this one:

- It is a five-storey apartment block with three repeating balcony columns
  on a rectangular plan. A regular block tolerates stretching better than a
  form whose identity is a corner or a court.
- Correction after rendering it: it is not a plain bar. One end has a
  single-storey lounge wing with a planted roof terrace. That wing, its
  furniture and its planting stretch with the rest of the model.
- It is small (3.1 MB), already published and hash-pinned, and has a reviewed
  entrance record, so the entrance check has real data.
- It has no reviewed side-clearance row and no dwelling programme, so the
  pilot invalidates no existing neighbour or housing claim.

Alternatives considered and set aside: the Calgary Beltline mid-rise is a
square mixed-use corner building, the Nordic Roof-Garden Apartments is nearly
square with a roof pavilion and a 48 MB model, and Switchback is four storeys.

Judgment call: this is a seniors' residence by programme. To pilot a different
block, change the single `families` entry in the tuning file. The script
refuses a model that is not in the reviewed clay library.

## Tune everything in one file

`frontend/src/data/buildingResizeTrial.json` holds every tunable. The backend
reads a byte-identical copy at `backend/app/data/buildingResizeTrial.json`.
After editing, run:

```bash
python scripts/building_resize_trial.py --write-mirror
python scripts/building_resize_trial.py
```

The frontend exposes the same values as named constants in
`RESIZE_TRIAL_SETTINGS` (`buildingResizeTrial.ts`).

| JSON key | Value | Meaning |
| --- | --- | --- |
| `stretch.minimum_scale` / `maximum_scale` | 0.70 / 1.40 | Exact model band per axis |
| `stretch.step` | 0.05 | Reserved for a slider; the inputs accept any size |
| `stretch.fit_plot_margin_m` | `null` | Clear space kept each side by Fit building to plot. `null` keeps the model's own plot margin (about 2.0 m) |
| `stretch.squeeze_on_plot_resize` | `true` | `true`: a plot made too small squeezes the exact model to fit. `false`: the model is left alone and the plot stops at the room it needs |
| `stretch.rigid_prop_materials` | `["CLAY_PLANTING"]` | Model parts with these material names keep their real proportions under a stretch |
| `stretch.rigid_prop_max_size_m` | 2.5 | Only parts up to this size count as props. Longer runs such as hedges stretch |
| `shape_freely.minimum_width_m` / `minimum_depth_m` | 9.0 / 9.0 | Smallest outline |
| `shape_freely.minimum_area_m2` | 100 | Stops thin slivers that pass the width test |
| `shape_freely.maximum_size_m` | 120 | Largest outline extent |
| `shape_freely.maximum_outline_points` | 24 | Corner limit |
| `massing.style` | `archetype_kit` | How Shape freely is drawn. `floor_lines_and_windows` is the plain fallback |
| `massing.kit.ground_floor_height_m` / `upper_floor_height_m` | 4.0 / 3.2 | Floor levels, measured from the model. Floor lines sit on them |
| `massing.kit.plinth_height_m` / `parapet_height_m` | 0.15 / 0.48 | Base band and parapet, measured |
| `massing.kit.window_bay_module_m` / `window_width_m` | 3.5 / 2.5 | Window bay module and window width |
| `massing.kit.window_height_m` / `window_sill_m` | 2.28 / 0.5 | Upper-floor window |
| `massing.kit.ground_window_height_m` / `ground_window_sill_m` | 2.87 / 0.42 | Ground-floor window |
| `massing.kit.loggia_bay_module_m` / `loggia_width_m` | 5.3 / 4.45 | Balcony bay module and opening |
| `massing.kit.loggia_height_m` / `loggia_depth_m` | 2.72 / 1.4 | Balcony opening height and recess depth |
| `massing.kit.loggia_min_wall_m` | 20 | Only a wall this long carries balcony columns |
| `massing.kit.corner_pier_m` | 0.55 | Solid wall at each end of a facade |
| `massing.kit.railing_height_m` | 1.05 | Balcony railing |
| `massing.kit.entrance_width_m` / `_depth_m` / `_height_m` | 9.2 / 1.6 / 3.85 | Entrance canopy on the front wall |
| `massing.kit.colors.*` | 12 colours | Measured from the model's materials. Glass and frame are darkened on purpose |
| `massing.floor_line_height_m` | 0.12 | Floor line band height |
| `massing.surface_offset_m` | 0.03 | Stand-off of frames and lines from the wall |
| `massing.bay_module_m`, `window_*`, `wall_end_margin_m`, `floor_line_spacing_m`, `floor_line_color`, `window_color` | | Used only by the plain fallback style |

A hard ceiling of 0.5–1.6 for the band lives in
`building_flex_contract.py` and the script. The file may narrow the band
freely. It cannot widen past that ceiling without a code change.

## How it works

### Saved state

All state is ordinary zone `properties` and `coordinates`, so undo, redo and
reload need no new storage.

| Property | Exact model | Shape freely |
| --- | --- | --- |
| `building_footprint_program_id` | `building-resize-trial-v001` | same |
| `building_footprint_mode` | `exact_model` | `shape_freely` |
| `building_footprint_width_scale` / `_depth_scale` | 0.70–1.40 | removed |
| `building_footprint_mode_reason` | removed | `stretch_out_of_band` after an automatic switch |
| `building_geometry_basis` | `placement_plot` | `drawn_footprint` |
| `pedestrian_building_entrance` | moved with the stretch | removed |
| Zone coordinates | the plot rectangle | the building outline |

A freshly placed building carries none of these. It stays undeclared, and is
planned exactly as before, until a student applies a trial control.

The uniform house-pilot field `building_footprint_scale` is never written, so
older code cannot mistake a trial building for a house-pilot one.

### Server authority

- `building_flex_contract.py` validates identity, mode and both scales against
  the packaged file. Client-claimed native dimensions are ignored. An invalid
  declared state fails closed with HTTP 409.
- `lego_assembly._fixed_landmark_is_select_and_place` gained an optional
  `resize_trial` contract. It returns `False` only for the module whose
  variant, candidate and sha256 the file pins, and only when the request
  declares the programme. Every other call path is unchanged.
- `_resize_trial_plan` emits `scale: [width, depth, 1.0]`, no quarter turn,
  and refuses a target outside the band or outside the plot.
- Shape freely is certified in `_assert_resize_trial_shape_freely`: it must
  arrive without a recipe, and its outline minimum is measured on the server.

### Facade kit for Shape freely

`buildLegoMassingKitData` in `legoMassingGeometry.ts` builds a complete shell
for any outline from the kit values. It measures nothing itself.

- **Vertical:** plinth, a 4.0 m ground floor, 3.2 m upper floors, parapet with
  a dark cap, flat roof and roof plant. A subtle line marks each floor.
- **Horizontal:** a wall of 20 m or more gets a window bay at each end and as
  many balcony bays as fit between them. A shorter wall gets window bays only.
  Whatever is left over becomes solid wall, shared between both ends.
- **Front:** the first drawn edge is the front. It carries the timber-fin
  entrance canopy, or a plain door when the wall is too narrow for it.
- **Check:** on a 24 m wall the kit gives window, three balconies, window,
  which is the model's own front.

The plain prism stays in place as the click and inspection target but is not
painted, because the shell has real recesses the prism would plug.

### Rigid props under a stretch

`keepPropsRigidUnderStretch` runs on the viewer's own clone of the exact model
before the stretch is applied. Small planting keeps its shape and moves to
where the stretch puts it, so a tree stays a tree. It changes geometry copies
only. The cached GLB and its bytes are never touched.

### Review page

`frontend/resize-pilot-review.html` renders the reference images, the exact
model and Shape freely side by side with the real code, so proportions and
colours can be tuned without a database. See
[Tune by eye without a database](#tune-by-eye-without-a-database).

### Editing

- `assetForZone` returns the trial view of the asset: a resizable plot for
  Exact model, an `authored_footprint` outline for Shape freely. The park
  outline editor (corner drag, add point, resize keeping shape) is reused
  as it is.
- A plot edit that leaves too little room squeezes the building in the same
  save (`resizeTrialPlotReshape`), so undo restores both together. Set
  `stretch.squeeze_on_plot_resize` to `false` to switch that off.
- Typing a larger building grows its plot. A plot is never shrunk by a
  building edit.

## Files changed

Backend

- `backend/app/core/config.py` — the setting.
- `backend/app/services/building_flex_contract.py` — trial contract and validation.
- `backend/app/services/lego_assembly.py` — explicit opt-out and the stretch plan.
- `backend/app/api/v1/lego_assembly.py` — plan field, strict plan, Shape freely certification.
- `backend/app/services/model_contract.py` — a freely shaped outline is a floor plate, not a plot.
- `backend/app/services/building_placement_edges.py` — reshaped building keeps its whole polygon.
- `backend/app/services/residual_landscape.py` — stretch joins the source fingerprint.
- `backend/app/data/buildingResizeTrial.json` — server copy of the tuning file.
- `backend/tests/test_building_resize_trial.py`, `backend/tests/test_building_resize_trial_script.py`.

Script

- `scripts/building_resize_trial.py` — offline verification, dry-run by default.

Frontend

- `frontend/src/data/buildingResizeTrial.json` — the tuning file.
- `frontend/src/features/pickPlace/buildingResizeTrial.ts` — flag, constants and all trial logic.
- `frontend/src/features/pickPlace/assetRegistry.ts` — `footprintProgram.mode` gains `independent_horizontal_scale`.
- `frontend/src/features/pickPlace/catalogue.ts` — `assetForZone` applies the trial.
- `frontend/src/features/pickPlace/BuildingDesignControls.tsx` — width, depth, Fit building to plot, the mode toggle, handover.
- `frontend/src/features/pickPlace/ReshapePanel.tsx` — resizable plot, outline tools, live figures.
- `frontend/src/features/pickPlace/buildingPlacementEdges.ts`, `nativeBuildingContract.ts`, `representationNotice.ts`, `useAutomatic3D.ts` — guards and wording.
- `frontend/src/features/legoAssembly/communityCompiler.ts`, `legoAssemblyApi.ts`, `nativeClayPlacement.ts` — stretch targets, explicit massing, centring.
- `frontend/src/components/viewer/globe/legoMassingGeometry.ts`, `GlobeLegoAssemblyLayer.tsx` — the facade kit, and the plain floor-line fallback.
- `frontend/src/features/legoAssembly/resizeTrialRigidProps.ts` — planting keeps its proportions under a stretch.
- `frontend/resize-pilot-review.html`, `frontend/src/review/resizePilotReview.tsx` — the review page.
- `frontend/src/components/viewer/globe/GlobeEditMode.tsx` — plot corner handles for the exact model.
- `frontend/src/features/projects/ProjectViewPage.tsx` — save path.
- `frontend/scripts/public-env.mjs`, `public-env.test.mjs` — flag added to the browser env allowlist.
- `frontend/src/data/runtimeAssetManifest.json` — three new source files registered.
- Seven new or extended test files beside the code they cover.

Docs

- `docs/BUILDING_RESIZE_PILOT_HANDOFF.md` — this file.

## What was relaxed, and why

No production gate and no existing test was weakened. Each item below is
either flag-gated or additive.

Two items depart from `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` on purpose, for
this one building and only with the flag on. They are the point of the pilot,
and they are yours to accept or reject after you see it:

- **Gates C2 and B1 expect native scale to be preserved.** Exact model
  stretches the reviewed GLB. That is the feature you asked for.
- **Gate C2 says a plot resize must not stretch a native model.** It names
  houses, courts and street sections. With `squeeze_on_plot_resize` on, a plot
  made too small squeezes this mid-rise. This was my judgment call, so that
  dragging a plot into a tight space fits the building in one move. Set the
  key to `false` and the only things that stretch the model are the width and
  depth inputs and Fit building to plot.

Record both in the runtime review for this variant. Neither is claimed as
passed.

| Change | Why | Scope |
| --- | --- | --- |
| `_fixed_landmark_is_select_and_place` accepts an explicit trial contract | You asked for an explicit opt-out, not a looser default | Flag on, pinned bytes, declared programme |
| Band 0.70–1.40 with its own 0.5–1.6 ceiling | The house clamp (0.75–1.25, axis ratio 1.20) is untouched, so the pilot needed a separate bound | Trial contract only |
| Fixed plot becomes resizable, minimum 26.7 × 16.7 m | A building cannot be fitted to a space while its plot is locked at 36.4 × 22 | Flag on, this asset |
| Plot coverage check uses a 1 mm buffer | A plot saved in degrees drifts by fractions of a millimetre when moved | Trial plan only |
| A recipe-less Shape freely building is accepted as massing | Otherwise the server answers "an exact family is available" and refuses it | Flag on, validated mode |
| `uses_placement_plot` is false for Shape freely | The outline is the floor plate, so the report may measure it | Flag on, validated mode |
| A reshaped building claims no dwelling programme | It is no longer the reviewed model | Flag on. This asset has none today |
| Reshaped building keeps its whole polygon as contact envelope | Reviewed side clearances describe the native model only | Independent of the flag. This asset has no row today |
| Stretch joins the compiled source fingerprint | A stretch that leaves the polygon alone must still mark the compile stale | Only zones declaring the programme. All other hashes are unchanged |
| Whole-model centring also accepts the planner's `fit.resize_trial` marker | The checklist requires the planner's explicit native lock for that path. A stretch is not locked, so the planner sends an explicit marker of its own | Server-produced marker only |
| The plain massing prism is not painted when the facade kit draws the building | The kit has real balcony recesses that the prism would plug. The prism still takes clicks and inspection | Flag on, Shape freely, kit style |
| Planting geometry is copied and reshaped per stretched building | So trees and shrubs keep their proportions. The cached GLB is untouched | Resize-trial plans at a stretch other than 100% |
| Flag added to `PUBLIC_ENV_NAMES` and to its test fixture | That gate strips every unlisted `VITE_` name, and its test requires each consumer to be listed | One name |
| Three entries added to `runtimeAssetManifest.json` `sourceInputs` | The manifest check lists every reachable source file | Hand-inserted, see below |

## Tests run

Run in the sandbox on this branch.

| Check | Result |
| --- | --- |
| `pytest tests/test_building_resize_trial.py tests/test_building_resize_trial_script.py` | 78 passed |
| Backend neighbours: flex contract, house pilot, placement edges, towers, brick podium, clay runtime, lego assembly, residual landscape, student report, native home plot | 427 passed |
| Full backend suite `pytest tests/` | 3,415 passed, 74 skipped, 15 failed, 16 errors. The 31 are pre-existing, see below |
| `ruff check .` and `black --check --line-length=120 .` in `backend/` | Passed |
| New frontend tests (7 files) | 76 passed |
| Full frontend suite `npx vitest run` | 4,604 passed, 47 skipped, 6 failed. The 6 are pre-existing, see below |
| `npm run type-check` | Passed |
| `npx eslint --max-warnings=0` on every changed frontend file | Passed |
| `npm run check:dead-code` | Passed |
| `node --test scripts/public-env.test.mjs` | 4 passed |
| `python scripts/building_resize_trial.py` | Verified offline, model bytes matched the pin |

The failures are not from this branch. I ran the same files on an untouched
`deployment-version` worktree and the failing sets were identical. They need a
database or Git LFS asset bytes that the sandbox does not have.

| Suite | File | Failing in sandbox |
| --- | --- | --- |
| Backend | `tests/test_archetype_model_cache.py` | 7 failed, 7 errors |
| Backend | `tests/test_library_first_generation.py` | 6 errors |
| Backend | `tests/test_processing_cache.py` | 3 errors |
| Backend | `tests/test_classroom_model_library.py` | 3 failed |
| Backend | `tests/test_claude_five_library.py` | 1 failed |
| Backend | `tests/test_drawn_bridge_routes.py` | 1 failed |
| Backend | `tests/test_native_bridge_release.py` | 1 failed |
| Backend | `tests/test_project_details.py` | 1 failed |
| Backend | `tests/test_source_span_bridges.py` | 1 failed |
| Frontend | `src/components/viewer/globe/publicRealmOwnership.asset.test.ts` | 4 failed |
| Frontend | `src/features/parks/sandyBeach.test.ts` | 2 failed |

Run both full suites on your machine, where the fixtures are hydrated, before
relying on these numbers.

`python -m tools.catalogue_promotion check --metadata-only` also passed with
88 buildings, unchanged.

The tests found and fixed two real defects before you saw them: a number input
whose step made the browser refuse 32.36 m, and a ragged plot minimum that
made it refuse round sizes such as 30 m.

## Checks not run

None of these were run. Do not read any of them as passed.

**Visual, in the 3D viewer**

- The stretched model at 70%, 100% and 140% on each axis, and at 70% × 140%.
- Balconies, windows, entrance canopy and roof edge under stretch.
- Floor lines and window bays on a rectangle, an L shape and a rotated outline.
- Z-fighting between the dressing and the massing wall, near and far.
- Massing wall colour against the dressing colours.

**Runtime, against a real model library**

- `/api/v1/lego-assembly/plan` returning `fit.resize_trial` for this model.
- A full compile of a stretched building and of a Shape freely building.
- Ground contact and the foundation surface when scale is not 1.
- Entrance approach path to a street after a stretch.
- Picking a new entrance step on a stretched model.
- `buildingPlacementEdges` snapping beside a neighbour when scale is not 1.
  This asset has no side-clearance row, so its plot is its envelope. That is
  covered by unit tests only.
- Undo, redo and reload in the browser. Covered by unit tests only.
- Dragging plot corners and outline corners on the globe. Handle counts are
  unit tested; the drag itself is not.
- Direct 3D capture and any AI render of a trial building.
- The student planning report with a Shape freely building.

**Tooling**

- `npm run check:runtime-assets`. It cannot finish in the sandbox: it reports
  376 missing asset files on untouched `deployment-version` too. The three new
  `sourceInputs` lines were inserted by hand and checked with a copy of the
  generator's own source walk (680 expected, 680 recorded). Run
  `npm run check:runtime-assets` locally and regenerate if it disagrees.
- `npm run test:e2e` (Playwright).
- `python scripts/building_resize_trial.py --check-database`.
- `python -m tools.catalogue_promotion check` without `--metadata-only`. No
  catalogue entry changed.
- `npm run build`.

Per `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`, a materially revised building
variant needs `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` completed before its
student runtime integration is called ready. That review is not done. It
needs the viewer.

## What the review page showed

I rendered the review page in headless Chromium with software rendering and
compared it with the archetype reference images. The page uses its own
lighting and has no globe and no database. These are observations to guide
tuning. They are not passed checks, and the screenshots are not committed.

- **Shape freely now reads as the same building.** On a 24 × 16 m block the
  kit gives the model's own front: framed end windows with curtains, three
  timber-lined balcony columns with railings, the timber-fin entrance, a dark
  parapet cap and roof plant.
- **It holds on awkward outlines.** A 50 m bar, an L shape, a five-corner
  outline, the 9 × 12 m minimum and a 90 m bar all drew cleanly. Balcony
  columns appear only on long walls.
- **Trees and shrubs keep their shape at 70% and 140%.** Before this change
  they went thin and fat.
- **Still stretched on the exact model:** terrace furniture, the umbrella and
  the rooftop units, and every window and balcony. Windows are narrow at 70%.
- **The kit's glass and frames are darker than the clay model's.** That was
  deliberate, to read like the reference. It means Shape freely has stronger
  window contrast than Exact model.
- **Not like the reference, and not addressed:** brick texture, lit interiors,
  planting and paving around the building. The model is architectural clay by
  design, and the surroundings belong to the site, not this pilot.

## Needs tuning by eye

1. **The band.** 0.70 and 1.40 are your numbers. Windows are narrow slots at
   70% and balconies are wide at 140%. Judge both in the viewer.
2. **Glass and frame colour.** The kit uses darker glass and frames than the
   clay model. Lighten `colors.glass` and `colors.frame` if Shape freely should
   match Exact model more closely than the reference.
3. **Balcony rule.** Balcony columns go on every wall of 20 m or more. Raise
   `loggia_min_wall_m` if side and rear walls should stay plain.
4. **Entrance canopy.** It projects 1.6 m beyond the drawn outline, as the
   model's does. Set `entrance_depth_m` lower if that crowds a street.
5. **Roof plant on small roofs.** The largest unit looks heavy on a 9 m block.
6. **Surface offset.** 0.03 m may z-fight at distance on some GPUs.
7. **Minimum size.** 9 × 9 m and 100 m² allow a small point block.
8. **Fit margin.** `null` keeps about 2 m each side. Set `0` for buildings
   that should meet the plot edge.
9. **More rigid props.** Only planting is rigid. Furniture shares materials
   with facade parts, so it was left to stretch rather than risk gaps.

## Known limits of this first pass

- Shape freely drops the entrance connection. The reviewed entrance returns
  when the building goes back to Exact model.
- Returning to Exact model starts from the nearest size the model can take and
  builds a new rectangular plot around it. Check that plot for overlaps.
- Storeys cannot be edited in Shape freely. You asked for storeys and floor
  height to be kept, so they follow the exact model.
- A stretched model has no interior walking. The viewer already skips walking
  for any scaled module.
- The legacy 2D map editor saves coordinates without the squeeze rule. The
  globe editor and the panel both use it.
- With the flags switched off later, a stretched building returns to the
  exact model at 100% when its plot still holds it, otherwise to plain design
  massing. A Shape freely building becomes plain massing or the exact model.
  Nothing is deleted, and switching the flags back on restores it. Existing
  buildings keep their last compiled look until their next edit or Retry.
- Dwelling counts for a stretched or shaped building are not modelled.
- The kit's windows are flat panels and its shell has no interior.
- The kit takes its storeys from the saved building and its floor heights
  from the kit. Its walls top out at the parapet, 17.4 m. The server still
  records the model's full 19.0 m, which is where the roof plant ends.
- Place another, from a stretched or freely shaped building, places a fresh
  exact model on its catalogue plot. The stretch is not copied.

## Switch it on locally

1. Get the branch.

   ```bash
   git fetch origin
   git checkout claude/building-resize-pilot
   ```

2. Verify the contract offline. This reads repository files only.

   ```bash
   python scripts/building_resize_trial.py
   ```

3. Start the backend with the flag.

   PowerShell:

   ```powershell
   cd backend
   $env:ENABLE_BUILDING_RESIZE_TRIAL = 'true'
   uvicorn app.main:app --reload --port 8000
   ```

   bash:

   ```bash
   cd backend && ENABLE_BUILDING_RESIZE_TRIAL=true uvicorn app.main:app --reload --port 8000
   ```

   Or add `ENABLE_BUILDING_RESIZE_TRIAL=true` to `backend/.env`.

4. Start the frontend with the flag.

   PowerShell:

   ```powershell
   cd frontend
   $env:VITE_ENABLE_BUILDING_RESIZE_TRIAL = 'true'
   npm run dev
   ```

   bash:

   ```bash
   cd frontend && VITE_ENABLE_BUILDING_RESIZE_TRIAL=true npm run dev
   ```

   Or add `VITE_ENABLE_BUILDING_RESIZE_TRIAL=true` to the `.env` file your
   Vite setup already reads for `VITE_API_URL`.

5. Optional, read-only. Confirm your local library holds the pinned model.

   ```bash
   python scripts/building_resize_trial.py --check-database
   ```

   It prints `binding` and `object` as `verified` when the installed row and
   stored bytes match. It never writes. If the row is missing, install the
   clay library the usual way; this pilot adds no rows of its own.

6. On `localhost:5174`, place **Aspen Terrace Seniors Apartments** and select
   it. The panel shows **Fit this building to your space**.

Suggested first run: set width 38 m and apply; drag a plot corner inward; press
Fit building to plot on a 60 m wide plot and read the handover label; switch
to Shape freely, add an outline point and drag it; undo back to the start;
reload.

## Tune by eye without a database

The review page needs only the frontend dev server.

```powershell
cd frontend
$env:VITE_ENABLE_BUILDING_RESIZE_TRIAL = 'true'
npm run dev
```

Then open `http://localhost:5174/resize-pilot-review.html` with one of:

| Address ending | Shows |
| --- | --- |
| `?view=compare&model=<GLB URL>` | Reference images, exact model and Shape freely side by side |
| `?view=stretch&model=<GLB URL>` | The exact model at six stretches |
| `?view=massing` | The facade kit on six outlines |
| `?view=panel-exact`, `panel-stretched`, `panel-free-auto`, `panel-free-l` | The panel in each state |

`<GLB URL>` is any address your browser can load
`final-seniors-apartments-clay-v003.glb` from, for example your local file
API. Without it the massing and panel views still work. Edit
`buildingResizeTrial.json`, save, and the page reloads with the new values.

## Switch it on in staging

Staging is defined in `render.staging.yaml`. That file is unchanged.

1. Merge or deploy this branch to staging by your normal reviewed route.
2. In Render, add `ENABLE_BUILDING_RESIZE_TRIAL=true` to
   `cityprompt-staging-api`. Add it to the four workers too
   (`-images`, `-maintenance`, `-general`, `-scheduler`) so every process
   reads the same setting.
3. Add `VITE_ENABLE_BUILDING_RESIZE_TRIAL=true` to the static site
   `cityprompt-staging-web`.
4. Redeploy the API and workers, then trigger a manual deploy of
   `cityprompt-staging-web`. Vite flags are baked in at build time and that
   site has auto-deploy off.
5. Confirm the staging library holds the pinned model before inviting anyone.

To switch off, remove both variables and redeploy both sides.

## Commits on this branch

1. `feat(resize-pilot): server contract for stretching one mid-rise`
2. `feat(resize-pilot): offline verification script, dry-run by default`
3. `feat(resize-pilot): frontend trial logic, compiler and massing dressing`
4. `feat(resize-pilot): stretch controls, Shape freely and live figures`
5. `feat(resize-pilot): make the plot squeeze a named, switchable setting`
6. `docs(resize-pilot): handoff`, then a correction after the first renders
7. `feat(resize-pilot): draw Shape freely with the building's own facade kit`
8. `feat(resize-pilot): review page for tuning by eye`
9. `docs(resize-pilot): record the facade kit, rigid planting and review page`
