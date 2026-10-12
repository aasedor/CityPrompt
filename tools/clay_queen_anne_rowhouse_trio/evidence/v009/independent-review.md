# Independent holistic review: clay-queen-anne-rowhouse-trio v009 (RLASM v6.1)

Reviewer: independent. Inputs read: sources/front.png, sources/oblique.jpg, sources/top.jpg, all 18 renders at full resolution (1440x1080), and the 4 phone boards. No code, build reports or builder notes were read. Pixel coordinates below are native render pixels (x, y).

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: three of the four v008 P1s are fixed in the pixels, but the black voids at the corners of every window and door reveal are still there. A spurious slate pent band also hangs below the main front eave and reads as a second eave that neither source shows.

Counts: P0 = 0, P1 = 2, P2 = 8

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | facade_close: upper sash corners (238-245,59-66), (385-392,64-70), (238-245,330-337), (385-392,331-337); green door frame top corners (518-525,557-563), (649-656,557-563). glass_close: sash corners (428,230), (905,238), (436,915), (898,888). interior: frame corners (560,60), (975,50), (565,630), (970,630) | At every window and door frame corner there is a square void of about 4x4 px with luminance 0-5 (pure black), sitting between the frame and the cream surround. It shows in every close-up and on the phone board. The v008 corner-void defect is still there. | The brown frame members and the reveal liners still do not close the corner. The visible black is the unlit cavity behind the frame where the jamb and head members meet with a gap, or where they are mitred short of the liner. Making the liners proud did not cover the frame-to-liner corner. | Extend the jamb members of every frame (sash box and door frame) by the full head and sill thickness, so the jamb overlaps the head and sill. Alternatively, add a solid back plate or reveal-return box behind each frame that fills the opening perimeter. Re-render facade_close and glass_close and confirm that no pixel under luminance 15 remains at the frame corners. |
| 2 | P1 | front: dark slate slabs at (555-632, 492-515) and (808-957, 492-515), plus similar slabs flanking each end gable at (270-345, 492-515) and (1010-1035, 492-515). front_corner: grey band under the eave along the middle unit (790-950, 590-620). aerial: band under the gutter (540-700, 555-650). facade_close: top edge (260-700, 0-25) | A second, lower slate skirt or pent hangs below the main eave gutter (light grey and green) across the middle unit and beside the upper bays. It sits in front of the brick head course just above the first-floor window heads, so the facade reads as having a double eave. Both locked sources show a single green gutter on the brick, with window heads directly below (front.png 480-560, 280-300; oblique.jpg 560-650, 430-460). | The new "slate hip skirt" geometry, or the main-roof eave skirt, is placed or extruded along the eave line instead of only between the ground bay cap and the upper canted bay. Alternatively, an old pent piece was not removed when the bays were rebuilt. | Delete the under-eave slate slabs along the main front eave, so the eave ends at the green gutter over the brick. Keep slate between floors only at the ground-bay hip caps. Re-render front and front_corner and confirm there is a single eave line between the gables. |
| 3 | P2 | gable_close, architecture_close, roof_contact (all bargeboards) | The bargeboards are plain square beams. The source gables have pierced fretwork bargeboards with drops. The identity still reads. | Simplified clay member | Optionally add a scalloped or pierced profile to the inner edge of each bargeboard. |
| 4 | P2 | front (700-735, 385-460); architecture_close (0-160, 620-1010) | The middle brick gable has a glazed arched sash. The source shows a blind arched recess (front.png 405-440, 220-290). | Window reused from the end gables | Replace it with a shallow blind arch in brick and cream. |
| 5 | P2 | party_wall (310-1440, 0-370); left_side (455-985, 290-515) | The west party-wall gable triangle above the eave line is a smooth, darker field with no brick coursing. The wall below it is coursed, so there is a visible material seam along the eave line. | A different material or UV on the gable triangle | Apply the coursed brick material to the gable triangle. |
| 6 | P2 | front_corner (720-1130, 680-910); aerial (400-760, 640-900); top (390-1050, 765-910) | The front gardens are bare brown soil with one hedge bar and one small shrub each. The source gardens are densely planted with clipped hedges and shrubs. | Minimal planting in clay | Add 2-3 more shrub masses and a hedge return per garden. |
| 7 | P2 | entrance_steps (0-1440, 900-1080); front (205-1235, 785-845) | The railings stand on a thin kerb at grade. The source shows the fence on a low stone wall or plinth (front.png 0-810, 660-700). | Wall height near zero | Raise a 0.3-0.4 m cream or stone plinth wall under the fence line. |
| 8 | P2 | facade_close (518-656, 555-630); entrance_steps (1175-1300, 200-300) | Each door transom is an opaque door-colour panel with dark grey slots at its sides. It does not read as glazing. | Transom glass sits behind the door leaf | Make the transom a glazed light within the frame, in front of the leaf. |
| 9 | P2 | aerial (90-240, 185-260) and (590-760, 500-590); front (355-555, 478-500), (965-1165, 478-500) | Under each end gable there is a flat light-grey ledge sandwiched between two green bands. This reads as a thick lead shelf where the source shows a single green fascia at the gable base. | Upper-bay roof cap plus gable sill stacked | Reduce the stack to a single green fascia. |
| 10 | P2 | rear (230-1230, 210-500); rear_yards | The rear cross gables are blank brick triangles. The source top view shows only the roofs, so this is a coherence-only note: the rear is plausible but plain. | No rear gable openings | Optionally add one small attic sash per rear gable. |

