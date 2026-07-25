# Image Card Library — Claude Code Instructions

## What this session does

You have a folder of reference image cards used to style AI architectural
renders. This session will:

1. Read every image in the cards folder
2. Assign structured metadata to each one using the schema in imageCardSchema.ts
3. Produce a complete imageCardLibrary.ts file with all cards catalogued
4. Identify gaps in the library and produce imageCardWanted.ts with briefs
   for missing card types
5. Flag any cards that are low quality or poorly suited as AI render references

---

## Files involved

| File | Location | Action |
|---|---|---|
| `imageCardSchema.ts` | `src/data/imageCardSchema.ts` | Already placed — read this first |
| Image cards folder | `src/assets/cards/` | Read every image in here |
| `imageCardLibrary.ts` | `src/data/imageCardLibrary.ts` | Create this — full catalogued library |
| `imageCardWanted.ts` | `src/data/imageCardWanted.ts` | Create this — gap analysis |

---

## Step by step

### Step 1 — Read the schema
Read `imageCardSchema.ts` completely before doing anything else. Understand:
- All allowed taxonomy values (TYPOLOGIES, MATERIALS, HEIGHTS etc.)
- The ImageCard interface — every field must be populated
- The WantedCard interface — used for gap-filling entries
- The SEED_CARDS and SEED_WANTED_CARDS — use these as style reference

### Step 2 — Catalogue every image
For each image file in `src/assets/cards/`:

Open and examine the image carefully. Then assign:

**typology** — What building type is this? Pick the closest match from TYPOLOGIES.

**primaryMaterial** — What is the dominant facade material? Pick from MATERIALS.
If two materials share roughly equal prominence, assign the more visually
dominant one as primary and the other as secondaryMaterials.

**height** — How many storeys does the building appear to be? Pick from HEIGHTS.

**context** — What is the surrounding urban context? Pick from CONTEXTS.

**climate** — What climate does the vegetation and sky suggest? Pick from CLIMATES.

**lightingCondition** — What is the lighting? Pick from LIGHTING_CONDITIONS.

**renderAngle** — What angle is the image shot from? Pick from RENDER_ANGLES.
IMPORTANT: Cards shot from eye level (street perspective) should be flagged
with a note — they are less effective as references for aerial oblique renders.

**style** — Is this photorealistic, a CGI render, a sketch etc? Pick from STYLES.

**mood** — Overall colour temperature and feeling. Pick from MOODS.

**ipAdapterStrength** — Recommend a value between 0.3 and 0.9:
- Strong single-material cards (full glass, corten): 0.45–0.55
- Moderate complexity (brick + glass): 0.55–0.7
- Subtle or neutral palette: 0.65–0.8
- Masterplan / multi-building: 0.45–0.6 (scale mismatch risk)

**depthStrength** — Recommend a value between 0.7 and 0.95:
- Strong pattern or texture that might compete with geometry: 0.7–0.8
- Clean facades with clear geometry: 0.8–0.9
- Simple massing studies: 0.85–0.95

**promptBooster** — Write a short phrase (under 20 words) of material and
texture keywords that reinforce this card's visual character. These are
appended to the AI render prompt automatically. Focus on words the model
responds well to: material names, surface qualities, light descriptions.
Example: "hand-set terracotta brick, arched openings, warm ochre tones, deep shadow reveals"

**quality** — Score 1–5:
- 5: Ideal reference. Clear material, good angle, strong lighting, high resolution.
- 4: Good reference. Minor issues (slightly low res, minor angle mismatch).
- 3: Usable but not ideal. May produce inconsistent results.
- 2: Poor reference. Wrong angle, unclear material, or low resolution.
- 1: Do not use. Flag for removal.

**tags** — Add 4–8 freeform lowercase tags useful for search and filtering.

**notes** — Add any observations about render performance, limitations, or
specific use cases this card works well for.

### Step 3 — Write imageCardLibrary.ts
Create `src/data/imageCardLibrary.ts` with this structure:

```typescript
import { ImageCard } from './imageCardSchema';

export const IMAGE_CARD_LIBRARY: ImageCard[] = [
  // One entry per image card, fully populated
];
```

Use the actual filenames from src/assets/cards/ in the filename field.
Assign a consistent id slug: lowercase, hyphens, descriptive.
Example: "warm-brick-midrise-nashville-01"

### Step 4 — Gap analysis
After cataloguing all cards, compare the library against the taxonomy to
find missing coverage. Look specifically for:

**Missing typologies** — Are any building types completely absent?

**Missing materials** — Are any common facade materials unrepresented?

**Missing angles** — Are all cards eye-level when aerial-oblique is needed?
This is the most common and most important gap to flag.

**Nashville-specific gaps** — Are there gaps relevant to Nashville's context:
- Cumberland River waterfront
- SoBro / Gulch high-rise
- East Nashville / Wedgewood-Houston industrial adaptive reuse
- Suburban infill residential

**Climate mismatch** — Are cards from nordic or arid contexts being used for
a humid subtropical city? Flag these.

### Step 5 — Write imageCardWanted.ts
Create `src/data/imageCardWanted.ts` with this structure:

```typescript
import { WantedCard } from './imageCardSchema';

export const WANTED_CARDS: WantedCard[] = [
  // Start with SEED_WANTED_CARDS from imageCardSchema.ts
  // Add new entries for every gap you identify
];
```

For each wanted card, write a clear brief describing exactly what the ideal
image looks like — angle, material, lighting, context, approximate resolution.
Include a rationale explaining why this gap matters for the Nashville use case.

Mark priority:
- high: Commonly needed typology with zero coverage
- medium: Useful typology with weak coverage (1 low-quality card)
- low: Niche typology, nice to have

### Step 6 — Summary report
After completing the files, print a short summary:

```
CARD LIBRARY SUMMARY
────────────────────
Total cards catalogued: X
Quality 4–5 (recommended): X
Quality 3 (usable): X
Quality 1–2 (flagged for review): X

Angle breakdown:
  aerial-oblique-mid: X
  aerial-oblique-low: X
  eye-level-street: X  ← these need replacing
  other: X

Top gaps identified: X wanted cards added
High priority gaps: X
```

---

## Quality flags to watch for

Flag these in the notes field and set quality: 1 or 2:

- **Eye-level street photos used as aerial reference** — angle mismatch
  will confuse IP-Adapter conditioning
- **Images with people as the dominant subject** — the model will try
  to reproduce the people rather than the building character
- **Night-only images** — hard to use as reference for daytime renders
- **Low resolution** — anything that appears under ~800px on the longest edge
- **Heavy post-processing / filters** — Instagram-style editing confuses
  the model's material read
- **Images showing multiple strongly contrasting buildings** — the model
  averages them, producing muddy results

---

## Final file structure expected

```
src/
  assets/
    cards/           ← your image files (unchanged)
  data/
    imageCardSchema.ts     ← already placed
    imageCardLibrary.ts    ← CREATE THIS
    imageCardWanted.ts     ← CREATE THIS
```
