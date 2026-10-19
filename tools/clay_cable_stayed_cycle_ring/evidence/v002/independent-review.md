# Independent holistic review: ring v002 (cable-stayed circular cycle bridge)

Reviewer: independent RLASM v6.1 holistic reviewer. Evidence used: the pixels of `sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`, all 18 `renders/*.png` opened at full resolution, the four `boards/*.png`, and zoomed crops written to the new folder `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/ring-v002-review-crops-427e846b/`. I did not rely on metadata or the builder's notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v001 P0 and most of the v001 P1s are fixed in the pixels, but three P1 defects remain. The cables do not reach their anchor blocks, a black slot still shows at the gable base of every pitched context house, and the ramp has the red ring finish where all three sources show a pale concrete ramp.

Counts: P0 = 0, P1 = 3, P2 = 6

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | architecture_close, column_support, facade_close (also legible in intersection_under) | Every stay cable stops at the top edge of the inner deck kerb. Its white rectangular "anchor" block hangs on the inner fascia about 15–20 px lower in full-frame pixels, with a clear strip of bare fascia between the cable end and the block (architecture_close at x≈620/1330, y≈485–560; column_support along the inner arc; facade_close along the far arc). So the cables seem to go into the deck top, and the anchor boxes float as unconnected parts. | The cable end point is set at deck-top/kerb height, while the anchor block is placed at a fixed lower offset on the fascia. The two are not derived from the same anchor point. | Compute one anchor point per cable on the inner fascia face, put the block's centre there, and end the cable on the block's top face, or move the block up so it takes the cable end at the kerb line. Re-shoot architecture_close and column_support. |
| 2 | P1 | front, front_corner, right_side, rear, rear_side, rear_north, ramp_landing, column_support | The v001 pure-black gables are now brick triangles, but each pitched-roof context house still shows a solid black slot along the gable base / eave line, a few px thick at full frame and a stark black band when zoomed (rear_north x≈1195–1345, y≈705–715; rear x≈1205–1255 and ≈950–1000; front_corner x≈95–150, y≈685–720; ramp_landing x≈470–565, y≈435–440). | The gable triangle sits on top of the wall with a gap, or the roof plate overhang leaves an open, unlit slot (a backface or interior showing) between the wall top and the gable or roof plate. | Extend the gable triangle down to the wall top, or close the eave with a soffit or fascia strip in brick or roof colour. Check that no open or back-facing polygon stays at the eave of any context house. |
| 3 | P1 | top, aerial, front_corner, ramp_landing, front | The whole ramp deck is red-brown with a dashed centre line, the same as the ring. All three sources show the ramp in a different material from the ring: pale grey-beige concrete (source top mean RGB ≈ 158,135,112 against the ring at ≈ 149,120,104) with a single solid white centre line, which you can see clearly in source top, the oblique ramp and the source front ramp. The governing top view loses the source's red-ring/grey-ramp material hierarchy. | The ring deck material and line style were reused for the ramp deck. | Give the ramp deck the source's pale grey concrete tone and a continuous white centre line. Keep the red only on the ring and on the at-grade cycle path and apron. |
| 4 | P2 | pylon_head, front_corner, cable_fan | The cable head is still a flat-topped drum wider than the mast, with an inverted funnel under it that narrows downwards. The source collar (front, oblique, top) is a cone that flares downwards from the mast, with the cables leaving its lower rim. The v001 P2 is therefore not resolved: the silhouette is the reverse of the source. | The spreader cone is built upside down, or set below a leftover drum. | Remove the drum. Add a single cone with its narrow end at the mast and its wide end at the bottom, and start the cables from its lower rim. |
| 5 | P2 | intersection_under, facade_close, front_corner | The pylon foot is a cylindrical sleeve on a flat disc. The source oblique shows a flared white conical foot on a kerbed round island. | The base is simplified. | Model a short flared cone foot on a raised round island with a kerb ring. |
| 6 | P2 | front | The front camera is now valid (outside the ring by the ramp, with the near arc, a column, the ramp going down to the right and the pylon centred), but it sits far back and only slightly above the deck. The ring fills about 64% of the frame width and the deck plane reads edge-on as a thin red strip. In the source front the ring overfills the frame and the deck surface is seen from above. | The camera was pulled back so the whole pylon fits. | Move the camera closer and a little higher, and let the mast tip leave the frame top as the source front does, or keep the full-pylon framing but raise the camera so the deck surface is legible. |
| 7 | P2 | ramp_landing, front_corner | The ramp handrail bars end in free cantilevers with no end post or return. The right rail stops about one bay short of the foot while the left rail runs to the end. | The rail run length is set per side with no terminal component. | End both rails at the same station near the foot with an end post and a downward return. |
| 8 | P2 | top, aerial | The ring is slightly small for the road layout: outer diameter / E-W carriageway width ≈ 3.0 in the render against ≈ 3.9 in the source top, so the inner circle only just clears the crossing box instead of reaching over the corner islands. | The road widths were scaled up, or the ring radius was scaled down. | Narrow the carriageways (or the lane count) by about 20–25%, or enlarge the ring by the same amount, and keep the columns on the corner islands. |
| 9 | P2 | rear_side, pylon_head, cable_fan, column_support | In rear_side a large foreground context block takes up the lower centre of the frame and hides the near column foot. pylon_head and cable_fan render grey-on-grey with very low contrast, so the cable and mast edges are faint. The ring columns render as pale as the steel deck, whereas the source columns are darker raw concrete. | Context placement, the haze/exposure setting, and a shared light material. | Move or lower the rear_side foreground block. Reduce the haze or raise contrast for the sky-backed detail views. Give the columns a mid-grey concrete tone darker than the white steel. |

