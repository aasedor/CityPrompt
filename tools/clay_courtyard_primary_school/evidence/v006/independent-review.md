# Independent RLASM v6.1 holistic review: school v006 (clay courtyard primary school)

Reviewer: independent, adversarial. Evidence used: only `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, the 18 renders in `renders/` (all opened at full resolution) and the 4 phone boards. I did not read any build code, report or notes. Pixel coordinates are for the 1440x1080 renders, 1195x896 for oblique/top sources and 1024x768 for the front source. I also measured crops and sampled pixel colours to confirm two findings (roof tones, corner box position).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v005 P0 (east wing length) and v005 P1 (corner post instead of a box) are fixed, but three P1 fidelity defects remain. The corner concrete box does not run to the street and leaves the yard open at the SE corner. The wing's south end face has a fins-and-strip window where both sources show blank brick. All gravel roofs are the same neutral grey as the paved terrace.

**Counts: P0 = 0, P1 = 3, P2 = 7**

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | aerial (box ~560-860, 540-800; fence end ~590,870); entrance_passage (box 750-1180 x 365-760; fence 395-1050 ends short of slab corner ~1100-1180, 740-840); facade_close (box 1140-1400, 555-760; fence 1130-1430 in front); front (box 1100-1195 x 590-640 behind fence 850-1210); top (light-grey strip x 900-1045, y 860-910 south of the canopy pad) | The board-formed box is a short cube under the canopy's SE corner only. Its south face sits flush with the canopy edge, set back about 17% of the court depth from the street. A light-grey forecourt fills the gap between the box and the street fence. The street fence runs past in front of the box and stops short of the slab's east edge, so the yard is open to the east sidewalk at the corner. The source oblique (box from ~880,440 to ~680,790 in source px) shows a narrow, long concrete box/wall. It runs from under the canopy corner south to the street fence and closes the east side of the fenced dark yard. In the source front (box x 600-710, base y ~600) the box stands on the street line where the fence ends. In source top the yard south of the pad is dark rubber paving with a thin concrete edge on its east side (~x 850-870, y 680-715). | The box was modelled as a cube under the canopy corner rather than as the yard's east enclosure wall, and the paving zones were split | Extend the box south from under the canopy to the street fence line as a narrow, long volume (E-W about 1/4 of its N-S length). Inset its east face to the canopy's east edge, end the street fence against its west face, and repaint the area south of the pad dark yard paving to match the court. |
| 2 | P1 | entrance_passage (upper south face of the wing, x 630-1110, y 150-325: 4-pane strip window with yellow/green/teal fins); facade_close (x 725-1140, y 340-470); aerial (x 700-830, y 600-700); architecture_close (x 1075-1440, y 560-750) | The south end face of the two-storey east wing, above the canopy, has a full strip window with three coloured fins. Both sources show this face as **blank brick**: in the source oblique it is the large plain brick face at about x 655-810, y 490-640 above the corten canopy, and in the source front it is solid brick above the concrete box at about x 540-705, y 330-450. That blank brick end is a key part of the corner's identity: a solid brick volume over a corten band over a concrete box. | The east-facade strip-window module was repeated around the corner onto the south end face | Remove the strip window and fins from the wing's south end face (both storeys above the canopy) and leave plain brick with the concrete parapet coping. Keep the ground-floor entrance door under the canopy. |
| 3 | P1 | top (sampled: west wing roof RGB 168,165,160; NE "gravel" patch 165,162,157; east wing roof 171,169,164; corten-storey roof 169,166,162; paved terrace 164,164,162; ground 163,164,164); aerial (all roofs read as one pale grey) | All roofs are the same neutral pale grey, and they are almost the same value as the ground plane. Gravel roofs and the paved hall terrace cannot be told apart (at most about 6 RGB units). The source top shows warm tan gravel on the west wing, the east wing, the NE terrace corner and the corten-storey roof (sampled ~162,119,77 / 177,148,118 / 147,110,81). The paved terrace is cool grey (~128,145,155). That gravel-versus-paving pattern is one of the strongest readings in the source top and oblique. | Roof material assigned one shared concrete or clay colour | Give every gravel roof a warm tan source-palette colour (about #A8835E to #B89470). Keep the hall terrace cool pale grey with a paving-joint grid. Check in top/aerial that the roof zones read as in source top. |
| 4 | P2 | facade_close (fascia y 530-550 over a ~230 px storey); entrance_passage; front | Corten canopy fascia is a thin plate. Source front shows a deep corten band (~25% of storey height); source oblique shows a deep upturned edge. | thin slab | Thicken the canopy edge to a deep corten fascia/upstand of about 0.6-0.8 m. |
| 5 | P2 | top (pad east edge flush with wing at x ~1045); aerial | The canopy pad's east edge is flush with the wing's east facade. In source top the pad and box are inset from the wing's east face. | alignment | Inset the pad and box east edge by about the fin depth plus 0.5 m. |
| 6 | P2 | canopy_contact (posts at x ~575-610, 785-820, 915-940); courtyard; entrance_passage | Three slender posts along the court-strip canopy; source oblique shows one slender post near the court corner. Posts are plausible, but they add more structure than the source. | extra supports | Reduce to one or two posts in line with the source. |
| 7 | P2 | courtyard, playground, glass_close/interior | Court-facing ground-floor full-height glazing has no coloured fins; source oblique shows fins at the ground floor too (around x 420-560, y 460-520). Ground floor of the east street facade also lacks fins (source front x 850-970). | fins only on upper storey | Add fins to the ground floor using the same rhythm. |
| 8 | P2 | aerial, entrance_passage, top | Canopy deck seams are faint lines; source has pronounced standing-seam corten slats. | seam depth | Add raised standing seams or slat ribs at the source spacing. |
| 9 | P2 | aerial, rear_side, penthouse_terrace | Raised gravel boxes or rooflights on the west wing (source oblique x 215-330, y 340-390) are missing; rooftop plant boxes are generic. | omitted roof furniture | Add the two raised rectangular roof upstands on the west wing. |
| 10 | P2 | left_side, rear | Party walls are flat, uninterrupted brick with no coping line distinct from the walls. This is coherent for party walls, but the concrete coping band visible on the street faces does not continue. | coping only on street faces | Continue the concrete coping on the party-wall parapets. |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette (U around a south court, NW higher block, mid-block corner plot) | conforms | top vs source top; aerial vs oblique |
| Storey count (2 brick storeys + 1 corten storey on the NW block; one-storey canopy) | conforms | front, right_side, front_corner |
| Courtyard and wings (court ratio ~1.0 vs source ~1.02; west wing full depth to street; east wing stops ~47% of court depth short of the street) | conforms | top (court y 612-910, wing end y 770) vs source top (court 465-715, wing end ~600) |
| Entrance passage and canopy (corten canopy over court strip + pad, open covered passage, concrete corner box) | deviates: box does not run to the street, the forecourt is light and open at the corner (F1), the fascia is thin (F4) | aerial, entrance_passage, facade_close, top |
| Fins and glazing (strip windows with red/yellow/green/teal fins, full-height court glazing) | deviates: extra fins and window on the blank south end face (F2); ground-floor fins missing (F7, P2) | fins_close, courtyard, entrance_passage |
| Corten storey (NW, corten-clad, south glazing, rails) | conforms | penthouse_terrace, aerial, front_corner |
| Roofs and rails (gravel roofs, paved hall terrace, perimeter rails) | rails conform; roof materials deviate (F3) | top, aerial, rear_side |
| Materials hierarchy (brick / concrete bands / corten / gravel / dark rubber court) | deviates: no gravel tone, light forecourt in place of dark yard paving (F1, F3) | top (sampled), aerial |
| Party walls west and north blank | conforms | left_side, rear |
| Street fence with gate | conforms (red gate present); fence end at the corner is wrong (F1) | playground, courtyard, entrance_passage |

## 4. Camera validity

All 18 views are valid. Nothing is clipped and every target is legible.
- left_side and rear are blank party-wall elevations by design. They are legible and correct, with little information.
- top is a valid orthographic plan. The pale-grey roofs on a pale ground lower the contrast (see F3), but the plan can still be read.
- interior is shot from outside through the glazing. Tables are visible, which is acceptable for clay.

## 5. Prior-version (v005) findings: status judged from the pixels

| v005 finding | Status | Evidence |
|---|---|---|
| P0: two-storey east wing reached the street line with the passage cut into its ground floor; the sources show the wing stopping ~47% of court depth short, with a one-storey slatted corten canopy pad over the court strip at wing width and open fenced yard paving beyond | **Resolved** for wing length and canopy pad. **Partly** for the yard beyond: it is light forecourt paving, open at the SE corner, instead of dark fenced yard paving enclosed by the box (now F1, P1). | top: wing south face y 770 within court y 612-910 = 47% short; corten strip x 810-900 plus pad x 810-1045, y 770-860; aerial shows a one-storey canopy |
| P1: canopy street corner rested on a slender post where the sources show a solid board-formed concrete box with closed south and east faces under the corten band | **Resolved as stated**: a board-formed box with closed south and east faces now carries the corner, and the slender posts are only on the court side. It does not yet run to the street (F1). | entrance_passage box 750-1180 with board lines; aerial crop box below the canopy corner; facade_close |
| 7 v005 P2s (not listed individually in the brief) | Not individually verifiable from the brief; current P2s are listed above | n/a |
