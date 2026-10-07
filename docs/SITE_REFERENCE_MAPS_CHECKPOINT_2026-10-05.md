# Site reference maps checkpoint — 2026-10-05

Baseline: `1750a1c9b` (the saved all-building-walking version). Initiative:
`codex/site-reference-maps-2026-10-04`. The dirty primary checkout was preserved.

## Changes

- Calgary zoning boundaries and codes have independent visibility controls.
  District polygons are clipped to the saved site boundary, including holes.
  These are display-only reference overlays, excluded from Direct 3D captures.
- An on-demand assessment lookup uses Calgary's current-year parcel dataset.
  Totals deduplicate assessment accounts, retain distinct accounts sharing land,
  and include every fetched account before limiting the displayed breakdown.
- Full intersecting-property assessments and a separate area-weighted concept
  estimate are labelled explicitly. Missing/conflicting values, limited fetches,
  mapped coverage and partial properties remain visible.
- The endpoint checks project access and the saved active boundary. An unsaved
  geometry cannot be used accidentally. Bounded caching and shared concurrent
  lookups reduce duplicate source requests within one backend process.

## Verification

- 18 frontend tests in `zoningLabels`, `ZoningLabelsControls` and
  `SiteAssessmentPanel`; 12 backend tests in the service and endpoint suites.
- TypeScript checking, touched-file lint and the production build pass.
- The bundle budget fails: total JavaScript 9,532 KiB against 8,448 KiB.
  Initial JavaScript is 455.2 KiB against 600 KiB. This requires a separate
  performance initiative; this checkpoint does not claim classroom readiness.
- Browser verification used the isolated local app at port 5178 and backend
  8009, with a disposable account/project in the existing test database.
  No paid render or Direct 3D generation calls were enabled.
- A five-corner 4.0 ha Currie site displayed seven clipped zoning areas, codes
  and boundaries. Both visibility preferences and the saved boundary survived
  a reload. Assessment calculation is deliberately on demand after a reload.
- The live 2026 lookup returned 549 assessment accounts: $118,443,500 in full
  intersecting-property assessments and a $101,776,669 area-weighted estimate.
  Mapped coverage was 43.33%; the app disclosed partial properties. These are
  trial outputs, not an official valuation of this partial site.
- Captured browser error/warning log was empty. The map's existing terrain
  alignment system separately displayed an unverified-ground warning on this
  built-up site; terrain verification was not changed by this initiative.

## External local output

Browser screenshot: `C:/dev-artifacts/CityPrompt/overnight-2026-10-04/zoning-assessment-browser.jpg`.
Launchers, logs, Vite cache and test environment files are in the same ignored
external output directory. Frontend dependencies are an ignored junction.

Docker startup required preserving two stale socket directories under sibling
`*.startup-backup-20261005` names. No persistent Docker volumes, databases,
settings or application assets were deleted or reset.

## Remaining roadmap

Student-authored existing/proposed graphic layers, vector map export,
performance improvements and a 40-user hosted trial, catalogue filters and
reviewed additions, flexible park recipes, render-style examples, landing-page
copy and optional camera-path video remain separate initiatives. Button cleanup
remains reserved for the user's separate session. Nothing was pushed, deployed
or promoted to the release catalogue by this checkpoint.
