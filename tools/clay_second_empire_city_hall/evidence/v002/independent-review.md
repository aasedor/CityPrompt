# Independent holistic review: clay-second-empire-city-hall v002 (RLASM v6.1)

Reviewer: independent; did not build this candidate. I opened all 18 renders at full resolution, all 4 phone boards, and the 3 locked sources (front.png, oblique.jpg, top.jpg). I cropped and enlarged junctions, the porch, the tower and the court to inspect them. Metadata, hashes and builder notes were not used as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: Most v001 defects are fixed (rhythm, pavilion mansards, dormers, porch pediment, tower plane). However, black voids remain at every mansard junction, the court walls carry pure-black bands, the stair and porch topology departs from the source, the tower cap reads as an onion dome, and the roof plan and roof tone do not match the top source.

Counts: P0 = 0, P1 = 7, P2 = 10

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, rear, cornice_contact, front_corner, pavilion_mansard, roof_court | Pure-black triangular voids where each wing mansard meets a corner-pavilion mansard, and black vertical slots on both sides of the tower where the wing mansard meets the tower shaft. In front.png there are four voids, at roughly x 500, 660, 800 and 950, y 450-515. In cornice_contact the void runs about 90 x 300 px. Smaller black slivers also sit at the mansard foot and the cornice mitres on every pavilion corner (pavilion_mansard ~680,760; roof_court ~415,905 / 545,1025). The v001 finding is **not resolved**. | The wing mansard is a straight extrusion that stops at the pavilion bounding box, not at the pavilion's raked slope. Its end cap is missing or back-facing, so the void behind it renders black. The cornice mitre blocks leave gaps at the corners. | Extend each wing mansard and its upper roof into the pavilion and tower volumes (or boolean-trim them against the raked faces) so the slopes intersect with no gap. Cap all open ends. Close the cornice and mansard-foot mitres with a corner block. Re-check every junction in front, rear, cornice_contact and pavilion_mansard. |
| 2 | P1 | rear_court, aerial, rear_side | Two continuous bands run around the whole inner court at storey lines. The upper band is pure black (0,0,0), about 14 px thick. The lower band is a thin black line under a ledge. The court wall planes visibly step from storey to storey, so the court reads as stacked, misaligned boxes with a void between them. | The court-face shells for each storey (or the court-side cornice) are offset from one another, which leaves a see-through gap into an unlit cavity. | Make each court face one coplanar wall from court floor to coping, or close the offset with a solid string course that meets both planes. Verify there are no 0,0,0 pixels on court walls in rear_court. |
| 3 | P1 | front, porch_stair, facade_close, front_corner | The stair climbs a full storey, about 25 risers from grade, directly onto the piano-nobile porch. The porch has a single tier of four columns and no front balustrade. The "rusticated arcade" has shrunk to two blind arches on the side and front of the porch base, beside the stair, and the stair hides the rest. The source (front, oblique) shows a short, broad flight up to a **ground-floor columned arcade or porch**, with a second columned loggia above at the piano nobile behind a front balustrade, all under the pediment. | The v001 stair-head clash was fixed by raising the stair to the piano nobile rather than restoring the two-tier porch. | Rebuild the porch in two tiers. Make the lower tier a rusticated arcade or columned porch at raised-ground level, reached by a short broad flight (about 1.2-1.5 m rise) with stone cheeks. Make the upper tier a four-column loggia at the piano nobile with a balustrade across its front, under the pediment. Keep the stair cheeks clear of the arcade arches. |
| 4 | P1 | front, clock_tower, left_side, right_side, roof_court | The tower cap is a bulbous onion. It is pinched in at the base, swells past the clock stage, then necks in to a concave waist under the lantern, which reads Russian or Byzantine. The source cap is a convex, ribbed mansard dome with oculus dormers that rises from the clock-stage cornice and is widest at its base. The stage below the clock is a tall, plain vertical stone shaft with one arched window and a small square window. The source has a slate-clad, tapering stage with a pedimented arched window, corner urns and scrolls. The clock stage is short relative to the shaft, while in the source it is the dominant stage. | The cap profile curve has an inflection that is too strong and a re-entrant base. The tower's lower stage was built as a plain box. | Redraw the cap profile so it is widest at the cornice, convex, with only a slight concave flare at the lantern neck and no base tuck. Add an oculus dormer per face. Clad the lower tower stage in slate with a battered taper, a pedimented arched opening and corner urns. Rebalance the stage heights so the clock stage is at least as tall as the stage below it. |
| 5 | P1 | top, aerial, front_corner, rear_side, left_side | In plan, the roof is a low-pitched ring around a large central court of about 35% x 33% of the roof footprint, so the court is a dominant hole in every aerial view. The top source shows large hipped roof masses with clear ridges and only a small court slot (about 27% x 15%) behind the tower. In elevation (left_side, right_side, rear) the upper roofs read almost flat above the mansards. The v001 "flat upper roof" finding is only partly resolved. | The court footprint is oversized and centred, and the upper-hip pitch is low. | Reduce the court to a narrow slot sized and placed as in top.jpg, and widen the wing depths to suit. Steepen the upper hips so the ridges read from oblique and side views. |
| 6 | P1 | aerial, top, front_corner, rear_side, roof_court | Roof tone does not match the source hierarchy. The upper roof field samples at about (139,147,151), lighter than the buff wall field at about (133,131,124), and reads as pale lilac-grey from every aerial view. The source roofs are a dark zinc and slate grey-green (top source about 87,88,90), clearly darker than the walls. Only the mansard slopes (about 114,121,129) have been darkened. The v001 "roofs as light as the walls" finding is **not resolved** for the upper roofs. | The upper-roof material uses a light zinc base colour. | Darken the upper roof and tower-cap material to the source's dark grey-green zinc (value about 0.30-0.35), below the wall value, and keep the mansard slate slightly darker still. |
| 7 | P1 | left_side, architecture_close, front_corner, top, front | The west-street trees stand at the inner edge of the sidewalk. Their canopies are about 2 m from the wall and overlap the ground-floor and piano-nobile windows (left_side ~545/835; architecture_close ~120-320). The source puts street trees at the curb edge, well clear of the facade. The v001 "trees against the facade" finding is resolved for the forecourt lawn trees but **not** for the west side. | The tree instance offsets are measured from the wall line, not from the curb. | Move the side-street trees to the curb line, with canopies at least 4 m from the facade, or remove them. |
| 8 | P2 | facade_close, porch_stair, front | Ground-floor arch heads and porch arches are visibly faceted (few segments). One porch-arch reveal has a flat wedge kink. | Low arc segment count. | Use 16 or more segments on arch heads and soffits. |
| 9 | P2 | glass_close, facade_close, cornice_contact | Small black specks at the corners of every window frame. | Frame mitre gaps. | Close the frame corners. |
| 10 | P2 | facade_close, porch_stair | The ground-floor rustication is only faint horizontal lines and barely reads. | Shallow channel depth. | Deepen the channels and add vertical joints. |
| 11 | P2 | front vs source front | The source's low basement windows at sidewalk level are absent. | Not modelled. | Add the basement openings if the plinth height allows. |
| 12 | P2 | top, aerial vs top source | The corner-pavilion tops are flat with cresting. The source shows low pyramidal caps. | Simplified cap. | Add low pyramids inside the cresting. |
| 13 | P2 | clock_tower, left_side | The clock-stage corner pilasters are a saturated mint and look detached at the corners. | Material saturation; a corner gap. | Desaturate toward verdigris and join the corner pilasters. |
| 14 | P2 | front, facade_close | The wall field (buff) and the dressings (off-white) differ only slightly. The source has stronger contrast between the brick field and grey stone. | Close material values. | Increase the field-to-dressing value contrast. |
| 15 | P2 | front_corner, aerial vs oblique | Hedges in the forecourt lawns are missing. | Not modelled. | Add hedge masses along the fence and porch. |
| 16 | P2 | pavilion_mansard, roof_court | Chimneys are oversized and bright white compared with the source. | Scale. | Reduce them and match the stone or roof tone. |
| 17 | P2 | interior | The interior is generic (table, chair, blocks) but valid. | n/a | Optional: add civic furnishing. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Silhouette | Deviates. The street elevation matches well (corner pavilions, central tower, porch). The aerial and top silhouette differs: a ring roof around an oversized court instead of hipped masses with a small slot; an onion tower cap. | front, front_corner, aerial, top |
| Storey count | Conforms. Rusticated ground, piano nobile, second storey and mansard; the basement level is absent (P2). | front, left_side, rear |
| Tower stages and clock faces | Deviates. There are 4 clock faces (front, west, east, rear), a tall arched opening per face and a lantern. However, the cap profile is an onion, the lower stage is plain stone, not a slate-clad taper with urns, and the stage proportions are off. | clock_tower, front, left_side, right_side, rear |
| Porch and stair | Deviates. There are four columns and a pediment (fixed since v001). However, it is a single tier at the piano nobile reached by a full-storey stair; the source has a two-tier porch with a short flight to the ground-floor arcade and a balustraded loggia above. | porch_stair, facade_close, front |
| Pavilions and mansards | Conforms. The corner pavilions are 2 bays with clearly taller square mansards, one large arched dormer per face and cresting. Junction voids are logged separately (finding 1). | front, architecture_close, pavilion_mansard |
| Dormer rhythm | Conforms. 3 dormers per front wing bay group, regular rhythm on the sides and rear, with light stone cheeks. | front, cornice_contact, left_side, rear |
| Window rhythm and hoods | Conforms. Bay rhythm is 2/3/3/3/2 on the front; pedimented piano-nobile windows with one continuous iron-railed balcony per pavilion face; hooded second-storey windows. | front, architecture_close, facade_close |
| Cornice and rustication | Partly conforms. The bracketed modillion cornice is present. Rustication is weak (P2). Cornice mitre slivers are part of finding 1. | cornice_contact, facade_close |
| Fence and forecourt | Conforms. Iron fence with stone piers and twin lawns either side of the stair. Hedges are missing (P2). | front_corner, porch_stair, top |
| Materials hierarchy | Deviates. Walls versus dressings now read (fixed since v001), and the mansard slate is darker than the walls. The upper roofs and tower cap, however, are lighter than the walls, which inverts the source's dark zinc roofscape. | aerial, top, front |
| North and east faces (not in any source) | Coherent with the visible grammar (same bays, balconies and dormers). | rear, right_side, rear_side |

