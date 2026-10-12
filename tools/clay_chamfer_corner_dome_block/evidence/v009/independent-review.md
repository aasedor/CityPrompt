# Independent holistic review: chamfer v009 (RLASM v6.1 architectural clay)

Reviewer: independent; judged only rendered pixels (renders/*.png, boards/*.png) against locked sources (sources/front.png, oblique.jpg, top.jpg). No code, reports or builder notes consulted.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the massing, storeys, bowed bay, balconies, cornice and parapet now match the sources, and the ribs and cresting are fixed. Four dome and roof defects remain visible in the hero and top views: unglazed solid dormer discs, the rib/oculus phase on the chamfer axis is wrong, the lantern is an open white-post gazebo, and the pyramid rooflight shows up as a flat grey slab.

Counts: P0 = 0, P1 = 4, P2 = 7

## 2. Findings table

| # | severity | view(s) with pixel regions | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front.png dome x630-810 y320-370; chamfer_dome.png x545-895 y430-510; architecture_close.png x495-945 y160-250; left_side.png x920-1070 y365-400 | Every dormer still reads as a solid copper disc. The face inside the moulded ring is the same copper value as the frame (sampled about 165,128,110), so no glass and no dark recess show. The "bonnet" is a one-sided crescent fin on the inboard side of each disc, not a hood over the top. Source front.png (x505-545 y140-170) and oblique.jpg (x590-640 y450-490) show a dark glazed oculus in a moulded frame under a small top hood. | The oculus pane uses the copper material, or sits flush or behind an opaque cap; the hood is rotated 90 degrees around the dormer axis. | Give each oculus a glass pane in the window-glass material (the grey-green used on the facades), recessed at least 1/4 of the frame radius behind the ring. Rotate the bonnet so it caps the top of the frame. Re-render chamfer_dome and front and confirm a dark pane is visible in every dormer. |
| 2 | P1 | front.png x718-726 y285-420 (rib on axis); chamfer_dome.png x715-725 y300-660; architecture_close.png x715-725 y0-350; top.png rib toward the lower-left corner | A copper rib runs straight down the chamfer axis, with two dormers set symmetrically either side. In the sources the axis falls on a panel: source front.png has one centred oculus at x523 y155 flanked by ribs at about x497 and x548, and the oblique shows the same centred oculus at x625 y470. The dome's rhythm is half a bay out of phase, which changes the face of the identity element. | Rib and dormer azimuths start at 0 degrees on the chamfer axis instead of being offset by half a panel. | Rotate the rib set by half a panel (22.5 degrees for 8 ribs) so the chamfer axis falls on a panel centre. Put one dormer on the axis and keep the others in panel centres. |
| 3 | P1 | front.png x690-750 y195-280; chamfer_dome.png x670-770 y100-285; roof_terrace.png x650-735 y255-405 | The lantern is an open ring of thin white stone-coloured posts. Sky shows straight through it, with no glazing, no entablature and a low smooth hemispherical cap under a thin grey rod. Source front.png (x495-550 y20-110) and oblique.jpg (x575-640 y240-380) show a glazed octagonal copper lantern: dark glass between copper mullions, a moulded entablature, a ribbed copper cupola and a ball finial. In the hero view it reads as a gazebo, a different element. | The lantern is built from posts only, with no glass panes and the posts using the stone material. | Fill the bays between posts with glass panes in the window-glass material and change the posts to copper. Add an entablature ring, rib the cap into 8 segments and replace the rod with a ball-and-spike finial. |
| 4 | P1 | top.png x705-835 y450-580 and small units x620-670 y395-430 and x872-920 y623-658; aerial.png x690-810 y490-590; front_corner.png x675-795 y465-535; left_side.png x630-760 y455-505 | From above (the matched top role and the aerial), the pyramid rooflight is a flat grey square plate in a white rim, with no ridges, no glazing bars and no visible pitch. Only the low side view (left_side) shows that a fully transparent, frameless pyramid exists. The small rooflights are flat grey squares as well. Source top.jpg (x545-655 y380-495) shows a clear four-facet glazed pyramid with ridge and glazing bars on an upstand, and oblique.jpg shows sloped framed glazed rooflights. | The glass is fully transmissive with no frame or ridge members, so the pitch never registers optically, and the pyramid sits straight on the deck. | Add copper or dark-metal ridge, hip and glazing-bar members and a low masonry upstand. Give the pyramid glass and the small rooflights the window-glass material (partly reflective, tinted) so the facets read in top and aerial views. Re-render top and aerial to confirm. |
| 5 | P2 | chamfer_dome.png x540-900 y575-660 | The cresting is a flat-topped band of repeated "8" loops between thin posts. The source has peaked pierced roundel or scroll panels with crests over pedestals. Height and placement are now right. | Simplified panel motif. | Optional: arch or peak each panel top and add a roundel motif and pedestal blocks. |
| 6 | P2 | chamfer_dome.png dome vs roof deck | The copper dome (about 165,128,110) is close in hue and value to the terracotta deck (about 184,153,135). In the sources the copper is clearly darker and browner than the tiles. | The copper colour is too close to the roof palette. | Darken and desaturate the copper toward bronze-brown. |
| 7 | P2 | ground_arcade.png x620-820 y415-745 | The chamfer entrance has a semicircular head. The source entrance (front.png x488-562 y565-700) is tall and nearly flat-headed in a stone frame. | Generic arch profile. | Flatten it to a segmental or square head with a stone surround. |
| 8 | P2 | front.png ground floor x380-580 and x860-1060 y710-820; glass_close.png | The shop openings are narrower than the source's (about 1/3 of the bay against about 1/2), and the rustication is drawn as hairline joints only. | Opening width and channel depth. | Widen the openings toward source proportion and deepen the channel joints. |
| 9 | P2 | top.png x380-440 y650-700 and x555-600 y830-875 | The chamfer pier cornice caps read as skewed wedges projecting past the facade lines next to the dome. | The cap geometry is rotated 45 degrees at the chamfer. | Trim the caps so they meet the wing cornices cleanly. |
| 10 | P2 | balcony_ironwork.png, facade_close.png | The ironwork is plain bars, where the source has ornamented cast iron. Acceptable for clay. | Simplification. | Optional baluster or scroll infill. |
| 11 | P2 | cornice_contact.png x900-1200 y295-590 | The corner pier cap is an oversized plain block above the cornice. | Simplified pedestal. | Optional: mould the cap. |

## 3. Source conformance checklist

| item | status | view used |
|---|---|---|
| Silhouette | conforms: a square corner block with a chamfered corner and a dome above a bowed bay | front, front_corner, aerial vs front.png, oblique.jpg |
| Storey count | conforms to the source pixels: a tall ground floor plus two upper storeys on the wings, with a two-storey glazed bay. The sources show the same count (the brief's "five storeys" text is not borne out by the locked pixels; the render follows the pixels) | front vs front.png; roof_terrace vs oblique.jpg |
| Chamfer bay and dome | bay conforms (bowed, columns, glazing, balconies); dome **deviates** (findings 1, 2, 3) | front, chamfer_dome, architecture_close |
| Window rhythm and balconies | conforms: 4 bays per wing, a continuous balcony on the first floor, individual balconies above, stone surrounds, tall French windows with visible reveals | front, facade_close, balcony_ironwork |
| Ground-floor arches and entrance | conforms on rhythm, entrance on the chamfer; P2 on head shape and opening width | ground_arcade, glass_close |
| Cornice and parapet | conforms: a bracketed cornice with a balustrade and corner pedestals | cornice_contact, front, roof_terrace |
| Roof elements | **deviates**: the pyramid rooflight and small rooflights are illegible from above (finding 4); terracotta deck and four chimney stacks conform | top, aerial vs top.jpg |
| Materials hierarchy | conforms: stone base, bay and surrounds; warm brick field; dark iron; terracotta deck; copper dome (P2 on copper contrast) | front, chamfer_dome |

## 4. Camera validity

No invalid cameras. All 18 views frame their target without occlusion or clipping. interior.png is dark but legible (the French window, the iron rail outside and the reveal are all visible). front_corner.png and aerial.png show the building small in frame but legible. The rear faces (rear, rear_side, right_side, rear_court) are plain and coherent with the visible grammar, which is acceptable because no source shows them.

## 5. v008 findings: resolved in the pixels?

1. **v008 P1, dormers as solid copper discs with hood plates, no glazed oculus in a moulded frame, outer two standing off the outline: NOT RESOLVED.** A moulded ring frame and a shorter crescent hood are now visible, and the outer two sit on the shell (chamfer_dome x545-600 and x840-895). But no oculus shows glass or a dark recess: every face is copper-coloured and flat (chamfer_dome x600-700 and x750-850 y440-505). The read is still "solid disc", so this carries forward as finding 1.
2. **v008 P1, only the front rib continuous, the others stepped with gaps short of the lantern: RESOLVED.** In chamfer_dome.png and architecture_close.png every visible rib is one unbroken swept band from the cresting up to the lantern neck (for example chamfer_dome x560-690 y300-600 and x740-880 y300-600), with no steps or gaps.
3. **v008 P1, thin post-and-zigzag cresting on a stone disc: RESOLVED.** Tall open copper panels now stand at the dome base on a copper-faced disc (chamfer_dome y575-660, about 22% of the dome height). The panel motif is a residual P2 (finding 5).

The v008-verified items still hold: the bowed bay reads correctly and the front camera is valid.
