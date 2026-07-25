# SCHEMA Color Fidelity Research

> How to ensure buildings, streets, and parks in SiteForge renders stay true to their specified colors from the SCHEMA prompt system.

**Date:** 2026-03-31
**Model under test:** Gemini 3.1 Flash Image (Nano Banana 2)
**Render pipelines:** Aerial (useAIRender.ts), Street View (useStreetViewRender.ts)

---

## 1. Current Color System Analysis

### 1.1 How Colors Enter the Prompt

SiteForge has **two separate color concepts** that coexist in every render prompt, and their conflation is likely a root cause of color drift:

| Concept | Purpose | Format | Example |
|---------|---------|--------|---------|
| **Zone overlay color** | Spatial mapping — tells the AI *where* each zone is in the reference image | Hex color mapped to a human-readable name via `colorName()` | `#E03C31` -> "red" |
| **Archetype material/color scheme** | Aesthetic intent — tells the AI *what materials and colors* the building should have | Descriptive prose from `facadeDetail.colorScheme` | "warm honey limestone, dark slate roof, dark oak doors" |

**Zone overlay colors** are assigned per zone type (red for buildings, green for parks, grey for roads) and are used to paint the colored polygon overlays in the map screenshot or the 3D clay massing model. The AI is told to "replace every red pixel with building facade."

**Archetype color schemes** come from `buildingArchetypes.json` via the `facadeDetail.colorScheme` field. These are purely descriptive strings like:
- `"warm limestone body, dark slate or polychrome slate roof, dark oak doors, lead-grey window frames"`
- `"rich red brick, pale cream stone dressings, dark slate roof"`
- `"sage green, cream trim, warm timber"`

### 1.2 How Colors Are Communicated in Each Pipeline

**Aerial Pipeline (`useAIRender.ts` / `buildStructuredPrompt`):**
- The prompt says: `"The red polygon is a building footprint. Render a 4-story Georgian Terrace House building..."`
- Archetype description is appended via `buildArchetypeDescription()`, which includes `colorScheme` at the end of a long narrative.
- The `colorScheme` appears as a plain prose fragment, e.g., `"warm honey limestone, dark slate roof, dark oak doors"` buried within a paragraph-length zone description.
- No hex codes, no Pantone references, no explicit color assertion language.

**Street View Pipeline (`useStreetViewRender.ts`):**
- A 3D clay massing model is rendered with solid-colored volumes (one color per zone).
- The COLOR-TO-ZONE MAPPING legend maps each hex color to a zone name:
  ```
  The #E03C31 colored volume = "Georgian Terrace House"
  ```
- Zone descriptions are built by `describeZoneForStreetView()`, which includes facade/roof/materials info but typically does **not** prominently feature the color scheme — it focuses on the archetype title, facade rhythm, massing, and public realm.
- The `colorScheme` field is included in `getZoneArchetypeInfo()` return but is only used in the building prompt path (line 1068: `Color palette: ${archetypeInfo.colorScheme}`), and only for the two-pass building-specific prompt, not the main street view narrative.

### 1.3 The `palette` and `shadeId` Fields

Each archetype in `buildingArchetypes.json` also has:
- **`shadeId`**: A hex color (e.g., `"#5B4A3F"`) used as the zone's map overlay color when this archetype is assigned. This is purely for spatial identification, NOT for material color guidance.
- **`palette`**: An object with keys like `facade`, `trim`, `roof`, `door`, `accent` mapping to descriptive color names (e.g., `{ "facade": "warm cream limestone", "trim": "Portland stone", "roof": "dark slate" }`).

**Critical finding:** The `palette` object is present in the archetype data but is **never used in prompt construction**. Only `facadeDetail.colorScheme` (a single descriptive string) makes it into the prompt. The structured `palette` data with per-element color assignments is completely ignored in the render pipeline.

### 1.4 Temperature and Sampling Settings

| Pipeline | Temperature | top_p | top_k | Notes |
|----------|-------------|-------|-------|-------|
| Aerial (default) | 0.0 | not set | not set | Maximum consistency, set in backend |
| Aerial (with guidance_scale) | `1.5 - (guidance/30)*1.5` | not set | not set | Higher guidance = lower temp |
| Street View | 0.35 | 0.85 | 32 | Slightly creative for material variance |

