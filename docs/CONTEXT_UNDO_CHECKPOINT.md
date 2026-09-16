# Boundary context and undo checkpoint

Creating a site boundary starts a background OpenStreetMap context fetch. That
fetch used to change the saved zone revision without advancing the creating
tab's undo revision. Undo then failed with a conflict despite no authored edit.

Context enrichment now reports the exact before/after revisions. The creating
tab advances its local undo revision only when the before revision matches.
The server checks project edit access, then locks and checks the source revision
after fetching, so a slow context request cannot overwrite a newer authored edit.
Redo retains the context present at successful undo. Existing project schemas
are unchanged; response metadata is additive.

## Verification

- 64 frontend tests across `useSiteZones`, `undoRevision`, and `undoProjectScope`;
  TypeScript and changed-file ESLint pass.
- Three backend endpoint cases pass: exact revision metadata, concurrent-edit
  rejection without property loss, and unauthorized access without context fetch.
- Live browser: drew a boundary in local project
  `f3519d2c-e40b-4967-ac6f-96f7ca0ed38c`; waited for real context enrichment
  (revision advanced from 06:17:05 to 06:17:26 UTC on 16 September 2026);
  confirmed Design; Undo removed it; Redo restored one boundary with identical
  coordinates, ground settings and OSM context; reloaded successfully.
- Recreated IDs and one-shot client request metadata intentionally differ.
  Screenshots of enriched, undone, redone and reloaded states were inspected.
  No additional browser exceptions or failed resource requests during this flow.

Evidence remains outside Git in
`C:/dev-artifacts/CityPrompt/student-design-transformation/PHASE13-*` and
`phase13-boundary-*.json`. No paid image or video validation was used.

This accepts the boundary-context undo repair, not the complete persistence,
backwards-compatibility, grounding or first-time-student acceptance gates.
