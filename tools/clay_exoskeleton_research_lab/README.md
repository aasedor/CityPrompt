# Research laboratory with a white steel exoskeleton (RLASM v6.1 architectural clay)

Candidate F2 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `research_laboratory / variant_0`
(catalogue variant id `high_tech_exoskeleton`) from `frontend/public/archetypes/buildings/research-laboratory/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,303,211 | `8aed179ffe03b5db` |
| oblique | `variant_0_angle_60.jpg` | 908,152 | `b9f323ed50f2d453` |
| top | `variant_0_angle_90.jpg` | 810,690 | `9b2377977becd244` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 31 x 25 m, 23.4 m to the highest point; 4 storeys (recessed glazed ground floor (lobby, service bays), three laboratory floors, roof plant).
- storey programme: recessed glazed ground floor (lobby, service bays), three laboratory floors, roof plant
- plan: 30 x 25 m upper block (top view); the ground floor recessed 2.4 m behind V-pilotis on the south and set back 7 m at the west under a cantilever; plant screen set 3 m in from the roof edge
- facade: curtain wall with white slab bands on the south, west and north; white steel exoskeleton with alternating diagonals and grey louvre infill on the east, wrapping the south-east corner; V-pilotis at the street; angled cantilever soffit at the west
- inferred: storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the curtain-wall grammar
- levels (m): 0.15, 5.60, 9.80, 14.00, 18.20

## Construction and delivery (Phases C to F)

`family_lab.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, v_pilotis, exoskeleton, roof_screen, cantilever, stacks, interior, rear_north`.

Run:

```
python tools/clay_exoskeleton_research_lab/lock_sources.py
python tools/clay_exoskeleton_research_lab/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_exoskeleton_research_lab/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_exoskeleton_research_lab
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

## Open blockers after v003 (v004 targets every P1)

1. P1: black blocks where the portal post meets its head, at the cantilever's north-west corner and on the exoskeleton column tops. Survived one targeted fix.
2. P1: a deep white band above the top floor and a heavy frame hide the perforated roof screen in the front view; the source glass runs to a thin edge under a tall perforated crown.
3. P1: the east louvres read from the front as narrow recessed strips with wide white margins; the steel is chunkier and the louvres lighter than the source. Survived one targeted fix.
