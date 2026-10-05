# MDP and CTP map layers

Initiative: `codex/citywide-policy-maps-2026-10-05`, based on the Riley policy
map checkpoint `8acd57351`. Local implementation; no production deployment.

## Student workflow

Open **1 Site → City-wide policy maps**, or the same controls under **Layers**.
Expand Municipal Development Plan or Calgary Transportation Plan. Every map
has an independent switch and 0–100% opacity slider. Preferences are local to
the browser and project; all maps start off. “Hide all” clears the city-wide
overlays together. The existing zoning and Riley layers remain separate.

Click visible map artwork, or **Legend & meaning**, to read a short explanation,
the original City legend, and a link to the relevant PDF page. Legend images
can be enlarged. Escape closes the explanation. Drawing, placement, measuring,
walking and street-view picking retain priority over map inspection.

These are georeferenced published map images with original colours, lines,
symbols and hatching. Inspection explains the map as a whole; it does not
identify an individual road or polygon. Riley retains its individual
designation/polygon inspection. Student guidance is separate from the City's
written policies. Top View gives the clearest geographic comparison.

## Published sources

Both PDFs were retrieved 5 October 2026 from the City statutory plan library,
office consolidation **23 June 2026 / 18P2026**. The City still lists MDP and
CTP as current plans; its MDP landing page describes a proposed 2027 replacement.

- [Municipal Development Plan](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgAction=Download&msgID=OTTKcgyTerX)
- [Calgary Transportation Plan](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgAction=Download&msgID=ETerrTTsycC)
- [City MDP information](https://www.calgary.ca/planning/municipal-development-plan.html)

| Plan/map | Title | PDF page | Printed page |
|---|---|---:|---:|
| MDP 1 | Urban Structure | 188 | 160 |
| MDP 2 | Primary Transit Network | 189 | 161 |
| MDP 3 | Road and Street Network | 190 | 162 |
| MDP 4 | Open Space and Naturally Vegetated Lands | 191 | 163 |
| MDP 5 | Jurisdictional Areas | 192 | 164 |
| MDP 6 | Major Development Influences | 193 | 165 |
| CTP 1 | Always Available for All Ages and Abilities (5A) Network | 100 | 92 |
| CTP 2 | Primary Transit Network | 101 | 93 |
| CTP 3 | Downtown Transit Network | 102 | 94 |
| CTP 5 | Primary Goods Movement Network | 104 | 96 |
| CTP 6 | Primary HOV Network | 105 | 97 |
| CTP 7 | Road and Street Network | 106 | 98 |

CTP Map 4, Conceptual Calgary Regional Transit Plan, is explicitly removed on
PDF page 103. The controls explain its absence. Shared MDP/CTP themes retain
their separate published page references.

## Geographic registration and limits

`tools/policy_maps/citywide_calibration.json` pins the exact PDF SHA-256 hashes,
pages, affine transforms and checks. Transforms map PDF points into NAD83 / UTM
zone 11N (EPSG:26911), then WGS84 longitude/latitude.

Nine maps use the published dashed City boundary matched to the City GIS
[City Boundary service](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/City_Boundary/FeatureServer/0).
Their outline fit residuals are approximately 1.3–1.4 m RMS. The 5A and
Jurisdictional maps were registered to the calibrated boundary using rendered
outline ink. Downtown uses its Centre City outline matched to the calibrated
Urban Structure map, including the page's 90-degree rotation.

An independent check at **14 St NW / Kensington Rd NW**, using City street
network coordinates (-114.0947104, 51.0525233), measures 2.27–3.64 m for seven
maps and 26.59 m for 5A. This is one check location, not a city-wide accuracy
certification. The other four maps lack an extractable matching junction in
this check; they have visual comparison and outline registration only.
Initial automatic nearest-vertex searches matched unrelated road vertices
where roads crossed between vertices; these were rejected in favour of the
actual noded intersection. They are not reported as registration accuracy.

The raster registrations' saved `diagnosticOnly` distances include missing
dashes and excluded/coloured ink; they are explicitly not accuracy estimates.
Jurisdictional Areas originates as a lower-resolution raster inside the PDF.
The policy sources generalize routes and symbols; map widths and buffers must
not be read as surveyed parcel boundaries or engineering dimensions. The globe
uses a curved reference surface at site elevation, not a terrain survey.

## Delivery and performance

- Artwork is processed offline; students do not download or parse the PDFs.
- Each active map first loads its small geographic manifest and a 1024-pixel
  overview. In-view 512-pixel tiles load when zoomed close enough to need detail.
- Geographic meshes are reused during opacity changes. Textures are disposed
  when their map/detail view is no longer needed; retries affect one map.
- Paper becomes transparent. Original map RGB colours remain intact. Page
  furniture is removed from the overlay; original legends are provided separately.
- City policy overlays are excluded from direct 3D render captures, matching
  the existing reference-map behaviour.
- 12 manifests and 724 WebP images occupy approximately 62 MiB on disk. This
  is the full optional library, not the initial page download. WebP delivery
  files use Git LFS. Production prebuild checks hydration and every referenced
  tile, so a checkout containing LFS pointers fails before deployment.

Regeneration requires `pip install -r tools/policy_maps/requirements.txt` and
the two pinned PDFs named `mdp.pdf` and `ctp.pdf` in an external source folder:

```powershell
python tools/policy_maps/tile_citywide.py --sources C:/source --output C:/review
python -m unittest discover -s tools/policy_maps -p test_citywide.py
```

Review overviews and legends before promoting only the files referenced by each
manifest. Recalibrate and review if the PDF hash changes. The tool refuses
unreviewed replacement PDFs. Source PDFs, intermediate images, browser auth,
test launchers and screenshots stay outside the repository under
`C:/dev-artifacts/CityPrompt/citywide-policy-2026-10-05`.

## Verification

- 103 policy and reference-layer tests passed; TypeScript check passed.
- Five offline extraction checks cover inventory, colour/alpha preservation,
  exact neighbouring tile seams, the independent junction checks and downtown
  orientation. Asset delivery checker validates every referenced WebP.
- Local Chrome on `localhost:5174`, dedicated classroom trial project/API:
  all 12 maps loaded; native canvas clicks opened the matching card; legends
  loaded; Escape closed cards; zero/full opacity and off toggles worked.
- Two simultaneous layers retained independent opacity. The 1024×768 layout
  kept the details card within the viewport with no horizontal overflow.
- All 12 maps also loaded simultaneously. Reloading retained the enabled MDP
  map and 40% opacity, with only that map present in the scene. Riley details
  replaced city-wide details correctly. The final browser error log was empty.
- This is local functional/visual verification. Render deployment, a live
  40-student load trial and physical iPad testing are separate work.
