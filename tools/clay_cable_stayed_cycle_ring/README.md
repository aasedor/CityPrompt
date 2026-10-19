# Cable-stayed circular cycle bridge (RLASM v6.1 architectural clay)

Candidate H5 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `dedicated_cycle_bridge / variant_1`
(catalogue variant id `dedicated_cycle_bridge_v1`) from `frontend/public/archetypes/streets/dedicated-cycle-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,220,653 | `c3bbebd85c5bc155` |
| oblique | `variant_1_angle_60.jpg` | 804,750 | `59f81bdf60ace7b3` |
| top | `variant_1_angle_90.jpg` | 890,788 | `2eed66a8bdfc962b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 72 x 130 m, 60.0 m to the highest point; 0 storeys (bridge: a circular cycle and footbridge over a road intersection).
- storey programme: bridge: a circular cycle and footbridge over a road intersection
- plan: 72 m ring (top view), a 5.4 m deck, one straight ramp leaving the south-west of the ring and running south
- facade: red cycle surface with white dashed markings, white railings on both edges, white box girder, radial steel cables, a slender steel pylon, concrete columns
- inferred: the corner plots and their houses are simplified context; ramp length is an assumption
- levels (m): 0.00, 6.60, 48.00, 60.00

## Construction and delivery (Phases C to F)

`family_ring.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, pylon_head, cable_fan, ring_deck, ramp_landing, column_support, intersection_under, rear_north`.

Run:

```
python tools/clay_cable_stayed_cycle_ring/lock_sources.py
python tools/clay_cable_stayed_cycle_ring/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_cable_stayed_cycle_ring/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_cable_stayed_cycle_ring
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

## Open blockers after v002 (v003 reworks these three)

- P1 #1: the cables stop at the top of the inner deck kerb while their anchor blocks hang lower on the fascia with bare fascia between; the cables don't land on their anchors and the blocks float.
- P1 #2: every pitched context house still has a solid black slot along the gable base or eave (the v001 black-gable finding, partly fixed, surviving one targeted fix).
- P1 #3: the ramp deck has the ring's red finish and dashed centre line; the sources show a pale grey-beige concrete ramp with a solid white centre line.
