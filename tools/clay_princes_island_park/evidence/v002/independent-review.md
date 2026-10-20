# Independent holistic review: clay-princes-island-park v002 (RLASM v6.1)

Sources opened: sources/front.png, sources/oblique.jpg, sources/top.jpg. Renders opened at full resolution: all 18 PNGs in renders/. Boards opened: phone-01 to phone-04. Zoomed crops (read-only copies) are in /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/review-crops-35f1a953/.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: three of the five v001 P1s are fixed and two are reduced to P2, but rip-rap boulder tips now break through the boardwalk deck, and at pedestrian range the bed planting still reads as primitive pastel sheets and faceted lumps.

Counts: P0 = 0, P1 = 2, P2 = 11

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | boardwalk (also visible at the same edge in right_side and rear_side) | About seven beige-grey pyramidal wedges stick up through the boardwalk deck just inside the east kerb, at irregular spacing along the curve. They are the same colour and facet style as the rip-rap boulders. This is an intersection or contact defect on a hero walking surface. | The enlarged 2–3× rip-rap boulders were scattered against the bank line without being clipped to, or kept clear of, the boardwalk deck and kerb footprint. | Reject or push seaward any boulder whose bounds overlap the deck or kerb footprint plus about 0.1 m. Alternatively, cap boulder height under the deck, then re-render boardwalk and right_side. |
| 2 | P1 | front, porch_northwest, west_path, glazing_close, promenade_beds (and front_corner at mid-range) | At pedestrian range the beds still read as primitives. The perennial "flower masses" are flat pastel sheets draped over the mounds: pink reads as crumpled cloth (west_path, right), and white reads as snowcaps with cone-shaped heads (front foreground, glazing_close). The shrubs have clearly faceted silhouettes and flat-shaded planes despite the "smooth-shaded" claim (front, porch_northwest left bed). Each grass clump is 5–8 stiff straw blades with bare bed fill between them, against the dense feathery, plumed grasses and fine flower spikes of the front and oblique sources. In the front view one mound passes through the bed kerb and onto the paving. From the air (front_corner, aerial) the density and pink/lavender/white drift now read well, so only the close-range finish is still failing. | The flower head is a single domed cap mesh with low subdivision, the shrub lobes are low-poly spheres, and the grass has too few blades per clump. Mound placement is not clamped inside the kerb inset. | Replace each domed cap with clusters of small separate flower heads or spikes (for example 15–30 small instanced heads per drift) and shade-smooth the shrubs with more subdivision. Raise grass clumps to about 20–30 thinner blades and add plumes to some. Inset all placements at least 0.25 m inside the kerb. Re-render front, west_path, porch_northwest and glazing_close. |
| 3 | P2 | green_roof, aerial, top, front | The sedum roof is now a continuous olive/ochre/rust mat, which fixes the v001 flagstones. But the patches are coarse (about 0.5–1.5 m), stretched along one world axis so they read as diagonal striping on the rotated roof, and the salmon-rust share is too high, so the roof reads peach-orange against the source's ochre-gold and olive. The claimed undulation is not visible: the roof reads as a flat printed plane, and the flowering clumps read as tiny cubes. From the front, no mat shows above the fascia, whereas the source front shows a tufted green edge. | Anisotropic patch noise, an over-weighted rust layer, and too little displacement amplitude. | Use isotropic, finer patches, cut rust to small accents and increase the displacement or tuft relief. Let the mat edge rise just above the fascia line. |
| 4 | P2 | front, pavilion_close, promenade_beds, boardwalk, west_path, rear | Tree crowns still show polygonal silhouettes and facets (the "smooth-shaded" claim is not borne out), and every tree is a lollipop form with a long bare trunk. | Low-subdivision crown spheres with flat or partly flat shading. | Subdivide and smooth the crowns, add lower scaffold branches, and vary crown base height. |
| 5 | P2 | footbridge, bench_plaza, left_side, top | The far bank is now wooded: about 30 trees in staggered rows with understorey mounds and shore boulders, so the v001 P1 is resolved. It still reads as a planted belt of equal-height standard trees with exposed trunks over lawn, rather than the dense woodland in the oblique source with canopy down to the shore. | Uniform trunk height, no low canopy layer. | Vary trunk heights, add lower-canopy and shrub masses between the trunks near the landing. |
| 6 | P2 | riprap_bank, right_side, footbridge | The rip-rap is larger and better massed, but the boulders are pale cream-grey, sharp-faceted polyhedra (hexagonal outlines) rather than the grey-brown rounded river stone of the oblique and top sources. Grass clumps between them are sparse. | Low-poly boulder meshes and a light albedo. | Smooth or subdivide the boulders, darken and warm the albedo toward grey-brown, and add a few more grass tufts. |
| 7 | P2 | promenade_beds, porch_northwest | Where sett borders end or turn at bed edges they finish in sharp dark-grey dagger points that overhang the paving or grass. | Mitre or offset artefacts at the polyline ends of the sett border. | Square or clip the border ends to the path outline. |
| 8 | P2 | bench_plaza, footbridge, front | Small black squares sit at slab joint crossings (bench_plaza), and short black slits appear in the bridge kerb (footbridge). | Joint-gap geometry showing the void beneath, or z-gaps. | Fill the joint crossings and close the kerb segment gaps. |
| 9 | P2 | glazing_close, pavilion_close | The battens stop at the window head and leave a row of short stubs that read as a dentil course above the glazing. | Batten array not trimmed to a head board. | End the battens on a continuous head trim or carry them up to the beam band. |
| 10 | P2 | front vs source front | The south-west face has a door, one 2×2 window and corner glazing. The source front also shows a long horizontal upper glazing band over the timber panels. | Simplified opening schedule. | Add the upper glazing band on the south-west face. |
| 11 | P2 | front, promenade_beds, front_corner vs oblique | The promenade is large slabs framed by sett bands. The oblique and front sources also show wide bands of long-format stretcher-bond pavers flanking the slabs. | Paving hierarchy reduced to two materials. | Add linear-paver strips between the sett borders and the slab field. |
| 12 | P2 | footbridge, rear_side | The edge of the model tile is visible: the river ends in a hard cut with a large flat grey void beside it. | Camera framing includes the tile boundary. | Tighten the framing, or extend the water and bank planes beyond the camera frustum. |
| 13 | P2 | rear | The raised rear camera shows only about a third of the pavilion roof; the north grove still hides most of the pavilion. | Camera still low or close relative to the grove. | Raise or pull back slightly so the roof reads in full over the grove. |

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Plan: pavilion position and rotation (about 27°) | conforms | aerial vs top source, top | Centre-right, rotated to match the source roof edges. |
| Plan: promenade past the south-west face, south plaza to north-west | conforms | aerial, front_corner | |
| Plan: west crossing band | conforms | aerial, west_path, left_side | |
| Plan: two north-south cycle paths | conforms | aerial, top | |
| Plan: lens-shaped kerbed beds | conforms | aerial, front_corner | |
| Plan: grove north of the pavilion and trees along the boardwalk | conforms | aerial, right_side | |
| Plan: boardwalk and rip-rap bank on the east, river east | conforms | aerial, top | |
| Pavilion green roof | deviates (P2 #3) | green_roof, aerial | Continuous ochre-olive mat, but coarse, striped and too rust-heavy. |
| Pavilion thin dark metal fascia | conforms | pavilion_close, green_roof | |
| Pavilion cedar board-and-batten | conforms | pavilion_close, porch_northwest | Stub battens above the glazing (P2 #9). |
| Pavilion glazed south-east face, dark mullions, long table inside | conforms | glazing_close, riprap_bank | The interior has depth and returns. |
| Pavilion south-west door and corner glazing | conforms, simplified | front, pavilion_close | Upper glazing band missing (P2 #10). |
| Pavilion north-west porch with two doors | conforms | porch_northwest, promenade_beds | |
| Pavilion clerestory on the north-east face | conforms | riprap_bank | |
| Pavilion slim timber corner posts | conforms | front, green_roof, porch_northwest | Posts land on the slab. |
| Pavilion interior | conforms | glazing_close | Table, benches, back counter, side glazing. |
| Promenade slabs | conforms | front, promenade_beds | |
| Promenade sett borders | conforms | front, front_corner, promenade_beds, aerial | Flush, dark, jointed two setts across, with cross-bands. End artefacts (P2 #7); no linear-paver band (P2 #11). |
| Promenade joints | conforms | bench_plaza, front | Flush lines. Black dots at crossings (P2 #8). |
| South plaza, sett frame, two trees in kerbed pits | conforms | aerial, front_corner | |
| Cycle paths: asphalt, yellow dashes, flush concrete edges | conforms | west_path, bench_plaza, front_corner | |
| Boardwalk deck and kerbs | deviates (P1 #1) | boardwalk | Boulder tips pierce the deck. |
| Boardwalk railings | conforms | boardwalk, riprap_bank, right_side | Open picket railings on both sides; you can see through them. |
| Boardwalk ramps | conforms | right_side, front_corner | Cycle path transitions onto the deck. |
| Rip-rap and bank grasses | deviates (P2 #6) | riprap_bank | Faceted, pale, sparse grass. |
| River | conforms | aerial, right_side | Flat clay water plane. |
| Planting beds: kerbs | conforms | front_corner | One mound intersects a kerb (part of P1 #2). |
| Planting beds: grasses, shrubs, flowers | deviates (P1 #2) | front, west_path, porch_northwest, glazing_close | Reads well from the air, primitive at pedestrian range. |
| Trees | deviates (P2 #4) | front, boardwalk | |
| Benches and bins | conforms | bench_plaza, front_corner, promenade_beds | Timber on dark steel; corten bins. |
| Footbridge: cambered deck, two piers, picket railings | conforms | footbridge, rear_side | |
| Footbridge abutments and landings | conforms | footbridge, rear_side, top | Minor kerb slits (P2 #8). |
| Far bank | conforms, residual (P2 #5) | footbridge, bench_plaza, top | Wooded belt rather than dense woodland. |
| Materials hierarchy | conforms, simplified | front, front_corner | Timber, dark metal, pale slab, dark sett, asphalt, corten are all distinct. |
| Aerial-scale finish against the park benchmark | conforms | front_corner, aerial | Composition and density read as an authored park. |
| Pedestrian-scale finish against the park benchmark | deviates (P1 #2) | front, west_path, porch_northwest | Planting primitives and a faceted canopy fall below the conservatory close-up finish. |

## 4. Camera validity

- All 18 delivered views are valid. No asset is clipped in a way that invalidates the view, and every target is legible.
- rear: the pavilion is only partly visible behind the north grove (P2 #13). The view still shows the north grove, the paths and the pavilion's position.
- footbridge and rear_side: the model tile edge and grey void are visible (P2 #12). The targets (bridge, piers, railings, bank) are legible.
- green_roof: the foreground is now clear of the plaza tree, so the roof reads unobstructed.
- The brief's view list names facade_close, architecture_close and glass_close. These files were not delivered, but the delivered set totals 18 as the brief states, and pavilion_close and glazing_close cover those roles.

## 5. Previous-version (v001) findings: are they resolved in the pixels?

1. **Sett borders: RESOLVED.** Flush dark-grey sett bands with cross-joints and a centre joint run along both promenade edges, cross it at intervals, frame the south plaza and edge the narrow paths (front, front_corner, promenade_beds, aerial). The pale raised ribs are gone. Residual P2s: band-end spikes (#7) and the missing linear-paver strips (#11).
2. **Planting as primitives: NOT RESOLVED. It remains P1 (#2), narrowed to pedestrian range.** The gem flowers and boulder shrubs are gone, and the aerial and mid-range density and colour drift now match the sources. Close up, the flower masses are draped pastel sheets and snowcaps, the shrubs are still faceted, the grasses are sparse straw blades, and one mound breaks through a kerb.
3. **Sedum roof as flagstones: RESOLVED to P2 (#3).** It now reads as a continuous ochre-olive planted mat, not plates. It is still coarse, banded and over-rust, and the claimed undulation is not visible.
4. **Solid railing panels: RESOLVED.** The boardwalk and footbridge have open picket railings, and the deck, planting and water show through them (boardwalk, riprap_bank, footbridge).
5. **Far bank not wooded: RESOLVED, residual P2 (#5).** About 30 trees in staggered rows with understorey and shore boulders. It reads as a tree belt rather than dense woodland.

Builder's P2 claims:
- Rip-rap is larger, mixed boulders with grass between: partly true. They are larger and mixed in size, but pale and faceted rather than grey-brown and rounded, and the grass is sparse (#6). The enlargement also caused P1 #1.
- Rounder, smooth-shaded crowns in three greens: three greens yes, smooth no (#4).
- Rear camera raised: partly (#13).
- green_roof camera clear: confirmed.

Holds from v001 that still hold: the plan and the pavilion's position and rotation; the promenade, south plaza, west crossing and cycle paths with yellow dashes; the lens-shaped kerbed beds; the cedar pavilion with its glazed south-east face, door, corner glazing and porch; the boardwalk along the rip-rap bank (apart from new defect #1); the footbridge on two piers; the benches and corten bins.
