# Codex Globe Feature Integration Handoff

Date: 2026-04-23

Use this note to start a fresh Codex conversation without losing the thread.

## Current Goal

Selectively integrate useful work from `origin/codex/google-3d-globe-integration` into `origin/feature/merge-codex-ux-onto-stable`.

The priority is to bring over UI and quality-of-life work, especially version history, while preserving the newer renderer work already present on the feature branch.

## Active Worktree

Path:

`C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt\2D23D\codex-google-globe-feature-integration`

Branch:

`integrate/codex-google-globe-onto-feature`

Base:

`origin/feature/merge-codex-ux-onto-stable`

Source branch being selectively ported:

`origin/codex/google-3d-globe-integration`

## Local Preview

Frontend:

`http://127.0.0.1:5175/`

Vite is run from:

`codex-google-globe-feature-integration\frontend`

Frontend API target:

`http://localhost:8001`

Isolated backend stack:

`docker compose -p codexglobe5175 -f docker-compose.5175.local.yml up -d db redis minio backend`

Backend health:

`http://localhost:8001/health`

Important: this is intentionally separate from the older `feature-ux-asedor-integration` backend on `8000`, so the 5174/8000 workflow does not get disturbed.

## What Has Been Ported

- Zone history backend model/schema/routes.
- Zone history migrations `020_create_zone_history.py` and `021_add_previous_snapshot.py`.
- Frontend `HistoryPanel`.
- Frontend `useZoneHistory`.
- `zoneHistoryApi`, history types, and undo/redo skip-history header support.
- Selectable history rows: selecting an older entry and pressing Restore/Undo checks out that point without adding a duplicate history entry. The restore participates in client undo/redo, and future edits from that restored state become the new branch.
- Toolbar UI controls from the globe branch:
  - Street View
  - History
  - Buildings toggle
  - More Tools
- `ProjectViewPage` wiring for HistoryPanel.
- Admin render logs row expansion, lazy preview loading, and Up/Down navigation from the globe branch.
- Project list caps removed for the normal Projects page and admin All Projects endpoint when callers do not explicitly pass a limit.
- Globe AI Render panel now docks at the bottom of the globe canvas as a wider, shorter tray instead of replacing/covering the zone properties panel, so development type controls remain reachable while rendering.
- AI preview generation now clears the selected zone/building and waits for the UI to redraw before capture, keeping vertices/selection handles out of render inputs.

Renderer preservation rule:

Do not wholesale copy renderer files from the globe branch. Keep the feature branch's newer renderer modules unless a specific hunk is intentionally ported.

## Known Remaining Work

- Existing user/project data has not been copied into the isolated `8001` DB. Test with a new project or intentionally import/clone dev data.
- Version History now supports live undo/redo plus selected-entry restores without adding duplicate server history rows. A future pass could visualize the selected restore point and any later branch origin more explicitly.
- Broad `npm run type-check` still fails on inherited branch-wide issues outside this integration slice.
- Render quality improvements from the globe branch's `useAIRender` still need a careful second pass.

## Good First Prompt For A New Conversation

Continue the work in:

`C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt\2D23D\codex-google-globe-feature-integration`

We are selectively integrating `origin/codex/google-3d-globe-integration` into `origin/feature/merge-codex-ux-onto-stable`. Preserve the feature branch renderer. The local frontend is on `5175` and the isolated backend is on `8001`. Read `docs/CODEX_GLOBE_FEATURE_HANDOFF.md` first, then continue refining Version History branch visualization and testing it locally.
