# Independent holistic review: clay-timber-covered-footbridge v002 (RLASM v6.1)

Reviewer: independent; judged from rendered pixels against the three locked sources only. I opened all 18 renders, the 3 sources and the 4 phone boards. Zoomed crops are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-crops-1259114811/`.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: most v001 defects are fixed in the pixels, but the side-wall bay schedule still does not match the sources. There are now 10 narrow bays, with a louvre-only end bay and a separate open diagonal bay. The sources have 6 equal bays, and each end bay combines full-height louvres with the one long diagonal.

Counts: P0 = 0, P1 = 1, P2 = 12

## 2. Findings

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front, front_corner, aerial, rear, rear_side, rear_north, facade_close, architecture_close | Each side wall reads as 10 bays: [louvre-only end bay][open bay with one long diagonal][6 open knee-braced bays][open diagonal bay][louvre-only end bay]. In the sources (oblique: posts at about x 515/665/770/855/920/980/1040; top: posts at about x 320/410/510/610/707/810/905, an even ~97 px spacing; front: bay 478-665) there are **6 equal bays**. Each end bay holds full-height louvres **and** the long diagonal, which runs from the post foot on the portal side to the post head on the midspan side and lies over the louvres. The 4 interior bays are open and knee-braced. The render therefore adds an extra bay type at each end: the diagonal is in an open bay and the louvred bay has no diagonal. Bays are also about 30% narrower relative to the roof width (render bay/roof width ≈ 0.49; source ≈ 0.69). | The builder split the "end bay" and the "bay next to each portal" into two separate bays. The bay count follows a fixed module and is not fitted to the length from the top source. | Rebuild the side frames with 6 equal bays over the same overall length (≈ 1/6 of the post-to-post length each). In each end bay, keep full-height louvres on the bottom rail and put the single long diagonal across them from the foot of the portal-side post to the head of the midspan-side post. Make the 4 interior bays open, with knee braces under the rail and one louvre band above it. Delete the separate louvre-only bay and the open diagonal bay. |
| 2 | P2 | facade_close, roof_eaves, front | Interior braces are short, straight 45° knee braces (about 1/4 of the bay). The front source (crop) shows long, shallow, slightly arched braces that make a segmental arch under the rail in each interior bay. | Brace length and curvature set by a generic knee-brace module | Lengthen the braces to reach about 40% of the bay and give them a shallow curve or a flatter angle |
| 3 | P2 | front, portal_end, architecture_close, left_side, right_side | Large knee braces sit in the plane of the portal frame. Neither front nor oblique source shows braces in the portal opening: it is a clean rectangular post-and-header frame. | Interior transverse frame reused at the portals | Remove the portal-plane knee braces, or keep them only on the interior transverse frames |
| 4 | P2 | pier_abutment, rear, rear_north | The round pier carries a tapered headstock about 1.3x the pier diameter. The front source shows a plain wide cylinder with the girder bearing directly on it. | Headstock flare set wider than the brief's "as wide as the pier" | Trim the headstock top to the pier diameter, or drop it and let the girder bear on the cylinder |
| 5 | P2 | top, stream_under, rear, aerial | The stream is still a uniform hard-walled canal with straight edges. The top source has a soft, reed-planted bank on the east side and an irregular edge. | Channel generated as a straight extrusion (carried over from v001) | Add a reed/planted strip and a softened bank edge on one side over about 1/3 of the visible length |
| 6 | P2 | top, aerial, left_side | Planting is still sparse: low-poly shrub lumps on flat grass strips. The sources show dense planted banks next to the approaches. | Carried over from v001 | Add massed shrub/bank planting beside both landings and along the bank shown in the sources |
| 7 | P2 | portal_end, left_side, right_side, front | The landing is a timber plate sitting proud of the paving with a visible raised edge. In portal_end, the glass wing panels flare out and stand on the paving beyond the landing edge. | Landing modelled as a slab on top of the paving, not flush. Wing panels placed on a flare angle. | Set the landing flush with the paving and align the wing glass to the landing edges |
| 8 | P2 | architecture_close, portal_end | A thin dark seam runs between the triangular gable board and the portal header. There is a light sliver between the header top and the roof fascia. | Small gap or z-offset between the gable board, header and soffit | Close the gap: seat the gable board on the header and the soffit on the header top |
| 9 | P2 | portal_end, architecture_close | A small grey block (ridge-cap end) sits proud above each hip apex, like a tiny chimney. It is not timber, so v001's poke-through is gone. | Ridge cap end-cap is longer or taller than the hip apex | Shorten the ridge cap to stop at the apex and mitre it into the hip caps |
| 10 | P2 | front, architecture_close, portal_end | The roof soffit under the eaves and over the portal is grey zinc colour. The front source shows a warm timber-boarded soffit. | Roof underside uses the roof material | Assign the timber clay colour to the soffit or underside faces |
| 11 | P2 | deck_inside, portal_end, right_side | Irregular dark blotches on the deck boards, not tied to any geometry | Low-sample or denoiser shading artifact, or diffuse light leaking through the louvres | Raise the render samples or turn on the denoiser for the interior views, or add a simple fill light |
| 12 | P2 | front_corner, left_side, rear_side, context in general | The context block is still 5-6 storeys with a plain cube roof. The oblique source shows a 4-storey block with a parapet roof. No render repeats the oblique source's elevated along-axis viewpoint; aerial is the closest. | Carried over from v001 | Drop the block to 4 storeys. Add one camera that matches the oblique source (elevated, about 30° off the axis, west portal plus the south wall). |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Plan and proportions | Conforms overall. Length-to-roof-width ≈ 4.9 against source 4.7. Bridge runs E-W across the stream and both towpaths, with timber landings at both ends and hips at both ends. Bay module deviates (finding 1). | top vs top source, aerial |
| Frames and braces | **Deviates**: 10 bays against 6. The end bay and the diagonal bay are separated, so the diagonal sits in an open bay. Interior braces are short. Portal braces are extra. The diagonal direction is correct (portal-side foot to midspan-side head). No truss reading remains. | front_corner, rear, facade_close, front |
| Louvres | Conforms in form: one regular layer of louvres, full height in the end bays on a bottom rail, and one band above the rail in the interior bays. The band is about 22-29% of the wall height, against about 28% in the source. Placement deviates because it follows finding 1. | louvre_wall, facade_close, roof_eaves, front |
| Roof and eaves | Conforms: grey standing-seam hip roof, seams running down the slope, ridge plus hips, deep overhang at the hip ends (about 30% of portal width in front, as in the source). Soffit colour deviates (P2). | front, top, roof_eaves, portal_end |
| Deck | Conforms: timber boards, glass balustrade with a steel cap rail inside. Shading artifact is P2. | deck_inside, glass_close |
| Piers and abutments | Conforms: round concrete piers at each stream edge on the towpaths; concrete abutments cut into both planted banks with the girder ends seated square. Headstock flare is P2. | pier_abutment, rear, stream_under, front |
| Approaches and railings | Mostly conforms: paved approaches with grey steel bar railings along the stream walls and glass at the landings. Large-format paving rather than setts is acceptable in clay. Raised landing edge is P2. | front, portal_end, left_side |
| Stream and banks | Deviates (P2): uniform canal with hard walls on both sides and no reed bank. | top, stream_under |
| Planting | Deviates (P2): sparse shrub lumps. | top, aerial |
| Context | Partly conforms: brick-coloured apartment blocks with balconies. Height is 5-6 storeys against 4 (P2). | front_corner, left_side |
| Materials hierarchy | Conforms: timber frame and louvres, grey zinc roof, grey concrete piers, glass balustrade, grey steel railings. Soffit colour is P2. | all |

## 4. Camera validity

- **front**: valid. The whole near portal, its roof corner and its eaves are inside the frame. The railing in the foreground crosses the girder but does not hide the target.
- **aerial**: valid. The east portal, landing and abutment are now clear of the tree.
- **left_side / right_side**: valid but they are along-axis end views, not side elevations. The target is legible. In right_side the context block takes the right quarter of the frame, but the bridge is not occluded.
- **louvre_wall, glass_close**: valid close-ups. The dark area at the top of louvre_wall is the roof soffit, not a void.
- **stream_under, pier_abutment**: valid. Supports and the underside are legible.
- No view is clipped, occluded or illegible: no P0 camera defect.

## 5. v001 findings: resolved in pixels?

| v001 finding | Status in v002 pixels |
|---|---|
| P1 Side bays read as a Warren/Howe truss (a diagonal in every bay, no knee braces) | **Resolved as stated**: interior bays are open with knee braces, and only one diagonal sits near each end. **Superseded by new P1 #1**: the end-bay schedule and bay count do not match the sources. |
| P1 Interior louvres in two staggered, ragged layers ending in mid-air with no bottom rail | Resolved: one regular louvre layer between the rail and the wall plate. End-bay louvres stand on a bottom rail (facade_close, roof_eaves, louvre_wall). |
| P1 Timber block poking through the zinc roof near the hip apexes | Resolved: no timber pierces the roof. A small grey ridge-cap nub remains at the apex (P2 #9). |
| P1 Portal post tops showing black void faces under the eaves | Resolved: no black squares (architecture_close, portal_end). A thin seam line remains (P2 #8). |
| P1 Edge girder about twice the source depth, with tapered boat ends | Resolved: the girder is straight with square ends. Depth ≈ 0.22 of the deck-to-plate height, within the source range (about 0.15-0.28 across front and oblique). |
| P1 No concrete abutments; girder ends running into the planted bank | Resolved: concrete abutments are cut into both banks with a cill, and the girder seats on them (pier_abutment, rear, stream_under). |
| P1 Pier cap off-centre and floating over water in the front view | Resolved: concentric headstock on a round pier standing on the towpath. Flare is P2 #4. |
| P1 Front camera clipping the near portal post, roof corner and eaves | Resolved (front). |
| P1 Foreground tree in the aerial view hiding the east portal end, support and landing | Resolved (aerial). |
| P2 No render repeats the oblique viewpoint | Not resolved (P2 #12). |
| P2 Uniform hard-walled stream, no reed bank | Not resolved (P2 #5). |
| P2 Sparse planting | Not resolved (P2 #6). |
| P2 Raised timber kerbs on the landings | Partly resolved: the edge-beam upstands no longer run onto the paving, but the landing plate is still proud of the paving (P2 #7). |
| P2 Thin black line between header and roof soffit | Not resolved (P2 #8). |
| P2 Span slightly long for the stream | Acceptable now: span-to-stream ratio is close to the top source. |
| P2 Five-storey context block | Not resolved (P2 #12). |
