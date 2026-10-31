# Rebuilding the undergraduate teaching overlay

The checked-in `reviewed-inputs/audit.json` is the authored 2026-10-25 audit
of 196 exact local choices at source commit `55033b913`. It records the scope,
image-review limitations, confidence, interpretations and primary sources.
`reviewed-inputs/inventory.json` preserves the exact placement contracts from
that same review: domain, archetype, variant, revision and model method.
It omits unrelated registry properties and contains no model binaries.

`reviewed-inputs/evidence-lock.json` binds those two snapshots by SHA-256.
The compact inventory also records the original full inventory digest
`19ed89a4100801a72c9f21bd0bb21db6baa8d90bb074f1e5e4748e0e1878ee61`.
The generator rejects altered inputs before writing any output. Do not update
this lock to make a newer inventory pass: review changed exact models and
their teaching interpretations first, then preserve a new reviewed pair.
The scoped `.gitattributes` rule preserves snapshot bytes across Windows/Linux
checkouts; do not normalize line endings in these hash-bound files.

From the repository root, write a new ignored review file:

```powershell
python tools/catalogue_teaching/build_data.py --output artifacts/catalogueTeaching-rebuilt.json
python -m unittest tools.catalogue_teaching.test_build_data -v
```

The output path must not exist. The generator does not overwrite a reviewed
overlay or modify any registry, model, source image or placement property.
Compare the rebuilt JSON with `frontend/src/data/catalogueTeaching.json`
before deliberately promoting a reviewed update. There is no live catalogue
activation or architectural approval step in this command.
