# Independent holistic review: stepg v002 (clay stepped-gable canal house)

Reviewer: independent RLASM v6.1 holistic reviewer (not the builder).
Inputs I looked at: sources/front.png, sources/oblique.jpg, sources/top.jpg; all 18 renders/*.png at full resolution; boards/phone-01..04. I made zoomed crops only in a new scratch folder (`indrev-stepg-v002-crops-x7q`). I did not use any metadata, counts or builder notes as evidence.

## 1. Verdict

**VERDICT: VISUAL_REWORK_REQUIRED.** v002 fixes the storey count, the left_side camera, the door, transom, stoop and gable-to-roof closure. But the pixels still show eight P1 defects: brick that reads as lap siding up close, a roof lighter than the brick, an invented stepped rear gable, east windows in the wrong place, an incoherent rear face, two weak cameras and a tree at the wrong scale.

Counts: P0 = 0, P1 = 8, P2 = 9

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | glass_close, wall_anchors, entrance_stoop, east_side (also visible on front_corner zoom) | The brick has only horizontal grooves, about two brick courses apart, with no head joints. In glass_close and wall_anchors the wall reads as painted lap siding or clapboard, and the projecting string course reads as a timber fascia. This is the v001 "brick reads as siding" finding, still present at close range. The colour itself is now correct (median render facade RGB about 109/75/60 against source about 108/74/55). | The joint shader or normal map draws bed joints only. Course spacing is about 2x the Dutch brick module. | Either add staggered perpends (head joints) at roughly 3:1 stretcher proportion and halve the course height, or remove the grooves and leave a flat clay brick colour. Re-render glass_close, wall_anchors and east_side. |
| 2 | P1 | front, front_corner, aerial, rear_side, roof_chimney, left_side, right_side | The roof is a mid blue-grey with luminance about 100 (sampled 95/100/107 on front_corner and aerial), lighter than the brick (about 75). In both sources the roof is the darkest mass: about 31/32/37 on the oblique and 45/50/59 on the front, clearly darker than the brick. So the value hierarchy is inverted, and the "steep dark tiled roof" does not read. | The roof material base colour or albedo is too light. | Set the roof albedo to near-black charcoal (about 0.04 to 0.06 linear, slightly blue) so the roof reads darker than the brick in every lit view. Re-check the front_corner and aerial against the oblique. |
| 3 | P1 | front, front_corner, aerial, top, rear, rear_side, roof_chimney | The rear (north) gable is a second crow-stepped gable with copings and a pinnacle, so the front view's east roof edge shows a sawtooth of steps (front, x 930–1040, y 380–520). The sources disagree: the front source shows a smooth straight rake there, and the top source (which governs the plan) shows a plain raked rear gable with a continuous white coping and the chimney stack (two pots) at its apex. The render's chimney instead stands on its own on the east slope, about a third of the depth from the rear (top render). | The front gable module was mirrored to the rear instead of authoring the rear gable from the top source. | Replace the rear gable with a plain raked brick gable with a continuous light coping. Move the chimney onto or against the rear gable apex, offset to the east as the front source shows, with two pots. |
| 4 | P1 | front, right_side, front_corner, rear_side, east_side | East side window schedule: the count and types are now right (2 small upper, 2 tall ground, basement grille), but the two small upper windows sit in the front third of the wall, at about 30% of the depth. In both the front and oblique sources they sit in the rear half, stacked directly over the first tall ground window (front source: small windows and the first tall window all at x≈805, about 62% of the wall's span on screen). This is the v001 "wrong east window schedule" finding, only half fixed. | The window x-positions were kept from v001. Only the count and sizes were changed. | Move both small upper windows back so their centres line up vertically with the first (front-most) tall ground window. Keep the second tall window and the basement grille near the rear corner. Re-render right_side and east_side. |
| 5 | P1 | rear, rear_north, rear_side | The rear face breaks the house's own grammar. Its two-bay windows have no white frames and no stone sills (only a grey glass sheet with a thin cross; the gable window has a sill but no frame). There are no iron anchors on the rear at all. Below the gable the wall has no joint lines (rear_north shows a seam about y 150 where the jointed gable meets the smooth wall). The rear reads as a stucco building of a different period. | The rear façade was built with a generic opening component and without the shared wall material and anchor set. | Reuse the front and side sash component (white frame, small panes, stone sill) on the rear openings. Put anchor rows at the rear floor lines. Apply the same brick material to the whole rear wall. |
| 6 | P1 | front_corner, aerial (matched role for sources/oblique.jpg); phone-01 | The two oblique matched-role cameras frame the house at about 5.6% of the frame area (about 235×370 px of 1440×1080), against about 27% in the source oblique. On the phone board the sashes, anchors, stoop and gable copings cannot be compared with the source. aerial is also nearly a duplicate of front_corner. The asset is not clipped, so this is P1, not P0. | Camera distance was set for the whole context slab, not for the building. | Dolly front_corner in to match the source oblique's elevation (about 35–40°) and scale (house about 60% of frame height). Make aerial a distinct higher view, or match the source oblique more closely. |
| 7 | P1 | glass_close | The camera crops its own subject. Only the head and top two pane rows of one first-floor sash are in frame (bottom third). The rest of the image is blank wall, string course and two anchors. The meeting rail, lower sash, sill and reveal depth of the glazing cannot be judged. | The camera target is on the anchor or string course height, not the sash centre. | Re-aim at one complete sash including its sill. Frame it at about 70% of frame height with a slight oblique, so the reveal return and glass recess are visible. |
| 8 | P1 | front, left_side, right_side, rear, top | The street tree is a short stick with a flat, wide low-poly "umbrella" crown. Its crown sits at about first-floor height, and it reads as a stone pine or acacia. In the front source the tree is a tall deciduous street tree with an upright oval crown reaching about the eave and gable base. | A placeholder tree asset at the wrong scale and form. | Use a clay deciduous street tree about 1.0–1.1× the eave height, with a taller clear trunk and an upright oval crown, in the same position west of the stoop. |
| 9 | P2 | front, facade_close, wall_anchors | Projecting brick string courses at both floor lines. The source has no projecting bands, only flat brick work and relieving arches over the windows. | An invented trim element. | Remove or flush the bands. Optionally add relieving-arch lintels. |
| 10 | P2 | stepped_gable, front | The hoist beam at the top of the gable in both sources (front and oblique) is missing. | Omitted detail. | Add a small light-stone or timber hoist-beam block below the top step. |
| 11 | P2 | entrance_stoop, front | The stoop is near-white (about 165/164/160) where the source stone is grey-beige. | Material too light. | Use a mid-grey stone value. |
| 12 | P2 | front, left_side, rear, top | The street "brick paving" is long, continuous parallel lines on a pink-tan slab and reads as timber decking. The slab ends abruptly on an infinite grey floor. | A plank-like stripe texture. | Use short staggered paver joints or a plain grey-beige clay. A road edge or kerb is optional. |
| 13 | P2 | entrance_stoop, front | Ground-floor windows are about 1.6× the upper-window height; the source ratio is about 1.2×. | Opening height. | Lower the ground window heads to the door-transom head and keep the sills. |
| 14 | P2 | entrance_stoop | The door surround carries a cornice cap. The source surround is a plain stone frame. | Extra trim. | Drop the cap or make it flush. |
| 15 | P2 | interior | The left wall has a tall, narrow, unlit dark slot with no glazing or daylight. It reads as a void, not a window. | Side opening with no glass or light, or a mismatched size. | Glaze it and size it to the small east upper window. |
| 16 | P2 | facade_close, stepped_gable, rear_north | In straight-on views the eave and gutter ends show as dark wedges outside the gable outline. The source shows a light cornice return there. | The gutter end cap is dark. | Give the eave end a light cornice return cap. |
| 17 | P2 | front, left_side, rear | The lamp is a plain post with a box head. The source has a tapered ornate standard with a lantern. | A placeholder asset. | Use a simple tapered post with a four-sided lantern head. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | deviates | front vs source front, front_corner vs oblique, top vs top | The front gable silhouette conforms. The added stepped rear gable puts a sawtooth on the east rake (F3). |
| Storey count and proportions | conforms | front, facade_close, front_corner | Raised ground floor with basement windows, two 3-bay upper floors and a gable with one window, matching both sources. Narrow and deep plan; the top-view depth to width is about 1.65 against about 1.4 in the source (acceptable). Ground windows are a little tall (F13). |
| Brick and joints | deviates | glass_close, wall_anchors, east_side, rear_north | Colour conforms. Joints are bed-only and read as siding (F1). Rear wall has no joints (F5). |
| Stepped gable: step count | conforms | stepped_gable vs source front | 5 steps each side plus the top block, as in the source. |
| Stepped gable: copings | conforms | stepped_gable, roof_chimney | Light stone copings on every step. |
| Stepped gable: gable window | conforms | stepped_gable | A single white small-paned window with sill. |
| Stepped gable: pinnacle | conforms | stepped_gable | Narrow top block with cap. The hoist beam is missing (F10). |
| Sashes and sills | conforms (front and east), deviates (rear) | facade_close, wall_anchors, entrance_stoop | 6-over-6 upper sashes, small-paned tall ground windows, stone sills, visible reveal returns. Rear has frameless, sill-less glazing (F5). |
| Door, transom and surround | conforms | entrance_stoop | Mahogany six-panel door, diamond-pattern transom, white surround stopping below the string course. The cap is extra (F14). |
| Stoop and rails | conforms | entrance_stoop, front | Four butted steps up to a landing at the threshold, light cheek face (no black face), newels on the bottom step and wall posts on the landing. Colour too white (F11). |
| Anchors | conforms (front, sides), deviates (rear) | facade_close, wall_anchors, east_side, rear | Vertical black bars at each floor line, 4 per row on the front. None on the rear (F5). |
| Side walls and windows | deviates | right_side, front, east_side, left_side | East has the right count and types but the small upper windows are in the wrong position (F4). The west (unseen in sources) is plain brick with a few small windows, which is coherent. White east eave board present. |
| Roof and chimney | deviates | roof_chimney, front_corner, aerial, top | Steep roof is closed to both gables with no voids. Too light (F2). Chimney is not at the rear apex shown in the top source (F3). |
| Street | deviates (P2) | front, top | Slab and side alley east are present, but the paving reads as decking (F12). |
| Tree and lamp | deviates | front, left_side, rear | Both are present and placed west of the stoop. Tree scale and form are wrong (F8); the lamp is simplified (F17). |
| Materials hierarchy | deviates | front, front_corner, aerial | The source runs dark roof < brick < white trim < light stone; the render runs brick < roof < trim (F2). |

## 4. Camera validity

- **left_side**: valid. The west wall is fully legible. The v001 blocking context box is gone.
- **entrance_stoop**: valid. Door, transom, both ground windows, both basement windows, the full stoop and rails are in frame (the v001 crop is fixed).
- **stepped_gable**: valid. All steps, copings, pinnacle and the gable window are in frame (the v001 crop is fixed).
- **glass_close**: deficient (P1, F7). It shows only the top third of one sash, so the glazing subject is clipped.
- **front_corner and aerial**: deficient (P1, F6). The target is legible as massing but too small to compare details with the source oblique. The two views are near-duplicates.
- **rear_north**: acceptable for a detail view. It crops the ground floor and gable top, but the rear wall grammar it is meant to show is legible.
- **front, top, right_side, rear, rear_side, facade_close, architecture_close, wall_anchors, east_side, roof_chimney, interior**: valid. Nothing is occluded or clipped and the subject is legible.

## 5. Previous-version (v001) findings, checked in the pixels

| v001 finding | status in v002 pixels | evidence |
|---|---|---|
| Extra upper storey | **resolved** | front and facade_close show ground plus two upper floors plus the gable window, matching sources/front.png. |
| left_side camera blocked by west context box | **resolved** | left_side shows the full west wall with no box. |
| Salmon brick reading as siding | **partly resolved; still P1** | The colour now matches the source. At close range the bed-only grooves still read as lap siding (F1). |
| Coarse sashes | **resolved** | 6-over-6 upper sashes and small-paned tall ground windows (facade_close, entrance_stoop). |
| Cross-shaped anchors | **resolved** | Vertical bars on the front and east (facade_close, east_side). The rear has none (F5, a new finding). |
| Flat orange door, plain transom | **resolved** | Mahogany six-panel door and diamond transom (entrance_stoop). |
| Door surround running into first-floor sill | **resolved** | The surround cap stops below the string course, well clear of the first-floor sill (entrance_stoop). |
| Black stoop side face | **resolved** | The cheek face is light stone (entrance_stoop). |
| Stoop rails ending in mid-air | **resolved** | Bottom newels sit on the bottom step or pavement; top posts stand on the landing at the wall (entrance_stoop crop). |
| Black void between lowest gable step and roof | **resolved** | The roof plate meets the gable inner faces at both ends (architecture_close, roof_chimney, front_corner). The sawtooth shading on the roof is a soft shadow, not a gap (left_side and top crops). |
| Gutters running past the gables | **resolved** | At the front-east corner the gutter ends at a white cornice return at the gable corner (architecture_close crop). Only a P2 dark end-cap shows in straight-on views (F16). |
| No white east eave cornice | **resolved** | A white eave board runs under the gutter along the east eave (architecture_close, front). |
| Wrong east window schedule | **partly resolved; still P1** | The count and types are now right, but the small upper windows are positioned in the front third, not over the first tall ground window (F4). |
| entrance_stoop and stepped_gable cameras cropping their subjects | **resolved** | Both subjects are fully framed. glass_close now has the same kind of fault (F7). |
