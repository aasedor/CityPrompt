# Land-use drawing pilot — 2026-10-05

Students can draw a saved site boundary, open **Site → Zoning map studio**, choose
a Calgary district or custom zone, and draw directly on the Google 3D globe.
Existing and proposed studies remain separate reference layers. Standard districts
receive the City's published Land Use Class colour; custom areas keep a student
name and colour and are explicitly labelled Custom. These are cartographic studies,
not zoning compliance checks or amendments to official district boundaries.

## Source snapshot

`frontend/src/features/referenceLayers/calgaryBylawCatalogue.json` contains 68
district choices and 14 class colours, retrieved 2026-10-05. The dropdown is local
and needs no catalogue network request. Saved/site-specific full designations,
including Direct Control references and modifiers, supplement those choices.

- [Calgary bylaw district index](https://www.calgary.ca/planning/land-use/districts.html)
- [City Land Use Districts dataset](https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh)
- [City-owned Land Use Class map item](https://www.arcgis.com/home/item.html?id=9b9a0fbe41794e34902948dfd30eb04e)
- [Published class renderer](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Calgary_Land_Use_Class/FeatureServer/0?f=pjson)

The renderer's RGB values are converted directly to hex and joined through each
district's `major` class. This names one published City palette; it does not assert
that every City map uses identical symbology. Refresh the snapshot against both the
district dataset and bylaw index when the City changes districts. Keep the source
URLs, retrieval date, and matching colour tests synchronized. Existing saved manual
colours are preserved until the user selects a district again.

## Browser trial

Local frontend: `http://localhost:5174`; isolated API: port 8009.
Project: `023faa41-4296-4bae-a3d0-c97099426f2a`, **Hillhurst · land-use drawing pilot**.
The other existing Hillhurst and Currie trial projects were preserved.

1. Drew a six-corner site boundary with browser mouse clicks and Enter.
2. Drew an R-CG polygon, an S-SPR polygon and an irregular custom Community garden.
3. Saved the proposed layer and reopened it. Verified exact district metadata,
   colours `#fff7da` / `#d3e6bd`, and custom colour `#75b6b0` through the API.
4. Copied 19 clipped City district pieces into a separate existing study and saved.
   Verified both slots independently and retained full DC/modifier designations.
5. Checked 0%, 40% and 100% fill, Escape cancellation, and layer off/on. Opacity
   changes reused the same GPU geometry. Hiding both studies removed their scene
   groups; showing the proposed study restored its three areas.
6. At the user's request, changed this trial boundary to **Clear site for
   redevelopment** and applied its proposed level, 1034.9375555295435 m WGS84
   ellipsoid. Cartographic overlays use that prepared level. The surrounding Google
   tiles remain visible. This is a concept surface, not surveyed grading.
7. Checked desktop 1600×1100 and 1024×768 layout: no horizontal overflow. Physical
   iPad/touch hardware was not tested. A fresh browser run ended with no page errors.

API/geometry verification: one site zone (the boundary), two study layers (3 proposed
and 19 existing areas), all polygons covered by the saved site boundary. Proposed
opacity is saved at 100%. Existing study is hidden for the final proposed view.
The demonstration proposal is not a claim about Hillhurst's statutory zoning.

## Checks and local evidence

- 31 Vitest tests passed across catalogue, study geometry/export, editor, map drawing
  bridge, zoning surface geometry and existing drawing geometry.
- 25 focused backend zoning-study tests passed.
- Frontend TypeScript check and `git diff --check` passed.
- No migrations, paid image generation, deployment or source push.

Screenshots, raw API inspection, and browser helpers are outside the source tree in
`C:/dev-artifacts/CityPrompt/land-use-drawing-2026-10-05/`. Reviewed final images:
`10-final-cleared-plan.png` and `11-final-cleared-oblique.png`.
`trial-verification.json` records the filtered API/geometry checks. These generated
files are not part of the source commit.

## Site boundary opacity follow-up

**Site → Review site boundary → Site boundary opacity** provides a 0–100% slider.
Use **Save Changes** to apply it. The value persists in the boundary's properties,
independently of either zoning study's opacity. Older prepared boundaries retain
their solid appearance; boundaries following existing terrain retain their clear
fill until explicitly edited.

Partial opacity reveals the original Google tiles, including roads and buildings.
The prepared level, flat placement surface and boundary outline remain in place.
At 100%, the prepared boundary clips the source tiles again. Independent road cuts
remain active at every opacity. The surface writes flat depth before authored
buildings, so original rooftops cannot hide proposals. Exact GLB review buildings
now use the same render order as other authored building geometry.

Browser verification on the same Hillhurst project:

- Saved 0%, 50% and 100%; reloaded and confirmed 50% in the slider and API.
- Placed a temporary fourplex through the catalogue. Its prepared datum remained
  1034.9375555295435 m and its foundation anchor 1034.977555527964 m at both
  endpoints, with no reported grounding issues. Verified the fourplex visually
  against the revealed Google context at 50%.
- Removed the temporary fourplex and its automatic landscape after the trial.
  The pilot retains the original boundary and both zoning studies; boundary
  opacity is now 50% for review.
- 59 focused Vitest tests across the properties panel, tile masking, prepared
  surface and exact GLB placement passed, along with the TypeScript check.
  The browser reported no page errors.

Final screenshot: `18-final-site-opacity-50.png`; building verification:
`15-opacity-flat-building-trial.png`, in the external evidence directory above.
No migration or backend change was required. This follow-up is local only.
