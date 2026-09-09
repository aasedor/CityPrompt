# Editing and deletion reliability — 7 September 2026

Student report: 404 on deletion, models returning, and same-tab moves showing another-session conflicts.

## Changes

- Catalogue model deletion resolves its source drawing rather than deleting only a compiled model that automatic 3D recreates. Imported models retain model-only deletion.
- Project-scoped, QueryClient-owned write queue coordinates authored saves, automatic compilation and automatic park-ground saves within this tab. Authoritative save responses update the query cache before the next write reads its revision. Genuine server conflicts are not retried or bypassed.
- Delete 404 reconciliation requires a successful authorized project read confirming absence; unrelated 404s remain errors.
- Boundary feedback now explains that the full plot includes surrounding space. Geometry guards remain active.
- Conflict text says newer saved version instead of assuming another session.

## Verification

55 focused Vitest tests passed, including delayed compile -> move -> delete revision ordering, failure ordering, confirmed-absence 404 reconciliation, stale compiled model identity, automatic 3D and automatic ground saves. TypeScript passed.

Browser QA used an isolated copy, project c8b76e11-8aac-49b5-9760-8c62528cfe54. Resized the copied bungalow plot to 30 x 24 m, then 32 x 24 m. Both saved and compiled. Clicked the model and pressed Delete. After reload the server listed only the site boundary and the visible community model count was zero. No browser errors or save-conflict messages observed. The original student project d2cfc01b-1b4f-4e79-ad89-0826a3f4549f was read only.

Screenshots are external under C:/dev-artifacts/CityPrompt/render-prompt-review-2026-09-07/: edit-qa-ready.png and deleted-after-reload.png. No generated artifacts or provider renders are included in this source change. No paid render calls were made.

## Limits

The queue coordinates this tab, not other users. Server revision checks still protect concurrent editors. Background 3D work may briefly delay an edit while its write completes. Existing model records belonging to deleted drawings remain excluded by the existing source-zone visibility filter; this change does not introduce a destructive model-file cleanup policy.
