# Ten more streets — native asset batch

Initiative: `codex/ten-street-asset-batch`, based on `eb7ec7c20`.
User requested ten more streets, continuing the offline asset workflow with
browser testing deferred. No production catalogue/seed/runtime edits or push.

## Finite scope and pilot

Ten distinct reference-informed concepts: Neighbourhood Main Street, Protected
Cycle Avenue, Planted Service Lane, Transit Stop Street, Pedestrian Market
Street, Ruelle Verte Community Alley, Heritage Mews Lane, Waterfront Timber
Boardwalk, Playful School Street, Grand Promenade Boulevard.

Authoritative source images were inspected from
`frontend/public/archetypes/streets` in the primary local repository. Each exact
image is copied and hash-locked into its external package. Recipes separate
observed features from adaptations; dimensions are original concept sections,
not dimensions inferred as facts from a perspective image. Neighbouring
buildings, people and vehicles are omitted. Existing student IDs are untouched.

All ten dry runs passed before the main-street pilot. Four recipe tests passed.
Pilot: `C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/pilot/main_street`.
The actual exported/reimported GLB passed 1,422 material-aware clear-route rays,
18 endpoint rays, eight tree-root/well checks, native module envelopes and
ground contacts. Agent visual review of aerial, top, detail and street views
passed for the concept. Independent human and browser review remain pending.

Pilot/source checkpoint: `69786529a`. The remaining nine were generated in a
bounded two-worker batch. Final native checks and agent visual review pass all
ten. The companion JSON locks the exact accepted GLBs, modules, builder files,
reference images and forty reviewed native renders.

## Accepted delivery

Root: `C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22`.
Use the following exact packages; earlier experiments remain preserved.

| Kind / ID suffix after `student_` | Fixture m | Distinct details | Package |
| --- | --- | --- | --- |
| `main_street_v1` | 23 x 48 | Tree grates, heritage lanterns, parking and planted parklet | `pilot/main_street` |
| `cycle_avenue_v1` | 24 x 48 | Two-way cycle track, planted divider, bicycle symbols | `batch/cycle_avenue` |
| `planted_lane_v1` | 12 x 40 | Timber fences, running-bond paving, layered planting and rest bays | `revised/planted_lane` |
| `transit_street_v1` | 27 x 48 | Glazed shelter facing boarding area, stop pole and cycle crossings | `revised/transit_street` |
| `market_street_v1` | 18 x 48 | Striped stalls, fountain, cafe parasols and cobbles | `batch/market_street` |
| `green_alley_v1` | 11 x 40 | Timber planting boxes, vine trellises and community seating | `batch/green_alley` |
| `heritage_mews_v1` | 10 x 40 | Cobbles, lanterns, frontage planters and bollards | `batch/heritage_mews` |
| `boardwalk_v1` | 12 x 48 | Timber decking, physical guardrail, suspended hammocks and cafe seats | `batch/boardwalk` |
| `school_street_v1` | 18 x 48 | Blue play ribbon, yellow dots, hopscotch, cycle racks and timber seat walls | `revised/school_street` |
| `grand_promenade_v1` | 24.5 x 48 | Central tree promenade, news kiosk, flower/produce stall and outer lanes | `batch/grand_promenade` |

Each package contains an assembly GLB, separately reusable native-origin modules,
surface/placement recipe, archived references, builder sources, four renders and
an exact-candidate pending runtime form. The `delivery` folder contains aerial,
detail, top and street contact sheets, individual four-view review sheets,
accepted package index and a deduplicated `street-amenity-kit`: fourteen GLBs,
468,352 bytes total. Eleven amenity types are new; the cafe table, parasol and
seat wall reuse the existing sports/public-realm geometry.

`CityPrompt-ten-streets-3D.zip` at the external root bundles the ten accepted
packages, native amenity kit, forty native renders, review sheets and source
meadow kit. ZIP CRC verification passed: 271 files, 96,014,758 bytes. Its SHA-256
is recorded in `archive-check.json` and the companion repository manifest.
This is a local archive, not an uploaded backup or published catalogue.

Assemblies range from 0.90 to 2.79 MB and 18,516 to 195,616 triangles, with
18–193 mesh instances. These are offline budgets, not district FPS benchmarks.
All hardscape trees have physical wells; soft-ground trees retain planted beds.

## Verification and revisions

Four recipe tests and Python compilation pass. All ten delivered assemblies and
their module bytes passed final reimport, finite metric bounds, material-aware
clear-route and endpoint rays, root/well checks, image hashes, native module
envelopes, ground-contact ownership and amenity clearance checks: 12,078 route
rays and 44 tree-root checks in total, plus separate endpoint rays. Each passed
the 350,000-triangle and 12 MB fixture budgets. No frontend production code was
changed, so frontend type-check and browser acceptance are not claimed.

Visual review caught a road-facing shelter orientation error that ordinary
floor-clearance rays did not detect. The new horizontal front/rear ray check
fails the original `batch/transit_street` with "Transit shelter front blocks
road-facing boarding side" and passes `revised/transit_street`. The old package
remains explicitly failed. The other two revisions fill the service-lane beds
and match the school reference's blue/yellow paint. Original planted-lane and
school-street packages are superseded, not accepted deliveries.

Agent review inspected all forty accepted aerial/top/detail/street views from
the reimported GLBs. All ten pass the native concept review. This is separate
from independent human approval and runtime acceptance. No paid image calls,
browser session, protected Currie project modification, seed writes or push.

## Reusable method

- Metric band recipes own every floor cell. Fine stone/brick/cobble/deck patterns
  preserve world-space phase across cell partitions. No coplanar slab overlays.
- Furnishing bays preserve clear walks, cycle tracks and carriageways. Every
  hardscape tree goes through the shared physical tree-well preparation.
- Fourteen origin-based amenity types include lanterns, bollards, a glazed stop
  shelter, stop pole, market stall, fountain, planted trellis, timber fence,
  boardwalk guard, hammock and kiosk, plus three existing cafe/seating models.
- Render actual reimported GLBs, audit module bytes/envelopes/supports, retain
  exact image references and per-candidate pending runtime review forms.
- These straight, level fixtures are not route meshes. Runtime must rebuild
  bands on the shared sampled centreline/ground, place rigid modules at native
  scale and let the street network own junctions, crossings, ramps and endpoints.
  Never bend, stretch or repeat the full preview assembly.

Run `tools/public_realm_assets/run_street_batch.py` with an explicit `--kinds`
list, `--blender`, `--kit`, `--reference-root` and fresh `--output`; use `--dry-run`
first. The queue uses at most two workers, refuses existing packages and calls
`verify_street_batch.py` after each build. No paid APIs are called. Heavy GLBs,
reference copies and rendered images stay under the external artifact root.

All runtime gates remain **NOT TESTED**: Currie terrain/context, bent/reversed
routes, intersections, access connections, edit/Undo/Redo/reload and exact export.
Flush concept streets are not certified traffic, drainage or accessible designs.
