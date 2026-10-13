# Codex prompt: try the twenty clay buildings in the browser

Copy everything below the line into Codex as its first message. It asks Codex to build a
small standalone three.js viewer for the twenty RLASM clay building candidates, check it
with headless screenshots, and push it on its own branch. Nothing in the app, the archetype
catalogues or the runtime is touched. Background on the models is in
`docs/showcase/CODEX_HANDOFF_CLAY_BUILDINGS_2026-10-12.md`.

---

I want to look at twenty architectural-clay building models in a web browser. Build me a
small standalone viewer page, prove it works with screenshots, and push it to a new branch.
Read this whole message before starting.

## Where the models are

- Repository https://github.com/aasedor/CityPrompt, branch `claude/ten-new-buildings`.
- The models are `tools/clay_*/candidates/*.glb`, exactly one per family folder, twenty in
  total. They are ordinary git blobs (no Git LFS), each under 4 MiB.
- I may also have copies in a Google Drive folder, so the page must also open GLB files
  that I drag onto it or pick with a file button.

The GLBs are standard glTF 2.0 binaries: Y up, 1 unit = 1 metre, building centred near the
origin at grade y = 0, the main front facing +Z. They have no textures. Colour comes from
14 to 21 flat PBR materials per file, named `CLAY_<ROLE>` (for example `CLAY_STONE`,
`CLAY_GLASS`, `CLAY_ZINC`, `CLAY_ROOF`). Glass uses `KHR_materials_transmission` and
`KHR_materials_ior`, which three.js's `GLTFLoader` supports. Some nodes carry a translation
and scale, so measure bounds with `Box3.setFromObject`, never from accessor min/max.

## The twenty buildings

| # | building | GLB path (repository root) | bytes | review P0 / P1 |
|---|---|---|---|---|
| 1 | Campus shed office | `tools/clay_campus_shed_office/candidates/clay-campus-shed-office-clay-v009.glb` | 1,111,200 | PASS, 0 / 0 |
| 2 | LED grow block (vertical farm) | `tools/clay_led_grow_block/candidates/clay-led-grow-block-clay-v007.glb` | 790,632 | PASS, 0 / 0 |
| 3 | Cantilever fire station | `tools/clay_cantilever_fire_station/candidates/clay-cantilever-fire-station-clay-v009.glb` | 781,440 | 0 / 1 |
| 4 | Courtyard primary school | `tools/clay_courtyard_primary_school/candidates/clay-courtyard-primary-school-clay-v009.glb` | 1,009,176 | PASS, 0 / 0 |
| 5 | Limited-service hotel | `tools/clay_limited_service_hotel/candidates/clay-limited-service-hotel-clay-v007.glb` | 1,055,852 | 0 / 1 |
| 6 | Queen Anne rowhouse trio | `tools/clay_queen_anne_rowhouse_trio/candidates/clay-queen-anne-rowhouse-trio-clay-v009.glb` | 1,091,912 | 0 / 2 |
| 7 | Crane-way hall | `tools/clay_craneway_hall/candidates/clay-craneway-hall-clay-v007.glb` | 1,167,908 | 0 / 2 |
| 8 | Energy centre | `tools/clay_energy_centre/candidates/clay-energy-centre-clay-v010.glb` | 653,220 | PASS, 0 / 0 |
| 9 | Anchored plaza supermarket | `tools/clay_anchored_plaza_supermarket/candidates/clay-anchored-plaza-supermarket-clay-v010.glb` | 587,736 | 0 / 1 |
| 10 | Slab balcony tower | `tools/clay_slab_balcony_tower/candidates/clay-slab-balcony-tower-clay-v007.glb` | 1,020,940 | PASS, 0 / 0 |
| 11 | Brick podium condo tower | `tools/clay_brick_podium_condo_tower/candidates/clay-brick-podium-condo-tower-clay-v006.glb` | 1,024,756 | PASS, 0 / 0 |
| 12 | Plus 15 glass office tower | `tools/clay_plus15_glass_office_tower/candidates/clay-plus15-glass-office-tower-clay-v006.glb` | 910,328 | PASS, 0 / 0 |
| 13 | Arched brick mill mixed use | `tools/clay_arched_mill_mixed_use/candidates/clay-arched-mill-mixed-use-clay-v005.glb` | 744,024 | PASS, 0 / 0 |
| 14 | Courtyard mixed-use mid-rise | `tools/clay_courtyard_mixed_use_midrise/candidates/clay-courtyard-mixed-use-midrise-clay-v009.glb` | 958,528 | 0 / 1 |
| 15 | Chamfered corner dome block | `tools/clay_chamfer_corner_dome_block/candidates/clay-chamfer-corner-dome-block-clay-v006.glb` | 971,772 | 0 / 2 |
| 16 | Scottish Baronial railway hotel | `tools/clay_baronial_railway_hotel/candidates/clay-baronial-railway-hotel-clay-v006.glb` | 4,172,400 | PASS, 0 / 0 |
| 17 | Belle Epoque grand magasin | `tools/clay_grand_magasin/candidates/clay-grand-magasin-clay-v004.glb` | 4,177,416 | 0 / 2 |
| 18 | Barcelona Modernista mercat | `tools/clay_modernista_market_hall/candidates/clay-modernista-market-hall-clay-v003.glb` | 2,057,252 | 0 / 3 |
| 19 | Montreal Second Empire city hall | `tools/clay_second_empire_city_hall/candidates/clay-second-empire-city-hall-clay-v004.glb` | 3,768,468 | 0 / 3 |
| 20 | Parisian corner block with a zinc dome | `tools/clay_zinc_dome_corner_block/candidates/clay-zinc-dome-corner-block-clay-v004.glb` | 3,933,508 | 0 / 1 |

