# Classroom starter v1

`starter-v1.json` owns the finite first-release roster: three buildings, three
streets and three parks. It locks existing model, module, texture and reference
bytes, with separate asset and runtime review status. Inclusion is an integration
target, not visual approval or proof of a hosted classroom release.

Run from the repository root:

```text
python scripts/classroom_release.py sync
python scripts/classroom_release.py check
python scripts/classroom_release.py preflight --public-root <deployed-public-directory> --report artifacts/classroom-preflight.json
python scripts/classroom_release.py preflight --public-root <deployed-public-directory> --require-release
```

`sync` updates the frontend/backend generated copies. `check` checks schema,
identity and parity; it does not read asset bytes. `preflight` checks every locked
dependency and distinguishes missing files, unhydrated LFS pointers and revision
mismatches. JSON/text locks normalize line endings, binary locks do not.
`--require-release` additionally requires accepted runtime reviews and packaged
sources. It intentionally fails while integration remains unfinished.

In a sparse checkout, include the manifest's repository dependencies and public
paths (prefixed with `frontend/public/`) before selective `git lfs pull`/checkout.
The native streets require both `frontend/public/street-kits/pilots/` directories;
ordinary catalogue thumbnail checks do not cover their dynamic module URLs.
Do not regenerate models to repair a missing tracked file.

The infill GLB is an exact copy of the previously demonstrated v006 model from
the D5 trial, SHA-256
`eeb0d1d878ec474e6743a1e1aeef7bf84dfda360c1150662b60430095f26ac37`.
Packaging preserves those bytes; it does not perform a new RLASM keeper review,
activate a family, seed a database or upload storage objects. Library seeding and
destination-bucket readback remain separate release requirements. The other two
building models retain their existing architectural-clay library packages.

The roster covers archetype dependencies; it does not replace the full app's
runtime asset manifest, service configuration, Model Library storage check or
Currie browser rehearsal. After changing a dependency, inspect it and deliberately
update its lock; never accept newly generated hashes merely to make a check green.
