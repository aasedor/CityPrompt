# Parcel and zoning overlay — 2026-10-02

## Student workflow

After drawing a site boundary, open **Site → Parcels & land use** or **Layers**.
Parcel boundaries and land-use labels have separate checkboxes. Both start off;
choices are remembered on this browser for each project. Zoom in to see labels
that were hidden to avoid overlapping text. Split zoning displays each matching
district, including Direct Control identifiers and published modifiers.

This first version covers Calgary. Rezoning and subdivision are future work.
It does not write site zones, change terrain, mask Google tiles, alter generated
models, or enter planning calculations. Overlay objects do not intercept drawing
and are excluded from Direct 3D captures and existing reference-overlay capture
paths. The legacy 2D master-plan editor is outside this student-globe feature.

## Sources and coverage

- Parcel geometry: City of Calgary's [parcel fabric vector map](https://www.arcgis.com/home/item.html?id=d65f01030ee6494b98b7bdce021a4b25),
  `Calgary_VectorBasemap/VectorTileServer`, layers `Ownership Parcel RP` and
  `Ownership Parcle NR`. Road layers are not loaded into the overlay. This
  includes public and unassessed ownership parcels, instead of restricting
  coverage to property assessment records.
- Zoning: [Calgary Land Use Districts](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh),
  queried live with bounded spatial filters. Labels come from the district
  `label` field (or `lu_code` when absent), joined by polygon intersection.
- Zoning is never guessed. `Unknown` marks an unmatched parcel; an empty zoning
  response explains that Calgary coverage may not include the site.

The giant east-field trial at longitude -113.857, latitude 51.002 is outside
Calgary: the official City Boundary service returned zero containing features,
and the Calgary zoning service returned no district. It needs another municipal
source. It must not receive fabricated Calgary codes.

The display is clipped to the site's rectangular extent. It is map detail, not
survey geometry. Vector fragments are rejoined only when they overlap in area;
touching parcels keep their shared boundary. Zoning overlaps smaller than 0.25 m²
are ignored to suppress digitization slivers. Labels use interior points that
avoid polygon holes. Multi-code labels wrap, and screen-space collision checks
keep the map readable.

Requests are limited to 25 km², 64 vector tiles at zoom 16, 1,500 parcels/districts,
and 8,000 raw tile fragments. Fetching uses four tile requests at a time, a
30-second deadline, cancellation, and a 15-minute in-memory cache. Oversized,
failed, or truncated queries show a retry/size message rather than silent partial
coverage. A changed boundary cannot display the previous query's geometry.

## Verification

- 19 Vitest tests in five narrow reference-layer files passed. Coverage includes
  adjacent lots versus duplicate tile fragments, holes, split zoning, unknown
  codes, bounds, cancellation, source failure, independent checkboxes, project
  preferences, and changed/deleted boundary recovery.
- TypeScript check passed.
- Live browser: **QA - Manual streets Currie**, project
  `60db592e-2d49-4cfb-8d53-fb8004c25784`: 54 parcel labels with no unmatched codes.
  Overhead and oblique views reviewed. This includes parcels missing from the
  earlier assessment-only approach.
- Live data checks: larger Currie envelope, 188 parcels; Nose Hill Park test
  envelope, one parcel with published `DC1Z2003SITE1`. Every tested parcel matched
  zoning. No assumption was made that all parks have the same designation.
- Browser verified lines-only, labels-only, both off, persistence after reload,
  a simulated HTTP 503, and successful retry. No page errors or project-data
  mutation requests occurred. All inspected overlay renderables were excluded
  from Direct 3D capture.

## Local output

Source initiative: `codex/parcel-zoning` in the managed parcel-zoning worktree.
Preview: `http://localhost:5194` (backend 8018; shared hydrated public assets).
QA scripts, screenshots, and reports stay outside Git at
`C:/dev-artifacts/CityPrompt/parcel-zoning-2026-10-02/`.
No generated model assets, database migrations, or catalogue edits are included.
