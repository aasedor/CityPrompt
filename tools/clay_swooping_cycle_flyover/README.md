# Swooping elevated cycle flyover (RLASM v6.1 architectural clay)

Candidate H10 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `dedicated_cycle_bridge / variant_0`
(catalogue variant id `dedicated_cycle_bridge_v0`) from `frontend/public/archetypes/streets/dedicated-cycle-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,373,407 | `ed500b98870febb7` |
| oblique | `variant_0_angle_60.jpg` | 946,422 | `8b344d31bea17460` |
| top | `variant_0_angle_90.jpg` | 908,066 | `06f41b7b82df87fd` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 280 x 46 m, 7.5 m to the highest point; 0 storeys (bridge: an elevated cycle ribbon swooping over a street junction).
- storey programme: bridge: an elevated cycle ribbon swooping over a street junction
- plan: an S-shaped ribbon about 190 m across the junction (top view) in two broad bends, ramps down at both ends
- facade: dark deck with a white dashed centre line, tall orange slatted parapets with a flat orange handrail, pale underside, slender concrete Y-columns
- inferred: the ramp ends beyond the junction and the corner blocks are simplified context
- levels (m): 0.00, 6.20, 7.45

## Construction and delivery (Phases C to F)

`family_flyover.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, y_column, ramp_curve, parapet_panel, deck_surface, street_under, landing_ramp, rear_north`.

Run:

```
python tools/clay_swooping_cycle_flyover/lock_sources.py
python tools/clay_swooping_cycle_flyover/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_swooping_cycle_flyover/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_swooping_cycle_flyover
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
