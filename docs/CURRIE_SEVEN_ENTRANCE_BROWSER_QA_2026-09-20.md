# Vacant Currie seven-house entrance continuation — 20 September 2026

The disposable full-layout project `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`
now has authored pedestrian entrances for all seven houses. After a fresh
browser reload, shared ground reached `ready` with two stable passes and valid
quality; all seven models were visible and the building-ground issue list was
empty. All seven plan routes resolved as `connected` to the same six-metre
shared street. Browser page errors were empty. This is a geometry and runtime
pilot, **not** student-ready acceptance or a construction/accessibility review.

| House | Copy adjustment | Native-step anchor (plot m) | Connected route |
| --- | --- | --- | ---: |
| West 2, Craftsman | 2.4 m west | (0.9, -10.35), 1.8 m wide | 5.32 m |
| West 3, Craftsman | 0.6 m west | (0.9, -10.35), 1.8 m wide | 3.40 m |
| West 4, Edwardian | none | (0, -8.965), 1.65 m wide | 4.18 m |
| East 1, modern infill | none | (2.88, -5.875), 2.12 m wide | 3.61 m |
| East 2, modern infill | none | (2.88, -5.875), 2.12 m wide | 3.27 m |
| East 3, modern infill | none | (2.88, -5.875), 2.12 m wide | 3.27 m |
| East 4, modern infill | none | (2.88, -5.875), 2.12 m wide | 3.27 m |

West 3 first reported `entrance_approach_too_short` at the original plot
position. A bounded 0.6 m west trial within the existing site boundary
cleared that warning. Read-only geometry checks found a 4.561 m minimum
boundary margin, 1.60 m to the street zone, 2.983 m to the nearest neighbour,
and zero positive-area overlaps. West 4 connected at its original placement.
The bottom native foundation step measured 1.65 m wide, and the approach
shared its world-space centre within measurement precision.

Each east house uses the same `infill_flat_roof_minimal` assembly with the
same native foundation mesh signature and -90-degree plot rotation. The
bottom two-tread step is 2.12 m wide, centred at model-local (2.88, 0, 5.9),
which measured as plot offset (2.88, -5.875) in each house. East 1 was authored
through the Connections dialog, then its route and native step were reviewed
in 3D. East 2–4 were saved one at a time in the disposable copy; a browser
reload and ready-ground check followed each save. The approach meshes
intersect the native step at the intended horizontal position. For east 2
and 4, the centre falls between two vertices on the vertical face of the
approach riser rather than exactly on a vertex; those vertices bracket the
native step height. The observed geometry therefore does not imply a gap.

The Edwardian pilot exposed a form defect: the valid 1.65 m native-step width
could not be saved because the number input's 0.1 m step made it invalid.
`Walkway width (m)` now permits any value within its existing 1.2–4 m limits.
A focused test checks that 1.65 m submits, and the live editor successfully
saved the Edwardian anchor after the fix. The control should surface validation
more clearly in a later usability pass.

The original read-only Currie project `f5bffc94-def9-4c43-942e-9ae7411872e9`
was not edited. Its ten zone coordinate arrays still match the earlier saved
snapshot. The layout was API-authored from reviewed assets, so these results
do not establish that a novice can create it unaided. The high exposed
Craftsman foundation and long concept stairs remain visually unresolved;
landings, guards, accessible routes, street-tree and furniture clearance,
and applicable site requirements have not been validated. Keep the original
fixture and catalogue unchanged while treating these as release work.

Screenshots, measured-step scripts, per-house trial records, and route checks
are external to Git in `C:/dev-artifacts/CityPrompt/grounding-batch-a/`,
including `currie-seven-entrances-top.png`,
`currie-west4-edwardian-entrance-northeast.png`,
`currie-east1-connected-northwest.png`, and
`currie-east4-entrance-northwest.png`. No paid AI generation or push occurred.
Focused Vitest passed 22 tests across the Connections editor and pedestrian
route files. Frontend TypeScript type-check and changed-file ESLint passed.

The next bounded product slice is to make a student choose a model entrance
directly in 3D, show an immediate saved/invalid route result, and guide a
recovery when the plot lacks enough street setback. Pilot that on the vacant
Currie copy before scaling it to other building families. A separate design
review must decide how to handle the high-foundation stairs and street-side
furniture before this layout can be presented as student ready.