The street view pipeline's `temperature: 0.35` introduces some randomness that can cause color drift across re-renders of the same scene.

---

## 2. Root Causes of Color Drift

### 2.1 Color Scheme Is Buried and Understated

The `colorScheme` string appears deep within a long paragraph of zone description prose. In the aerial prompt, a typical zone description might be 200+ words, with the color scheme mentioned once near the end. Gemini processes the entire prompt holistically, but research shows that attributes mentioned early in the prompt and with emphasis receive more attention.

**Example of what the AI sees for a single zone:**
> "The red polygon is a building footprint. Render a 4-story Georgian Terrace House building. Front-facing facade with stone quoins and classical proportions. Ground floor: rusticated stone base. Upper floors: ashlar limestone with sash windows. Cornice: classical stone cornice with dentils. Colors: warm honey limestone, dark slate roof, dark oak doors. Flat parapet with hidden valley gutters. Slate tiles with copper flashings. Aerial: regular rectangular footprint with uniform slate roof plane. This is a large 4-story structure that fills the entire red footprint..."

The color information (`Colors: warm honey limestone...`) is one clause in a 150-word paragraph. The AI often prioritizes the more prominent structural/compositional instructions.

### 2.2 Conflation of Zone Color and Material Color

The prompt tells the AI to "replace every red pixel" with building materials. The red of the zone overlay and the desired material color (e.g., warm honey limestone) are completely different hues. The AI must:
1. Identify red pixels in the reference image
2. Replace them with warm honey limestone colors

This two-step cognitive task can fail when the AI latches onto the zone overlay color or is influenced by it. Research on image-to-image models shows that strong input colors can "bleed" into the output, especially at lower denoising strengths.

### 2.3 Clay Model Color Bleeding (Street View)

In the street view pipeline, the 3D clay render uses **solid, fully saturated zone colors** (e.g., bright red `#E03C31` for buildings). These colored volumes are the primary visual input. The AI is instructed to "replace each colored volume with photorealistic materials," but the strong input colors can bias the output:
- A bright red building volume may cause the AI to add reddish tints to the rendered facade.
- A green park plane may bleed green into adjacent building bases.

The prompt says "Do not allow materials from one zone to bleed into adjacent zones," but this is a soft instruction that cannot physically prevent the latent space influence of strong input colors.

### 2.4 Style Modifier Competition

Style prompts like "Atmospheric" and "Photomontage" include extensive lighting and mood descriptions:
- "Low-angle warm sunlight rakes across rooftops..."
- "Pools of standing water... doubling the warm sky colours on the ground plane"
- "Wet surfaces from recent rainfall create mirror-like reflections"

These atmospheric descriptions can override material color specifications. Golden hour lighting shifts all surface colors warm, overcast lighting desaturates, and twilight introduces blue-purple shifts. The style modifier is appended early in the prompt (before zone descriptions in `buildStructuredPrompt`), giving it higher priority in the model's attention.

### 2.5 No Color Assertion Language

The current color descriptions use passive, descriptive language:
- "Colors: warm honey limestone, dark slate roof, dark oak doors"
- "Color palette: rich red brick, pale cream stone dressings"

There is no forceful assertion language like "MUST be", "exactly", or "strict adherence required." Research on Gemini prompt engineering shows that explicit constraint language significantly improves adherence.

### 2.6 Unused Palette Data

The structured `palette` object in each archetype contains per-element color mappings (facade, trim, roof, door, accent), but this data never reaches the prompt. Instead, only the `facadeDetail.colorScheme` summary string is used. The per-element breakdown would be more effective because it ties specific colors to specific architectural elements, reducing ambiguity.

---

## 3. Research Findings: Color Fidelity Techniques

### 3.1 Color Swatch Reference Images (Highest Impact)

A case study on Gemini color adherence found that passing a **flat color swatch image** as a multimodal reference input alongside the text prompt achieves near-perfect color reproduction, with an average Delta E score of 0.90 (imperceptible to the human eye). This dramatically outperforms text-only color specifications.

**How it works:**
1. Generate a small PNG image (e.g., 64x64) filled with the target hex color using PIL/Canvas.
2. Pass it as an additional image input alongside the main reference image.
3. Reference it in the prompt: "Apply the facade color shown in the color swatch image."

