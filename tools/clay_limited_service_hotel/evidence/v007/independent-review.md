# Independent holistic review: clay limited-service hotel v007 (RLASM v6.1)

Reviewer: independent (not the builder). Evidence: the three locked sources, the 18 renders and the 4 phone boards, all opened at full resolution. Pixel regions are given as (x0-x1, y0-y1) in the native 1440x1080 render frame unless noted otherwise.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the two-colour band is now correct, but the lobby tower head still stands at or above the main parapet. Its dark roof is flush with, or above, the main roof, and its header cuts through the main block's navy band. The sources show the tower roof stepping down below the main roof, with the main parapet and band running on above and behind it.

Counts: P0 = 0, P1 = 1, P2 = 6

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | parapet_corner (300-1270, 315-610); architecture_close (535-1370, 305-440); front (705-1000, 255-330); lobby_tower (515-1130, 0-190); aerial (630-860, 505-545); top (830-930, 700-800). Sources: oblique (495-790, 340-385), front (395-575, 255-290), top (775-860, 525-600) | **The tower head still reads above the main roof.** In parapet_corner the tower's charcoal roof slab sits higher than the adjacent main parapet cap, and the banded header box stands proud of the parapet line on both sides. The header also replaces the main block's navy band across the whole tower width. In aerial and top the tower roof is a dark charcoal square flush with the main roof. The sources show something different. In the oblique, the tower has its own pale membrane roof set well below the main roof. The main parapet cap and its navy band continue unbroken above and behind it, roughly a band's depth higher. In the front source, both adjacent main parapet caps visibly overtop the tower header. In the top source, the tower roof is a small white panel. The v007 change (header top 0.2 m above the cap) puts the tower roof above the main roof, which is the opposite of the source relationship. | The header box is sized to cap the glazing and was raised to the parapet cap, not set below it. The tower roof uses the charcoal header material, not white membrane. The main parapet and band are not modelled behind the tower. | Lower the header top to about 0.8-1.0 m below the main parapet cap. Put the tower's flat roof at that level, finished in the white roof membrane. Carry the main parapet cap and navy band continuously across the faces behind the tower, so the step-down reads in front, aerial and parapet_corner. Recolour the header from charcoal with navy stripes to the source's warm taupe/bronze, with one or two shallow reveal lines. Re-render parapet_corner, architecture_close, aerial and top to confirm. |
| 2 | P2 | front (310-700, 320-560) vs source front (175-400, 310-460) | The beige leg's south face is a flat field of paired windows. The source groups some window pairs in slightly recessed darker vertical panels. | Facade bays modelled as a single plane | Add shallow (about 0.1 m) recessed charcoal/taupe panels behind selected window pairs |
| 3 | P2 | wing_contact (115-1010, 495-845); front (130-320, 575-650) vs source front (15-140, 455-520) | The breakfast wing's glazing is three large two-pane frames. The source shows a finer ribbon of about 6-8 narrow mullioned bays. | Coarse mullion count | Subdivide each wing opening into narrower mullion bays |
| 4 | P2 | facade_close (700-855, 0-1080) | The pylon sign panel and pole occlude the centre third of the facade detail view. The facade stays legible. | Camera placed with the pylon in the line of sight | Shift the camera or target about 2 m so the pylon falls outside the frame |
| 5 | P2 | architecture_close (590-1330, 440-468); parapet_corner (690-1210, 600-625) | A continuous black slot sits between the tower glazing head and the header soffit. It reads as a void, not a transom. | Glazing stopped short of the header with no closure panel | Add a solid charcoal transom or spandrel closure at the glazing head |
| 6 | P2 | roof_plant (190-860, 255-700) vs source oblique (480-900, 240-300) | The rooftop units are plain white boxes with a single disc. The source units are low grey boxes with fans and vents. | Simplified rooftop-unit primitive | Use lower, wider grey units with a raised fan housing (optional for clay) |
| 7 | P2 | porte_cochere (545-750, 300-1080); interior (1220-1440, 0-970) | The stone-clad piers are smooth taupe with banding. They have no cap or plinth course, where the source piers show a cap. | Pier primitive has no cap | Add a 0.15 m projecting cap and plinth to each pier |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette (L-plan block, low SW wing, SE tower) | conforms, except the tower head (finding 1) | top vs source top; aerial and front_corner vs oblique |
| Storey count (4 storeys on the main block, 1 on the wing) | conforms | front, right_side, left_side, rear |
| Window rhythm (paired punched guest-room windows, stone-base ground floor) | conforms (bay panels missing, P2) | front, facade_close, right_side, rear_entry |
| Lobby tower (full-height glazing at the SE corner) | deviates: the glazing conforms, but the head height, roof level and header colour do not (P1) | parapet_corner, architecture_close, aerial, top |
| Porte-cocheres (two, glass-roofed, on stone piers, east and south) | conforms | aerial, porte_cochere, top, front |
| Low wing (one-storey glazed breakfast/pool wing with rooflight at the SW) | conforms (mullion count coarse, P2) | wing_contact, top, front_corner |
| Roof plant (white membrane roof, rooftop units) | conforms (units simplified, P2) | roof_plant, aerial, top |
| Site elements (parking court, drive loop, pylon sign, landscape verge) | conforms | top, aerial, front |
| Materials hierarchy (beige/charcoal EIFS, stone base, accent band: navy on the beige south leg's south and east faces, dark green on the charcoal north leg and the beige leg's west end) | conforms for the band; deviates for the tower header colour (inside P1) | front, right_side, left_side, rear_side, aerial, wing_contact |

## 4. Camera validity

- No view is invalid. Every target is legible and nothing is clipped.
- facade_close is partly occluded by the pylon sign (P2, finding 4).
- left_side, right_side and rear frame the asset small, at about 50-60% of the frame width. They are acceptable as elevation checks.

## 5. Previous-version (v006) findings, as verified in the v007 pixels

| v006 finding | status in v007 | pixel evidence |
|---|---|---|
| P1: the glazed lobby tower rose half a storey to a storey above the main parapet, where the sources put the tower header level with or just below the adjacent parapet caps and the tower roof below the main roof | **Partly resolved, P1 remains.** The large overshoot is gone: in right_side (430-540, 432-450) the header top is about level with the parapet top. But the header still stands proud of the parapet in parapet_corner and architecture_close. The tower roof is charcoal and at or above the main roof level (aerial, top), not stepped below it. The main navy band is interrupted by the header and does not continue behind it. | parapet_corner (300-1270, 315-610); architecture_close (535-1370, 305-440); aerial (630-860, 505-545); top (830-930, 700-800) |
| P1: the under-parapet accent band was navy on every block | **Resolved.** The band is navy on the beige leg's south and east faces. It is dark green on the charcoal north leg (rear, rear_side, right_side 640-1200, 455-470) and on the beige leg's west end (left_side 720-1005, 445-465; wing_contact 95-660, 0-195). | front, right_side, left_side, rear_side, wing_contact, aerial |
| v005 items (apron slot, frontage sequence and pylon, wing ribbon, cars on the verge) | Still resolved; no regression seen | top, aerial, front, wing_contact |
