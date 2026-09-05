# Calgary zoning spatial pilot

Initiative: `codex/calgary-zoning-reference`, September 5, 2026.

## Source and extract

The existing Calgary connector correctly identifies the spatial source as
[Open Calgary Land Use Districts](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh),
dataset `qe6k-p9nh`, geometry field `multipolygon`. The older `mw9j-jik5` record
does not provide the polygon geometry used by this connector.

Live metadata was inspected before download. It reports source rows updated
September 1, 2026 at 15:23:13 UTC. Fields include `lu_code`, `label`,
`description`, `major`, `generalize`, `lu_bylaw`, `dc_bylaw`, `dc_site_no`,
`density`, `height` and `far`. These attributes are retained as source data;
they do not automatically define every applicable bylaw rule or extrude geometry.

A bounded query around the existing Fort Calgary / East Village pilot returned
22 features. The WGS84 envelope is west -114.051, south 51.0425, east -114.0425,
north 51.0485. Polygons were clipped to that envelope without simplification,
retaining holes, multipart geometry and attributes. Edges on the rectangular
extract boundary must be understood as extraction limits, not new zoning lines.

Local deliverables, all under ignored `artifacts/calgary-zoning/`:

- `calgary-land-use-fort-calgary.geojson`: 17,438 bytes, 22 features.
- `source-response.geojson`: unmodified API response before clipping.
- `provenance.json`: exact request, timestamps, bounds and checksums.
- `fetch_pilot.py`: bounded extraction script (fails if its result cap is reached).
- `README.md`: import instructions and limitations.

This is a dated extract, not automatic live synchronization or citywide loading.
The existing reference importer accepts GeoJSON and zipped shapefiles; a direct
"Load Calgary zoning around my site" command remains a separate UI increment.

## Import bug found and fixed

The real upload with a source link failed with HTTP 500. Geometry parsing had
already passed independently. A direct call against the isolated local database
reproduced a `TypeError` in `ReferenceLayerMetadata`: `Field(max_length=2048)`
attempted to apply `len()` to a parsed Pydantic `HttpUrl` object.

The schema now validates the length of the serialized URL, retaining HTTP/HTTPS
validation and the 2,048-character storage bound. It applies to both imports and
metadata updates. New API regressions cover import/update provenance, malformed
URLs, unsupported schemes and URLs exceeding the database bound. The earlier
tests only exercised imports without source links, so they missed this failure.

The browser visibility trial also exposed a StrictMode replay bug. The first
toggle read and wrote localStorage inside a state updater; React could replay
it against the newly written storage and reverse the toggle. The updater now
uses a stable state snapshot and an effect persists the committed result.
Regression tests exercise first-click hiding, showing again, remount persistence
and project switching under StrictMode.

## Verification

- The actual file passed `parse_reference_file`: 22 features, expected bounds,
  no warnings, well below importer limits.
- 35 backend tests passed across reference import and reference-layer endpoints.
- The repaired endpoint saved all 22 features against the isolated local database;
  that diagnostic transaction was rolled back before the real browser import.
- The live browser trial uses **Layers → Import reference → Zoning reference**
  in local project `de492723-417b-4729-a76c-f797cc8528d6`.
- The upload created reference layer `f65fdfe6-e489-4879-872c-71e7222b98f3`;
  a subsequent API read confirmed all 22 features and the source link. Provenance
  dates and clipping context were then saved in its description.
- Before/after proposal snapshots matched exactly. Evidence is in
  `artifacts/calgary-zoning/import-result.json`.
- 16 frontend reference-layer tests passed, plus TypeScript and changed-file
  ESLint. A full browser reload was needed after changing hook order during HMR.
- After reloading, the layer and provenance remained available. The first hide
  click changed the control to Show and persisted the hidden ID; Show restored
  visibility. District labels were available in the feature selector and the
  purple boundaries appeared on the globe. The initial HMR error did not recur
  during these post-reload interactions. No final image render was requested.

Reference layers have their own database table. Globe outlines do not intercept
design clicks or become SiteZone building polygons; the existing renderer marks
the reference overlay excluded from direct 3D captures. This pilot does not add
district-coloured fills, on-map labels, terrain draping or automated rezoning advice.
Inspect codes and attributes in the layer panel and use its visibility toggle.

No paid image/video generation, asset promotion or deployment is part of this
pilot. Source changes are limited to URL validation, reference visibility,
regression tests and this note; downloaded GIS data, runtime logs and screenshots
remain ignored.
