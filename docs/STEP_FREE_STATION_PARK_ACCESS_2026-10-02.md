# Step-free station and park access — local runtime extension

The two station-capable elevated rail variants now show a glass lift tower at
each side platform. The lift connects the prepared ground-level concourse to a
short guarded bridge at platform height. In Walk, stand inside the lift landing
and use **Take lift to platform** or **Take lift to street**. The original stairs
remain available. A station with no placed stop has no lifts.

Four stair-based parks now have a distinct lift and guarded bridge to their
main elevated or recessed destination:

| Park | Step-free destination | Level change |
| --- | --- | ---: |
| Quarry Garden | Lower garden court | 4.5 m down |
| Cascade Water Garden | Upper garden | 4.5 m up |
| Treetop Walk Park | Canopy circuit | 4.2 m up |
| Terraced Rose Garden | Upper pergola garden | 2.4 m up |

Spiral Lookout Park already has a continuous graded promenade from its entrance
to the summit; its original walk geometry remains unchanged. The new bridges
use the same visible geometry and Walk height data. Movement chooses the closest
surface at overlapping levels, so passing below a bridge does not move the
camera onto it. Navigation excludes bridge supports and low-clearance areas;
the user can turn or retreat from their edges.

This is a runtime extension of the existing exact native park and station
assets. Source GLBs, hashes, saved selections and the original stair routes
are unchanged. Existing projects gain the access features without replacing
their saved models. The station lifts appear only with deliberately placed
stations, and park lifts only when their verified native assemblies are ready.

## Review and limits

Seventy-five focused Vitest checks and TypeScript pass. On the saved 15-zone east
Calgary trial site, all four park structures, four station lift towers, five
park models and three rail corridors mounted without a failed asset or browser
error. Live keyboard Walk completed a Civic Flow street → lift → platform →
street loop and all four lift-served park destinations in both directions,
including a return from Quarry Garden's lower court. Screenshots and results are in
`C:/dev-artifacts/CityPrompt/step-free-access-2026-10-02`.

This provides step-free routes to the named main destinations. Intermediate
Quarry, Cascade and Rose terraces still use their original stairs. External
public-street connections, natural terrain and construction-level accessibility
requirements have not been assessed. The lift is an instant level transition
in Walk, rather than a timed cabin animation. This is a concept review, not a
certification or a claim of full-site accessibility.
