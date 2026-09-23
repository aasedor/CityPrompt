# Ten sports-court park candidates

User requested ten more native 3D sports parks in the style of the pickleball
garden, and explicitly deferred browser testing. Scope is offline asset creation,
native visual review and geometry checks; no picker, seed, provider call or push.

Branch: `codex/sports-court-batch-ten`, based on the shared tree-well checkpoint
`771b904da`. All heavy output is external:
`C:/dev-artifacts/CityPrompt/sports-ten-2026-09-23/`.

The bounded list is basketball, 3x3 basketball, tennis, padel, hardcourt volleyball,
beach volleyball, badminton, netball, bocce and two-lane petanque. Sources and
dimensions live in `tools/public_realm_assets/court_specs.py`. Each uses the
actual exported meadow furniture, vegetation and tree-well geometry, a fixed
native sport module, clear approaches, planted seating and a shaded terrace.

## Pilot checkpoint

Dry-run preceded one basketball pilot. The first native preview revealed
coplanar playing/underlay surfaces; it is preserved under `basketball-pilot/`
as rejected visual evidence. The corrected `basketball/` asset passed native
visual review, all generic geometry checks, full-width entry rays, two measured
3.05 m rims, full tree-envelope clearance and the new coplanar-floor regression.
The corrected underlay is 12 mm below the playing finish; walk checks accept
less than 25 mm finish differences, without claiming accessible construction.

Three pure-Python tests pass: unique finite IDs/native reserves, source-based
run-off dimensions, and sport-specific equipment with isolated recipe copies.
The nine remaining candidates will use the same builder after this checkpoint,
with a maximum of two concurrent Blender processes and no overwritten output.

All browser/runtime terrain, edit/Undo/reload, access and capture gates remain
NOT TESTED by user direction. Native GLBs and source recipes are for the next
integration trial, not automatic student catalogue activation.
