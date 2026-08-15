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

Compiler renders, comparison sheets, review galleries, and other reproducible
QA output do not belong in `frontend/public` unless the runtime manifest proves
that the application addresses them. Generate those outputs under an ignored
`artifacts/` directory or external artifact storage, then promote only an
intentional runtime deliverable.
