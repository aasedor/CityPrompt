# Selective LFS downloads for deployment

The deployment-version branch defaults to leaving Git LFS files as pointers at
checkout. Render's initial clone ignored the service's GIT_LFS_SKIP_SMUDGE setting
and exhausted build disk while downloading historical building textures, before
the Docker or frontend build could start.

The repository .lfsconfig sets lfs.fetchexclude to *. This changes download
defaults only: tracking rules, source hashes, object storage, and Git history are
unchanged. The owner approved this policy change on 2026-10-14.

The frontend build remains:

```sh
npm ci --prefix frontend
python3 scripts/build_hosted_frontend.py --fetch-lfs
```

RepositoryAssets fetches the finite required paths with explicit --include and
--exclude= arguments, overriding the default exclusion. It checks asset hashes
and rejects unresolved LFS pointers in published output. The backend Docker
build uses source files; private catalogue models are separately imported into
object storage and verified against their manifests.

For local work that requires an individual LFS source file:

```sh
git lfs fetch origin --include="path/to/required.glb" --exclude=""
git lfs checkout "path/to/required.glb"
```

Choose only the files needed for the task. A fresh clone will not automatically
contain every historical model, image, texture, or video.

## Validation

- An isolated local Git/LFS fixture proved the baseline clone hydrated assets.
- With this configuration and no GIT_LFS_SKIP_SMUDGE environment variable, a
  fresh clone retained pointers. Explicitly fetching one asset hydrated its
  exact SHA-256 bytes while leaving the unrelated asset as a pointer.
- The fixture remained clean after hydration.
- All 12 tests in scripts/tests/test_hosted_assets.py passed.

These checks establish local Git/LFS behavior. A successful Render checkout and
build must still be verified on the hosted release; they are not implied here.
