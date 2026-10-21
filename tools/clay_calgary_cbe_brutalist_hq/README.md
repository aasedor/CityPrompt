# Calgary Board of Education brutalist headquarters (RLASM v6.1 architectural clay)

Candidate I3 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a building option from the building catalogue. State: **reopened by the user for a second pass (v004 re-aims the front, front_corner and side cameras to the locked views; geometry unchanged from v003); v002 remains the candidate until a review beats it**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_cbe_brutalist_hq / variant_0`
(catalogue variant id `calgary_cbe_brutalist_hq_v0`) from `frontend/public/archetypes/buildings/calgary-board-of-education-hq/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,299,315 | `9def4af92fce9930` |
| oblique | `variant_0_angle_60.jpg` | 875,513 | `596e75b3b905efd1` |
| top | `variant_0_angle_90.jpg` | 859,525 | `205aefd0b79e3ea7` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 38 x 35 m, 25.0 m to the highest point; 4 storeys (recessed ground storey (lobby and public counters), three office floors in the cantilevered precast box, a mechanical penthouse).
- storey programme: recessed ground storey (lobby and public counters), three office floors in the cantilevered precast box, a mechanical penthouse
- plan: 37.8 x 35.1 m corner block of 14 x 13 precast bays (top view); penthouse set back towards the north
- facade: deep plain fascia over the recessed ground storey; one deep-set window per bay between tapered fins; spandrel noses with sloped tops; tall plain parapet band; board-formed columns and wall panels below
- inferred: interiors, the west and north elevations and the ground-floor layout behind the glass are teaching assumptions
- levels (m): 0.45, 5.20, 5.60, 10.00, 14.40, 19.80, 24.20

## Construction and delivery (Phases C to F)

`family_cbe.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, window_module, corner_cantilever, ground_entrance, arcade_soffit, sculpture_plaza, west_side, roof_penthouse, interior, rear_north`.

Run:

```
python tools/clay_calgary_cbe_brutalist_hq/lock_sources.py
python tools/clay_calgary_cbe_brutalist_hq/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_calgary_cbe_brutalist_hq/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_calgary_cbe_brutalist_hq
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

## Open blockers after v003 (x)

x