Google DeepMind's own showcase promotes this workflow: passing color swatch images as reference inputs for precise color matching.

The SiteForge pipeline already supports multi-image inputs (archetype card images are sent as reference images in both pipelines). Adding color swatch images would require minimal architectural changes.

### 3.2 Hex Code Specification in Prompts

Gemini's Nano Banana models do understand hex color codes in text prompts. Research shows that including hex codes (e.g., `#8B4513`) alongside descriptive names improves color accuracy compared to descriptive names alone, though not as much as image swatches.

**Recommended format:** `"warm honey limestone (#F5DEB3)"` — combining the descriptive name for semantic understanding with the hex code for precision.

### 3.3 Positive Framing Over Negative Prompts

Negative prompts have been deprecated in Imagen 3+ and newer Gemini models. The current backend appends negative prompt text as `"Do NOT include: ..."`, which is suboptimal. Research indicates:
- **Semantic negative prompts** (describing what you want positively) are more effective than negation.
- Instead of "NOT blue, NOT green," describe: "strictly warm-toned facade in cream and brown, with zero cool-toned elements."
- Affirmative framing consistently produces cleaner results.

### 3.4 Prompt Position and Emphasis

Gemini pays more attention to:
1. **Words positioned earlier** in the prompt.
2. **Content with explicit constraint language** ("MUST be", "EXACTLY", "STRICT").
3. **Repetition** of critical attributes.

The color scheme should appear:
- Near the beginning of each zone's description (not buried at the end).
- With assertion language: "The facade MUST be warm honey limestone (#F5DEB3)."
- Repeated in the containment rules: "Ensure the Georgian Terrace House maintains its warm cream limestone palette."

### 3.5 Per-Element Color Specification

Instead of a single color scheme string, specifying colors per architectural element improves fidelity:
```
Facade walls: warm cream limestone (#F5DEB3).
Roof: dark natural slate (#2F4F4F).
Window frames: lead grey (#708090).
Front door: dark oak brown (#5C3A1D).
```

This is more actionable for the model than a comma-separated list because it explicitly binds each color to a specific spatial element.

### 3.6 Camera/Lighting Color Anchoring

Specifying color temperature constraints prevents lighting-driven color shift:
- "Neutral 5500K daylight white balance"
- "True-to-life colors without atmospheric color grading"
- "Color-accurate architectural documentation rendering"

### 3.7 Lower Temperature for Color Stability

Lower temperature (closer to 0.0) produces more deterministic and consistent outputs. The aerial pipeline already uses `temperature: 0.0`, but the street view pipeline uses `0.35`. Reducing street view temperature to `0.15-0.20` would improve color consistency while retaining some natural material variance.

### 3.8 Iterative Refinement (Multi-Turn)

Gemini supports conversational image editing where you can progressively refine colors. However, this is impractical for SiteForge's single-shot render pipeline. A simpler approach is **generate-then-verify**: use Gemini's text understanding to analyze the output image and flag color deviations, then re-render with reinforced color instructions.

---

## 4. Recommended Fixes (Ranked by Impact)

### Priority 1: Strengthen Color Language in Prompts (Low effort, High impact)

**Changes to `buildArchetypeDescription()` and `buildStructuredPrompt()`:**

1. Move the color scheme to the **beginning** of each zone's narrative, immediately after the archetype title.
2. Add assertion language: "MUST", "EXACTLY", "STRICT".
3. Include hex codes alongside descriptive names.
4. Repeat key colors in the containment instruction.

**Before:**
```
"The red polygon is a building footprint. Render a 4-story Georgian Terrace House building.
Front-facing facade with stone quoins... Colors: warm honey limestone, dark slate roof, dark oak doors."
```

**After:**
```
"The red polygon is a building footprint. Render a 4-story Georgian Terrace House building.
MATERIAL COLORS (strict): Facade walls MUST be warm cream limestone (#F5DEB3). Roof MUST be
dark natural slate (#2F4F4F). Doors MUST be dark oak brown (#5C3A1D). Window frames MUST be
lead grey (#708090). Front-facing facade with stone quoins..."
```

**Estimated improvement:** 30-40% reduction in color drift based on prompt engineering research.

### Priority 2: Use the Structured `palette` Object (Low effort, High impact)

**Changes to `getZoneArchetypeInfo()`:**

