# Autumn park trio — local validation candidates

Branch codex/catalogue-parks-autumn builds on building checkpoint c5261e5f2.

- Urban Splash-Play Plaza, autumn-splash-v002: 32 x 36 m. Crescent planted edge, flowing colour fields, six arched sprays, four flush jets and supported bucket. Static water geometry.
- Stone Labyrinth Garden, autumn-labyrinth-v005: 34 x 40 m. Six connected circuits with smooth turns, central stone bench, hedge and wall enclosure. 1.15 m circuit path; no universal-access certification claimed.
- Sheltered Dog Park, autumn-dog-v001: 36 x 42 m. Four turf rooms, three timber shelters, gravel circulation, containment fence, open entrance vestibule and planted borders.

Each exact native assembly owns its ground, retains its dimensions and uses prepared level terrain. Existing park bindings remain unchanged. Reference photographs are picker heroes. Meshes, recipes and review hashes are retained in seed/classroom-parks/autumn-*. Generated renders and rejected versions remain outside source under C:/dev-artifacts/CityPrompt/autumn-nine-2026-09-30/parks/.

All four reimported-GLB cameras were inspected for each selected model: aerial, top, detail and walking height. Refined sparse splash planting and folded labyrinth joins before registration. Shared native botanical plants and furniture maintain the existing material language. Source references and adaptations are recorded in recipes.

Checks: source image and delivered GLB hashes, embedded dependencies, finite metric bounds and triangle ceiling; frontend park identity/movement/save serialization, access, picker/search (31 tests); backend native parks (37 tests). Local staging verified all six new GLB/hero assets. Browser and paid-render acceptance remain NOT TESTED and completed=false.

Reproduce using tools/public_realm_assets/build_autumn_parks.py with a new external output, review it, then scripts/register_autumn_parks.py --package. Stage reviewed seed files with --public-dir. The general all-parks staging command needs the hydrated original runtime-assets.zip; this checkout holds its LFS pointer, so the finite autumn stager verifies and stages only this trio without replacing existing files.
