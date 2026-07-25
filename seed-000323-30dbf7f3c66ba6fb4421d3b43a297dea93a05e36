## OSM Fetching and Caching

When using OSMnx, enable local caching during development to avoid repeated network calls, slow test cycles, and temporary rate limiting.

Recommended setting:
- `ox.settings.use_cache = True`

The implementation should reuse cached OSM results whenever possible.

## Testability and CI/CD

The pipeline must be testable offline.

Requirements:
- network calls to OSMnx should be isolated and mockable
- context fetching should be separated from subdivision and geometry logic
- geometry processing and parcel subdivision should be testable without live network access
- CI/CD test suites should not depend on external OSM availability

## Orphaned Block and Sliver Cleanup

After subtracting ROW polygons from the site, the engine may produce orphaned fragments such as:
- tiny corner triangles
- traffic-island remnants
- narrow unusable slivers

These should be explicitly filtered out before subdivision.

Support a configurable:
- `sliver_area_threshold`

Recommended initial default:
- discard any resulting block smaller than `50 sqm` unless explicitly retained for a special use case.