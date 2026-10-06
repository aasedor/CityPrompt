# Calgary zoning and the classroom catalogue

Click a coloured City zoning polygon or a saved student study zone to inspect catalogue candidates. Choose **Buildings** or **Parks** in the panel. The district legend provides keyboard-accessible inspection buttons. The drawing studio also shows the same lists for its selected zone, updating immediately when the district changes. Custom zones and Direct Control designations explain why ordinary district matching is unavailable.

This is a **new-building use and model-envelope height screen**, not a development-permit determination. Permitted and discretionary candidates have a listed use route and pass the preliminary height comparison. Missing program details, existing-building prerequisites, contextual rules and unknown mapped heights remain in “More information needed.” A model can match several districts. Every required component of a mixed-use program must have a listed route.

**Parks use a separate land-use-only screen.** A park assembly's height can be dominated by trees, so it must not be compared with building-height limits. The park panel and every result state that buildings, shelters and elevated structures require separate measurements and site checks. This includes the conservatory, bridges, pergolas and lookouts. A permitted park use is not approval of every object in its model.

## Park programs and land uses

All **32 current park placements** have explicit programs in `parkPrograms.json`: 28 native layouts and four flexible layouts. Records bind placement ID, variant ID and exact revision. Native and flexible pocket parks/greenways share variant IDs, so variant-only deduplication or classification would lose a layout or apply the wrong program. Unknown or changed layouts remain unclassified. No geometry or catalogue eligibility changed.

`parkUseRules.json` adds 129 relevant use routes across the same 68 district records, with section and definition references; the existing building/height snapshot remains intact. The source for each is the corresponding district's `source` in `districtRules.json`. Conditional former-school and existing-building routes remain review-only. The data was checked against the October 5 source retrieval, including the unpunctuated Park entry in R-C1 s.385(1), and M-G s.606.

| Intended use | Catalogue layouts |
|---|---|
| Park | Conservatory botanical garden; Museum sculpture court; Neighbourhood orchard; Timber and stone square; Wetland boardwalk; Teaching demonstration garden; Shaded Reading Garden; Rustic Pocket Garden; Railway Meadow Greenway; Inclusive Woodland Playground; Woodland Stream & Bridge Garden; Reflecting Fountain Garden; Urban Splash-Play Plaza; Stone Labyrinth Garden; Sheltered Dog Park; Community Allotment Garden; Forest Adventure Nature Play; Spiral Lookout Park; Quarry Garden; Cascade Water Garden; Treetop Walk Park; Terraced Rose Garden; Flexible pocket park; Flexible linear greenway; Flexible shade courtyard; Flexible meadow grove |
| Outdoor Recreation Area | Basketball park; Pickleball Social Garden; Garden Tennis Court; Bocce Pergola Garden |
| Park + Performing Arts Centre | Terraced performance lawn, screened as a programmed performance venue |
| Park + Outdoor Café + supporting food use (review required) | Terraced Café & Fountain Court; the trial assumes Restaurant: Food Service Only, but the operator and facilities must be established before confirmation |

These are stated teaching programs, not classifications inferred from appearance alone. Each card explains its assumption and links both the district permission and the use definition. Community gardens and orchards assume recreational/social growing rather than commercial production. Ornamental wetland/meadow/woodland designs are not automatically classified as Natural Area; none of the current models establishes an ecological conservation or naturalization program. Private accessory amenity space, off-leash operations, and an incidental event in a park can require a different review.

Relevant definitions and district examples:

