# Regional hospital with braced-frame ward block and glass atrium (RLASM v6.1 architectural clay)

Candidate D5 of the five-building wave of 2026-10-15, chosen to fill catalogue gaps (building types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `regional_hospital_medical_center / variant_0`
(catalogue variant id `regional_hospital_contemporary_teaching`) from `frontend/public/archetypes/buildings/regional-hospital-medical-center/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,295,867 | `4e6289d461f2ad8b` |
| oblique | `variant_0_angle_60.jpg` | 924,620 | `67e7bf7fa9838b5c` |
| top | `variant_0_angle_90.jpg` | 860,461 | `1bceac8705902772` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 69 x 59 m, 40.0 m to the highest point; 9 storeys (two-storey brick base (outpatients, emergency), five clinical storeys, plant storey; ward block of nine storeys).
- storey programme: two-storey brick base (outpatients, emergency), five clinical storeys, plant storey; ward block of nine storeys
- plan: clinical block 51 x 35 m at the south-west; L-shaped ward block (north bar 50 x 18 m, east leg 10 x 53 m); atrium 8 x 31 m between them opening south (top view at 0.097 m/px)
- facade: clinical block: brick base with large windows, pale panels with perforated screens over strip glazing, dark vertical signage panel, dark louvre band at the plant storey; ward block: glazing behind a steel exoskeleton of 5 m bays, ring beams every two storeys and X-braces; atrium: glass with a diagonal mullion net
- inferred: storey heights and interiors are teaching assumptions; the north and west faces of the ward block are not visible in the front or oblique and repeat the visible grammar
- levels (m): 0.15, 5.00, 9.00, 13.00, 17.00, 21.00, 25.00, 29.00, 33.00, 37.00

## Construction and delivery (Phases C to F)

`family_hospital.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, braced_frame, entrance_canopy, roof_canopy, roof_plant, brick_base, interior, rear_north`.

Run:

```
python tools/clay_braced_frame_hospital/lock_sources.py
python tools/clay_braced_frame_hospital/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_braced_frame_hospital/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_braced_frame_hospital
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

## Open blockers after v004

- P1: the atrium's diagonal mullion net runs to the pavement across the main entrance, the revolving doors behind the lattice; the source has a straight vertical-mullion storefront with a revolving door below the canopy line
- P2: see evidence/v004/independent-review.md
