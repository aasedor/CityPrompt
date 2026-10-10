# Queen Anne rowhouse trio (three units, individual grade entrances) (RLASM v6.1 architectural clay)

Candidate 6 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `brick_rowhouse_terrace / variant_2`
(catalogue variant id `queen_anne_bay_window_terrace`) from `frontend/public/archetypes/buildings/brick-rowhouse-terrace/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,498,852 | `8ceae05a5766013b` |
| oblique | `variant_2_angle_60.jpg` | 964,010 | `0b7e647668380cd6` |
| top | `variant_2_angle_90.jpg` | 927,428 | `7e0d7266af5a30bc` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; depicts the catalogue hero, not enrolled).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Three 5.8 m units (17.4 m frontage) 11 m deep; front gardens 4.2 m behind a low wall and iron fence; rear yards 6 m with timber fences.
- Levels 0.15 / 3.4 m; eaves 6.6 m; slate main roof to a 11.2 m ridge (40 degrees) with front cross gables over the end units, a small dormer over the middle unit, rear cross gables over rear wings and chimney stacks at the party lines and both ends.
- Unit pattern: A (east end) bay window right and door left under a bargeboard gable; B door, window and dormer; C door right and bay window left under a gable.
- Sash windows with cream stone sills and lintels, cream string courses, canted bays under slate hip caps, three-step stoops with iron handrails, green timber gable infills with battens and finials.
- Source conflict recorded: the locked views show the terrace continuing west; the three east-end units are modelled as one building with a blank west party wall.

## Construction and delivery (Phases C to F)

`family_rowhouse.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `entrance_steps, bay_window, gable_close, roof_contact, rear_yards, interior, party_wall`.

Run:

```
python tools/clay_queen_anne_rowhouse_trio/lock_sources.py
python tools/clay_queen_anne_rowhouse_trio/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_queen_anne_rowhouse_trio/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_queen_anne_rowhouse_trio
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
