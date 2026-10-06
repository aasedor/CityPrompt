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

Expected current park counts: S-SPR 30 permitted, two outside this screen; S-R 26 permitted, five discretionary and one requiring its associated food-service site review; R-CG 26 permitted and six outside. S-UN has no confirmed candidates from these ornamental/recreational teaching programs. S-SPR, S-R and S-UN open on Parks by default; other districts start on Buildings, with Parks one click away. The choice stays selected when rezoning the active study zone.

## Evidence and scope

- Snapshot date: October 5, 2026. The 68 district choices have source links, relevant permitted/discretionary use entries, section references and preliminary height rules in `frontend/src/features/zoningCatalogue/districtRules.json`. This is a subset of uses relevant to the catalogue, not a reproduction of the complete bylaw.
- Primary source: [City of Calgary online Land Use Bylaw 1P2007](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html). District sources are attached to every rule record. Sources were retrieved during this implementation; do not replace them with recollected historical limits.
- [R-CG ss.526–527 and 541](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5&div=11): the retrieved consolidation sets a 10 m general maximum, with additional height-plane/rear/corner conditions. Contextual houses and rowhouses do not automatically qualify for a permitted route from their appearance alone.
- [R-G/R-Gm s.547.3](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5&div=12): Single Detached Dwelling is permitted in R-G but discretionary in R-Gm. The two district records must remain independent.
- [MU-1 ss.1366–1367](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=14&div=2): permissions conditional on an existing approved building are not carried onto a new catalogue building. Explicit new-building discretionary routes are retained. MU-2 has the equivalent distinction in ss.1376–1377.
- Full `f`, `h` and `d` designation text is preserved. Height-dependent districts with no applicable `h` value remain unconfirmed. FAR and density are not evaluated. Unrecognised designations never inherit an inferred district.
- The current catalogue contains **34 exact placeable building variants**. `buildingPrograms.json` binds each teaching program to its exact model revision. Thirty-three have stated programs usable for preliminary screening. The passenger station has a known program but needs a dedicated site/authority review; no ordinary district route is claimed. Changed revisions fail safely pending classification review. Historical catalogue families are not made available by this feature.
- Program evidence: exact asset descriptions and revisions in `validationCatalogue.json` and `classroomExpansion.json`, plus the matching variant descriptions in `buildingArchetypes.json`. The earlier September 2 crosswalk is context only; see `CALGARY_RESEARCH_RECONCILIATION_2026_09_05.md`. No building geometry, catalogue eligibility or published assets changed.

Model dimensions are measured envelopes from the runtime registry. They are not substituted for Calgary's grade-based height method. Spires, roof exemptions, height planes, parcel size, setbacks, coverage, density, floor area, parking, access, use-specific limits and location overlays require further review. Centre City/no-maximum entries do not waive those rules. Special-purpose or mapped height areas without a verified numeric comparison remain review-only.

## Verification

69 focused Vitest tests passed across building/park matching, panel behaviour, geometry picking, existing zoning and study editing; TypeScript and the production Vite build passed (the existing large-chunk warning remains). The React best-practices checklist was applied to the touched components. Browser verification used the Hillhurst trial project on localhost:5174:

