# Independent RLASM v6.1 holistic review — energy centre clay candidate v003

Reviewer: independent (did not build). Judged only rendered pixels against the three locked sources
(`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). All 18 renders, the 3 sources and the
4 phone boards were opened at full resolution; enlarged crops were made of the entrance, the stack, the
interior column base and the source roof/entrance regions for pixel checks. Builder notes, counts and
hashes were ignored.

Status of the v002 findings, verified in pixels:

| v002 finding | v003 status | where verified |
|---|---|---|
| P0 south face of the glazed block open for a third of its length | FIXED — the short face is fully enclosed: corner pier / concrete bay / pier / narrow glazed bay / pier / corten | front, facade_close, front_corner |
| P0 no board-formed concrete corner panel | FIXED — lined concrete panel in the middle band of the corner bay on both faces, brick corner pier between | front, front_corner, facade_close, architecture_close, plant_window |
| P0 no public entrance on either street face | FIXED as program (glazed double door in the tall glazed bay of the street face) — but its expression introduces new defects (findings 1 and 3 below) | corner_entry, glass_close, left_side, front_corner |
| P1 uniform bay rhythm | FIXED — street face reads end bay / tall glazed bay / wide concrete corner bay; short face reads wide concrete bay / narrow glazed bay | left_side, front, front_corner |
| P1 brick frames reading as detached screens past the corner and above the roof | FIXED for the brick — parapet band meets the roof membrane with no gap and the corner pier is solid; but a NEW detached white blade now stands in front of the entrance (finding 3) | front_corner, architecture_close, stack_contact |

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the three v002 P0s are genuinely fixed in the pixels, but the new entrance
introduces a floating threshold slab and an invented freestanding white blade-and-canopy that no source
shows, and the interior view exposes a plant-room column that does not reach the floor.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P0 | corner_entry (x≈600–900, y≈795–830), glass_close (x≈215–500, y≈930–970); also visible small in front_corner and left_side | A thin white slab under the entrance fin/door hovers above the pavement: a continuous dark shadow gap runs under its full length and its far (right) end is lifted clear of the paving with a wedge of shadow beneath — the slab is tilted/floating, not sitting on the pavement | Threshold/plinth object placed with its origin above pavement level and a small rotation; never snapped to the pavement plane | Delete the slab, or set its base flush to the pavement z and zero its rotation so all four edges contact the paving; re-render corner_entry and glass_close |
| 2 | P0 | interior (x≈470–530, y≈900–965) | The round plant-room column ends short of the floor: its bottom end-cap is visible as a lit rim and its floor shadow is a detached blob ~30 px below the column, with clean floor between — the column floats | Column cylinder sized from its centre with insufficient height, or interior floor slab placed above the column base | Extend the column to the slab (base at floor z, top through the ceiling); confirm the base shadow is contiguous with the column in a re-render |
| 3 | P1 | corner_entry, glass_close, front_corner (x≈420–460, y≈600–830), left_side (x≈665–680) | A freestanding white blade (one bay-mullion wide) rises from the pavement to the glazing head in front of the glass, with a flat white cantilevered canopy pinned to it at door-head height; the blade's top is a free end against the glazing. Nothing in front.png shows this — the source entrance (front.png x≈290–360, y≈560–640) is a dark-framed storefront double door set slightly under a dark soffit within the glazed bay, with no fin and no canopy. The blade reads as the detached-screen grammar v002 flagged, now at the most important street element | Entrance modelled as an added fin + canopy + door assembly instead of as a door within the curtain wall | Delete the blade and the canopy; keep the double door inside the glazed bay, recessed ~0.3 m with a dark head/soffit panel matching the source; re-render corner_entry, glass_close, left_side, front_corner |
| 4 | P1 | left_side (x≈285–400, y≈705–820; window x≈280–470, y≈560–640), front_corner (x≈290–350, y≈640–720) | The end bay of the street face renders as a near-flush pale rectangle with no door leaf and no legible recess depth, under a small 6-pane window. front.png (x≈130–280, y≈380–640) shows a deep concrete-lined recess with a tall door leaf and a broad glazing band filling most of the bay above it — an opening without visible depth/returns and a reduced upper opening | Recessed entrance/service bay built as a shallow inset plane; upper glazing sized as a small window | Recess the lower bay ~1.0–1.5 m behind the brick frame with concrete reveals and a tall door leaf; widen the upper window to the band width in the source |
| 5 | P2 | stack_contact, roof_plant, front | Stack lattice is a single cone of four straight struts from a base pad to mid-stem; the source's X-braced hourglass cage with a square collar at the top is absent, so at close range the stack reads as a cylinder on a tripod | Simplified cage | Add the upper flare and square collar so the cage widens again at the flue |
| 6 | P2 | top | Corten footprint is flush with the brick block north and south; top.jpg shows it projecting ~7% beyond the brick block at both ends | Footprint simplified | Extend the corten block ~1 bay-module N and S |
| 7 | P2 | top, aerial | Corten roof single-fan unit sits at ~80% along the block (south end); top.jpg has it mid-roof | Placement | Move the unit to mid-roof |
| 8 | P2 | top | Hourglass stack sits close to the south cooling bank; top.jpg has it centred between the two banks | Placement | Centre the stack between the banks |
| 9 | P2 | front, facade_close | Narrow glazed bay on the short face is ~40% of the concrete bay width; front.png shows only a thin glazed strip (~10%) between the concrete bay and the corten | Bay proportion | Narrow the bay |
| 10 | P2 | corten_block, front, right_side | Corten is a bright saturated orange with a square panel grid (vertical and horizontal joints); the source is dark rust-brown vertical standing seam only | Palette and joint pattern | Darken to the source rust tone; vertical seams only |
| 11 | P2 | roof_plant | The three slender flues rise out of the top of the horizontal duct instead of from their own base plate beside it (top.jpg) | Placement | Seat the flues on a base plate next to the duct |
| 12 | P2 | left_side, front_corner | End-bay upper window is a small punched opening; source shows glazing across most of the bay width (see finding 4) | Sizing | Covered by fix 4 |

## 3. Source conformance checklist

| item | status | view used / evidence |
|---|---|---|
| Silhouette (two volumes, lower brick frame + taller corten block, roof plant above the brick block) | conforms | front_corner vs front.png / oblique.jpg; top vs top.jpg (corten ~45–47% of the width, proportion matches). Minor: corten flush N/S instead of projecting (P2 #6) |
| Storey count (two storeys in the brick block: plant glazing / concrete band / clerestory; interior stair and upper gallery) | conforms | front, left_side, corner_entry vs front.png |
| Bay rhythm and glazing | deviates (P1 #4, P2 #9, #12) | left_side / front_corner vs front.png: street face end bay / tall glazed bay / wide concrete corner bay is right in count and order; the end bay's recess and glazing band are wrong. Short face narrow bay too wide |
| Concrete corner panel (board-formed, middle band, wrapping both faces around a brick corner pier, clerestory above) | conforms | front, front_corner, facade_close, architecture_close, plant_window vs front.png / oblique.jpg |
| Entrance | deviates (P0 #1, P1 #3, P1 #4) | corner_entry, glass_close vs front.png x≈130–360: door exists in the right bay but with an invented fin/canopy and a floating threshold slab; the recessed concrete bay is flat |
| Corten block and slot | conforms | front, architecture_close, corten_block vs front.png: slot in the far third of the south face, runs from the upper band to near ground, has a reveal and internal transoms. Colour/joint pattern P2 #10 |
| Roof plant and stack (two 3-fan banks on the west edge, I-shaped duct run, 3 flues, hourglass stack; corten roof: 3-fan unit + 1-fan unit + small box) | conforms with P2s (#5, #7, #8, #11) | top vs top.jpg; roof_plant, stack_contact vs oblique.jpg. All elements present, counts match, stack base pad contacts the roof |
| Materials hierarchy (buff brick frame / lined concrete / dark-mullioned glazing / corten / pale plant) | conforms | front_corner, facade_close; corten tone is lighter and more saturated than the source (P2 #10) |
| North and east faces | not visible in any source; coherent (blank corten/brick with a louvre and a door each) | rear, rear_side, right_side, rear_service |

## 4. Camera validity

All 18 renders have a legible, unoccluded, unclipped target. Notes:
- `front` is a flat elevation of the short face rather than the source's corner perspective; `front_corner` carries the oblique-matching role, so coverage is complete.
- `interior` is a valid camera (glazing, column and plant massing all legible) — it is the view that exposes finding 2.
- `stack_contact` shows the stack base pad meeting the roof clearly; the three flues' bases are hidden behind the duct in this view but are visible in `roof_plant`.
- `corten_block`, `rear_service`, `plant_window`, `glass_close`: targets fill the frame with visible reveals; no clipping.
- Boards `phone-01` to `phone-04` reproduce the renders at reduced size and add no information; findings 1–3 are visible on them only as small artefacts, which is why full-resolution reads were used.

Counts: P0 = 2, P1 = 2, P2 = 8.
