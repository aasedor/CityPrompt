# Old Montreal limestone commercial building (RLASM v6.1 architectural clay)

Candidate I4 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a building option from the building catalogue. State: **stopped at v004 by the stopping rule (independent review PASS_ZERO_P0_P1); v004 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `old_montreal_limestone_commercial / variant_0`
(catalogue variant id `old_montreal_limestone_commercial_v0`) from `frontend/public/archetypes/buildings/old-montreal-limestone-commercial/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,509,189 | `af691c0c7a1f20be` |
| oblique | `variant_0_angle_60.jpg` | 923,080 | `b158c78db9eb6550` |
| top | `variant_0_angle_90.jpg` | 874,520 | `f5653065c75c4e01` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 107 x 49 m, 42.5 m to the highest point; 3 storeys (low basement and three storeys of market hall, shops and assembly rooms).
- storey programme: low basement and three storeys of market hall, shops and assembly rooms
- plan: 107 m long hall in two 21 and 19.5 m deep ranges offset by one range depth at a 22 m square dome block (top view); south portico 17 m wide, north arcaded porch
- facade: grey limestone ashlar; three tiers of six-over-six windows with barred basement vents; pilaster strips, plinth, sill bands and a modillioned eave cornice; east end pavilion with round-arched windows, radial fanlights, iron balconettes, an eaves balustrade and a pediment
- dome: square stone attic with corner pedestals, drum of sixteen round-arched windows between pilasters, ribbed silver tin dome, open lantern with cupola and cross
- inferred: interiors, the north and west fronts and the dome block east face follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.90, 6.00, 10.60, 15.00

## Construction and delivery (Phases C to F)

`family_oldmtl.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`portico, dome_drum, end_pavilion_arches, balconettes, east_door, long_facade, roofs_dormers, west_range, interior, rear_north`.

Run:

```
python tools/clay_old_montreal_limestone_commercial/lock_sources.py
python tools/clay_old_montreal_limestone_commercial/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_old_montreal_limestone_commercial/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_old_montreal_limestone_commercial
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

## Open blockers after v004 (x)

x
