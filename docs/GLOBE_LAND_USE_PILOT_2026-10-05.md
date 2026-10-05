# Google 3D land-use map pilot — 5 October 2026

## Scope and visual direction

The Site and Layers panels now offer **Show land-use map**, a single switch for
the existing Calgary district overlay inside the Google 3D Tiles environment.
The map starts off for new projects. Enabling it shows district boundaries,
published labels and colour fills. Each can be adjusted separately, and fill
opacity runs from **0% (transparent) to 100% (solid)**, starting at 40%.
Changing opacity does not alter label or boundary visibility. Turning the map
off removes its scene objects and label-frame work; turning it back on restores
the chosen appearance. Preferences survive reload and remain project-specific.
Existing label/outline preferences migrate without resurrecting cadastral lines.

The user selected a planning-map appearance within the 3D environment. The pilot
borrows warm residential yellow, multifamily ochre, mixed-use coral, park green,
and mauve from the palette direction of these Calgary precedents:

- [University District, May 2025, pages 4–5](https://myuniversitydistrict.ca/wp-content/uploads/2025/05/2024-132-University-District-Information-Session-Boards-May2025.pdf#page=4)
- [West District, February 2025, slides 10–11](https://hellowestdistrict.com/wp-content/uploads/2025/02/25-02-05-online-information-session-slide-deck.pdf#page=10)

Fine charcoal boundaries have a narrow light casing for contrast over imagery.
Map lettering uses a light text halo rather than floating badges. The legend
matches the polygon colours. These are **CityPrompt presentation colours**, not
an assertion of an official statutory colour specification. All Direct Control
districts use mauve: an underlying residential/commercial use cannot be inferred
from a source description that only says Direct Control.

The [City's published district dataset](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh)
still supplies the geometry, full designation and description. No R-CG or other
code is invented for the pilot. Existing and proposed student-study layers retain
their separate visibility controls and saved geometry. This change refines the
existing-district globe overlay; it does not recolour or rewrite saved studies.

## Verification

- All 16 focused reference-layer Vitest files: **75 tests passed**.
- `npm run type-check` and `git diff --check`: passed.
- Live Chrome verification on `localhost:5174`, dedicated local API `8009`.
- Disposable project **Land-use map pilot — Currie / Richmond**:
  `47264cb3-c871-45a0-85bf-c22c1bd31fda`. Its sole boundary covers
  `[-114.125, 51.015, -114.115, 51.020]`. The pilot uses **Follow existing terrain**
  so the existing Google buildings and streets remain visible. No earlier design
  was altered; the new project's ground preference was saved through the UI.
- Live City response: **32 district pieces, 21 distinct legend entries**.
- Browser checked: whole-overlay off/on, 0/40/100% opacity, independent boundary
  and label visibility at the transparent endpoint, and both on and off reloads.
- Opacity changes reuse the same GPU geometry. District fills are one mesh with
  **445 triangles** on this site; boundaries use two batched line draws.
- Cached toggles and appearance changes made zero additional district requests
  and zero design API writes. Direct 3D capture exclusion remains intact.
- Final browser error log: empty. Reviewed overhead and oblique screenshots.
- At a 1024 × 768 browser viewport, the left panel scrolls to the opacity control;
  its solid endpoint works. This is viewport emulation, not physical iPad/Safari
  or 40-student hosting verification.

## Pilot limitations

This is a cartographic overlay at the site's reference elevation. It does not
implement terrain/roof classification or survey-grade draping. Full source
designations remain available in the legend when overlapping map labels are
hidden at distant views.

The larger retained-terrain test boundary triggers the existing **Ground
alignment could not be verified** banner both with this overlay off and on.
The shared-ground sampler reports unavailable after its attempt. That remains
an open ground-review issue, and the screenshots preserve the warning. This
pilot is not a claim that construction placement or ground-dependent renders
on that large site pass. The overlay remains excluded from those render captures;
the evidence images are browser screenshots.

## Local checkpoint and evidence

Branch: `codex/globe-land-use-pilot-2026-10-05`.
Only source, tests and this record belong in the commit. Screenshots, browser
scripts, private local authentication state and runtime output remain outside
Git at `C:/dev-artifacts/CityPrompt/globe-land-use-pilot-2026-10-05/`.

Reviewed deliverables:

- `pilot-translucent-3d.png` — 40%, angled Google 3D view
- `pilot-solid-top.png` — 100%, overhead Google 3D view
- `pilot-solid-3d.png` — 100%, angled view
- `pilot-outlines-top.png` — 0%, labels and boundaries retained
- `pilot-off-3d.png` — entire existing-district overlay hidden
- `pilot-tablet-controls.png` — scrolled tablet-sized opacity control
- `pilot-browser-qa.json` — assertions and scene evidence

No push or deployment. No new dependencies, generated catalogue assets or paid
image generation. Visual approval and any broader rollout remain separate from
this local pilot.
