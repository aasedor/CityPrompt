# Optional public data layers — local review

Open **Layers → Optional public data** in a project. Every option starts off in a new page session. Choices affect only that student's view, not saved designs or imported layers.

## Available choices

Eleven Calgary map overlays: recent property assessment history, building permits, development permits, public water mains, suburban growth and servicing, 2021 community population profiles, historic resources, public trees, 2022 canopy, community services, and schools. Community population details link to full official community profiles for income, tenure and other topics.

CMHC rental-market information and off-site levy information have separate tick boxes for official source-reference cards. These are clearly labelled as cards without map overlays. No finance worksheet or development-cost calculation is added.

## Performance and teaching limits

- Unticked options make no data requests and create no map geometry. Panning does not trigger public-data requests.
- Map overlays require a drawn Calgary-area site. Queries include a 250 m buffer and must remain under 4 km² and 4 km in either dimension.
- Up to four map datasets and two concurrent requests. Each request has a 20-second timeout and a 2 MiB response limit. At most 300 source rows and 4,000 source coordinates/estimated ground samples per layer are displayed.
- Line budgets account for the renderer's ten-metre subdivisions. Public point symbols use one terrain sample rather than the seventeen used by existing transit-stop symbols; the existing transit mode is preserved.
- Unticking or changing sites cancels obsolete work. A ten-minute fresh cache avoids repeat downloads; selecting stale cached data refreshes it. No polling or focus/reconnect refetch.
- Partial and empty results are labelled. Source links, retrieval dates, survey vintages and short limitations accompany selected data. No owner or permit-applicant columns are requested.
- Area overlays draw original source boundaries within the local window. Artificial window edges are never drawn as geographic boundaries. An enclosing area's records remain inspectable even when none of its edges are nearby; counts therefore describe loaded records.
- Assessments are not sale prices; permit estimates are not property values; mains do not establish capacity. Community census values describe whole communities. The new overlays inherit the reference group's exclusion from direct 3D render captures.

## Verification

2026-10-25: 66 focused tests across nine files passed, covering new requests, lazy controls, cancellation, cache freshness, project/site isolation, limits, renderer grounding, existing reference controls, resource disposal and direct 3D capture. A fresh independent code review found an ambiguity in artificial polygon clipping edges; enclosing-window and crossing-window regression cases failed first, then passed after preserving original boundary segments and retaining area attributes without artificial edges. No other Critical, Important or Minor findings were returned. `npm run type-check` passed.

All eleven selected public Socrata schemas accepted a bounded real query (HTTP 200). The actual localhost:5174 project page was tested with all eleven options in finite groups. In the court-only student pilot, examples included 147 water-main records, three community records, 300 public trees with a row-limit warning, 55 canopy records with row/display-budget warnings, 300 building permits with a warning, 79 development permits, 53 historic resources, 153 assessment records with warnings, 13 community services and four schools. Suburban growth correctly showed an empty-result explanation for the downtown site. Both source cards, four-layer selection limits, source attributes and removal were checked. The final area-boundary change was rechecked in top and oblique views with assessments, communities and canopy. The page reported no console warnings or errors during the completed trials.

This is functional verification of bounded behavior, not a hardware-independent frame-rate guarantee. No paid render was generated, and nothing was deployed or pushed. Review screenshots are local output outside the repository: `C:/dev-artifacts/CityPrompt/optional-public-data-20261025/optional-data-checkboxes.png` and `optional-data-original-boundaries.png` in the same folder.

## Implementation choices

The integrated feature is committed as one initiative after browser verification, rather than committing its fetch adapter separately. This makes the commit larger while keeping it reviewable as one feature. Requiring a boundary avoids continuous downloads during exploration; the tradeoff is that students must draw a site first. Official source cards avoid presenting unverified parcel-level rental or levy data; students open the official source for those details. The small public-point mode adds a renderer option, covered by grounding and existing-mode regression tests.