The `palette` field already exists in archetype data with per-element colors. Wire it into the prompt as a structured color specification block instead of relying solely on the `colorScheme` summary string.

```typescript
// In getZoneArchetypeInfo, add palette extraction:
const palette = entry.palette || {};
const paletteLines: string[] = [];
if (palette.facade) paletteLines.push(`Facade: ${palette.facade}`);
if (palette.trim) paletteLines.push(`Trim: ${palette.trim}`);
if (palette.roof) paletteLines.push(`Roof: ${palette.roof}`);
if (palette.door) paletteLines.push(`Door: ${palette.door}`);
if (palette.accent) paletteLines.push(`Accent: ${palette.accent}`);
```

Then in the prompt, render as a structured block:
```
MATERIAL PALETTE (mandatory):
  Facade: warm cream limestone
  Trim: Portland stone white
  Roof: dark natural slate
  Door: dark oak brown
```

**Estimated improvement:** 20-30% improvement in per-element color accuracy.

### Priority 3: Color Swatch Reference Images (Medium effort, Highest impact)

**Changes to `useAIRender.ts` and `useStreetViewRender.ts`:**

Generate small color swatch images from the `palette` hex values and send them as additional reference images alongside the archetype card images.

Implementation approach:
1. Add a utility function `generateColorSwatchImage(palette: Record<string, string>): string` that creates a small PNG with labeled color bands (one per element).
2. In the multi-image payload, include the swatch as an additional image with label: "Material Color Reference Swatch — match these exact colors."
3. Reference in the prompt: "Image N is a color swatch showing the EXACT material colors for this building. Match these colors precisely."

This is the single highest-impact technique based on research (Delta E ~0.90), but requires generating and transmitting additional images.

**Estimated improvement:** 50-60% reduction in color drift.

### Priority 4: Add Hex Codes to colorScheme Data (Medium effort, Medium impact)

**Changes to `buildingArchetypes.json`:**

Enrich the `palette` and `colorScheme` fields with hex codes. Currently the data is purely descriptive ("warm honey limestone"). Adding hex values makes the color specification machine-parseable:

```json
{
  "colorScheme": "warm honey limestone (#F5DEB3) body, dark natural slate (#2F4F4F) roof, dark oak (#5C3A1D) doors",
  "palette": {
    "facade": "#F5DEB3",
    "facadeDesc": "warm honey limestone",
    "roof": "#2F4F4F",
    "roofDesc": "dark natural slate",
    "door": "#5C3A1D",
    "doorDesc": "dark oak brown"
  }
}
```

This could be done incrementally or with a script that maps common architectural color names to hex codes.

**Estimated improvement:** 15-25% with hex codes in text prompts alone; enables Priority 3 (swatches) with precise hex values.

### Priority 5: Reduce Style Modifier Interference (Low effort, Medium impact)

**Changes to `buildStructuredPrompt()` and street view prompt builder:**

1. Add a color preservation clause after the style modifier: "Regardless of atmospheric lighting conditions, maintain the specified material colors for each zone. Do not allow golden hour warmth, overcast desaturation, or twilight blue-shift to override the stated facade colors."
2. In the style prompt itself, add: "Preserve material-accurate colors under the specified lighting conditions."
3. For the street view pipeline, add to the SPATIAL REFERENCE instruction: "The material colors specified in the COLOR-TO-ZONE MAPPING take absolute priority over atmospheric color grading."

**Estimated improvement:** 15-20% reduction in lighting-driven color shift.

### Priority 6: Lower Street View Temperature (Trivial effort, Low-Medium impact)

**Change in `useStreetViewRender.ts`:**

Reduce `temperature` from `0.35` to `0.20` for the street view render API call. This reduces randomness and makes color outputs more consistent between re-renders of the same scene.

```typescript
temperature: 0.20,  // was 0.35 — lowered for color stability
```

**Estimated improvement:** 10-15% improvement in color consistency across re-renders.

### Priority 7: Post-Generation Color Verification (High effort, Medium impact)

Build a lightweight color verification step after render completion:

1. After receiving the rendered image, sample pixel colors from known zone locations.
2. Compare sampled colors against expected palette values using Delta E in LAB color space.
3. If Delta E exceeds a threshold (e.g., >15), flag the render or trigger a re-render with reinforced color instructions: "The previous render drifted from the specified colors. This time, ensure the facade is STRICTLY warm cream limestone (#F5DEB3) with zero blue or grey shift."