- Native canvas clicks selected an existing M-CGd72 polygon and a proposed R-CG polygon.
- R-CG showed four discretionary candidates; changing the proposal to R-G originally showed eight permitted candidates (ten after the program review below). Undo restored R-CG without saving changes to the project.
- Tested full C-COR2f2.8h16 designation, DC fallback, custom zone explanation, legend buttons, Escape/focus, layer hiding, zero opacity, reopening opacity, site-boundary review and 768×1024 layout.
- No uncaught browser errors. Some pre-existing catalogue preview files are missing locally; cards show a neutral building placeholder when an image fails.
- Park extension: existing S-R showed 26 permitted and five discretionary park candidates; switching R-CG between Parks and Buildings preserved their distinct counts. The proposed S-SPR drawing-studio panel showed 30 permitted parks, changed to five discretionary candidates when rezoned to S-R, and Undo restored S-SPR without saving project changes. A native canvas click on the proposed S-SPR polygon opened the Parks panel (existing study hidden for unambiguous selection); its 768×1024 bounds, no horizontal overflow and Escape dismissal passed. Visibility preferences were restored. No uncaught browser errors. Park cards use a tree placeholder when an existing thumbnail is unavailable.
- Source/data changes are under this document and `frontend/src/`. Research HTML, test screenshots and the build log stay outside Git at `C:/dev-artifacts/CityPrompt/zoning-catalogue-2026-10-05/`. The build used the existing external build helper and output directory under `C:/dev-artifacts/CityPrompt/local-area-plans-browser-followup-2026-10-05/build/`.

## Maintenance

Recheck the linked bylaw when the City changes its consolidation. Review conditional clauses, cross-references and inherited/general district rules before promoting updated facts. Never automatically promote scraped text into approved matches. R-CG contextual permitted routes, worship size classes and historic/existing-building conditions need facts beyond a model label. To resolve the program queue below, record the missing occupancy/arrangement facts for the exact variant, update its components and assumption, and remove its review hold only after that evidence is available.

The matcher reuses the current canonical catalogue and compares locally on selection; it makes no per-click network or AI requests. Map inspection reuses already-rendered triangles, preserves holes and keeps native raycasting disabled for drawing and terrain sampling. Hidden/transparent layers and editing/navigation modes do not intercept map clicks. Student zones take precedence over City zoning when both overlap; policy map inspection remains separately prioritised. Selection is resolved against live records and cleared on hiding, deletion, editing or project change.

## Exact-model program review

The table below lists the intended teaching program, not the established occupancy of a real-world property. “Screenable” still requires an applicable district use route and height comparison.

| Catalogue building | Model height | Program status | Program / remaining site dependency |
|---|---:|---|---|
| Beltline mixed-use mid-rise | 20.4 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Blue glass office tower | 99.0 m | Screenable | Office tower, including its entrance lobby; no residential use assumed. |
| Brick courtyard entrance building | 12.3 m | Screenable | Classroom program: eight apartments on the two upper occupied floors, reached by shared stairs. The courtyard is a separate site element. |
| Buff-brick infill | 10.7 m | Screenable | Classroom program: one detached home occupying the complete buff-brick building, without a secondary suite. |
| Calgary Modern Infill | 7.0 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Charcoal Gable Fourplex | 9.6 m | Screenable | Classroom program: four side-by-side, unstacked homes with individual entrances and shared party walls. |
| Corner Café & Apartments | 20.6 m | Screenable | Apartments over an unlicensed café. A licensed restaurant would need its own use check. |
| Crystal brewhouse | 14.6 m | Screenable | Classroom program: brewery production with a small public tasting area included in the brewery use. |
| Earth-sheltered museum | 8.8 m | Screenable | Museum exhibition and visitor spaces. |
| Edwardian Foursquare | 10.8 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Gilded Terracotta Tower | 68.6 m | Screenable | Classroom program: offices above a retail base. |
| Gothic Community Church | 44.0 m | Screenable | Place of Worship – Large: the authored assembly hall exceeds 500 m². |
| Grand Deco Cinema | 21.4 m | Screenable | Cinema/movie theatre, with associated lobby spaces. |
| Grand Iron & Glass Market | 19.1 m | Screenable | Classroom program: a multi-vendor market selling goods and food products, with shared customer seating. |
| Halifax clapboard house | 10.5 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Living-Roof Aquatic Centre | 16.6 m | Screenable | Indoor swimming facility. A community-operated facility may follow a different use definition. |
| Machiya cafe and gallery | 8.4 m | Screenable | Classroom program: an unlicensed café and a commercial art gallery selling artwork. |
| Mass-timber Library | 15.5 m | Screenable | Library reading, collection and associated spaces. |
| Mediterranean Courtyard Hotel | 13.6 m | Screenable | Hotel guest accommodation with associated reception and pool. |
| Nordic Roof-Garden Apartments | 22.8 m | Screenable | Residential apartments; no shops or offices assumed. |
| Plateau stacked duplex | 8.1 m | Screenable | Two stacked homes, treated as a Duplex Dwelling. |
| Post-war bungalow | 6.4 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Rammed-earth timber infill | 10.1 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Side-by-side duplex | 9.0 m | Screenable | Two side-by-side homes. Calgary classifies this arrangement as semi-detached, rather than a stacked duplex. |
| SoHo cast-iron loft | 16.4 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Streamline Moderne corner | 23.3 m | Screenable | Classroom program: apartments above street-level shops. |
| Terraced garden mid-rise | 16.3 m | Screenable | Classroom program: apartments above ground-floor shops. Both residential and retail uses must be allowed. |
| Timber Art & Design School | 16.3 m | Screenable | Classroom program: a post-secondary art and design school with teaching studios and a student exhibition gallery. |
| Timber Sanctuary Church | 17.5 m | Screenable | Place of Worship – Large: the authored assembly hall exceeds 500 m². |
| Timber community hall | 13.1 m | Screenable | Classroom program: a neighbourhood community association hall for social and recreational activities. |
| Timber-screen townhouse | 16.5 m | Screenable | Classroom program: one detached home occupying the complete timber-screen building, without a secondary suite. |
| Tuscan Arcade Villa | 11.8 m | Screenable | One detached home, with no secondary suite assumed. Contextual permitted routes require a separate site assessment. |
| Vancouver balcony and podium tower | 58.8 m | Screenable | Teaching program: apartments above or alongside retail. Both residential and retail uses must be listed; changing the shop program changes the result. |
| Victorian Grand Station | 32.6 m | Site review required | Passenger rail station: platforms, ticketing, passenger circulation and a café. |

