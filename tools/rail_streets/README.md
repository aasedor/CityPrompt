# Rail streets

Three drawable rail corridors for the native street engine, built in pure Python:

| Street | Id | Parent archetype | Width | Cycle |
|---|---|---|---:|---:|
| Median LRT Avenue | `student_median_lrt_avenue_v1` | `light_rail_tram_avenue` | 34 m | 40 m |
| LRT Right-of-Way | `student_lrt_right_of_way_v1` | `light_rail_tram_avenue` | 20 m | 40 m |
| High-Speed Rail Line | `student_high_speed_rail_line_v1` | `high_speed_rail_corridor` (new) | 30 m | 50 m |

Students draw them like the other native streets: pick the card, click a route with
bends or curves, from one cycle long up to 2 km, and the engine repeats one fixture
cycle along it. They are local pilots: registered, not runtime-tested, not published.

`docs/RAIL_STREETS_2026-11-20.md` describes the sections and the checks.

## How a rail street is drawn

- **Program details** are boxes the engine sweeps along the route and bends with it:
  rails, sleepers, slab panels, base layers, cable troughs, curbs, gutters,
  markings, and the contact, messenger and feeder wires with their droppers.
  `z` is a detail's centre height.
- **Mesh details** are triangles in the cycle frame, clipped and bent the same way:
  the ballast prisms and the high-speed embankment.
- **Modules** are rigid GLBs placed per cycle: poles, masts, fence panels, lights,
  trees, cabinets and marker boards. The engine drops a module near a junction or
  a bend sharper than 15°, so fences open where streets cross, and keeps the wires
  and rails running.

Every cantilever ends on its contact wire, and nothing below 4 m stands inside a
train's envelope; `test_rail_streets.py` checks both.

## Files

| File | Purpose |
|---|---|
| `build.py` | The three streets. Every dimension is a named constant or a spec value |
| `install.py` | Additive, text-level registration in every registry, refusing conflicts; dry run by default |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the three-cycle preview assembly in headless Chromium |
| `test_rail_streets.py` | 24 tests: the generator reproduces the registered rows and module bytes, determinism, sections, module fit, train envelopes and clear routes, gauge and continuity, cantilevers, lane counts, high-speed dimensions, conventions |

Module GLBs, previews and renders are review material under the ignored
`artifacts/rail-streets/` directory; the registered modules are under
`frontend/public/street-kits/pilots/<id>/`.

## Reproduce

```bash
python3 tools/rail_streets/build.py --street median_lrt --output <dir>-card
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/rail_streets/render.cjs median_lrt <dir>-card/assembly-preview.glb <dir>-card/renders card
python3 tools/rail_streets/build.py --street median_lrt --output <dir> --reference <dir>-card/renders/card.png
python3 tools/rail_streets/install.py --package <dir> --backups <backup dir>            # dry run
python3 tools/rail_streets/install.py --package <dir> --backups <backup dir> --install  # add --no-history for all but the last
python3 -m pytest tools/rail_streets
```

The build is deterministic, so the second build writes the same modules and preview
as the first and adds only the card image and its reference lock. The streets are
`median_lrt`, `lrt_row` and `hsr`. `build.py` refuses an existing directory and
`render.cjs` refuses to replace a render.
