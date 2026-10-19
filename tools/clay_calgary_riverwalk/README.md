# Calgary RiverWalk street option (RLASM v6.1 architectural clay)

Candidate G11, added at the user's request after wave G on 2026-10-18: Calgary's RiverWalk as a street option,
locked from the Bow River pathway's Summer River Day views, which show the RiverWalk and the Peace Bridge. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `bow_river_pathway / variant_0`
(catalogue variant id `bow_river_pathway_v0`) from `frontend/public/archetypes/streets/bow-river-pathway/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,674,303 | `16b0c7932cb4ebc6` |
| oblique | `variant_0_angle_60.jpg` | 960,596 | `13dba812cdd827d1` |
| top | `variant_0_angle_90.jpg` | 938,413 | `3d0699cef7e90e0e` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 16 x 72 m, 18.0 m to the highest point; 0 storeys (street option: a riverside promenade section; the flanking blocks are context).
- storey programme: street option: a riverside promenade section; the flanking blocks are context
- plan: 16 m section from the rip-rap toe to the building line (top view), 72 m long, the Peace Bridge landing at the north end
- facade: pale scored concrete promenade, bronze handrail, rip-rap, riparian planting and cottonwoods, stone-faced planters and gabions, timber benches, pale-brick blocks, the red Peace Bridge
- inferred: the far bank, skyline and blocks are context; the river bed below the surface is not modelled
- levels (m): 0.00, 1.20

## Construction and delivery (Phases C to F)

`family_riverwalk.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, promenade_section, river_railing, planters_benches, riprap_bank, peace_bridge, aerial_section, rear_north`.

Run:

```
python tools/clay_calgary_riverwalk/lock_sources.py
python tools/clay_calgary_riverwalk/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_calgary_riverwalk/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_calgary_riverwalk
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Street-option notes

This is a fixed native street section built with the RLASM v6.1 clay method. The manifest's `street_contract`
records the ordered bands, the axis and a `pavers` junction finish for the shared street graph. The street gates
S1 to S4 in `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` (section, network, shared grade, clearance and identity) are a
separate runtime checkpoint and remain NOT TESTED. The context blocks, far bank and bridge are not part of the
section's runtime footprint.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v001 (the v002 rework targets all nine)

- P0 #1: the Peace Bridge does not land on the promenade: its deck and truss stop inside the planting against a continuous river rail, with no abutment, landing or rail opening, and open bar stubs at the truss ends.
- P1 #2: the bridge is a constant-section box with a flat deck at bank level; the sources show a tube with pointed tapered ends, a shallow arched deck and a white roof.
- P1 #3: band widths wrong: rip-rap about 0.5x and the riparian strip about 0.65x the promenade width, where the top source shows both about 1x.
- P1 #4: the rip-rap is sparse near-white angular cubes brighter than the promenade, not packed rounded grey boulders.
- P1 #5: the riparian strip is mostly bare soil with sparse stick grasses and lone shrubs; the sources show dense grass and shrub cover.
- P1 #6: the building-edge planters are smooth beige boxes of green cubes; the gabion walls and the building-side bronze rail are missing.
- P1 #7: the rear and end facades of the three blocks are blank.
- P1 #8: an open slot runs between the promenade slab and the riparian bed; the rail posts sit on the slab edge.
- P1 #9: the rear, left_side and rear_side cameras show the asset too small.
