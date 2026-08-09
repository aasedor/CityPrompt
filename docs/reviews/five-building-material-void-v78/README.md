# Five-building material and void pilot v78

This bounded batch applies the v77 material-continuity and executable-void lessons to five new exact catalogue variants. Every family passed production preflight, Blender runtime quality gates and GLB validation. Visual status remains a separate human decision.

![Exact archetype comparisons](five-building-comparison.png)

![Roof and spatial-void audit](five-building-spatial-roof-audit.png)

## Outcome

- **Keeper pilots:** Neoclassical Courthouse, Italian Portici Block and Romanesque Revival Warehouse.
- **Provisional pilots:** Arts & Crafts Heritage and Scandinavian Courtyard Block. Their massing, roof materials and spatial openings are substantially better, but a family-level facade atlas still leaves the wrong opening/detail language. They must receive exact-variant facade sources before catalogue promotion.
- **Rejected during the run:** the original Art Deco courthouse attempt. Its generated massing used the correct Art Deco metadata, but the available facade sheet belonged to a Neoclassical parent. The run was replaced with the matching Neoclassical Temple variant instead of publishing a sibling-atlas mismatch.

## Pipeline changes proven by this batch

- Compact exact-variant massing recipes now expand into production `massing-graph@1` contracts.
- One opening block can construct multiple rectangular or round-arched recesses, with real piers, heads, reveals, back planes and facade-skin clearances.
- Courtyard passages are physically open through the front wing into a real perimeter court.
- Fixed assemblies and roofs bind to required textured material slots; missing or mismatched texture families fail the quality contract.
- A luminance-aware exact-variant tint can correct the wall hue of a reusable atlas while preserving dark glazing. This is a bounded fallback, not a substitute for an exact-variant atlas when masonry/opening language differs.

## Review rule

Structural passes do not prove likeness. Only the three keeper pilots are candidates for the next catalogue-quality iteration; the two provisional pilots remain evidence for the next exact-atlas and fixed-detail phase.
