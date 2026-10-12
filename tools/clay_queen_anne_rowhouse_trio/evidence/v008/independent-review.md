# Independent holistic review — rowhouse v008 (RLASM v6.1 architectural clay)

Reviewer: independent, no relationship to the builder. Judged only the locked sources
(`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`), the 18 renders and the
4 phone boards. No build report, metadata or builder notes were used as evidence. Every
render was opened at full 1440x1080 and suspect regions were inspected at 2-4x nearest-
neighbour magnification; pixel values quoted below were sampled from the render files.

## 1. Verdict

**VISUAL_REWORK_REQUIRED** — the v007 door-rhythm, blind-gable-window and sill-band-void
findings are fixed in the pixels, but the end-gable rake gap is still there (now black
instead of pale), every opening has black corner voids, the first storey over each end bay
is flat where both locked sources show a set-back canted upper bay, and the east elevation
does not carry the openings the locked front and oblique show.

Counts: P0 = 0, P1 = 4, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | `front_corner.png` E unit x 930-1050 y 500-600, W unit x 640-790 y 580-680; `aerial.png` x 700-800 y 640-730; `facade_close.png` x 740-1300 y 0-430; `top.png` x 440-600 and x 890-1050 y 740-800 (only the ground bay projects). Sources: `front.png` x 600-730 y 280-400 (E) and x 200-300 y 300-440 (W); `oblique.jpg` x 700-840 y 420-600 | The storey above each end bay is a flat wall carrying [narrow window][cream pilaster][wide window][pilaster][narrow window] all in one plane; the slate hip cap closes the ground bay against that flat wall and the gable sits on the flat wall. Both locked sources show the upper storey as a set-back **canted** bay: the narrow flank windows are at an angle with deep returns, the slate cap is a hip skirt between the wider ground bay and the narrower upper bay, and the gable sits on the upper bay. In oblique views the render reads as bay-then-flat-wall, not the two-storey canted stack | Upper-storey bay carrier built as a flat pilastered panel instead of a three-face canted volume | Build the first-floor volume over each end bay as a canted prism (centre face + two 45° flanks) set back ~0.3 m from the ground bay faces; turn the slate cap into a hip skirt from the ground-bay outer faces up to the upper-bay faces; mount the narrow flank sashes in the canted flanks; seat the gable on the upper-bay centre face |
| 2 | P1 | `gable_close.png` left rake x 420-700 (10-14 px wide, RGB ≈ 20-30), right rake x 760-1050 thinner; `roof_contact.png` right rake x 790-870 y 600-1000 (tapered, widest at foot), left rake x 600-700; `front_corner.png` x 750-765 y 495-580; `aerial.png` x 465-475 y 450-500; `front.png` W gable x 375-525 y 275-490 and E gable x 975-1135 y 275-490 (1-2 px dark line inside both rakes) | A near-black strip runs inside both rakes of both end front gables, between the inner edge of the cream bargeboard and the infill. It has a hard edge, constant or growing width toward the foot, and is darker than any cast shadow elsewhere in the clay (deepest sill shadows ≈ 60-80). It is a through-gap showing the gable's unlit interior, not a recess shadow. The middle (green/brick) gable has no such strip | Gable infill triangle is cut to the bargeboard's inner line (or slightly inside it) instead of overlapping behind the bargeboard; v007's pale strip was the same gap seen lit | Extend each end-gable infill triangle outward by at least the bargeboard width so it lies behind the board, or give the bargeboard an inward return that overlaps the infill; re-render `gable_close` and `roof_contact` and confirm zero pixels < RGB 40 along either rake |
| 3 | P1 | `glass_close.png` corners x 400-440 y 200-240 (250 black px), x 890-935 y 205-245 (221), x 400-445 y 920-960 (198), x 885-930 y 870-915 (181); `facade_close.png` every window head/sill corner; `entrance_steps.png` door-frame heads at (1145,135) and (1345,170) and every window corner; `bay_window.png` bay sash corners (440,310), (725,300), (455,745); `interior.png` x 555-575 and x 965-985 y 45-70, and sill corners y 630-640; `front.png` ~244 near-black pixels at opening corners across x 250-1200 y 500-830 (visible as dots at normal size) | Every window and door opening has two black patches at each corner: one square at the outer corner of the cream surround/reveal and one rectangle at the inner corner between frame and reveal. Seen from inside (`interior`) the same corners are black, so these are through-voids where the reveal, surround and frame members meet, not shadows | Reveal/surround/frame built as separate butt-jointed bars that stop short of each other at the corners, leaving an open notch into the wall cavity | Mitre or overlap the four reveal bars and the four frame bars at each corner (or cut the opening as a single boolean and line it with one continuous reveal loop); verify `glass_close` corners have no pixel < RGB 60 |
| 4 | P1 | `right_side.png` gable x 480-960 y 280-510 (blank), windows only at x 790-850 y 530-630 and y 690-800; `front_corner.png` x 820-1010 y 560-880; `aerial.png` x 820-1010 y 540-860. Sources: `front.png` x 870-960 y 170-290 (two attic windows in the east gable), x 920-950 y 330-420 (first floor), x 830-845 and x 920-945 y 480-600 (two ground windows); `oblique.jpg` x 1005-1030 y 320-360 (attic window), x 1000-1030 y 440-520 and y 620-700 | The east elevation is a locked, fully visible face. Both sources show at least one tall attic window in the east gable (front source shows two), a first-floor window and two ground-floor windows in two columns. The render's east gable is blank and only one column of two windows (first floor + ground) exists | East-face opening programme authored from the generic side-wall rule rather than the two source views | Add two attic sashes in the east gable (source proportions: tall, narrow, cream head and sill), keep the existing first-floor window, and add the second ground-floor window near the front (SE) corner; keep bands and quoins |
| 5 | P2 | `front.png` middle gable x 650-790 vs end gables x 370-530 / x 970-1130; source `front.png` middle x 360-480 vs E x 540-760 | Middle brick/green dormer gable is 0.87x the end-gable width; sources show ≈0.7x (a noticeably smaller dormer) | Dormer width parameter | Narrow the middle gable base by ~20 % and keep its apex slightly below the end-gable apices |
| 6 | P2 | `front.png` faint vertical lines on the slate at x ≈ 565, 652, 833, 934; `rear.png` x ≈ 440-1000; `top.png` x 540, 650, 790, 900; `architecture_close.png` diagonal seam (470,290)-(980,1000); `roof_contact.png` x ≈ 240-330, 900, 1190 | Per-unit roof slabs show as shading seams on what should be one continuous slate slope | Roof built as abutting per-unit slabs with normals not merged | Merge the main roof slopes into one mesh per slope or weld normals across the slab joints |
| 7 | P2 | `architecture_close.png` x 720-740 y 332-345 | Small vertical step where the east gable's west slope starts above the main roof plane at the ridge, leaving a ledge | Gable roof plane offset a few cm above the main plane | Drop the gable roof plane to the main-roof plane at the ridge line |
| 8 | P2 | `left_side.png` x 455-985 boundary at y ≈ 500; `party_wall.png` sloping boundary (300,390)-(1440,250) | Brick coursing lines stop at eave height; the gable triangle above is smooth — the party wall reads as two panels of one colour | Coursing applied to the storey wall but not to the gable extension | Apply the same coursing to the gable triangle of the party wall |
| 9 | P2 | `front.png` W parapet x 265-330 y 260-490 (red, uncapped) vs E parapet x 1130-1180 (cream coping); `top.png` x 380-395 (red) vs x 1050-1065 (cream) | The two raised party-wall parapets are finished differently: east has a cream coping, west is bare brick | Coping only applied to the east wall | Either cap both (preferred, matches the east source verge trim) or neither |
| 10 | P2 | `glass_close.png` x 1190-1240 y 860-1000 | Lowest SE quoin block reads as a sheared wedge, unlike the rectangular blocks above it | Lowest quoin clipped by the plinth/band boolean | Give the lowest quoin the same box geometry as the others, finishing on the plinth |
| 11 | P2 | `rear_yards.png` x 650 y 980-1080 and x 1385-1400 y 850-1080 | Black vertical slits where the rear-yard fence panels meet at the party lines | Panels butt without overlap | Overlap or share the post at each junction |

