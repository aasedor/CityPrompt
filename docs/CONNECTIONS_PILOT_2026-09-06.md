# Neighbourhood connections pilot — 6 September 2026

## Result

The existing park-to-sidewalk connection works in a small authored scene and
recalculates after saved edits. Building approaches are independent paths: they
do not follow a moved house. The pilot establishes the next implementation work;
it does not introduce automatic building-door connections.

Local project: http://127.0.0.1:5178/projects/3df7bca4-d9a5-48d0-b04f-956c114d72db

## Method and scope

Created a reproducible seven-zone fixture through the local application API:
an open Fort Calgary field boundary, one Calgary local street with sidewalks,
one neighbourhood park, a post-war bungalow, an Edwardian Foursquare and two
manually authored house approaches. Inspected the scene in the browser. Saved
mutation trials used the API with revision checks and browser reloads; this was
not a complete novice UI placement/reshape trial.

The street is 74 m long and 16 m wide. The park is 40 by 35 m. Both houses face
the street. Their approaches are 1.8 m wide. Existing Google tile paths are
visual context, not authored network connections.

## Observations

| Trial | Result |
| --- | --- |
| Baseline park access | One 2.2 m-wide connection to the near-side sidewalk; external gap 3.2 m. Visible bridge mesh has 15 vertices. |
| Save park at 50 by 30 m, reload | Park access recalculates and the scene recompiles. |
| Save street 3 m farther away, reload | Connection follows the shifted sidewalk. |
| Save bungalow 5 m east, reload | Its approach stays at its old location. No building-to-path relationship exists. |
| Restore and reload | Baseline objects and connections restored. |
| Free direct capture | Completed at 1600 by 936; detected street, park and building classes. This checks source capture, not AI output fidelity. |

Additional pure solver scenarios, without saving each variant: moving the park
3 m retained a connection; moving it 9 m left it unresolved; rotating the park
180 degrees retained a connection; moving the street 12 m left it unresolved.
The solver did not invent a long connection across those larger gaps.

The houses and park are on opposite sides of the road. Their sidewalk links
alone do not form a complete walking route across it. No crossing was authored
or automatically invented during this pilot.

## Ground alignment finding

The original 90 m-wide site boundary caught the western tree edge. Sampling
failed its continuity checks and hid the objects. Trimming the unused edge to
80 m allowed sampling to complete with no reported grounding issues. This was
a fixture correction, not a terrain algorithm fix.

The measured park connector endpoint terrain heights were 1027.35124 m and
1027.35081 m. Ground continuity at this location is encouraging, but it does not
establish accessibility compliance, construction suitability, or performance
on a materially sloping site. Google tile detail changes during camera movement
also triggered resampling and temporary object disappearance.

## Recommended next implementation

1. Add explicit front-door anchors to catalogue assets and saved relationships
   between buildings, approaches and sidewalk targets. Recompute links after
   translation, rotation or reshape, with undo support.
2. Allow students to move and lock park entrances. Explain unresolved connections
   in a small connection check instead of silently leaving a gap.
3. Support deliberate crossings and curb transitions. Distinguish an entrance
   reaching a sidewalk from a complete route to the opposite side of a street.
4. Improve terrain failure feedback by highlighting suspect sample areas; trial
   continuous connections on sloping ground before making accessibility claims.
5. Verify close and occluded AI finishes after source connectivity is stable.

## Verification and deliverables

46 existing targeted tests passed across park access solving, bridge geometry,
street placement, shared ground provider/surface and ground capture. No
production TypeScript changed in this pilot.

Fixture scripts, saved mutation evidence, solver scenarios, geometry audit,
capture transcript and screenshots are outside Git at:
`C:/dev-artifacts/CityPrompt/connections-pilot-2026-09-06/`.

No paid AI images or video were generated. No catalogue assets were published.
The only source-tree deliverable for this initiative is this report.
