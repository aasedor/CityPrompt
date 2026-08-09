# Scottish Baronial v76 - architectural evidence pilot

![Archetype, v68 and evidence-informed v76 comparison](01-v68-v76-reference-comparison.png)

![MoGe-2 and Depth Anything 3 evidence](02-geometry-evidence-board.png)

## Outcome

This bounded pilot joins the strongest part of the existing pipeline—the
gold-set fixed-identity grammar—to free local geometry evidence. MoGe-2 supplies
street depth and normals; Depth Anything 3 supplies three-view depth and
confidence; OpenCV aligns the predictions and exposes disagreement. The
learned meshes remain evidence only. The delivered candidate is deterministic,
authored Blender geometry with 148,990 assembled triangles and no API cost.

The evidence corrected a real v68 dimensional error. The inherited graph was
55 x 36 m with a 39 x 20 m court, producing a shallow perimeter and thin side
reading. V76 is 55 x 48 m with a 29 x 24 m court. It also restores side turrets,
a courtyard-facing central gable, and audited gable/turret windows. The aerial,
roof and rear views therefore read as a quadrangle rather than a decorated
street wall.

## Evidence and fidelity

The geometry evidence is coherent but remains under review: audited street
coverage is `0.925`, median MoGe/DA3 disagreement is `0.034`, and median roof
confidence is `1.120`. The profile's reviewed thresholds pass, so only shared,
visible constraints were applied.

The two-view OpenCV regression contract passes: street silhouette IoU is
`0.902`, roof-plan IoU is `0.797`, and their roofline RMSE values are `0.052`
and `0.147`. V68 street IoU was `0.891`. These numbers catch gross drift; they
are not visual approval.

Visual review keeps v76 out of catalogue gold. Its largest remaining mismatch
is now the roof and gate vocabulary, not plan depth. The archetype has dense
dormer arrays, intersecting cross-gables, varied ridges and valleys, slate
texture, chimney clusters, and a tall arched crenellated gate tower. V76 still
uses simplified roof planes and an inherited entrance assembly. The added side
turret drums also need the same granite material and opening construction as the
main elevations.

## Pipeline decision

Keep the new architectural interpretation contract as an optional stage after
gold-set grammar compilation. Every graph operation must name its evidence and
architectural rationale, pass archetype/variant/base-graph identity checks, and
remain review-only until all declared views pass visual inspection. Learned
proxy meshes are explicitly prohibited from catalogue delivery.

The next bounded improvement should be an authored Scottish Baronial roof kit:
dormer arrays, cross-gable/ridge intersections, slate roof material, chimney
clusters, and a crenellated gate-tower portal. That work has higher expected
value than running another depth model on the same three images.

## Reproduction

- Evidence runner: `tools/archetype_compiler/run_scottish_baronial_v76_evidence.py`
- Evidence translator: `tools/archetype_compiler/archetype_geometry_pass.py`
- Interpretation compiler: `tools/archetype_compiler/architectural_evidence.py`
- Reviewed profile: `tools/archetype_compiler/architectural_evidence_profiles.json`
- Pilot compiler: `tools/archetype_compiler/create_scottish_baronial_v76_pilot.py`
- Comparison publisher: `tools/archetype_compiler/create_scottish_baronial_v76_comparison.py`
- Models: `Ruicheng/moge-2-vits-normal` and `depth-anything/DA3-BASE`

Full proxy meshes, model weights, `.blend` files, GLBs and unreviewed renders
remain ignored under `artifacts/architectural-evidence-v76/`.
