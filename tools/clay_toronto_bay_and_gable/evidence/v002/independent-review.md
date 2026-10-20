# Independent holistic review: Toronto bay-and-gable house, clay v002 (RLASM v6.1)

Reviewer: independent, adversarial. I checked only rendered pixels against the locked source pixels (sources/front.png, sources/oblique.jpg, sources/top.jpg). I opened all 18 renders and all 4 phone boards at full resolution. I wrote zoomed crops only to a new folder: `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/bayg-v002-indep-crops-6d6b7958/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: All six v001 P1s are fixed in the pixels. Two P1 problems remain:
- The front gable is not carried forward over the canted bay. Instead the bay sticks out past the gable face under a flat slate ledge, which breaks the defining bay-and-gable relationship.
- The porch braces cut through the frieze rail and the posts, leaving black patches.

Counts: P0 = 0, P1 = 2, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner, roof_chimney, top, aerial, gable_bargeboard, bay_window (compare source oblique, source top, source front) | The front gable sits flush with the main south eave. Its bargeboard feet line up with the main eave line in the top view (render top, about y 968 of the crop). The upper bay projects about 0.7 m past the gable face and is capped by a separate flat slate ledge. That ledge reads as its own small flat roof in front of the gable in front_corner and roof_chimney. In the sources the gable projects forward over the bay: the source top gable foot is about 1 m in front of the main eave. The upper bay meets the gable's horizontal base cornice directly, with brackets under the overhanging gable corners, and there is no flat roof on the bay. The render's gable feet instead drop on stepped brackets onto the main wall beside the bay. | The cross-gable volume (bargeboards, gable field, attic windows) is anchored to the main wall plane plus overhang, not to the bay's front face. The "slim slate ledge" bay cap fills the gap. | Move the cross-gable front plane forward to the bay's front face: bargeboards, gable field, attic windows and pendant/finial. Lengthen the cross-gable ridge and slopes so they run back into the main south slope. Replace the slate ledge with a horizontal gable-base cornice sitting on the upper bay. Put brackets under the gable corners where they overhang the canted faces. Re-render front_corner, roof_chimney, top and aerial. |
| 2 | P1 | porch_entrance, porch_frieze, bay_window | Every diagonal porch brace shows a black parallelogram where it meets the frieze rail, and a black sliver where it enters the post. There are four such patches across the front in porch_entrance, plus more on the far side in porch_frieze. They are conspicuous at detail scale and show the braces cutting through the rail and post instead of bearing on them. | The extended bracket solids overlap the rail and post, so interior or end faces show through (coplanar or inverted faces). | Cut each brace so its ends finish flush on the rail underside and the post face. Delete the overlapping end caps and recalculate normals. Re-render porch_entrance and porch_frieze. |
| 3 | P2 | gable_bargeboard, front | Attic triple window: the side lintels sit lower than the centre lintel and crowd the centre window's jambs. The pendant tip lands on the centre lintel. The source has one composite triple window under a shared head. | Each sash has its own lintel block. | Use one continuous head or lintel band across the triple window, and stop the pendant above it. |
| 4 | P2 | gable_bargeboard, front | The gable field reads as light grey horizontal siding, not grey-brown shingle with darker courses (builder claim not seen in the pixels). | The colour or course spacing is too pale and too even. | Darken to a grey-brown and use stronger, closer shingle courses. |
| 5 | P2 | porch_frieze, porch_entrance | The porch entablature or fascia is still deep and heavy compared with the slim fascia and spindle frieze in the source. | The beam depth was not reduced enough. | Reduce the beam depth by about 40%. |
| 6 | P2 | bay_window, front, foundation_fence, rear_north | There are small black slivers at the bay cornice mitres (front and bay_window top) and at the bay plinth canted corners (bay_window base). Black dots also show at the muntin crossings of the basement windows and the rear door. | Small mitre gaps and overlapping muntin bars. | Close the mitres and merge the muntin crossings. |
| 7 | P2 | front_corner, aerial, left_side, right_side, rear (and phone-01, phone-03) | The building fills only about 20 to 30% of the frame width. On the phone boards the front_corner and aerial panels show only massing. The house is still legible, but the claimed tighter framing is marginal. | The camera distance and focal length are too wide. | Move the camera in or lengthen the focal length so the house fills about 50% of the frame. |
| 8 | P2 | provenance | The brief lists facade_close, architecture_close and glass_close among the detail views, but no such files exist. Only 18 renders are present, which matches the stated count. Glass and facade detail is partly covered by bay_window and porch_entrance. | The list in the brief is out of step with the render set. | Render those three views, or correct the list. |

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | deviates | front_corner, roof_chimney, top: the overall L-plan, steep roofs and cross gable read correctly, but the gable does not project over the bay (finding 1). |
| Storey count and proportions | conforms | front, west_side: raised ground floor, upper floor and attic gable, two and a half storeys, matching the source. |
| Brick and joints | conforms | bay_window, west_side: red-brick clay with fine coursing. |
| Stone foundation and basement windows | conforms | foundation_fence, west_side, rear_north: grey foundation with basement windows. Smooth clay stands in for rough stone, which is acceptable for clay. Black muntin dots are finding 6 (P2). |
| Canted bay: three faces | conforms | bay_window, top. |
| Canted bay: sashes | conforms | bay_window: tall one-over-one sashes on all faces. |
| Canted bay: amber transoms | conforms | bay_window, front. |
| Canted bay: stone bands | conforms | bay_window: continuous mitred bands at ground sill, ground lintel (under the skirt), upper sill and upper lintel. Minor mitre slivers are finding 6. |
| Canted bay: slate skirt roof | conforms | bay_window, front. |
| Front gable: bargeboard | conforms | gable_bargeboard: one board per rake with no inner boards. Its placement relative to the bay deviates (finding 1). |
| Front gable: roundels and drops | conforms | gable_bargeboard: rings on the board face and drops from the lower edge. |
| Front gable: fretwork arch | conforms | gable_bargeboard: pierced arch inside the gable with spandrel spindles. |
| Front gable: finial and pendant | conforms | gable_bargeboard, front. Minor clash of the pendant with the lintel is finding 3. |
| Front gable: triple attic window | deviates (P2) | gable_bargeboard: staggered lintels (finding 3). |
| Front gable: relationship to the bay | deviates | front_corner, roof_chimney, top (finding 1). |
| Porch: turned posts | conforms | porch_entrance. |
| Porch: spindle frieze | conforms | porch_frieze. |
| Porch: corner brackets | deviates | porch_entrance, porch_frieze: braces intersect the rail and posts with black patches (finding 2). |
| Porch: iron balustrade | conforms | porch_entrance. |
| Porch: hipped roof | conforms | front, top. The fascia is heavy (finding 5). |
| Door and transom | conforms | porch_entrance: dark green door with raised lower panels and an amber transom. |
| Stair and walk | conforms | front, top, porch_entrance: stone stair with iron handrails down to a brick walk. |
| Roof: cross gable | deviates | top, roof_chimney: the cross gable is present but sits flush with the main eave (finding 1). |
| Roof: west and east gables | conforms | west_gable, roof_chimney, top: the front block is gabled to west and east with no hip lines. |
| Roof: rear hip | conforms | rear_side, rear_north, top: hipped wing whose ridge dies into the main north slope along two valleys, on one eave line. |
| Roof: chimney | conforms | roof_chimney, top: brick chimney at the east gable end on the ridge. |
| West side windows | conforms | west_side: tall sashes with stone sills and lintels. |
| West gable window | conforms | west_gable: paired tall one-over-one sashes with sills and lintels. |
| Fence | conforms | foundation_fence, top: low iron fence on the south and west of the front lawn. |
| Lawn, sidewalks and trees | conforms | top, front: south street and west side street with sidewalks, lawn, shrubs and street trees (low-poly clay). |
| Materials hierarchy | conforms | front: brick body, buff stone bands, tan woodwork, grey slate, dark iron, green door. |

## 4. Camera validity

- No view has the target occluded, clipped or illegible.
- front_corner, aerial, left_side, right_side and rear are framed loosely; the house is small in frame (P2, finding 7).
- west_gable has a tree crown entering the lower right corner, but the gable is fully legible.
- interior is a legible room with a fireplace and a window wall.
- The matched roles agree with the sources:
  - front vs source front
  - front_corner and aerial vs source oblique
  - top vs source top
- Three detail view names in the brief have no render (finding 8). This is not a camera defect.

## 5. Previous-version (v001) findings: resolved in pixels?

1. **Fretwork arch outside the gable, with stub boards: RESOLVED.** In gable_bargeboard and front, the arch is a pierced board inside the gable in the bargeboard plane. It springs from the inner edges of the bargeboards and crests just above the attic lintels, with spindles in the spandrel. Nothing lies across the roof slopes and no boards poke through either rake.
2. **Doubled bargeboard with floating roundels: RESOLVED.** There is one board per rake from the apex to the foot, with roundels on its face and drops from its lower edge. The inner diagonal boards are gone and no rings float on the brick. Each foot ends on a block and a stepped bracket down to the wall. Where these brackets land is part of new finding 1.
3. **Stacked rear roofs, tan ledge and black hip voids: RESOLVED.** In rear_side, rear_north, aerial and top there is a single eave line with one fascia and gutter, and no tan ledge. There are no black voids at the hip corners or valleys.
4. **Plan not following the source top: RESOLVED.** The top view shows an L plan with a dominant gabled front block and a narrower hipped rear wing. The wing is inset on both sides and its width is about 0.69 of the front block, which matches the source. The ridge is centred and the chimney is at the east end. The remaining plan deviation is the gable-over-bay projection (new finding 1).
5. **Single small window in the west gable: RESOLVED.** west_gable shows two tall one-over-one sashes side by side under the ridge, each with a stone sill and lintel.
6. **Broken bay bands: RESOLVED.** bay_window shows continuous mitred bands around all three faces at the ground sill, ground lintel, upper sill and upper lintel, and the upper lintel band clears the bay cornice. Small black mitre slivers remain (P2, finding 6).
