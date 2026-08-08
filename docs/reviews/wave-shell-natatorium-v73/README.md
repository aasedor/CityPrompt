# Parametric Wave-Shell Natatorium pilot v73

This finite pilot applies the image-locked landmark method to a building whose identity is carried by a non-rectangular plan and a double-curved large-span roof rather than by a conventional facade stack.

## Result

- Production preflight: pass with the exact `parametric_wave_shell` variant and three compatible reference roles.
- Assembled landmark: 81.0 x 57.9 x 28.42 m and 29,184 triangles.
- Street identity gate: pass; silhouette IoU 0.850, roofline RMSE 0.057 and aspect error 0.087.
- Roof-plan gate: pass; silhouette IoU 0.675, roofline RMSE 0.073 and aspect error 0.033.
- Visual state: strong plan, shell, end-wall and structural identity; review-only for final material realism because the curtain wall remains cooler and less inhabited than the archetype source.

## Method changes

1. `wave_shell` samples a pinched plan and a two-crest longitudinal section into one closed outer skin, soffit and sealed perimeter.
2. A consolidated quilt-seam mesh follows the curved surface instead of using a texture or hundreds of detached rods.
3. `wave_end_wall` derives the glass head, perimeter arch, mullions and transoms from the same analytic section.
4. `mast_cable_array` creates bounded members between explicit 3D endpoints for masts, stays, entrance struts and cable fans.
5. Generic materials can now carry restrained transmission, IOR and clear-coat parameters, used here for the polycarbonate shell.
6. Roof audits now hide all presentation geometry—ground, roads, trees, cars and neighbouring buildings—not only context blocks.
7. The grammar accepts catalogue-authored 8-18 m civic-hall levels; the massing graph remains responsible for the exact final section.

## Honest limitations and next refinement

The silhouette scores validate outer form, not photorealism. The cool physical glass currently suppresses the warm occupied depth visible in the generated orthographic source. The next optical pass should test a registered reflected/interior albedo mixed into the physical glazing profile, then verify it under both Blender Eevee and the live City Prompt viewer without changing the accepted shell graph.

## Reproducible source

- Registry: `tools/archetype_compiler/worldclass_wave_shell_natatorium_v73.json`
- Exact signature: `parametric_wave_shell` in `architectural_signature_profiles.json`
- Orthographic source and prompt: `tools/archetype_compiler/facade_sources_v73/`
- Paired evidence contract: `reference_fidelity_contracts/wave_shell_natatorium_v73.json`
- Board generator: `create_wave_shell_natatorium_v73_comparison.py`

Full GLB modules, Blender file and unreviewed renders remain ignored under `artifacts/wave-shell-natatorium-v73/`. Only the audited boards, report and reproducible source are promoted.
