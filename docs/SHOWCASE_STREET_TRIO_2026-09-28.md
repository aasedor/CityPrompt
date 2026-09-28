# Three native showcase streets

These additions are local pilots. Browser testing, Walk and render capture are NOT TESTED at the user's request. No publication or completed-catalogue claim is made.

| Street | Section | Route range | Native program |
|---|---|---|---|
| Garden Tram Avenue | 22 m | 48–480 m, straight | Grass tracks, four rails, overhead wires, catenary masts, native trees and manually placed paired stops |
| Vine Pergola Promenade | 13 m | 36–480 m | Terracotta brick, vine-covered timber pergolas, iron waterside rail, benches, planted border and lanterns |
| Grand Haussmann Boulevard | 32 m | 48–480 m | Broad stone sidewalks, trees with grate wells, Morris columns, kiosks, lamps and benches |

The tram's inspection fixture illustrates one paired stop. Actual drawn routes start with **zero** stops. Existing right-click stop controls now also support the tram: each selected station places two complete native platforms with shelters, seating, flags and 1:12 end ramps. Stops require 15 m end clearance and 32 m separation. Shortening or bending an incompatible saved route is rejected; platforms never stretch or become automatic interval stations.

Each pilot retains its exact source recipe, reference-view thumbnail, native module bytes and offline visual ledger in `seed/classroom-streets/showcase`. Frontend and backend registry mirrors, immutable recipe/program/module hashes and module bounds agree. The previous capability fingerprint remains in history for existing projects. No existing street geometry is replaced.

Offline evidence lives in `C:/dev-artifacts/CityPrompt/showcase-nine-2026-09-27/streets/`. Aerial, top, detail and walking-height views were inspected from reimported GLBs. Promenade runtime metadata additionally records the four thin steel bed edges authored by `scene.bed`; it keeps the same source model hash and uses brick junction paving.

Checks: 59 focused frontend street tests, 22 backend/packaging tests, TypeScript type-check, registry parity/capability checks and diff whitespace checks. Source-program tests cover ground ownership, whole native module placement, route extension, stop positions and invalid-route rejection. Existing baseline Git LFS files were hydrated by exact hash for packaging tests, without staging those unrelated files.

Reproduce with `tools/public_realm_assets/build_showcase_streets.py` and `scripts/showcase_streets.py --package <delivery> ... --public-root <public directory>`. The stager rejects replaced identities and corrupted source/module hashes. Keep heavyweight Blender files and QA images outside the source tree.