- [Park, s.249](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=P#section249): open space for recreation, education, culture or aesthetics, including qualifying community growing. [Performing Arts Centre, s.255](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=P#section255) covers public live performance.
- [Outdoor Recreation Area, s.248; Outdoor Café, s.247](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=O): sports/athletic activity is screened separately; the café requires an associated qualifying principal food use.
- [Natural Area, s.243](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=N#section243): conservation or naturalization must be established, beyond a visual planting style.
- [S-SPR s.1026](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=9&div=3) lists both Park and Outdoor Recreation Area as permitted. [S-R ss.1042–1043](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=9&div=5) lists Park as permitted and Outdoor Recreation Area as discretionary. R-CG s.526(1) lists Park; its list does not provide the same standalone outdoor sports route. R-C1's outdoor recreation route depends on the former-school condition in s.386(3).

Expected current park counts: S-SPR 30 permitted, two outside this screen; S-R 26 permitted, five discretionary and one requiring program information; R-CG 26 permitted and six outside. S-UN has no confirmed candidates from these ornamental/recreational teaching programs. S-SPR, S-R and S-UN open on Parks by default; other districts start on Buildings, with Parks one click away. The choice stays selected when rezoning the active study zone.

## Evidence and scope

- Snapshot date: October 5, 2026. The 68 district choices have source links, relevant permitted/discretionary use entries, section references and preliminary height rules in `frontend/src/features/zoningCatalogue/districtRules.json`. This is a subset of uses relevant to the catalogue, not a reproduction of the complete bylaw.
- Primary source: [City of Calgary online Land Use Bylaw 1P2007](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html). District sources are attached to every rule record. Sources were retrieved during this implementation; do not replace them with recollected historical limits.
- [R-CG ss.526–527 and 541](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5&div=11): the retrieved consolidation sets a 10 m general maximum, with additional height-plane/rear/corner conditions. Contextual houses and rowhouses do not automatically qualify for a permitted route from their appearance alone.
- [R-G/R-Gm s.547.3](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5&div=12): Single Detached Dwelling is permitted in R-G but discretionary in R-Gm. The two district records must remain independent.
- [MU-1 ss.1366–1367](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=14&div=2): permissions conditional on an existing approved building are not carried onto a new catalogue building. Explicit new-building discretionary routes are retained. MU-2 has the equivalent distinction in ss.1376–1377.
- Full `f`, `h` and `d` designation text is preserved. Height-dependent districts with no applicable `h` value remain unconfirmed. FAR and density are not evaluated. Unrecognised designations never inherit an inferred district.
- The current catalogue contains **34 exact placeable building variants**. `buildingPrograms.json` binds each teaching program to its exact model revision. Nineteen have a stated program usable for preliminary screening; fifteen require program clarification. Changed revisions fail safely pending classification review. Historical catalogue families are not made available by this feature.
- Program evidence: exact asset descriptions and revisions in `validationCatalogue.json` and `classroomExpansion.json`, plus the matching variant descriptions in `buildingArchetypes.json`. The earlier September 2 crosswalk is context only; see `CALGARY_RESEARCH_RECONCILIATION_2026_09_05.md`. No building geometry, catalogue eligibility or published assets changed.

Model dimensions are measured envelopes from the runtime registry. They are not substituted for Calgary's grade-based height method. Spires, roof exemptions, height planes, parcel size, setbacks, coverage, density, floor area, parking, access, use-specific limits and location overlays require further review. Centre City/no-maximum entries do not waive those rules. Special-purpose or mapped height areas without a verified numeric comparison remain review-only.

## Verification

63 focused Vitest tests passed across building/park matching, panel behaviour, geometry picking, existing zoning and study editing; TypeScript and the production Vite build passed (the existing large-chunk warning remains). The React best-practices checklist was applied to the touched components. Browser verification used the Hillhurst trial project on localhost:5174:

- Native canvas clicks selected an existing M-CGd72 polygon and a proposed R-CG polygon.
- R-CG showed four discretionary candidates; changing the proposal to R-G showed eight permitted candidates. Undo restored R-CG without saving changes to the project.
- Tested full C-COR2f2.8h16 designation, DC fallback, custom zone explanation, legend buttons, Escape/focus, layer hiding, zero opacity, reopening opacity, site-boundary review and 768×1024 layout.
- No uncaught browser errors. Some pre-existing catalogue preview files are missing locally; cards show a neutral building placeholder when an image fails.
- Park extension: existing S-R showed 26 permitted and five discretionary park candidates; switching R-CG between Parks and Buildings preserved their distinct counts. The proposed S-SPR drawing-studio panel showed 30 permitted parks, changed to five discretionary candidates when rezoned to S-R, and Undo restored S-SPR without saving project changes. A native canvas click on the proposed S-SPR polygon opened the Parks panel (existing study hidden for unambiguous selection); its 768×1024 bounds, no horizontal overflow and Escape dismissal passed. Visibility preferences were restored. No uncaught browser errors. Park cards use a tree placeholder when an existing thumbnail is unavailable.
- Source/data changes are under this document and `frontend/src/`. Research HTML, test screenshots and the build log stay outside Git at `C:/dev-artifacts/CityPrompt/zoning-catalogue-2026-10-05/`. The build used the existing external build helper and output directory under `C:/dev-artifacts/CityPrompt/local-area-plans-browser-followup-2026-10-05/build/`.

## Maintenance

Recheck the linked bylaw when the City changes its consolidation. Review conditional clauses, cross-references and inherited/general district rules before promoting updated facts. Never automatically promote scraped text into approved matches. R-CG contextual permitted routes, worship size classes and historic/existing-building conditions need facts beyond a model label. To resolve the program queue below, record the missing occupancy/arrangement facts for the exact variant, update its components and assumption, and remove its review hold only after that evidence is available.

The matcher reuses the current canonical catalogue and compares locally on selection; it makes no per-click network or AI requests. Map inspection reuses already-rendered triangles, preserves holes and keeps native raycasting disabled for drawing and terrain sampling. Hidden/transparent layers and editing/navigation modes do not intercept map clicks. Student zones take precedence over City zoning when both overlap; policy map inspection remains separately prioritised. Selection is resolved against live records and cleared on hiding, deletion, editing or project change.

## Exact-model program review

The table below lists the intended teaching program, not the established occupancy of a real-world property. “Screenable” still requires an applicable district use route and height comparison.

| Catalogue building | Model height | Program status | Assumption / missing evidence |
|---|---:|---|---|
| Beltline mixed-use mid-rise | 20.4 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Blue glass office tower | 99.0 m | Screenable | Office tower, including its entrance lobby; no residential use assumed. |
| Brick courtyard entrance building | 12.3 m | Needs program review | Confirm the number and arrangement of homes and whether all required access is within this building. |
| Buff-brick infill | 10.7 m | Needs program review | Confirm whether this exact model contains one dwelling or multiple attached dwellings, and their access arrangement. |
| Calgary Modern Infill | 7.0 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Charcoal Gable Fourplex | 9.6 m | Needs program review | Four entrances do not establish a legal Rowhouse Building. Confirm stacking, party walls and unit access before choosing the bylaw use. |
| Corner Café & Apartments | 20.6 m | Screenable | Apartments over an unlicensed café. A licensed restaurant would need its own use check. |
| Crystal brewhouse | 14.6 m | Needs program review | Confirm the intended production program and whether a public taproom or restaurant adds another use. |
| Earth-sheltered museum | 8.8 m | Screenable | Museum exhibition and visitor spaces. |
| Edwardian Foursquare | 10.8 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Gilded Terracotta Tower | 68.6 m | Needs program review | Catalogue sources conflict between office and residential use. Choose and verify the occupied program before matching. |
| Gothic Community Church | 44.0 m | Needs program review | Assembly area has not been recorded. Confirm the worship size class and how the spire is measured for height. |
| Grand Deco Cinema | 21.4 m | Screenable | Cinema/movie theatre, with associated lobby spaces. |
| Grand Iron & Glass Market | 19.1 m | Needs program review | Confirm the vendor mix, food preparation and shared areas; market architecture alone does not determine all required uses. |
| Halifax clapboard house | 10.5 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Living-Roof Aquatic Centre | 16.6 m | Screenable | Indoor swimming facility. A community-operated facility may follow a different use definition. |
| Machiya cafe and gallery | 8.4 m | Needs program review | Confirm whether the gallery is a museum, retail art gallery or artist’s studio; each uses different bylaw definitions. |
| Mass-timber Library | 15.5 m | Screenable | Library reading, collection and associated spaces. |
| Mediterranean Courtyard Hotel | 13.6 m | Screenable | Hotel guest accommodation with associated reception and pool. |
| Nordic Roof-Garden Apartments | 22.8 m | Screenable | Residential apartments; no shops or offices assumed. |
| Plateau stacked duplex | 8.1 m | Screenable | Two stacked homes, treated as a Duplex Dwelling. |
| Post-war bungalow | 6.4 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Rammed-earth timber infill | 10.1 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Side-by-side duplex | 9.0 m | Screenable | Two side-by-side homes. Calgary classifies this arrangement as semi-detached, rather than a stacked duplex. |
| SoHo cast-iron loft | 16.4 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Streamline Moderne corner | 23.3 m | Needs program review | Catalogue sources conflict between office and residential use. Choose and verify the occupied program before matching. |
| Terraced garden mid-rise | 16.3 m | Needs program review | Confirm whether the live-work frontage adds an Office or another commercial use. |
| Timber Art & Design School | 16.3 m | Needs program review | Confirm the education provider, student level and public gallery program before choosing the school use. |
| Timber Sanctuary Church | 17.5 m | Needs program review | Assembly area has not been recorded. Confirm the worship size class and how the spire is measured for height. |
| Timber community hall | 13.1 m | Needs program review | Confirm the operator and activity program before selecting Community Recreation Facility or Indoor Recreation Facility. |
| Timber-screen townhouse | 16.5 m | Needs program review | Confirm whether this exact model contains one dwelling or multiple attached dwellings, and their access arrangement. |
| Tuscan Arcade Villa | 11.8 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Vancouver balcony and podium tower | 58.8 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Victorian Grand Station | 32.6 m | Needs program review | Transportation infrastructure and accessory café uses require a dedicated site and operator review. |
