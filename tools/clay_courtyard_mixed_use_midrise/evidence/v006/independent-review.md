# Independent RLASM v6.1 holistic review: courtyard v006

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The v005 blockers are fixed in the pixels, but the two wings are still drawn as mirror twins with a centred courtyard, where the front and top sources both show a much wider west wing and a courtyard and stair set east of centre. The glass close-up is also aimed at a tree trunk instead of the glazing.

**Counts: P0 = 0, P1 = 2, P2 = 10**

Coordinates are pixels in the 1440x1080 renders and in the native source images (front 1024x768, oblique 1195x896, top 1376x768).

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | top.png (wings x310-585 and x855-1130, courtyard x585-855); front.png (left wing x303-590, right wing x848-1137); aerial.png; board phone-01 | **The plan is symmetrical, but the sources are not.** In the render both wings are 275 px wide and the courtyard and stair sit on the centreline. In sources/top.jpg the west wing roof is about 305 px wide (x265-570) and the east wing about 215 px (x850-1065), so the west wing is about 1.4 times wider. The courtyard is centred near x710 against a building centre near x665, so it sits east of centre. sources/front.png shows the same thing: the west wing face is about 340 px wide (x50-390) against about 240 px for the east wing (x640-880), and the stair sits right of centre (x450-610). The render's silhouette and courtyard position do not match either source. | The wings were built as one parametric module mirrored about the centreline. | Widen the west wing to about 1.4 times the east wing (for example 0.36 / 0.31 / 0.33 of frontage for west wing / courtyard / east wing, from the top.jpg ratios). Shift the courtyard and stair east to match, keeping the east wing's street face fixed. Then re-render front, top, aerial and front_corner. |
| 2 | **P1** | glass_close.png (whole frame; trunk x700-900 full height, canopy y0-430) | **The camera is blocked.** A low-poly street-tree trunk fills the centre of the frame and the canopy fills the top 40%. The storefront glazing, mullions and returns this view should show appear only in slivers at the sides, so glass depth and frame returns cannot be judged. v005 already flagged a tree in this view; in v006 it has become the subject of the frame. | The camera target or position was not checked against street-tree placement. | Move the glass_close camera to a storefront bay with no tree in front (for example the east-face retail bay at the SE corner), or hide the trees for this one detail view. Frame the mullion and head/jamb returns with nothing in the way. |
| 3 | P2 | front.png (penthouses x318-600 / x848-1120, y352-415); roof_terrace.png (x570-1060, y440-700) | The penthouse walls are flat beige with two small windows. The sources show cedar-clad penthouse fronts with large black-framed glazing. | Material assignment | Put cedar on the penthouse south and courtyard faces and widen the glazing. |
| 4 | P2 | roof_terrace.png (eave x565-1090, y440-590); top.png (y755-785); aerial.png | The penthouse roof slabs are thin with a white edge and soffit. The source shows a deep dark slab with a cedar soffit. | Slab edge material | Make the fascia dark and the soffit cedar, and thicken the slab edge. |
| 5 | P2 | top.png (decks x315-580 / x860-1125, y785-860) | The wing terrace decks are pale grey (about RGB 164,161,157). sources/top.jpg shows warm cedar decking (x270-570 / x845-1035, y555-625). | Deck material | Use a cedar deck colour. |
| 6 | P2 | facade_close.png; balcony_close.png; architecture_close.png | The ribs are wide-spaced panel seams plus short ticks at the spandrels. The source cladding has dense fine vertical ribs. | Rib pitch too large | Cut the rib pitch to about 150-200 mm. |
| 7 | P2 | courtyard_stair.png; top.png (x655-785, y710-865) | The stair is a single straight concrete flight on the centreline, with no landing and no cedar seating tiers. The source has cedar bench tiers beside the stair, hugging the east side of the opening. | Simplified stair module | Add cedar tiers on the stair's east side and move the stair with the courtyard shift from #1. |
| 8 | P2 | front.png (right wing windows x975-1090); retail_corner.png; cladding_contact.png | The corner-bay windows on the east wing's south face are wide landscape pairs. The source shows portrait-proportioned windows. | Window module | Use portrait proportions, about 1:1.4. |
| 9 | P2 | top.png; front.png (courtyard tree x620-690) | The courtyard planting and rooftop units do not match the top.jpg layout. The source has a central planter and tree and wing units along the courtyard edge. In the render the east wing's unit is at the outer edge. | Placement | Move them to match top.jpg. |
| 10 | P2 | facade_close.png (x915, y225-235); balcony_close.png (x670-680, y325-345) | There are pure-black bands at the heads and left jambs of the recessed balconies. They read as gaps rather than frames. | Recess edge geometry or shadow gap | Close the gap, or give the band the frame colour. |
| 11 | P2 | top.png | The plan is a plain rectangle. sources/top.jpg shows a slight northward projection at the middle of the rear bar (x440-920, y70-130). | Footprint | Add the projection. |
| 12 | P2 | boards/phone-01-source-vs-render.png | The board pairs the SE oblique source with front_corner, which is shot from the SW (blank west wall at left). aerial.png is the SE match. | Board pairing | Pair the oblique source with aerial, or move the front_corner camera to the SE. |

