# The Exchange student workflow trial — 13 October 2026

Source: Mawson College, *The Exchange Master Plan*, March 2024, pages 10–11. Read the saved PDF at `C:/dev-artifacts/CityPrompt/ubst451-new-plans/The-Exchange.pdf`. The concept proposes a central market, music school, sports court, memorial/pavilion and riverside gathering spaces at Fort Calgary. This trial is a smaller, unsurveyed catalogue interpretation of that plan, not an exact architectural reconstruction or an approved redevelopment.

Local project: `e3c600db-15bf-43d6-a8b2-ba3d906e5406`, named **The Exchange · student workflow trial**, on frontend `http://127.0.0.1:5184`. Original projects were not edited.

## Saved design

- A six-click authored boundary resolved to five saved corners, approximately 5.7 ha. This covers the trial precinct rather than the complete 16 ha student site. Ground defaults to Clear site for redevelopment; tested opacity at 7% and 100%, retaining the prepared level.
- Three building placements: Grand Iron & Glass Market, Timber Art & Design School (music-school programme equivalent), and Timber community hall (pavilion equivalent).
- Three parks: Basketball park, Timber and stone square, and Sensory & Wellness Garden. The garden is a quiet-space substitute, not an authored memorial or cultural representation.
- One saved 1.8 m concrete pedestrian route, plus two imported American elms and one timber-backed bench.
- Proposed C-C1, S-CI and S-R polygons as a student study, separate from existing S-R zoning. Incomplete district coverage remains visible in the planning report.

## Browser checks

Completed through normal UI controls: project creation and address suggestions; zoning and MDP exploration before a boundary; MDP legend; boundary drawing and opacity; zoning drawing/save/reopen and map selection; category search and model placement; court keyboard movement, 15-degree rotation, deletion, undo, redo and restoration; narrow path drawing and recovery from overlap guidance; persistent Add Details picker, rotation, placement, arrangement and save; walking/turning across plaza ground; free street-view 3D preview; 5A/transit-route/stop toggles and transit explanation; Layers; Help/Next; Share dialog inspection; planning report request, student response save and HTML download; project reload; free aerial capture and PNG download.

The saved report contains seven proposal areas, proposed-zone comparisons, unknown/incomplete footprint quantities, local-plan coverage limitations, and the saved student response. The City assessment lookup returned two intersecting properties, 2026 roll, full-property total $130,330,000 and prorated trial-boundary estimate $59,753,200.23. This is existing-property assessment context, not an acquisition price or a valuation of the new design.

No approved local area plan in the loaded collection covers this site; the interface and report correctly retain that limitation. Source-policy amendment and heritage/floodplain decisions are not established by this trial.

## Failures found and repaired

1. Saving a zoning study and closing before completion left a stale local revision after reopen. Successful saves now update recovery state synchronously, remove only the matching submitted draft and update cached canonical data. Genuine conflicts and newer drafts remain protected. The exact save/immediately-close/reopen sequence passed after the fix; the three saved polygons matched the shared layer.
2. The detail arrangement editor treated an imported elm stored as a prop as a solid canopy-sized object. Two tree centres 12.55 m apart falsely conflicted. Recovered assets categorized as Trees now use the existing trunk clearance. Canopy overlap is allowed while trunk and furniture collision checks remain. The same saved arrangement reopened without the warning; a bench rotation/move/save then passed.

Normal route collision guidance appeared when trial alignments crossed reserved court/pavilion plots. The route saved after being redrawn clear. These recoverable validations were not hidden or counted as crashes.

Development hot reload interrupted intermediate walking/capture attempts while tests and fixes were edited. Walking and export were repeated after source freeze. The completed walking trial does not certify all interiors, stairs or slopes.

## Verification and evidence

- Zoning save regressions: 27 focused tests passed across editor, study and reference-layer tests.
- Detail collision/editor regressions: 29 focused tests passed across four files.
- TypeScript no-emit checks and `git diff --check` passed after the fixes.
- Final browser error/warning log was empty. This is a bounded workflow observation, not a guarantee against all possible failures.
- Free aerial PNG downloaded and inspected: 1280 × 656 pixels. Free street-view preview also displayed successfully. Account balance stayed at 6,460 tokens.

Evidence is outside Git at `D:/CityPrompt-student-trial-2026-10-13/`: `source-plan.png`, `community-final.png`, `walking-plaza.png`, `street-preview.png`, `community-3d.png`, `planning-report.html`, `planning-report.txt`, and `browser-diagnostics.json`.

Paid image/video generation, presentation-link activation, invitations, external publishing, Render-hosted acceptance and student-laptop capacity were not submitted or certified in this trial. Use the branch containing these fixes when following the Render staging guide.
