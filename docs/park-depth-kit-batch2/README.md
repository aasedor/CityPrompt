# Park depth kit batch 2

Status: **staging only — not integrated into the live viewer**.

This bounded batch adds three deliberately different park programs after the
inclusive-playground pilot passed visual review. Each GLB is metric, has its
ground-contact origin at `z=0`, and excludes the ground surface supplied by the
AI drape.

![Archetype comparison](batch2_archetype_comparison.png)

| Kit | Catalogue reference | Surface contract | Footprint | Triangles | GLB size |
| --- | --- | --- | ---: | ---: | ---: |
| Inclusive accessible playground | `inclusive_playground_v0` — base, 60°, 90° | Program overlay; drape supplies poured-rubber ground | 50 × 40 m | 3,324 | 178 KB |
| Community garden / allotments | `community_garden_v0` — base, 60°, 90° | Depth only; drape supplies gravel, meadow and crop texture | 50 × 50 m | 6,764 | 482 KB |
| Splash pad / water play | `splash_pad_area_v1` — base, 60°, 90° | Depth only; drape supplies colored wet deck and water appearance | 30 × 25 m | 5,396 | 326 KB |

## QA views

### Inclusive accessible playground

- [Overview](inclusive_playground_overview.png)
- [Top / mask fit](inclusive_playground_top.png)
- [Ramp and tower detail](inclusive_playground_detail.png)

The depth kit contains the accessible ramp network, twin roofed towers, slides,
adaptive swings, wheelchair spinner, sensory panels, shade canopies and benches.

### Community garden / allotments

- [Overview](community_garden_overview.png)
- [Top / mask fit](community_garden_top.png)
- [Greenhouse detail](community_garden_detail.png)

The depth kit contains twenty raised beds, low-poly crop clusters, trellises, a
timber-and-glass greenhouse, split-rail perimeter fence, compost bins, rain
barrel and boulder benches.

### Splash pad / water play

- [Overview](splash_pad_area_overview.png)
- [Top / mask fit](splash_pad_area_top.png)
- [Tipping-bucket detail](splash_pad_area_detail.png)

The runtime depth kit contains dry fixtures only: tipping-bucket tower, spray
arch, curved shower arm, mushroom sprayers, ground nozzles and benches. The pale
blue water lines in the QA renders are preview-only and are not exported to the
GLB.

## Staged assets

- [`inclusive-playground-v0-depth-kit.glb`](../../assets/park-depth-kits/staging-batch2/inclusive-playground-v0-depth-kit.glb)
- [`community-garden-v0-depth-kit.glb`](../../assets/park-depth-kits/staging-batch2/community-garden-v0-depth-kit.glb)
- [`splash-pad-area-v1-depth-kit.glb`](../../assets/park-depth-kits/staging-batch2/splash-pad-area-v1-depth-kit.glb)
- [Machine-readable asset manifest](../../assets/park-depth-kits/staging-batch2/manifest.json)
- [Catalogue-reference and drape contract](../../tools/park_asset_compiler/park_depth_batch2_reference_spec.json)

## Pilot gate

Pilot one kit at a time against its actual CityPrompt mask before viewer
registration. Confirm center, rotation, fixed footprint, shared `0.32 m` drape
elevation, terrain seating, shadow/material response, and mobile/desktop LOD.
Do not integrate this batch wholesale.
