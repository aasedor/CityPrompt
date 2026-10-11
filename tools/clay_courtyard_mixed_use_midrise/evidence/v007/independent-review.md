# Independent RLASM v6.1 holistic review: courtyard v007

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: P0 = 2, P1 = 1, P2 = 6. The v006 plan asymmetry and the glass_close camera are now fixed. However, the east street elevation and every courtyard-facing wall are smooth beige render rather than dark ribbed metal, and the rooftop units float above the roof.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P0** (source identity / material) | right_side (whole facade x 320-1120, y 320-690); architecture_close (x 740-1440); retail_corner and cladding_contact (x 740-1440, y 0-690); aerial (x 790-1080, y 440-800); rear_side (left face x 290-620) | The entire east street elevation above the retail base (three residential storeys plus the top storey) is flat, unribbed, pale beige/tan. The dark ribbed cladding stops at the SE corner arris (architecture_close x~740), so the street front reads as a thin dark skin on a beige stucco block. | The east-wing side-wall material slot is assigned the penthouse/beige material instead of the ribbed dark metal. The rib geometry is only generated on the south front and the north (rear) faces. | Apply the dark vertical-ribbed metal (with the same rib pitch and the stub-rib window heads used on the south face) to the full east elevation, floors 2-5. Keep it continuous round the SE corner. Source oblique (x 880-1030, y 220-700) and source front (x 900-1000, y 120-520) show the east face dark ribbed right up to the roof. |
| 2 | **P0** (contact / floating parts) | roof_terrace (units at x 205-400 y 215-335, x 585-810 y 205-300, x 890-1045 y 140-215, small boxes x 400-440 y 240-275); front_corner (x 390-480 y 365-420, x 560-675 y 310-380); aerial (x 625-695 y 265-325) | The rooftop mechanical units hover above the roof membrane. There is a lit strip of roof between the bottom of each unit and its soft shadow, which falls detached 10-60 px below and in front of the box (very clear in roof_terrace under the left unit at y 335-390). | The unit base z is offset above the roof slab top, or it uses the parapet height instead of the deck height. | Seat every rooftop unit (and its small companion boxes) on the roof deck, with z equal to the deck top, or add curbs or plinths that reach the deck. Re-render roof_terrace and front_corner and confirm that the shadow attaches to the base. |
| 3 | **P1** (material / coherence) | courtyard_stair (west inner face x 0-420, east inner face x 1020-1440, y 0-460); front (inner returns x 640-660 and 870-893, y 360-620); aerial and front_corner (courtyard walls); top-storey band on the rear and left_side and rear (beige band y 320-440) | The courtyard-facing walls of both wings and of the rear bar's end walls are smooth beige with punched windows. Cedar appears only inside the balcony recesses. | The same beige material slot as finding 1 is used for all non-street walls. | Clad the courtyard-facing walls in dark ribbed metal and keep cedar only in the balcony reveals and soffits. Source front x 390-490 (inner face of the west wing) and x 640-660 (east wing) show dark ribbed walls with cedar only at the recessed balconies. Optionally, use warm cedar (not pale beige) for the penthouse south fronts. |
| 4 | P2 | front (y 350-362), roof_terrace (x 565-1165 y 420-590) | The penthouse roof edge is a thin light-grey or dark slab. The source has a deep cantilevered dark eave with a cedar soffit and an upturned profile (source front x 120-390 y 150-215, x 650-920 y 95-190). | Thin fascia primitive | Thicken and extend the eave by about 1.2-1.5 m, make it dark, and add a cedar soffit plane. |
| 5 | P2 | top (stair x 705-835, courtyard x 640-900) | The stair is centred in the courtyard notch. In the source top view (x 680-805 inside courtyard x 575-850) it sits in the east half, with cedar stepped seating along its east side and a planted terrace to its west. | Stair centred on the courtyard axis | Shift the stair about 1.5 m east, add cedar bench steps on its east flank and a planted landing to its west. |
| 6 | P2 | top, courtyard_stair | The courtyard furnishing is sparse (one tree, one planter, two benches). The source has a central timber planter with a tree, tables, an umbrella and a perimeter planting bed. | Minimal entourage | Add 3-4 tables, an umbrella and a perimeter planter as simple masses. |
| 7 | P2 | right_side (x 500-1120, y 690-800), cladding_contact (x 1120-1440) | The east ground floor beyond the corner bay is mostly blank dark wall with a single door and window. The source oblique shows the cafe glazing wrapping 2-3 bays, then the mural wall (x 850-1010). | Storefront wrap shortened | Extend the storefront by 1-2 bays on the east face. Leave the remainder as a solid mural-wall panel. |
| 8 | P2 | front (x 320-640 and 895-1120, y 365-415) | The penthouse south fronts are pale beige rather than the warm cedar of the source (source front x 160-380 y 200-245). | Shared beige material | Use the cedar palette colour on the penthouse front faces. |
| 9 | P2 | balcony_close (x 1010-1430, y 270-295, 740-770) | The balcony slab edges are bright white bands. The source slab edges are dark metal fascias. | Light concrete material on the slab edge | Use a dark fascia material on the balcony slab edges. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (two street-end blocks with set-back tops, lower recessed rear bar, open south notch) | conforms | front vs source front; front_corner vs source oblique |
| Storey count (retail + 3 residential + penthouse = 5) | conforms | front, right_side, rear (5 levels counted) |
| U-plan and courtyard (asymmetric, courtyard east of centre, raised on the podium) | conforms. I measured the top render at y 600: west wing x 310-640 = ~330 px, east wing x 900-1132 = ~230 px, ratio 1.43. The source top (x 265-575 = 310 px, x 850-1065 = 215 px) gives 1.44. The courtyard centre (x 770) lies east of the building centre (x 721). | top vs source top |
| Street stair (wide concrete stair from the sidewalk to the raised courtyard, between the retail blocks, with handrails) | conforms. The placement within the notch deviates slightly (P2 #5). | courtyard_stair, top, front |
| Balconies and cedar reveals (recessed, cedar-lined, glass balustrades) | conforms | balcony_close, facade_close, front |
| Window rhythm (tall black-framed paired windows, 5 bays on the west-wing front, 3 floors) | conforms on the south face. The east face has a regular 6-bay rhythm but the wrong material. | facade_close, right_side |
| Penthouses and terraces (set back at the front end of each wing, glass-railed terraces) | conforms in massing. The eave and front material deviate (P2 #4, #8). | roof_terrace, front |
| Retail base (dark storefronts across the south ground floor, corner glazing) | conforms on the south face. The east wrap is short (P2 #7). | front, retail_corner, glass_close |
| Materials hierarchy (dark ribbed metal dominant, cedar accents) | **deviates.** The east elevation and the courtyard walls are beige (P0 #1, P1 #3). | right_side, architecture_close, courtyard_stair, aerial |
| Rooftop units on the rear bar | **deviates.** The units float (P0 #2). | roof_terrace, front_corner |
| North and west faces (not shown in any source) | The west face is a blank dark party wall with a slot-window column and a beige top band. The rear has dark ribs. Both are coherent with the visible grammar apart from the beige band. | left_side, rear, rear_lane |

## 4. Camera validity

No view has its target occluded, clipped or illegible. glass_close now frames black-framed storefront glazing with no tree in front. facade_close and cladding_contact have a foreground tree crown in the lower 10-35% of the frame, but the subject stays legible. interior is dark but legible.

## Prior-version (v006) findings

| v006 finding | status in v007 pixels |
|---|---|
| P1: the plan was symmetrical, while the sources show the west wing ~1.4x wider than the east, with the courtyard and stair east of centre | **Resolved.** The top render measures 330 px vs 230 px (1.43), with the courtyard and stair east of centre. The front render agrees: west block x 302-640, east x 893-1135. |
| P1: the glass_close camera was blocked by a street tree | **Resolved.** The full frame is storefront glazing and frames, with no occluder. |
