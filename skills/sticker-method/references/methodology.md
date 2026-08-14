# Sticker Method methodology

## Contents

1. Evidence authority
2. Binding architectural lock
3. Geometry and sticker responsibility
4. Literal topology audit
5. Intrinsic assets and registration
6. Glass and occupied depth
7. Roof and all-surface coverage
8. LEGO scaling contracts
9. Visual iteration and scoring
10. Common failure diagnoses

## 1. Evidence authority

Treat all compatible views of the selected variant as one evidence set. Record exact file hashes before interpreting the design. Use image evidence in this order:

1. selected-variant exact images;
2. compatible views of that same variant;
3. catalogue variant prose that agrees with the images;
4. parent-family metadata only where it does not conflict;
5. conservative constrained completion for unseen faces.

Reject sibling aesthetics and generic metadata that introduce a different floor count, roof, entrance, balcony, material system, or massing. Record rejected claims in the evidence lock so they cannot return later.

## 2. Binding architectural lock

Freeze the decisions that determine identity before modeling:

- canonical width, depth, occupied datums, parapet/crown heights;
- plan type and true voids such as courts, arcades, passages, atria, or naves;
- public and service orientations;
- bay centers, widths, opening schedules, bands, corners, and terminal pieces;
- singular entrance, pavilion, tower, pylon, oriel, screen, chimney, or roof kit;
- material hierarchy and distinct optical classes;
- rear completion limits;
- tier behavior and forbidden scaling.

Make counts exact when the images prove them. Do not use ranges as permission to improvise.

## 3. Geometry and sticker responsibility

Geometry owns anything that changes silhouette, casts a meaningful shadow, creates a void or depth, closes an envelope, or must remain correct from an oblique camera. This includes:

- building masses, wings, courts, setbacks, roofs, parapets, coping, and caps;
- apertures, jambs, heads, sills, soffits, thresholds, frames, mullions, and doors;
- canopies, columns, braces, screens, balconies, rails, stairs, rooflights, and equipment;
- all side, rear, courtyard, terminal, underside, and roof-return surfaces.

Stickers own intrinsic surface and optical evidence:

- masonry courses, grain, aggregate, patina, restrained weathering, membrane response;
- metal and glass optical response;
- subdued, bounded occupied-depth cards;
- role-specific front, return, rear, roof, coping, service, and equipment finishes.

Never print structural geometry or cast shadows into intrinsic assets. Never use a material to camouflage an open seam or missing carrier.

## 4. Literal topology audit

Review source coordinates and faces independently of focused tests. Verify:

- opaque fabric exists above, below, and beside every aperture;
- every opening plane is physically recessed from the correct exterior side;
- pane, card, backing, and interior cues move inward monotonically;
- every wall, slab, band, frame, cap, parapet, roof field, and ornament is disjoint except at documented bearings;
- roofs meet gables, lanterns, screens, courts, parapets, and terminals without gaps or penetration;
- openings and courts remain open through every slab and roof layer;
- outward normals match the actual exterior or courtyard direction;
- extended tiers preserve canonical coordinates and semantic roles;
- fixed kits are not duplicated or elastically stretched.

Add regression tests for the spatial cause, not merely for object counts or metadata flags.

## 5. Intrinsic assets and registration

Build deterministic sources from exact-reference palette and scale. Require:

- RGB mode and declared dimensions;
- exact crop bounds and source hashes;
- real metric texture period;
- semantic exclusions for printed structure, openings, text, lighting, and horizons;
- byte-identical output across repeated runs;
- asset-level SHA-256 provenance.

Use separate roles when physical response differs. A roof field, flashing return, parapet vertical, coping top, door leaf, reveal, and equipment casing must not share one generic material merely because their colors are similar.

## 6. Glass and occupied depth

Use the layer order:

1. physical opening and reveal;
2. physical frame or sash;
3. pane at the optical plane;
4. room card immediately behind the pane;
5. shallow floor, ceiling, and side cues when the view needs depth;
6. opaque backing farther inside.

Keep the glass non-emissive. Put warmth on the card or local interior cue. Use deterministic, nonadjacent atlas cells and restrained per-bay variation. Backings must contain cards and never sit before them. Check all orientations, shaped heads, returns, stair slots, lobbies, and monumental glazing separately.

## 7. Roof and all-surface coverage

Treat roof evidence as primary identity. Build separate domains for roof field, service path, court floor, flashing, coping, curbs, glass, screen, and equipment. Map plan textures only to intended upward faces. Classify physically reversed prisms by world position or centroid rather than blindly trusting winding.

Audit aerial and roof views for:

- true courts and voids;
- ridge, valley, eave, gutter, parapet, and coping continuity;
- lantern and rooflight end closure;
- terminal slivers and backfaces;
- roof material leaking onto walls or undersides;
- floating or intersecting equipment;
- metric tile, seam, and weathering scale.

## 8. LEGO scaling contracts

For a repeatable family, distinguish fixed identity from ordinary capacity. Keep all canonical fixed assemblies byte-identical where practical. An extended tier must add explicit, disjoint construction:

- complete wall/opening module on every affected exterior;
- aligned floor and roof pieces;
- aligned courtyard or rear fabric;
- constant metric UV and opening scale;
- translated terminal construction only where the new module requires it.

Do not validate a tier with marker solids or metadata-only modules. A rendered module must exist and canonical bay roles must not flip because enumeration parity changed.

For a fixed landmark, approve only the whole building. Do not create a second size merely to satisfy catalogue capacity.

## 9. Visual iteration and scoring

Use finite, bounded iterations:

- clay identifies topology and archetype problems;
- EEVEE identifies ownership and broad material problems;
- low-sample Cycles identifies optical and terminal problems;
- formal Cycles confirms the complete release.

Lead each correction with the highest-impact visible defect. Freeze geometry after the clay gate unless a later renderer exposes a real topology defect. Freeze material values after the final diagnostic pass.

The formal five-part rubric totals 100. Record exact decimal components and arithmetic. Do not round a failing result upward. A machine pass cannot approve architectural likeness.

## 10. Common failure diagnoses

| Symptom | Likely cause | Correction |
| --- | --- | --- |
| Black aperture | missing head/sill fabric, wrong pane winding, backing before card | inspect layer coordinates and wall panels |
| Black terminal tick | run overlaps a frame or ends without adjacent-finish cap | shorten run and add explicit cap |
| Flat dark glass | card too remote, opaque backing dominates, glass overly absorptive | fix ordering and depth before color |
| Roof looks uniform | wrong face grouping or missing semantic fields | split roof domains by actual construction |
| Courtyard wedges | stacked per-level caps expose backfaces | use one continuous watertight corner closure |
| Extended tier looks stretched | canonical bays reflow or carriers lengthen | preserve canonical anchors and insert a real module |
| Material looks pasted | perspective or structural content baked into asset | regenerate an intrinsic orthographic source |
| Ornament floats | no shared boundary with load path | connect physically or remove unsupported motif |
| Render passes tests but looks wrong | tests assert declarations rather than space | add literal coordinate and forbidden-overlap tests |
