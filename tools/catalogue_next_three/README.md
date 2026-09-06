# Three exact-reference clay buildings

Finite September 2026 batch: rammed-earth infill, classic motor-court motel,
and brick Beltline mixed-use mid-rise. These builders author native geometry;
they do not generate raster references or call paid providers.

Read the repository RLASM 6.1 method and `docs/BUILDING_CATALOGUE_WORKFLOW.md`
before building or activating a model. The exact source folders and variant
indices are declared in each builder. Hidden elevations/programme assumptions,
source measurements, contact requirements and the entire camera roster are
written before geometry in the immutable prework manifest.

```powershell
blender --background --python tools/catalogue_next_three/infill.py -- --source-root <hydrated-repo> --output <new-external-candidate> --version 1 --dry-run
blender --background --python tools/catalogue_next_three/infill.py -- --source-root <hydrated-repo> --output <new-external-candidate> --version 1 --resolution 1440
python tools/catalogue_next_three/proof.py <completed-external-candidate>
```

Replace `infill.py` with `motel.py` or `beltline.py` for the other exact variant.
Always use a fresh output directory/version. Wait for `BUILD_COMPLETE` before
proof generation. Proof preflight refuses incomplete builds before writing
boards. Proof reruns refuse to overwrite an existing evidence decision.

`support.py` reuses low-level clay mesh/window/delivery helpers, not another
family's geometry. The final GLB is merged by material, reimported unchanged,
and rendered in 13 source/comparison/construction views. Actual native bounds
include all authored overhangs and asymmetry. Design dimensions are estimates
and are not used as the runtime envelope. Proof independently compares the
report with the Y-up GLB dimensions.

The result is architectural clay, not a fully textured RLASM keeper. No builder
or deterministic check grants visual approval. Preserve rejected versions;
obtain independent holistic review before using the promotion tool for local
trial. Publish only the same reviewed bytes after the student trial passes.
Do not check the external Blender/render directories into Git.
