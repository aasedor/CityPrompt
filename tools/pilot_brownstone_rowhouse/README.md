# Pilot: brownstone end-of-row house (RLASM v6.1 architectural clay)

One-building pilot of the RLASM method run from a Linux cloud session, using
locked catalogue views as the only source. State: **candidate under review**.
Nothing here is keeper-approved, runtime-integrated, enrolled in a catalogue or
activated. Those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `brownstone_rowhouse_frontage / variant_0`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,313,577 | `81b0c505faff936e` |
| oblique | `variant_0_angle_60.jpg` | 883,218 | `ea4ddffe045599af` |
| top | `variant_0_angle_90.jpg` | 802,789 | `79d3e4f2dc8b6cfe` |

Origin: `catalogue_reference_nomination`. `hero.png` is byte-identical to the
front view and is not enrolled twice. Sibling variants 1 to 3 are excluded;
mixing is not allowed. This was the only rowhouse archetype whose three
roles were hydrated locally; every other candidate had LFS pointers for the
oblique and top views.

## Measurement contract (Phase B)

Read from the pixels, calibrated to an 11.6 m frontage:

- Five front bays at 2.32 m: window, window, pedimented entrance, window, window.
- Raised garden level with four grilled windows and an under-stoop passage door;
  parlour and upper storeys above; bracketed cornice; flat roof with parapet.
- High stoop (11 risers) landing on the areaway fence line with urn newels.
- Left flank: quiet brick with sparse rear-half openings and two chimneys.
- Right elevation: blank brick party wall (end-of-row unit), one chimney.
- Lower two-storey rear wing flush with the party wall; glazed roof lantern.
- Levels 0.15 / 2.10 / 5.80 m; main roof 9.30 m; wing roof 6.00 m; cornice
  crown 9.94 m; chimney pots 11.37 m.

Metric dimensions, interiors and the wing depth are authored teaching
assumptions. The storey programme is a fixed authored assembly (three levels).

## Construction and delivery (Phases C to F)

`family_brownstone.py` composes the building with the repository's own
`clay_core`, `geometry` and `assemblies` modules, unchanged. `build.py` is a
Linux-safe runner that mirrors `prepare_candidate` without its Windows
artefact-root assertion, writes heavyweight artefacts outside the repository,
and renders every roster camera from the re-imported GLB with Cycles on CPU.

Camera roster: the ten required baseline views plus `top`, `stoop_contact`,
`areaway_door`, `roof_contact`, `rear_wing`, `side_openings`, `interior` and
`stairs`.

Run:

```
python tools/pilot_brownstone_rowhouse/lock_sources.py
python tools/pilot_brownstone_rowhouse/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/pilot_brownstone_rowhouse/phone_board.py --candidate <artefact dir>
```

Requires the `bpy` 4.2 module on Python 3.11.

## Version history

| version | purpose | builder result |
|---|---|---|
| v001 (720 px, 8 spp, 6 views) | first geometry check | silhouette and rhythm correct; newels collided with gate piers; furniture overexposed; roof slab edge exposed as a band |
| v002 (1440 px, 32 spp, 18 views) | full roster | fixes above verified; coplanar wall overlaps at every corner and parapet corner; cornice crown overhang overlapped the corner block |
| v003 | aborted before render completed (the cornice fix had not been applied) | superseded by v004 |
| v004 (1440 px, 32 spp, 18 views) | corner topology fix | builder pass, zero P0: cornice mitre, parapet corners and wing junction clean; 16,394 triangles, 856,808-byte GLB (sha256 a3dff60a40b70668…), aperture audit PASS, 888 s render on 4 CPU cores; independent review in `evidence/v004/independent-review.md` |

## Where the artefacts are

- `candidates/pilot-brownstone-end-rowhouse-clay-v004.glb`: the delivered model,
  kept as an ordinary Git blob because Git LFS uploads are refused from the
  cloud build environment (reads work; the batch verify call returns
  Forbidden). It is under the 1 MiB blob policy. To move it into LFS from a
  desktop clone: add a `candidates/*.glb` LFS attribute and run
  `git lfs migrate import --include="tools/pilot_brownstone_rowhouse/candidates/*.glb"`
  on this branch.
- `evidence/v004/`: build report, source entry, prework manifest, aperture
  audit, the independent review record, and sub-megabyte JPEG copies of all
  18 renders and the 4 phone boards.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as two zip archives in the session that produced them.

## Not done, by design

- Keeper approval: requires the independent holistic review in this record to
  show zero P0 and P1, and is never granted by the builder.
- Runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
  program, picker enrolment and catalogue splice.
- Human activation quote and date for publication.
- Any force-add of the `.glb` into Git LFS (`*.glb` is ignored by default).
