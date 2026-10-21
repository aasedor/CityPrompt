# Planting kit showcase (kit showcase, not a catalogue candidate)

> **This is not a catalogue candidate.** It has no locked sources and no `sources.json`, and it maps to no
> catalogue archetype or variant. Nothing here is keeper-approved, runtime-integrated, enrolled in a catalogue,
> seeded or activated. The family exists so that the shared planting kit can be reviewed once, at eye level,
> before park families reuse it.

## Why the kit exists

The wave H and wave I park families stopped on close-up planting:

- **Green bridge:** boulders, then gumdrops and lilac capsules.
- **Halifax Public Gardens:** faceted gem heads.
- **Prince's Island Park:** cone heads, flat straw ribbons and bare fill between the mounds.

The kit replaces those per-family primitives with one shared vocabulary that follows
`docs/HIGH_QUALITY_3D_PARK_MEMORY.md`, which sets the conservatory benchmark: a legible plan, controlled richness
and grounded, complete 3D at pedestrian height.

## The kit chunk

The kit is a shared helper chunk, `plantkit.py`. Assemble a park module like this, with the kit after `gcommon.py`:

```
cat <key>_head.py common.py gcommon.py plantkit.py <key>_body.py > tools/<family>/<module>.py
```

The chunk starts at the line `# ---- shared planting kit` in `family_plantkit.py`. That copy is the reference text:
keep every family's copy identical to it.

These rules apply to every builder:

- **Grounded:** every plant base and every carpet edge sits `PK_SINK` (2.5 cm) below the soil top. The flat caps are
  buried.
- **Shading:** curved surfaces are smooth-shaded. Buried caps are flat-shaded.
- **No coplanar faces:** lobes interpenetrate; adjacent bedding bands meet at a lapped clipped step (the lower band
  runs 5 cm under the higher, which is at least 1.5 cm taller), never on a shared plane and never in a soil valley.
- **No ridged noise:** every displaced surface uses soft signed noise, so nothing reads as creased, spurred or
  crumpled (the v001 shrub, hydrangea, yarrow and carpet failures all came from `abs(noise)`).
- **Clearance rule (kit-wide):** `kit.fits()` / `kit.place_in()` keep every plant's buried base `PK_CLEAR` (5 cm)
  inside each registered bed edge and off every obstacle; only canopy above kerb height may overhang a kerb, and an
  obstacle taller than 0.3 m (a rail, a wall) keeps the whole canopy clear. Pots (protos with `rim_r`) must stay their
  two rims plus 3 cm apart.
- **Shell audit (kit-wide):** carpets, bands, groundcover and climber carriers are registered shells
  (`pk_mesh(..., shell=True)`); faces of two different shells whose centroids lie within 2 mm with opposing
  (dot < -0.5) or coincident (dot > 0.9) normals are counted, the black-slit and z-fighting signature.
  `kit.audit()` counts clearance, pot and shell violations together; the showcase build fails unless it is 0.
- **Leaf shading (v003):** canopy leaves are curved, tapered ovate cards (`_pk_ovate`, 6 vertices, 4 triangles) whose
  custom normals lean about 70% toward the canopy normal, so a mass of leaves shades as one soft canopy instead of a
  heap of chips. A role that carries custom normals is stored as triangles wound to face their normals (Cycles renders
  a back-facing leaf black), which the build's triangulate pass and the glTF round trip keep exactly.

### API

**Setup and placement**

| function | what it does |
|---|---|
| `pk_palette(PALETTE)` | Adds the kit roles (`pk_leaf`, `pk_pink`, `pk_groundcover`, `pk_shrub_core`, and so on) without overriding any role the family already defines. |
| `kit = PlantKit(module, instancing=True)` | Creates the prototype registry. Each proto records `base_r` (buried footprint below kerb height), `canopy_r` and `height`. |
| `pk_bed(..., kit=kit)` / `kit.register_bed(region)` | Registers a plantable region (bed minus kerb) for the clearance rule. |
| `kit.add_obstacle(geom, top)` | Registers a rail, wall or post footprint and its height above the soil. |
| `kit.place_in(proto, x, y, z, rot, s, region=, aspect=, lean=)` | Places a prototype only if it passes the clearance rule (trying 1.0, 0.85 and 0.72 x s), else skips it. |
| `kit.place(proto, x, y, z, rot, s, sz=, sy=, lean=)` | Places without checking: non-uniform scale and a small lean, as linked instances or merged per role. |
| `kit.place(..., track=False)` | Places a climber part (spray, trailing cane) that belongs on its wall and is not audited as a ground plant. |
| `kit.audit(detail=False)` | Counts (or lists) clearance, pot-overlap and shell-face violations. |
| `kit.flush()` / `kit.stats()` | Merges batches and records counts, violations and rejections. |

