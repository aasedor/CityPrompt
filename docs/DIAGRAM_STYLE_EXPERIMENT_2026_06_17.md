# Which Diagram Style Does GPT Image 2 Render Best? — Empirical Experiment (2026-06-17)

**Question:** what *type* of technical conditioning-diagram does GPT Image 2 (and Gemini) turn into the most accurate, building-free, geometry-faithful render?

**Method:** controlled A/B/C. One subject (protected intersection), identical to-scale geometry, **only the visual style varies**. 9 styles × {GPT Image 2 via `images/edits`, Gemini via inline-image `generateContent`} × oblique aerial, constant prompt = 18 renders, plus a nadir confirmation. Styles + scoring rubric designed by a 5-agent workflow. Artifacts: `artifacts/diagram-style-doe/{styles,renders}/`. Scripts: `_gen_diagram_styles.py`, `_render_style_experiment.py`.

## TL;DR — Winner: **desaturated real-material flat-color plan**

The validated flat-color to-scale plan with its palette **muted toward true-material chroma**. It ties the bright "flat" champion on geometry/building-free/markings/artifacts and **beats it on photorealism** (believable brick-red colored asphalt vs slightly neon terracotta), at **zero added cost** — it's just a palette swap, fully reusable across every archetype. Now the production palette in `_render_diagrams_toscale.py`.

## Results (GPT Image 2, oblique)

| Style | Bld-free | Geometry | Markings | Artifact-free | Photoreal | Verdict |
|---|---|---|---|---|---|---|
| **desat** (muted real-material) | ✓ | ✓ exact 4-way + corner islands | ✓ crisp | ✓ | ★★★ most natural | **WINNER** |
| flat (champion/control) | ✓ | ✓ | ✓ | ✓ | ★★ slightly neon terracotta | co-champion / safe baseline |
| shadow (+drop-shadow on raised) | ✓ | ✓ | ✓ | ✓ | ★★ | good; best when raised islands/bulbs dominate |
| realistic (Gemini-textured input) | ✓ | ✓ | ✓ | ✓ | ★★★ | excellent but **least reusable** (per-image Gemini pass) |
| bold (charcoal keylines) | ✓ | ✓ | ✓ | ✓ (charcoal didn't leak) | ★★ | fine; no clear edge over borderless |
| axon (pre-tilted oblique) | ✓ | ✓ held | ✓ | ✓ | ★★ | projection-match worked; extra authoring cost |
| seg (label-map, no markings) | ✓ | ✓ | ~ crosswalks softer | ✓ | ★★ | OK; markings less crisp |
| **cad** (grayscale line-art) | ✓ | ~ | ~ | ✓ | ✗ bike track renders **GRAY** | **LOSER** — no colour ⇒ lost material semantics |
| **blueprint** (white-on-blue) | ✓ | ~ | ~ | ✓ | ✗ bike track **GONE** | **LOSER** — no colour ⇒ lost the feature |

## Key empirical findings

1. **Color-fill beats line-art, decisively.** Every flat-color style produced a faithful, building-free render on BOTH models. The two no-color styles failed: **cad** rendered the protected bike track as plain gray (lost the bike-lane meaning); **blueprint** dropped the bike ring entirely. Material *color* in the input is what carries surface semantics — GPT preserves it (locked-high input fidelity), so a colored region becomes that material; a white/blue void gets improvised.
2. **Desaturate toward real materials.** GPT preserves input color literally, so a slightly muted brick-red / olive-green / cool-grey palette lands on photoreal surfaces; bright "diagram" colors read a touch toy. Same geometry, better photo.
3. **No phantom buildings anywhere.** All 18 renders were building-free — the buildings-free diagram input is a hard win, independent of style.
4. **No roundabout drift** on any color-fill style — the strong terracotta ring + 4 distinct legs held the 4-corner topology on both models.
5. **Plan → oblique works.** The nadir-plan `desat` input rendered a faithful *oblique* aerial with no re-projection distortion — the feared plan→oblique mismatch was not a problem here. (Projection-matched `axon` also worked but adds authoring cost.)
6. **`gpt-image-2` rejects `input_fidelity`** (HTTP 400) — confirms the literature finding that it's locked-high, not a usable lever. Removed from the harness.
7. **Gemini-specific trap:** `cad` → Gemini invented a **horizon + sky** from the white void (phantom context). Another reason to avoid empty/line-art inputs.

## The winning style spec (production)

Nadir top-down plan, to-scale (px = m × SCALE), one flat fill per surface class, **no text**, only the 3–4 defining markings (white zebra, dashed amber centreline, terracotta bike fill); no turn arrows/pictograms; no baked cars/people. Muted real-material palette:

```
asphalt   (118,120,122)   bike track (168, 92, 74)   grass (138,158,112)
island    (150,176,138)   crosswalk  (238,240,242)   centreline (222,188, 86)
curb edge (158,162,166) 1px hairline only — no black outlines
```

Dimensions live ONLY on the separate `variant_0_spec.png`, never fed to the model.

## Applied to production
- Winning palette baked into `_render_diagrams_toscale.py`; all 3 diagram archetypes (protected intersection, compact roundabout, curb extension) regenerated. Prior bright-"flat" versions kept as `variant_0_flat.png` for A/B.
- Going forward: every new diagram archetype uses this style.

## Situational add-ons (not default)
- **shadow** (one soft drop-shadow on raised elements) — for archetypes where 3D relief matters (raised refuge islands, bulb-outs, raised crossings/tables).
- **axon** (projection-matched oblique) — only if a render consistently needs a steep oblique and the nadir plan drifts; derive the shear from the real camera pitch.

## Do-not-use (confirmed traps)
Grayscale CAD line-art, blueprint, pure black keylines (use charcoal), neon segmentation palettes, baked text/arrows/figures, heavy texture/gradients.
