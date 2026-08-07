# Park LEGO catalogue closure — Batch 23

Batch 23 closes 30 previously unmapped variants across ten community-garden,
Paris, Amsterdam and Barcelona families. Catalogue coverage advances from
379/520 to 409/520 variants; 111 variants remain.

## Families closed

| Family | Retained anchor | Newly closed variants | Parcel logic |
| --- | --- | ---: | --- |
| Enhanced community garden | Healing garden | 3 | Allotment grid, permaculture guild ring, intercultural social garden |
| Parisian place | Place Royale | 3 | Quiet cobble room, statue axis, cafe edge |
| Parisian square | Ordered tree grid | 3 | Linear edge, corner cafe, compact cobble room |
| Jardin à la française | Water axis | 3 | Clipped parterre, parallel rills, paved forecourt |
| Amsterdam Vondelpark | Pavilion garden | 3 | Neighbourhood green, cafe edge, planted corner |
| Amsterdam hofje | Gravel-cross garden | 3 | Lush communal court, pocket garden, historic lawn court |
| Amsterdam plein | Brick market plein | 3 | Glass canopy, cafe threshold, open brick room |
| Barcelona pati interior | Green fountain pati | 3 | Lawn court, social paved court, shade court |
| Barcelona plaça xamfrà | Planted corner | 3 | Cafe corner, clear corner, active corner |
| Barcelona superilla | Coloured green rooms | 3 | Plaza planters, green corridor, social garden |

## Method

- The four local catalogue images for every parent were reviewed together.
- Buildings visible in the reference images remain separate building-family
  work; they are not embedded in park recipes.
- People are not rendered. Their reference scale informed bed, table, canopy,
  path and tree spacing.
- Thirty material families were compiled from exact local reference-image
  statistics into six procedural roles: paver, lawn, asphalt, planting,
  safety and timber.
- No source pixels were projected, no AI draping was used, and no image API
  calls were made.
- Every missing selection has an explicit backend capability, frontend LEGO
  mapping, appearance kit, planting structure and additional program component.
- Variant-aware renderer branches change site composition as well as texture.
  Recipes adapt counts and spacing to the drawn parcel instead of reproducing
  the reference photograph verbatim.

## Live City Prompt trial

The 42 × 37 m project polygon was compiled one park at a time as
`community_garden_enhanced / garden_classic_allotment`, beside the separately
compiled Parisian building family. Generate to 3D reported one assembled
building, one compiled park and zero skipped families. The park used
`park_kit`; no AI drape was invoked.

The first pass was rejected because the allotment read as shallow pads on a
dark field. The accepted recipe raises the kit above the flattened parcel,
adds twelve regulation-like plot modules, visible crop rows, four small
support sheds, an orchard edge and planted perimeter bands. This browser
review directly changed the shared community-garden methodology.

## Review assets

- `park_lego_batch23_city_family_sheet.jpg` — all 30 source images beside the
  six compiled role swatches.
- `city_prompt_classic_allotment_live_trial.png` — accepted live City Prompt
  LEGO trial with a separately compiled building.

The earlier intermediate browser captures are retained only when useful for
diagnosis; the two files above are the intended review deliverables.
