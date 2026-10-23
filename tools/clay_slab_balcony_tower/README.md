# Mid-century slab balcony tower (RLASM v6.1 architectural clay)

Candidate T1 of the towers and mixed-use batch. State: **PASS_ZERO_P0_P1 at v007 (independent review); v007 is the candidate, not keeper-approved**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `west_end_mid_century_tower / variant_0`
(catalogue variant id `midcentury_concrete_slab`) from `frontend/public/archetypes/buildings/west-end-mid-century-tower/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,359,002 | `2162c09765e06422` |
| oblique | `variant_0_angle_60.jpg` | 962,210 | `5f73a8002e4e03e7` |
| top | `variant_0_angle_90.jpg` | 860,456 | `b5030b8a17f908b9` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Square 22 x 22 m plan read from the top view; balcony plates project 1.6 m on the outer bays of every face.
- Recessed glazed ground floor (4.6 m) on columns; twelve apartment storeys at 2.95 m; roof 42.95 m, parapet 43.65 m; penthouse 6.2 m.
- Per face: balcony bay, centre bay with brick spandrel and window band, balcony bay; concrete fins at the bay lines and corners; slab edge band every storey.
- Two-storey concrete mechanical penthouse at the centre-rear with a louvre, door and elevator overrun; three rooftop units.
- Storey count recorded: the oblique balcony stacks read twelve to thirteen; twelve authored within the 1 MiB clay budget.

## Construction and delivery (Phases C to F)

`family_slab_tower.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `balcony_close, fin_contact, lobby_entry, roof_penthouse, base_corner, interior, rear_lane`.

Run:

```
python tools/clay_slab_balcony_tower/lock_sources.py
python tools/clay_slab_balcony_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_slab_balcony_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_slab_balcony_tower
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 1 MiB (Git LFS
  uploads are refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

## Open blockers after v007 (passed)

Passed at v007 (0 P0 / 0 P1 / 7 P2) in the reopened run after the lifted GLB limit; no open blockers. Open P2 for a later detail pass: light hotspots through the glazing, a stepped penthouse where the source shows one cube, generic rooftop unit placement, a heavier corner pier than the source's thin fin, a thin canopy, a small speckled sliver at one north fin head, a tight interior camera. Not keeper-approved; RLASM asset review, runtime acceptance and publication approval are separate checkpoints.
