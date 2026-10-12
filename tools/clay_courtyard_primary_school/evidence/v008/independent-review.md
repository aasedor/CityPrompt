# Independent holistic review: clay courtyard primary school, v008 (RLASM v6.1)

Reviewer: independent, did not build. Evidence used: the three locked sources, all 18 renders at full resolution, and the four phone boards. I did not read any source code, build reports or builder notes. Pixel coordinates are in each image's native resolution (renders 1440x1080, sources 1024x768 / 1195x896).

## 1. Verdict

**VISUAL_REWORK_REQUIRED.** The fins, corten storey glazing and deep canopy fascia are now right. The south-east street corner still differs from both sources in two ways. From the street the passage still reads as a slot beside the concrete wall, not as a concrete-lined opening under the brick upper storey. The corner concrete wall stands beside the canopy instead of carrying it.

Counts: P0 = 0, P1 = 2, P2 = 6

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | right_side x365-520 y590-670 (passage mouth = gap at x365-415; the entrance block's east ground floor at x435-500 is a finned classroom window); aerial x855-895 y780-860 (narrow light-floored slot between the concrete box and the brick block); facade_close x1045-1185 y600-760 (the east side of the passage is a closed brick wall with a window). Sources: front.png x710-800 y485-590 (recessed glazed entry doors in a concrete-lined opening on the east face, directly behind the corner wall); oblique.jpg x800-870 y590-660 (dark opening and light concrete floor under the brick upper storey, facing the street). | The entrance block's ground floor is now open, but only towards the yard and court. On the street face, which is the face both sources show, there is no opening under the brick upper storey. The block shows brick and a finned classroom window there. The only street access is still the gap between the concrete wall and the brick block, south of the block, under the canopy. Seen from the street, this is the same "gap beside the concrete wall" that v007 reported. | The passage volume was opened on its south (yard) and west (court) sides only. The east (street) wall and its window were kept, so the passage's mouth is on the wrong side. | Open the entrance block's east ground-floor bay nearest the corner, about one bay wide and the full ground-storey height, directly north of the concrete wall. Line its jambs and soffit in concrete. Set the glazed double entry doors plus one solid corten-tone leaf about 1-1.5 m back from the facade line, as in source front x710-800. Remove the finned window from that bay. The yard-side openings can stay. |
| 2 | P1 | front x1160-1215 y585-690 (box rises to the canopy's top edge and stands proud of the canopy's east end); aerial x695-800 y790-900 (stacked box whose top face is exposed beside the canopy end; the canopy butts into its west flank); architecture_close x910-1320 y950-1080 (box top level with or above the canopy surface, in front of it); entrance_passage x850-1180 y280-840. Sources: oblique.jpg x720-800 y650-790 (the corten fascia runs continuously over the top of the concrete wall, and the wall top is hidden); front.png x600-710 y448-600 (the fascia band sits on the wall). | The corner concrete wall reads as a separate free-standing pier or box that reaches the full canopy height, with the canopy stopping against its side. In both sources the wall is a ground-storey support under the canopy, and the deep corten fascia wraps continuously across its top at the corner. This changes the main street-corner composition, the most recognisable feature of the building. | The wall height was set to the canopy's top elevation and its footprint sits outside the canopy outline. The canopy is trimmed to the wall instead of oversailing it. | Lower the wall top to the canopy underside (the bottom of the 0.9 m fascia). Extend the canopy slab and fascia so that they oversail the wall by the fascia thickness on its south and east faces, and wrap the fascia around the corner above the wall. Check that the wall and the canopy underside meet with no gap and no overlap in aerial, front and architecture_close. |
| 3 | P2 | top x395-585 y615-915 vs source top x300-480 y550-720 | The west wing is one flat roof. The source shows a stepped roof with a raised strip or rooflight band and two gravel fields. | Simplified roof massing | Add the low upstand or rooflight strip across the west wing roof. |
| 4 | P2 | front_corner (whole frame); board phone-01, second row | The corner camera is from the south-west and shows the blank west party wall. The locked oblique, which the board pairs it with, is from the south-east street corner. The comparison does not match by role (aerial does match). | Camera placed at the wrong corner | Move front_corner to the south-east, at roughly the oblique source's bearing and elevation. |
| 5 | P2 | facade_close x735-810 y610-750; entrance_passage x760-850 y480-660; playground x1280-1410 y370-540 | An external straight stair in the passage runs up into the passage soffit. No landing or soffit opening is legible. The stair does not appear in any source. | Stair added for coherence; its upper end is not resolved | Show a soffit opening with a landing above it, or move the stair behind the glazed screen. |
| 6 | P2 | front y480-500 and y585-595; source front y365-410, y475-490 | The concrete parapet copings and first-floor bands are thinner and less dominant than the heavy concrete bands in the source. | Band depth under-scaled | Increase the parapet coping to about 0.6 m and the floor band to about 0.4 m. |
| 7 | P2 | front (whole frame) | The building fills only about 45 % of the frame width, with a large empty sky and ground. It is legible but under-framed. | Camera distance | Tighten the framing to about 80 % of the frame width. |
| 8 | P2 | interior | The "interior" view is taken from outside the glazing. The interior shows only as reflections and furniture behind the glass. | Camera outside the envelope | Acceptable for clay. Optionally place the camera inside the classroom, looking out to the court. |

No P0 findings. The storey count, U plan, playground, party walls, corten third storey, roof rails, fence and gate are all present. No part was found floating or intersecting, apart from the stair top in #5, which is ambiguous rather than visibly broken.

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | conforms. U around a south playground; NW corten box; NE notch beside the north party line. | top vs source top; aerial vs oblique |
| Storey count | conforms. Two brick storeys plus a corten third storey over the NW only. | front, right_side, rear_side |
| Courtyard and wings | conforms. West wing, north hall range and SE entrance block enclose the court; paved hall terrace; gravel patch to the NE. | top, aerial, courtyard |
| Entrance passage and canopy | deviates (findings #1 and #2). Canopy plan and the deep fascia conform. The street-facing passage mouth and the wall/canopy junction do not. | right_side, aerial, facade_close, front vs source front and oblique |
| Fins and glazing | conforms. Coloured fins on both storeys, street and court sides; full-height ground-floor court glazing with fins down to the ground. | glass_close, interior, courtyard, fins_close |
| Corten storey | conforms. Long east face glazed as one continuous band with slim mullions; south face solid corten with one door; rail on top. | aerial, rear_side, architecture_close, penthouse_terrace vs oblique |
| Roofs and rails | mostly conforms. Gravel-tone roofs and paved terrace with perimeter rails. The west-wing roof step is missing (P2 #3). | top, aerial, penthouse_terrace |
| Materials hierarchy | conforms. Brick (tan), corten (orange, more saturated), concrete (light grey), dark frames and coloured fins can be told apart. Concrete bands are under-scaled (P2 #6). | front, entrance_passage, courtyard |

## 4. Camera validity

No camera is invalid. The target is legible in every view and nothing is clipped. Weaker cases:
- **front_corner** shows the south-west party-wall corner instead of the street corner. It is mismatched by role, not invalid (P2 #4).
- **front** is under-framed (P2 #7).
- **interior** is taken from outside the glazing (P2 #8).
- **entrance_passage** has the corner concrete wall in the foreground, and it hides most of the passage's street side. The passage is still readable through facade_close and playground.

## 5. v007 findings: resolved in the pixels?

1. **Open passage read only as a gap south of the east wing beside the concrete wall.** PARTIALLY RESOLVED. From the yard (facade_close, playground, canopy_contact) the entrance block's ground floor is now an open passage. It has a concrete-framed opening, soffit, glazed screen into the hall, and a light floor. From the street (right_side x365-520, aerial x855-895) the passage still reads only as the slot beside the concrete wall, and the block's east ground floor is a finned window. This remains open as P1 #1.
2. **Corten canopy read as a thin plate where the sources show a deep fascia band.** RESOLVED. A deep corten fascia band is visible in front (y577-603), facade_close (y530-605), canopy_contact and courtyard, in proportion with the source band. The remaining problem is how the canopy meets the concrete wall (P1 #2), which is a separate defect.
3. **Coloured fins only on the upper storey.** RESOLVED. Ground-floor fins appear on the street windows (glass_close, right_side) and on the full-height court glazing (interior, courtyard, fins_close).
4. **Corten third storey opening rhythm differed on the long glazed face.** RESOLVED. The east face is one continuous full-height glazed band with slim mullions under a corten fascia (aerial x700-880 y370-470, rear_side x800-1100 y440-545, architecture_close x1035-1440 y325-440), matching oblique x620-775 y235-330. The south face is solid corten with a single door, consistent with the oblique.