## Program backlog review — October 5

Reviewed the 15 flagged buildings and one café park against exact variant records,
their current model recipes, and the linked bylaw definitions. Fourteen building
programs now proceed through normal use/height screening. Two entries have a known
program with a specific unresolved site dependency: the passenger station and the
café court. These remain unconfirmed; clearing a catalogue description does not
clear a site's approvals.

`classification` distinguishes model evidence from a declared classroom program.
`conditions` states the limits of that program on the card. `siteReview` blocks a
permitted/discretionary result even when ordinary use components are listed.
`review` remains reserved for unresolved catalogue classifications. A changed model
revision does not inherit the old program or display its old evidence.

| Reviewed item | Decision and evidence |
|---|---|
| Brick courtyard entrance building | Eight-apartment teaching layout: four furnished bays on each of two upper floors and two shared stairs in `tools/catalogue_courtyard_pilot/build.py`. Individual access to grade remains a separate district check. |
| Terraced garden mid-rise | Apartments plus retail: terrace-v006's `scripts/terrace.py` names ground-floor shopfronts and residential living/terrace openings above. |
| Gilded Terracotta Tower | Office plus retail: the exact tower-v005 recipe in `tools/showcase_building_trio/tower.py` names office partitions and retail base details; the family-level residential description is superseded for this revision. |
| Streamline Moderne corner | Residential upper floors plus shops is the explicit teaching occupancy. Streamline-v003's recipe confirms street shops and upper occupied lounges. |
| Both churches | Place of Worship – Large. `tools/large_civic_pilot/build_timber.py` supplies a 24 × 38 m hall; `build_church.py` supplies a 25 × 41 m nave with connected side aisles. A conservative 22 × 30 m portion of each connected hall is 660 m² before small column deductions, above 500 m². These are conceptual model dimensions, not surveyed properties. Complete model height, including spires, remains the conservative screen. |
| Charcoal Gable Fourplex | Four unstacked, side-by-side homes with separate stoops and shared walls, from `tools/fourplex_pilot/build_fourplex.py`. Rowhouse placement must face a public street and meet the direct-entry/party-wall definition; Townhouse is not offered as an interchangeable label. |
| Buff-brick infill and Timber-screen townhouse | One complete detached home each is the declared classroom occupancy. Exact brick-v002/timber-v002 recipes provide whole envelopes and entrances but do not verify several dwellings. Names/door counts alone do not establish a legal townhouse or duplex. Native model heights are preserved, so the 16.5 m timber model remains outside R-G's height screen. |
| Crystal brewhouse | Brewery with a small tasting program. Brewhouse-v003 contains process vessels and six tasting tables. Public consumption is explicitly limited to 150 m² and entertainment to 10 m² as an operating assumption; this is not a claim that the entire visitor wing has been measured at 150 m². A larger taproom requires another use check. |
| Machiya café/gallery | Unlicensed food-service café plus a commercial gallery selling art. This is a declared retail operation, not a museum or production studio inferred from style. |
| Timber community hall | Community Recreation Facility, assuming a non-profit neighbourhood association with voluntary membership. Another operator requires reclassification. |
| Grand Iron & Glass Market | Retail and Consumer Service for a multi-vendor goods/food-products market with shared seating. The exact market-v006 recipe supplies stocked stalls, displays and tables. Independent restaurants or licensed vendors need separate checks. |
| Timber Art & Design School | Post-secondary Learning Institution, assuming a higher-education operator; student exhibition space is ancillary. `tools/interior_building_pair/` and the University Academic Complex record support this scenario. |
| Victorian Grand Station | Known passenger rail program, but no ordinary new-building district route verified. Operator, authority, site and café review remain necessary. No Utilities/Office/Retail substitution is used to invent a station permission. |
| Terraced Café & Fountain Court | Park + outdoor café + an associated restaurant supplied separately. `tools/public_realm_assets/build_showcase_parks.py` contains café furniture but no restaurant building or food-preparation facility. The principal food-service dependency remains blocking. |

