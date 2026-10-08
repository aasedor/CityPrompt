# Independent bench detail trial — 8 October 2026

## Result

The project toolbar now offers **Edit details**. Students can add the existing
1.9 m detailed timber bench, move/rotate/remove it and save its geographic
position without attaching it to a building, park, street or site boundary.
Context outlines guide placement; they do not constrain it. Expand view exposes
more open ground. Small furniture is not selectable in normal 3D editing.

The original rustic neighbourhood park bench editor remains available for that
park's automatically populated benches. It keeps its existing layout rules.

## Browser trial

Local project: `099fdc75-8eb1-4849-b602-8eebecef296e`, **Bench detail editor · pilot**.

URL: http://127.0.0.1:5183/projects/099fdc75-8eb1-4849-b602-8eebecef296e

Through the browser, added a Timber community hall and Quiet Residential Street,
then added three project benches: in front of the hall, beside the street, and on
open ground east of the park. Inspected all three in 3D. Moved and rotated the
street-side bench, removed it, used Undo to restore it, saved and reloaded. All
three persisted. Clicking the open-ground bench in normal 3D selected the site
underneath, not the bench.

Evidence outside the repository:

- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/independent-benches-layout.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/independent-frontage.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/independent-street-side.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/independent-open-ground.png`

## Implementation

- Authenticated GET/PUT `/api/v1/projects/{project_id}/details` stores versioned
  furniture data in existing project metadata; no schema migration or fake zones.
- Viewer/editor permission checks, finite coordinates, unique IDs, a 256-bench
  pilot limit, and revision conflict protection. Other metadata is preserved.
- Positions are geographic, independent of subsequent building/park movement.
  The editor freezes its coordinate frame for the lifetime of an open draft.
- Reuses the existing timber GLB. No model generation or paid rendering.
- Prepared ground is reused where available. Elsewhere terrain probes are bounded
  to two per frame and retried as tiles load. Bench meshes do not participate in
  normal scene picking.

## Verification

- 37 Vitest tests passed across projectBenches, benchDetails, BenchDetailEditor,
  StudentWorkflow and neighborhoodParkLayout.
- Three backend project-details tests passed (save/clear, ownership and stale
  revisions, invalid data); backend was restarted and browser saves use live API.
- `npm run type-check` passed.
- ESLint passed for the new/refactored detail components and conversion helper.
- `git diff --check` passed.
- No-boundary/open-ground placement and coordinate stability across different
  editor frames are covered by tests. The browser examples used a level site.

## Pilot limits

This exposes one bench model and independent added benches, not all furniture
embedded inside every existing archetype. The editor uses a 2D context plan with
3D results after saving; Undo is local to the open draft. Steep terrain, public
shared-project viewing, alternative map engines and generated-image fidelity
have not been validated for this extension. New independent furniture is wired
into the authenticated project globe; public shared viewers need their own data
integration before this is a full release.

Source changes belong to branch `codex/independent-bench-details-2026-10-08`.
Screenshots, backend logs and trial database state are local artifacts, not Git
deliverables. No push or hosted deployment was requested for this trial.
