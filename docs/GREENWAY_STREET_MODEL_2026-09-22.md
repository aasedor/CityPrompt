# Neighbourhood greenway — offline street pilot

User request: add parks/open spaces and streets before combined Sol testing.
Worktree: `C:/dev/CityPrompt-greenway-street-model`, branch
`codex/greenway-street-model`. This is one bounded street-section pilot.

## Delivered concept and source limits

`student_greenway_segment_v1` is an 11 m wide, 48 m long straight inspection
fixture based on the metric `neighborhood_greenway_v0` catalogue section.
The three authoritative front/oblique/top references were inspected, copied and
hashed. The fixture supplies opposing bicycle sharrows, one speed table, two
1.6 m sidewalks, planting verges, four lights and a 3 m flush pedestrian crossing.
It has no centre line, parking lane or separated cycle lane.

The reference pictures contain traffic islands and a public junction. Those
need network-specific geometry and are explicitly outside this segment pilot;
this is **not** approval of the full existing reference variant. Existing saved
IDs and reference images are unchanged. The new trial ID must remain separate.

Section, left to right: 0.3 m setback + 1.6 m sidewalk + 1 m boulevard + two
2.6 m shared lanes + 1 m boulevard + 1.6 m sidewalk + 0.3 m setback = 11 m.
Carriageway datum is zero; sidewalks are 0.15 m higher. At the crossing they
ramp down over 2 m on both approaches. The speed table rises 0.075 m with 1 m
ramps and a 2 m top. These are concept dimensions, not an engineering approval.

Tree locations are declared for the existing `GlobeLandscapeTreeStand`, with
bounded crowns and clear stems. Trees are not baked into these preview GLBs;
their in-context appearance and traffic/pedestrian clearance need Sol review.
Do not substitute rounded proxy crowns or fork the shared tree generator.

## Evidence

External package:
`C:/dev-artifacts/CityPrompt/public-realm-pilots-2026-09-22/greenway-v001/`.
Assembly preview SHA-256:
`b00ff868c624bd8bf7575081f1edac93eb51bebc24911317a5503363c98637de`.
346,124 bytes; 2,766 triangles before shared trees.

All five reimported-GLB renders were inspected: aerial, top, pedestrian,
access close-up and speed-table close-up. Builder visual check passes for the
sectional concept. Independent visual review has not been performed.
Blender geometry verification passes exact section width/length, 315 crossing
ray samples, ramp continuity, table height/full width and lamp clearances.
An exact float32 band-edge ray initially missed. Verification now requires both
adjacent surfaces within 0.1 mm and agreement within 0.2 mm; one-sided or larger
gaps still fail. No model geometry was changed to conceal that test result.

## Sol integration before browser tests

This package is a model/section study, **not an installed executable street**.
Add an isolated exact-ID trial through the shared `streetSectionProfiles`,
`streetMesh3D`, route and furniture mechanisms. Rebuild the section along the
authored centreline; never repeat or bend the assembled preview GLB. Supply
crossing openings and ramps through network-owned geometry, and exclude furniture
near joins. A straight fixture cannot establish safe junction behaviour.

Test fixed width through straight/bent/reversed routes, slope measurements,
building/park approach connections, proposed public-road endpoints, move/edit,
Undo/Redo, reload, landscape exclusion and actual exact export on a disposable
vacant Currie layout. Trees must use shared metric profiles and must fit the
full street envelope. All runtime gates remain NOT TESTED in the copied review
template. No picker activation, database seeding or publication occurred.

Replay with Blender 5.2 using `--python-exit-code 1` and
`tools/greenway_street_model/build.py -- --output <fresh-external-directory>
--source-root <hydrated-checkout> --dry-run`, then remove `--dry-run`.
Run `tools/greenway_street_model/verify.py -- <candidate-directory>` afterwards.
No paid generation. GLBs/renders remain outside Git; browser work stays deferred.