**Checked and not raised.** The upper storeys of the east face (right_side.png, aerial.png) are a taupe panel over a dark retail base. I first suspected a material defect there, but sampling the source pixels rules it out: the oblique's sunlit east face is a warm taupe panel (about 146,129,109) and only the south faces read near-black. The render conforms.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | **deviates**: the wings are symmetric where the source west wing is about 1.4 times wider (#1) | front, top vs sources/front, sources/top |
| Storey count | conforms: retail plus 3 residential storeys plus a set-back penthouse on the wings; the rear bar has 4 balcony levels plus a roof | front, right_side, courtyard_stair |
| U-plan and courtyard | partly conforms: the U opens south over a raised courtyard, but the courtyard is centred, not offset east (#1) | top, aerial |
| Street stair | partly conforms: a wide concrete stair from the sidewalk with rails, but no cedar tiers and in the wrong lateral position (#7) | courtyard_stair, top |
| Balconies and cedar reveals | conforms: recessed with cedar reveals and glass balustrades on the south faces and courtyard faces | facade_close, balcony_close, courtyard_stair |
| Window rhythm | mostly conforms: west wing 4 portrait columns plus a balcony stack; east face 6 columns; corner-bay window proportion is off (#8) | front, right_side, facade_close |
| Penthouses and terraces | conforms in geometry: set back, with decks about 5-6 m deep and open to the sky; the finish is off (#3, #4, #5) | roof_terrace, top, front |
| Retail base | conforms: dark storefront base with black-framed glazing on both street faces | front, retail_corner, cladding_contact |
| Materials hierarchy | mostly conforms: dark ribbed metal on the south street faces and the rear, taupe east face, tan and cedar courtyard faces; ribs are sparse and the penthouses are not cedar (#3, #6) | front, aerial, right_side, architecture_close |
| North and west faces | not visible in any source; they are coherent with the visible grammar (dark ribbed, tan top storey, blank party wall) | rear, left_side, rear_lane |

## 4. Camera validity

- **glass_close.png: invalid.** A street tree blocks the target (#2).
- front_corner.png is valid but faces the SW, so it is the wrong match for the SE oblique source; aerial.png covers that role (#12).
- All other views are legible and unclipped: front, aerial, top, left_side, right_side, rear, rear_side, facade_close, architecture_close, courtyard_stair, retail_corner, balcony_close, roof_terrace, cladding_contact, interior and rear_lane.

## 5. v005 findings: status in the v006 pixels

| v005 finding | sev | status | evidence |
|---|---|---|---|
| Rear bar's floating roof slab not visible | P1 | **resolved** | front.png x600-840 y375-385: a dark slab with fascia and three posts. Also visible in aerial.png, roof_terrace.png and courtyard_stair.png. |
| Wing roof terraces were a 1.5 m ledge | P1 | **resolved** | top.png: decks about 75 px deep beyond a 30 px eave, roughly 5-6 m, with the outer part open to the sky. Also roof_terrace.png. |
| Wing courtyard faces dark ribbed instead of tan and cedar | P1 | **resolved** | courtyard_stair.png and front.png: the courtyard faces are tan panel with cedar recessed balconies. |
| Black crevice under right wing roof slab over rear-bar roof | P1 | **resolved** | aerial.png and rear_side.png: no black void at the wing-to-rear-bar junction. |
| Rear walkway near-black from above | P2 | resolved | top.png: the rear bar slab and walkway read pale. |
| Three roof tones | P2 | resolved | top.png and aerial.png: one roof grey with a tan parapet. |
| Penthouse walls beige not cedar; pale slab edges | P2 | **not resolved** | #3, #4 |
| Sparse ribs | P2 | **not resolved** | #6 |
| Stair without wood seating tiers or mid-flight landing | P2 | **not resolved** | #7 |
| Plant positions | P2 | partly | #9 |
| Tree in the glass close-up | P2 | **not resolved, now worse**: raised to P1 camera defect | #2 |
| Corner bay rhythm | P2 | partly: the count matches but the proportion is wrong | #8 |
