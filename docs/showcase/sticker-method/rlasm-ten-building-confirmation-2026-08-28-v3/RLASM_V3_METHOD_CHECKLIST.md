# RLASM v3 — Reference-Locked Atomic Sticker Method

RLASM v3 is the production method used for the reviewed ten-building
confirmation batch dated 2026-08-28. It preserves the visual specificity of
the successful sticker method while requiring real 3D massing, physical depth,
neutral contextual glass, finished materials, and multi-view verification.

## 1. Prework is mandatory

No Blender build starts until the candidate has all of the following:

1. A locked multi-view reference sheet showing the primary identity, physical
   depth, roof/topology, rear/side conditions, and unique details.
2. A unique-role inventory. Every non-repeatable piece receives its own card;
   one broad crop cannot stand in for several different roof, entry, tower, or
   side-wing roles.
3. Atomic cards for repeatable windows, doors, trim, roof pieces, masonry,
   siding, and ornament. Similar-looking family members may still require
   different cards when their brick, sash, trim, siding, hardware, or roof
   language differs.
4. A reference-specific material palette. Generic brick, wood, stone, glass,
   roof, or trim is not an acceptable substitute.
5. A massing and contact plan that records every principal volume, roof,
   extension, step, balcony, stair, frame, pane, and supporting surface.

## 2. Construction rules

- Use real volumes for the building envelope, roofs, recesses, stairs, entries,
  balconies, and silhouette-defining pieces.
- Stickers/cards provide visual identity; they do not replace required massing
  or become giant rectangular building shells.
- Repeat only roles explicitly identified as repeatable. Unique roofs, domes,
  towers, gables, entries, corners, and service wings remain unique.
- Register every window, card, rail, stair, canopy, and ornament to a local
  physical surface. Never distribute one global rectangular grid across a
  non-rectangular or stepped building.
- Every contact must be physically supported or intentionally recessed. No
  floating windows, rails, handles, lights, slabs, stairs, or decorative cards.
- Glass uses the reusable neutral low-iron physical module. It has no image
  texture and no reflection baked from a prior render. Reflections come only
  from the current scene, lighting, and geometry.
- Occupied-depth imagery may sit behind glass, but must not be mistaken for the
  reflective pane and must remain bounded to the opening.

## 3. Giant-box and carrier-visibility hard gate

The Chateauesque and Coastal failures established this mandatory rule:

> Every large volume must be intentionally shaped, roofed, windowed or
> articulated, and visually finished from every exposed direction. An
> oversized blank carrier, hidden support block, flat cap, or topology-
> substitute slab is a hard failure even when the front view looks correct.

Required checks:

- `PASS_ZERO_EXPOSED_GIANT_SUPPORT_BOXES`
- `PASS_WINDOW_MASK_EXCLUDES_EXTERIOR_TRANSPARENCY`
- no window/card/support projects outside the physical envelope;
- no broad facade card contains sky or exterior transparency that turns into
  visible geometry;
- every service wing, rooftop control volume, tower, ell, courtyard edge, and
  rear shell is finished or intentionally concealed by valid geometry;
- open courtyards remain open rather than being filled by a box;
- non-rectangular components use their own local surface registry.

## 4. Required review views

Each candidate must provide actual 3D renders for:

- front;
- front corner;
- aerial/topology;
- side;
- rear side;
- facade close-up;
- glass close-up.

The front view alone cannot approve a building. Aerial and rear-side views are
specifically required to detect giant carriers, flat caps, blank backs,
misregistered windows, open seams, and floating elements.

## 5. Pass policy

A CityPrompt sample may pass at 95/100 or higher when all genuine 3D hard gates
pass. Minor close-range cosmetic differences may be left for downstream GPT
image/video refinement, but they must be recorded. Geometry, topology,
containment, glass, material specificity, contact, or runtime-state failures
cannot be waived as cosmetic.

Before publishing, the candidate must show:

- reference and unique-role prework present;
- actual `.blend` and `.glb` evidence present;
- zero generic material fallbacks;
- zero floating-contact findings;
- neutral scene-only glass and no baked reflection;
- seven required rendered review views;
- no exposed giant support/carrier box;
- a final visual QA record with score and hard-gate results.

## 6. Bounded production loop

Run one integrated build, then at most two focused correction passes. Fix the
largest reference, topology, material, or contact defect first. Preserve
rejected iterations for diagnosis. If only minor cosmetic debt remains after
the bounded loop and the candidate is still 95+, publish it truthfully and
move on; do not open an unlimited polishing cycle.
