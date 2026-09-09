# Skyscraper architectural-clay batch

Three RLASM 6.1 candidates are complete and independently reviewed. They remain
external review deliverables; no runtime catalogue, database, or Git main
publication has been performed.

| Candidate | Final folder | Levels | Height |
| --- | --- | ---: | ---: |
| Blue glass office tower | glass-v003 | 25 | 99 m |
| Vancouver balcony/podium residential high-rise | vancouver-v004 | 16 | 58.8 m |
| Twisting glass tower with sky garden | twisted-v005 | 40 | 147.7 m |

Heights and level counts are conceptual source interpretations, not surveys.
Use fixed-native placement: reshape the plot, not the building's floors or
balconies. Engineering, simplified planting and interiors remain conceptual.

## Deliverables and validation

External root: `C:/dev-artifacts/CityPrompt/skyscraper-trio-2026-09-08`.
Each final folder contains the GLB, authoring scene, exact source images and
hashes, build scripts, full-resolution views, phone comparison boards,
deterministic delivery verification and independent review JSON/Markdown.

All three pass delivery verification and independent architectural-clay review
with zero unresolved P0/P1 findings. Proof views were rendered from the actual
reimported GLBs, without replacement materials. The separate reviewer inspected
every final view and board. No paid generation calls were used.

Final model SHA-256:

- Blue: `de6faa2fa3b7abe467b6902767f42e26d0f45813fa696b9aed1abfa5fe2c9c43`
- Vancouver: `ddcdf3b267589c54d0f9d3949157c7745a4efb06a9a13e53685e20ac31e6e172`
- Twisting: `932dc2152becbf9e74f2c7d83f314d6f93853be9794c628852a5e4154d010978`

All three `catalogue_promotion trial` dry runs pass. The delivery-contract and
clay-library pytest selection reports 4 passed and 7 skipped. Python builders
compile successfully. No TypeScript production code changed.

## Next: local placement trial, then publication

The external `blue-promotion.json`, `vancouver-promotion.json` and
`twisted-promotion.json` packages bind models to their independent reviews.
Human-approval and app-trial fields intentionally remain empty until performed.
Follow `docs/BUILDING_CATALOGUE_WORKFLOW.md` for selective local trial and
promotion. Google-tiles ground contact, student placement and runtime performance
have not yet been tested for this batch; asset review does not certify them.

Best preview views: blue `renders/front_corner.png`, Vancouver
`renders/front_right.png`, twisting `renders/front_corner.png`.

Reproduction instructions: `tools/catalogue_skyscraper_pilot/README.md`.
Earlier candidate versions are preserved externally as review history. The
initial Art Deco alternative was deferred because its reference views conflicted.

Two existing source PNGs were hydrated for package preflight. Their bytes match
HEAD, but the current LFS clean filter reports them modified; they are excluded
from this initiative's commit. Generated models and proof images remain external
and are not ordinary Git blobs.
