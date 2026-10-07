# Catalogue browsing checkpoint — 2026-10-05

Initiative: `codex/catalogue-browsing-facets-2026-10-05`, based on the student
zoning checkpoint. Local source only; no push, deployment, asset generation or
catalogue promotion.

## Student behaviour

The community catalogue retains its current categories and placement workflow.
A collapsible filter panel combines land-use purpose, registered default plot
area and authored architectural style. Parks use purpose and plot area; streets
use role and registered corridor width because the student draws route length.
Search, all filters and existing categories intersect. Reset clears the entire
intersection and restores the first twelve results.

Plot bands are under 500, 500–under 2,000, 2,000–under 10,000, and at least
10,000 m². Street-width bands are under 12, 12–under 20, and at least 20 m.
Only represented bands and styles appear. Card metadata states the registered
dimensions and distinguishes default reserved plot area from gross floor area.
Styles come from existing categories and positive tags; unknown styles remain
explicit. Scandinavian/Nordic and Brutalist aliases are supported, but no
currently unregistered Brutalist asset has been activated.

Expansion parents absent from the validation-only inspector catalogue recover
only browsing category and tags from preserved source metadata. This does not
restore their other variants or geometry defaults. Supplementary park and
Street Manual choices now use the exact reviewed registry objects, repairing
the existing canonical identity test failure and preserving reviewed groupings.

## Verification

- Six relevant Vitest files: **65 passed** (facets, palette, canonical discovery,
  existing category and hero-image tests).
- TypeScript check and ESLint for all touched production files: passed.
- Map-enabled production build, catalogue JSON and model-contract checks: passed.
- Bundle budget: initial JS **455.2 KiB**, total JS **8,063.0 KiB**, CSS
  **167.1 KiB**. Total JS rose about 6.3 KiB from the zoning checkpoint; the
  initial route budget is unchanged. These are build checks, not proof of
  forty simultaneous hosted users or smooth rendering on basic laptops.
- Browser: development preview on 5178 and built production preview on 5179.
  Standard production roster remains **95 choices: 34 buildings, 30 parks,
  31 streets**. The development launcher adds ten sealed temporary fixtures;
  those are outside source and are absent from the production roster.
- Combined Apartments + 500–under 2,000 m² + Scandinavian/Nordic returns the
  exact Nordic Roof-Garden Apartments. Choosing it opens the existing placement
  preview at **24 × 23 m**; cancellation was verified without placing a zone.
- Empty intersection/reset, section-change reset, narrow street filtering and
  garden purpose/size filtering: verified in browser.
- 820 × 1,180 responsive check: no horizontal overflow; results remain scrollable.
  Production console error capture after corrected preview setup: empty.

The production preview initially inherited the default API proxy on 8000; its
external launcher was corrected to the disposable backend on 8009. Existing
Currie terrain alignment remains unverified, as disclosed by the app. No paid
render or third-party 3D generation was invoked during these checks.

## Source and output

Source changes are confined to catalogue UI, discovery metadata, tests and this
checkpoint. No catalogue JSON, registered geometry, image, GLB, dependency or
backend source was changed. Ignored `dist/`, Vite cache and the dependency
junction are local output. Browser proof and launcher logs are outside Git:

- `C:/dev-artifacts/CityPrompt/overnight-2026-10-04/catalogue-nordic-production.jpg`
- `C:/dev-artifacts/CityPrompt/overnight-2026-10-04/catalogue-parks-ipad.jpg`

The dirty primary OneDrive checkout and unapproved Wave 1/Wave 2 families remain
preserved. Additional archetype authoring and human visual acceptance are still
separate work.
