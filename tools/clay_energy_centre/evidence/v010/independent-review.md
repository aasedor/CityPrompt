# Independent holistic review: clay energy centre v010 (RLASM v6.1)

Reviewer: independent (not the builder). Evidence: the 3 locked sources, all 18 renders at full resolution, and the 4 phone boards, opened with Read. I did not use any build report, builder note, metadata or hash as proof.

## 1. Verdict

**PASS_ZERO_P0_P1**: the pixels show the full source identity, with correct topology, storeys, bay rhythm and roof plant, and the v009 P1 is fixed (the concrete bands now meet level at the identity corner). Only polish items remain.

Counts: P0 = 0, P1 = 0, P2 = 9

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| - | P0 | - | None found. | - | - |
| - | P1 | - | None found. | - | - |
| 1 | P2 | front (lower wall y 456-833 against corten y 372-833); left_side | The lower volume reads about 12-15 % short against the corten block compared with the locked front. This was carried over from v008/v009 and downgraded because the locked front and top disagree on it. | The lower-volume height was chosen as a compromise between the sources. | Optional: raise the lower parapet about 0.5-1 m if a later version is allowed. |
| 2 | P2 | top (corten 740-1105 x 178-900 against lower 335-740 x 178-900) against source top (corten 168-722 against lower 190-712) | The corten block is exactly as long north-south as the lower volume. In the source it projects slightly past it at both ends. | Both volumes share one footprint depth. | Lengthen the corten block about 2-4 % at its north and south ends. |
| 3 | P2 | top (flue cluster at about 600,635); roof_plant | The three-flue cluster sits south of centre. The source top puts it nearer the centre of the lower roof (about 548,520), just east of the hourglass stack. | Placement offset. | Move the flue plinth about 8 % of the roof depth north. |
| 4 | P2 | stack_contact (800-890, 490-650); roof_plant (940-1000, 420-600) | The flues have dark conical rain caps. The source flues read as plain open silver pipes. | Cap geometry was added. | Drop the caps or tint them in the flue colour. |
| 5 | P2 | front (735-748 x 460-830); front_corner (880-890, 640-760 in the 2x crop) | A thin buff-brick strip separates the south glazing from the corten block. In the source front the south glass band runs straight into the corten. | The brick frame return was carried around the east end. | Trim the east end pier to the frame thickness or remove it. |
| 6 | P2 | corten_block (848-1092 x 75-1080) | The slot window has a dark return on its left jamb only. The glass reads nearly flush, so its depth is weak in close-up. | The glass inset is shallow. | Inset the slot glass about 150-200 mm and add a visible head/jamb return. |
| 7 | P2 | plant_window; interior; glass_close | The plant showcase holds sparse massing (one teal box, two pipe runs, plain boxes). The source shows dense teal pumps and pipework behind the glass. It is legible as plant, but thin. | Low interior plant count. | Add 2-3 more pump/manifold masses and vertical pipe drops in each glazed bay. |
| 8 | P2 | rear_service (620-935 x 485-500) | A light grey sliver shows at the top-left of the louvre opening. The louvre has depth, but its top blade/frame does not close the void. | The louvre frame is shorter than the opening. | Extend the top frame or blade to the head of the opening. |
| 9 | P2 | front (role match) | The front render is a square-on south elevation. The locked front is a south-west corner perspective, and front_corner carries that comparison. | The camera role definition. | Optional: tilt the front camera about 25-30 deg toward the west to mirror the source. |

## 3. Source conformance checklist

| Item | Status | View used |
|---|---|---|
| Silhouette (low two-storey brick volume on the west, taller corten block on the east, stack rising well above both) | conforms (lower height P2 #1) | front, front_corner, aerial, rear |
| Storey count (lower volume two storeys, corten one tall block) | conforms | front, left_side |
| Bay rhythm and glazing (west face: door bay with clerestory, tall glazed entrance bay, brick pier, corner bay with glass/concrete/glass; south face: continuous upper band, two lower bays with a pilaster and a door at the east end) | conforms | left_side, front, front_corner against source front/oblique |
| Concrete panel (corner bay and south band, level datums) | conforms. Measured: west corner bay concrete 32-64 % of wall height (y 609-732 on a 470-855 wall); south face 32-65 % (y 589-712 on a 456-833 wall); west upper glass about 24 % of the wall | left_side, front, front_corner |
| Entrance (recessed glazed doors with a dark canopy in the west face, brick jambs with returns) | conforms | glass_close, corner_entry, left_side |
| Corten block and slot (dark vertical-seam cladding, narrow tall slot, louvre on the west face above the lower roof) | conforms (slot depth P2 #6) | front, architecture_close, corten_block |
| Roof plant and stack (two three-fan banks on the west edge, duct runs, three-flue cluster, hourglass-framed stack on a plinth, two units on the corten roof) | conforms (flue position and caps P2 #3, #4); all parts sit on plinths or supports with no floating parts | top, roof_plant, stack_contact, aerial |
| Materials hierarchy (buff brick frame > glass plant showcase > board-formed concrete panels > dark corten > pale membrane roof) | conforms | front_corner, facade_close |
| North and east faces (no source) | coherent: corten and brick with a service door and louvre, same grammar | rear, rear_side, right_side, rear_service |

## 4. Camera validity

No view is invalid. In every view the target is unoccluded, unclipped and legible. The trees partly overlap the west corner bay's lower glass in front_corner and the corten slot base in corten_block, but they hide no identity element. facade_close, architecture_close and the detail views crop deliberately and keep their subjects legible.

## Previous-version findings

- **v009 P1 (concrete bands misaligned across the identity corner):** RESOLVED in the pixels. In left_side the west corner bay's concrete runs from 32 % to 64 % of the wall height, and the upper glass band is about 24 % of the wall, not the old 11 %. In front the south band runs from 32 % to 65 %. In the front_corner close crop the two bands meet level on either side of the brick corner pier, which matches the source oblique and source front.
- **v008 lower-volume height (downgraded to P2 in v009):** unchanged at about 12-15 % short, so it stays P2 (#1).
