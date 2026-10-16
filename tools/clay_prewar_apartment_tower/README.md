# New York pre-war apartment tower (RLASM v6.1 architectural clay)

Candidate E2 of the three-tower wave of 2026-10-16, chosen to add residential towers (types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `new_york_pre_war_apartment / variant_0`
(catalogue variant id `prewar_beaux_arts_grand`) from `frontend/public/archetypes/buildings/new-york-pre-war-apartment/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,588,791 | `a6d0d2b26c6a1999` |
| oblique | `variant_0_angle_60.jpg` | 1,024,116 | `63bb5633dd721a9f` |
| top | `variant_0_angle_90.jpg` | 860,261 | `c4c63aecf64a29cf` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 32 x 25 m, 48.4 m to the highest point; 12 storeys (two-storey limestone base (lobby, doctors' offices), ten brick storeys of flats).
- storey programme: two-storey limestone base (lobby, doctors' offices), ten brick storeys of flats
- plan: 32 x 25 m corner block, streets south and east (top view at 0.049 m/px); water-tank house 9.4 x 10.6 m on the roof north of centre
- facade: limestone base with rusticated joints; brick above a stone belt course; limestone quoin strips at the corners; a stacked limestone-framed bay over the entrance; dark double-hung windows on a 3.2 m bay with flat stone lintels and sills; stacked iron balconies on both street faces; deep modillion cornice and balustraded parapet with pedestals and corner urns
- inferred: storey heights and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar
- levels (m): 0.15, 4.55, 7.65, 10.75, 13.85, 16.95, 20.05, 23.15, 26.25, 29.35, 32.45, 35.55, 38.65

## Construction and delivery (Phases C to F)

`family_prewar.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, entrance_marquee, limestone_base, fire_balconies, cornice_balustrade, tank_house, interior, rear_court`.

Run:

```
python tools/clay_prewar_apartment_tower/lock_sources.py
python tools/clay_prewar_apartment_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_prewar_apartment_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_prewar_apartment_tower
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
