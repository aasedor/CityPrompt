# Riley Urban Form map pilot — 2026-10-05

The approved Riley plan's Map 3 is now a separate, read-only layer in the Google
3D globe. Open **1 Site → Local area plan → Show Riley policy map**, or use the
Layers panel. The layer has 0–100% opacity, an original-colour legend identifying
categories in the selected site, and an **Only show inside my site** option.
Existing district codes and student zoning studies retain their own controls.

Click a coloured polygon or a legend entry to open its designation explanation.
The selected polygon is outlined; selecting a legend entry outlines that category.
All nine categories have a student summary, three planning considerations and a
link to the relevant section and printed page in the approved PDF. The panel can
be closed with its button or Escape and scrolls on smaller screens.

This is a bounded Urban Form pilot, not the complete local-area-plan policy
analysis. The explanations summarize the category policies in section 2.2.
Building Scale, modified-scale areas, comprehensive planning-site hatching,
active-frontage symbols and parcel-specific policy combinations still require
the original plan. Conditional provisions remain conditional: for example, the
Neighbourhood Local colour alone does not impose the Limited Scale restrictions.

## Sources and extraction

- [City Riley plan page](https://www.calgary.ca/planning/local-area/completed-plans/riley-communities.html).
- [Approved Riley PDF](https://www.calgary.ca/content/dam/www/pda/pd/publishingimages/riley-communities-local-area-plan/Riley-Communities-Local-Area-Plan.pdf),
  PDF page 24 (zero-based page 23), **Map 3: Urban Form**. Approved 25P2025;
  consolidation includes amendment 38P2025, April 9, 2025. The exact source SHA-256
  is recorded in `tools/policy_maps/riley_calibration.json`.
- [City Policy Plan Boundary API](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Policy_Plan_Boundary/FeatureServer/0),
  Riley Communities, OBJECTID 323. Its fields provide the approved plan boundary
  and document references; they do not supply the detailed Urban Form categories.
- [City Street Centreline](https://data.calgary.ca/Transportation-Transit/Street-Centreline/4dx8-rtm5),
  used for independent junction checks, not for fitting the map.

The separate high-resolution three-page map download contains raster images.
The full approved PDF contains vector paths. Extracting these preserves the
City's category colours and boundaries without OCR, image segmentation or AI
generation. There is no embedded geospatial viewport in this PDF.

The extractor preserves even-odd compound paths and holes, samples Bezier curves,
applies the PDF's fill painting order and removes the street-symbol strokes from
the colour fills. It excludes the legend, page background and additional-policy
symbols. Areas without an extracted colour remain transparent. Road gaps are
the published map's generalized symbol widths, not surveyed rights of way.

The reviewed output is **362 polygons, 8,980 vertices, nine categories**, about
343 KB JSON / 67 KB gzip. All polygons are valid, with no material category
overlap. Shared edges are retained; separately simplifying neighbouring polygons
introduced thin overlaps and was removed before promotion.

## Alignment and accuracy

The PDF's outer plan boundary (drawing 1452; filled equivalent 2) was aligned to
the City's GIS plan boundary in NAD83 / UTM zone 11N (EPSG:26911). Calibration
uses a six-parameter affine transform: 1,600 evenly spaced PDF perimeter samples,
a bounded closest-point initialization, then robust point-to-boundary least
squares. The fixed transform and source hashes are in `riley_calibration.json`.
Apply the matrix to PDF point `[x,y]`, add the translation, then transform UTM
coordinates to WGS84 longitude/latitude. PDF y points downward.

Calibration residuals: **0.137 m RMS, 0.238 m at the 95th percentile, 0.879 m
maximum**. These measure the fit to the calibration boundary; they are not an
independent claim of parcel accuracy.

Five separate street-junction points, read from PDF road strokes and compared
with the City's street-centreline geometry, were withheld from calibration:

| Junction | Offset |
| --- | ---: |
| 21 Street NW / 5 Avenue NW | 2.07 m |
| 27 Street NW / 5 Avenue NW | 1.11 m |
| 14 Street NW / Kensington Road NW | 0.09 m |
| 22 Street NW / 14 Avenue NW | 2.76 m |
| 7 Street NW / 2 Avenue NW, eastern centreline node | 3.98 m |

The regression tests retain both PDF points and City coordinates and recalculate
these offsets. Five junctions do not establish accuracy at every parcel. The PDF
generalizes roads and some boundaries, and Google imagery can have its own
positional/parallax differences. Use this for planning context and comparison;
use the original plan and official parcel data for parcel-specific decisions.

The globe draws the overlay at the site's reference elevation, independently of
the underlying photogrammetry. **Top View** is the appropriate alignment check.
The oblique view provides context; this pilot does not drape each vertex over
terrain or building roofs. It does not alter the flat site or building placement.

## Runtime behaviour

- The extracted snapshot loads as a separate cached chunk only when requested.
  Browsers do no PDF processing and make no City policy API request.
- Preferences are scoped per project in optional browser storage. Missing,
  invalid, outside-plan and partly covered sites have explicit states. The exact
  plan polygon determines coverage, not only its bounding rectangle.
- Opacity changes reuse the batched mesh. Off/0% remove the overlay. Full Riley
  uses 7,895 triangles; the Hillhurst test site's clipped map uses 179.
- Normal terrain/model raycasting still ignores the overlay. A browse-mode click
  explicitly tests the rendered policy triangles, including their holes, so an
  angled view selects the visible polygon rather than the ground below it.
  Compact per-polygon face ranges keep the base surface batched.
- Drawing, placement, measurement, walking, entrance/Street View picking and
  navigation drags take priority over policy inspection. Details clear on entry
  into these modes and when the layer is hidden, clipped or made transparent.
  The overlay stays excluded from AI/direct-3D captures and hides during
  zoning-study drawing, like existing district cartography.
- The snapshot is pinned to the reviewed 2025 consolidation. It does not claim
  automatic amendment tracking. A different PDF hash stops extraction until its
  paths, colours and geographic calibration are reviewed again.

## Reproduce and verify

Use Python 3.12 and the offline dependencies in
`tools/policy_maps/requirements.txt`. Download the approved source PDF outside
the repository, then run from the repository root:

```powershell
python tools/policy_maps/extract_riley.py C:/path/to/riley-approved-plan.pdf --output frontend/src/features/policyPlans/data/rileyUrbanForm.json
python -m unittest discover -s tools/policy_maps -p 'test_*.py' -v
```

Frontend verification from `frontend`:

```powershell
npm.cmd test -- --run src/features/policyPlans src/features/referenceLayers/zoningSurfaceGeometry.test.ts src/features/referenceLayers/ZoningLabelsControls.test.tsx
npm.cmd run type-check
```

Results: **25 frontend tests and TypeScript pass**. The three extraction/geography
tests passed for the unchanged polygon snapshot in the original pilot.
React review checked lazy data loading, stable memoized geometry, project-scoped
preferences, labelled native controls and cleanup through the existing renderer.

Browser trial: `localhost:5174`, project
`023faa41-4296-4bae-a3d0-c97099426f2a` (Hillhurst land-use drawing pilot), using the
isolated local API on port 8009. Verified off/on, 0/50/100% opacity, geometry reuse,
site clipping, capture exclusion, non-intercepting picking, reload persistence
and a 1024×768 viewport. No project API writes or browser errors were recorded.
The viewport check is not a physical iPad or forty-student hosting load test.

Designation inspection adds 22 browser checks covering all nine legend entries,
source-page links, Escape, actual polygon clicks in top/oblique views, clipped
polygons, zero-opacity picking, off/on dismissal and tablet panel bounds.
No new browser errors occurred after a fresh load; the browser log retained four
earlier development hot-reload errors, recorded separately in the QA report.
With the policy layer visible, measurement produced a 309 m two-point result and
an unfinished building outline accepted two points without opening policy
details. Both were cancelled; the drawing was not saved.

Reviewed screenshots and detailed local evidence are outside Git at
`C:/dev-artifacts/CityPrompt/riley-policy-pilot-2026-10-05/`:

- `riley-full-plan-solid-top.png` — entire Riley plan over Google context.
- `riley-hillhurst-3d.png` — translucent policy areas in the oblique globe.
- `riley-hillhurst-transparent-top.png` — 50% fill and existing street context.
- `riley-site-only-solid-top.png` — polygons clipped to the drawn site.
- `riley-hillhurst-context-top.png` — matching view with 0% policy opacity.
- `riley-tablet.png` and `browser-qa.json` — viewport and functional checks.
- `riley-policy-polygon-details.png` — clicked polygon, explanation and source.
- `riley-policy-details-tablet.png` and `policy-details-browser-qa.json` —
  designation selection, source links, keyboard dismissal and smaller viewport.

Source changes and the small reviewed geographic snapshot are committed locally.
Downloaded PDFs, browser credentials, research intermediates and screenshots are
external evidence only. This pilot has not been pushed or deployed to Render.
