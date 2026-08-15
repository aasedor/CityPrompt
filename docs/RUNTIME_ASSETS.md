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

Most large images and model files use Git LFS. A normal release check must run
`git lfs pull` and then `npm run check:runtime-assets:hydrated`. CI checks out
LFS objects and enforces the hydrated gate so a build cannot silently publish
Git LFS pointer text in place of an image or model.

Compiler renders, comparison sheets, review galleries, and other reproducible
QA output do not belong in `frontend/public` unless the runtime manifest proves
that the application addresses them. Generate those outputs under an ignored
`artifacts/` directory or external artifact storage, then promote only an
intentional runtime deliverable.
