# Large civic archetype trial

## Scope

Trial the existing Grand Iron & Glass Market and Victorian Grand Station, then
build two original churches with occupied interiors. Local review only; nothing
is pushed, seeded or broadly activated. Generated design references are labelled
as original concepts, not real-building photographs. Delivery is architectural
clay, with physical detail and no image textures.

External evidence: `C:/dev-artifacts/CityPrompt/large-civic-archetypes-2026-10-02/`.
Project: `72e227dd-1235-4462-a228-243e908401fe`, Civic Quarter - Large Archetype Trial.
The 240 × 260 m prepared site is a conceptual test pad, not surveyed grading.

## Checkpoint before the second build

Gothic Community Church v005 passed independent review: zero P0/P1 blockers.
Exact GLB SHA-256: `ca7066e8dc41f1d1e258ec5b162ed832787d576be8ee67d7449ddfa3850741fb`.
Complete exact-GLB reimport renders, source lock, phone comparison, aperture
audit and supplemental roof contact proof are under `gothic-v005/`.
Earlier failures remain immutable; `candidate-history.json` records their state.

Existing market/station placement, save/reload and short walking checks passed
without browser exceptions. Exterior and interior captures are in the external
batch root. These checks do not establish every gallery, stair or train route.

At that checkpoint, browser acceptance and the second review were pending.

## Completed local trial — 2026-10-03

Both churches passed independent architectural-clay review with zero P0/P1
blockers. Compact review records and portable source locks are preserved under
`tools/large_civic_pilot/`. Both are original conceptual designs; dimensions and
hidden details are interpreted, not surveyed.

| Model | Native dimensions (width × depth × height) | Detail |
| --- | --- | --- |
| Gothic Community Church v005 | 27.095 × 55.445 × 43.950 m | Single tower/spire, rose window, six-bay vaulted nave, side aisles, stained glazing, pews and altar |
| Timber Sanctuary Church v002 | 32.770 × 43.500 × 17.550 m | Glazed gable, eight timber frames, pews, pendants and furnished community annex |

Timber GLB SHA-256:
`da8ad808774d542d9b4f6216f3c9589b40633a6c56222ab05c9863fe6cdd712b`.
Its second candidate closes the sloped glazing perimeter, seats the pendant
cords against the lining, and removes a downpipe from inside the annex.

The fresh site contains four saved buildings: the existing market and station,
plus both churches. Preview:
`http://localhost:5199/projects/72e227dd-1235-4462-a228-243e908401fe`.

Browser checks on the exact delivered GLBs:

- Placed both churches using the catalogue and canvas; fixed native dimensions
  retained. The app added planting from their archetype frontage notes.
- Inspected close exterior and interior captures. No replacement render was
  used as evidence of the runtime model.
- Traversed all four authored walking routes with the app's movement solver:
  both centre aisles and returns, Gothic side aisle loop, and timber side aisle
  through the annex opening. Furniture remained excluded.
- Used Walk mode and keyboard movement to enter each church, advance about
  24 m, then back out onto the prepared site. No trapped route or floor jump
  occurred in these tests. Entry/exit ground transition is approximately 0.16 m.
- Reloaded the project without browser exceptions. Exact movement results are
  in `church-browser-results.json`; captures use `*-browser-*.png`.
- Confirmed all four saved buildings and both church GLBs after a fresh page
  load; switched generated models off and on and confirmed both loaded again.
  `final-runtime-check.json` records this additional check. Inspected close
  exterior views of both churches and the timber annex interior.

The optional review-model walking integration uses each model's actual world
transform and only registers its network on prepared ground. Existing models
without walking metadata keep their previous behavior. The Gothic tower is
visual architecture, not a climbing route. These bounded checks do not prove
every possible user movement, terrain condition or all older station galleries.

Verification: 30 targeted frontend tests, TypeScript type-check and 22 compiler
method/quality-memory tests passed. Source-lock dry runs validated four source
roles and sixteen cameras for each church. A preview asset-load failure was
resolved by restarting Vite after copying the new public files; the successful
browser run had zero page exceptions.

## Source and generated output

Source changes include the two archetype/validation records, optional walking
registration, generators, source locks, review records and LFS source PNGs.
GLBs, full renders, browser screenshots, transient trial scripts and private
authentication state remain outside the source tree in the external evidence
directory. Private state must never be copied into Git.

Nothing is pushed or added to the approved seed library. These remain local
review models pending the user's visual acceptance. Follow the hydration steps
in `tools/large_civic_pilot/README.md` to reproduce the preview asset paths.
