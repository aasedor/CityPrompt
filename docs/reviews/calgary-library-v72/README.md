# Calgary catalogue library pilot v72

This finite pilot tests a building whose exact catalogue images stress two weaknesses not covered by the Alpine rollout: a landmark entrance that is a deep curved section rather than facade ornament, and a roof composition whose central court and equipment must match aerial evidence.

The selected UI images conflict with the prose metadata for the real Calgary New Central Library. V72 records that conflict and treats the exact selected street, 60-degree and 90-degree images as the variant construction contract.

## Result

- Structural validation: pass; assembled landmark graph is 76.0 x 63.8 x 24.48 m and 17,848 triangles.
- Street identity gate: pass; silhouette IoU 0.706, roofline RMSE 0.150, aspect error 0.501.
- Roof-court gate: pass after one evidence-led plan correction; IoU 0.813, roofline RMSE 0.106, aspect error 0.013.
- Production preflight: pass with exact variant and three reference roles.

The street aspect threshold remains deliberately visible at 0.51. This is the weakest metric and the next camera-calibration target; it should not be mistaken for survey-grade reconstruction.

## Method changes

1. `timber_arch_shell` creates independent front/back power-curve sections, a real flare, nested laminated ribs and a recessed glazed back plane.
2. The roof is four perimeter wings around a physical court, with a raised pavilion, skylights, plant and a secondary rear timber shell.
3. Presentation cameras accept a variant-level distance/obliqueness contract.
4. A context-free `roof_audit` render makes plan occupancy machine-measurable.
5. `building-reference-evidence@2` requires every named view to pass; a good hero view cannot average away a failed roof.
6. Plaza/apron geometry stays outside the exported building envelope and belongs to placement/public-realm context.

## Research scan and optional future accelerators

The no-install pipeline remains deterministic OpenCV plus Blender. Recent primary-source work suggests four optional offline helpers for a future phase:

- [VGGT](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) can initialize cameras, point maps and depth from one or many views; use it to reduce manual camera matching, not to replace the semantic graph.
- [MASt3R-SLAM](https://openaccess.thecvf.com/content/CVPR2025/html/Murai_MASt3R-SLAM_Real-Time_Dense_SLAM_with_3D_Reconstruction_Priors_CVPR_2025_paper.html) or [DUSt3R](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_DUSt3R_Geometric_3D_Vision_Made_Easy_CVPR_2024_paper.html) can provide multi-view geometric priors when the catalogue has compatible views.
- [SAM 2](https://ai.meta.com/research/publications/sam-2-segment-anything-in-images-and-videos/) can produce promptable masks for portals, roof courts, pavilions and equipment before human audit.
- [Depth Anything V2](https://papers.nips.cc/paper_files/paper/2024/hash/26cfdcd8fe6fd75cc53e92963a656c58-Abstract-Conference.html) can add a monocular depth prior for front/side layer ordering.
- [Semantic Line Combination Detector](https://openaccess.thecvf.com/content/CVPR2024/html/Ko_Semantic_Line_Combination_Detector_CVPR_2024_paper.html) can improve vanishing-point and principal-edge estimation for rectification.
- [BuildingGPT](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_BuildingGPT_Auto-Regressive_Building_Wireframe_Reconstruction_Model_with_Reinforcement_Learning_CVPR_2026_paper.html) is the most directly relevant recent building-specific direction: point-cloud-to-wireframe sequence prediction. It is a future experiment once a trustworthy multi-view point cloud exists, not a reason to replace the current deterministic Blender graph today.

The immediate next improvement is a landmark-coordinate gate: normalize portal spring points/apex, corner piers, court corners and roof-pavilion bounds in every compatible view, then compare those features in addition to outer silhouettes.

## Reproducible source

- Registry: `tools/archetype_compiler/worldclass_calgary_library_v72.json`
- Exact signature: `library_original_snohetta` in `architectural_signature_profiles.json`
- Facade source and prompt: `tools/archetype_compiler/facade_sources_v72/`
- Opening and band schedules: `facade_opening_schedules_v72/` and `facade_band_schedules_v72/`
- Paired evidence contract: `reference_fidelity_contracts/calgary_library_original_v72.json`
- Board generator: `create_calgary_library_v72_comparison.py`

Full GLBs, facade-sheet derivatives, Blender file and unreviewed renders remain ignored under `artifacts/calgary-library-v72/`. Only the audited boards, report and reproducible source are promoted.
