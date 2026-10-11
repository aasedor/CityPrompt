# Independent RLASM v6.1 holistic review: farm v005 (clay LED grow block)

I looked at the three locked sources, all 18 renders at full resolution and all 4 phone boards. I did not read any build code, report, README or VERSIONS file. Every statement below comes from the pixels. Colour figures were measured directly on pixel crops (HSV medians).

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The three v004 P1s are resolved in the pixels. Two new P1s remain: the east face slot composition does not match the source, and the entrance corner of the plinth is built wrong.

**Counts: P0 = 0, P1 = 2, P2 = 9**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | **P1** | right_side.png (whole face, x 490-950, y 260-790); aerial.png right face (x 760-1000, y 430-800); boards/phone-02 and -03 | The render's east face (the entrance face) has the same rigid 6 x 5 grid of identical, all-lit slots as every other face. Both sources show this face (sources/front.png right face x 655-910, y 0-535; sources/oblique.jpg right face x 680-940, y 250-780) with a distinct staggered composition: about 7 lit slot columns of different lengths, with the middle columns offset vertically (lit lower half under an unlit upper section, and lit upper half over unlit lower). They also show one or two **dark, unlit vertical slots** (front.png x≈770, y 30-260; oblique.jpg x≈790 and x≈855, y 340-510). The slot rhythm of this face is part of the building's identity, and the render reduces it to the south face's grammar. | One generic slot generator is applied to all four faces. The east face's stagger and dark slots were never encoded. | Give the east face its own slot schedule, read from front.png and oblique.jpg: 7 columns. In columns 3-5 the lit glazing covers only the lower or only the upper storeys, as in the sources, and the remaining length is a dark, recessed, unlit slot of the same width. Keep the outer columns full height. Re-render right_side, aerial and front. |
| 2 | **P1** | entrance_contact.png (x 210-375, y 155-800); right_side.png (x 430-445, y 800-915); front.png (x 950-1025, y 795-920) | At the entrance corner the actual building arris is a **charcoal strip running to grade** (entrance_contact x 340-375). The "concrete corner pier" is a separate grey slab standing proud **in front of** the south cladding (entrance_contact x 210-340). It has its own shadow line on the charcoal behind it (x 185-210) and a visible top ledge (y≈155). So the concrete does not wrap the corner. It reads as a panel stuck onto the facade, with dark cladding showing between it and the east-face concrete. In both sources the concrete plinth wraps the corner continuously at grade (front.png x 555-660, y 545-665; oblique.jpg corner base x 600-680, y 800-860), and the charcoal mass sits above it. | The pier and the east plinth are separate boxes. The pier is offset outward from the south face, and the upper charcoal cladding volume is carried down to grade at the corner. | Remove the charcoal corner sliver below the first-floor line. Model the plinth as one L-shaped concrete volume that wraps the corner: a short return on the south face and the full east face, flush with or slightly recessed under the charcoal mass above. Do not let any part stand proud of the cladding. Check in entrance_contact that no dark strip reaches the ground at the corner. |
| 3 | P2 | entrance_contact.png, right_side.png (x 445-580) | The glazed entrance starts immediately at the corner. In the source (front.png x 655-720) a solid concrete bay about 20 % of the face width separates the corner from the entrance. | Opening placed at offset 0. | Move the entrance about 0.2 x the face width in from the corner, and fill the gap with concrete (this goes with fix 2). |
| 4 | P2 | right_side.png | The source east face ground storey has a dark service door near the far (north) end (front.png x 895-920, y 575-650). The render has two narrow slits and no door there. | Not modelled. | Add a flush dark service door at the north end of the east plinth. |
| 5 | P2 | all slot views; front.png | Slot glass hue measures 310° against 320-324° in the sources (saturation and value now match). The lit glass reads slightly violet next to the source magenta. The rack shelf bands read beige/peach. | Emission tint is slightly too blue. | Shift the emission colour about 10° toward red, e.g. RGB about (214,130,180). |
| 6 | P2 | front.png, left_side.png, architecture_close.png | The solid cladding band between storey windows (about 20 px of a 117 px storey, plus deep frames) reads heavier than the thin dark transoms in the sources. The facade looks like a punched grid rather than tall strips. The source's horizontal panel joints, about every two storeys (front.png y≈230 and y≈545), are absent. Only the first-floor band is modelled. | Spandrel too tall; joint grid missing. | Cut the inter-storey solid to a thin dark transom about half the current height. Add a recessed horizontal joint every 2 storeys. |
| 7 | P2 | top.png, aerial.png | One planter strip on each side of the roof. The source top shows paired (two-row) planter strips on both sides (top.jpg x 410-625 and 675-855, y 330-360). | Single row modelled. | Double each planter strip into two parallel rows. |
| 8 | P2 | top.png, roof_greenhouses.png, parapet_corner.png | The glasshouses have 4 bays and no ridge vents. They cover about 45 % of the roof depth against about 55 % in top.jpg. The source glasshouses are longer and carry ridge vent boxes (oblique.jpg y 130-260). | Shorter module count. | Lengthen each glasshouse to about 55 % of the roof depth (6 to 8 bays). Add small ridge vent boxes. |
| 9 | P2 | top.png, aerial.png | The penthouse interior holds sparse equipment (one unit, two fans, one block). The source shows a dense set of plant units and ducts (top.jpg x 460-655, y 120-240). | Simplified. | Add 3-4 more plant boxes or ducts inside the open-topped penthouse. |
| 10 | P2 | right_side.png, entrance_contact.png | The east plinth face is flush with the charcoal above. In the source the charcoal mass visibly overhangs a recessed concrete plinth, with a shadow line (front.png y 545-560). | No recess. | Set the plinth back by about 0.2-0.3 m under the charcoal mass. |
| 11 | P2 | front.png, left_side.png, top.png | The pavement base is made of two overlapping offset rectangles, which gives stepped corners (e.g. front.png x 320-420, y 830-930). | Two slabs. | Use one pavement slab with a clean outline. |

