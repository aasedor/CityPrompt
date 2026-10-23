# Barcelona passatge (covered passage) (RLASM v6.1 architectural clay)

Candidate K5 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `barcelona_passatge / variant_0`
(catalogue variant id `barcelona_passatge_v0`) from `frontend/public/archetypes/streets/barcelona-passatge-covered-passage/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,623,910 | `81100da89fdcde1e` |
| oblique | `variant_0_angle_60.jpg` | 973,696 | `91e5b7b486005a0c` |
| top | `variant_0_angle_90.jpg` | 941,432 | `c13e0acab15bcb53` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 70 x 81 m, 20.5 m to the highest point; 3 storeys (street option: a covered pedestrian passage; the three-storey brick facades with shops below and flats above are the walls it is read with).
- storey programme: street option: a covered pedestrian passage; the three-storey brick facades with shops below and flats above are the walls it is read with
- plan: 11 m between the passage facades and 30 m from the open south mouth to the end wall (top view); a 1.2 m brick end wall with a round-arched portal to the north street; a tiled square in front of the mouth
- facade: red-orange brick with cream stone pilasters, belts and arch surrounds; timber shopfronts with green gilt-lettered signboards; round-arched French windows with wrought-iron balconies; wall lanterns
- vault: pointed glass vault on five transverse wrought-iron ribs with lattice brackets on pilaster corbels, dense glazing bars, three purlins a side, crests on the ribs, a glazed north lunette and an ornamental south end arch
- inferred: shop interiors, upper rooms, the outer faces of the passage block and the surrounding blocks are context and teaching assumptions; metric dimensions are authored from the pixel ratios
- levels (m): 0.00, 0.12, 5.00, 8.00, 10.80, 15.92

## Construction and delivery (Phases C to F)

`family_passatge.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, interior, roof_vault, south_portal, north_portal, shopfronts, floor_tiles, pavilion_finial`.

Run:

```
python tools/clay_barcelona_passatge/lock_sources.py
python tools/clay_barcelona_passatge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_barcelona_passatge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_barcelona_passatge
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

## Open blockers after v001

Candidate: `clay-barcelona-passatge-clay-v001.glb`. The v001 independent review (`evidence/v001/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, facade_close, architecture_close, glass_close, interior, north_portal (vs source front)): Each main rib comes down the pilaster as a plain square bar. One straight diagonal strut joins it to the rib, and it lands on a plain cream box corbel. No openwork lattice spandrel bracket is visible, and neither are the hangers or the ring. In the source, each main rib carries a large pierced scroll and lattice... Likely fix: On every main rib, add a pierced lattice spandrel plate (a perimeter frame plus diagonal lattice or scroll infill, in the source palette's dark green-grey) filling the triangle between the leg, the rib and the strut....
- **P1** (roof_vault, rear, rear_side, left_side, right_side, aerial, front_corner (vs source oblique)): Seen from outside, the main ribs are smooth single bars with only a small spike at the ridge. The source shows a tall openwork cresting standing proud of the glazing on every main rib, plus a continuous crested ridge. The ridge cap and gutters are not legible as distinct members. Likely fix: Instance a pierced crest band, about 0.4 to 0.6 m tall, along the outer edge of each main rib from springing to ridge, plus a continuous ridge cresting. Add a visible ridge cap profile and an eaves gutter box at each...
- **P1** (facade_close, architecture_close, front, interior, shopfronts (vs source front)): The upper bays are two small stacked arched windows, each about 40% of the bay width, set in a flat brick field. They carry very deep, thick slab balconies (about 1 m) with plain vertical-bar rails. In the source, each bay above the signboard is a tall round-arched opening that nearly fills the bay between... Likely fix: Widen the arched openings and surrounds to about 65 to 75% of the bay. Recess the glazing about 0.3 m in brick reveals with visible returns. Reduce the balcony slabs to about 0.45 m deep and 0.12 m thick, with a...
- **P1** (interior, north_portal): Looking south out of the south mouth, the frame shows only a flat grey plane and a raw horizon line. There is no street frontage, block or skyline beyond the square, and the square ends abruptly. This sits inside a hero interior view. Likely fix: Add a cream stuccoed 5 to 6 storey context frontage across the street south of the square, built from the same block grammar as the east, west and north blocks, so the end arch frames a city view.
