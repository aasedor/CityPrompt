# Building trial renders

This folder separates direct 3D-model evidence from AI-enhanced presentation
concepts.

## Native 3D evidence

The files under [`native-3d/`](native-3d/) are direct raster renders of the
actual models. They are suitable for checking massing, openings, materials,
secondary elevations, and overall model completeness.

- [`brick-bronze-wave003-native-front-left.png`](native-3d/brick-bronze-wave003-native-front-left.png)
- [`restored-kyoto-machiya-native-front-corner.png`](native-3d/restored-kyoto-machiya-native-front-corner.png)
- [`restored-kyoto-machiya-native-rear-corner.png`](native-3d/restored-kyoto-machiya-native-rear-corner.png)

The Brick & Bronze image is a development render. Its scene is complete and
renderable, but its strict fixture audit still records an exterior-bounds
tolerance mismatch.

## AI-enhanced presentation concepts

The two `*-presentation-v1.png` files in this folder were generated from the
native renders to demonstrate downstream image-refinement potential. They are
not geometry evidence and may contain AI-refined architectural details.
