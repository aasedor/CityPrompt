# Independent holistic review: clay-regency-stucco-terrace v002 (RLASM v6.1)

Reviewer: independent; judged only rendered pixels (18 renders, 4 phone boards) against the three locked sources (sources/front.png, sources/oblique.jpg, sources/top.jpg). Builder notes, metadata and counts were not used as evidence. Zoomed crops used for this review are in `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/indep-review-regency-v002-crops-x7q/`.

## 1. Verdict

VISUAL_REWORK_REQUIRED: the v001 orientation, mansard, capital, porch and rustication defects are fixed, but black open voids remain where coping meets corner pedestals (one of the v001 findings, so not resolved), and the matched front view is set too close and too low and is blocked by a tree, so it does not reproduce the source front.

Counts: P0 = 0, P1 = 2, P2 = 10

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | front_corner (hero oblique; SE balustrade corner and both near porch balconies), glass_close, facade_close, east_side, architecture_close, front_corner SW corner | Black rectangles or parallelograms sit on the top of every porch-balcony corner pedestal, and at the main-parapet corner pedestals (SE corner clearly; SW corner as a black dot; NE corner of architecture_close as a dark sliver). The glass_close zoom shows it is a void at the joint: the pedestal cap steps down and the returning balustrade coping stops short, which leaves an open slot that shows the dark hollow inside. The v001 finding "open balustrade and porch-coping corners" is therefore still visible. Pedestals were added, but the joint is still open. | The corner pedestal is a hollow or uncapped shell, or the coping rails end before the pedestal (mitre gap), so the top face does not close over the joint | Extend each coping rail into the pedestal (overlap by at least the coping depth) and give every pedestal a solid cap that overhangs the shaft on all four sides. Re-render front_corner, glass_close, facade_close and architecture_close and confirm there are zero pure-black pixels on any parapet or balcony top |
| 2 | P1 | front (matched to sources/front.png) | (a) The camera is far closer and lower than in the source (horizon at about y 770 of 1080; in the source it is near mid-frame), so the steep upward view hides the whole mansard: in front_roofline, only a balustrade against the sky and one stack show above the cornice. The source front shows the slate mansard, the dense dormers and the white party-wall fins prominently. (b) A foreground tree canopy covers the near corner's capitals, entablature, cornice and balustrade (x 320-800, y 180-470). (c) The framing is turned toward the south pediment end, which takes up about 60% of the frame. The source front shows the long porch front with three porches as the dominant face (about 75% of the frame) and the end face only as a short return. Proportions, rhythm and roofline cannot be compared one-to-one with the locked front. | Front camera not re-matched after the v002 facade remap: wrong azimuth, distance and height; street tree placed in the sightline | Re-seat the front camera on the long west or east front at the source's azimuth, so the long face dominates and the near corner is at about 3/4 of the frame width. Pull back and raise it to source eye-height and horizon so the mansard, dormers and fins read above the balustrade. Move or omit the corner street tree so no canopy crosses the facade above the first floor |
| 3 | P2 | giant_order, architecture_close, mansard_dormers | The Corinthian capitals are a crown of upright prism stubs with diagonal sticks for volutes. They read as Corinthian at envelope distance, but at the detail distance they look like blocky teeth, not acanthus | Low-segment procedural capital | Taper and curl the leaf prisms (two rows of bent leaves) and give the volutes a scroll profile |
| 4 | P2 | glass_close, porch_balcony, facade_close | Visible low-poly faceting: the giant-column base is an octagonal plinth and the porch shafts show flat faces | Low radial segment count | Raise the segments to 24 or more for shafts, bases and tori |
| 5 | P2 | porch_balcony, facade_close, east_side, front | Black tick slots at the foot of each ground-floor voussoir joint; black vertical slits between the abaci of paired porch columns under the porch entablature | Channel and joint cutters leave open ends; the paired abaci do not meet | Cap the channel ends; merge the paired abaci into one block |
| 6 | P2 | architecture_close, giant_order, mansard_dormers | The balusters are flat rectangular slats, not vase-turned balusters | Simplified baluster profile | Use a lathe-profile baluster (bulb plus neck) |
| 7 | P2 | top, front_corner, end_pediment | South mansard: one dormer on each side of the pediment, against two each side in the oblique and top sources. The party fins on the E/W fronts sit at about 27/53/79% of the length from the north; the source top has fins at the north corners and at about 1/3 and 2/3 | Dormer and fin layout tables | Add a second south dormer each side; shift the fins to the north-corner, 1/3 and 2/3 positions |
| 8 | P2 | top, rear_north, aerial | The inner mansard slopes to the court are bare. The source top shows small dormers and rooflights on the inner slopes, and a court that is longer north-south than the render's near-square opening | Inner slope not populated; court aspect | Add 2-3 inner dormers or rooflights per side; lengthen the court north-south by about 15% |
| 9 | P2 | rear, rear_side, rear_north, left_side | The north terrace is one continuous tan hipped block. It reads as a single building, not a row of brick terrace houses with parapets, party walls and stacks (source top) | One-box context massing | Split it into 5-6 house units with brick parapets or party-wall upstands at the stacks |
| 10 | P2 | front, facade_close, porch_balcony, top | Pavement railings are present, but no sunken basement area or basement windows can be read in any view | Area depth too shallow or not modelled | Drop the area by about one storey behind the railings with visible basement window heads |
| 11 | P2 | end_pediment, front_corner | The pediment is a flat gable against the hip. The source oblique shows a small slate roof running back from the pediment into the mansard. The tympanum relief is placeholder blocks | Pediment authored as a wall only | Add a short gabled slate roof behind the pediment; keep the clay relief as is |
| 12 | P2 | aerial, left_side, right_side | The asset fills only about 40-45% of the frame width; the detail is legible but small | Loose framing | Tighten the framing so the asset fills about 70% of the frame |

