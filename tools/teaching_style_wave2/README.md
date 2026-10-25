# Teaching archetypes — Wave 2

Finite original designs: Bauhaus-inspired design workshop (pilot), then De Stijl
artist studio and Mughal-inspired reading pavilion. Use RLASM 6.1 architectural
clay, fixed native scale and separate independent holistic visual review.
No catalogue, seed, placement or app activation is performed by these scripts.

Generated source staging uses only
`frontend/public/archetypes/buildings/teaching-wave2/<family>/`. It is ignored
until an explicit later promotion. Originals, source crops, candidate versions,
replay snapshots and review evidence are preserved externally under
`C:/dev-artifacts/CityPrompt/teaching-wave2-20261025`.

```powershell
python -m pytest tools/teaching_style_wave2/test_contracts.py tools/teaching_style_pilot/test_contracts.py -q
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/teaching_style_wave2/build.py -- --family workshop --version 3 --output C:/dev-artifacts/CityPrompt/teaching-wave2-20261025/dry-run-workshop-v003 --dry-run
```

Build only a deliberately chosen new candidate version by omitting `--dry-run`.
Existing directories are refused. Source hashes, immutable copied builder
scripts, exact export/reimport bounds, texture/image counts, all through-wall
apertures and camera margins are recorded before visual acceptance.

Prepare unchanged-source comparisons after a complete build:

```powershell
python -m tools.teaching_style_pilot.prepare_review C:/dev-artifacts/CityPrompt/teaching-wave2-20261025/bauhaus-design-workshop-clay-v003
```

The per-version `runtime-template-*` external snapshot preserves the small
repository-shaped dependencies and canonical reference paths needed to replay
the archived builder. Its manifest hashes every input. A candidate's four
copied builder files alone are not advertised as a standalone application.
Render originals and `.blend`/GLB binaries stay outside Git.

Workshop source labels need interpretation: “TRUE TOP” is a high aerial, and
the alleged rear is another compatible front-high oblique. Those real roles
are recorded in provenance. Metric scale and unshown rear/right designs are
inferences. No generated source is retouched to conceal a model discrepancy.

Builder rejections remain preserved: v001 has a generic door, milky glazing
and an unhelpful stair camera; v002 corrects those but exposes QA-emitter
reflections and missing intermediate landing guards. v003 addresses that
finite list and rerenders all fourteen exact-GLB views. Independent review
determines its actual acceptance, not this README or the deterministic checks.
