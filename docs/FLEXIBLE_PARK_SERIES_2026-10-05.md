# Flexible park series — 2026-10-05

Added two local draw-first pilots to the existing pocket park and linear greenway: **Flexible shade courtyard** and **Flexible meadow grove**. They reuse the exact existing `urban_pocket_park_v1` and `urban_pocket_park_v2` procedural kits, including their distinct modern/formal and meadow/grove appearances. This is a bounded two-design expansion, with no new generated asset batch or deployment.

Each choice has its own saved placement ID, programme key, searchable card and canonical discovery ID. The inspector retains all three supported pocket variants. The server rejects mismatched programme/variant pairs and requires an explicitly prepared site. Existing pocket envelope limits and greenway limits remain intact. The lawn/circulation and planting fit the polygon; rigid furniture is not scaled to fill it.

## Local pilot evidence

Agent-operated ordinary controls in disposable Currie project `45e678b9-4898-4ef5-a611-bec132511a3a`, Edge at 1420 × 1111:

- Courtyard: five-corner outline, renamed through the object panel and saved. Target 648.193 m², metric frame 36.606 × 22.711 m. Exact saved recipe hash `6314a09e04473ef705917a9b75495a60aa398240e2dc43d446fafc53652a8ee9`, appearance `modern_steel_turf_v1`, structure `formal_quad`.
- Meadow: six-corner concave outline, saved, undone and restored through Redo. Readback after Redo retains six corners and exact `urban_pocket_park_v2`; target 945.876 m², frame 41.208 × 35.372 m. Recipe hash `38c93098d9bab5549e0ebec5fdf235dda24b667cd62a6520271551ecc518169a`, appearance `natural_meadow_v1`, structure `naturalistic_grove`.
- Saved project reopened. The earlier pocket and both zoning-study layers remain saved. Reference layers were hidden through ordinary controls for visual inspection.
- The first meadow recovery attempt was interrupted by a local dev-server restart after Undo; its unsaved in-memory redo history was lost. A second finite drawing/Undo/Redo sequence succeeded without restarting. No other projects were changed.

The courtyard close view is still sparse and uses the existing procedural ground treatment. Neither thumbnail is an exact preview of every irregular fitted layout. Tree/furniture finish and path legibility need instructor visual review before calling these keeper designs. No habitat, stormwater or accessibility claim is made.

Per-exact-variant template reviews preserve applicable unrun gates:

- [Courtyard review](FLEXIBLE_PARK_REVIEW_URBAN_POCKET_PARK_V1_2026-10-05.md)
- [Meadow review](FLEXIBLE_PARK_REVIEW_URBAN_POCKET_PARK_V2_2026-10-05.md)

## Verification and remaining acceptance

Fifteen focused frontend tests and eight backend checks pass, including concave/triangular outlines, unsupported small plots, exact appearance/structure recipes, wrong-identity rejection, search/draw and saved registry identities. TypeScript, touched-file ESLint and the production build pass. Catalogue delivery verifies **97 production choices / 337 image-model dependencies / zero failures**; the local dev overlay also has ten previously sealed fixtures, outside the production roster.

Generated delivery packets, screenshots, builds and private DB fixtures remain outside committed source. Existing source images are reused without editing or generated substitutes. Live mixed building/street/park connectivity, sloped terrain, advertised extrema/full rotation, touch/iPad authoring and faithful presentation acceptance remain open. Natural terrain is deliberately unsupported for these shape-first choices. No building-family catalogue or sealed-wave approval status changed.
