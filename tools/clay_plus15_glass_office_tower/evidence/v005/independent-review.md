# Independent RLASM v6.1 holistic review: plus15 v005

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the three v004 P1s are fixed in the pixels, but two P1s remain. The Plus 15 bridge docks about 0.22 of the face width from the west corner, while the top source puts it just west of mid-face (about 0.48). The colonnade corner bays also show an unattached glass leaf and an open black soffit void.

**Counts: P0 = 0, P1 = 2, P2 = 9**

Method: I opened every image at full resolution (3 locked sources, 18 renders, 4 phone boards). I made crops of top, front, rear_service, plus15_bridge and architecture_close, and took simple pixel profiles and colour masks for floor count, colonnade height and green-roof share. I did not read any build code, reports, READMEs or notes.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | top (bridge x 620-655, south edge y 683); aerial (bridge 440-600, 640-800); front_corner; board phone-01 | The bridge leaves the south face at about 0.22 of the face width from the west corner (x 620-655 inside 575-862). In sources/top.jpg the bridge strip (x 578-628, y 645-850) sits at about 0.48 of the face (365-858), just west of centre. The oblique also shows it near mid-face, at about 0.4 of the left face after allowing for foreshortening. The front source shows it to the left of the near corner, not tight to the far corner. Matched top-to-top, the bridge is about 6 bays too far west. | The bridge was placed at the brief's "west end" wording, not at the measured top-source position. | Move the bridge axis east to about 0.45-0.48 of the south-face width, measured from the west corner. Keep its level inside the colonnade and keep both piers. Re-check top, aerial, left_side, plus15_bridge and architecture_close. |
| 2 | P1 | rear_service (glass leaf x 1310-1395, y 15-700; black void x 1390-1440, y 0-55); plus15_bridge (black void x 710-775, y 272-292 over an opaque pale panel x 710-780, y 290-380 in the last colonnade bay before the corner column) | The colonnade corner bay is not closed. In rear_service, one full-height glass leaf stands proud of the column line, past the last column, attached to nothing, with a black unlit gap above it at the soffit. In plus15_bridge, the bay next to the corner column has a black wedge where the soffit should be, and a flat pale panel instead of recessed glazing. This is a floating part and an opening with no closed return, at a corner that the detail cameras frame. This is the v004 "loose glass leaf" P2, now with a soffit hole visible beside it. | The recessed lobby glass line and the colonnade soffit stop short of the corner bay. The last glazing panel is placed on the column line, not on the recessed line. | Run the recessed glass line and its corner mullion around the corner behind the corner column. Delete or snap the stray leaf onto the recessed line. Extend the colonnade soffit slab to the corner column so no black void can be seen. Re-render rear_service and plus15_bridge. |
| 3 | P2 | lobby_entry (x 730-945, y 515-528) | A thin black transom gap remains above the centre door set. | The door frame head sits below the transom bar. | Raise the door head or lower the transom so they touch. |
| 4 | P2 | interior | The window wall is one flat dark band with tiny sill ticks. There are no mullions and no spandrel or vision split as seen from inside. | The interior uses a single plane for the glazing. | Add interior mullions at the exterior bay pitch and a sill or upstand. |
| 5 | P2 | plus15_bridge; left_side; architecture_close | The bridge glazing is still coarse: 4 panes span the frame, at a ratio of about 1.1:1, with thin mullions. The front source shows about 0.8:1 panes and heavier frames. | Bridge mullion spacing is too wide. | Tighten the bridge mullion pitch by about 30 percent and match the tower mullion profile. |
| 6 | P2 | front (y 215-228); crown_penthouse; source oblique | The parapet band is about one spandrel deep. The oblique shows a slightly heavier pale coping band, about 1.3-1.5 times a spandrel. | The parapet height is the same as a spandrel. | Raise the parapet band by about 40 percent. |
| 7 | P2 | top; roof_terrace; rear_side | The green-roof share is now about 19 percent of the roof, against roughly 21-27 percent in the source, so the gap is no longer P1. Remaining gaps: the south bed is shallower (0.105 of roof width against about 0.14 in the source) and stops about 0.1 short of the penthouse's east edge. The west-bed path is at 0.31-0.36 of the depth where the source has it at 0.46-0.57. The small roof hatch box that interrupts the source's south bed is missing. The beds are a flat green with no mottling. | The bed rectangles are tuned slightly small. | Deepen the south and NE beds by about 35 percent, extend the south bed to the penthouse's east wall, move the west path to mid-depth, add the hatch box, and use two-tone bed colour. |
| 8 | P2 | crown_penthouse; roof_terrace; front | The penthouse fins have a mid-height transom that splits them into two tiers. The source oblique reads as single tall fins. A small stepped plinth corner shows at crown_penthouse (x 1000-1170, y 600-690). | The fin modules are stacked. | Use single full-height fins and trim the plinth step to the fin line. |
| 9 | P2 | top; aerial; front_corner | The bridge is about 0.78 tower widths long over a street of about 0.54 tower widths. The source has about 0.46 widths over about 0.33. The landing block is a bare box. | The street and bridge length are overscaled. | Shorten the street and bridge to the source proportions. |
| 10 | P2 | front (box x 536-668, y 855-975); top | The bridge landing box hides one lobby bay in the front view. The top view uses about 20 percent of the frame width, which wastes resolution (framing). | Camera framing. | Tighten the top and front framing, or offset the front camera so the box does not cover the lobby. |
| 11 | P2 | architecture_close (bridge end x 980, column 1000-1040) | The bridge end meets the colonnade column line. From the rendered angles I cannot confirm that its enclosure reaches the recessed lobby glass. | The bridge-to-glass connection is not framed by any camera. | Add a short glazed throat from the column line to the recessed glass, and frame it once. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (square tower, penthouse about 0.4 of the roof, slightly north-heavy) | conforms | top vs source top (penthouse share 0.40 vs 0.41), front_corner and aerial vs oblique |
| Floor count | conforms: 16 office floors by vision-band count (left_side x 700: bands start at y 207 and repeat every ~38 px to 775), within the 16-18 the oblique reads | left_side, front, right_side, rear |
| Spandrel and mullion rhythm | conforms: a pale spandrel under each dark vision band, about 23 close mullions per face, mullion returns visible | facade_close, glass_close, curtain_grid, front |
| Corner columns and parapet | corner columns conform (single full-height pier, not doubled); parapet deviates slightly (P2 #6) | architecture_close, curtain_grid, front, crown_penthouse |
| Lobby colonnade and entry | deviates (P1 #2 at the corner bay); otherwise conforms: about 3.5-3.9 floor pitches high with an intermediate band, glazing recessed behind perimeter columns with visible depth, door sets present (P2 #3) | front, left_side, lobby_entry, rear_service, architecture_close |
| Bridge | deviates (P1 #1, position along the face); level inside the colonnade conforms; enclosed glazed tube conforms; two piers conform | top, aerial, left_side, plus15_bridge, architecture_close |
| Green roof and penthouse | conforms at P1 level: an L of beds from walkway to penthouse wall with a west path and a continuous south bed; one full-height glazed box including the unit court, units in the open-topped court; P2 #7 and #8 remain | top, aerial, rear_side, roof_terrace, crown_penthouse |
| Materials hierarchy | conforms: pale clay frame, spandrels and columns; dark blue-grey vision glass; lighter lobby and bridge glass; green beds | all views |

## 4. Camera validity

- All 18 views are legible and none clips its target.
- The front view: the bridge landing box covers about one lobby bay (P2 #10). The view stays valid.
- The top view: the asset fills only about 20 percent of the frame width, which hurts detail. The view stays valid.
- interior shows the target window wall, but it is flat (P2 #4).
- No view is invalid.

## 5. v004 findings, judged from v005 pixels

| v004 finding | status | evidence |
|---|---|---|
| P1 colonnade base only about 1.5 floor pitches, with no intermediate band | resolved | left_side: lobby y 811-943 at a 38 px pitch = 3.5 pitches; front: 765-893 at 33.6 px = 3.8 pitches; intermediate band visible in lobby_entry and rear_service |
| P1 bridge docked into the first office floor, not inside the colonnade | resolved (level). The position along the face is a new P1, #1 | left_side: bridge y 840-885 lies inside the lobby zone 811-943; architecture_close and plus15_bridge show it under the first spandrel |
| P1 only the north part of the penthouse was full-height glazing, with units behind a low picket rail | resolved | crown_penthouse, roof_terrace and rear_side: full-height glazed fins wrap the unit court; the penthouse is about 0.40 of the roof in top |
| P1 green-roof beds were narrow planters, about 14 percent | resolved to P2 | top: about 19 percent green against roughly 21-27 percent in the source; west path and continuous south bed present; residual depth and hatch gaps are P2 #7 |
| P2 shallow parapet band | not resolved | front and crown_penthouse: parapet is about one spandrel deep |
| P2 loose glass leaf at the rear corner | not resolved, raised to P1 #2 | rear_service x 1310-1395, now with a black soffit void; plus15_bridge corner-bay void |
| P2 doubled corner columns | resolved | architecture_close and curtain_grid show a single pier |
| P2 transom gap at the lobby doors | not resolved | lobby_entry x 730-945, y 515-528 |
| P2 flat interior window wall | not resolved | interior |
| P2 coarse bridge mullions | partly resolved (still coarse) | plus15_bridge: 4 panes span the frame |
| P2 framing | partly resolved | top still small in frame; front box covers a lobby bay |
