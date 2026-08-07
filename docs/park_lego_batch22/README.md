# Park LEGO catalogue closure — Batch 22

Batch 22 closes 30 previously unmapped variants across ten four-variant park parents:

- cemetery / memorial grounds
- courtyard plaza
- transit plaza
- amphitheater / performance space
- stormwater retention pond
- canal / waterway
- custom parks and plazas
- nature preserve
- riverfront park / beach
- street plaza / parklet

Each new selection has an explicit frontend and backend family contract, a distinct appearance-kit and planting/program identity, and a six-role PBR pack derived locally from the exact catalogue reference. The retained anchor variant in each parent keeps its reviewed family and skin. The assembly logic adapts whole program modules to the parcel rather than stretching a reference layout verbatim. People and adjacent large buildings in reference photographs are scale/context evidence only; they are not generated as park kit.

## Review assets

- `park_lego_batch22_four_variant_sheet.jpg` compares all 40 catalogue references and their six material roles.
- `city_prompt_ecological_wetland_live_trial.png` records the corrected one-park City Prompt trial beside a separately generated Parisian building.
- `city_prompt_trial_results.json` records the persisted zero-call LEGO recipe.

## Live trial finding

The first ecological-wetland render compiled correctly but exposed inherited anchor geometry: one oval basin. Visual review rejected that result. The rerun replaces the oval with a parcel-scaled treatment-cell mosaic, cross-boardwalk circulation, inlet/outlet infrastructure and wetland planting cues. The exact reference skin forms the tile-flattening polygon base, and the Google photogrammetry does not protrude through the park.

No image API, AI drape, people, embedded building, or paid generation call was used.

## Coverage checkpoint

The executable catalogue now contains 130 parents and 520 variants: 379 mapped, 141 unmapped, 83 complete parents, 47 partial parents and zero uncovered parents. The next bounded closure should prioritize the remaining city-specific garden and plaza parents, which already have one reviewed anchor each.