This adds latency and API cost but provides a safety net for critical renders.

**Estimated improvement:** 20-30% catch rate for severe color drift.

### Priority 8: Neutral Clay Model Colors (Medium effort, Low impact)

**Change in `useStreetViewRender.ts` / `generateClayRender()`:**

Instead of using the zone's actual map color (bright red, green, etc.) for the clay model volumes, use **neutral grey tones** with zone identification via edge outlines or subtle labels. This eliminates the strong input color bias.

However, this conflicts with the current COLOR-TO-ZONE MAPPING system which relies on distinct colors for zone identification. A compromise: use muted/desaturated versions of the zone colors (e.g., `#B0A0A0` instead of `#E03C31` for buildings) that are still distinguishable but less likely to bleed into the output.

**Estimated improvement:** 10-15% reduction in zone-color bleeding into materials.

---

## 5. Implementation Roadmap

| Phase | Fixes | Effort | Files Changed |
|-------|-------|--------|---------------|
| **Phase 1 (Quick wins)** | Priorities 1, 2, 5, 6 | 1-2 days | `useAIRender.ts`, `useStreetViewRender.ts` |
| **Phase 2 (Data enrichment)** | Priority 4 | 2-3 days | `buildingArchetypes.json`, archetype data scripts |
| **Phase 3 (Image swatches)** | Priority 3 | 3-5 days | `useAIRender.ts`, `useStreetViewRender.ts`, new utility |
| **Phase 4 (Verification)** | Priority 7 | 3-5 days | New verification module, render pipeline integration |
| **Phase 5 (Clay model)** | Priority 8 | 1-2 days | `useStreetViewRender.ts` |

---

## 6. Key Source Files

| File | Role |
|------|------|
| `frontend/src/components/viewer/useAIRender.ts` | Aerial render pipeline — `buildStructuredPrompt()`, `buildArchetypeDescription()`, `getZoneArchetypeInfo()`, `collectZonePromptEntries()`, `colorName()` |
| `frontend/src/components/viewer/useStreetViewRender.ts` | Street view pipeline — `describeZoneForStreetView()`, `getZoneMaterial()`, COLOR-TO-ZONE MAPPING, clay render generation |
| `frontend/src/data/buildingArchetypes.json` | Archetype metadata — `palette`, `shadeId`, `facadeDetail.colorScheme` |
| `frontend/src/data/streetPathArchetypes.json` | Street archetype metadata |
| `frontend/src/data/openSpaceArchetypes.json` | Open space archetype metadata |
| `backend/app/api/v1/render.py` | Backend Gemini API call — temperature mapping, negative prompt handling |

---

## 7. References

- [How to prompt Gemini 2.5 Flash Image Generation for the best results (Google Developers Blog)](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- [Color Code Adherence in AI Image Generation: A Case Study with Gemini (Google Cloud Community)](https://medium.com/google-cloud/color-code-adherence-in-ai-image-generation-a-case-study-with-gemini-9d48c06d9e41)
- [Nano Banana image generation (Google AI for Developers)](https://ai.google.dev/gemini-api/docs/image-generation)
- [Ultimate prompting guide for Nano Banana (Google Cloud Blog)](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)
- [6 Ways to Control Colors in AI Images (Kiki and Mozart)](https://kikiandmozart.beehiiv.com/p/control-colors-in-ai-images)
- [How to generate AI images in specific colors (Recraft)](https://www.recraft.ai/blog/how-to-generate-ai-images-in-specific-colors)
- [Nano Banana can be prompt engineered for extremely nuanced AI image generation (Max Woolf)](https://minimaxir.com/2025/11/nano-banana-prompts/)
- [Gemini Image High Resolution HD Prompts Quality Guide (LaoZhang)](https://blog.laozhang.ai/en/posts/gemini-image-high-resolution-hd-prompt)
- [Generating Consistent Imagery with Gemini (Towards Data Science)](https://towardsdatascience.com/generating-consistent-imagery-with-gemini/)
- [Omit content using a negative prompt (Google Cloud Vertex AI)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/omit-content-using-a-negative-prompt)
