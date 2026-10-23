# Independent holistic review: The Overhang, v002

Reviewer: independent RLASM v6.1 holistic reviewer. I did not build this candidate. I opened all 18 renders at full resolution, the three locked sources and the four phone boards, and zoomed into the junctions listed below. Metadata and builder notes were not used as proof.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: The plan, storey grammar, pool deck and the leaning, open-topped timber shell all match the sources, but two P1 defects block production approval. The rooftop penthouse is roughly twice the height the sources show. The shell's west flare meets the frame-box parapet and spandrel bands with a visible stepped, intersecting edge.

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, rear, rear_side, pool_deck (compare source front) | The penthouse reads as a tall, nearly double-height pavilion. In the render front, its west glazing is about 1.2x the height of the frame-box ribbon storey below it. In the source front it is about 0.55x. The penthouse wall is about 2.25x the height of its north door, against about 1.3x in the source. In the rear view the blank penthouse wall rises about 1.7 pool-block storeys above the parapet and about 90 px above the four-storey east block's roof line. The source shows a low, one-storey pavilion just above the pool deck. | The penthouse box height (or the deck level it sits on) is set to about 7-8 m instead of a single storey of about 4 m. | Cut the penthouse to one storey (about 4 m from deck to roof, with about 3 m of glazing) and keep its plan, door, glazing split and roof plant. Check that the door is about 0.7-0.75 of the wall height and that in the front view the glazing is about 0.5-0.6 of the frame-box ribbon storey. Check that the roof stays only slightly above the east block, as the shadow in the top source implies. |
| 2 | P1 | rim_interior (clear), top (visible at the shell's west flare / frame-box junction, about x 560-585, y 690-730) | Where the shell's west flare meets the south end of the pool block, the white frame-box parapet band and the spandrel band below it cut into the timber. This leaves two small honey-coloured stepped notches, so the edge is serrated instead of one clean fold. The bands' ends stick through the shell plane. | Parapet and spandrel boxes are extended "into the shell" and overlap the flare planes. Their ends are not trimmed to the shell surface, and the shell polygon is not closed over them. | Trim the parapet and spandrel bands to end exactly on the shell's west face, or extend the flare plane so it fully covers their ends. Leave no honey return faces around the band ends. Re-check from rim_interior and top that the junction reads as one straight fold, as it does in the top source. |
| 3 | P2 | front, front_corner, aerial, rim_interior | South-face holds are still about 2-3x denser than in the source and read as a busy speckle. The broad west faces carry no holds, although the source shows a few white holds near the west/south fold. | Hold scatter density is too high; the west-face hold set is empty. | Thin the south-face holds by about another 40-50% and add about 10-20 sparse white holds near the west/south fold. |
| 4 | P2 | climbing_face, front, right_side | All three climbers use the same rigid spread-eagle pose (both arms straight up, legs splayed). | One shared pose rig. | Vary the poses: one reaching, one with a flagged leg, one resting with one arm low. |
| 5 | P2 | top, rim_interior | Inside the hollow, the inner walls show a soft curved light gradient that reads like a warped surface rather than flat folded CLT planes. The dark deck is clear. | Point-light falloff in the dimmed hollow. | Use flat or area fill inside the hollow so each inner plane reads as a uniform facet. |
| 6 | P2 | aerial | The glass ribbons on the white facade under the east overhang read as thin double-line streaks rather than recessed glazing. | Very shallow ribbon depth seen at a grazing angle. | Deepen the ribbon reveal slightly, or darken the glass so they read as openings. |
| 7 | P2 | front, front_corner, wall_base_contact | The shell's west face facets are low-contrast. The source shows a strong diagonal crease across the sunlit west face. | Flat shading with planes in similar orientations relative to the key light. | Raise the key-light angle contrast, or tilt the crease planes slightly further apart. |
| 8 | P2 | front, front_corner, top, pool_deck | The pool water is muted grey-blue (about RGB 111,150,162) against the turquoise source (about 90,181,200). Overall exposure is grey and dim, and the rear elevation is underlit. | Water material and exposure. | Use a more saturated pool colour and lift the exposure about 0.3 EV; add a rear fill. |
| 9 | P2 | front, front_corner (compare source front and oblique) | The source shows short flights of steps where the plaza meets the west sidewalk and the south-east corner. The render plaza is flush with the sidewalk. The street-tree crowns are larger and rounder than the young trees in the source. | Plaza edge not authored; generic tree asset. | Add 2-3 risers at the plaza's west and south-east edges, and shrink the street-tree crowns by about 30%. |

Counts: **P0 = 0, P1 = 2, P2 = 7**

## 3. Source conformance checklist

| Item | Status | View(s) used | Notes |
|---|---|---|---|
| Silhouette: three-storey pool block | conforms | left_side, front, rear | Recessed glazed ground floor plus two upper storeys and a deep parapet. |
| Silhouette: penthouse | deviates | front, rear, rear_side vs source front | One floor, but about twice the source height (finding 1). |
| Silhouette: four-storey east block | conforms | right_side, rear, aerial | Four storeys; the north and east faces are coherent with the visible grammar. |
| Plan (top view) | conforms | top vs source top | Pool block on the west with a north-south pool along the west edge, deck and lounger column to the east, penthouse strip in the middle, east block with skylights, shell rim over the south plaza east of the pool block. Proportions are within a few percent. |
| Shell: foot on the plaza | conforms | wall_base_contact, entrance, front | Long base edge sitting on the paving beside the entrance bay; no gap seen. |
| Shell: lean and overhang | conforms | front, front_corner, right_side, aerial | Leans east at about 23-25 degrees, matching the source; the rim cantilevers over the plaza and the white facade. |
| Shell: folded faces | conforms (P2 contrast) | front_corner, rim_interior, top | Lower flare, upper panel and horizontal fold at parapet height are all present; facet contrast is weaker than the source. |
| Shell: level open rim with light fascia | conforms | front_corner, rim_interior, top | Level rectangular rim with a lighter timber fascia. |
| Shell: contact with the plaza | conforms | wall_base_contact | |
| Shell: contact with the facade | deviates | rim_interior, top | Serrated band intersection at the frame-box junction (finding 2). |
| Holds and climbers | conforms (P2) | climbing_face, front, right_side | Dark and white holds, densest on the south face; three climbers on the south mid panel with hands on holds. Density is high and the poses are identical. |
| Open top and inner walls | conforms | top, rim_interior, front_corner | Inner walls with white holds; dark crash mat/deck visible at the bottom from above. |
| West front rhythm (fins, spandrels, recessed windows, glazed ground floor) | conforms | left_side, facade_close | About 10 bays, matching the source; reveals and returns are visible. |
| South frame box and glass ribbons | conforms | front, architecture_close, glass_close | Projecting white frame holding two storeys of glass ribbons. |
| Entrance doors | conforms | entrance, interior | Two pairs of doors in recessed ground-floor glazing. |
| Parapet band | conforms | left_side, architecture_close | Deep white band with glass balustrade above. |
| Pool deck: infinity pool, weir and trough | conforms | pool_deck, rear_side, top | Overflow channel along the west edge at the parapet. |
| Pool deck: glass balustrades | conforms | pool_deck, left_side, rear_side | |
| Pool deck: loungers | conforms | pool_deck, top, front | Row along the penthouse plus a row at the north end. |
| Roof garden (planters, grasses, small trees) | conforms | rear_side, pool_deck, top | Raised planters with grasses and yellow-green trees at the north end. |
| Penthouse: glazing and solid end with door | conforms | pool_deck, front, rear_side | Glazed to the deck at the south end; solid with a door at the north end. |
| Penthouse: roof plant | conforms | top, rear_side | Air-handling unit with fan. |
| East block roof (skylights, plant) | conforms | top, rear_side, aerial | Two skylights and small plant. |
| White facade under the overhang | conforms (P2) | right_side, aerial | Ribbons with a vertical return; they read thin in the aerial view. |
| Plaza: paving bands | conforms | top, wall_base_contact, plaza_planters | Two-tone grey bands. |
| Plaza: grass planters | conforms | plaza_planters, top, front | Raised rectangular south-west planter and L-shaped south-east planter with tall straw grasses. |
| Plaza: bollards and lamp posts | conforms | aerial, right_side, front | |
| Sidewalks | conforms | left_side, top | Steps at the plaza edges are missing (P2). |
| Street trees | conforms (P2) | left_side, top | In pits; crowns are oversized. |
| Streets and crossings | conforms | top, aerial | West street and east street, each with crossings. |
| Parked cars | conforms | right_side, aerial, top | |
| Neighbours | conforms | aerial, front, rear_side | Generic brick and grey mid-rises, which is acceptable as clay context. |
| Materials hierarchy | conforms | all | White precast, glass, honey CLT (front, about 188,140,70, within the source palette), grey granite. Pool colour is muted (P2). |

## 4. Camera validity

No view is invalid. Every whole-envelope view (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) shows the target unoccluded and legible. left_side hides the shell behind the pool block, which is expected for a west elevation, and shows the rim above the parapet. The detail views crop the shell on purpose (climbing_face, wall_base_contact, entrance, plaza_planters) but stay legible. In the rear view the facade is underlit and the windows read near-black, but the elevation is still legible (P2, finding 8). The top view is slightly off-nadir, so a strip of the shell's south face is visible below the rim; this is consistent with the source top and is not a defect.
