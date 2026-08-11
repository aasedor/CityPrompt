# Sticker Method

This folder is the working specification for producing image-locked architectural
landmarks by combining approved 3D construction with registered surface
stickers. It consolidates the lessons through the Belle Époque Grand Magasin
V95 pilot.

The current reference result is the geometry-conditioned V95 pilot:
**95/100, approved, with zero hard stops**. It proves continuous exterior
shells, floor-addressable ownership, complete surface coverage, real entrance
depth, roof-edge ownership, persistent landmark glass and physical dome
structure. This is the first 95+ production reference; catalogue scale remains
blocked until the three-archetype transfer proof in the production plan passes.

## The central rule

**A sticker is made for its final 3D carrier; it is not a finished flat image
that is later stretched onto an approximate model.**

The approved clay mesh is frozen first. That exact mesh produces the UV charts,
surface-position map, normals, depth, curvature, visibility, floor IDs and
semantic masks used to create the sticker. A sticker is approved only after it
has been rendered back on that same mesh from the required reference views.

The master sticker is de-lit intrinsic surface colour plus explicit material
channels—not a photograph with its old perspective, sunlight, shadows and
reflections baked in. Those effects are re-created by the 3D carrier, PBR
material, glazing and scene lighting.

This changes the workflow from `beautiful image → wrap it somehow` to:

`reference evidence → final carrier geometry → carrier-space evidence → sticker → projected proof render`.

## What the method is

- A **fixed select-and-place landmark representation** for image-specific
  buildings. Translation and rotation are safe; non-uniform scaling and
  arbitrary polygon fitting are not.
- A **continuous exterior shell** whose faces retain ground, middle, crown and
  roof ownership. Floor addressability must not create stacked closed boxes or
  horizontal facade cuts.
- A **layered representation**: geometry owns silhouette, depth, openings and
  shadow-bearing construction; stickers own image-locked colour, fine ornament
  and irregular identity; PBR materials own optical response.
- An **all-surface system**. Front, side, rear, chamfer, courtyard, roof, dormer,
  dome, entrance return, canopy edge and exposed cap all require an owner.

## What the method is not

- A billboard pasted onto a box.
- A monolithic elevation texture stretched to a different floor count.
- Independent floor prisms stacked behind attractive strips.
- A way to paint a doorway over solid masonry. Recesses and tunnels remain
  actual topology.
- A licence for generic glass or roof geometry to cover photographed windows,
  frames, ornament or roof details.

## Authoritative documents

- [95+ production plan](STICKER_METHOD_95_PLUS_PLAN.md)
- [Machine-readable contract](sticker_method_contract.json)
- [Current V95 evidence](../reviews/catalogue-rollout-v95/belle-epoque-geometry-conditioned-sticker-pilot/README.md)
- [V94 baseline evidence](../reviews/catalogue-rollout-v94/belle-epoque-continuous-sticker-pilot/README.md)
- [High-quality building memory](../HIGH_QUALITY_3D_BUILDING_MEMORY.md)

## Current findings

1. Beautiful source skins retain archetype identity, but their accuracy is lost
   when geometry, UVs, floor datums or physical overlays use a different
   registration frame.
2. Complete named-material coverage is insufficient. The final Blender scene
   must report zero fallback polygons after every carrier is bound.
3. Floor ownership is useful for replacement and bounded height variants, but
   the visible wall should remain one continuous cap-free shell.
4. Curved walls, domes and pitched roofs need shape-appropriate UV charts.
   Planar projection is not an acceptable universal mapping.
5. Corners and elevation transitions need shared boundary evidence. Independent
   front and side images create colour, course and feature discontinuities even
   when both are individually attractive.
6. A physical optical layer is allowed only inside a sticker-derived, registered
   mask. Otherwise it duplicates or obscures windows.
7. Raw sticker beauty is diagnostic, not an approval result. The projected
   multi-view render is the product the user will see.
8. Floor/roof ownership follows the final carrier's construction domain, not
   its shader class. Glass on a dome is still roof-owned.
9. Identity-bearing landmark glass must persist in every presentation LOD.
   Hiding it in aerial views exposes backing geometry and invalidates the
   sticker approval even when street views pass.
10. A thin return must use shared boundary texels or be authored as an explicit
    construction joint. Isolation-border pixels are never valid seam content.