**Prototype plants** (each returns a proto to place)

- **`flower_head_cluster(kit, name, head=..., leaf_w=, leaves=)`**: a leafy mound (a small hidden core, keeled leaves
  arching to a basal skirt; `leaf_w` 0.5 lanceolate, 0.3 divided) with stems carrying smooth heads. `head` is one of:
  - `'daisy'`: a scalloped, drooping ray disc round a boss (coneflower, rudbeckia);
  - `'spike'`: a tapered core packed with floret whorls (salvia, veronica);
  - `'umbel'`: a flat-topped corymb of small smooth floret domes (yarrow, sedum);
  - `'cup'`: a bowl of four broad petals round a dark boss (poppy, tulip);
  - `'panicle'`: an open branched raceme: a nodding rachis, 9-13 side branches shortening to the tip, tiny floret
    specks with air between them (astilbe, panicle hydrangea, phlox); cream and pink (astilbe) in the showcase;
  - `'mophead'`: hydrangea heads of smooth floret-cluster domes seated into and collared by the leaves of the plant's
    own broad, low domed body (3-4 lobes round a centre, h:w about 0.75) of large ovate leaves that splay and droop to
    the soil at the skirt.
- **`lavender(kit, name, ...)`**: no dome: 40-48 short leafy stems of grey-sage needle leaves (custom normals leaning
  to a low hemisphere, soil showing at the edge) under a vase-shaped fan of flower stems within about 25 degrees of
  vertical, each a spike of 6-8 tiny paired whorls tapering to the tip (lavender, catmint, perovskia); use two seeds.
- **`arching_grass(kit, name, ..., plumes=, plume_height=)`**: keeled blades arching from a low crown; optional plumes
  are a slim spindle wrapped in hair-fine spikelets on a nodding rachis.
- **`shrub_mass(kit, name, radius, height, lobes=, ...)`**: structure first. An irregular multi-lobe hull
  (`_pk_shrub_hull`: flattened lobes in a ring with two adjacent slots left empty for a deep bay, lower lobes reaching
  out and upper ones drawn in, an uneven crown of off-centre lobes at different heights) in mid-dark green, lifted on
  visible stems, clothed by `_pk_canopy` in an inner layer of large dark leaves lying flat on it (a third of the
  leaves) and an outer layer of ovate leaves lifting 15-35 degrees, a sixth of them in threes on twig sprigs that break
  the outline. Use 0.4, 0.8, 1.2 and 1.6 m sizes with h:w about 0.7-0.8; repeats come from spin, lean and
  non-uniform scale.
- **`bedding_cushion(kit, name, kind='begonia'|'ageratum'|'alyssum', ...)`**: a broad lumpy mound (6-8 low sub-mounds,
  h:w about 0.25-0.35) clothed in 3-5 cm ovate leaves with flower clusters over 40-70% of its top: bead clusters,
  fuzzy puffs or a white froth. Cushions placed closer than their diameter merge into a band.
- **`pot_plant(kit, name, plant='geranium'|'box'|None)`**: a terracotta pot with a rolled rim and a soil top, holding
  a geranium, a leaf-skinned box ball, or nothing (the root pot of a climber). The proto records `rim_r` for the pot
  audit.
- **`climber_sprays(kit, name, leaf_role, bract_roles)`**: the instanced climber parts: a leafy spray (5-6 short
  arching stems, about 60 ovate leaves), two flowering sprays (16-20 three-bract clusters held above the leaves, one
  bract tone each) and two trailing canes (0.65 and 1.0 m, leafy, with bract triads along the lower half).

**Beds, carpets and drapes** (unique geometry, merged)

- **`pk_bed(name, outline, soil_z, kerb=..., kit=)`**: a granite kerb ring and a mulch surface.
- **`groundcover(name, poly, z, kerb=..., dots=, grain=)`**: a softly cushioned carpet lapped 1.5 cm under the kerb,
  its rim held below the kerb's inner arris by an 8 cm shoulder (an outline ring and a shoulder ring, no teeth);
  optional micro-floret and leaf-grain specks.
- **`carpet_bands(name, outline, z, bands, kerb=...)`**: the Halifax module: flat clipped bands (bump <= 4 mm,
  near-vertical 2.5 cm shoulder) following the outline, with automatic laps and height steps and micro-florets
  (`pk_dots`, 100-300 per m2, two hue roles). `bedding_band(...)` builds one band.
