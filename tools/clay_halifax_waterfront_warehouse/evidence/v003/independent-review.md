# Independent holistic review: clay-halifax-waterfront-warehouse v003 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only on rendered pixels against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders at full resolution, plus the 4 phone boards, and checked suspect regions in zoomed crops in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/hfxwh-v003-indep-crops-5e2b01c2/`. I did not use builder metadata, counts or notes as evidence.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**. The four v002 defects are fixed in the pixels and the identity is strong. However, a new pure-black open cavity shows at the back of the south-west cornice end, and the v002 slit fix made the west neighbour deeper than the warehouse, which contradicts the governing top source. The large south arch also shows a rectangular carrier-cut recess at its shoulders.

Counts: P0 = 0, P1 = 3, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | left_side (whole-envelope); crop `left_sw.png` | The south-front copper cornice runs past the warehouse's west wall above the lower neighbour. On its north/back side, the cornice end shows two pure-black (0,0,0) horizontal slots between the corona, frieze and bracket layers, about 315 px of pure black at x 1251-1286, y 416-438. A bracket stub hangs below in the void. This is the same class of open, black cornice end that v002 recorded at the north-east, now at the south-west. | The cornice is built from separate stacked slabs with no back or end closure, and the frieze break-forward does not wrap the west end. The interior faces or back faces render as unlit holes. | Close the west end of the south cornice: add an end cap or return on the corona, frieze and soffit (same treatment as the new north-east return). Alternatively, stop the cornice flush at the west wall and return it 0.3-0.5 m onto the west face above the neighbour roof. Re-render left_side and confirm zero pure-black pixels at the south-west corner. |
| 2 | P1 | top, rear, rear_side, left_side vs sources/top.jpg; crops `top_nw.png`, `rear_nw.png`, `rearside_nw.png`, `src_top_west.png` | In the render, the west neighbour is a plain box that runs deeper (further north) than the warehouse, and its east face is exposed beyond the warehouse's north wall. In the locked top view, the neighbour's main block stops about 28% of the warehouse depth short of the warehouse's north parapet. Behind it are a lower annex and an alley, so the warehouse's west parapet stands free for its northern third. The plan relationship that the top view governs is reversed. | The v002 neighbour slit was "fixed" by extending the neighbour past the warehouse's north wall instead of closing the contact. | Restore the neighbour's depth to the top-view proportion (about 0.72 of warehouse depth, optionally with the lower annex). Make it contact the warehouse's west wall flush, with no gap (wall faces coplanar or overlapped inside the party wall). Finish the exposed northern west wall of the warehouse as brick, with its parapet and copper coping running the full depth. |
| 3 | P1 | arched_windows, facade_close; crops `aw_shoulder_r.png`, `fc_bigarch.png` | At both shoulders of the large round-arched window in the middle south bay, a rectangular recessed notch (dark edge line and shadow) sits in the brick outside the archivolt. The rectangular opening cut extends beyond the arched head, so a box corner reads behind the arch. The smaller arches do not show it. | The large arch's wall aperture (carrier cut) is a rectangle sized to the full arch height and width. The archivolt does not cover its top corners. | Cut the large-arch aperture to the arched profile (or a rectangle no larger than the archivolt outline). Alternatively, fill the shoulder corners with brick flush to the wall plane. Re-render arched_windows and facade_close. |
| 4 | P2 | top, left_side | The west parapet coping is brick-coloured. The locked top view shows the copper coping ring on all four parapets. | The coping strip was omitted on the party-wall parapet. | Add copper coping to the west parapet. |
| 5 | P2 | facade_close vs front source | The ground shopfront of the west (triplet) bay shows 2 large lights. The source suggests 3 narrower lights under the triplet. | Simplified mullion count. | Split it into 3 lights aligned under the triplet. |
| 6 | P2 | arched_windows, east_side, right_side | The archivolts have no impost or springer blocks at the springing (the source has them). Arches and archivolts are visibly faceted (about 8 segments) in the close views. | Low arc tessellation; impost blocks not modelled. | Raise arc segments to 16 or more and add small granite impost blocks. |
| 7 | P2 | rear, rear_side, left_side | The neighbour's north and east faces are blank, with no windows and no cornice line. They read as a placeholder block. | Context massing kept minimal. | Add simple window recesses and a cornice band (or keep these faces out of the hero cameras). |
| 8 | P2 | rear, rear_side, left_side; crops `rear_ne.png`, `rearside_ne.png` | The north-east returns of the cornice, belt and plinth are closed (no black). They read as stacked stub slabs that stop abruptly 1.4 m along the north wall. | The return is modelled as separate offset boxes. | Bevel or step the return end faces, or end it at a pilaster strip. |
| 9 | P2 | rear_north; crop `rn_chimney.png` | There is a 1-2 px pure-black line under each chimney where it overhangs the north wall face. | Unlit underside or back face of the chimney overhang. | Close the chimney underside or seat the chimney flush. |
| 10 | P2 | rear_north, rear | The north wall is a flat brick colour without the coursing lines used on the south and east faces. | A different material was assigned to the rear wall. | Use the coursed brick material. |
| 11 | P2 | top, aerial, front_corner | The roof membrane is light neutral grey. The source roof is a darker brown-grey membrane. | Palette choice. | Shift the roof colour toward the source membrane tone. |
| 12 | P2 | east_side, right_side | A street tree covers part of east bay 3 (upper right window and pier). | Camera and tree placement. | Nudge the camera or tree for these detail views. |
| 13 | P2 | aerial; crop `aerial_ne.png` | Seen from above, the corona plates at the north-east corner overlap with a small stepped notch. | Overlapping break-forward plates. | Mitre or merge the corner corona plates. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial vs front/oblique | Flat-roofed two-storey block with a deep projecting cornice, a parapet with raised blocks and a central raised panel. |
| Storey count and proportions | conforms | front, right_side, facade_close | Two storeys, with a tall shopfront ground storey and an arched upper storey. Plan ratio ≈1.39 vs source ≈1.44 (top). |
| Piers (rustication, caps) | conforms | granite_piers, architecture_close, facade_close | Horizontal channel rustication, cap blocks under paired copper consoles, and the corner pier wrapping both faces. |
| Brick bays | conforms | facade_close, east_side | Red brick (coursed) between piers on the south and east. |
| Shopfronts and entrance | conforms (P2 #5) | facade_close, glass_close, interior, front | Dark-green frames with transoms, bulkheads, and a double door with sidelights in the middle south bay. Openings have depth (interior visible). |
| Belt entablature | conforms | facade_close, east_side, granite_piers | A continuous granite belt wraps the corner. |
| Arched windows (counts per bay, archivolts, keystones, sills) | conforms with defect (P1 #3, P2 #6) | front, facade_close, arched_windows, right_side, east_side | South: triplet / single large arch / pair. East: a pair per bay in all 3 bays. Granite archivolts with keystones, sills on a band, and reveal depth visible. The large arch has a box-corner leak (P1 #3). |
| Copper cornice and brackets | deviates (P1 #1) | front, architecture_close, copper_cornice, right_side, left_side | Deep verdigris corona with modillions and paired consoles over piers; the frieze breaks forward over the pier caps. The south-west end is open and black from behind. |
| Parapet, raised blocks and coping | conforms with defect (P2 #4) | copper_cornice, roof_chimneys, right_side, front_corner | Raised blocks over the piers, a raised panel over the middle south bay, and copper coping on the south, east and north. The west coping is brick. |
| East ground windows | conforms | right_side, east_side, front | A glazed corner shop in east bay 1, and arched windows in brick with granite archivolts in bays 2 and 3. |
| Roof and chimneys | conforms (P2 #11) | top, roof_chimneys, aerial | Flat membrane, 2 brick chimneys on the north parapet at positions close to the top source, plus small vents. |
| Sidewalks, trees and lamp | conforms | front_corner, aerial, top, right_side | Sidewalks on the south and east, a corner kerb radius, a crosswalk, trees on both streets, and lamps. |
| Neighbour | deviates (P1 #2, P2 #7) | top, rear, rear_side, left_side, front | Brick neighbour attached on the west and lower than the warehouse (matches front/oblique). Its depth contradicts the top view. |
| Materials hierarchy | conforms (P2 #10) | all | Granite piers and belt > red brick infill > verdigris copper top > dark-green joinery. Clay palette is consistent with the sources. |

## 4. Camera validity

- All 18 views are legible and none has the target fully occluded or clipped.
- front: the north-east end of the east façade sits at the right frame edge with a tree. It is acceptable (the source front crops the same way).
- left_side: because the west face is a party wall, this camera shows mainly the north wall and roof from the north-west. It is valid, and it is the only view that exposes the P1 #1 cavity.
- east_side and right_side: a tree partly covers east bay 3 (P2 #12). It does not invalidate either view.
- interior: legible. The shopfront openings read with depth.

## 5. Previous-version (v002) findings: resolved in pixels?

| v002 finding | Status in v003 pixels | Evidence |
|---|---|---|
| Two upper arched windows of east bay 1 overlapping their archivolts, with a black void between | **Resolved** | right_side, east_side, front, architecture_close (crops `right_bay1.png`, `front_eastbay1.png`, `archclose_eastbay1.png`). The two archivolts are separate, with a brick gap between them, clear of the corner pier and next pier, and there is no black. |
| Black slot between the south-east corner pier cap and the copper frieze and cornice soffit | **Resolved** | architecture_close, front (crops `archclose_corner.png`, `front_corner_cornice.png`). The frieze breaks forward over both faces of the corner pier cap. The pocket is filled in copper, with no pure-black pixels. |
| East copper cornice ending open and black at the north end; black slots where belt and plinth meet the north wall | **Resolved at the north-east corner** | rear, rear_side, left_side, right_side (crops `rear_ne.png`, `rearside_ne.png`, `left_ne.png`, `right_ne.png`). The cornice, belt and plinth return closed along the north wall with no black. However, the same defect class now appears at the **south-west** cornice end (new P1 #1). |
| Full-height black slit between the north wall and the attached neighbour | **Resolved as a slit, but replaced by a plan deviation** | rear, rear_side (crops `rear_nw.png`, `rearside_nw.png`). There is no black slit: the neighbour's east face is lit brick. The fix extends the neighbour past the warehouse's north wall, contradicting the top source (new P1 #2). |