## 3. Source conformance checklist

| Item | Status | View used / evidence |
|---|---|---|
| Silhouette (steep end gables with finials, lower middle gable, slate main roof, chimneys on ridge, bays under hip caps) | **conforms** (dormer slightly oversized, P2 #5) | `front.png` vs `sources/front.png`; `aerial.png` vs `sources/oblique.jpg` |
| Storey count (two storeys plus gable attic) | **conforms** | `front.png`, `front_corner.png` |
| Unit rhythm and doors (E: bay + green door west of bay; M: maroon door at west end, two ground windows, three upper windows; W: bay + door west of bay; one stoop with handrails per door) | **conforms** | `front.png` x 260-560 (W), 560-940 (M), 880-1180 (E); `entrance_steps.png`; `sources/oblique.jpg` x 430-700 |
| Bays and gables (canted ground bay, slate hip cap, narrow flank sashes, cream/green boarded end gables with bargeboards, arched gable window, finial) | **deviates** — upper storey over each bay is flat, not a set-back canted bay (P1 #1); black gap inside the rakes (P1 #2) | `facade_close.png`, `front_corner.png`, `gable_close.png` vs `sources/front.png` x 560-780 y 250-470 and x 190-330 y 290-470 |
| Dormer and roof (small brick gable with green bargeboard and glazed arched sash over the middle unit; slate main roof; gable ridges meet main ridge with converging valleys) | **conforms** (dormer width P2 #5; slab seams P2 #6; ridge ledge P2 #7) | `front.png` x 650-790; `top.png` vs `sources/top.jpg` |
| Chimneys (two stacks on the ridge, one at the W/M party line, one at the east end, two pots each) | **conforms** | `front.png` x 575-605 and x 1080-1110; `top.png`; `sources/front.png` x 300-330, `sources/oblique.jpg` x 320-370 and x 990-1030 |
| Fence and gardens (iron railings on a low plinth, openings at each stoop, hedges, small shrubs) | **conforms** (clay simplification) | `front.png` y 780-850; `entrance_steps.png`; `aerial.png` |
| Rear (three cross gables, two windows per unit upstairs, window + door per unit downstairs, walled yards) | **not visible in sources except roof form** — coherent with the front grammar; rear gable roofs conform to `sources/top.jpg` | `rear.png`, `rear_side.png`, `rear_yards.png`, `top.png` |
| East elevation openings | **deviates** — blank gable, one column of windows (P1 #4) | `right_side.png` vs `sources/front.png` x 820-1000 y 150-660 and `sources/oblique.jpg` x 880-1060 |
| West party wall | **coherent** (blank by recorded source conflict; coursing stops at eave, P2 #8; uncapped vs east, P2 #9) | `left_side.png`, `party_wall.png` |
| Materials hierarchy (red-brown brick field, cream bands/lintels/sills/quoins, cream and green gable boarding, green bargeboard on the middle gable, slate blue-grey roof and bay caps, maroon/green doors, dark iron fence) | **conforms** | `front.png`, `facade_close.png`, `bay_window.png` |
| Openings with depth/returns | **conforms** on reveal depth (interior visible, sash bars, reveals), **deviates** at corners (P1 #3) | `glass_close.png`, `interior.png` |

## 4. Camera validity

All 18 views have the intended target in frame, unclipped and legible: `front`, `front_corner`,
`aerial`, `top`, `left_side`, `right_side`, `rear`, `rear_side` show the whole envelope;
`facade_close`, `architecture_close`, `glass_close`, `entrance_steps`, `bay_window`,
`gable_close`, `roof_contact`, `rear_yards`, `interior`, `party_wall` each show their named
element. `party_wall` is a deliberately blank face and is legible as such. `interior` has a
half-height cream wall occupying the lower 35 % of frame but the window, reveals, fence and
hedge beyond are legible. No view is invalid.

## 5. Previous-version findings, verified in this version's pixels

| v007 finding | Status in v008 pixels | Evidence |
|---|---|---|
| P1 thin pale strip inside both rakes of the two end front gables, splitting from the bargeboard and ending in mid-air | **Not resolved — changed, not removed.** The pale mid-air strip is gone, but a near-black gap strip now runs the full length inside both rakes of both end gables (new P1 #2) | `gable_close.png` x 420-700 (RGB ≈ 20-30, 10-14 px); `roof_contact.png` x 790-870 y 600-1000; `front.png` both end gables |
| P1 middle unit's door centred between two windows (sources: door at west end, two ground windows, three upper windows) | **Resolved.** Maroon door at the west end of the middle unit, two ground windows east of it, three upper windows | `front.png` door x 590-635, ground windows x 680-740 and x 775-840, upper windows x 605-650, 700-745, 800-845; `entrance_steps.png` |
| P1 west unit's door east of its bay (mirrored) | **Resolved.** West unit door now sits west of its bay against the party wall, with the upper window above it | `front.png` door x 285-325 y 690-790, bay x 360-560; `front_corner.png` x 640-680 y 790-860 |
| P1 middle gable's arched window a blind panel with no sash or glass | **Resolved.** The middle gable's arched opening carries a two-light sash with meeting rail and glass showing interior tone | `front.png` x 700-745 y 395-470; `architecture_close.png` x 0-170 y 620-1010 |
| P1 black void where the east bay's sill band met the quoin stack | **Resolved.** The bay's cream base band and the quoin stack meet cleanly on a grey plinth; no pixels below RGB 60 at the junction | `bay_window.png` x 960-1260 y 820-1040; `glass_close.png` x 1170-1260 y 820-1020 |
| v006 slate-below-eave finding | Remains resolved — eave slate terminates in the eave fascia on all gables | `front.png` y 485-500; `rear.png` y 490-520 |
| v005 end-gable, bay-cap and side-apex findings | Remain resolved — end gables carry finials and bargeboards, bay caps are hipped, side apices carry the chimney/finial correctly | `front.png`, `left_side.png`, `right_side.png` |
