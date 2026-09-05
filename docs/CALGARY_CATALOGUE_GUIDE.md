# Calgary catalogue guide

Local implementation, 2026-09-05. Initiative: `codex/calgary-catalogue-guide`.

Students browse by the purpose of a place, then choose its appearance. Calgary
districts and design documents provide references for explaining a proposal;
they do not constrain the student's drawing or certify permission on a parcel.

## Student experience

- Buildings: detached homes; duplexes and semi-detached homes; rowhouses and
  townhomes; apartments; residential towers; mixed use; shops and services;
  offices; civic and recreation; industry; infrastructure; other ideas.
- Parks: small local parks; neighbourhood/community parks; regional/destination
  parks; green connections; natural areas; plazas; play/sport amenities; gardens;
  water spaces; parking and special sites. These are City Prompt browsing groups,
  not a reproduction of the City's formal park classification system.
- Streets: local, collector, arterial, alleys, active travel, transit, intersections,
  traffic calming, and other/global references.

The three existing property-panel pickers now offer these groups, search, an
optional appearance/category filter, and 12 cards per page with “Show more”.
Selecting a group does not change a model or clear its saved archetype. Selecting
an asset or variant still uses the existing identity and save path.

Search accepts spelling/punctuation variants such as `R-C1`, `RC1`, and
`single family`. District searches find **groups with district references**;
they are not a complete list of uses allowed in a district. For example, the
detached group refers to several housing districts, while rowhouse forms refer
to a different group. A building can be appropriate to more than one district.

The two pick/place pilot cards also expose a collapsed Calgary guide. The larger
catalogue remains in the existing property tools. No unreviewed models have been
promoted to immediate placement; browsing-reference availability and 3D readiness
remain separate.

## Source decisions

Reviewed official sources on September 5, 2026:

| Source | Status and use in this version |
| --- | --- |
| [Land Use Bylaw, Part 5](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=5) | Housing district references. Section 384 describes the R-C1 single-detached purpose. |
| [Citywide rezoning repeal](https://www.calgary.ca/planning/projects/rezoning.html) | The City's page says the April 8 repeal took effect August 4, 2026. Do not retain the older assumption that R-C1 is universally obsolete. Parcel exceptions still matter. |
| [Land Use Bylaw, Part 6](https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html?part=6) | Multi-residential district references, with different scales and forms. |
| [City district summaries](https://www.calgary.ca/planning/land-use/districts.html) | Commercial, mixed-use, industrial and special-purpose starting points. For example, S-SPR concerns reserve land; it is not a synonym for every park. |
| [Complete Streets](https://www.calgary.ca/planning/transportation/complete-streets.html) | Council-approved 2014 policy/guide; design context for the street groups. |
| [Street Manual project](https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html) | Current page anticipates administrative approval in Q2 2027. Existing Draft 4.0 catalogue sections stay draft references. This supersedes the earlier project summary's expectation of approval in early 2026. |
| [Connect: Calgary's Parks Plan](https://www.calgary.ca/planning/parks-rec/parks-plan.html) | Approved May 2025; use instead of treating the 2002 Open Space Plan as the latest policy. |
| [Parks Plan text](https://www.calgary.ca/content/dam/www/programs-services/city-planning/parks-projects-and-developments/parks-plan.pdf) | Sections 4.4–4.5 address park types and connections. Amenities and park service areas are distinct. Legacy “community park” assets remain discoverable without claiming that label is the new formal classification. |
| [Local area plan resources](https://www.calgary.ca/planning/local-area/resources.html) | Site-specific policy remains a separate review. No automatic LAP-to-parcel matching is claimed. |
| [City publication library](https://www.calgary.ca/planning/publications.html) | Lists landscape construction 2026 (effective March 23) and subdivision servicing 2020 as current. Linked for detailed design follow-up, not encoded as engineering constraints. |

## Implementation and limits

`frontend/src/features/calgaryCatalogue/guide.ts` owns the small reference
registry, review date, functional classification, and search aliases. The
classification is attached to runtime catalogue options in `aestheticCatalog.ts`,
outside all geometry, prompts and persistence presets. The source catalogue JSON,
image URLs, generation identity, floor ranges and asset availability are untouched.

Existing development-type metadata supplies the initial building groups. Explicit
exceptions separate known rowhouse/townhouse forms from legacy labels that put
them under duplex or single-family categories. This is a browsing crosswalk,
not a comprehensive legal interpretation of all 223 available building references.
Unusual concepts remain available and need individual review.
References attach to the parent archetype, not a legally assessed use for every
visual variant. Some families include both detached and duplex variants. A later
parcel analysis must inspect the selected variant and proposed use explicitly.

The park crosswalk distinguishes amenities from service-area concepts, and
separates legacy parking/transport entries from plazas. International references
retain their names and appearance; they are not presented as City-approved designs.
Only the existing `calgary_street_manual` group receives `draft_manual` provenance;
other street concepts are design references, with their existing citations retained.

No zoning overlay, parcel lookup, dimensional compliance check, automatic rezoning
recommendation, report generation, new model production or live provider generation
is added by this initiative. The guide prepares a citable foundation for those
future features without conflating them with choosing an object.

Before the January 2027 course, recheck the source registry, parcel district data,
and document status. For a later report, evaluate the student's actual geometry,
uses and site policy; do not turn these broad browsing tags into approval rules.

## Verification

Targeted tests cover catalogue-domain coverage, form exceptions, district searches,
parking/amenity distinctions, draft provenance, pagination, combined filters and
preservation of saved selections. Existing asset selection and placement tests,
TypeScript checking and changed-file lint are also required.

Browser trial evidence is kept under ignored `artifacts/calgary-catalogue/`.
This document and the source changes are the intended tracked deliverables.
No paid API tests or deployment are needed for catalogue organization.

Completed checks:

- 62 tests passed across the new guide/browser tests, existing catalogue and
  property-panel tests, and pick/place geometry and automatic-3D tests.
- `npm run type-check`, changed-file ESLint and `git diff --check` passed.
- The live chooser displayed two neighbourhood/community park choices and kept
  parking under special sites. The expanded guide showed the Parks Plan sources.
- `RC1` found detached references and excluded the explicitly mapped London
  townhouse. The original building workflow still asks for a development type
  before opening its full catalogue; Single Family was selected in the local QA
  project for this trial. No archetype variant was changed.
- Local streets plus a `Calgary` search displayed Calgary Local and Calgary Local
  Industrial, with draft status and the 2027 anticipated approval visible.
- Browser API snapshots before/after building and street filter trials matched:
  browsing did not change saved zone geometry or properties. No page errors were
  observed during those trials.
- Inspected the chooser at 1440 × 1050 and 390 × 844. The mobile chooser fits the
  viewport width and uses the existing vertically scrolling property sheet.
- Existing Google-tile loading/ground-alignment pauses remain; this initiative
  does not claim to resolve the broader globe performance issue.
