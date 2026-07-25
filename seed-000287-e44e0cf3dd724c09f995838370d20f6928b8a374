# Generate Community errors on unsaved boundary — Fix Plan (2026-07-07)

**Report:** clicking "Generate Community" on a freshly drawn (unsaved) boundary spews console
errors: `422` on `site-zones/temp-…` from `Object.update` (api.ts:616, uncaught promise),
`[ZoneProps] Save — variantPalette="undefined" …` (ZonePropertiesPanel.tsx:496), plus urban-dna
404s (those are expected "no snapshot yet" responses — noise, not a bug).

## Root cause

Same class as the fixed Site-DNA bug (commit d5c227a): newly drawn zones carry a client-side
`temp-<timestamp>` id until SAVE CHANGES persists them, and several ZonePropertiesPanel flows
call the backend with that id, which UUID-validates paths → 422/404:

1. `handleGenerate` (ZonePropertiesPanel.tsx:2291) → `siteZonesApi.generateForBoundary(project_id,
   zone.id)` with the temp id.
2. The property auto-save/debounce-flush path fires `siteZonesApi.update(zone.id)` for temp
   zones (the uncaught `Object.update` 422 at api.ts:616) — the save handler at ~:447/:496 runs
   with undefined palette/archetype and still posts.
3. Previously fixed instances: SiteIntelligencePanel fetches/generate + boundary-analysis (guards
   exist via `isPersistedZoneId` in `frontend/src/utils/zoneIdentity.ts` — REUSE IT).

## Plan (recommend A + B, ~half a day)

**A — root cause (preferred UX): persist the boundary when drawing completes.**
Find the draw-finish handler (GlobeSitePlannerMap / ProjectViewPage flow that currently stages the
zone with a temp id) and call the existing `useSiteZones.createZone` mutation immediately on
finish — temp ids then live for under a second and every downstream flow just works;
SAVE CHANGES becomes property-save only.
Care points: (a) drawing-cancel after auto-create must delete the created zone; (b) undo/redo
stack interplay (see undoRedo store — system actions use `setSkipHistory`); (c) the optimistic
temp entry already exists in `useSiteZones.ts:26-83` — on-finish create should reuse it, not
duplicate.

**B — belt-and-braces guards (do regardless):** audit every `siteZonesApi.*` call site in
`ZonePropertiesPanel.tsx` for temp-id safety and gate with `isPersistedZoneId`:
- `handleGenerate`: when unsaved, disable the button and show the same hint used by Site DNA
  ("Save the boundary first — Save Changes above"); guard inside the handler too.
- Auto-save/debounce flush + `handleSave`: skip `onUpdate`/`siteZonesApi.update` for temp ids
  (edits stay local; they persist with SAVE CHANGES). Add `.catch` so nothing rejects uncaught.
- Sweep the rest: `applyLayout`, `delete`, any other id-parameterized call in the panel.
- Downgrade the noisy `[ZoneProps] Save — …undefined` log to debug or remove.

**Console-noise nicety (optional):** the urban-dna 404s are handled but alarm users watching
devtools; a HEAD-less "exists" probe isn't worth it — leave, or silence via a comment in the
handler explaining the 404-is-normal contract.

## Tests / verification

- Vitest: handler guard (unsaved zone → no API call, hint rendered); auto-save skip for temp ids.
- If A: draw → finish → zone persists (real UUID within ~1 s) → Generate Community works without
  touching SAVE CHANGES; drawing-cancel leaves no orphan zone; Ctrl+Z after draw behaves.
- Manual: fresh boundary → click Generate Community → no 422/uncaught in console; after save,
  generation queues buildings as before.
