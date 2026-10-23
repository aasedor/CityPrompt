# Climbing wall building: The Crucible (RLASM v6.1 architectural clay)

Candidate K1 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `climbing_wall_building / variant_0`
(catalogue variant id `climbing_crucible`) from `frontend/public/archetypes/buildings/climbing_wall_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,254,544 | `a2b53e14adb38bae` |
| oblique | `variant_0_angle_60.jpg` | 815,928 | `8443b0f6a5b3da03` |
| top | `variant_0_angle_90.jpg` | 896,561 | `cb1a5bf529bebca5` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 101 x 28 m, 28.1 m to the highest point; 4 storeys (a climbing hall behind the sloped wall, a glazed east hall of three upper levels over a ground-floor lobby).
- storey programme: a climbing hall behind the sloped wall, a glazed east hall of three upper levels over a ground-floor lobby
- plan: 101 m by 28 m block (landmark fit of the front and oblique; the AI-rendered top view is not consistent with them): a 62 m climbing wall between a 22 m west Corten block and a 17 m east Corten block
- facade: south: dark charcoal hexagonal panels on a wall leaning back slightly (1.5 m over 28 m) that folds into a darker facet near the east block, with amber LED route lines and holds; Corten panel grid on the end blocks; east: Corten frame round a mullioned curtain wall over a projecting band and recessed ground glazing
- roof: green roof of native grasses inside a coped parapet; red running-track loop with lane lines and a second run closing a loop round the west bed, dark pavilion, sunken half-round seating bowl, concrete paths, north walkway with a rail, two vent boxes
- site: black rubber fall-zone apron with a white edge, a bent steel bouldering frame and a disc; boulders, lawn, curving path, shrub beds; paved east plaza
- context: white smokestack north-east, red-brick gabled warehouses, road, parking and harbour water beyond (simple massing)
- inferred: interiors behind the east glazing, the north face and the west end face follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.15, 9.00, 14.50, 20.00

## Construction and delivery (Phases C to F)

`family_crucible.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`climbing_wall, route_holds, fall_zone, glass_close, architecture_close, facade_close, east_entrance, roof_track, roof_pavilion, interior`.

Run:

```
python tools/clay_climbing_crucible/lock_sources.py
python tools/clay_climbing_crucible/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_climbing_crucible/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_climbing_crucible
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v002

Candidate: `clay-climbing-crucible-clay-v001.glb`. The v002 independent review (`evidence/v002/independent-review.md`) left these P0/P1 findings open:

- **P1** (climbing_wall, front, front_corner, roof_track, top): The two west-half routes make a crossing "+"/X. A diagonal line runs from near the coping (268,305 in climbing_wall) down to (365,610), and it is crossed at (295,445) by a long near-horizontal traverse (240,440)→(575,478) that then turns down to (640,615). Neither route reaches the foot. The sources (front and... Likely fix: Re-author the two west polylines as in the source. Route A runs near-vertical from just below the coping to mid-height at about 0.08–0.12 of the wall length. Route B is a short horizontal (about 0.12 L) that then...
- **P1** (climbing_wall, front, front_corner): The same west traverse is broken: across about 3 panels (climbing_wall x≈370–470, y≈450–465) the amber strip vanishes behind the hex panels, and only small zig-zag slivers show in the joints between panel tops. This is an LED strip intersecting and passing behind the cladding. Likely fix: Subdivide every LED segment to at most the panel pitch. Project each vertex onto the real panel front surface and offset it by panel thickness plus a stand-off. Re-render climbing_wall and front to confirm the line...
- **P1** (top, roof_track, front, rear): The roof paths are disconnected fragments. A straight pale strip leaves the pavilion and dead-ends in the meadow (top 530–690, 520–610). A lone chevron or "V" slab sits beside the bowl with no connection to anything (top 785–840, 605–660; roof_track 1070–1215, 630–720). None of the paths reach the track, the bowl... Likely fix: Rebuild the roof paths as one connected polyline network per source top: pavilion forecourt → loop round the inner bed → bowl entry → junctions with the track on its south and east sides. Delete the chevron slab....
- **P1** (top, roof_track, rear, front): The "seating bowl" is a full-circle raised pale disc (a plinth with a vertical edge). It has a dark curved wall round roughly half its rim and only a short arc of about 3 tiers, covering about 1/3 of the circumference. In the rear view it reads as a round platform with a wall, not a bowl. Source top shows a... Likely fix: Replace it with a D-plan bowl of about the same radius: a flat paved stage on the diameter side, 4–5 concentric tiers stepping up over the full 180° curve, and a low dark retaining wall on the outside of the curve....
- **P1** (right_side, front, front_corner, glass_close, east_entrance): Behind the east curtain wall, two horizontal slab bands and six identical bright oval spotlight hot spots on blank interior walls (two columns × three storeys in right_side, with dimmer pools between them) dominate the glazing. The east end reads as a three-storey lit office façade. Source front and oblique show a... Likely fix: Remove or recess the intermediate slabs behind the curtain wall, or set them well back and dark, so the hall reads full-height. Replace the spot lamps with soft, even area lighting. Darken the interior linings or the...

The candidate v001's own open findings are in `evidence/v001/independent-review.md`.
