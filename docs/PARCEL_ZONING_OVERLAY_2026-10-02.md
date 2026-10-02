# Zoning labels — 2026-10-02

## Current student workflow

At the user's request, the overlay now shows zoning codes only. Open **Site →
Land use** or **Layers** and enable **Show zoning codes**. The parcel-boundary
checkbox, parcel geometry requests, tile reconstruction, and parcel-to-zoning
joins have been removed. The prior parcel prototype remains in Git history.

Labels come directly from Calgary's [Land Use Districts dataset](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh).
Each district is clipped to the actual drawn site polygon before positioning its
labels. Separate pieces receive separate labels; label points avoid holes and
stay inside the site. No lot lines or district outlines are drawn. Zooming in
reveals labels hidden by overlap prevention. Published modifiers and Direct
Control identifiers are preserved.

The checkbox is remembered per project in this browser. Existing label
preferences are retained; the old line preference is ignored. Calgary coverage,
loading, retry, and unavailable-data messages remain. Requests are bounded to
25 km² and 1,500 districts/label pieces, with a 30-second deadline, cancellation,
and a 15-minute in-memory cache. Changing the site polygon changes the cache key,
including when its rectangular extent stays the same.

This is display-only: no changes to saved site geometry, terrain, Google tile
masks, authored models, calculations, or generation. Labels cannot intercept
map drawing and remain excluded from Direct 3D and reference-overlay capture
paths. No rezoning, subdivision, or LiDAR integration is included.

## Verification

- 17 tests across four narrow reference-layer files passed, covering direct
  source loading, concave polygons, holes, separate district pieces, clipping,
  malformed responses, limits, cancellation, preferences, and failure recovery.
- TypeScript passed.
- Browser QA on **QA - Manual streets Currie** verifies labels in overhead and
  oblique views, no line objects, show/hide, reload persistence, failed-source
  retry, capture exclusion, no parcel-service requests, and no saved-design writes.

Source remains on `codex/parcel-zoning`. Preview uses `http://localhost:5194`.
QA scripts, screenshots and reports remain outside Git in
`C:/dev-artifacts/CityPrompt/parcel-zoning-2026-10-02/`, with `codes-only-` filenames.
No generated assets or database changes are part of this change.
