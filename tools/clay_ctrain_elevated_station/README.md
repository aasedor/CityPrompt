# Downtown elevated CTrain station (RLASM v6.1 architectural clay)

Candidate D3 of the five-building wave of 2026-10-15, chosen to fill catalogue gaps (building types
with no clay or runtime family yet). State: **PASS_ZERO_P0_P1 at v004 (independent review); v004 is the candidate, not keeper-approved** (not keeper approval). Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_ctrain_station / variant_0`
(catalogue variant id `ctrain_downtown_platform`) from `frontend/public/archetypes/buildings/calgary-ctrain-station/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,429,334 | `6f2d08e5f54d240f` |
| oblique | `variant_0_angle_60.jpg` | 935,570 | `eb69fb9869a125e6` |
| top | `variant_0_angle_90.jpg` | 862,998 | `526e800497081f31` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(8 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 72 x 72 m, 18.6 m to the highest point; 3 storeys (street lobby, platform-level concourse, upper concourse with the skywalk links).
- storey programme: street lobby, platform-level concourse, upper concourse with the skywalk links
- plan: 36 x 26 m headhouse; twin 6 m side platforms either side of two tracks on an elevated deck running 35 m south over the east-west street; 24 m glazed canopies; west skywalk 22 m; east link and a 60 m north-south skywalk (top view at 0.115 m/px)
- facade: red brick with tall punched windows; glazed top-storey band between the towers; stair towers with full-height glazed bays and pale caps
- inferred: storey heights and interiors are teaching assumptions; the neighbouring towers the skywalks reach are not part of the asset, so the skywalks end at glazed stair pavilions; the north face is not visible in any source
- levels (m): 0.15, 6.00, 10.00, 14.00

## Construction and delivery (Phases C to F)

`family_ctrain.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, platform_canopy, skywalk_bridge, street_underpass, tower_cap, train_platform, interior, east_skywalk`.

Run:

```
python tools/clay_ctrain_elevated_station/lock_sources.py
python tools/clay_ctrain_elevated_station/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_ctrain_elevated_station/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_ctrain_elevated_station
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

## Open blockers after v004 (independent review PASS_ZERO_P0_P1; not keeper approval)

- No P0 or P1. P2 polish items (mullion stubs and specks at frame and truss nodes, converging verticals in the front, charcoal underpass soffit, slightly light brick, street position relative to the platforms, track ends reading as a terminus) are listed in evidence/v004/independent-review.md
