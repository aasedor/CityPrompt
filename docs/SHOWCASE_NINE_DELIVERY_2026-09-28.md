# Nine local showcase additions

The requested batch is installed in the approved-validation checkout on `codex/water-zone-clean3d`. The current student picker contains **23 buildings, 18 parks and 13 streets: 54 distinct placement choices**. These nine additions remain local pilots, with `completed: false` and runtime/browser status `NOT TESTED`. Existing projects and model bindings were preserved.

| Domain | New choice | Exact reviewed delivery |
|---|---|---|
| Building | Grand Iron & Glass Market | market clay v006 |
| Building | Gilded Terracotta Tower | tower clay v005 |
| Building | Living-Roof Aquatic Centre | aquatic clay v004 |
| Park | Woodland Stream & Bridge Garden | woodland v004 |
| Park | Reflecting Fountain Garden | reflecting v002 |
| Park | Terraced Café & Fountain Court | court v002 |
| Street | Garden Tram Avenue | tram v002 |
| Street | Vine Pergola Promenade | promenade v003 |
| Street | Grand Haussmann Boulevard | boulevard v001 |

The tram starts without stations. Students explicitly place paired stops using the route's stop controls. Its fixed section and route constraints protect complete platforms, shelter dimensions, track spacing and access ramps. Buildings and parks retain whole native compositions; streets use the native route/module programs. Photographic street-view references are used for picker cards.

## Verification completed

- All three buildings passed separate, holistic architectural-clay review against their three exact reference views and complete final exported-model image sets. No unresolved P0/P1 findings. This is not a textured-keeper or human runtime approval.
- All six parks/streets passed the recorded builder offline checks from aerial, top, detail and walking-height views of reimported GLBs.
- 142 focused frontend checks across 25 files passed after updating the historical 20/15/10 count fixture to 23/18/13; the affected five-test file was rerun successfully. TypeScript type-check passed.
- 52 integrated backend park/street checks passed. 51 Python building promotion/compilation checks passed, including native-scale placement of the three new buildings on original/enlarged plots and rejection of insufficient plots.
- Three new local building database bindings and object-store GLBs passed exact-byte readback. The additive installer refused overwrite of mismatched existing identities or objects.
- All 64 new public assets passed hash comparison through the actual local frontend HTTP server. The frontend and backend health requests returned 200.
- Diff whitespace checks passed. Commits contain explicit source/seed deliverables; generated render/authoring packages and preview sheets remain external. Prior hydrated files were not staged.

The tests exposed a sibling-variant restore bug, now fixed by matching both building parent and exact variant. Integration also normalized the combined catalogue JSON to UTF-8, preserving the café title and all existing records.

No browser sessions, student-project edits, paid AI renders, remote pushes or publication were performed for this batch. Browser placement, route editing, Walk, rendering, terrain interaction and frame rate still need the later student validation session.

## Records

- [Building details](SHOWCASE_BUILDING_TRIO_2026-09-28.md)
- [Park details](SHOWCASE_PARK_TRIO_2026-09-28.md)
- [Street details](SHOWCASE_STREET_TRIO_2026-09-28.md)
- Exact building selection: `seed/classroom-buildings/showcase-selection.json`, with model/review/source hashes in the canonical clay library.
- Exact park selection: the mirrored native park registry and `seed/classroom-parks/showcase-*` evidence.
- Exact street selection: mirrored native street registries and `seed/classroom-streets/showcase` module/source locks.

External evidence root: `C:/dev-artifacts/CityPrompt/showcase-nine-2026-09-27/`. The `showcase-nine-native-models.jpg` sheet shows actual model exports. `local-static-asset-verification.json` records all 64 served asset hashes. Full source locks, Blender files, final review images, phone boards and superseded candidates remain there.
