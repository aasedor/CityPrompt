# Calgary elevation trial — 2026-10-02

## Outcome

The bounded trial loaded Calgary's actual 2 m bare-earth DEM over two real sites
in City Prompt and tested a 60 m diagnostic connection to a visible paved junction.
The data is useful for ground shape, but **automatic alignment with Google's
visible surface is not accepted**. No production ground-source behavior changed.

Land-use work was pushed first to `origin/codex/parcel-zoning` at `6fc24a9ee`.
The separate elevation initiative is local on `codex/calgary-elevation-trial`.

## Source and preparation

- [Calgary's 2 m DEM dataset](https://data.calgary.ca/Base-Maps/Digital-Elevation-Model-DEM-ASCII-2m/eink-tu9p/about_data)
  and its [2024 metadata](https://data.calgary.ca/api/views/eink-tu9p/files/5f381905-9061-402c-b8f5-b0753c47944c?download=true).
- Downloaded two ASC sections from the official ATS archive with validated HTTP
  range requests. Total source transfer: **2,367,792 bytes in 17 requests**,
  including archive directory and header inspection. The 1.59 GB archive was not
  downloaded in full. Discovery was bounded to 36 candidate sections, 180 requests
  and 32 MB; only sections 06-24-01-W5 and 07-24-01-W5 were retained.
- Horizontal source: EPSG:3776, NAD83 original / Alberta 3TM 114W. Heights are
  declared CGVD28, with the GSD95 ITRF geoid model. Source files and their SHA-256
  hashes are recorded in the external download manifest and preparation output.
- Cell-centre bilinear sampling respects north-first ASC row order. Missing
  source cells and points outside interpolation support are rejected. Two 60 m
  squares use 31 × 31 samples at 2 m spacing. This does not create finer source
  information or classify bridge decks, steps, or curbs.

The reproducible preparation helper is `tools/elevation_trial/calgary_dem.py`.
It uses the local NumPy, pyproj and requests environment, with no application
dependency or API change.

## Coordinate conversion and limits

The [NRCan GPS·H service](https://webapp.csrs-scrs.nrcan-rncan.gc.ca/geod/tools-outils/gpsh.php?locale=en)
was queried with **GSD95, ITRF2014, epoch 2024-01-01** at the site centres and
corners. Full query parameters and service responses are retained. For this
diagnostic display, `h = H + N` uses the source-stated GSD95 model; N varies
bilinearly across each square. This is a declared approximation, not an accepted
survey registration or a claim that all CGVD28 realizations equal GSD95.

- Both centre results: **N = −16.005 m**.
- Corner ranges: slope −16.006 to −16.004 m; street −16.007 to −16.004 m.
- The app's existing broad regional estimate is −25 m. It must not be reused as
  this dataset's geoid conversion: the difference here is about **9 m**. This
  does not establish that all existing Google-based placements have a 9 m error.
- PROJ's available NAD83-original / WGS84-ensemble operation reports **4 m
  accuracy**. A source coordinate epoch is not specified; the ITRF2014/2024 choice
  is a trial assumption. Horizontal displacement on slopes can also appear as a
  vertical disagreement. GSD95/CGVD28 realization, coordinate epoch, acquisition
  age, and mesh errors remain confounding factors.
- No visual fit, constant correction, terrain clamping, or Google-derived
  adjustment was applied to Calgary elevations. The measured residual cannot be
  attributed entirely to either provider's accuracy.

## Browser measurements

Preview: existing isolated localhost:5194 frontend, backend:8018. Two dedicated
QA projects were created; previous designs were not edited.

| Trial | Centre (longitude, latitude) | DEM relief in 60 m square | Median Google minus converted DEM | Visible-surface range |
|---|---|---:|---:|---:|
| Slope / sports-field embankment | −114.1265, 51.0245 | 5.174 m | −1.402 m | −1.972 to +10.615 m |
| Street approach / verge | −114.1200, 51.0160 | 3.704 m | −1.403 m | −1.922 to +11.355 m |

Each site had 73 probes: a sparse grid plus a centre profile. Three passes used
only visible Google tile meshes; all probes returned plausible heights. Maximum
change between the last two passes was **0 m** in these runs. Repeatability here
establishes a stable loaded mesh, not independent elevation accuracy. The
all-surface statistics include trees and other objects; they are not ground-only
error statistics. The six southern centre-profile probes on the slope's visible
open field ranged from −1.422 to −1.254 m (median −1.301 m).

Screenshots show a cyan DEM wireframe through the context to make comparison
possible. This deliberately ignores visual occlusion for that debug wireframe;
it does not represent a cleared site or alter collision/grounding.

### Connection trial

A separate 60 m × 6 m diagnostic corridor was sampled eastward from the street
site toward the paved roundabout approach, using the same ASC source. Its 31
centre-profile probes were sampled three times against visible tiles. The final
DEM endpoint was **1.609 m above the visible Google paved surface**, with 0 m
change between the last two passes. Overhead and oblique screenshots were
visually reviewed to check that the endpoint reaches the pavement.

The cyan strip represents a DEM-derived profile, not a graded native street
archetype, walkable route, or accepted physical road connection. No blending was
applied to conceal the mismatch. Saved site-zone JSON before/after was identical;
the diagnostic had zero design mutation requests and zero browser page errors.

### Existing ground review

The app's existing Google ground checks correctly continued to flag uncertain
areas near vegetation. These notices were not suppressed. This trial does not
resolve those warnings, test exports, certify accessible grades, or enable a new
production survey import. Debug overlays exist only for the automated browser
session and must be rerun to display them; the QA project boundaries remain saved.

## Verification and evidence

- 3 offline reader tests passed: cell centres/row orientation, missing-data
  rejection and out-of-support rejection.
- Two site comparisons and the connection trial completed with zero browser
  page errors and zero design writes during measurement.
- Overhead and 3D screenshots were inspected. No Google tiles were hidden or
  modified to make the surfaces look aligned.
- Source-only files are the preparation helper, its tests, and this report.
  No TypeScript/backend runtime files or generated assets were changed.

All source data, range-download helpers, manifests, geoid responses, browser
scripts, measured JSON and screenshots remain outside Git:

`C:/dev-artifacts/CityPrompt/calgary-elevation-2026-10-02/`

Key files: `download-manifest.json`, `trial-data.json`, `browser-comparison.json`,
`street-connection.json`, `browser_trial.cjs`, `street_connection.cjs`,
`slope-dem-3d.png`, `street-connection-top.png`, `street-connection-3d.png`.

QA project IDs:

- Slope: `2910580c-fb75-4c32-8f02-22c1774f6163`.
- Street: `c81bf288-7a9c-4cfb-bf74-773a67d992fa`.

Reproduce preparation after the bounded download:

```powershell
python tools/elevation_trial/calgary_dem.py --data C:/dev-artifacts/CityPrompt/calgary-elevation-2026-10-02 --out C:/dev-artifacts/CityPrompt/calgary-elevation-2026-10-02
python -m pytest tools/elevation_trial/test_calgary_dem.py -q
```

## Next implementation gate

The coordinate conversion portion of gate 1 was implemented in the follow-up
below. Independent control and the Google surface mismatch remain unresolved.

1. Resolve the source datum realization and choose a better justified horizontal
   and vertical operation, ideally checked against independent control points.
2. Keep surveyed ground and visual-context alignment as separate, explicit
   concepts; never alter an entire site's ground to satisfy a road endpoint.
3. Prototype a bounded local transition at an existing-road connection, with
   rejected/uncertain endpoints handled explicitly. A fixed citywide −1.4 m
   correction is not supported by this trial.
4. Re-test near trees, on sloping ground, and across differing acquisition areas
   before promoting any source selection or corridor replacement to students.

The data has not been redistributed or published. Calgary's portal licence and
the attachment's restrictive wording still need reconciliation before a hosted
data release; that did not prevent this small local evaluation.

## Coordinate alignment follow-up — 2026-10-02

### Implemented operation

`tools/elevation_trial/calgary_alignment.py` now provides an explicit conversion
for the recorded baseline. It preserves the same physical DEM sample positions
and orthometric heights, replacing the baseline's identity datum assumption:

1. Interpret the baseline's longitude/latitude as NAD83 Original (its EPSG:3776
   inverse projection was followed by the identity NAD83-to-WGS84 operation).
2. Apply Alberta's **ABCSRSV7** NTv2 grid to obtain NAD83(CSRS)v7 at **2010.0**.
3. Apply **inverse EPSG:8265** at 2010.0 to obtain ITRF2014 coordinates.
4. Query NRCan GPSH GSD95 in ITRF2014 at that same epoch, then use `h = H + N`.

Alberta's [coordinate transformation fact sheet](https://open.alberta.ca/dataset/e953c4f5-4789-4b86-9459-a845f2314033/resource/d8591c1f-d387-4ea4-a069-5df019ab8826/download/c_localdataweb-docsgeodetic_control_unitweb-docs-publish-march-2021fact-sheetsfactsheet5-transfo.pdf)
identifies ABCSRSV7 as the Original-to-CSRSv7/2010 grid and describes ABCSRSV4 as
an older adjustment. The current grid comes from the
[Alberta download catalogue](https://open.alberta.ca/opendata/national-transformation-analysis-data-tables-1-to-12).
It is 1,307,520 bytes, with SHA-256
`f5cf8cfa53e6922ebfa02d4b76400d02c84b840cf5a298b79b00bb82606cf2aa`.

The helper requires that exact grid and frame operation. Missing or different
grids, unsupported baseline shapes, invalid coordinates and already-converted
input are rejected. There is no approximate fallback. Source and display heights
stay separate: the Helmert height change is not added a second time after GPSH.
Frame pipeline, coordinate epoch, versions, hashes and raw geoid responses are
recorded. The output directory must differ from the baseline directory.

This is still approximate alignment to Google's unspecified WGS84 realization
and imagery epoch. We use the grid's documented 2010 epoch; we do not pretend to
propagate it to 2024 by changing the Helmert timestamp alone. PROJ explains that
[time-dependent transforms require the coordinate epoch](https://proj.org/en/stable/operations/transformations/helmert.html).
Absolute accuracy remains unquantified. EPSG's zero accuracy for the defining
frame operation does not mean the DEM, grid, or rendered scene has zero error.
No independently surveyed control point was acquired in this trial.

### Browser results

Re-ran both 60 m sites (73 visible-tile probes each) and the 60 m corridor (31
probes), three passes each. Measurements below are **Google height minus DEM
height** except the road endpoint, which is explicitly DEM above Google.

| Measurement | Original trial | Aligned trial |
| --- | ---: | ---: |
| Slope site, median of all surface probes | -1.402 m | -1.360 m |
| Street site, median of all surface probes | -1.403 m | -1.379 m |
| Slope open-field subset, median of same six source samples | -1.301 m | -1.306 m |
| Road endpoint, DEM above visible pavement | 1.609 m | 1.525 m |

Horizontal positions moved **1.429–1.433 m northwest**. Matching the geoid epoch
lowered displayed heights by **19–20 mm**; source DEM heights did not change.
All-surface medians include vegetation and other objects and are not ground
control statistics. The open-field subset remains the six southern centre-line
samples selected in the original trial, not a new selection fitted to results.

All probes returned a hit. The final two passes agreed exactly, with zero browser
page errors and zero design mutation requests during measurement. The corridor's
saved site-zone JSON was identical before and after. Overhead and oblique images
were inspected; the endpoint still reaches pavement. Existing ground warnings
near vegetation remain visible. The corridor is still a diagnostic mesh, not a
graded or walkable street archetype.

**Conclusion:** the coordinate conversion is implemented and tested. It does not
eliminate the vertical difference with Google's reconstructed surface. A fixed
citywide downward adjustment is still unsupported. Production integration and a
local road transition need a separate test; neither is enabled by this change.

### Reproduction and checkpoint

Download the exact grid linked above into the external alignment directory, then:

```powershell
python -m tools.elevation_trial.calgary_alignment --baseline C:/dev-artifacts/CityPrompt/calgary-elevation-2026-10-02/trial-data.json --grid C:/dev-artifacts/CityPrompt/calgary-alignment-2026-10-02/ABCSRSV7.DAC --out C:/dev-artifacts/CityPrompt/calgary-alignment-2026-10-02
$env:CALGARY_ALIGNMENT_GRID='C:/dev-artifacts/CityPrompt/calgary-alignment-2026-10-02/ABCSRSV7.DAC'
python -m pytest tools/elevation_trial/test_calgary_dem.py tools/elevation_trial/test_calgary_alignment.py -q
```

**14 tests passed**, including official-grid round trips, shift direction,
fail-closed input checks, source preservation and single application of the geoid
correction. Three grid integration cases require the environment variable above;
they skip when the external grid is unavailable. No production TypeScript or
backend runtime code changed.

Alignment outputs are separate from the preserved baseline:
`C:/dev-artifacts/CityPrompt/calgary-alignment-2026-10-02/`.
This contains the grid, `trial-data.json`, GPSH responses, adapted browser scripts,
`browser-comparison.json`, `street-connection.json`, and inspected screenshots.
These data and generated files remain outside Git. Source changes are the new
alignment helper, its tests, and this report; the checkpoint remains local.

New QA projects: slope `e3d543e6-c8aa-48b5-bed9-84c8022465dc`; street
`3ceef542-2cef-4370-8cb6-715a59cebcd7`. Debug overlays are session-only; rerun
`browser_trial.cjs` and `street_connection.cjs` from the alignment output directory
to display them. Saved projects contain only the trial boundaries.
