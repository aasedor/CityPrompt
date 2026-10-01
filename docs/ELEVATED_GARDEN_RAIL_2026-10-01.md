# Elevated Garden Rail — local runtime review

One original elevated rail street, added on `codex/elevated-rail-street` from
`a3a6c4114`. It is available in the local Streets → Transit catalogue.
Publication and human visual approval remain separate from this author review.

## Design and supported use

- Exact variant: `student_elevated_garden_rail_v1`; parent: `elevated_garden_rail`.
- A 26 m corridor with a 10.4 m concrete viaduct, twin tracks, a static two-car
  metro train, parapets, end buffers, maintenance gates, bearings and drainage.
- Two 3.5 m paths beneath the deck, a 4 m outer promenade, a 3 m cycle path,
  planted strips, shade trees, benches and lighting. Trees have soft planting
  below them. The deck underside is approximately 6.3 m above prepared ground.
- Straight routes from 48–288 m on a cleared, level site. Deck, rails and ground
  extend continuously. Complete native supports repeat with spans no longer
  than 22 m, including supports near both ends at arbitrary route lengths.
- The train and furniture retain their authored sizes. Tracks are protected
  from pedestrian access. This version has no passenger station, rail junctions
  or transport animation. Other streets must remain outside its corridor;
  unsupported overlaps are rejected on the client and server in either edit
  direction. The ordinary road graph excludes this elevated railway.

The preview fixture measures 26 × 48 m and contains 294,073 triangles. Ten
independent GLB modules are reused in the app. The whole preview assembly is
never stretched. All runtime modules are self-contained and hash verified.

## Exact candidate and evidence

The machine-readable companion records source, assembly, program and module
SHA-256 values: [ELEVATED_GARDEN_RAIL_2026-10-01.json](ELEVATED_GARDEN_RAIL_2026-10-01.json).

- Source delivery: `seed/classroom-streets/elevated-rail-v001`.
- Generator: `tools/public_realm_assets/build_elevated_rail.py`.
- Registration/hydration: `scripts/elevated_rail.py`.
- Evidence: `C:/dev-artifacts/CityPrompt/elevated-rail-street-2026-10-01`.
- Disposable project: `http://localhost:5186/projects/d52ba95f-f099-4e8e-a4b3-26142f28bdcd`.
- Reviewer: Codex author inspection; desktop Chromium, 1264 × 625 viewport.
- Source inspection used the actual exported/reimported GLB, including aerial,
  detail and pedestrian views. The catalogue image depicts that exact asset.

The finite generation batch comprised a dry run and three candidate deliveries.
Pilot 01 established the section. Pilot 02 added planting and rounded train
corners but failed the complete canopy bounds check. Pilot 03 moved the west
trees inward and passed. Only pilot 03 was promoted. Earlier candidates and
render output remain outside the repository.

## Runtime checks

The site and railway were drawn through the normal student controls. No API
geometry writes or injected camera poses were used. Read-only API and scene
inspection verified saved identity, hashes, module readiness and ground state.

| Gate | Result and scope |
| --- | --- |
| C1 Identity | Exact catalogue card, backend capability and ten module bindings agree. The same zone ID survives editing and reload. |
| C2 Dimensions | Fixed width; minimum, maximum, arbitrary residual lengths, reversed and rotated routes tested. Rigid structural modules remain at scale 1. |
| C3 Ground | Prepared-level placement and movement pass with no grounding issues. Natural/sloped terrain is unsupported and rejected. |
| C4 Freshness | Readiness requires current geometry and exact module counts. During extension the updating state blocked readiness; the completed revision passed. |
| C5 Pedestrians | Both under-deck paths traversed in both directions with ordinary keyboard input, 5,060 samples in 202.4 seconds. Feet remained at one ground elevation throughout; zero browser errors. Column collision, side-sliding, retreat and all three clear paths also have focused tests. |
| C6 Edits | Endpoint drag extended 125.079 m to 148.242 m; Undo restored the former; Redo and reload restored the latter. A subsequent whole-route move retained width, length and complete modules. Add bend is disabled. |
| C7 Recovery | Unsupported bends, overlaps, lengths and public-road connections reject. Changed packaged module bytes fail verification. Interrupted navigation, failed-save conflict recovery and missing module recovery were not separately induced for this candidate. |
| C8 Visual/capture | Actual native aerial and pedestrian views inspected. Exact live capture result is recorded in the companion JSON. Paid AI output was not submitted. |
| C9 Ordinary controls | Catalogue discovery, draw, prepared site, select, endpoint edit, move, Undo, Redo, reload and Walk exercised in the disposable project. |

Initial placement mounted 356 native components. The extended, reloaded and
moved route mounted all 412 required components. Readiness passed after each
operation. The first automated walking attempt lost held-key input; a fresh
keydown resumed movement at the same location. Repeating keydown events in the
test driver completed the full route. The application collision code did not
block movement at that pause.

Mixed building/park access, public street intersections, stations, sloped
contacts and human visual approval are not claimed by this review. The
prepared site itself has a visible flat perimeter; surrounding map geometry
is context, not part of the authored rail asset.

## Verification and delivery

- 130 focused frontend tests pass, including catalogue category, continuous
  deck/rails, native module repetition, walking and existing street regression
  checks. TypeScript type-check passes.
- 59 backend tests pass, covering exact native capabilities, identity, route
  limits, overlap protection, road graph and zone helpers.
- Two packaging tests pass. A fresh external public directory was hydrated
  from the seed after verifying module, assembly, recipe and build-source hashes.
- Frontend/backend native street manifests match. The runtime asset manifest
  is current (4,660 required file records). Its refresh also includes already
  committed catalogue additions; no previous model bytes were changed. The
  entire historical release package is not hydrated in this local checkout.
- Reviewed binary assets use Git LFS. Source snapshots preserve their exact
  bytes on Windows and Linux. Images and full experiment outputs stay outside
  the source tree, apart from the intentional catalogue thumbnail and seed.
- Pre-existing street thumbnails and hydrated reference output were preserved
  and excluded from staging. No push or deployment was performed.

To restore this asset after hydrating its Git LFS seed:

```powershell
python scripts/elevated_rail.py --from-seed --public-root frontend/public
```

The archived generator uses the shared native kit identified by `kit_sha256`
in `source-recipe.json`; that kit is an external build input. Runtime hydration
uses the packaged GLBs and does not require Blender or that build kit.
