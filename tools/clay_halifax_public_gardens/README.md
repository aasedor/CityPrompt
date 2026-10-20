# Halifax Public Gardens (RLASM v6.1 architectural clay)

Candidate I6 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a park and open-space option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `halifax_public_gardens / variant_0`
(catalogue variant id `halifax_public_gardens_v0`) from `frontend/public/archetypes/openspaces/halifax-public-gardens/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,556,335 | `e87f7a011833076c` |
| oblique | `variant_0_angle_60.jpg` | 1,021,819 | `fe4f13a4732e47f4` |
| top | `variant_0_angle_90.jpg` | 928,683 | `adbd6581a714fa26` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 43 x 57 m, 14.0 m to the highest point; 0 storeys (open space: a fenced Victorian public garden with a bandstand; the street blocks are context).
- storey programme: open space: a fenced Victorian public garden with a bandstand; the street blocks are context
- plan: 43.2 x 57.2 m fenced block (top view at about 0.08 m per pixel): axis, cross path, paved bandstand circle, oval loop path, four inner carpet-bed lawns, four outer tree lawns
- facade: black wrought-iron picket fence on a granite curb, brick gate piers with lanterns and a gilded iron sign arch, white octagonal bandstand with a pink-copper ogee roof
- inferred: the north and side entrances, bed planting mixes and the street blocks are teaching assumptions
- levels (m): 0.00, 0.04, 0.07, 0.09, 1.00

## Construction and delivery (Phases C to F)

`family_hpg.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`gate_arch, gate_piers_fence, bandstand, bandstand_roof, carpet_beds, inner_lawn_beds, loop_benches, mature_trees, side_entrance, rear_north`.

Run:

```
python tools/clay_halifax_public_gardens/lock_sources.py
python tools/clay_halifax_public_gardens/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_halifax_public_gardens/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_halifax_public_gardens
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
