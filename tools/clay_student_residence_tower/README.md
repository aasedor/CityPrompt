# Student residence tower with a glass roof dome (RLASM v6.1 architectural clay)

Candidate E1 of the three-tower wave of 2026-10-16, chosen to add residential towers (types
with no clay, runtime or seed-library model yet; it replaces a Vancouverism tower that already had one). State: **stopped at v003 by the rework rule; v002 (0 P0 / 4 P1, tied with v003) is the candidate**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `student_residence_tower / variant_0`
(catalogue variant id `contemporary_curtainwall_biophilic`) from `frontend/public/archetypes/buildings/student-residence-tower/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,206,622 | `f71657f046d330b5` |
| oblique | `variant_0_angle_60.jpg` | 930,652 | `d2ecf16c6ffe4b80` |
| top | `variant_0_angle_90.jpg` | 876,613 | `0ed3c8e1b6353959` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 27 x 31 m, 47.6 m to the highest point; 12 storeys (two-storey glazed base (study commons, bike room, cafe), ten residence storeys, roof lounge under the dome).
- storey programme: two-storey glazed base (study commons, bike room, cafe), ten residence storeys, roof lounge under the dome
- plan: 26 x 30 m tower plate; base projecting 1.2 m south and east; white wall mass 10 x 10 m at the south-west corner; dome 12 m across near the roof centre (top view)
- facade: white columns and band over the glazed base with a sloping white soffit at the east end; white wall mass with horizontal joints; glass bands with white slab edges tilting alternately from floor to floor; recessed planted terraces
- inferred: storey heights and interiors are teaching assumptions; the north and east faces are not visible in the front or oblique and repeat the visible grammar
- levels (m): 0.15, 4.15, 8.15, 11.45, 14.75, 18.05, 21.35, 24.65, 27.95, 31.25, 34.55, 37.85, 41.15

## Construction and delivery (Phases C to F)

`family_student.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, glazed_base, slab_edges, planted_terrace, roof_dome, lattice_screen, interior, rear_north`.

Run:

```
python tools/clay_student_residence_tower/lock_sources.py
python tools/clay_student_residence_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_student_residence_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_student_residence_tower
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

## Open blockers after v003 (stopped: the same finding survived two targeted fixes)

- P1: the dome reads as a different object: a round hemisphere in a lawn ring, where the source dome is oval with a diagonal geodesic net on a storey-high glazed drum, further east against the south screen, densely planted on its west side (roof-garden finding carried from v001 and v002)
- P1: the penthouse is too small and low; in the source it is a full storey with doors and a parapet, about as tall as the dome, the dominant roof mass
- P1: the lattice screen reads as a guardrail; the source screen is 1 to 1.5 storeys of triangulated see-through panels hiding the lower dome
- P1: too many terraces (about 6 of 10 west floors against 2 to 3) and every terrace a planter box on the slab edge; the sources show recessed balconies with set-back glass and white side returns
- P2: see evidence/v003/independent-review.md
