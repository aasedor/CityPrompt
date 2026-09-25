# Native street junction runtime pilot

Date: 2026-09-23. Branch: `codex/native-street-intersections`. The baseline
[ten-street Currie trial](TEN_STREET_CURRIE_INTERSECTION_TRIAL_2026-09-23.md)
found five pairs of full native sections simply overlapping. This follow-up
adds one owned junction for each compatible crossing in that same saved project.

## Reusable contract

Every development-review native street registers a fixed `[width, length]`
metre envelope, ordered `surfaceRegions`, and `junctionSurface` (`pavers`,
`brick`, `cobble`, or `timber`). Local X is section width; local Y is the route.
The street builder records `junction_surface` from its authored `pattern`;
the hydrator also recognizes the historical batch's pattern and rejects an
unknown finish. The registry test crosses **every** registered
native street against another street, so a newly registered candidate cannot
silently omit the shared junction path.

The existing street graph detects the node. The native adapter accepts two
perpendicular four-arm fixed sections that fit the prepared site and share one
datum. Both source grounds, painted detail and paving units are clipped to
the same two-metre junction lead-in; rigid model islands in that envelope are
cleared. A single node mesh rebuilds the authored asphalt, cycle, pedestrian,
planting and paving bands. Circulation wins over planting in the crossing;
distinctive timber, cobble and brick finishes carry through the node. Existing
street detail away from the crossing stays native. Move, rotate and reload
recompute the node from saved zone geometry without a Currie-specific offset.

Direct 3D capture labels the node with its two persisted source IDs. The
server independently proves the four-arm crossing for registered native trial
assets in development only; unknown assets and production trial claims
remain rejected. Publication still needs a normal compiled street recipe and
server-backed capability, not this development-only registry.

## Currie visual and technical result

The saved vacant Currie project has ten roads in five isolated crossing pairs.
After browser reload, all ten native models were ready and the live scene had
five junction nodes. Oblique reviews covered Main Street/Cycle Avenue,
Transit/Market, School/Grand Promenade, Planted Lane/Heritage Mews, and
Boardwalk/Green Alley. The first three retain distinct travel bands; the two
all-paved pairs now have cobble and continuous timber finishes rather than a
blank grey square. Junction trees and furniture are cleared in the node
footprint. Browser console errors/warnings: none. A free exact Direct 3D
capture succeeded with all five junction identities in its instance manifest;
visible junctions had nonzero class pixels. No further paid image calls were
made after the baseline five-render trial.

Automated checks: 43 focused frontend tests passed, including every native
street asset, clipping, prop clearance, and previous procedural junction
regressions; frontend TypeScript check passed. Three focused backend tests
passed for local registration, unknown-asset rejection and production denial.

## Scope still open

This is a concept-grade four-arm solution for two rigid native sections on a
level prepared site. T junctions, skew, bends, mismatched elevations,
native/procedural pairs, public-road endpoints, comprehensive curb ramps,
marking continuation and student-authored placement remain separate tests and
capabilities. The ten streets are still development-only review assets, not
student-picker entries. This browser pass does not approve exact export,
photorealistic fidelity or student publication for any variant.

When promoting a native street family, carry this section/finish metadata into
the compiled recipe, use the same graph-owned clipping and junction ground,
and complete S1–S4 of the
[runtime checklist](ARCHETYPE_RUNTIME_INTEGRATION.md) for each exact variant.
Review a vehicular and a pedestrian crossing before scaling a new batch.

## Follow-up: connected network verification

See [STREET_JUNCTION_NETWORK_FOLLOWUP_2026-09-23.md](STREET_JUNCTION_NETWORK_FOLLOWUP_2026-09-23.md).
The native rectangle now uses its physical length as the graph axis and joins
orthogonal three-arm T nodes as well as X nodes. The earlier “T junctions” item
above records the scope at the time of this pilot; the follow-up supersedes it.
