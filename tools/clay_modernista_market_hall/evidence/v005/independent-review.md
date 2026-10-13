# Independent holistic review: clay-modernista-market-hall v005 (RLASM v6.1)

Reviewer: independent, no relationship with the builder. Inputs read: `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 renders at full resolution, the four phone boards, and 3x zoom crops of the gable piers, the crest/coat of arms, the rose roundel and the aisle dado. The crops are in a separate scratchpad folder, `mercat-v005-review-crops/`. Metadata, evidence JSON and builder notes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The pinwheel envelope, lantern, quadrant roofs, dado pedestals, awnings and plaza now read correctly, and the tympanum field is a filled mosaic. But the gable's identity ornament is still wrong in the pixels:
- The archivolt "stained-glass roundels" are hollow gold rings.
- The rose and blue roundels are flat untraced discs.
- The gable rakes cut through the coat of arms.
- Dark rake-end blocks still stop in mid-air at every pier capital.

## 2. Findings

Counts: P0 = 0, P1 = 3, P2 = 8

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | great_arch, facade_close, crest_contact, rear_court, front, left_side/right_side/rear | The "band of 19 framed stained-glass roundels" round the archivolt is hollow, thin gold torus rings. The dark archivolt plate shows through every ring, with no glass, no colour and no iron frame or tracery. The rose is a flat 12-sided yellow disc with a flat red centre: a bullseye or target card with no frame, mullions or radiating panes. The two blue roundels are flat blue polygon discs laid over the tile grid. They cover tiles regardless of the leading, and the horizontal transom bars cross in front of them (crest_contact, left disc). In the source (front gable), about 22 roundels are filled with blue, green and amber stained glass in dark iron frames. They sit in a spandrel field between a deep pierced archivolt and the rakes. The rose and blue roundels have iron frames and radial or star tracery. Here the arch crown nearly touches the rakes, so there is no spandrel field at all. | The roundels were modelled as a ring (torus) primitive with no disc fill. The rose and blue roundels are single flat n-gon cards with no frame or subdivision. Gable proportion: arch rise is about 0.43 of span against about 0.57 in the source, and the arch crown is about 11% of gable width below the apex against about 18%. | Give each archivolt roundel a recessed stained-glass disc (muted blue/green/amber, 3 to 6 radial panes) inside a dark iron frame ring, and drop the gold. Rebuild the rose as a framed roundel with a dark frame, 8 to 12 radial leaded panes and a small red centre, muted to the tympanum palette. Do the same for the two blue roundels, and cut the tympanum tiles under them rather than overlaying. Stilt the arch (raise the springing or narrow the span) or lift the apex so a spandrel field opens between archivolt and rakes. Set the roundels in that field as in the source. |
| 2 | P1 | crest_contact, great_arch, rear_court, lantern_roofs | The coat of arms (yellow octagon with red/yellow vertical bars) sits on the apex and is bisected by both gable rakes. The beige fascia and dark rake beams pass in front of it, and the upper half of the shield rises above the roof line. The red and yellow bars are separate slabs that overrun the shield outline at the top and bottom. A loose yellow box sits on the apex above it. In the source, a crowned shield with foliage sits fully inside the gable, below the apex and above the archivolt, clear of the rakes. | The shield was placed at apex height on the gable plane without clearing the rake members. The stripe slabs are not clipped to the shield profile. | Move the shield down into the gable field under the apex, clear of both rakes and above the archivolt crown (this needs the spandrel from #1). Trim the stripe bars to the shield outline. Add a simple crown/foliage frame. Remove or seat the loose apex box. |
| 3 | P1 | facade_close, aisle_arcade, plaza_awnings, rear_court (all four gables) | At every gable pier capital, two dark rectangular rake-end blocks with an oblique cut hang off the side face of the pier just below the cap. The top block carries a thin vertical rod. They bear on nothing and stop in mid-air. The beige rake/eave fascia plank runs diagonally into and through the pier cap: the cap is visibly penetrated in aisle_arcade and plaza_awnings. This is the v004 "stub through the pier capital" defect in a new form. One seam line was removed, but the rake members still overrun the pier. | The gable rake (dark outer member, inner member and cresting post) is extruded past the pier line, and the fascia plank is not trimmed at the pier. | Terminate the rake members and fascia on the pier cap: either stop them at the cap's inner face, or land them on a modelled bracket or stone corbel seated on the cap. Delete the cresting post where it has no rake beneath it. Verify in facade_close, aisle_arcade and plaza_awnings at 3x. |
| 4 | P2 | great_arch, facade_close, crest_contact | The tympanum mosaic is a strict orthogonal grid of opaque square cards on a dark plate. The leading is about 25% of the pitch and tiles are missing at random. It reads like pixel art. The source has continuous leaded glazing with vertical iron mullions and an organic tree motif. | Uniform tile grid with a fixed gap. | Thin the leading. Add 5 to 7 vertical iron mullions and one diagonal tie per side. Bias the colour into vertical tree/foliage zones. |
| 5 | P2 | front, great_arch, crest_contact, lantern_roofs, rear_court | The apex crest is a spoked wheel on a mast and reads as a ship's wheel. The source has a tall wrought-iron filigree spire with scroll cresting along the rakes. | Simplified primitive. | Replace it with a tapering spire of stacked scroll/fleur profiles. The rake cresting can stay as posts. |
| 6 | P2 | aisle_arcade, plaza_awnings, architecture_close | The dado tile panels are a cream panel with about 12 widely spaced small blue/brown squares. They read as sparse insets rather than the source's continuous patterned ceramic tiling, which is orange/blue/white, full panel, with a green border tile course. | Sparse tile placement. | Fill the panel with a dense tile pattern (for example 4 by 16 small tiles, alternating motif) and add a green border course. |
| 7 | P2 | aisle_arcade (left) | A black full-height slit is visible between a pedestal and the adjoining dado/pier block. | Gap between adjacent boxes. | Close the gap or add an end return. |
| 8 | P2 | crest_contact | A black crack runs through the centre roundel at the archivolt crown, a seam between voussoir segments. | Unwelded arch segments. | Merge or overlap the segments at the crown. |
| 9 | P2 | architecture_close, aisle_arcade | The quadrant gablets have blank flat grey faces, with no louvre or glazing bar. | Single flat face. | Add a mullion and a louvre or glazing bar to each gablet face. |
| 10 | P2 | front, left_side, right_side, rear | The building fills only about 55% of frame width and about 35% of height, with a large empty foreground. It is legible but small. | Camera distance. | Tighten the framing by about 20%. |
| 11 | P2 | interior, glass_close | The produce in the stalls is flat orange slabs. Acceptable for clay. | Simplification. | Optional: add small crate and mound blocks. |

## 3. Source conformance checklist

| item | status | views used | note |
|---|---|---|---|
| Silhouette | conforms | front vs source front; front_corner, aerial vs oblique | Single storey, cross of high gabled wings, raised central lantern, lower corner quadrants. Square plan as in top/oblique. |
| Roof pinwheel and lantern | conforms | top vs top; lantern_roofs; aerial | Four gabled wings with ridges on the cross axes and a square glazed lantern with a pyramid roof. The wing rooflights match the top source's glazed strips. The lantern does not have the oblique source's arched stained-glass lantern gables, but the brief specifies a pyramid roof. |
| Great arch: archivolt | deviates | great_arch, crest_contact vs source front | Plain dark band, too flat. It touches the rakes and leaves no spandrel (finding #1). |
| Great arch: tympanum | conforms (field) / deviates (roundels) | great_arch, facade_close | The mosaic field is filled with small muted green/teal/amber panes. The rose and blue roundels are flat untraced discs (#1); leading style is P2 (#4). |
| Great arch: roundel band | deviates | great_arch, crest_contact | Hollow gold rings, not stained glass (#1). |
| Great arch: crest | deviates (P2) | crest_contact | Wheel instead of a filigree spire (#5). |
| Great arch: coat of arms | deviates | crest_contact | Bisected by the rakes and half above the roof line (#2). |
| Great arch: piers | deviates | facade_close, aisle_arcade, plaza_awnings | Stone piers with caps and recessed panels are present and seated on the plaza. The rake-end blocks hang in mid-air and the fascia penetrates the cap (#3). |
| Aisle walls: dado | conforms (P2 detail) | aisle_arcade, plaza_awnings | Stone pedestals under the columns, framed panels between them and a plinth course. The tile density is sparse (#6), with one slit (#7). |
| Aisle walls: cast-iron columns | conforms | aisle_arcade, architecture_close, glass_close | Round columns with bases and caps on the pedestals, and branching brackets. |
| Aisle walls: glazing | conforms | aisle_arcade, glass_close | Iron-framed glazing over the dado, with depth to the interior visible. |
| Awnings | conforms | aerial, top, architecture_close, plaza_awnings | Red/yellow/blue awnings over every perimeter bay, three per face per quadrant, as in the top/oblique sources. They have valances and attach under the brackets. |
| Gablets and quadrant roofs | conforms (P2 faces) | architecture_close, top, aerial | Hipped quadrant roofs with glazed pyramid centres (triangular teal/amber panes) and two gablets per eave face. The gablet faces are blank (#9). |
| Clerestories | conforms | aisle_arcade, lantern_roofs, architecture_close | Glazed clerestory band between the aisle roofs and the wing roofs. Glazed lantern drum and rooflights. |
| Entrance and interior | conforms | great_arch, facade_close, interior | Glazed screen with open central doors between the piers. The interior has a deep nave, iron trusses, a lantern and stalls with canopies. The far gable tympanum is visible from inside. |
| Plaza | conforms | aerial, front_corner, plaza_awnings | Paved slab with bollards, lamp posts and trees. Clay has no paving texture, which is acceptable. |
| Materials hierarchy | conforms (except the gable ornament) | all | Stone piers and dado, dark iron frame, taupe metal roofs, glazing, coloured canvas. Gold is overused on the roundel rings and the rose (#1). |

## 4. Camera validity

- No view is invalid. All 18 views frame their target without clipping.
- front, left_side, right_side and rear are small in frame (P2 #10) but fully legible.
- In glass_close, a foreground column splits the frame. The glazing, trusses and awnings are still legible.
- In rear_court, the foreground trees cover part of the lower right gable and aisle. The gable, arch, crest and pier are legible.
- interior, top and aerial are clear.

## 5. Previous-version (v004) findings: are they resolved in the pixels?

1. **Tympanum (mostly clear glass, about 30 large saturated cards in a sunburst, no band of roundels): partly resolved.**
   - Resolved: the field is now a filled mosaic of small muted green/teal/amber panes on a dark plate. The sunburst cards are gone.
   - Not resolved: the rose and the two blue roundels are again large flat saturated cards, with no frame or tracery, laid across the leading. The claimed "band of 19 framed stained-glass roundels" is hollow gold rings with no glass, and there is still no spandrel field.
   - This carries forward as P1 #1.
2. **Aisle dado (continuous timber-like box, no pedestals or tile panels): resolved at the P1 level.**
   - Stone pedestals stand under each column, with framed tile panels between them.
   - Remaining issues are P2: sparse tile pattern (#6) and one slit (#7).
3. **Dark stub through each gable pier capital stopping in mid-air: not resolved.**
   - The single seam line is gone. But at every pier capital, two dark rake-end blocks with a cresting rod still hang off the pier face below the cap and terminate in mid-air, and the beige fascia plank passes through the cap.
   - This carries forward as P1 #3.

**Net: P0 + P1 = 3, the same as v004 and v003.** The coat-of-arms intersection (#2) is newly identified. Fixing one P1 and partly fixing another leaves the total unchanged.
