# Parking drawn on the site — 30 October 2026

User request: draw a parking outline like Ground surface, then compute stalls
and drive lanes automatically. Keep the student interaction simple.

The Streets picker starts the existing 3D polygon drawing controls instead of
opening the separate details plan editor. New parking uses a versioned asphalt
ground-zone recipe, so selection, corner dragging, movement, Undo/Redo, saving,
reload and capture use the established ground-surface workflow. Older parking
and plaza zones and metadata-authored paving remain unchanged.

Use the existing bounded parking engine: 2.7 × 5.5 m stalls, 6 m drive lanes,
0.5 m margin. Choose between two perpendicular row directions and three bounded
boundary alignments along a stable longest edge. Single rows are opt-in for this
new recipe; older saved lots retain their paired-row layout. The panel shows capacity,
an optional row-direction override and Delete. Recompute after an outline edit;
never stretch stalls. A small lot can remain asphalt with zero stalls and a
plain explanation. Road access is drawn separately.

Paint is part of the asphalt texture and shares its exact mesh and metric UVs.
This avoids separate marking triangles floating above or passing under terrain
crests, and keeps live terrain refinement coherent. Grain retains its 2 m repeat.
Per-axis texture resolution scales with lot dimensions, capped at 2048 pixels;
concept paint has a one-pixel minimum at the largest supported plots.

No GLBs, catalogue entries, paid generation, dependencies or publication gates
change. This is a concept layout, without accessible-bay design, vehicles,
landscape islands, engineering grading or automatic public-road access.

Implementation and verification sequence:

1. Exercise automatic orientation, real dimensions, reordered/rotated/concave
   outlines, invalid bounds and capture-revision changes with focused tests.
2. Wire drawing, selection and settings to existing site zones; conform paint
   to the same measured ground mesh. Bind the parking recipe to capture claims
   in both browser and backend, retaining plain-surface hash compatibility.
3. Test ordinary browser drawing, edit/recalculation, save/reload, Undo/Redo,
   deletion and exact source capture in a disposable QA project. Record actual
   results and remaining terrain/input limitations; preserve the user's project.
4. Run relevant tests, TypeScript, lint and current build budgets. Review and
   push one coherent unit to the existing draft handoff PR; do not deploy live.

## Verification and runtime review

Local disposable project: `ca2f429a-23af-4ffa-b2b1-d53a73a709d1` on QA5177.
Original user projects and the original 5174 service are preserved.

| Gate | Status and evidence |
| --- | --- |
| C1 Identity / saved recipe | PASS: ordinary picker drawing and reopened saved lot; no archetype compilation required. |
| C2 Metric dimensions | PASS: fixed stall/lane tests, rotated and concave polygons, single rows, bounded input and legacy layout regressions. |
| C3 Ground | PASS for the prepared level browser site; paint shares the asphalt mesh. Natural/sloping-site browser trials NOT TESTED. |
| C4 Freshness | PASS: real corner drag recalculated 56 to 40 stalls. FE/BE golden capture hash changes with parking/row direction while old plain-surface hashes remain compatible. |
| C5 Road connection | N/A: separate drawn road access, explicitly described in the panel; no automatic public-road entrance advertised. |
| C6 Editing / recovery | PASS: browser resize, Undo to 56 and Redo to 40. Hook regressions retain failed drafts and prevent delayed saves cancelling a newer outline. Browser delete/reload follow-up recorded in delivery note. |
| C7 Interrupted saves | PASS for focused hook tests; network interruption not forced in the browser. Selection follows the exact optimistic request, never just the tool name. |
| C8 Visibility / capture | Browser rows and asphalt inspected overhead. Exact export and additional low/sloped views recorded separately when exercised. No paid AI comparison in this task. |
| C9 Student controls | PASS: ordinary desktop pointer drawing, Enter completion, direct capacity panel and corner handles. Touch NOT TESTED. |

83 focused frontend tests passed; 46 relevant backend capture/scene checks
passed. TypeScript, scoped ESLint, Ruff and pinned Black 24.10.0 pass. The
Maps-enabled Node 20 code build passes the unchanged performance budgets;
it deliberately omits copying heavyweight public assets. The prior exact-byte
asset packet remains separate and must be re-prepared before deployment.
Independent review found and verified fixes for paint/terrain contact and a
late-save selection race; no remaining concrete code findings.

Evidence: `C:/dev-artifacts/CityPrompt/overnight-hardening-20261030/parking-ground-drawing-20261030/`.
Screenshots are browser UI evidence, not AI image originals. This change does
not activate the unfinished catalogue pilots or update live services.
