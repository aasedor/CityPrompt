# San Francisco classified-ground pilot

Status: geographic data, separate elevation authority and provider invariance
verified in a bounded local experiment. **Google/survey surface agreement is not
accepted.** This does not certify survey accuracy or enable production imports.

## Source and limits

[2023 USGS San Francisco LiDAR](https://www.fisheries.noaa.gov/inport/item/73386/full-list),
credited to USGS/NV5, was captured on 20 April 2023. The published metadata records
classified ground, NAD83(2011) source coordinates and NAVD88/GEOID18 metre heights.
The public EPT delivery uses EPSG:3857 horizontally and retains NAVD88 heights.
Access constraints are none; retain attribution, temporal-change cautions and
NOAA's limitation on critical use. No sample is shipped as production content.

Only a roughly 180 m square around Dolores Park (-122.4273, 37.7596) was extracted.
The fixed extraction stops at depth 9, 100 nodes and 25 MB. It downloaded 86 LAZ
nodes / 21,359,401 bytes, retaining 2,242,315 points, including 1,471,550 class-2
ground returns. Withheld points are excluded. Source URLs, bounds and individual
SHA-256 values are retained in the local crop manifest.

Display uses deterministic 0.4 m voxel representatives: 377,195 points, one coarse
and four fine PNTS tiles, totaling 6,129,992 bytes. Ground uses the original ground
returns, not this display reduction. This is a small two-level streaming pilot,
not proof of browser performance for a whole city.

## Coordinates and ground

Horizontal coordinates are inverted from the declared EPSG:3857 delivery.
The [NGS GEOID18 service](https://geodesy.noaa.gov/web_services/geoid.shtml) reports
N = -32.556 m at the source anchor, with 0.03 m reported geoid error. The four
50 m test-grid corners vary by at most 0.001 m from that value. The conversion is
h = H(NAVD88) + N(GEOID18). No visually fitted height or horizontal offsets are used.

GEOID18 supplies NAD83(2011) ellipsoid heights. This pilot uses the approximate
NAD83(2011)-to-WGS84 ensemble operation derived from EPSG:9774 (PROJ reports 2 m
accuracy). The EPT metadata does not preserve its exact original horizontal datum
operation, and Google does not supply a matching survey epoch. This approximation
is explicitly insufficient for survey-grade registration; do not mistake the
source LiDAR accuracy for the accuracy of this entire transformation.

A 50 m square support grid, 21 × 21 at nominal 2.5 m spacing, uses eight nearest
class-2 points with inverse-square-distance weighting. Maximum support distance
is 1.693 m. Heights span -6.007 to 1.816 m above the ellipsoid; negative heights
are valid here. The common SW–NE triangle sampler serves every proposal consumer.
A comparison against 116,196 source ground returns has 0.0205 m RMS fit residual,
0.0370 m p95 absolute residual and 0.3154 m maximum. These are approximation
residuals, not independent survey validation.

## Application contract

The boundary owns a versioned `survey_ground` measurement payload in existing
JSON properties. No database migration or second design state is introduced.
It records the source fingerprint, class, derivation, datum operation and accuracy.
The shared ground provider selects it independently of context visibility.
Missing/malformed/out-of-coverage survey data fails closed; it cannot silently
fall back to Google and move the proposal. Existing projects without that property
retain their original Google/prepared-ground behavior.

The bounded reader validates geographic extent, grid size, finite heights,
coverage, provenance and the existing slope/discontinuity gates. Survey snapshots
identify `classified_lidar` and zero live measurement passes; they do not pretend
to have passed two Google raycast measurements. A debug terrain surface uses the
same ground triangles. Capture is deliberately blocked until the backend render
provenance contract supports this source.

The existing development-only context selector uses a second fixed local manifest
(`/sf-lidar/manifest.json`) tied to the pilot project. Its URLs cannot be supplied
arbitrarily. Google, point-cloud capture and terrain change visual context only.
Normal projects gain no new controls or sample requests.

## Browser evidence

Project `98bd1ffa-e8ef-454b-a52a-e56777b4db17` is a fictional engineering test at the
real Dolores Park location. Its boundary and measured ground were prepared through
the local API. A reviewed Calgary modern infill house was chosen and placed using
the actual catalogue and canvas. This is not a proposed park development or a full
first-time-student acceptance test.

- Google → LiDAR → terrain → Google preserved exact camera position/quaternion,
  native RLASM mesh world matrices/UUIDs and the complete ground snapshot.
- Complete saved zones and the ground snapshot were exactly equal after reload.
- A failed local tileset request restored Google, with unchanged camera/ground;
  an explicit retry succeeded. No retry loop or paid rendering occurred.
- Contact, overview and reload screenshots were inspected. The foundation meets
  the derived sloping terrain. Google alignment remains visibly imperfect.
- Eight open-ground probes found Google 0.709–0.923 m below the converted LiDAR.
  A ninth visible-surface probe hit canopy, 6.531 m above the classified ground.
  The discrepancy is retained, not hidden by moving the proposal or ground.
- No new uncaught browser errors appeared; a fresh reload reported no failed
  resource statuses. Intentionally aborted requests are separate failure evidence.

At 1600 × 1000, three-second samples recorded median 16.7 ms / p95 16.8–16.9 ms
rAF intervals in each context, with none over 50 ms. Google / cloud / terrain
submitted 681 / 33 / 27 draws. The cloud submitted 754,390 point draws across
render passes for its 377,195 stored representatives. Heap observations ranged
433–457 MB and are GC-sensitive. No GPU-memory or speed improvement claim is made.

Far/near camera checks submitted 62,866 / 754,390 points, confirming that the
coarse/fine point-cloud LOD changes. The survey ground review is read-only and
explains that surrounding-surface agreement remains under review. Its screenshot
was visually inspected. The normal Gold Standard main-street view was also
rechecked with Google context, no grounding issues and no failed resources.

Validation: 51 narrow tests across nine suites passed, along with TypeScript and
changed-file ESLint. This is a LiDAR grounding and point-cloud pilot, not a
Gaussian-splat rendering acceptance test; that separate visual-context pilot is
being investigated following the user's clarification.

## Reproduction and remaining work

All source data, preparation scripts, manifests and screenshots are outside Git at
`C:/dev-artifacts/CityPrompt/student-design-transformation/sf-lidar/` (screenshots
in its parent). `fetch-crop.py` and `derive-pilot.py` retain the finite extraction
and conversion. `crop-manifest.json`, `derivation-report.json`, `geoid-*.json`,
`dtm-fit.json`, `google-ground-comparison.json`, `switch-invariance.json` and before/
after reload JSON files preserve the numerical evidence.

Data preparation used the existing NumPy/SciPy/pyproj stack and isolated offline
LAZ readers, laspy 2.7.0 (BSD-2-Clause, 86 KB wheel) and lazrs 0.8.2 (MIT, 433 KB
Windows wheel). These handle classified LAZ decoding, which the existing stack
could not do. They are installed only in the external preparation directory;
there is no frontend bundle, backend runtime or repository dependency addition.

Next: validate the original survey CRS/coordinate epoch against control points
before choosing a more precise datum transformation; measure Google differences
again without fitted offsets; define visual terrain replacement at the proposal
boundary; broaden street/park and out-of-coverage tests; integrate source-aware
render/export provenance. The observed Google mismatch remains an open grounding
and final context gate. Do not claim that context switching alone resolves it.
