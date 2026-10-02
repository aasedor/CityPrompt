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
