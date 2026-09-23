# Currie empty-lot catalogue trial — 2026-09-22

Status: local student-workflow evidence. This record does not publish or grant
runtime approval to any candidate.

## Purpose and setup

An agent simulated a new student through ordinary browser controls on the local
application. The main project began as an empty irregular 2.8 ha Currie parcel
between a curving western road and a straight eastern corridor:

- Project: `Currie Empty Lot — Sol Catalogue Trial`
- Project ID: `54818ada-581f-4643-900a-78867b076c8c`
- Browser: desktop Chromium through `agent-browser`
- Evidence: `C:/dev-artifacts/CityPrompt/sol-empty-lot-trial-2026-09-22/browser`

The warehouse was tested in a second empty field because its complete native
envelope cannot plausibly fit the residential parcel:

- Project: `Currie Warehouse Fit Check — Sol`
- Project ID: `d6010349-f038-416c-8ddb-acb60ee1d050`

The projects are disposable local evidence. The external screenshots are not
publication assets and are intentionally outside Git.

## Catalogue items exercised

All five new building cards were opened and placed through the normal picker:

| Candidate | Browser result | Important limit |
| --- | --- | --- |
| Calgary side-by-side duplex | Placed in the mixed neighbourhood; later moved, undone, redone and reloaded | Exact entrance and full per-variant runtime review remain open |
| Montreal Plateau stacked duplex v004 | Placed in the mixed neighbourhood and persisted | Exact entrance and full per-variant runtime review remain open |
| Modern brick courtyard entrance v004 | Placed and visible at native scale | This is the entrance bar, not a complete courtyard block |
| Timber community hall v002 | Placed and visible at native scale | Raised threshold/accessibility design remains open |
| Tilt-wall mega-center v003 | Placed at 156 x 95 m on its own large empty field | Requires a prepared level and separate freight/pedestrian site design |

The main neighbourhood also included `Neighborhood Greenway`, `Bioswale & Rain
Garden Corridor`, and `Neighborhood Park (Natural Meadow)`. A direct `Market
Square` placement rendered as a fallback and was removed rather than presented
as a supported final object.

## Student workflow result

The main project passed the useful prototype loop:

1. Draw an irregular site around genuinely empty land.
2. Place multiple buildings, a greenway, rain garden and park.
3. Move a duplex, then Undo, Redo and reload without losing the edit.
4. Change the site to `Clear site for redevelopment`.
5. Preview and apply `Natural landscape`; the residual surface filled gaps while
   keeping buildings and public-realm objects visible.
6. Export the current exact 3D view and complete the actual download action.
7. Generate one `Photo Realistic` GPT Image 2.5 Flare view with people and
   vehicles, inspect the source/final comparison, and save the result.

The landscape result was a useful contextual base beneath the authored objects.
The greenway initially exposed two shared renderer defects: partial shared-ground
coverage bypassed its local terrain fallback, and development remount disposed
owned procedural materials. The shared renderer was repaired; the final street
showed dark travel lanes, pale sidewalks and green planted edges.

## Open findings

### Classroom blocker: route clearance feedback

The visible Multi-Use Trail / Green Corridor route appeared clear after several
ordinary-control attempts, including moving the duplex. Placement still hard
rejected against the hidden `Plateau stacked duplex` plot clearance. A student
cannot understand or recover from a mismatch between visible space and the
collision envelope. Shared assisted placement should preview the same envelope,
snap to the nearest valid location where possible, and reserve hard rejection
for cases with no nearby valid result.

### Classroom blocker: paid-render cost preflight

Follow-up reconciliation, September 22: read-only local database audit confirms
the original call charged 94 credits (`gpt-image-2.5-flare`, 23:30:35 UTC).
The account's weekly reset occurred at 23:30:36 UTC: reservation logic reset
the stale balance to 1,000, then charged 94, yielding 906. The apparent 3,151
drop was not the image price. This resolves the discrepancy and the pause on
paid trials below; a visible server-calculated cost preflight remains useful.
The later [vegetation trial](MEADOW_VEGETATION_SITE_TRIAL_2026-09-22.md) used two
explicitly authorized calls at 94 each and reconciled 906 -> 718.

The render button stated `1 image · uses your current view` but did not show the
reserved credits or whether the current balance could fund the call. One image
completed, yet the visible balance changed from 4,057 to 906 credits during the
trial. The server-side Direct 3D estimator caps the expected GPT Image 2.5
reservation far below that observed 3,151-credit change for one normalized
image. The non-admin test account cannot read render audit logs, so this trial
does not attribute the entire balance change to that one request. Before a
student pilot, expose a server-calculated preflight cost and remaining balance,
then reconcile the audit log for this project. Do not repeat paid calls while
that discrepancy is unresolved.

The user authorized up to five different style renders. One paid render was run;
the remaining four were not attempted because the displayed balance was no
longer sufficient for the same apparent charge.

### Follow-up: AI fidelity

The Photo Realistic provider image was visually attractive and read as a broad
aerial neighbourhood, but the automatic design checks rejected it. The product
correctly retained the exact source as the safe result and exposed the original
as unverified. Future style trials must compare each output with the exact
same-camera source; visual appeal alone is not an accuracy pass.

### Follow-up: natural versus prepared ground

The warehouse could be placed on natural ground but did not initially show
reliable support. `Review ground` followed by `Close gaps at site edges` and
`Apply redevelopment level` produced a credible grounded result. Large fixed
native assets must be trialed on an appropriately sized empty parcel and on the
actual terrain mode they advertise. A small residential test site cannot stand
in for this check.

## Reusable acceptance rules

Apply these rules to every future building, street and park batch:

- Start at least one mixed-scene trial from an empty project and visibly vacant
  land. Place through the same picker and controls students use.
- Test an oversized fixed-native asset on a separate, appropriately sized vacant
  parcel; preserve full native bounds and record ground preparation.
- Keep unsupported fallback objects out of the final evidence scene.
- Complete edit, Undo, Redo, reload, residual landscape, free exact export and
  actual file download before spending image credits.
- Verify collision previews, snapping and final placement use the same occupied
  envelope. Record hidden-clearance rejection as a product issue, not student
  error.
- Before a paid image call, show the selected engine, exact reserved credits,
  remaining balance and number of calls. Compare and record the provider output
  against the exact source, including any automatic fallback.
- Keep scene-level success separate from exact-variant entrance, terrain,
  accessibility, visual approval and publication decisions.

## Evidence highlights

- `21-greenway-bands-confirmed.png`: corrected greenway material identity.
- `35-bioswale-placed.png` and `37-neighborhood-park-placed.png`: public-realm
  objects in the mixed scene.
- `42-duplex-moved.png`, `44-undo-move.png`, `45-redo-move.png`, and
  `46-reload-persisted.png`: edit and persistence sequence.
- `47-landscape-preview.png` and `48-natural-landscape-applied.png`: residual
  landscape preview and applied result.
- `49-free-export-complete.png`: exact 3D download flow.
- `50-photo-realistic-review.png` and `51-photo-realistic-saved.png`: paid image
  review/fallback and saved result.
- `59-warehouse-grounded.png`: full-size warehouse on prepared vacant land.

## Decision

The expanded catalogue is usable for continued prototype work and bounded
student testing. These candidates remain local-only. Route-clearance recovery
and paid-render cost preflight are the two glaring workflow defects found here;
the exact candidates still require their completed runtime review records and
human visual/publication decisions before catalogue activation.
