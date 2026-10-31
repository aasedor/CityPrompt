# Teaching style pilots

This is a finite, local RLASM 6.1 architectural-clay batch, not an activated
catalogue expansion. The first pilot is a Prairie School house. The second is a
Postmodern neighbourhood library, started after the first independent review pass.

The immutable source and candidate bundles live under
`C:/dev-artifacts/CityPrompt/teaching-gaps-20261025`. Reviewed delivery receipts
are recorded there in `delivery-manifest.json`. No heavyweight output is staged
from this directory.

Run from the repository root:

```powershell
python -m pytest tools/teaching_style_pilot/test_contracts.py -q
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/teaching_style_pilot/build.py -- --family prairie --version 4 --output C:/dev-artifacts/CityPrompt/teaching-gaps-20261025/dry-run-prairie-only --dry-run
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python tools/teaching_style_pilot/build.py -- --family library --version 2 --output C:/dev-artifacts/CityPrompt/teaching-gaps-20261025/dry-run-library-only --dry-run
```

Omit `--dry-run` only for a new deliberately authorized finite candidate version.
Existing candidate directories are refused, never overwritten. The shipped
builder, contracts and low-level core are copied into each candidate so the
exact source script bytes remain available. The batch also preserves the runtime
template required to replay an external candidate's script.

After a build:

```powershell
python -m tools.teaching_style_pilot.prepare_review C:/dev-artifacts/CityPrompt/teaching-gaps-20261025/prairie-school-house-clay-v004
```

Evidence preparation refuses existing boards/verification. It records exact
source hashes, export/reimport bounds, zero textures/images, real carrier
apertures, complete camera safety margins and full-resolution render validity.
These checks cannot grant visual approval. Open every render, write a builder
review, then request a separate holistic source-locked clay review.

The initial AI board's rear quadrant was mirrored. A replacement rear proposal
corrected handedness but shifted the chimney horizontally. Both are preserved
as rejected sources. The final source lock uses unchanged extracts of the three
compatible front/oblique/top panels, with crop rectangles and parent hash in
`references/source-provenance.json`. The complete rear is an explicit architectural
inference; it is reviewed visually without claiming an exact rear-source match.

No image or source is retouched to hide a modelling discrepancy. Source panel
extraction and evidence letterboxing preserve original pixels and provenance.
The generation originals are retained separately.

The library uses its own source extracts and provenance, not the Prairie board.
Its third source is a high aerial view despite the generated label "top roof
plan". The observed rear wing setback, portico centre and pediment height govern
the model instead of the requested prompt dimensions. Unseen rear/left openings
and the internal shelving layout are explicit architectural inferences.

Library v001 is preserved as a builder rejection: coincident circular carrier
and frame reveals produced triangular rendering artefacts. v002 enlarges only
the structural cut by 35mm, retaining the clear frame diameter. Every GLB view
was regenerated. Full-resolution `glass_close` evidence shows the result; a
successful Boolean audit alone would not have detected that surface conflict.

All models are fixed native scale. No runtime binding, catalogue activation,
arbitrary resizing, terrain fit, student-control test, textured keeper approval
or accessibility compliance is implied. See the per-candidate unrun integration
matrix and measured entrance contract before any later local app trial.
