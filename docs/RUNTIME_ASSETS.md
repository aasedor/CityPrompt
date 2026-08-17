# Runtime asset policy

City Prompt keeps deployable visual assets under `frontend/public`. The source
of truth for what the application can address is
`frontend/src/data/runtimeAssetManifest.json`; it is generated, deterministic,
and checked in CI.

Run these commands after changing a catalogue, family signature, park recipe,
or public asset:

```powershell
cd frontend
npm run generate:runtime-assets
npm run check:runtime-assets
```

The manifest separates three categories:

- direct references found in production source and catalogue data;
- dynamic collections whose filenames are composed at runtime (LEGO building
  families, park kits, and park skins);
- unclassified files, which are cleanup candidates rather than automatically
  safe deletions.

Most large images and model files use Git LFS. Routine CI deliberately keeps
those files as pointers and runs `npm run check:runtime-assets`; this proves
that every runtime reference exists and that the checked-in manifest is
current without exhausting a standard runner's disk.

Before a release, manually run the **Release Assets** GitHub Actions workflow
for the exact candidate ref. It fetches only manifest-required LFS objects and
runs `npm run check:runtime-assets:hydrated`, preventing a release from
silently publishing Git LFS pointer text in place of an image or model. The
equivalent local sequence is `git lfs pull` followed by the hydrated check.

The database/object-storage model seed has a separate geometry preflight. It
reads only GLB headers, so checking the full multi-gigabyte library is fast and
does not decode textures or vertex buffers:

```powershell
python tools/audit_seed_model_library.py
python tools/seed_model_library.py --dry-run
```

The seed command runs this audit automatically before uploading objects. It
fails on missing LFS objects, malformed or externally linked GLBs, missing
normals, non-finite geometry, and LEGO modules that violate the bottom-centre
grounding contract. Stackable modules must also reach the declared height used
as the next module's placement datum, which prevents a valid-looking base from
hiding a floating upper level. Geometry may extend above that datum for
cornices, canopies, parapets, and other seam-crossing details. Triangle,
primitive, material, file-size budgets, and above-datum seam details are
reported as review warnings; pass `--verbose` to the standalone audit to list
them.
`--skip-asset-audit` is reserved for controlled maintenance and should not be
used for a release seed.

For Sticker Method GLBs fragmented into hundreds of otherwise compatible
surface materials, run `python tools/optimize_seed_glbs.py` first. The bounded
default pilot writes review candidates under `artifacts/` and rejects changes
to bounds, triangle count, or normals. After side-by-side visual review, rerun
with `--apply` and synchronize each changed row's `content_hash` before seeding.
The optimizer pins glTF Transform 4.4.2 so results remain reproducible.

The Vite development server also exposes `/dev/model-benchmark`. This
developer-only laboratory streams the original objects from the local Git LFS
cache and the optimized objects from the current seed, then runs deterministic
1/10/25-instance A/B suites with synchronized GPU timing, draw-call, FPS,
loading, allocation, and geometry-parity reporting. If an original benchmark
object is unavailable, run `git lfs fetch origin main`. The route and asset
endpoints are not emitted by the production build.

Use the Restored Kyoto Machiya A/A control before accepting a new Blender or
browser environment. Both sides load the same delivery GLB, so its run must
report parity, `Ground Y O / N: 0.0000 m / 0.0000 m`, and identical bounds.
That separates loader/ground-datum regressions from optimization differences.

For post-export visual review, render the final on-disk GLB rather than only
the pre-export Blender scene:

```powershell
blender --background --factory-startup `
  --python tools/archetype_compiler/render_delivery_glb.py -- `
  --input path/to/assembled--default--lod0.glb `
  --output-dir artifacts/delivery-review `
  --family example-family
```

The renderer imports the delivery GLB in a clean Blender session, records its
ground delta and bounds, and writes front, corner, rear, and aerial evidence.
The generated review belongs under ignored `artifacts/`.

Compiler renders, comparison sheets, review galleries, and other reproducible
QA output do not belong in `frontend/public` unless the runtime manifest proves
that the application addresses them. Generate those outputs under an ignored
`artifacts/` directory or external artifact storage, then promote only an
intentional runtime deliverable.
