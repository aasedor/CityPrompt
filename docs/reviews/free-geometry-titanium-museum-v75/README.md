# Titanium Museum v75 - bounded free-geometry pilot

![Archetype, SAM v74 and free-geometry v75 comparison](01-reference-comparison.png)

![MoGe-2 and Depth Anything 3 geometry evidence](02-geometry-evidence-board.png)

## Outcome

This pilot proves a useful, zero-API-cost alternative to the SAM 3D reference
pass. MoGe-2 supplies sharp street-view depth and normals; Depth Anything 3
supplies three-view depth and confidence. OpenCV aligns the predictions,
measures disagreement and produces an uncertainty map. The learned meshes are
evidence only: the shipped model remains deterministic, authored Blender
geometry with 21,052 assembled triangles.

The evidence improved the parts it could see reliably. The v75 model has a
physically open silver screen instead of an opaque ribbon, visible separation
between screen and inner masses, a curved tapered gallery shell, and a genuine
cantilever soffit. These changes give the sides substantially more depth.

The automatic evidence status is `review`, not accepted. Valid street coverage
is `0.996` and roof confidence passes, but median MoGe/DA3 disagreement is
`0.076`, above the strict `0.060` gate. Human review therefore applied only
constraints shared by the models and visible in the references. Reflective
screen depth, glazing, vegetation and hidden sides were withheld.

## Comparison result

The camera-locked contract remains a narrow failure. Street silhouette IoU is
`0.657` and roof-plan IoU is `0.902`; street aspect error is `0.453`, missing the
`0.450` gate by `0.003`. SAM v74 scores `0.674`, `0.912` and `0.427`
respectively. The metrics see outer silhouettes only, so they under-report the
v75 improvement in screen porosity, shadow transmission and side depth.

Visual review also prevents a false success: v75 still models the roof as
separate recessed pod wells. The archetype instead reads as interconnected
curvilinear walls, roof courts, folds and terraces. Bright titanium response,
glazing depth and warm occupied interiors are also underdeveloped.

## Pipeline decision

Keep this evidence pass as an optional review stage for difficult non-boxy
archetypes. It is most useful for visible curvature, overhang position, layer
separation, pod hierarchy and multi-view roof elevation zones. It must continue
to expose uncertainty and must not convert proxy geometry directly into the
LEGO catalogue mesh.

The next bounded pilot should add a connected curvilinear roof-wall kit before
more model inference. After that, calibrate bright titanium, deeper glazing and
interior lighting. Those are now higher-value improvements than another depth
model.

## Reproduction

- Runner: `tools/archetype_compiler/run_free_geometry_museum_v75.py`
- Evidence translator: `tools/archetype_compiler/archetype_geometry_pass.py`
- Pilot compiler: `tools/archetype_compiler/create_free_geometry_museum_v75_pilot.py`
- Comparison publisher: `tools/archetype_compiler/create_free_geometry_museum_v75_comparison.py`
- Model IDs: `Ruicheng/moge-2-vits-normal` and `depth-anything/DA3-BASE`
- Inputs: exactly three catalogue views; CUDA inference is local and incurs no API charge

Full proxy meshes, model weights, `.blend` files, GLBs and unreviewed renders
remain ignored under `artifacts/archetype-geometry-pass-v75/`.
