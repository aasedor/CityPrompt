# Mixed LEGO building + park pilot

This visual checkpoint tests one authored building family and one authored
park family together in City Prompt, without using the master planner.

## Families

- Building: `contemporary-midrise-brick-bronze-renderlocked-v1`
- Park: `park_memorial_garden_v0`

The building is a 32.0 x 21.8 m, six-storey family. The park uses its exact
archetype-owned skin and metric 3D depth kit; no AI drape or generic park
dressing is used.

## Validation

- Compile result: 1 building, 1 park, 0 streets
- Building assembly: 1 assembled, 0 without family, 0 skipped
- Geometry: no overlap; measured gap is approximately 4.0 m
- Render direction: preserve both family geometries and the site layout; no
  people, added buildings, roads, or generic dressing

## Images

- `comparison-mobile.png`: vertically stacked review sheet for mobile GitHub
  viewing
- `live-mixed-lego-scene.png`: live City Prompt globe viewport
- `compile-family-summary.png`: compiler summary showing both authored families
- `photorealistic-mixed-lego-result.png`: original saved render, without UI

The images are tracked with Git LFS.
