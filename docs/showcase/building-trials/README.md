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
