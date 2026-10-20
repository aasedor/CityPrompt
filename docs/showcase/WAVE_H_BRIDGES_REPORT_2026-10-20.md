# Wave H: ten bridges, report, 2026-10-20

Wave H built the ten bridge options the user chose ("Let's do all 10"). They come from the six bridge
archetypes in the street catalogue:

- urban vehicular bridge;
- dedicated cycle bridge;
- urban pedestrian footbridge;
- shared cycle and pedestrian bridge;
- rail and transit viaduct;
- landscape park pedestrian bridge.

Each family locks the three views (front, oblique, top) of one catalogue variant. All work is on
branch `claude/ten-new-buildings`.

Every version followed the RLASM v6.1 process used since wave D:

- **Build:** rendered from the actual optimised GLB, 18 views at 1440 px and 32 samples.
- **Review:** reviewed by a separate agent that had not built it.
- **Evidence:** preserved as JPEG evidence in `tools/<family>/evidence/<version>/`.

Each bridge then went through the stopping rule in `docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md`.
A bridge stops at the first of these:

- the review returns PASS_ZERO_P0_P1;
- two consecutive reviews fail to lower P0 + P1;
- the same finding survives two targeted fixes.

The best-reviewed version stays the candidate, and a tie keeps the earlier version.

These are street-catalogue options, not buildings. Nothing here is enrolled, published,
runtime-integrated or keeper-approved. Each README states that nothing in the family is keeper-approved, runtime-integrated, enrolled in a catalogue or activated, and that those remain separate checkpoints for the user's decision.

## Results

Seven of the ten bridges reached PASS_ZERO_P0_P1. The other three stopped with one or three P1s open.

| bridge | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 |
|---|---|---|---|---|---|---|---|
| Riveted steel through-truss road bridge | urban_vehicular_bridge / variant_1 | `tools/clay_steel_truss_road_bridge` | **PASS_ZERO_P0_P1** at v002 | v002 | 60,842 | 3,282,652 | 0 / 0 |
| Cable-stayed circular cycle bridge | dedicated_cycle_bridge / variant_1 | `tools/clay_cable_stayed_cycle_ring` | **PASS_ZERO_P0_P1** at v003 | v003 | 35,368 | 1,941,156 | 0 / 0 |
| Swooping elevated cycle flyover | dedicated_cycle_bridge / variant_0 | `tools/clay_swooping_cycle_flyover` | **PASS_ZERO_P0_P1** at v003 | v003 | 74,996 | 3,850,284 | 0 / 0 |
| Heritage stone arch road bridge | urban_vehicular_bridge / variant_0 | `tools/clay_stone_arch_road_bridge` | **PASS_ZERO_P0_P1** at v003 | v003 | 76,684 | 3,878,388 | 0 / 0 |
| Weathering-steel truss footbridge | urban_pedestrian_footbridge / variant_0 | `tools/clay_weathering_steel_footbridge` | **PASS_ZERO_P0_P1** at v003 | v003 | 24,976 | 1,442,444 | 0 / 0 |
| Victorian brick arch rail viaduct | rail_transit_viaduct / variant_0 | `tools/clay_brick_arch_viaduct` | **PASS_ZERO_P0_P1** at v003 | v003 | 73,520 | 3,928,328 | 0 / 0 |
| Elevated riveted steel arch rail viaduct | rail_transit_viaduct / variant_2 | `tools/clay_rail_through_truss` | **PASS_ZERO_P0_P1** at v005 | v005 | 70,940 | 3,906,840 | 0 / 0 |
| Timber covered footbridge | urban_pedestrian_footbridge / variant_2 | `tools/clay_timber_covered_footbridge` | stopped: the side-wall end-bay finding survived two fixes | v002 | 29,118 | 1,664,448 | 0 / 1 |
| Tied-arch shared cycle and pedestrian bridge | shared_cycle_pedestrian_bridge / variant_1 | `tools/clay_tied_arch_shared_bridge` | stopped: the plan-skew finding survived two fixes | v003 | 21,182 | 1,296,740 | 0 / 1 |
| Planted green bridge | landscape_park_pedestrian_bridge / variant_2 | `tools/clay_planted_green_bridge` | stopped: the planting finding survived two fixes, and v003 scored worse | v002 | 50,748 | 3,481,664 | 0 / 3 |

The candidate GLB of each family is the only tracked file in its `candidates/` folder. Every
candidate is under the 4 MiB ordinary-blob cap.

**Rail viaduct name.** The family folder is still called `clay_rail_through_truss`, after the first
reading of the source. The source shows heavy, low, open-topped riveted bowstring arches on columns,
not a through truss. The title was corrected in the README; the folder name was kept so the evidence
paths stay stable.

### Trajectory (P0 / P1 per independent review)