Definition sources: [worship size classes and post-secondary education](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=P),
[brewery s.156.1](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=B),
[community recreation s.169](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=C),
[retail/restaurant/rowhouse definitions](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=R),
and [Outdoor Café s.247](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=4&div=2&alpha=O).

Three missed community-hall entries were added: S-SPR s.1027(1), CC-MHX s.1134(3)
and CR20-C20/R20 s.1307(3). The source display text says “Community Recreational
Facility” but each links to use definition 169, Community Recreation Facility.
The canonical name is used; categories, source sections and height handling are
unchanged. The S-SPR hall still needs a height assessment.

Nineteen previously classified buildings and 31 previously classified parks are
unchanged. All 66 exact revision bindings remain unchanged. The new program
metadata does not confer visual approval, runtime release approval or geometric
compliance. Pre-edit program backups, source inventory, cached official pages and
QA output are external at `C:/dev-artifacts/CityPrompt/zoning-program-review-2026-10-05/`.

Browser follow-up passed in the Hillhurst project on localhost:5174: a native City
polygon click opened M-CGd72 with nine discretionary candidates including the
newly classified buff-brick home. A proposed R-CG zone changed to R-G and showed
ten permitted models; the fourplex frontage condition, teaching basis disclosure
and definition link were visible. Changing it to CC-X showed 29 discretionary
buildings, including the office/retail tower; the Large church stayed outside the
screen and the station stayed in review. Switching to Parks kept the café court
in review with its missing restaurant dependency. The 768 × 1024 editor remained
within the viewport with no horizontal overflow. Undo restored the original R-CG
zone and disabled Save; no project edits were saved, layer visibility was restored,
and the browser reported no uncaught errors. Five review screenshots remain in the
external QA directory, separate from the committed source and documentation.
