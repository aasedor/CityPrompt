# Autumn building trio — local candidates

Starting commit: 97caede53. Initiative branch: codex/catalogue-buildings-autumn.

Three additive RLASM v6.1 architectural-clay candidates are available in the local validation catalogue. They are not textured keepers or browser-approved completions.

| Model | Exact candidate | Native levels | Model bytes |
|---|---|---|---|
| Nordic Roof-Garden Apartments | autumn-timber-clay-v004 | 6 | 48,163,508 |
| Tuscan Arcade Villa | autumn-villa-clay-v004 | 3, including attic | 2,401,440 |
| Grand Deco Cinema | autumn-cinema-clay-v004 | 3 | 994,708 |

All preserve native geometry and fixed footprints. No storey or footprint deformation is added. Original catalogue bindings are unchanged. Photographic front references own picker heroes.

Exact source, model and independent review hashes are in the LFS-backed clay library and seed/classroom-buildings/autumn-selection.json. All three passed independent holistic source comparison with zero P0/P1 findings, including actual exported GLB reimport renders and phoneboards. Review addressed obstructed timber loggias, the villa's left arcade entrance and cinema marquee support/stepped footprint. Native vegetation retains shared materials; timber model size is a runtime performance risk to check.

Verification: promotion suite 18 passed/7 optional fixture skips; backend clay runtime 38 passed; focused frontend suites 17 passed after updating legacy parent-based catalogue expectations and 12-card pagination; TypeScript passed. Local storage install/readback verified all three exact objects and bindings. No paid generation, browser acceptance or push performed.

Rebuild: tools/autumn_buildings/prepare.py source-lock dry run; Blender tools/autumn_buildings/autumn_build.py with --kind, --version, --kit, --lock and a new external --output; independent review; scripts/autumn_buildings.py --package. A complete three-entry selection can then be staged/installed through scripts.classroom_buildings. Unreviewed versions remain external.

Generated build/review evidence: C:/dev-artifacts/CityPrompt/autumn-nine-2026-09-30/buildings/. Source controls, immutable selected GLBs and compact reviews are tracked; intermediate geometry, Blender files and rendered review images stay outside Git.
