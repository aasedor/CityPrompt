# Beaux-Arts terminal V83 — surface-story pilot

Status: **surface methodology keeper; archetype model provisional**.

This is a controlled comparison against V82 of the same Beaux-Arts terminal.
It applies the useful lessons from the reviewed Blender videos: real-world UV
scale, baked PBR surface variation, localized material history, a neutral
diagnostic render and a source-versus-export check.

## Result

- Production preflight: pass, 39 runtime gates.
- Output validation: pass with budget warnings.
- Surface audit: pass for six required baked materials.
- Blender source versus re-imported GLB: 99.23% mean pixel similarity.
- Assembled model: 133,788 triangles, 17 materials, 13.9 MB.

V83 is visibly less uniform than V82. Limestone courses read at facade scale,
the headhouse roof is a pale mineral field instead of the wall material, roof
edges now have side/rear parapets, and the clock tower has additional belt
courses. The changes survive GLB export.

The model is not yet a catalogue keeper for exact archetype likeness. The
largest remaining gap is fixed architectural identity: the reference tower is
more slender and sculpted, the facade has carved relief and richer capitals,
the balustrade cadence differs, and the glazed trainshed end needs a more
reference-accurate frame hierarchy. Increasing texture noise would not solve
those issues.

## Boards

- `01-archetype-before-after.png` — exact reference, V82 baseline and V83.
- `02-roof-before-after.png` — aerial reference and both roof-audit passes.
- `03-neutral-glb-parity.png` — source blend, imported GLB and difference map.

## Next bounded step

Add a fixed Beaux-Arts ornament kit for this variant: tower corner pilasters
and layered crown, carved spandrel/medallion motifs, capital blocks, stone
balustrade modules and a more faithful trainshed end frame. Keep the V83 baked
materials and neutral parity gate unchanged while testing that geometry pass.
