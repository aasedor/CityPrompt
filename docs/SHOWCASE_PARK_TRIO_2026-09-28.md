# Three native showcase gardens

Local pilot additions, requested for a colleague demonstration. Browser testing is deliberately deferred. These are not completed/runtime-approved catalogue entries.

| Park | Native footprint | Reviewed delivery |
|---|---|---|
| Woodland Stream & Bridge Garden | 46 × 58 m | showcase-woodland-v004 |
| Reflecting Fountain Garden | 34 × 48 m | showcase-reflecting-v002 |
| Terraced Café & Fountain Court | 40 × 48 m | showcase-court-v002 |

The source recipe, exact GLB, photographic picker hero, geometry report and exported-model visual ledger are retained in each `seed/classroom-parks/showcase-*` directory. Model identity, entrances, occupied bounds and content revision use the existing schema-v2 native park registry. Existing instances and variants are unchanged. Each layout requires prepared level ground and retains its native dimensions; surrounding parcels may change only while the intact layout fits.

The woodland garden has a winding stream, arched timber bridge and raked-gravel room. Its unseen plan is explicitly inferred. The fountain garden has a two-lobed basin, four water jets, continuous coping, clipped hedges and perimeter access. The café court adapts the reference's sunken composition to a flush entrance datum, with seven rising seat steps and physically supported perimeter terraces.

Offline evidence: `C:/dev-artifacts/CityPrompt/showcase-nine-2026-09-27/parks/`. Four actual reimported-GLB views per park were inspected: aerial, top, detail and walking height. No AI render was used as model acceptance evidence.

Verification: 38 backend/staging tests; 31 frontend park tests, including exact-model movement, rotation and JSON save/reload for these three layouts. Hash-verified staging checks all 31 park assets and embedded dependency closure. Runtime placement, frame rate, Walk and image capture remain NOT TESTED.

Reproduce registration with `scripts/register_showcase_parks.py --package <delivery>` and stage with `scripts/stage_native_parks.py --archive <hydrated runtime-assets.zip> --public-dir <public directory>`. Registrations reject different model bytes under these identities. Keep Blender authoring files, source views and large review renders outside Git.