- **`wall_drape(name, p0, p1, out, profile, curtain, kit, sprays, openings=, trunks=, floor=, spacing=)`**: a
  wall-trained climber or parapet cascade (bougainvillea). A thin hidden carrier sheet in mid-dark green (the only
  closed shell, its edges diving into the masonry) gives depth; the visible canopy is instanced sprays oriented to the
  carrier normal (flowering where a blob mask covers about 65%), trailing canes from the hanging edge kept clear of the
  openings and above `floor`, and a woody armature of canes fanning from each trunk over the wall and coping. Openings
  are cut with a 7 cm margin and spray centres stay 17 cm clear of them.

**Placement and outlines**

- **`perennial_drift(kit, poly, z, mix, kerb=..., underlay='pk_groundcover')`**: assigns Poisson-spaced plants to
  species by low-frequency noise fields, so species form interlocking drifts. Every plant passes the clearance rule
  with its own base radius and gets a non-uniform scale and a small lean; a groundcover underlay hides the fill by
  default.
- **`pk_scatter`, `pk_dots`, `pk_ellipse`, `pk_leaf`, `pk_blob`, `pk_rounded_rect`, `pk_region`**: scatter, specks,
  bed outlines and the plantable region inside a kerb.

## Instancing and how to adopt it

### Findings

**glTF instancing survives export and reimport.** In Blender 4.2.0, linked duplicates export as one mesh with many
nodes, and reimport gives one mesh datablock.

| experiment | joined | instanced |
|---|---|---|
| 200 copies of a 2,048-triangle plant | 9,908,488 B | 79,556 B |

**`clay_core.deliver()` joins every object per role,** which would turn instances back into geometry. This family's
`build.py` therefore adds two family-local shims; `clay_core` itself is not edited:

- `keep_instances()` renames each instance's role to `<role>_instanced`, so the join loop skips it. The true role is
  kept in `cityprompt_base_role` and on the shared material.
- The triangulate pass runs once per shared mesh.

Everything else in `deliver()` runs unchanged: bounds, the carrier aperture audit, the GLB round trip, the renders
and `build-report.json`.

### Measured on the showcase

v003 smoke build at 480 px and 8 samples: 337 placements (plants and climber parts) from 31 prototypes on 629
instance nodes, plus the unique carpets, kerbs, plaza walls, climber carriers and canes.

| | v003 (instanced) | v002 (instanced) | v001 (instanced) |
|---|---|---|---|
| Showcase GLB | 4,100,404 B (94 KB under the 4,194,304 B cap) | 3,931,904 B | 3,338,232 B |
| Stored triangles | 125,828 | 134,728 | 143,020 |
| Scene (rendered) triangles | 603,625 | 587,044 | 667,084 |
| Prototype triangles | 86,683 | 83,536 | 68,832 |
| glTF JSON (mostly instance nodes) | 498,660 B | 347,236 B | |
| Clearance, pot and shell violations | 0 | 0 (clearance only) | not measured |

v003 byte split (mesh buffers): shrubs (4 prototypes) about 800 KB, kerbs, soil and groundcover about 400 KB, B6 and B7
carpet bands about 540 KB, lavender (2 seeds) 212 KB, hydrangea 152 KB, cushions 269 KB, other perennials and grasses
about 1.1 MB, climber sprays and canes 63 KB plus 99 KB of unique carrier and armature. Custom-normal leaves cost about
42 B per triangle (156 B per leaf).

For v001, the same scene joined (`--no-instancing`) came to 15,861,936 B, and each further instanced plant costs
about 1.9 KB (3.1 nodes at about 615 B each, mostly glTF extras). The build passes `build_valid` with
`PASS_CARRIER_APERTURES` and a round-trip delta of 0.0.

### Rules for park families

- Instance every prototype plant.
- Merge anything under about 20 triangles per role, such as dots and florets, because a node costs more than its
  geometry.
- Budget the carpets: they are unique geometry and, with the kerbs, they are most of the non-plant bytes. Carpets
  under plants can use `grid=.22`; leaf-card skins cost about 100 B per leaf, specks about 110 B each.
- Register every bed with `kit=` and every rail or wall with `kit.add_obstacle()`, place with `place_in()` or
  `perennial_drift()`, and fail the build unless `kit.audit()` is 0.
- Copy `keep_instances()` and the dedupe of the triangulate loop into the family `build.py`. A one-line change to
  `clay_core.deliver()`, skipping `rlasm_instance` objects in the join, would remove the need for the shim. That is a
  separate decision.

## Running it

```
python tools/clay_planting_kit_showcase/build.py --version 3 --output <dir> --resolution 480 --samples 8
python tools/clay_planting_kit_showcase/build.py --version 3 --output <dir2> --cameras front_corner --no-instancing   # size comparison
python tools/clay_planting_kit_showcase/phone_board.py --candidate <dir>
```

