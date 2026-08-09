# Three New Archetypes — V85 Review

This bounded batch applies the image-lock, fixed medium-detail, facade-sheet,
layered-glass and baked-PBR pipeline to three catalogue archetypes that had no
prior generated pilot artifacts.

## Results

| Building | Human status | Geometry | Surface/export | Main finding |
|---|---|---|---|---|
| Classic Brownstone Streetwall | Keeper candidate | Pass; 32,276 assembled triangles | Pass; 96.91% foreground parity | Three physical stoops, party walls, chimneys and carved trim preserve the row identity. A pale baked roof map was required to match the aerial evidence. |
| Blue Curtain-Wall Office | Conditional pilot | Pass; 25,104 assembled triangles | Pass; 99.70% foreground parity | Layered glazing and occupied depth avoid plastic glass, but the existing rectified sheet overstates the opaque metal-panel zone. |
| Nordic Mass-Timber Mid-Rise | Keeper candidate | Pass; 24,464 assembled triangles | Pass; 99.83% foreground parity | Expressed glulam, recessed loggias, larch, sedum terrace and pavilion read clearly after redundant projecting frames were removed. |

The office has 14 delivery warnings in its modular set and the Nordic building
has seven, primarily material-count and high-detail module warnings. Their
assembled delivery models remain 4.11 MB and 5.03 MB respectively. These are
optimization tasks after visual approval, not reasons to conceal the current
comparison result.

## Review boards

- `01-archetype-comparison-v85.png` — exact catalogue image, generated identity
  view and close facade audit.
- `02-roof-comparison-v85.png` — exact angle-90 evidence, generated roof audit
  and aerial silhouette.
- `03-neutral-glb-parity-v85.png` — source Blender render, re-imported GLB and
  foreground-only difference heat map.

`review-summary.json` contains the machine-readable validation, warning,
triangle, size, parity and human-status results.

## Next correction

Create a variant-native curtain-wall facade sheet in which the upper frontage
is predominantly blue glass with only the solid zones visible in the exact
three-image set. Keep the current layered glass, lobby depth, roof screen and
exported PBR path as the controlled baseline.
