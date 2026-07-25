# Archetype target versus v6 model comparisons

This review applies the quality-first modular pipeline to three catalog families,
not just the Kinnaird-derived pilot. Each board compares the catalog image with a
new Cycles render and records both the matched design language and the next
typology-specific grammar gap.

## Results

| Archetype | Feature fidelity | Strongest transfer | Largest remaining gap |
|---|---:|---|---|
| Parisian limestone mansion block | 80/100 | stone palette, iron balconies, mansard, sash rhythm | corner/storefront massing and sculpted ornament |
| Nordic mass-timber mid-rise | 60/100 | timber PBR, glazing depth, inhabited interiors | exposed frame, recessed loggias and roof pavilion |
| Victorian mill conversion | 61/100 | brick PBR, steel glazing and streetwall | arched factory bays, pitched end, chimney and rooftop glass |

Scores measure coverage of architectural features, not pixel similarity. All
three assembled models and their six-module families passed automated geometry
and manifest validation. The comparison renders intentionally omit AO baking to
keep this multi-family review economical; production exports can turn it back on.

## Reproduce

```powershell
python tools/archetype_compiler/generate_family.py --archetype-id parisian_midrise_block --floors 5 --output build/lego-archetype-comparisons-v6/parisian --textures tools/archetype_compiler/textures_kinnaird_v6 --presentation-engine cycles --presentation-samples 32 --no-ao

python tools/archetype_compiler/generate_family.py --archetype-id nordic_timber_midrise --variant-id nordic_timber_mass_timber --floors 8 --output build/lego-archetype-comparisons-v6/nordic --textures tools/archetype_compiler/textures_archviz_v5 --presentation-engine cycles --presentation-samples 32 --no-ao

python tools/archetype_compiler/generate_family.py --archetype-id industrial_brick_mixed_use --variant-id industrial_brick_original_mill --floors 5 --output build/lego-archetype-comparisons-v6/industrial --textures tools/archetype_compiler/textures --presentation-engine cycles --presentation-samples 32 --no-ao

python tools/archetype_compiler/create_archetype_comparisons_v6.py
```

The review also improved the general heritage rules: cream/Lutetian limestone
now selects the premium heritage stone PBR set, carved ornament inherits the
primary stone rather than becoming a contrasting rubble material, and projecting
balconies compile into modeled stone slabs, corbels and individual iron pickets.
