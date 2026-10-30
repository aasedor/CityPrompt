# Straight source-owned bridge handoff

`straight_build.py` derives fifteen closed modules from the exact five source
GLBs pinned in `straight_specs.py`. It never edits an original GLB, installs an
asset, seeds a catalogue, or writes generated output inside the repository.

```powershell
python -m tools.drawn_bridge_routes.straight_build --style all --dry-run --output-dir C:/dev-artifacts/CityPrompt/straight-review
python -m tools.drawn_bridge_routes.straight_build --style all --output-dir C:/dev-artifacts/CityPrompt/straight-review
python -m pytest tools/drawn_bridge_routes/tests/test_straight_build.py -q
```

Every style emits `bridge_left_end.glb`, `bridge_main.glb`,
`bridge_right_end.glb`, `nativeStreetPilot.json`, and `provenance.json` under its
style subfolder. The row uses `source-span-bridge-v1`, ordered parts with metric
lengths and fixed/span/repeat modes. Each module is centred on its source
interval in glTF X across, Y up, Z negative along. Provenance contains exact
source/module/tool/material locks, component bounds/counts, closedness and
structural grade-contact bounds. Full source glTF material dictionaries survive
export, including extensions and semantic extras.

| Style | Rigid left / adaptive main / rigid right | Supported route length | Elevated surface |
| --- | --- | --- | --- |
| Brick viaduct | 11.630002 / 8.2 repeat / 7.1 m | 26.930002–240 m | Deck 8.4 m; railhead 8.96 m |
| Steel rail deck arch | 30.900002 / 15 repeat / 30.900002 m | 76.800004–240 m | Deck 13.05 m; railhead 13.36 m |
| Steel road truss | 5.457144 / 170/7 span / 5.457144 m | 29.128573–41.271431 m | Road 5 m; footway 5.15 m |
| Stone road arch | 24.5 / 19.5 repeat / 33.290001 m | 77.290001–240 m | Road 11 m; footway 11.15 m |
| Tied shared arch | 13.658241 / 38 span / 13.658241 m | 59.616482–71.016482 m | Foot/cycle 3.32 m; compact quays 3.3 m |

The outer rigid intervals enclose the complete native source feet, guards and
ornaments. These full-footprint lengths differ from a bearing-centre span or
an original authoring cut. Walking coordinates use the same native module
intervals and origins. The semantic junction selector is `pavers`; no new
ground surface or changed source material is emitted by that selector.

The rail derivative preserves the complete south bowstring, complete repeated
deck-arch ribs, paired bents and transverse portals. Train door leaves share
`CLAY_PLATE` with the structure, and train sill frames share `CLAY_HARDWARE` with
the guards; source-specific assembly bounds exclude both along with all train
skin, glass, roofs and bogies. Ribs and trailing bents each have one owner.

The brick source rectangular wall carrier is non-manifold after material
merging. Its exact original rectangular pier/header cells are recovered from
the locked authoring profile, retaining original curved spandrels, arch rings,
pilasters, shops and track components. Open source bed-joint sheets become
1 mm closed relief, and loose three-face ballast stones receive base faces.
One chosen complete detailed shop arch repeats; the source run's individual
shutter and plain-shop sequence is intentionally not reproduced bay by bay.

The road truss retains compact intersections of the original banks beneath
its bearings at ±17 m. The stone derivative retains the compact source-owned
abutment/quay polygons from its pinned ownership contract. These functional
supports reach grade and are distinct from the excluded surrounding banks.

The tied arch removes only the global 13° heading. The opposite 6° end skews
remain, and complete bearings, shelves, plinths, quays, guards and 17-tread
pedestrian stairs stay in the rigid end modules. The central arch, hangers,
ties, deck and planted divider deform together within 85–115%.

These are prepared-level conceptual derivatives. Road and rail endpoints stay
elevated; no automatic grade ramps or public-road/rail connections are claimed.
The tied stairs imply cyclist dismounting. Runtime previews, placement, terrain,
walking, edits, recovery, capture and human visual approval require separate
runtime evidence. No engineering or accessibility certification is implied.