| bridge | v001 | v002 | v003 | v004 | v005 |
|---|---|---|---|---|---|
| steel truss road bridge | 1 / 4 | **0 / 0** | | | |
| cycle ring | 1 / 5 | 0 / 3 | **0 / 0** | | |
| cycle flyover | 2 / 6 | 0 / 3 | **0 / 0** | | |
| stone arch road bridge | 1 / 10 | 0 / 4 | **0 / 0** | | |
| weathering-steel footbridge | 0 / 6 | 0 / 1 | **0 / 0** | | |
| brick arch viaduct | 0 / 8 | 0 / 2 | **0 / 0** | | |
| riveted steel arch viaduct | 0 / 5 | 0 / 2 | 0 / 1 | 1 / 1 | **0 / 0** |
| timber covered footbridge | 0 / 9 | 0 / 1 | 0 / 2 | (stopped) | |
| tied-arch shared bridge | 0 / 3 | 0 / 2 | 0 / 1 | (stopped) | |
| planted green bridge | 0 / 6 | 0 / 3 | 1 / 6 | (stopped) | |

The riveted steel arch viaduct ran two versions past its best. v004 rebuilt the bowstrings to the
source's heavy, low, open-topped form, but it rendered one camera black and left black wedges on the
new trusses. That review did not improve on v003, but it was only the first such review, so the
family continued. v005 fixed both problems and passed.

## Open findings on the candidates that did not pass

Each family README lists these under "Open blockers", and the full reviews are in
`evidence/vNNN/independent-review.md`.

### Timber covered footbridge v002 (0 / 1)

- **Survived two fixes (P1):** each side wall has four end bays louvred to full height with the
  diagonal over the louvres. The sources show the louvres stopping on the diagonal, with the
  triangle below open and the glass balustrade running through.
- **What happened after v002:** v003 fixed the bay rhythm, but its review also found the glass
  balustrade reading as a solid light-grey parapet in the elevated views. That made v003 worse than
  v002.

### Tied-arch shared bridge v003 (0 / 1)

- **Survived two fixes (P1):** the plan skew does not match the source top. The model is a
  13-degree parallelogram. The source skews about 6 degrees at the west end, and its east deck end
  runs about 6 degrees the other way along an angled landing pier.
- **Resolved along the way:** the deck ties, the fascia and quay, the deck overrun and the rear
  framing.

### Planted green bridge v002 (0 / 3)

- **Open P1s:**
  - the viewing pods are undersized and pointed;
  - the pod access spur turns the plan into a cross;
  - the beds read as boulder fields, not lush perennial planting.
- **Survived two fixes:** the planting finding. v003 replaced the boulders with mounds, lavender and
  grasses, but its review found the lavender reading as solid lilac capsules and the mounds as
  uniform gumdrops.
- **What happened in v003:** it also broke cameras and deck ends that had passed. One close-up
  camera was jammed against a mound, the front lost the water, and the deck ends stopped in mid-air
  above the bank. Its review scored 1 / 6, so v002 stays the candidate.

## What carried over between bridges

- **A black render means the camera is inside something.** The viaduct's `track_deck` view was
  inside the last train car. Check every detail camera against the geometry, not only the framing,
  whenever a model is rebuilt.
- **Short members collect coincident faces.** On the viaduct's bowstrings, the end panels next to
  each shoe were only about 0.87 m tall. That was too short for both an upper and a lower gusset, and
  the overlap rendered as black wedges. One full-height gusset per face fixed it. Coplanar faces
  remain the cause of every black patch, as in waves D to G.
- **Read the source's structural type before building.** The rail viaduct cost two versions because
  v001 to v003 modelled a tall through truss before the review established that the source shows
  low open-topped bowstrings. Name the type from the pixels, not from the archetype label.
- **Plan geometry is the hardest finding to fix by small steps.** The tied-arch skew survived two
  targeted fixes. A wrong plan angle needs the deck, piers and landings re-set out together, not
  nudged.
- **Planting needs a method, not more primitives.** The green bridge's planting moved from boulders
  to gumdrops without reading as perennials. The park memory (`docs/HIGH_QUALITY_3D_PARK_MEMORY.md`)
  and the conservatory benchmark now set the approach for later parks: arching multi-blade tufts,
  mounded drifts with flower masses, and grounded multi-lobe shrubs.
- **Size budget.** Six of the ten candidates sit between 3.2 and 4.0 MB. Smooth-shaded organic
  meshes share vertices, so they cost far less per triangle than flat-shaded ones. Use smooth
  shading for crowns, mounds and boulders before cutting detail.

## Branch hygiene

Evidence JPEGs are all under 950 KB. Only candidate GLBs are committed, as ordinary blobs under
4 MiB. Superseded candidate GLBs were removed from tracking as each new candidate replaced them.
