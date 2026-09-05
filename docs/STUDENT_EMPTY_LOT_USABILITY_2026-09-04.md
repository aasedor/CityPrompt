# Student empty-lot usability exercise — 4 September 2026

Branch: codex/student-empty-lot-usability. Base: 1a4c0bf62.
The running frontend is the student-studio-2027 worktree on port 5175.
The main checkout was already dirty and was left untouched.

## Actual student exercise

Created the local project **Student first-use — empty lot and varied building sizes**
through the browser, using the existing local test account. Project:
http://127.0.0.1:5175/projects/76696eee-711d-4ce6-a3b6-5319362d822d

Address search: 750 9 Ave SE, Calgary. Drew on the visibly open Fort Calgary
field, away from existing buildings. This is a fictional classroom proposal,
not a claim that the public park is available for development. No site boundary
was required. All drawing, archetype selection, resizing and generation used
the visible interface; no fixture coordinates were injected into the project.

Three building outlines and a park were saved:

| Building | Properties-panel footprint | Map area | Final floors |
| --- | --- | --- | --- |
| Small Vancouver Craftsman Bungalow | 14 × 13 m | 142 m² | 1 |
| Medium untyped building | 24 × 19 m | 384 m² | 3 |
| Long Vancouver Craftsman Bungalow plot | 49 × 18 m, then 55 × 22 m after dragging a corner | 892 m², then 1,041 m² | 1 |

These are rounded properties-panel dimensions. The 3D assembly panel uses a
different footprint envelope and displays different dimensions. This discrepancy
is still a usability issue; neither number should be presented as a surveyed
measurement.

## Reproduced problems and changes

1. **Enter performed two actions.** Closing Guide restores focus to its button.
   Clicking the map did not change that focus. Enter saved the polygon and
   reopened Guide. With Building focused, Enter instead toggled drawing off,
   causing the next attempted outline to disappear. Drawing now consumes Enter
   while points exist, preserving text-input handling and ordinary keyboard
   activation when no drawing is in progress.
2. **No obvious overhead control.** The angle badge looked clickable but was
   only text. Added Top view / 3D view, retaining the point under the centre of
   the camera and approximately retaining viewing distance. Overhead uses local
   north as camera-up to avoid a degenerate look-at pose.
3. **The map instruction was wrong.** Left drag pans; right drag rotates.
   Updated the hints from the actual installed globe-control implementation.
4. **Finishing depended on knowing a shortcut.** Added a visible desktop
   Finish drawing button after enough points exist. Existing mobile controls
   remain.
5. **A bungalow inherited ten floors.** The generic drawing started at ten
   floors; choosing a variant with no explicit floor override retained that
   value despite its parent specifying one floor. Selecting such an archetype
   now replaces a missing/out-of-range count with its suggested midpoint.
   Compatible existing counts are preserved.
6. **Scale was locked behind type selection.** Students can now open Scale
   immediately, edit floors/height, and save without picking an architectural
   category. Added associated input labels and explicit corner-resizing help.
7. **Area similarity was presented as guaranteed fit.** Changed building card
   wording to Area match / Area comparison, and explain that shape, dimensions
   and floors determine actual model fit.

## Browser verification

- Top view reached 90° overhead; switched back to the oblique scene.
- Three different building sizes and a park were drawn on open ground.
- Dragging the long building's white corner increased its area and dimensions;
  the changed outline survived reopening the project.
- Selecting Classic Craftsman produced one floor / 3 m, replacing ten floors.
- Scale worked on the untyped building; entering three floors updated height
  to 9 m. Saving marked the previous 3D scene stale; rebuilding used three floors.
- Repeated the Guide-focus reproduction: Enter saved a temporary park, Guide
  stayed closed, and Park stayed active. Undid that temporary polygon.
- Drew another temporary park and finished with the visible button, then undid
  it. The final project contains only the intended three buildings and one park.
- Generate to 3D completed, reporting one detailed building, two massing
  fallbacks and one procedural park. Render/video became available after
  generation. No image or video API was invoked.
- Browser error log returned no errors at the final check.
- React review: no added effects/listeners or dependencies; new controls are
  real buttons and form labels. Existing drawing listener cleanup is retained.

Automated checks: 33 tests passed across ZonePropertiesPanel.test.tsx,
SitePlannerToolbar.test.tsx and globe/drawingGeometry.test.ts.
New regression coverage exercises correcting an incompatible inherited height,
preserving the compatible existing count, and editing height before choosing a
type. npm run type-check and git diff --check passed.
Keyboard and camera changes were verified in the real browser, not a mocked
WebGL component test.

## Remaining work, in priority order

1. **Make the chosen building's actual footprint visible before generation.**
   The small house plot fell back to plain massing, while the large plot received
   one native-size house surrounded by a large dark ground area. This is
   technically consistent with the current fixed-native clay contract, but
   surprising for a student expecting their outline to define building size.
   Preview the actual detailed footprint inside the outline, with a clear choice
   between parcel layout and an exact-footprint building proposal.
2. **Add a reviewed repeated-home layout contract.** The long bungalow plot
   does not become a row of houses. Implement deterministic placement of
   separate native homes with contained footprints and gaps; preview the count
   and layout. Do not stretch one clay house across the block or silently
   substitute a different family.
3. **Unify footprint measurements.** Properties and assembly currently report
   different bounding dimensions. Share the same geometry definition, and
   explain whether students are editing a building footprint or a development
   parcel. Numeric width/depth editing would complement the working handles.
4. **Simplify catalogue and 3D language.** The house list is long and difficult
   to scan. Add search, a small useful starting set and an exact model preview.
   The separate AI Generate 3D, Build with LEGO Modules and Generate to 3D
   actions need a clearer primary route. The untyped building also received a
   misleading fixed-clay fallback explanation; errors should distinguish no
   chosen family from an incompatible chosen family.
5. **Improve location search.** Westbrook Station produced no explanation for
   no results; Westbrook Mall suggested unrelated streets. A full street
   address worked. Support landmark search or show useful no-result guidance,
   with stale-response protection.
6. **Continue terrain verification.** This exercise confirms placement on a
   visibly open field and a generated park. It does not certify ground contact
   over slopes, tile reloads or every clay foundation. The large dark plot
   surface around the native house needs visual/ground review.

These changes are local only. No catalogue additions, deployments or paid
generations were made. Source changes are the three frontend files plus this
report; project drawings and generated recipes/models remain in the isolated
local application data, outside the source commit.