## 4. Camera validity

All 18 views are valid. Each target is legible, unclipped and unoccluded.
- rear_court is now inside the court, so the v001 camera defect is fixed. It exposes finding 2.
- front: the forecourt trees partly overlap the pavilion ground floor in projection, but they stand in the lawn; this is acceptable.
- interior: valid; it shows a room with a tall window and an exterior view through the glass.
- top: true nadir; the whole lot is in frame.

## 5. Previous-version (v001) findings: are they resolved in the pixels?

| v001 finding | v002 status | evidence |
|---|---|---|
| Black seams at every pavilion junction | **Not resolved.** | Black voids at every wing/pavilion and wing/tower mansard junction (front, rear, cornice_contact), plus mitre slivers at the corners. |
| Black dormer cheeks | Resolved. | Dormer cheeks render as light stone (cornice_contact, pavilion_mansard). |
| Black pediment shells | Resolved. | Window and porch pediments are light (architecture_close, porch_stair). |
| Porch without a pediment | Resolved. | Full pediment over four columns (front, porch_stair). |
| Balustrade across the stair head; stair cheek through an arcade arch | Resolved as stated: no balustrade across the stair head, and the cheek clears the arches. | However, the fix introduced a new topology deviation from the source (finding 3). |
| Tower set back behind the pavilion mansard | Resolved. | The tower rises from the central pavilion face above the porch (front_corner, roof_court, front). |
| Squat tower cap and plain clock stage | Partly resolved. | The cap is taller and the clock stage now has pilasters and pediments. The cap has become an onion profile and the lower stage is plain (finding 4). |
| Pavilion mansards barely taller than the wings, two small dormers | Resolved. | The pavilion mansards are clearly taller than the wing mansards, with one large dormer per face (front, architecture_close). |
| Flat upper roof | Partly resolved. | The upper roofs are now hipped, but low-pitched; they read near-flat in elevation, and the court is oversized (finding 5). |
| Bay rhythm 3/2/4/2/3 with per-window balconettes | Resolved. | 2/3/3/3/2, with one continuous balcony per pavilion face (front, architecture_close). |
| One wall tone; roofs as light as the walls | Wall tone resolved. Roofs **not resolved**. | Buff field with off-white dressings. The upper-roof field is still lighter than the walls (finding 6). |
| Trees against the facade | Partly resolved. | The forecourt trees are now in the lawns. The west-side trees still crowd the facade (finding 7). |
| rear_court camera on the outer face | Resolved. | The camera is inside the court. The court shows black bands (finding 2). |
