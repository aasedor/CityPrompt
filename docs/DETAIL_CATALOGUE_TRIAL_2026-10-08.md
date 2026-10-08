# Standalone detail catalogue — 8 October 2026

This bounded expansion exposes six existing separate models in addition to the
timber bench and three oak shapes. No embedded archetype geometry is extracted,
and no new binary assets or paid image/model generations were needed.

## Catalogue

| Category | Choices |
| --- | --- |
| Seating | Timber bench; accessible picnic table |
| Trees | Oak shapes 1, 2 and 3 |
| Street furniture | Waste/recycling bin; three-space bicycle rack; drinking fountain |
| Landscape | Boulder group; timber fence section |

Project toolbar → Edit details. Search by name or purpose, filter the category,
select an item, inspect its dimensions and add it. Objects use their original
metric dimensions and geographic project positions. Move, rotate, remove, Undo
and Save details retain the existing isolated-editor behaviour.

The registry uses existing GLBs in `landscape-pilots/neighborhood-rustic-v5` and
`park-kits/shared-park-equipment-v1`. Model bounds verified locally: ground is at
Y=0, so the shared renderer converts Y-up to local Z-up without stretching or
recentering the source. Catalogue dimensions are checked against source manifests.
The existing asset override provides hydrated GLBs locally; Git LFS remains the
source delivery mechanism. No generated output was copied into the repository.

## Persistence and controls

`props` is an optional third collection beside `benches` and `trees` in existing
project metadata. Each collection is limited to 256 objects. Model IDs are
allowlisted server-side, coordinates must be finite, IDs are unique across all
collections, and existing project permissions/revision checks remain in force.
An older client omitting props preserves them; an explicit empty list clears them.
The normal 3D scene cannot select these small detail meshes.

## Browser trial

Project **Bench detail editor · pilot**, ID
`099fdc75-8eb1-4849-b602-8eebecef296e`, localhost:5183.

Added all six new choices through the editor in front of the community hall,
between the hall and residential street. Tested search, category filtering,
placement, rotation, removal and Undo. Saved, inspected all six models in 3D,
repositioned the picnic table away from automatically planted foliage, then
reloaded. Three existing benches, three existing trees and all six new objects
persisted. Browser error log was empty after the reload.

Evidence outside the source tree:

- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/detail-catalogue.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/catalogue-six-objects-3d.png`

## Verification

- 44 frontend tests across catalogue, coordinate conversion, detail editing,
  bench layout, student workflow and neighbourhood park layout passed.
- Seven backend tests passed, including legacy saves, explicit removal,
  allowlisted models, invalid coordinates and cross-collection ID collisions.
- TypeScript, focused ESLint and diff whitespace checks passed.

## Pilot limits

The plan editor displays archetype outlines and added details; it does not yet
show every automatically placed object. Check placement in 3D after saving.
Object spacing prevents overlapping detail bases but is not an accessibility,
utility-service or construction clearance assessment. Fence sections are placed
individually, not drawn as a continuous fence. Embedded/automatically generated
archetype details remain outside this catalogue. Steep-ground, large-scale,
public-share and AI-fidelity limitations from the earlier pilot still apply.

Local source checkpoint only; no push or deployment requested.
