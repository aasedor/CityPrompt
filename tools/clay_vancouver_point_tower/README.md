# Vancouverism point tower on a curved podium (RLASM v6.1 architectural clay)

Candidate E1 of the three-tower wave of 2026-10-16, chosen to add residential towers (types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vancouverism_tower_podium / variant_0`
(catalogue variant id `vancouverism_classic`) from `frontend/public/archetypes/buildings/vancouverism-tower-podium/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,268,249 | `5a3076ec759214b5` |
| oblique | `variant_0_angle_60.jpg` | 981,065 | `f213a2624823eb9d` |
| top | `variant_0_angle_90.jpg` | 932,733 | `a06d2b25d445cf20` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 58 x 42 m, 58.5 m to the highest point; 17 storeys (three-storey podium (retail colonnade, two storeys of flats), fourteen tower storeys, mechanical penthouse).
- storey programme: three-storey podium (retail colonnade, two storeys of flats), fourteen tower storeys, mechanical penthouse
- plan: podium 40 x 42 m with 6 m rounded south corners; east wing 18 x 28 m of two storeys; tower 32 x 24 m with 4 m rounded corners on the podium north half, leaving a 16 m roof terrace to the south (top view)
- facade: podium: round columns before recessed glazing, concrete frame with brick infill and windows, continuous second-storey balcony, white curved parapet with glass guard; tower: curtain wall with white floor bands, white fins at 1.2 m on the western half, stacked glass-fronted balconies on the eastern half and the east face, three white sweeping blades on the south face
- inferred: the catalogue range is 25-60 storeys but the locked views show fourteen tower storeys over the podium, so the pixels govern; storey heights and interiors are teaching assumptions; the north face is not visible in any source
- levels (m): 0.15, 5.00, 8.50, 12.00, 15.00, 18.00, 21.00, 24.00, 27.00, 30.00, 33.00, 36.00, 39.00, 42.00, 45.00, 48.00, 51.00, 54.00

## Construction and delivery (Phases C to F)

`family_vancouver.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, podium_colonnade, balcony_stack, sweep_blade, podium_terrace, roof_garden, interior, east_wing`.

Run:

```
python tools/clay_vancouver_point_tower/lock_sources.py
python tools/clay_vancouver_point_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vancouver_point_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vancouver_point_tower
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
