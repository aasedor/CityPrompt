---
name: sticker-method
description: Create, repair, validate, review, package, and release image-locked modular 3D building families with the Sticker Method. Use for exact-reference architectural asset work that needs deterministic geometry, intrinsic material assets, exact-one surface ownership, physical glazing and roof semantics, bounded LEGO tiers or fixed-landmark rules, clay-to-Cycles visual gates, 95-plus formal scoring, fail-closed release evidence, and scoped Git checkpoints.
---

# Sticker Method

Build one architecturally faithful, deterministic 3D family at a time. Treat exact reference images as design authority, geometry as construction, and stickers as intrinsic material/optical evidence. Never use a facade picture to conceal wrong topology.

## Start safely

1. Locate the repository root and read its `AGENTS.md` and `CLAUDE.md` before editing.
2. Read the repository's high-quality building memory and machine-readable companion when present. In CityPrompt these are:
   - `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`
   - `tools/archetype_compiler/high_quality_building_memory.json`
3. Read any recovery note before reorganizing generated output.
4. Run `git status --short --branch`. Preserve unrelated changes and use a named branch or worktree for one building initiative.
5. Keep heavy experimental renders outside source control. Promote only reviewed evidence.

## Select the representation

Choose exactly one contract before geometry:

- `fixed_landmark`: one reviewed whole-building atom. Allow translation and rotation only unless an explicit, conservative scale band is reviewed. Do not invent an extended tier.
- `discrete_horizontal_lego`: keep entrance, corners, ends, crown, roof, service kit, and other identity assemblies fixed. Add or remove only complete ordinary horizontal modules.
- `whole_attached_unit_lego`: repeat complete attached units, including their roof, rear, party-wall, and service construction.
- `bounded_vertical_lego`: use only when the references prove repeatable whole occupied levels and the fixed base/crown remain invariant.

If the evidence cannot support a repeatable module, use a fixed landmark. Never use continuous nonuniform scaling to satisfy a catalogue range.

## Run the workflow

### 1. Lock the evidence

- Use the selected variant's exact street, oblique, aerial, roof, side, and rear views as one building.
- Record every authoritative path, SHA-256, pixel size, and crop bound.
- Let selected-variant images override generic parent metadata when they conflict.
- Separate observed facts from constrained completion. Never label an inferred rear as exact evidence.
- Write a binding lock for plan, section, storeys, bay rhythm, entrance, corners, roof, materials, fixed kit, repeatable module, and forbidden drift.

Copy `assets/evidence-lock.template.json` when a machine-readable lock is useful. Read `references/methodology.md` for adjudication rules.

### 2. Build deterministic construction geometry

- Author topology from the lock, not from a generic scaffold.
- Model silhouette, openings, recesses, returns, load paths, courts, galleries, screens, parapets, caps, roofs, rooflights, and equipment as physical geometry.
- Panelize opaque walls around real apertures. Do not leave a backing shell behind a void.
- Give every mesh a globally unique stable name, semantic role, owner, closed/outward contract, and metric dimensions.
- Keep floors, walls, bands, caps, glazing, roofs, and ornaments disjoint except for deliberate boundary contact or documented structural bearing.
- Test literal coordinates and forbidden overlaps. Counts and metadata alone do not prove spatial correctness.
- Generate twice and require byte-identical geometry hashes.

Do not begin material compilation until a literal source audit passes. First clay may begin only after the source gate is clear.

### 3. Prepare intrinsic sticker assets

- Generate shadow-neutral, lighting-neutral, geometry-free material sources.
- Keep masonry courses, aggregate, grain, weathering, patina, membrane, glass tint, metal response, and occupied-depth imagery at real metric scale.
- Forbid printed openings, frames, mullions, panel joints, rails, structural grids, silhouettes, directional shadows, horizons, signage, and text unless the exact role explicitly requires text.
- Use separate front/return/rear assets when registration requires them; keep their scale and phase compatible.
- Use separate glass and deterministic nonadjacent interior-atlas cells. Glass never owns frames or room imagery.
- Run asset preparation twice and lock file modes, dimensions, crop bounds, reference hashes, asset hashes, and provenance.

