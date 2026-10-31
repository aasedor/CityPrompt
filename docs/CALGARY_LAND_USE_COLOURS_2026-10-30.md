# Calgary land-use map colours

The existing land-use overlay now uses the published Calgary Land Use Class
palette already captured in `calgaryBylawCatalogue.json` and used by the bylaw
editor. This replaces the separate CityPrompt presentation palette. The map,
inspection card and district legend share the same colour resolver.

Source checked 2026-10-30: [Calgary Land Use Class renderer](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services/Calgary_Land_Use_Class/FeatureServer/0).
Its published RGB values still match the retained catalogue snapshot. No new
runtime fetch or geometry change is needed.

Residential classes use three yellows; commercial uses salmon, commercial core
uses red-salmon, mixed use uses pink, industrial uses grey, parks/recreation/public
education uses pale green, institutional uses blue-grey, and major infrastructure
uses pale blue. Direct Control uses its own mauve without guessing the underlying
use. Centre City and special districts now resolve from their published class
instead of falling through to a generic colour. Unknown codes stay neutral grey.

Verify with the exact published colour tests, geometry vertex colours, existing
map controls/inspection and study tests, TypeScript, lint and the unchanged bundle
budget. Browser review should include CR20-C20/R20, CC-X, CC-MH, S-CRI and DC,
including the map legend and the fill-opacity control. Preserve custom student
study colours, source codes, boundaries and existing saved layer preferences.

Verification completed on local port 5177: 44 existing districts loaded with 35
legend entries; CR20-C20/R20 is core salmon, CC-X commercial salmon, CC-MH/MHX
high-density yellow, S-CRI infrastructure blue, and DC mauve. Checked full opacity
then restored 40% transparency. The 51 focused tests, TypeScript, scoped ESLint,
production bundle limits and independent review passed. No catalogue data,
custom colours, geometry or live deployment changed.
