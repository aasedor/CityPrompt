# Independent holistic review: clay-braced-frame-hospital v002 (RLASM v6.1 architectural clay)

Reviewer: independent; did not build this candidate. I judged only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg), all 18 renders at full resolution and the four phone boards. I made my own zoom crops in a separate scratch folder (`hospital-v002-indep-crops-7f3a`) and also sampled the pixel values of the near-black regions. I ignored the builder's metadata, hashes and notes as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: v002 fixes most of the v001 defects (the braced bar face, five even tiers, clean node plates, a continuous screen field and columns down to grade). Three P1s still block approval: the atrium still reads as an infill slot flush with the ward exoskeleton rather than a glass volume standing forward; there are pure-black voids or seams in the rear views; and the atrium diagrid members overshoot its edge frames.

Counts: P0 = 0, P1 = 3, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, aerial, top, front (vs oblique, top, front sources) | The atrium face sits on the same line as the clinical south face and the east-leg frame. The east-leg corner column stands at or in front of the atrium's east edge, so the atrium reads as a glazed slot pinched between two solids. The claimed 0.8 m projection is not legible at whole-envelope scale, and no glazed side return can be seen. In all three sources the atrium is a glass box standing well forward of the ward block's south face (top: about one-third of the atrium length lies south of the ward's south line; oblique: a clear glazed west return and a glass top in front of the braced face; front: a west return visible). The glass top and the full height are now present (aerial, glass_close). | Projection set to 0.8 m, and the ward east leg held on the same south frontage as the clinical block. | Either set the ward east leg's south face back about 4–6 m (one frame bay deep, as the top source shows) or bring the atrium 4–6 m proud of the street faces. Give it full-height glazed east and west returns with diagrid and corner mullions, keep the framed glass top, and re-seat the entrance canopy at the atrium's new front. Re-render front_corner, aerial and top to confirm the atrium is read as standing forward. |
| 2 | P1 | rear (also legible on phone-04), rear_side, left_side | **(a)** rear: a solid pure-black rectangle (sampled RGB 0,0,0, about 30×45 px at 1440 wide) where the clinical plant storey's north return should be, west of the ward bar. There is no louvre and no depth, and it shows as a black square even at phone size. **(b)** rear and rear_side: a 2–3 px pure-black seam (sampled 0–5) running the full height from grade to roof at the ward bar's north-west outer corner, behind the frame column. This is the same class of defect as the v001 east-corner bar, now on the opposite corner. **(c)** left_side: a 2 px near-black slit at the south end of the west louvre band. | (a) The plant-storey north face is missing or open, so the camera looks into an unlit cavity. (b) The two curtain-wall planes stop short of each other at the outer corner, leaving an open slot into the unlit interior. (c) The louvre return does not close the end. | (a) Carry the louvre band (or a solid return) across the plant storey's north face west of the bar. (b) Close every outer corner of the ward glazing with a corner mullion or mitred meeting. Check all four bar and leg corners, not only NW. (c) Cap the louvre end. Then re-scan all whole-envelope renders for pixels with luminance below 12. |
| 3 | P1 | glass_close, entrance_canopy, architecture_close | Where the atrium diagrid meets its edge frames, the diagonals run straight past the edge mullions. Free stubs about one member deep stick out beyond the frame on both the west and east edges, at every termination, including at the canopy level. The two diagonal sets sit on separate planes with no node at any crossing, so the net reads as two overlaid grilles rather than one jointed net. | The diagonal members are generated full-length on the bounding plane and never clipped to the inner face of the edge frame. The planes were offset (the claimed fix for the black dots) with no connecting node. | Clip each diagonal to the inner face of the edge frame and add perimeter shoes. Add small light-grey node discs at the crossings (not black). Keep the offset at 1–2 cm so the crossings read as jointed. |
| 4 | P2 | entrance_canopy, front | Still no entrance doors under the canopy: the atrium base is diagrid glazing to grade. Two thin slabs float inside the glass at door-head height with nothing under them. | Door heads modelled without door leaves or frames. | Add a pair of glazed door leaves with frames and a recessed threshold under each head. |
| 5 | P2 | front, architecture_close | Some canopy tension rods run up to the dark sign panel, the clinical screen panels and the brick facade rather than fanning from the atrium net as in the source. | Rod anchors set by position, not tied to the atrium. | Move the rod anchors onto atrium diagrid nodes about mid-height. |
| 6 | P2 | aerial, front_corner | A dark joint line between the bar roof and the east-leg roof, so the L reads as two abutting slabs. | Two separate roof slabs with a gap. | Make one continuous roof slab or a flush, light-coloured joint. |
| 7 | P2 | top, aerial | Three-lobed shadows ("propellers") under the roof vents remain. | Three light sources. | Use one key light for roof shadows, or soften the fill lights. |
| 8 | P2 | facade_close, front | Perforations read as flat mid-grey squares in a random scatter. The source shows dark holes in graded clusters with glazing behind. | Hole material is not darker and the hole layout is uniform-random. | Darken the hole recess or open the holes onto the darker strip glazing, and grade their density across each panel. |
| 9 | P2 | brick_base, front | Brick reads salmon/orange with horizontal-line coursing only. The source is a deeper red-brown. | Palette value. | Darken and desaturate toward the source brick. |
| 10 | P2 | interior | The atrium interior is very dark and low-contrast (legible, but murky). | No interior or skylight light. | Add a skylight-driven fill through the glass top. |
| 11 | P2 | front, left_side | The ward block is only level with the clinical roof canopy. In the front and oblique sources it clearly rises above the canopy. The atrium top sits at louvre-band height, a little higher than the source, where it stops below the clinical parapet. | Height choices. | Optional: raise the ward roof by about one storey, or lower the atrium top to the clinical parapet. |
| 12 | P2 | facade_close, front | The pale screen panels are near-white against a mid-grey sky, so the clinical field loses some of its pale-concrete warmth. | Palette. | Warm the panel colour slightly. |


## 3. Source conformance checklist

| Item | Status | View used | Note |
|---|---|---|---|
| Silhouette | conforms (with #1) | front, front_corner, aerial vs front and oblique | Low clinical block with louvre and raised canopy, taller braced ward L and a glass atrium between them. The atrium does not stand forward (P1 #1). |
| Storey counts | conforms | front, left_side, rear, right_side | Clinical: 2 brick + 5 screen storeys + recessed plant storey. Ward: 2-storey brick base + 5 braced tiers. |
| Plan: three volumes | conforms, except the atrium's forward position | top, aerial vs top source | Clinical block SW, ward L along north and east, atrium in between with a glass top running to the bar. The atrium and ward south-frontage relationship deviates (P1 #1). |
| Clinical: brick base | conforms | front, brick_base, left_side | Two storeys with large framed windows and a door; tone is P2 #9. |
| Clinical: perforated screens | conforms | front, facade_close, left_side | Continuous five-tier field with strip glazing behind; perforation finish is P2 #8. |
| Clinical: sign panel | conforms | front, architecture_close, front_corner | Tall dark panel near the east end of the south face, spanning the screen storeys. |
| Clinical: louvre band | conforms on S and W, deviates on the north return | front_roof crop, roof_canopy, left_side, rear | North return west of the bar is a black void (P1 #2a). |
| Clinical: raised roof canopy | conforms | front, roof_canopy, aerial | Tilted framed canopy on posts over the western roof; the recessed plant roof to the east matches the top source. |
| Ward: exoskeleton bays | conforms | right_side, rear, rear_north, front | Near-square bays, 2 bays on the south face of the east leg. |
| Ward: X-braces | conforms | braced_frame, rear_north, front_corner | Full-height X per bay with light node plates; also on the bar's south face above the clinical block and the atrium. |
| Ward: ring beams | conforms | right_side, rear_north | A ring at every tier plus a ring over the brick base. |
| Ward: brick base | conforms | front, right_side, rear, fc_eastface crop | Two storeys with frame columns carried to grade in front of the brick. |
| Atrium: diagrid | deviates | glass_close, entrance_canopy, architecture_close | A diamond net is present, but members overshoot the edges and have no nodes (P1 #3). |
| Atrium: roof | conforms | aerial, front_corner, glass_close, top | Framed glass top running north to the bar. |
| Atrium: volume / returns | deviates | front_corner, aerial, top | No legible projection or returns (P1 #1). |
| Entrance canopy: rods | conforms with a P2 | front, front_corner, glass_close | Rods present and in contact; some anchors are on the clinical sign/screen rather than the atrium (P2 #5). |
| Entrance canopy: posts | conforms | front, entrance_canopy, front_corner | Wider glass canopy centred on the atrium, front posts down to grade, single back edge, no black seam. |
| Roof plant | conforms | roof_plant, top, aerial | Boxes and vents on the bar roof, condensers on the recessed clinical plant roof. Tri-shadows are P2 #7. |
| Materials hierarchy | conforms | all | Red brick base, pale screens, dark sign and louvre, light-grey steel, blue-grey glass. |
| Unseen faces (west and north of ward) | conforms in grammar, except black defects | left_side, rear, rear_side | Braced frame on a brick base, consistent with the visible grammar, apart from P1 #2b. |

## 4. Camera validity

- All 18 views are legible. None has the target occluded or the asset clipped.
- front, left_side, right_side and rear are near-orthographic elevations with the asset at about 45–55% of the frame width. They are small but readable, and the phone board keeps them legible.
- interior is dark but legible (P2 #10).
- facade_close is strictly frontal and gives little depth cue, but the screens' stand-off from the glazing is visible at the panel gaps.
- The top view carries a large off-asset shadow wedge across the upper right. The asset itself is unobstructed.
- No camera P0.

## 5. Previous-version (v001) findings: resolved in the pixels?

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P1: no X-braced exoskeleton on the bar's south face above the clinical block and atrium (blank panel above atrium) | **Resolved** | front (braced tier above the louvre band), front_corner and aerial (braces continue along the bar's south face to the east leg), roof_canopy |
| P1: black full-height bar at the east wing's SE corner; black seam and band at the canopy junction | **Resolved at those locations** (no pixels with luminance below 12 in front, front_corner or right_side). **The defect class recurs** at the bar's NW corner and the plant-storey north return. | right_side and front crops; rear and rear_side (P1 #2) |
| P1: black diamonds at every X crossing; black dots at diagrid nodes | **Resolved**: light-grey node plates on the X-braces, no black dots on the diagrid. The diagrid now has no nodes at all and its members overshoot the edges (P1 #3). | braced_frame, rear_north, architecture_close, glass_close |
| P1: three tall tiers plus a squat top tier instead of about five even near-square tiers | **Resolved**: five even near-square tiers above the brick base. | front crop, rear, right_side, rear_north |
| P1: atrium a hidden recess rather than a projecting full-height glass volume with returns and a glass top | **Partially resolved**: full height and a framed glass top are now present, raised to louvre height. The projection and returns are not legible, and the atrium still reads as a flush slot. Kept as P1 #1. | front_corner, aerial, top, glass_close |
| P1: open unscreened bays on a stepped offset making diagonal dark streaks across the clinical screen field | **Resolved**: a continuous, even screen field. | front, left_side, front_corner, facade_close |
| P2: no entrance doors under the canopy | Not resolved (P2 #4) | entrance_canopy |
| P2: frame ring overhanging the brick base without columns to grade | **Resolved**: columns down to grade. | rear_north, fc_eastface crop, front |
| P2: brick tone | Not resolved (P2 #9) | brick_base |
| P2: coarse perforation | Largely unchanged (P2 #8) | facade_close |
| P2: dark interior | Not resolved (P2 #10) | interior |
| P2: triple roof-vent shadows | Not resolved (P2 #7) | top, aerial |
| P2: narrow canopy | **Resolved**: wider canopy centred on the atrium. | front, top |
| P2: unresolved atrium/bar junction | **Resolved**: the glass top meets the bar frame cleanly. A separate bar/leg roof seam is noted (P2 #6). | aerial, roof_canopy |

### Builder claims checked against the pixels

- Braced frame on the bar's south face above the plant storey and the atrium: **verified**.
- Shared corner columns drawn once: **verified at the SE corner**. However, a new black corner seam appears at the NW corner (P1 #2b).
- Single back edge on the canopy: **verified**.
- Ward leg's inner face no longer ending on the south carrier: **not contradicted**.
- Node plates with the second diagonal set behind the first: **verified on the braces**. The diagrid set on separate planes produced unjointed overshooting members (P1 #3).
- Five even tiers: **verified**.
- Atrium 0.8 m proud with glass returns and a framed glass top at 33 m: **the top is verified**. The projection and returns are not legible (P1 #1).
- Continuous screen field: **verified**.
- Columns down to grade: **verified**.
- Wider canopy: **verified**.
