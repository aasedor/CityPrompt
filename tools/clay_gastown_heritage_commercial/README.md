# Gastown heritage commercial block (RLASM v6.1 architectural clay)

Candidate J1 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `gastown_heritage_commercial / variant_0`
(catalogue variant id `gastown_heritage_commercial_v0`) from `frontend/public/archetypes/buildings/gastown-heritage-commercial/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,472,172 | `ddd3ab09b0127bb6` |
| oblique | `variant_0_angle_60.jpg` | 954,203 | `3b43cbf516b938a3` |
| top | `variant_0_angle_90.jpg` | 881,317 | `f9db097bb5223aa1` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 26 x 24 m, 19.5 m to the highest point; 3 storeys (ground-floor shops and two floors of offices).
- storey programme: ground-floor shops and two floors of offices
- plan: 26 m by 23.6 m corner block (top view), party walls to a lower neighbour on the west and a block on the north
- facade: red brick with rusticated sandstone piers; south front of five bays (four wide arched-window bays and a paired corner bay), east front of a wide corner bay, four narrow sash bays and a paired-arch end bay; stone sill bands and lintels, carved pier capitals, lettered frieze and modillion cornice; pediment with an acanthus crest over the central bay
- shopfronts: panelled bulkheads, plate glass, small-paned transoms, recessed timber doors, dark signboard fascia with gilt lettering and a moulded shop cornice
- streetscape: brick sidewalks, cobbled south street, asphalt east street, steam clock, chained bollards, globe-cluster lamp posts, two street trees
- inferred: interiors, the north and west walls above the neighbours and the roof penthouse interior follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.15, 5.60, 10.30, 16.50

## Construction and delivery (Phases C to F)

`family_gastown.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`steam_clock, storefronts, name_frieze_pediment, glass_close, architecture_close, east_facade, facade_close, roof_skylights, interior, rear_north`.

Run:

```
python tools/clay_gastown_heritage_commercial/lock_sources.py
python tools/clay_gastown_heritage_commercial/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_gastown_heritage_commercial/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_gastown_heritage_commercial
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

## Open blockers after v002 (x)

x
