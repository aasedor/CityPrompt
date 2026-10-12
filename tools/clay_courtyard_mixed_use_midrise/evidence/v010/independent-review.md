# Independent holistic review: courtyard v010 (RLASM v6.1 architectural clay)

## 1. Verdict

**VISUAL_REWORK_REQUIRED**. The v009 roof-lid finding is resolved, but the render wraps a saturated cedar band around the whole top storey of the east street face, the courtyard faces and the rear bar. The locked sources show that storey flush in the same taupe panel as the floors below, with cedar only on the set-back front penthouse walls and the rear-bar galleries. The east street elevation also uses an aligned six-bay grid of double windows, where the sources show narrow, staggered windows.

Counts: P0 = 0, P1 = 2, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side x450-1125 y325-430; aerial x560-1080 y440-660 (east face top band) and x600-720 y400-560 (inner faces); rear_side x330-1130 y380-620; roof_terrace x30-570 y330-720; rear x300-1140 y365-445; left_side x315-990 y330-430 | The whole top storey of every face except the south penthouse fronts is a saturated orange cedar band (render RGB about 138,108,77 to 160,120,80). That covers the east street face, both courtyard faces of the wings, the rear elevation and the west face. In sources/oblique.jpg x880-1030 y220-300 and sources/front.png x880-1000 y100-200, the east-face top storey is the same flush taupe panel as the floors below (RGB about 145,126,109), capped only by the thin dark roof edge. In sources/front.png x390-490 y160-260, the inner face of the left wing is also taupe at penthouse level. Cedar appears only on the set-back south penthouse walls and soffits, the balcony reveals and the rear-bar gallery walls. In every oblique and side view, the render therefore reads as a different building with a cedar crown. | The penthouse-storey wall material was applied to the whole top-storey perimeter, not only to the set-back south wall behind the terrace. | Give the top-storey walls on the east, north, west and courtyard faces the same panel material as the face below: taupe on the east and courtyard faces, dark on the west and rear to match their lower floors. Keep cedar only on the recessed south penthouse wall, the canopy soffit, the balcony reveals and the rear-bar gallery walls. Re-render right_side, aerial, rear_side and roof_terrace. |
| 2 | P1 | right_side x400-990 y430-670; architecture_close x930-1440 y0-1000; retail_corner x980-1440 y0-380; aerial x840-1060 y480-760 | The east street elevation shows six evenly spaced, wide two-pane windows per floor, aligned vertically over three floors on a smooth plane. sources/oblique.jpg x880-1030 y230-820 and sources/front.png x880-1000 y130-510 show 8-9 narrow single tall windows per floor in a staggered, offset pattern between floors, set in panel cladding with visible joints. That rhythm is the main signature of this principal street face. | The east-face fenestration was generated from a generic uniform-grid window module, not from the source rhythm. | Replace the east-face window set with narrow single-light tall windows, about half the current width, at 8-9 per floor. Offset alternate columns vertically to reproduce the stagger, and add the panel-joint lines seen in the source. Keep the dark retail base and the corner storefront. |
| 3 | P2 | front x620-900 y360-620; courtyard_stair x430-1010 y0-500 | Rear-bar galleries have frosted glass balustrades and thin pale posts. The source (front.png x490-640 y280-500) shows black metal picket railings with dark slab edges. | Shared glass-balustrade component reused | Swap gallery guards to dark metal rails with a dark slab fascia |
| 4 | P2 | top x640-900 y670-865; front x700-830 y640-735 | The stair is centred in the courtyard opening with symmetrical planters. In sources/top.jpg x680-810 y490-630 it sits in the east half of the opening, with a planting and seating strip to the west. | Symmetric placement | Shift the stair east and put the planting and seating strip on the west side |
| 5 | P2 | facade_close, balcony_close, front | The dark cladding reads as flat panels with wide joints and small tick marks, where the source shows fine vertical ribbing. It still reads as dark metal, so this is not blocking. | Joint spacing too coarse | Tighten the rib spacing |
| 6 | P2 | front_corner (whole frame) | The view is taken from the south-west, so the west face (not shown in any source) dominates, and the matched oblique role falls to the aerial view only. | Camera azimuth | Move front_corner to the south-east to match sources/oblique.jpg |
| 7 | P2 | left_side x315-1125 y430-800 | The west face is an almost blank dark wall with one column of three slot windows. It is coherent as a party-wall face but sparse. | Minimal unseen-face fenestration | Optionally add a few windows in the source grammar |
| 8 | P2 | rear_lane x900-1115 y640-950 | The service door is a flat pale slab with no frame or head. | Placeholder door | Add a dark frame and a slight recess |
| 9 | P2 | top x310-640 y755-800 and x900-1130 y755-800 | A dark strip sits between the wing roof and the cedar terrace deck in plan. It is plausible as the canopy overhang, but it is wider than the thin lid edge in sources/top.jpg y545-555. | Canopy depth | Reduce the canopy projection slightly |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | conforms | front vs sources/front.png; aerial vs sources/oblique.jpg |
| Storey count (retail + 3 residential + penthouse) | conforms | front, right_side vs sources/front.png |
| U-plan and courtyard (opens south, raised on podium) | conforms | top vs sources/top.jpg; aerial |
| Street stair (wide concrete, from sidewalk to podium) | conforms (centred, not offset east: P2) | courtyard_stair, top vs sources/top.jpg |
| Balconies and cedar reveals | conforms (recessed, cedar-lined, glass guards, real depth) | balcony_close, front vs sources/front.png |
| Window rhythm | deviates on the east face (finding 2); conforms on the south faces | right_side, architecture_close vs sources/oblique.jpg; facade_close vs sources/front.png |
| Penthouses and terraces | conforms at the south ends (set back, cedar wall, dark canopy, cedar deck); deviates in the wrap-around cedar band (finding 1) | roof_terrace, front, top vs sources/front.png and sources/top.jpg |
| Retail base | conforms (dark storefronts, wrapping the corner) | retail_corner, front vs sources/front.png |
| Materials hierarchy | deviates (cedar crown, finding 1); otherwise dark ribbed south faces, taupe east and courtyard faces, dark roof | aerial, right_side vs sources/oblique.jpg |

## 4. Camera validity

No view has its target occluded, clipped or illegible. glass_close and interior are tight but legible. front_corner is valid but comes from the south-west, not the source's south-east (P2 finding 6).

## 5. Previous-version findings

- **v009 P1 (rear bar roof as a separate lighter plane below the wings' dark lids, no rear fascia, pale slab over the courtyard galleries): RESOLVED in the pixels.** In aerial x400-1080 y260-640 and top x310-1130 y215-750, one continuous dark membrane with a black parapet line runs across both wings and the rear bar. In rear x300-1140 y355-365, a dark fascia now runs along the full rear elevation. In front x655-870 y370-385 and the zoomed courtyard crop, the gallery lid over the rear-bar courtyard face is dark. In rear_side x630-830 y300-440, the rear-bar roof abuts the wing lids with no lighter plane or step.
- **v008 penthouse finding (cedar walls, cantilevered dark canopy with cedar soffit, cedar deck): still resolved** at the south penthouse fronts (roof_terrace x580-1200 y420-800; right_side x390-450 y320-345). Its material has now leaked onto all other top-storey faces (finding 1).
