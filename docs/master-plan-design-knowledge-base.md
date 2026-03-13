# Master Plan Design Knowledge Base

Updated: March 10, 2026

This document captures the local map-design guidance added from:
- `Architectural and Computational Foundations of the Modern Community Master Plan Map: A Technical Specification`
- the three user-provided reference plans showing landscape-led orthographic community plans

## What We Learned

The paper reinforces that strong master plans are not just zoning diagrams. They are readable compositions built from:
- clear spatial layering
- disciplined figure-ground hierarchy
- restrained but meaningful color logic
- legible multimodal circulation
- landscape and water systems that organize the plan instead of filling leftover space

The attached reference plans add several practical visual signals we want the renderer to remember:
- perimeter tree bands and planted streets help the site read before individual building details do
- parks, courtyards, and canals are connective structure, not decorative afterthoughts
- building roofs stay light and orthographic with soft shadows rather than heavy photoreal textures
- context should recede through muted saturation and soft contrast
- accent colors should be sparse and reserved for civic or amenity emphasis

## 2D Rendering Rules

Use these as default guidance for presentation-grade 2D plans:
- Keep the site as the visual figure and the surrounding context as a quieter ground.
- Read circulation in order: boulevards, streets, paths, plazas.
- Let landscape lead the composition with canopy rhythm, buffers, internal greens, and waterfront edges.
- Prefer light roofs, controlled shadows, and crisp overlays over heavy stylization.
- Keep water edges defined and public-facing when waterfront structure exists.

## Preferred Prompt Vocabulary

These phrases now have explicit meaning in the local 2D knowledge base:
- `Illustrative Rendered` and `Digital Watercolor`: push the renderer toward textured presentation-board output instead of flat schematic fills.
- `Gradient Layering` and `Soft Shadows`: increase light-direction cues so buildings and surfaces read with more depth.
- `Detailed Vegetation Texture` and `Formal Allee`: replace generic tree-dot logic with richer canopy texture and more deliberate tree-row placement.
- `Specific Typology`: cues stronger identity, especially for typologies like `Classic Haussmannian Parisian`, `Whistler-Style Alpine`, and `Adaptive Reuse Warehouse Lofts`.
- `Annotated Typography` and `Integrated Context`: encourage more board-like labels and softer blending with surrounding context.

## 3D And Aerial Rules

Use the same knowledge when producing aerial previews or 3D map scenes:
- Streets, water, and parks should form the structural framework of the district.
- Match references at the level of planting rhythm, edge treatment, massing softness, and material tone.
- Use repeated public-realm patterns and coherent massing families instead of object-by-object novelty.
- Treat promenades, civic greens, and waterfronts as premium frontage that deserve stronger articulation.

## Color Logic

The paper points toward APA/LBCS-style legibility rather than arbitrary palettes:
- residential uses should stay in warm/yellow-adjacent families
- commercial and high-activity areas can take warmer accent families
- mobility corridors should remain neutral and asphalt-like
- civic uses can lean cooler
- open space and natural systems should stay clearly green and layered

## Code Integration

This knowledge now feeds local generation through:
- `backend/app/services/master_plan_design_knowledge.py`
- `backend/app/services/master_plan_2d.py`
- `backend/app/services/layout_planner.py`

The 2D renderer uses it to:
- enrich style-guide metadata for each generated option
- bias variant heuristics toward stronger landscape structure, softer context, and clearer roof massing

The aerial/site-preview prompt path uses it to:
- inject explicit master-plan composition guidance before image generation
- keep future 3D-oriented outputs aligned with the same planning and placemaking language


