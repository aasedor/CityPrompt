# Calgary side-by-side duplex pilot

One bounded exact-variant RLASM 6.1 architectural-clay build for
`calgary_modern_infill_house / infill_duplex`. It does not activate a runtime
entry or grant the detached parent a duplex programme.

The three existing variant-2 catalogue images govern the build. They show two
visible storeys, paired outer glazing stacks, central recessed independent
entries, separate flat roofs and upper cedar side bays. The catalogue prose's
three-storey/two-tone-stucco description conflicts with those pixels and is
recorded as a discrepancy. Dimensions and unseen rear/interior arrangements
are explicitly inferred.

`clay_core.py` is a preserved low-level geometry/export/reimport utility from
the reviewed infill v006 package, SHA-256
`19c432bdf42ce005a540d23776fcba1a860aa6101e3940eec8dd505f3187de33`.
Only construction utilities are reused. `build.py` authors the duplex's own
geometry and opening schedule; no building mesh or sibling composition is
copied. `proof.py` makes labelled, letterboxed comparisons without retouching
the sources or rendered images.

Use Blender 5.2 and a new external output directory for every candidate:

```powershell
& '<Blender>/blender.exe' --background --python tools/catalogue_duplex_pilot/build.py -- --source-root '<hydrated-checkout>' --output '<external-new-candidate>' --version 4 --dry-run
& '<Blender>/blender.exe' --background --python tools/catalogue_duplex_pilot/build.py -- --source-root '<hydrated-checkout>' --output '<external-new-candidate>' --version 4
python tools/catalogue_duplex_pilot/proof.py '<external-new-candidate>'
python '<rlasm-expert-skill>/scripts/validate_candidate.py' '<external-new-candidate>'
```

The build copies the exact sources and scripts into its immutable package,
writes the prework manifest before geometry, exports a texture-free GLB,
reimports that file, checks its native bounds, and renders all 13 declared
views. Replay can use a preserved candidate as `--source-root`, with its copied
build script and a new output directory. Never rerun evidence generation over
an existing candidate's boards or verification record.

Local output is under
`C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/duplex/`.
Versions 001–003 remain `visual_rework_required`. Their evidence is retained:
001 revealed overlapping entrance/floor surfaces; 002 revealed slab edges on
the facade plane; the complete independent 003 review identified omitted
near-grade glazing and a 40 mm gap beneath the central coping.

Version 004 corrects that finite list. It has two visible storeys, two independent
entrances, separate occupied interiors, physical glazing recesses and a
continuous capped party wall. The complete exported envelope measures
13.34000 × 21.47200 × 9.00000 m, including stairs, walks and roof projections.
It is one fixed native assembly. A proposed 17 × 25 m plot would leave at least
1.5 m conceptual edge clearance; this is neither a legal setback nor a completed
terrain-placement check. The model is 3,110,128 bytes with no embedded images
or textures. Its deterministic delivery checks and 13-view builder review pass.
See `candidate.json` for the separate independent decision and exact hashes.
No paid API calls are used.

Independent review and subsequent human runtime activation are separate from
the deterministic preflight. Preserve native scale, the two-home programme,
all source/review hashes, and any unresolved findings in the catalogue record.
