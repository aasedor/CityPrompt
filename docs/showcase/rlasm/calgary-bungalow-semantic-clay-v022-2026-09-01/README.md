# Calgary bungalow semantic-clay LEGO pilot

This is a bounded RLASM v6.1 builder trial of a semantic architectural-clay
handoff for the source-locked Calgary inner-city bungalow. It tests two claims:

1. one exact building can scale through complete horizontal LEGO bays without
   stretching its openings or duplicating its entrance; and
2. a texture-free, material-zoned clay asset can give an image model enough
   geometry and semantic information to produce a credible final render.

This package is builder evidence only. It is **not** independent RLASM keeper
approval and does not publish the family into the seed/runtime catalogue.

## City Prompt runtime

![Three semantic-clay bungalow variants running in City Prompt](runtime/cityprompt-three-clay-final.png)

The local City Prompt planner selected three finite assembled assets:

| Trial | Target envelope | Selected asset | Native asset size | Runtime scale |
| --- | ---: | --- | ---: | ---: |
| Native | 12.4 x 14.2 m | `native` | 11.8 x 13.6 x 7.41 m | `[1, 1, 1]` |
| Medium | 17.2 x 14.2 m | `wide_2` | 16.6 x 13.6 x 7.41 m | `[1, 1, 1]` |
| Wide | 22.0 x 14.2 m | `wide_4` | 21.4 x 13.6 x 7.41 m | `[1, 1, 1]` |

The entrance, porch, front brick gable, dormers, chimney and four end
conditions remain fixed. Only complete 2.4 m occupied side bays are inserted.
Fractional parcel remainder stays as setback; no X/Y mesh stretch is used.

The screenshot deliberately records the current local basemap limitation:
Google Photorealistic 3D Tiles returned HTTP 400, so City Prompt retained its
elevation fallback and blank-blue background. All three GLBs loaded and were
visibly selectable; the external tile failure did not affect model placement.

## Clay inputs

| Native | Medium (+2 bays) | Wide (+4 bays) |
| --- | --- | --- |
| ![Native semantic clay](clay/01-native-clay.png) | ![Medium semantic clay](clay/02-medium-plus-2-bays-clay.png) | ![Wide semantic clay](clay/03-wide-plus-4-bays-clay.png) |

The exporter preserves the reviewed source geometry and transforms while
collapsing 21 PBR materials into eight flat roles: masonry, wall, trim, roof,
glass, timber, interior and hardware. The exported GLBs contain no image or
texture records.

| Variant | Full RLASM GLB | Semantic clay GLB | Reduction |
| --- | ---: | ---: | ---: |
| Native | 20,879,652 B | 7,858,068 B | 62.4% |
| Medium | 22,313,064 B | 9,401,408 B | 57.9% |
| Wide | 23,647,064 B | 10,816,072 B | 54.3% |
| **Three-asset total** | **66,839,780 B** | **28,075,548 B** | **58.0%** |

The reduction is meaningful but smaller than a texture-only estimate because
the source geometry still dominates these detailed building files. A future
mesh-instancing/Draco pass is a separate optimization; it should not be mixed
with this material-handoff experiment.

## Three image-model renders

| Native | Medium (+2 bays) | Wide (+4 bays) |
| --- | --- | --- |
| ![Native photoreal render](renders/01-native-photoreal.png) | ![Medium photoreal render](renders/02-medium-plus-2-bays-photoreal.png) | ![Wide photoreal render](renders/03-wide-plus-4-bays-photoreal.png) |

The three outputs used the built-in image-generation edit path with one clay
guide per call. The locked material direction was warm variegated brick, pale
mineral stucco/siding, charcoal asphalt shingles, off-white trim, cedar porch
work, neutral glazing and concrete steps. See [PROMPTS.md](PROMPTS.md) for the
final prompt set.

Builder comparison:

- All three renders preserve the one-and-a-half-storey silhouette, main roof,
  front gable, porch, chimney, dormers and entrance location.
- The native, +2-bay and +4-bay widths remain visibly distinct; the image model
  did not collapse the larger assets back to the native footprint.
- The repeated window rhythm survives well enough to validate the handoff.
  Muntin detail, planting and small trim joins remain generative interpretation,
  so the clay guide is not a substitute for independent source-locked review.
- Semantic clay is therefore a strong scalable conditioning representation:
  it keeps the expensive geometric truth while letting the image model own
  finish, weathering, planting and light. Full PBR remains the stronger source
  for deterministic real-time close-ups and final construction-detail review.

## Reproduction boundary

- Exporter: `tools/archetype_compiler/export_semantic_clay.py`
- City Prompt family: `calgary-inner-city-bungalow-semantic-clay-v022`
- Source geometry family: `calgary-inner-city-bungalow-v021-semantic-scale`
- Lifecycle: `build_valid` / `visual_review_ready`
- Required next gate: separate holistic visual review before any keeper or
  catalogue promotion