"Review" is the open P0 / P1 count from that version's independent visual review (P0 =
identity or geometry failure, P1 = clear mismatch with the source images). Show it in the
page as information only. None of these models is approved for the product.

## What to build

Create a new folder `tools/clay_viewer/` with:

1. `index.html`, `viewer.js` and `style.css`. Plain ES modules, no build step, no npm.
   Load three.js with an import map from `https://cdn.jsdelivr.net/npm/three@0.160.0/`
   (`build/three.module.js` and `examples/jsm/` for `GLTFLoader`, `OrbitControls` and
   `RoomEnvironment`). Pin that exact version.
2. `manifest.json`, generated by `tools/clay_viewer/make_manifest.py` (standard library
   only). The script globs `tools/clay_*/candidates/*.glb`, and for each writes the family
   folder, a display name, the GLB path relative to the repo root, the version, the file
   size, and the review counts from the table above. Run it and commit its output.
3. `README.md` with the two commands to view it (below) and one screenshot.

The page needs:

- A list or dropdown of the twenty buildings from `manifest.json`, plus a "Open GLB…"
  button and drag-and-drop for local files.
- A light grey ground plane, a hemisphere light, one sun `DirectionalLight` with soft
  shadows sized to the model's bounds, `RoomEnvironment` for reflections, ACES filmic tone
  mapping and sRGB output. The clay colours must not wash out to white or go muddy.
- `OrbitControls` with damping, the target at the model's centre, and near and far planes
  set from the model's size so nothing clips.
- Camera buttons that match the review renders, with r = 1.7 × the larger plan dimension
  and h = the model height: Front at (0, 0.48h, r), Oblique at (-0.78r, 2h, 0.84r),
  Aerial at (0.7r, 3h, 0.8r), Top (orthographic, looking straight down), Left at
  (-r, 0.6h, 0), Right at (r, 0.6h, 0) and Rear at (0, 0.6h, -r). All look at
  (0, 0.45h, 0) except Top.
- An info panel: name, version, file size, triangle count, width × depth × height in
  metres, material count, and the review counts.
- Toggles for wireframe, shadows and "hide site plate" (hides meshes whose material is
  `CLAY_FOUNDATION` only; other materials such as `CLAY_CONCRETE` are building fabric in
  some families), and a "Save PNG" button.
- When switching buildings, dispose the old model's geometries and materials so memory
  stays flat after twenty switches.

To view it, from the repository root:

```
python3 -m http.server 8765
# then open http://localhost:8765/tools/clay_viewer/
```

The server must run from the repository root so the page can fetch
`../clay_*/candidates/*.glb`.

## How to check it

Use Playwright with headless Chromium (WebGL via SwiftShader is fine). For each of the
twenty buildings, load it, wait for the model, take the Front and Oblique views at
1280 × 800, and save them as JPEGs in a scratch folder outside the repository. Then:

- Fail if the browser console shows any error, or if any GLB fails to load.
- Fail if a screenshot is more than 90 percent one colour (blank canvas or model off
  screen).
- Print a table: building, triangles, width × depth × height, load time in ms.
- Open at least five of the screenshots yourself and say what you see. Do not report
  success from the console output alone.
- Put one contact sheet of all twenty Oblique views, as a single JPEG under 950 KB, in
  `tools/clay_viewer/contact-sheet.jpg` and link it from the README.

## Rules

- Work on a new branch `codex/clay-viewer` started from `claude/ten-new-buildings`. Do not
  push to `main` or to `claude/ten-new-buildings`, and never force-push.
- Do not change, move or re-export any GLB, generator, evidence file or report.
- Do not touch `frontend/`, `backend/`, `frontend/src/data/buildingArchetypes.json` or any
  other archetype catalogue. Do not enrol, seed or publish any building and do not describe
  any of them as approved.
- Do not commit PNGs, the Playwright screenshots or any file over 1 MiB. The contact sheet
  is the only image you commit.
- Do not add a package.json, node_modules or a bundler to the repository. Install
  Playwright only in your scratch environment.

## What to send me back

1. The branch name and the commit.
2. The two commands to open the viewer.
3. The table from the check, the console-error count, and the contact sheet.
4. Anything that looked wrong in the screenshots, by building and view, in plain words.
