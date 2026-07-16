# Codex LEGO Pilot

This pilot upgrades the archetype compiler from a generic box-and-window stack
to Building Grammar schema v2: a deterministic facade kit derived from the
catalogue's structured archetype data.

## What changed

- Four buildable facade systems: timber grid, punched white render, brick bays,
  and stone frame.
- Typed rules for window recess/projection, material and feature-bay frequency,
  balcony guards, planting, top bands, and entrance expression.
- Layered glazing/reveals, mullions, material bays, planted balcony modules,
  entrance modules, architectural bevels, and calibrated PBR materials.
- Three deterministic review renders per family: three-quarter, street, aerial.
- Strict planner matching: a requested archetype/variant cannot silently receive
  a module family that does not declare that id.
- Content-hashed model and thumbnail URLs so a re-import cannot show a stale
  `useGLTF` cache entry.
- Comparison-board generator with an explicit design-feature rubric.

## Pilot set

| Family | Facade system | Floors | Fidelity | Main remaining gap |
|---|---|---:|---:|---|
| Mass Timber Biophilic Infill | timber grid | 8 | 82/100 | planting and stagger pattern are schematic |
| European White Render Boutique | punched render | 6 | 79/100 | more asymmetry and finer Juliet rails |
| Contextual Dark Brick Classical | brick bays | 6 | 75/100 | true arched portal and multi-floor oriels |
| Limestone Panel Contemporary Infill | stone frame | 4 | 75/100 | crown wrap and perforated guard module |

The score is a human design-feature review (massing/floors, material/palette,
facade rhythm, signature features), not pixel similarity. Reference and pilot
images intentionally have different cameras and context.

## Review images

- `docs/lego_pilot/pilot_showcase.png`
- `docs/lego_pilot/before_after_mass_timber.png`
- `docs/lego_pilot/mass-timber_comparison.png`
- `docs/lego_pilot/white-render_comparison.png`
- `docs/lego_pilot/dark-brick_comparison.png`
- `docs/lego_pilot/limestone_comparison.png`

The generated GLBs, manifests, grammars, validation reports, and 12 source
renders are in `build/lego-pilot/pilot/` (local build output, not committed).
Every family passed `validate_outputs.py`.

## Reproduce

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id contemporary_midrise `
  --variant-id mass_timber_biophilic_tower `
  --output build/lego-pilot/pilot/mass-timber `
  --no-ao

python tools/archetype_compiler/create_pilot_comparisons.py
```

`--no-ao` was used for the rapid pilot review. Omit it for an import-ready bake.

## Recommendation

Treat 75–82/100 as a successful grammar/kit pilot, not final photorealism. The
next production increment should add alternate floor roles and authored
signature modules (oriel, true arch, perforated guard, crown), then validate in
the actual globe renderer with shadows and environment lighting enabled.

The implementation-ready roadmap is in
`docs/CODEX_LEGO_FIDELITY_V3_IMPLEMENTATION_PLAN.md`.