The build writes `evidence/planting-kit-size.json`, with the GLB bytes, stored and scene triangles, nodes, plants and
prototype triangles, clearance violations and rejected placements.

## Layout and cameras

There are nine kerbed beds and a paved plaza corner on a 41 × 22 m lawn with two gravel walks:

- **South row (y = -6.5):** B1 specimens of every head type (mophead, coneflower, rudbeckia, salvia, yarrow in two
  colours, cream panicle, pink astilbe, lavender) over an underlay; B2 perennial drift; B3 arching grasses; B4 shrub
  size range (0.4, 0.8, 1.2 and 1.6 m); B9 green-bridge strip (two lavender seeds at knitting spacing, poppies,
  fountain grass and small shrubs held clear of a railing by the clearance rule).
- **Middle row (y = +1):** B5 groundcover with florets and leaf grain; B6 clipped bedding rings with bedding cushions
  round a salvia; B7 the Halifax-style leaf carpet bed (flat clipped silver, begonia, ageratum and pink bands with
  micro-florets round white hydrangeas).
- **North (y = +8):** B8 the Prince's-Island-style perennial bed: a layered shrub backdrop at 1.3 m spacing, drifts of
  perennials, cream panicles, pink astilbe and grasses over a groundcover.
- **East (x = +17 to +26):** B10 the stepped-plaza corner: a 3 m rendered wall with a door and a window carrying a
  bougainvillea trained from a pot up and over its coping, a 1.1 m terrace wall with a parapet cascade, and geranium and
  box pots placed clear of each other (pot audit).

There are fifteen cameras:

- `front_corner`: an elevated oblique of the whole showcase;
- `top`;
- `eye_flower_heads`, `eye_specimen_close` (1.5 m, close on the hydrangea, yarrow and panicle), `eye_perennial_drift`,
  `eye_arching_grass`, `eye_shrub_mass`, `eye_lavender_rail`, `eye_groundcover`, `eye_bedding_band`, `eye_carpet_bed`,
  `eye_perennial_bed`, `eye_b8_rear` (looking south at the backdrop shrubs and the rear kerb), `eye_climber_wall` and
  `eye_cascade_pots`, all at 1.5-1.6 m.

## Version history

- **v001:** independent review FAIL, P0 = 0, P1 = 6, P2 = 9 (`evidence/v001/independent-review.md`): crumpled shrub
  masses, puffy carpet tubes with saw-tooth crests and mulch valleys, crumpled hydrangea heads, jagged yarrow plates,
  faceted feather-reed pods, and a placement rule that let a shrub cut its kerb.
- **v002:** independent review FAIL, P0 = 1, P1 = 7, P2 = 12 (`evidence/v002/independent-review.md`): carpets,
  yarrow, plumes and clearance fixed; shrubs as topiary balls of flat chips over a near-black hull, hydrangea body a
  drum, bougainvillea as a quilt with pink balloons and black slits (P0), panicle cones, sea-urchin lavender, gumdrop
  cushions and intersecting pots.
- **v003 (this module, the candidate):** independent review FAIL, P0 = 0, P1 = 2, P2 = 12
  (`evidence/v003/independent-review.md`). Fixed: the bougainvillea now reads as a flowering climber with no balloons
  or black slits, and the panicle, lavender, cushions, pot clash and hydrangea silhouette are fixed. Open: (1) the
  smooth shrub hull still shows between large flat leaves, so shrubs, the hydrangea body and the begonia cushion read
  as leaf-pasted lumps at 3-5 m; (2) three shrub canopies cross their kerbs, because the clearance audit measures a
  smaller footprint than the delivered canopy. The shrub finding survived two targeted fixes (v002, v003), so the
  stopping rule stops the kit at v003. The reviewer judged that v003 would close the stopped planting findings of
  Prince's Island Park, the Halifax Public Gardens and the stepped terraced plaza, but not the planted green bridge.

## Open points

State: **stopped at v003 by the stopping rule (the shrub finding survived two targeted fixes); v003 is the
candidate**. Nothing here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated.

- P1 #1 (v003): shrub hulls show between the leaf cards; shrubs read as leaf-pasted lumps rather than loose foliage.
- P1 #2 (v003): the clearance audit uses a smaller footprint than the delivered canopy, so three canopies overrun
  their kerbs although the build reports 0 violations. Fix: measure clearance from the instanced canopy's actual
  plan extent.
- The GLB has about 94 KB of headroom under the cap, and the glTF JSON (instance nodes, about 760 B each with extras)
  is 499 KB; a park family must budget its own carpets, drapes and node count.
- Instances are glTF node instances, not `EXT_mesh_gpu_instancing`; a runtime loader should batch shared meshes.
