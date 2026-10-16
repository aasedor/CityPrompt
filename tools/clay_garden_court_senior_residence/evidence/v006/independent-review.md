# Independent holistic review: garden-court senior residence, v006 (RLASM v6.1 architectural clay)

Reviewer: independent (did not build). Evidence: only the rendered pixels in `renders/` (all 18 opened at full resolution), the three locked sources, and the four phone boards. Zoomed crops were written only to `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-v006-crops-q7/`.

## 1. Verdict

**Verdict: PASS_ZERO_P0_P1.** The pixels show a coherent ring of three-storey red-brick blocks under copper standing-seam roofs, round a landscaped court, with gabled dormers, round-arched brick loggias, and an octagonal glazed garden room with a copper roof and a glass cupola. Every court element is present and grounded. The v005 garden-room door defect is fixed. What remains is polish only.

Counts: P0 = 0, P1 = 0, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| — | P0 | — | none found | — | — |
| — | P1 | — | none found | — | — |
| 1 | P2 | glass_close, architecture_close, court_view | The garden-room glazing is large 2x3 panes per facet, and the French-door leaves are single sheets of glass. The front source shows fine divided lites, about 6 to 8 small panes per sash, and muntin grids on the door leaves. | Muntin grid omitted on the glazing and door modules. | Add a thin white muntin grid to the facet sashes and the door leaves, roughly 3 columns by 4 rows per leaf. |
| 2 | P2 | glass_close, cv_door crop | The door handles render near-black. The builder claims brass. | Wrong handle material slot. | Assign a brass or ochre clay colour to the handle material. |
| 3 | P2 | facade_close, pergola_terrace, loggia_arcade | Up close, the wall "brick" shows only continuous horizontal course lines at about 0.19 m pitch with no head joints, so it reads as lap siding rather than masonry. | Course-line normal pattern without perpends, at about 2.5x brick course height. | Add staggered head joints, or use a finer course pitch, or drop the coursing and use plain brick-red clay. |
| 4 | P2 | court_view, front, front_corner | Each north loggia link has about 3 arches. The front source shows longer arcades of about 4 to 7 arches. This follows from the builder's top-view plan, which gives shorter links, so it is acceptable. | Plan conflict between sources, resolved toward the top view. | Optional: narrow the bay pitch to fit 4 arches per north link. |
| 5 | P2 | court_view, cv_fountain crop | The court fountain reads as a basin, an inner ring and one bowl with a stub finial. The source has a clearer stacked tiered form, with a mid bowl and a smaller upper bowl. The rose beds are small pink octagonal pads rather than the source's larger rose borders around the fountain. | Simplified fountain and bed primitives. | Add a smaller second bowl on a taller pedestal. Enlarge the rose beds into curved borders hugging the fountain plaza. |
| 6 | P2 | left_side (left_end crop) | A thin black vertical slot of about 2 to 3 px at full resolution sits at the outer end of the SW-pavilion-to-south-wing loggia, between the loggia end pier and the wing. | Small gap between the loggia end wall and the adjoining block, exposing an unlit cavity. | Extend the loggia end wall or pier to close the gap. |
| 7 | P2 | top vs source top | The source top shows a small white flat-roofed projection at the centre of the south wing's outer face, plus small white flat-roofed bays beside the north pavilions on the forecourt side. All are absent from the render top. They are on outer faces, small and ambiguous in the source. | Not modelled. | Optional: add a small white flat-roofed entry canopy at the centre of the south wing's outer face. |
| 8 | P2 | court_view, front, front_court crop | Iron balconies over arched garden doors appear on the NE pavilion court face and the east wing court face. None is legible on the NW pavilion court face, where the sources show one balcony per court face. | Balcony module not placed on every court face. | Place one balcony plus arched-door module at the centre of each block's court face. |
| 9 | P2 | glass_close, architecture_close | The garden-room corner posts are heavy round columns. The source shows slim square white posts between the glazed facets. | Column primitive choice. | Swap to square posts about 0.2 m wide. |

## 3. Source conformance checklist

