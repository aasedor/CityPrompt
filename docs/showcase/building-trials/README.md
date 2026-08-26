# Building trial renders

This folder separates direct 3D-model evidence from AI-enhanced presentation
concepts.

## Native 3D evidence

The files under [`native-3d/`](native-3d/) are direct raster renders of the
actual models. They are suitable for checking massing, openings, materials,
secondary elevations, and overall model completeness.

- [`cityprompt-native-3d-comparison-v1.png`](native-3d/cityprompt-native-3d-comparison-v1.png)
- [`brick-bronze-wave003-native-front-left.png`](native-3d/brick-bronze-wave003-native-front-left.png)
- [`restored-kyoto-machiya-native-front-corner.png`](native-3d/restored-kyoto-machiya-native-front-corner.png)
- [`restored-kyoto-machiya-native-rear-corner.png`](native-3d/restored-kyoto-machiya-native-rear-corner.png)
- [`art-deco-cream-terracotta-tower-native-front-corner.png`](native-3d/art-deco-cream-terracotta-tower-native-front-corner.png)
- [`passive-house-timber-block-native-front-corner.png`](native-3d/passive-house-timber-block-native-front-corner.png)
- [`modern-fire-station-mass-timber-native-front-corner.png`](native-3d/modern-fire-station-mass-timber-native-front-corner.png)

### Brick & Bronze size-variant pilot

[`brick-bronze-size-variants/`](native-3d/brick-bronze-size-variants/) contains
three newly generated members of the same semantic building family:

- small rectangle: 18×14 m, 4 floors;
- large rectangle: 40×25 m, 8 floors;
- native-height rear-left L: 25×25 m, 6 floors.

Each variant has a direct material render and a temporary-material geometry
proof. The comparison sheet includes the earlier 25×18 m native building as a
baseline. All seven PNGs are direct Blender 5.2 outputs or a deterministic
layout of those outputs; no AI image generation or enhancement was used.

- [`brick-bronze-size-variant-comparison-v3.png`](native-3d/brick-bronze-size-variants/brick-bronze-size-variant-comparison-v3.png)
- [`manifest.json`](native-3d/brick-bronze-size-variants/manifest.json)

[`comparison-manifest.json`](native-3d/comparison-manifest.json) records the
source render and assembled-model hashes used by the comparison sheet. The
sheet's `hard gates clear` note means the current assessor found zero hard
failures; it does not mean the families have completed the current human and
certification-evidence review gate.

The Brick & Bronze image is a development render. Its scene is complete and
renderable, but its strict fixture audit still records an exterior-bounds
tolerance mismatch.

## AI-enhanced presentation concepts

The two `*-presentation-v1.png` files in this folder were generated from the
native renders to demonstrate downstream image-refinement potential. They are
not geometry evidence and may contain AI-refined architectural details.
