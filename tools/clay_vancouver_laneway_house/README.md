# Vancouver laneway house (RLASM v6.1 architectural clay)

Candidate J3 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vancouver_laneway_house / variant_0`
(catalogue variant id `vancouver_laneway_house_v0`) from `frontend/public/archetypes/buildings/vancouver-laneway-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,408,640 | `6bc2fb3d703006bf` |
| oblique | `variant_0_angle_60.jpg` | 978,778 | `e753b3c4369a642d` |
| top | `variant_0_angle_90.jpg` | 852,387 | `a0cc3f3e463a046f` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 7 x 8 m, 8.3 m to the highest point; 2 storeys (living and dining on the ground floor behind the glazed corner, bedrooms and a sitting room above off the front balcony).
- storey programme: living and dining on the ground floor behind the glazed corner, bedrooms and a sitting room above off the front balcony
- plan: 7.4 x 8.1 m under one hipped roof (0.38 m side and 0.30 m end overhangs); a 2.9 x 1.0 m two-storey glazed bay at the south-west corner and a 1.0 m deep porch and balcony recess east of it, closed by a full-height cedar end fin; a 5.0 x 6.0 m one-storey garage against the rear wall
- facade: vertical cedar boards of varied tone with fine dark joints on a concrete plinth; heavy black window frames; a deep cedar band under the front roof edge; a horizontal-board panel over the side entry; wood front and side doors
- inferred: interiors, the east and rear walls and the garage interior are teaching assumptions; the garage, which the front view shows as a low hip-roofed building with a board door behind the house, is placed on the plan of the lower roof in the top view
- levels (m): 0.48, 3.32, 5.55

## Construction and delivery (Phases C to F)

`family_laneway.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

The garden beds are planted with the shared planting kit (`plantkit.py`, concatenated after `gcommon.py`;
its text is identical to the kit chunk in `tools/clay_planting_kit_showcase/family_plantkit.py`) as linked
instances, so `build.py` carries the kit's `keep_instances()` shim and writes `evidence/planting-kit-size.json`.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, glass_close, architecture_close, entry_steps, side_entry, west_wall, roof_seams, garage, interior, garden`.

Run:

```
python tools/clay_vancouver_laneway_house/lock_sources.py
python tools/clay_vancouver_laneway_house/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vancouver_laneway_house/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vancouver_laneway_house
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

## Open blockers after v001 (x)

x