| Item | Status | View(s) used | Note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial, rear, top | Five three-storey hipped-copper blocks round a court, a low loggia ring and a central octagon with a cupola. Matches the top source massing. |
| Storey count | conforms | left_side, right_side, rear, front | Three brick storeys plus a dormered roof storey on every block, matching the sources. |
| Plan (ring of blocks, court) | conforms | top vs source top, front_corner | Two north pavilions, the SW pavilion offset west, a long east wing and a long south wing, with low links between them. The court proportions (about 0.53 of the complex width) and the positions of the fountain, beds and pergola match the top source. The front/oblique disagreement is resolved toward the top view, as the brief states. |
| Roofs and dormers | conforms | dormer_roof, front_east_wing crop, top | The pavilions are hipped to a flat white top with rooftop units. The wings are hipped to a ridge. There are gabled white-framed dormers on every long slope, standing-seam ribs throughout and a clean eave overhang. The dormers sit on the roof plane. |
| Loggias and arches | conforms (P2 #4) | loggia_arcade, court_view, cv_nw_link crop, right_side | One-storey brick loggias with round arches, imposts, piers with real reveal depth, barrel soffits, raised stone plinth floors and hipped copper roofs. They are open through on the court face. Arch count is lower than in the front source. |
| Garden room and cupola | conforms (P2 #1, #9) | architecture_close, hub_cupola, glass_close, interior | The octagon is glazed on a brick base, with a radial-seam copper roof and a round glazed drum with a ribbed glass dome and finial. The drum sits on the roof. The garden room sits on the link between the north pavilions. |
| Window rhythm and balconies | conforms (P2 #8) | facade_close, left_side, right_side, cv_ne_face crop | Regular white double-hung windows with stone heads and sills, recessed with visible reveal shadow, in an even rhythm on every face. Arched garden doors with iron balconies above are present on the court faces, though not on every block. |
| Garden elements (paths, fountain, beds, pergola) | conforms (P2 #5) | court_view, garden_beds, pergola_terrace, top | Brick-tone paths form a central circle with cross paths. There are lawns, rose beds and a tiered fountain. The iron-fenced garden holds raised timber beds. The timber pergola has posts grounded on the dining terrace, with tables, chairs and benches. Everything is grounded and nothing floats. |
| Forecourt | conforms | top, hub_cupola, rear, front | North of the garden room: a circular lawn with cross paths and a two-tier fountain, a north path to the drive loop with its planted island, and the street. |
| Materials hierarchy | conforms (P2 #3) | all | Red-brick walls, copper roofs and white trim, glazing and stone base. Light grey roof membranes and units. Green lawns and brick-pink paving. The hierarchy matches the sources. The brick coursing reads as siding up close. |

## 4. Camera validity

- **front, front_corner:** whole envelope from high above the south, with nothing clipped. The court, garden room and cupola are legible. Valid.
- **aerial, rear_side:** whole envelope. Valid. The court is mostly hidden behind the blocks, as expected from these angles.
- **top:** whole site, nadir, legible. Valid.
- **left_side, right_side, rear:** the asset fills only about half the frame width, but it is not clipped and the elevations are legible. Valid. Tighter framing would be polish.
- **court_view:** the source-matched view into the court. The garden room with its door and step, the loggias, fountain, beds and pergola are all legible. Valid.
- **loggia_arcade:** a foreground tree canopy at top left and a white post at the right edge partly intrude, but the two arches, piers, imposts, soffit and plinth are fully legible. Valid.
- **facade_close, architecture_close, glass_close, dormer_roof, hub_cupola, garden_beds, pergola_terrace, interior:** each target is centred, not occluded and legible. Valid.
- No view is invalid.

## 5. Previous-version (v005) findings

| v005 finding | Builder's claim | Status in v006 pixels |
|---|---|---|
| P1: the garden room's court face read as fixed glazing down to grade, with no door frame or step. The sources show a white double French door with a transom and a stone step. | A pair of glazed French doors about 1.8 m wide in a heavy white casing with a proud head, a centre meeting stile, kick rails and brass handles, sidelights, a three-pane transom, a threshold and a projecting stone step, on both the court and forecourt faces. | **RESOLVED.** court_view (cv_door crop) shows on the south face a paired-leaf door in a heavy white casing with a projecting head block. The view also shows a centre meeting stile, narrow sidelights either side, the three-pane transom above, a bottom rail and threshold, and a projecting white stone step landing where the brick path arrives. glass_close and architecture_close confirm the casing, head, meeting stile, sidelights and transom, with handle pulls at the meeting stile. The interior view confirms the opening and the threshold from inside. The rear view (rear_center crop) shows the matching door, transom and sidelights on the north (forecourt) face. Remaining deviations are P2: the handles render dark, not brass (#2), the leaves lack the source's muntin grid (#1), and the kick rail is only a modest bottom rail. |