## 3. Source conformance checklist

| Item | Status | View(s) used |
|---|---|---|
| Silhouette | Conforms (oblique/top); deviates in the matched front because the mansard is hidden by the camera (F2) | front_corner vs oblique, aerial, top vs top, front vs front |
| Storey count | Conforms: rusticated ground plus two floors inside the giant order, then entablature, balustrade and mansard with dormers | east_side, left_side, facade_close vs front/oblique |
| Plan and light court | Conforms: near-square block, streets S/E/W, terrace on the N, central court with cream inner walls and windows. Court a little square (P2 F8) | top vs top, aerial (court crop) |
| Rustication | Conforms: deep horizontal channels and voussoir fans over the ground windows (black joint ends P2 F5) | facade_close, porch_balcony, east_side |
| Giant order (columns, capitals, rhythm) | Conforms: fluted engaged columns between every bay, foliated capitals with volutes, single columns near each corner. Capital finish crude (P2 F3) | east_side, giant_order, architecture_close vs front/oblique |
| Entablature and cornice | Conforms: architrave, frieze, modillion cornice continuous round the block and under the pediment | giant_order, end_pediment, architecture_close |
| Balustrade and pedestals | Deviates: pedestals over the columns and at the corners are present, but the corner pedestal/coping joints are open voids (P1 F1); balusters are slats (P2 F6) | architecture_close, front_corner, east_side |
| Porches and balconies | Conforms in programme: three paired-column porches with balconies on each of the E and W fronts, one under the S pediment. Deviates in finish: open coping voids on the balcony corners (P1 F1) | east_side, facade_close, porch_balcony, top |
| End pediments | Conforms: central pediment over the giant order on the south end with a porch below, as in the oblique and top (no roof behind it, P2 F11) | facade_close, end_pediment, front_corner |
| Windows (sizes per floor, balconettes, heads) | Conforms: tall first-floor windows with cornice heads and iron balconettes, shorter second-floor windows, deep reveals and glazing bars | glass_close, east_side, interior |
| Mansard (dormers, fins, stacks, flat top) | Conforms: about one-storey slate mansard, dense dormers on the E/W fronts, white party-wall fins with stacks, ridge ring and inner slopes to the court. Dormer/fin layout deviations are P2 (F7, F8). Not legible in the matched front (F2) | mansard_dormers, rear_side, top, rear_north, left_side |
| Areas and railings | Partially conforms: iron railings along the pavements; basement areas not legible (P2 F10) | front, facade_close, porch_balcony |
| Streets and trees | Conforms: streets S, E, W with pavements, street trees and lamps (one tree badly placed in the front view, F2) | top, aerial, front |
| Terrace houses north | Partially conforms: present, windowed, one continuous roof with stacks, but reads as one block (P2 F9) | rear, rear_side, rear_north |
| Materials hierarchy | Conforms: cream stucco throughout, blue-grey slate mansard, black ironwork, white fins and stacks with terracotta pots, tan brick terrace | all views |

## 4. Camera validity

- front: problematic (P1 F2). The tree canopy covers the near corner's order, entablature and parapet. The camera is too low and close for the mansard to show, and the framing favours the end face against the source's long front.
- rear: legible. The view is mostly of the north terrace, which correctly screens the party side. Acceptable because no source shows the north side.
- aerial, left_side, right_side: valid but loosely framed (P2 F12).
- end_pediment: a minor tree edge at bottom-left; the target is legible.
- All other views (front_corner, top, rear_side, facade_close, architecture_close, glass_close, porch_balcony, giant_order, mansard_dormers, east_side, interior, rear_north) are valid: target unobstructed, nothing clipped, legible.

## 5. Previous-version (v001) findings: status in the pixels

| v001 finding | Status in v002 pixels | Evidence |
|---|---|---|
| P0: facade programme rotated 90 degrees (pediment belongs on the south end; porches, fins and dense dormers on the E/W fronts) | Resolved | top: porches on E/W at three positions each, fins on E/W, pediment and porch on S. front_corner matches the oblique: pediment face on the left, long porch front with fins on the right, terrace at the far end |
| Mansard far too low, large flat top, no inner slopes to the court | Resolved (inner slopes bare, P2 F8) | left_side elevation: mansard about one storey tall. top, rear_north, aerial: ridge ring with inner slopes falling to the court |
| Capitals reading as Tuscan | Resolved (finish P2 F3) | giant_order, architecture_close: foliated bell with corner volutes under a square abacus |
| Porch columns reading as square piers | Resolved (faceting P2 F4) | porch_balcony, facade_close: round shafts with bases |
| No paired-column porch under the pediment | Resolved | facade_close: 2+2 round columns under a balcony, centred under the pediment |
| Open balustrade and porch-coping corners | Not resolved (P1 F1) | Corner pedestals now exist, but black voids remain at the pedestal/coping joints on every porch balcony and at the main-parapet corners (glass_close, facade_close, front_corner, east_side, architecture_close) |
| Windowless terrace-house box with roof gaps | Resolved (reads as one block, P2 F9) | rear, left_side: windows on all terrace faces; one continuous roof with stacks, no gaps |
| Rustication too faint | Resolved | facade_close, porch_balcony: deep shaded horizontal channels and voussoir fans |
