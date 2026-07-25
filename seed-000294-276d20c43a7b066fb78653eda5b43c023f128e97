# LEGO Fidelity v3 Pilot

This pilot implements the first production increment from the LEGO Fidelity v3
plan. It keeps the builder deterministic, geometry-first, and archetype-driven;
the review images are Blender renders of the generated GLBs, not AI-generated
substitutes.

## Delivered

- Building Grammar schema v3 with typed facade zones, bays, openings,
  attachments, floor variants, and valid level ranges.
- Real street-facing window voids assembled from sill, head, pier, glass,
  jamb, frame, and mullion geometry. The v2 solid frame plate is gone.
- Alternating `typical_a` / `typical_b` floor modules.
- Dedicated `upper` setback and `crown` modules.
- Family-specific signature geometry:
  - timber grid with alternating planted balconies and planted timber crown;
  - white render with punched openings, alternate balconies, terrace rail, and
    framed crown loggia;
  - brick with a true curved arch, vertically aligned projecting oriels, and
    three-part cornice;
  - limestone with warm balcony frames, colonnade, and corten crown screen.
- Manifest schema v3 module identity: `(family, role, variant_key, lod)`.
- Importer dedupe/storage and frontend types preserve all floor variants.
- Assembly planner alternates repeatable variants and reserves upper/crown
  levels instead of repeating one generic floor to the roof.

## Visual review

The scores are a human design-feature rubric—massing, materials, facade rhythm,
and signature features—not pixel similarity. References and deterministic
renders have different cameras and context.

| Family | v2 | v3 | Gain |
|---|---:|---:|---:|
| Mass Timber Biophilic Infill | 82 | 89 | +7 |
| European White Render Boutique | 79 | 85 | +6 |
| Contextual Dark Brick Classical | 75 | 88 | +13 |
| Limestone Panel Contemporary Infill | 75 | 86 | +11 |

Review boards:

- `docs/lego_fidelity_v3/v3_showcase.png`
- `docs/lego_fidelity_v3/mass-timber_v3_comparison.png`
- `docs/lego_fidelity_v3/white-render_v3_comparison.png`
- `docs/lego_fidelity_v3/dark-brick_v3_comparison.png`
- `docs/lego_fidelity_v3/limestone_v3_comparison.png`

## Validation

- 4/4 assembled families pass GLB geometry and manifest validation.
- 24/24 distinct modules pass origin, extent, height, and file integrity gates.
- 32 compiler / facade graph / planner contract tests pass.
- Frontend TypeScript type-check passes.

The mass-timber assembled preview has two non-blocking performance warnings:
91,580 triangles and an 8.7 MB assembled GLB. Individual modular assets remain
well within the import cap. LOD generation and shared texture compression remain
the next performance increment.

## Reproduce

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id contemporary_midrise `
  --variant-id mass_timber_biophilic_tower `
  --output build/lego-fidelity-v3/mass-timber `
  --no-ao

python tools/archetype_compiler/create_fidelity_v3_comparisons.py
```

Omit `--no-ao` for an import-ready ambient-occlusion bake. The source renders,
GLBs, manifests, grammars, and validation reports are local build output under
`build/lego-fidelity-v3/`; the review boards are committed documentation.

## Next fidelity increment

1. Add perforated/material-specific guard generators and richer vegetation.
2. Support multi-bay facade compositions so narrow/slender targets are not
   forced into the same full-width massing.
3. Add explicit interior depth cards and emissive evening presets.
4. Generate LOD1/LOD2 modules and share texture atlases across a family.
5. Add renderer screenshots from the actual globe placement path to the visual
   regression set.
