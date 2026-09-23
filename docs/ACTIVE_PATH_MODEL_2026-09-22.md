# Separated walking/cycling path — offline model batch

User asked for more archetypes before the combined browser session. This original
concept is `student_separated_active_path_v1`, built in
`C:/dev/CityPrompt-greenway-street-model` on `codex/active-travel-model-batch`.
It follows the shared greenway prototype and does not overwrite an existing card.

The fixed 8 m section comprises a 2.5 m pedestrian path, 0.5 m planted divider,
3 m two-way cycle track and 2 m furniture verge. A 36 m straight inspection
fixture includes a flush 3 m crossing through the divider, direction arrows,
centre dashes, two benches, two cycle stands and two lights. No motor-vehicle
lane, public-road junction, shared-use classification or traffic certification
is implied. All travel surfaces are at zero native datum; the divider is 0.08 m
high. Benches face the corridor and stay outside travel bands.

Final package:
`C:/dev-artifacts/CityPrompt/public-realm-batch2-2026-09-22/active-path-v002/`.
The companion `ACTIVE_PATH_MODEL_2026-09-22.json` records exact hashes, module
assets, sizes and geometry checks. The assembly is 85,072 bytes / 944 triangles.
V001 is preserved; v002 corrects bench orientation. Four final reimported-GLB
views were individually inspected. Builder visual review passes; no independent
review has occurred. Dry run, exact section arithmetic, finite/full-envelope
geometry, 447 travel/crossing ray samples and divider-gap checks pass. GLBs are
self-contained and texture-free. Browser/runtime gates remain NOT TESTED.

## Integration before Sol browser testing

This is **not an installed executable path**. Add an isolated exact-ID adapter
through shared street/path section, sweep, furniture, terrain and route systems.
Never bend or repeat `assembly-preview.glb`; sweep the metric bands along the
actual route. Preserve band ordering when reversing direction. Fixture endpoints
are evidence boundaries, not designed public junctions. Keep crossing openings,
markings and furniture exclusion owned by the same route/network geometry.

Keep native furniture scale and current measured support; use the existing
shared tree stand only if its complete envelope fits the reserved space.
No new trees or rounded proxy crowns were generated. On a disposable vacant
Currie layout, test straight/bent/reversed paths, park/building connections,
fixed width during edits, slope support, move, Undo/Redo, reload, landscaping
exclusion, stale-capture blocking and actual exact export. All these remain open
in the copied runtime-review template; this offline evidence is not a student pass.

Replay with Blender 5.2 and `--python-exit-code 1`:
`tools/greenway_street_model/build_active_path.py -- --output <fresh-dir>`.
First add `--dry-run`; afterwards run
`tools/greenway_street_model/verify_active_path.py -- <candidate-dir>`.
The existing `scene.py` utility is reused unchanged. Generated GLBs/renders stay
external; source and checkpoints only are committed. No paid generation,
database changes, catalogue activation or push occurred.
