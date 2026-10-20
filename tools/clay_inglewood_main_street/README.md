# Inglewood main street (RLASM v6.1 architectural clay)

Candidate I8 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `inglewood_main_street / variant_0`
(catalogue variant id `inglewood_main_street_v0`) from `frontend/public/archetypes/streets/inglewood-main-street/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,322,295 | `c528164ed6ce8922` |
| oblique | `variant_0_angle_60.jpg` | 957,382 | `08729fbdd71064f1` |
| top | `variant_0_angle_90.jpg` | 894,253 | `96ea0c7b00c1b01a` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 95 x 59 m, 12.0 m to the highest point; 2 storeys (street option: a main-street section; the two-storey commercial blocks are the street wall it is read with).
- storey programme: street option: a main-street section; the two-storey commercial blocks are the street wall it is read with
- plan: 28.4 m building line to building line (top view), 76 m run of the north street wall from the cross street, a back lane behind
- facade: pale scored concrete sidewalks, red brick-paver furnishing strips and crossings, young street trees, black lamp standards with red banners, angled parking with white stall lines, double yellow centre line; red-brick two-storey storefront blocks with cream stone and white trim, storefront glazing, sign bands and cornices
- inferred: the south blocks, the lane and the buildings beyond it are context; the block interiors and rear walls are teaching assumptions
- levels (m): 0.00, 0.15, 4.80, 9.20, 10.80

## Construction and delivery (Phases C to F)

`family_inglewood.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`storefront_close, bracketed_cornice, arched_windows, corner_entrance, angle_parking, crosswalk_bulbout, street_furniture, sidewalk_section, roof_parapets, rear_lane`.

Run:

```
python tools/clay_inglewood_main_street/lock_sources.py
python tools/clay_inglewood_main_street/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_inglewood_main_street/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_inglewood_main_street
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
