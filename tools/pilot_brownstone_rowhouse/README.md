# Pilot: brownstone end-of-row house (RLASM v6.1 architectural clay)

One-building pilot of the RLASM method run from a Linux cloud session, using
locked catalogue views as the only source. State: **candidate, visual rework
required** after three independent reviews (v004: 1 P0 / 8 P1; v006: 0 P0 / 3 P1;
v007: 0 P0 / 1 P1). The delivered model is `candidates/…-v007.glb`. The open P1
and the P2 list are in `evidence/v007/independent-review.md`; the next version
should rebuild the skylight glazing as one clean sloped plane within the brick
body, move the wing chimney to 43% of the width, then take the P2 list.
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
| v004 (1440 px, 32 spp, 18 views) | corner topology fix | builder pass, zero P0: cornice mitre, parapet corners and wing junction clean; 16,394 triangles, 856,808-byte GLB (sha256 a3dff60a40b70668…), aperture audit PASS, 888 s render on 4 CPU cores; independent review (separate agent, sources and renders only): **VISUAL_REWORK_REQUIRED**, 1 P0 (flank shows two window columns and no garden-level side door where the locked oblique shows three columns and a side entrance), 8 P1 (trim palette lighter than brick, roof furniture count and skylight form, open-stair stoop, undersized rear wing, window reveal seams, parapet corner slits, uncapped band ends), 9 P2; record in `evidence/v004/independent-review.md` |
| v005 (1440 px, 32 spp, 20 views) | rework from the v004 independent review: three flank columns and side entrance, two mid-depth chimneys, shed skylight, solid stoop with recessed entry, wing at 0.9 x 0.4 of the main block, measured palette, lined reveals, butted parapets, bands short of the party wall | builder: all nine P0/P1 items addressed in pixels; brick field renders 161/118/87 against the source sample 174/126/90, base and hoods darker than brick, cornice light; 19,030 triangles, 998,052-byte GLB, aperture audit PASS; one new defect, the hollow skylight's east face rendered as an open black panel |
| v006 (1440 px, 32 spp, 20 views) | solid skylight body with a dark backing plate under the glazing | independent review: **VISUAL_REWORK_REQUIRED**, 0 P0, 3 P1, 14 P2; every v004 blocker resolved or partly resolved; remaining P1: both main chimneys about 2.5 m too far back (source: 37% from the front), open end on the side-entrance step at grade, horizontal mortar grooves read as clapboard at detail scale; 19,014 triangles, 997,092-byte GLB; record in `evidence/v006/independent-review.md` |
| v007 (1440 px, 32 spp, 20 views) | main chimneys at 37% of the depth from the front, closed side-entrance step, plain brick field, darker membrane | independent review: **VISUAL_REWORK_REQUIRED**, 0 P0, 1 P1, 14 P2; prior P1s: stack depth partly resolved (main stacks correct, wing junction stack still at 57% of the width where the source shows 43%), step void resolved, grooved field resolved; remaining P1: the skylight glazing is a kinked plate overhanging its brick body and needs a single clean plane; 16,206 triangles, 845,256-byte GLB (sha256 53e8694cdcb233f5…); record in `evidence/v007/independent-review.md` |

## Where the artefacts are

- `candidates/pilot-brownstone-end-rowhouse-clay-v007.glb`: the delivered model,
  kept as an ordinary Git blob because Git LFS uploads are refused from the
  cloud build environment (reads work; the batch verify call returns
  Forbidden). It is under the 1 MiB blob policy. To move it into LFS from a
  desktop clone: add a `candidates/*.glb` LFS attribute and run
  `git lfs migrate import --include="tools/pilot_brownstone_rowhouse/candidates/*.glb"`
  on this branch.
- `evidence/v004/`, `evidence/v006/`, `evidence/v007/`: build report, source
  entry, prework manifest, aperture audit, the independent review record for
  that version, and sub-megabyte JPEG copies of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as two zip archives in the session that produced them.

## Not done, by design

- Keeper approval: requires the independent holistic review in this record to
  show zero P0 and P1, and is never granted by the builder.
- Runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
  program, picker enrolment and catalogue splice.
- Human activation quote and date for publication.
- Any force-add of the `.glb` into Git LFS (`*.glb` is ignored by default).