## 3. Source conformance checklist

| item | status | view(s) used |
|---|---|---|
| Plan and proportions | deviates (minor): circular ring centred on the crossing, one straight ramp leaving the south-west and running south beside the N-S road, as in the source top. The ring is slightly small against the carriageways (finding 8). | top vs source top, aerial |
| Ring radius and width | conforms: the deck width / outer diameter ratio is close to the source (≈ 0.08 against ≈ 0.09). | top, ring_deck |
| Pylon | conforms in mast form and placement: one tall central mast of constant diameter, whole tip in frame. The head and foot detailing deviate (findings 4, 5). | front, left_side, pylon_head, intersection_under |
| Cable fan | conforms as a radial fan from one head to the inner edge with dense spacing. The cable-to-deck anchorage deviates (finding 1). | top, cable_fan, front, architecture_close |
| Deck surface and edges | the ring conforms (darker red-brown, dashed white lines, outer kerb arc stops at the ramp mouth so the ring deck runs flush onto the ramp). The ramp surface deviates (finding 3). | ring_deck, top, front_corner, aerial |
| Railings | conforms: white posts and top rail on both ring edges, with glazed infill, a shoe kerb and depth visible. The ramp has open bars, close to the source's open ramp rail. The ramp rail ends deviate (finding 7). | glass_close, ring_deck, architecture_close, ramp_landing |
| Columns | conforms in count and form: four tapered blade columns under the ring and ramp piers, all touching the ground. The material tone deviates slightly (finding 9). | left_side, column_support, front, architecture_close |
| Ramps and landings | geometry conforms: straight ramp on piers that touches down on a red apron with white edge lines and block dashes joining the cycle path by the N-S road. Material deviates (finding 3). | ramp_landing, aerial, top |
| Intersection beneath | conforms: four-arm crossing, lane dashes, red cycle-crossing bands with block-dash edges, pylon island at the centre. | intersection_under, facade_close, top |
| Context | deviates: low brick blocks, pitched houses and trees are present, but there is a black eave/gable slot on every pitched house (finding 2). | rear_north, rear, front_corner |
| Materials hierarchy | deviates: the red ring and white steel read correctly, but the source's grey ramp and darker concrete columns are not separated from the ring and deck (findings 3, 9). | top, aerial, column_support |

## 4. Camera validity

- No view is invalid. In all eight whole-envelope views (front, front_corner, aerial, top, left_side, right_side, rear, rear_side) the full pylon tip is in frame and the ring is legible. In aerial and top the whole ramp is visible from the ring to its foot (in top the apron sits about 20 px above the bottom edge, which is tight but in frame).
- rear_side: the foreground context block covers the lower centre and the near column foot. The target is still legible (P2, finding 9).
- pylon_head and cable_fan: legible but low contrast against the hazy sky. In cable_fan the mast tip is about 10 px from the top edge (P2, finding 9).
- front: valid but distant and low (P2, finding 6).
- rear_north is now a distinct low NNE viewpoint. The ramp is hidden behind the ring from there, which is correct for that side.

## 5. Previous-version (v001) findings: resolution in the pixels

| v001 finding | status in v002 pixels |
|---|---|
| P0: ramp ground landing never shown; ramp lost while still raised | **Resolved.** ramp_landing stands at the ramp foot looking up the ramp: the deck touches down on a red apron with white edge lines and block dashes beside the N-S road's cycle path. aerial and top show the whole ramp from the ring to the foot. |
| P1: outer kerb ran across the ramp mouth as a raised bar | **Resolved.** The outer kerb and balustrade stop on either side of the mouth, and the ring deck runs flush onto the ramp (front_corner, aerial, top crops). |
| P1: ring balustrades open bars, no glazed infill | **Resolved.** glass_close, ring_deck and architecture_close show pale glazed panels under the top rail, with a shoe kerb and the cables seen behind the glass. The ramp keeps open bars. |
| P1: front camera on the deck at rail height | **Resolved.** The camera is outside the ring by the ramp, showing the near arc fascia, a column, the ramp going down to the right and the pylon centred. A residual framing issue is P2 (finding 6). |
| P1: pylon tip / cable collar / mast top cut off | **Resolved.** The tip is in frame in every whole-envelope view. pylon_head now frames the mast top and collar. |
| P1: context gable triangles rendered pure black | **Partly resolved, carried as P1 (finding 2).** The triangles are now brick, but a black slot remains at every gable base or eave. |
| P2: drum-shaped cable collar, mast tapering to a needle | **Mast resolved** (constant diameter, rounded tip). **Collar not resolved:** still a drum with an inverted funnel that narrows downwards, not the source's cone flaring downwards (finding 4). |
| P2: straight prismatic columns with cap blocks | **Resolved.** The columns are tapered blades, wider at the deck, with no cap blocks. |
| P2: zebra crossings instead of Dutch block-dash cycle crossings | **Resolved.** Red cycle bands with block-dash edges (facade_close, intersection_under, top). |
| P2: deck too light and pink | **Resolved.** The ring deck is now a darker red-brown. |
| P2: rear and rear_north near-duplicates | **Resolved.** rear is an elevated view from the north; rear_north is a low NNE viewpoint. |
