# Neighborhood Park LEGO skin pilot — Parisian atlas method

This revision uses the same reference/atlas split as the Parisian building
pilot. Each existing 90-degree park archetype image is treated as a hard design
reference, cropped into one rectified full-park identity atlas, and processed
locally into albedo, normal, roughness and ambient-occlusion maps. The atlas is
projected continuously across one fixed shallow LEGO park geometry.

No palette-only substitute, repeated material fragments, or image-generation
API calls are used. The compiler records the audited crop and PBR provenance in
`frontend/public/park-skins/neighborhood-park/manifest.json`.

![Four-way comparison of the Rustic Timber and Gravel, Modern Steel and Turf, Natural Meadow, and Urban Contemporary park skins](./neighborhood-park-lego-skins-comparison.png)
