# Currie Garden Walk — simulated student exercise

The user has no students until winter term and requested a simulated student.
This is a provisional **working-prototype pass**, with the retries below retained.
It supports continued bounded development without waiting for winter. It is not
independent novice usability evidence, asset approval or a deployed class service.

## Exercise and result

Started with an empty project using New Project and the visible CFB Currie address
search. All design changes used ordinary UI controls and native pointer/keyboard
events. API reads verified persistence afterward; no geometry was inserted by API,
database, store mutation or developer coordinates. Existing projects were untouched.

- Project: `1e37fb9f-c9f2-4a9a-b5e0-9d7089ddbc66`
- Name: **Currie Garden Walk — simulated student exercise**
- Worktree: `C:/dev/CityPrompt-grounding-edit-race`
- Branch: `codex/simulated-student-exercise`
- Isolated QA services: `127.0.0.1:5175` and `127.0.0.1:8001`
- Evidence: `C:/dev-artifacts/CityPrompt/simulated-student-2026-09-22/`

The 12-point, approximately 2.2 ha site occupies a portion of the vacant Currie
field between the curving west road and straight east road. It contains six
two-storey Infill homes (Flat Roof Minimal), a bent 16 m Calgary local street and
a 42 × 50 m Teaching demonstration garden (Demonstration-Plot Garden).

Homes on both sides turn toward the street and receive automatic entrance paths.
The garden was repositioned and turned to connect its internal path to the
sidewalk. Its full programme remains: shelter, 12 beds, 12 labels, two benches
and 18 perimeter trees. The street's public-road connection was enabled and its
endpoint extended to the visible eastern roadway edge. This is visual concept
alignment, not surveyed junction/vehicle-turning acceptance.

Neighbourhood gardens filled the remaining space without paid generation. The
site uses the automatically established prepared level, approximately 1101.687 m
WGS84 ellipsoid. Review ground closed measured edge gaps without changing that
level. Existing ground varies substantially, so retaining faces remain visible.

| Check | Result |
| --- | --- |
| New project and irregular site drawn through UI | Pass |
| Six buildings, street and complete garden placed | Pass, with retries below |
| Homes face opposite street sides; added approaches visible | Pass; all six appear in Review entrances |
| Garden reaches sidewalk after move/rotation | Pass through ordinary controls; manual entrance dialog inspected and cancelled |
| Building Move, Undo, Redo | Pass; full design data restored, excluding updated/compiled timestamps only |
| Free landscape and measured edge closure | Pass |
| Reload | All nine zones byte-for-byte identical in API JSON before/after; scene visible |
| Exact free export and Download render | Two PNGs downloaded through visible links; bytes match previews |
| Browser errors / paid credits | No uncaught browser errors; balance stayed 4,057; zero paid calls |

The closer final PNG is 1440 × 936, 2,506,789 bytes. Its native download completed
in approximately 0.4 seconds after clicking the ready preview link; this is
**download time only**, not total loading/export time. The wider contextual PNG
is also retained. `verification.json` records hashes and persistence comparisons.

## Friction, recovery and changes

1. **Landscape prerequisite was unclear.** New boundaries follow terrain, but
   landscape presets need a cleared, level site. The Guide and disabled-panel
   explanation now name **Site ground → Clear site for redevelopment → Save
   changes**, and explain the level-surface consequence. The exercise includes it.
2. **Quick road edit met a save guard.** Dragging an endpoint immediately after
   enabling public-road connection produced “Wait for this edit to save.” Waiting
   and retrying worked. The handout now explicitly includes that save wait.
3. **Close home placement needed a retry.** An east-side preview near the sidewalk
   was rejected as lacking room. Moving farther away placed it and automatically
   connected its entrance; a later Move brought the southern house closer. Do
   not treat this run as proof that every preview/drop or snapping case agrees.
4. **Garden rotation overlapped a home.** The rejected move/rotation retained the
   design. Moving the garden into clear space, rotating it, then moving it toward
   the sidewalk worked and created a visible connection. This still takes more
   thought than ideal; broader park snapping remains a bounded follow-up.
5. **Edge measurements needed time.** Close gaps at site edges began disabled,
   then enabled once measurements were ready. It applied successfully without
   entering a developer-selected elevation.

No geometry solver or catalogue asset changed in this turn. Source edits only
clarify the landscape prerequisite. Existing guide and landscape tests: **8 passed
in 2 files**; TypeScript type-check, focused component ESLint and diff checks pass.
The updated guide wording was checked in the live project. React review found no
new state, effects, listeners or data-fetching behavior in these text edits.

## Simulated student's submission

“I followed the curved field edge and kept the existing roads outside my site,
with two-storey homes facing a small internal street. Each home has a route to
the sidewalk, and the shared teaching garden connects near the street bend.
Turning and moving the garden gave it a clearer entrance, and bringing the last
home closer shortened its walk to the sidewalk.”

## Decision and next steps

Continue with a small catalogue batch using the shared per-variant runtime
checklist. Prioritize a complementary housing type and useful public-space/street
choices, based on instructor goals and the existing catalogue audit; do not create
duplicate entries simply to increase the count. Carry placement retry and park
rotation checks into each pilot. Asset visual approval/publication rules remain.

Actual student feedback remains scheduled for winter, not a blocker to prototype
development now. Remaining limits include visible retaining edges, schematic
planting and sparse density, unassessed accessibility/vehicle turning, and the
previously documented natural-ground limitations. This run used free exact
capture and did not revalidate paid AI image fidelity. There was no push.
