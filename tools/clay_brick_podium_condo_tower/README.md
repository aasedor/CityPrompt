# Brick-podium glass condominium tower (RLASM v6.1 architectural clay)

Candidate T2 of the towers and mixed-use batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `condo_podium_tower / variant_0`
(catalogue variant id `brick_podium_glass_tower`) from `frontend/public/archetypes/buildings/condo-podium-tower/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,239,794 | `247f085b7d208f1f` |
| oblique | `variant_0_angle_60.jpg` | 1,008,232 | `4fded6c1a678e8d3` |
| top | `variant_0_angle_90.jpg` | 949,163 | `f1e657ae0de18030` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Podium 42 x 32 m and tower 30 x 24 m read from the top view; the tower is flush with the south and east street faces; the podium roof wraps it as a terrace.
- Levels 0.15 / 5.0 / 9.3 m then eleven tower storeys at 3.0 m; tower roof 42.3 m, parapet 43.0 m; penthouse 4.2 m.
- Podium: brick piers on a 5.5 m bay with double-height storefronts, dark canopy band, ribbon windows with precast sills, precast cornice, glass terrace balustrade.
- Tower: curtain wall with continuous mullions at 1.5 m and a 0.62 m spandrel per floor; two balcony stacks per face projecting 1.5 m; corner columns; core.
- Pale metal penthouse 22 x 16 m with louvres, rooftop units and a guard rail.

## Construction and delivery (Phases C to F)

`family_podium_tower.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `podium_retail, podium_setback, balcony_stack, roof_crown, corner_entry, interior, rear_lane`.

Run:

```
python tools/clay_brick_podium_condo_tower/lock_sources.py
python tools/clay_brick_podium_condo_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_brick_podium_condo_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_brick_podium_condo_tower
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
