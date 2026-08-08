# Complete Mountain / Alpine category v71

This bounded rollout completes both Mountain / Alpine catalogue archetypes: four detached chalet variants and four mixed-use lodge variants. All eight families have exact variant provenance, three compatible reference roles, a dedicated massing graph, registered facade openings and bands, full presentation renders, structural validation and an OpenCV regression contract.

## Review boards

- `01-chalet-reference-comparison.png` compares the four detached chalet archetypes with their camera-locked Blender results.
- `02-lodge-reference-comparison.png` compares the four mixed-use lodge archetypes with their camera-locked Blender results.
- `03-roof-plan-comparison.png` compares every exact 90-degree catalogue reference with the generated aerial roof construction.
- `fidelity-summary.json` preserves the machine-readable metrics and selected comparison camera for every variant.

## Completed variants

| Family | Identity carried by | OpenCV IoU | Status |
| --- | --- | ---: | --- |
| Swiss traditional | weighted cross-gables, balconies, stone base, shingle/slab roof courses | 0.703 | pass |
| Austrian contemporary | concrete hillside plinth, dark larch shell, warm gable, zinc roof | 0.704 | pass |
| Bavarian painted | mural facade, timber oriels, flower balconies, broad clay roof | 0.777 | pass |
| Stone Berghaus | dry stone, small timber openings, dominant chimney, turf roof | 0.777 | pass |
| Ski-resort glulam | glazed two-storey hall, glulam frame, hearth spine, deep metal roof | 0.832 | pass |
| Tyrolean mixed-use | shopfront base, half timber, carved bays, balconies and dormers | 0.769 | pass |
| Stone and timber lodge | stone base, log gallery, cross-gables and entry canopy | 0.753 | pass |
| Eco-passive lodge | tall larch facade, irregular deep windows, butterfly green roof and U-shaped PV | 0.891 | pass |

The eco-passive contract uses the generated street view because it matches the authoritative front-facing catalogue camera; the other contracts use `archetype_match`. Metrics remain regression gates rather than likeness approval.

## Reproducible source

- Batch registry: `tools/archetype_compiler/worldclass_mountain_alpine_v71.json`
- Signature graphs: `tools/archetype_compiler/architectural_signature_profiles.json`
- Exact facade sources: `tools/archetype_compiler/facade_sources_v71/`
- Registered openings and band crops: `tools/archetype_compiler/facade_opening_schedules_v71/` and `facade_band_schedules_v71/`
- Fidelity contracts: `tools/archetype_compiler/reference_fidelity_contracts/*_v71.json` plus the retained Swiss v70 contract
- Board generator: `tools/archetype_compiler/create_mountain_alpine_v71_comparison.py`

Full GLBs, facade-sheet derivatives, validation reports and unreviewed render views remain ignored under `artifacts/mountain-alpine-v71/`. Only these reviewed comparison deliverables are promoted to Git.
