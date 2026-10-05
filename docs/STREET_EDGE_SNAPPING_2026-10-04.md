# Closer street-edge snapping — 2026-10-04

This shared authoring change builds on runtime integrity repair `ab291d0a3`.
The initiative is `codex/street-edge-snapping-2026-10-04`, using the existing
maintenance checkout. It does not regenerate or activate any asset.

## Behavior

- Buildings and parks can attract to nearby constructed street edges within
  three metres, including the sidewalk rather than the carriageway centreline.
- Parks no longer receive the blanket extra three-metre street reservation.
  An angled or irregular park can meet an angled street at its closest boundary
  point without rotating or changing its outline.
- Reviewed native buildings retain their approved front/contact envelope.
  Buildings without a matching reviewed edge contract retain their full plot
  padding. The test roster now explicitly distinguishes the 26 declared contact
  contracts from the additional eight buildings without contact approval.
- Size, model identity and authored geometry stay unchanged. A small numerical
  margin avoids overlapping faces. Buildings use their existing front alignment;
  snapping does not rotate a manually oriented building.
- Every attraction candidate passes the existing boundary, collision and
  pedestrian-route checks. Detached side space, protected entrances, neighbouring
  park approaches and other plots remain reserved. Distant objects stay where
  they were placed. Saved designs are not automatically rearranged.
- The placement preview and live drag both pass the actual zone type to the
  shared snap resolver, so parks work even without a picker asset ID.

These are concept-placement clearances, not a statement of legal setbacks.
The street envelope comes from the existing shared section/mask resolver;
transparent unbuilt boundary setbacks are not treated as constructed sidewalks.
Native models with their own unreviewed internal plot padding retain that padding.

## Verification

69 tests passed across six targeted Vitest files: snap placement, reviewed building
edge placement, automatic entrances, geometry, pedestrian connections and
neighbourhood entrances. TypeScript type checking passed. Cases cover four street
orientations, an angled park, full-plot fallback for unknown revisions, preservation
of scale/rotation, neighbouring plots, site boundaries and protected approaches.
The two React call-site edits only pass the existing zone type; they add no state,
effects, requests or dependencies.

The browser pilot used the isolated copied Currie project on port 5177, backed
by `cityprompt_repairs_20261004`. Before editing, its zones were recorded outside
Git at `C:/dev-artifacts/CityPrompt/street-edge-snapping-2026-10-04/before-zones.json`.
The original application and database were not edited. The pilot moved one Rustic
Pocket Garden and one current Buff-brick infill. The building was explicitly
aligned to the adjacent straight street before moving it.

Saved-state measurement against the constructed street envelope found:

| Pilot | Earlier gap | Saved gap | Identity and plot size |
| --- | ---: | ---: | --- |
| Pocket garden | 8.182 m | 0.020 m | Preserved |
| Buff-brick front | 10.371 m | 0.007 m | Preserved |

Both saved placements passed the same shared collision/boundary checks. The park
kept its existing angle; undo and redo restored its previous and snapped positions.
The models rendered after saving and reloading. External before/after JSON, screenshots and
`saved-frontage-verification.json` record the pilot. These measurements demonstrate
that pilot; they do not approve unreviewed native contact contracts or all street
and park variants. No paid image generation was used.

The original runtime on port 5176 remains available. There are still nine registered
worktrees. The change is local; main-branch integration and publication are separate.