(There are 8 P2 rows, #3-#10.)

## 3. Source conformance checklist

| item | status | view used / note |
|---|---|---|
| Silhouette | conforms | front vs front.png; front_corner vs oblique.jpg: three steep gables rising to or above a slate main ridge, with chimneys at the ridge. |
| Storey count | conforms | front, right_side: two storeys plus attic in the gables, matching front.png. |
| Unit rhythm and doors | conforms (with the recorded source conflict) | front: the sequence is door / W bay / door / two windows / door (green) / E bay. The source sequence is W bay / door / two windows / green door / E bay. The third door, west of the W bay, is a coherent completion of the three-unit cut. Each door has its own stoop with railings (front_corner, entrance_steps). |
| Bays and gables | conforms | bay_window, facade_close, front_corner: a canted ground bay under a slate hip cap, a narrower set-back canted upper bay with angled flank sashes, and a steep bargeboarded gable with cream (W) or green (E) infill and finials. |
| Dormer and roof | deviates (P1 #2, P2 #4) | front, front_corner, aerial: the middle gabled dormer is present with green bargeboard. The main roof has a spurious second slate skirt below the eave. The dormer is glazed where the source shows a blind arch. |
| Chimneys | conforms | front, rear, roof_contact: brick stacks with cream caps and pots at the ridge and at the end walls. |
| Fence and gardens | deviates (P2 #6, #7) | front_corner, entrance_steps: the iron railings and hedges are present. The low wall is near zero height and the planting is sparse. |
| Rear | conforms (coherence only) | rear, rear_side, rear_yards, top: three rear cross gables, rear doors and windows, and walled yards per unit. |
| East elevation | conforms | right_side vs front.png and oblique.jpg: two attic sashes, one first-floor window, two ground windows, cream bands and front-corner quoins. |
| West party wall | conforms (coherence) | left_side, party_wall: blank brick gable carrying a stack. There is a minor coursing seam (P2 #5). |
| Materials hierarchy | conforms | All views: red-brown coursed brick, cream stone bands, surrounds and quoins, blue-grey slate, green timber infill and trims, dark iron. |

## 4. Camera validity

All 18 views are valid. The target is legible in each, with no occlusion of the subject and no clipping of the asset. interior is deliberately framed from inside and reads as a bay room with three sashes. party_wall is a close oblique of the blank west wall, as intended. No view is invalid.

## 5. Previous-version (v008) findings, resolution in v009 pixels

| v008 finding | v009 status | evidence |
|---|---|---|
| P1: the storey above each end bay was a flat pilastered wall instead of a set-back canted upper bay with angled flank sashes under the gable | **Resolved** | front_corner: the W upper bay has an angled flank sash at about (680-700, 660-740) on a canted face. facade_close: the E upper bay's left flank (720-850, 40-390) is angled, with a narrow sash and slanting coursing. The upper bay sits back from and narrower than the ground bay, with the slate hip cap between the floors (bay_window 250-1225, 40-250). |
| P1: dark gap inside both rakes of both end gables, between the bargeboard and the infill | **Resolved** | gable_close (360-1040, 170-1080) and roof_contact (580-1000, 500-1080): the bargeboards are solid cream beams that meet the infill along their whole length, with no dark seam. The middle green bargeboards are also continuous (architecture_close). |
| P1: black voids at the corners of every window and door reveal | **Not resolved** | See finding #1: corner pixels at luminance 0-5 in facade_close, glass_close and interior. |
| P1: blank east gable with one window column instead of two attic sashes, a first-floor window and two ground windows | **Resolved** | right_side: two attic sashes (650-790, 385-470), one first-floor window (790-845, 530-630) and two ground windows (535-595 and 785-850, 690-790), with cream bands and a raking cream bargeboard. |
