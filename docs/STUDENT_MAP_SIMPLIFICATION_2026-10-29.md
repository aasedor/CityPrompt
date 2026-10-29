# Student map controls and Beltline policy coverage

Local implementation on `codex/student-ui-simplification-20261029`. No publication,
deployment, paid generation, or saved-project mutation was needed by this worker.

## Zoning and street names

Saving a site previously changed the zoning query from the map exploration window
to the exact boundary, and the district loader clipped every polygon to it. The
saved-site query now includes a bounded 300 m context margin. The new **Only show
zones within site boundary** checkbox starts unchecked, including migrated
preferences. Checking it clips the cached polygons to the actual site, including
concavities and holes. Labels, outlines, fills and inspection all use that same
display geometry. Toggling does not issue another request. The preference remains
scoped to the browser/project. Existing Calgary/25 km²/1,500-district limits remain;
near those query limits, the unpadded site bounding box is the bounded fallback.

Street names retain the actual selected source segment. Their sprite baseline is
rotated 90 degrees from that segment's projected bearing each frame, including
after orbiting the camera. Text is kept within a readable half-turn; collision
checks use the rotated extent. Degenerate projected segments are hidden. The
underlying renderer still omits crowded names. This is explicitly perpendicular
lettering, as requested, rather than lettering along the road.

## Official Beltline sources

Beltline uses an **Area Redevelopment Plan**, with separate Parts 1 and 2 and
**Land Use Concept** maps. It does not use the newer Local Area Plan Urban Form
classification system. Both parts are available in the existing plan selector,
automatic boundary matching, clipping, opacity, legend and inspection workflow.

Sources checked and downloaded 29 October 2026:

- [City downtown policy and regulation](https://www.calgary.ca/planning/downtown-strategy/policy-regulation.html)
  links the existing official plans separately from proposed amendments. Its
  timeline identifies 9 November 2026 as an anticipated public hearing for the
  strategic amendments. Those proposals are not included in these snapshots.
- [Official Part 1 PDF](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=PTTqycyTceP&msgAction=Download):
  February 2026 office consolidation. Map 3: Land Use Concept is PDF page 25,
  printed page 23, marked amended 51P2025. The consolidation's amendment table
  includes 1P2026. It explicitly advises consulting official bylaws when applying
  policy. This snapshot may omit later amendments.
- [Official Part 2 PDF](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=UTTqycyrcKO&msgAction=Download):
  linked official source with April 2019 publishing information. Map 4: Land Use
  Concept is PDF page 20, printed page 18. The source's own edition is retained;
  retrieval in 2026 does not establish a 2026 map edition.
- [City Policy Plan Boundary service](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Policy_Plan_Boundary/FeatureServer/0):
  approved Beltline Part 1 and Part 2 boundaries, OBJECTID 1929 and 1930,
  respectively. These disjoint GIS polygons determine coverage and matching.
- [City Street Centreline service](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Street_Centreline/FeatureServer/0)
  supplies independent geographic controls for the PDF affine calibration.

## Source extraction and limits

`tools/policy_maps/beltline_calibrations.json` pins PDF SHA-256 hashes, PDF pages,
exact source fill indices and colours, road stroke widths, the City boundaries,
three calibration controls per map and five independent check junctions. The
reproducible extractor fails closed if a PDF hash or reviewed fill changes.
PyMuPDF's quadrilateral operator is expanded into its actual four straight edges.
PDF fill order, holes and white cartographic road gaps are preserved. Transit
station outlines are not treated as roads or cut into policy fills.

The reviewed assets contain 123 Part 1 polygons and 54 Part 2 polygons. Original
RGB legend colours and plan-specific category names are retained. Geographic
rounding is followed by exact boundary clipping and collection-wide overlap
removal. The existing eight-plan metadata/geometry is unchanged.

Independent junction differences after calibration:

| Map | Junction | Difference |
|---|---|---:|
| Part 1 | 8 Street SW / 11 Avenue SW | 0.297 m |
| Part 1 | 1 Street SW / 12 Avenue SW | 0.104 m |
| Part 2 | 3 Street SE / 11 Avenue SE | 0.155 m |
| Part 2 | 3 Street SE / 12 Avenue SE | 0.214 m |
| Part 2 | 1 Street SE / 12 Avenue SE | 0.117 m |

These checks establish alignment at the listed locations, not cadastral accuracy
or survey fitness. The source maps explicitly prohibit deriving measurements.
The overlay does not establish height, density, zoning, current ownership or a
development permission. Potential Open Space is clearly described as potential.

Only base concept fills are displayed. Part 1 omits Warehouse District, Heritage
Commercial Concentration, Special Policy Area and Connaught School symbols, plus
the separate policy/density maps. Part 2 omits Festival Street, transit lines and
stations, Character Areas, and Density and Composition maps. These omissions and
source-edition limitations are visible in the UI. Read the full plan and current
bylaws before interpreting a proposal.

Reproduce with the exact pinned PDFs:

```powershell
python tools/policy_maps/extract_beltline.py beltline-part-1 C:/source/beltline-part1.pdf --output C:/review/part1.json
python tools/policy_maps/extract_beltline.py beltline-part-2 C:/source/beltline-part2.pdf --output C:/review/part2.json
python -m unittest discover -s tools/policy_maps -p 'test_*.py'
```

Original PDFs, raw City boundary/street responses and source-map captures remain
outside Git at `C:/dev-artifacts/CityPrompt/student-ui-maps-2026-10-29/`.
The implementation worker visually compared extracted base fills with both PDF
maps. Native browser rendering, clicking and camera-orbit verification are owned
by the main implementation pass and are not claimed here.