### 4. Compile exact-one surface ownership

- Bind the compiler to the approved geometry hash and exact evidence hashes.
- Assign every visible polygon to exactly one registered carrier and intrinsic asset.
- Fail on missing faces, multiply owned faces, fallback/default/clay materials, stale geometry, unknown roles, or unregistered assets.
- Map plan materials only to the intended upward faces. Give vertical returns, undersides, fascias, curbs, parapets, and caps their adjacent construction finishes.
- Keep pane, frame, card, backing, reveal, and interior architecture separate. Enforce exterior-to-interior ordering and positive containment margins.
- Keep cards behind panes and before opaque backings; bound every card to its opening.
- Use arc-length UVs on curved surfaces and constant metric UV scale across tiers.
- Compile twice and require byte-identical profile, registry, package, and contract files.

### 5. Pass the visual gates

Use the same locked cameras throughout iteration:

1. **Clay:** verify identity and topology before beauty. Require at least 93/100 and zero hard stops.
2. **EEVEE beauty:** diagnose ownership, registration, material hierarchy, terminals, roof domains, and obvious optical failures cheaply.
3. **Bounded Cycles diagnostic:** render critical views at about 16 samples. Resolve glass, interiors, fine terminals, material cadence, and reflection/transmission.
4. **Formal Cycles:** render all nine required views at 48 samples only after diagnostics pass.

Required formal views:

- preview
- archetype match
- street
- facade close
- front-corner oblique
- rear-corner oblique
- aerial
- roof audit
- context

Score exactly, without rounding:

- archetype identity: 30
- massing and geometry: 20
- sticker registration/material semantics: 20
- all-surface roof and entrance coverage: 15
- LEGO scale consistency/no stretching: 15

Release rules:

- every reviewed tier must score at least 95.00;
- a multi-tier unrounded mean must be strictly greater than 95.00;
- a fixed landmark's canonical score must be at least 95.00;
- hard-stop count must be zero;
- machine validation supports but never replaces visual review.

### 6. Publish fail-closed evidence

- Promote only reviewed renders, validation, preflight, surface audit, comparison boards, exact scores, and the approval verdict.
- Lock reference, geometry, builder, asset-provenance, compiler, registry, carrier-package, contract, render, and board hashes.
- Refuse publication when a score is pending, a hard stop remains, a hash differs, a required view is absent, or ownership is not exact-one.
- Run the publisher twice and require byte-identical output.
- Promote the batch ledger only after the evidence package passes.

Use `scripts/audit_release.py` to audit a batch ledger and its review packages. Read `references/release-contract.md` before writing or changing a publisher.

### 7. Commit one approved wave

- Run focused geometry, asset, compiler, publisher, JSON, and diff checks.
- Review `git diff --check`, `git diff --stat`, and `git status --short`.
- Stage explicit initiative paths only.
- Commit one coherent approved building wave. Push only when authorized.
- Preserve unrelated user changes and never stage generated directories wholesale.

## Correct failures in priority order

1. wrong archetype, floor count, plan, section, or roof topology;
2. missing openings, courts, entrances, load paths, closures, caps, or rear construction;
3. intersections, floating pieces, open seams, inverted normals, and optical ordering;
4. wrong material ownership, UV scale, roof domain, glass response, or repeated interiors;
5. fine ornament, weathering, and optimization.

Do not polish materials while a geometry hard stop remains. Correct the smallest bounded root cause, regenerate deterministically, and rerender only the necessary gate before resuming formal work.

## Resources

- `references/methodology.md`: detailed evidence, geometry, sticker, optics, roof, tier, and review rules.
- `references/release-contract.md`: release package and score requirements.
- `references/repository-workflow.md`: CityPrompt file patterns, commands, and naming conventions.
- `assets/evidence-lock.template.json`: portable exact-evidence lock.
- `assets/family-contract.template.json`: portable fixed/tier and hard-stop contract.
- `assets/visual-approval.template.json`: formal score and verdict record.
- `scripts/audit_release.py`: fail-closed batch/review auditor.
- `scripts/package_skill.py`: deterministic ZIP packager for sharing this skill.