## 3. Source conformance checklist

| item | status | view used / evidence |
|---|---|---|
| Silhouette (near-square corner block, flat parapet, penthouse block rising at the north-west) | conforms | aerial vs oblique.jpg; top vs top.jpg (penthouse x-inset 21 % vs 20 % in the source, width 39 % vs 38 %) |
| Storey count (ground plus 5 grow levels; oblique governs) | conforms | front.png, left_side.png, right_side.png, rear.png: 5 lit slot rows over one ground storey |
| Slot rhythm | **deviates** | South and west faces broadly conform (6 slots, lit depth with visible reveals and racks in slot_close, glass_close, interior). The east face deviates (finding 1). Transoms are heavier than the source (finding 6, P2). |
| Plinth and entrance | **deviates** | Cladding to grade with unlit slot glazing on the south face conforms (front.png, facade_close). The east-face concrete plinth with a recessed glazed entrance and returns is present (entrance_contact). The corner junction is wrong (finding 2); the entrance offset and the missing service door are P2. |
| Glasshouses | conforms (P2 notes) | Five gabled glasshouses, ridges running north-south, gable ends to the south, the larger gap between the 3rd and 4th matching top.jpg. They sit on the deck with no float or intersection (roof_greenhouses, parapet_corner). Length and vents are P2. |
| Penthouse and beds | conforms (P2 notes) | Open-topped penthouse at the north-west (aerial, top, front_corner). Four north-south raised beds at the north-east sit in concrete troughs on the deck (beds.png). Contact is clean. |
| Parapet and rail | conforms | The rail is continuous and meets at every corner post: parapet_corner (x≈720, y≈260), beds (x≈1240, y≈520), penthouse_contact (x≈140, y≈640), top and aerial |
| Materials hierarchy (charcoal panels > magenta lit slots > concrete plinth > clear glasshouses > green beds) | conforms | Slot glass measured at saturation 0.31-0.41, value about 0.84 (sources 0.37-0.42 at about 0.78-0.87). The hue is about 10° cool (P2). |
| North and east faces not covered by sources | coherent | The north (rear.png) concrete plinth with slits and a roller door is coherent with the visible grammar. The east face is actually visible in both sources, so finding 1 is a fidelity finding. |

## 4. Camera validity

All 18 views are valid. The target is legible in each, with no occlusion and no clipping of the asset.

- front_corner.png looks at the south-west corner, where both faces are clad to grade. The source oblique looks at the entrance corner. The matched oblique role is still met by aerial.png, which shows the entrance corner with the concrete base, so this is not a defect. It does mean front_corner cannot be used as evidence for the plinth corner.
- glass_close.png shows the left face at a grazing angle, so those slots read as dark reveals. The right-hand slot carries the evidence and is legible.
- interior.png is a frontal close-up of three slots rather than an interior. Its lit rack depth and reveals are legible.

## 5. Prior-version (v004) findings

| v004 finding | status in v005 pixels | evidence |
|---|---|---|
| P1: lit slot glass near-white pink (saturation about 0.13 at value 0.97) against source magenta (about 0.40 / 0.80) | **resolved** | Measured on single slots: front.png saturation 0.31 / value 0.85; left_side.png 0.41 / 0.84; interior.png 0.40 / 0.82. Sources measure oblique.jpg 0.37 / 0.81 and front.png 0.42 / 0.78. Hue is about 10° cool (P2, finding 5). |
| P1: south face a full-height grey concrete plinth with small slits, where the source carries charcoal to grade with unlit slot glazing | **resolved** | front.png and facade_close.png: the ground storey of the south face is charcoal cladding, and all 6 slot columns continue as framed, unlit grey glazing to grade. Concrete appears only at the corner (but see P1 finding 2 on how that corner is built) and on the east and north faces. |
| P1: roof guard rail stopped short of every corner | **resolved** | The rail is continuous through the corner posts in parapet_corner, beds, penthouse_contact, aerial and top. |
| v004 P2s (8, not itemised in the brief) | not individually verifiable | The remaining P2s are listed fresh in section 2. |
