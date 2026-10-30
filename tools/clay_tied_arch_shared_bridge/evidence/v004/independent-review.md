# Independent tied-arch v004 architectural-clay review

**Decision: visual rework required. P0: 0; P1: 1; P2: 6.**

Candidate: `clay-tied-arch-shared-bridge-clay-v004`

Exact GLB SHA-256: `1db1801d3a8d7fbcd5e96a694838f5eaa1e60ff6a7deea8fa002d650ed0a28ff`

Holistic review performed: true. Category-closure-only review: false. Architectural-clay pass: false. No keeper, runtime or publication approval.

All three exact references, all 20 original full-resolution reimported-GLB renders and all four regenerated full-resolution phone boards were opened directly. Exact inspected-file SHA-256 values, byte sizes and dimensions are recorded in the companion JSON.

## Blocking finding

### P1-01: missing outer quay guard returns

Both raised compact quays lack guard returns across their outer transverse edges beside the stairs. The broad paved landing areas terminate at exposed approximately 3.3 m drops. Longitudinal quay guards and stair handrails do not close these platform edges. The newly isolated context is visibly incomplete as a standalone pedestrian crossing. This is an obvious missing guard category, independent of engineering/accessibility certification.

Strongest evidence: `renders/west_approach.png` and `renders/east_approach.png`; also visible in whole views and `boards/phone-03-details.png`. The generator only adds the y=+/-7.85 long-edge quay guards.

Required correction: Preserve v004. In a bounded new version add outer transverse quay guard returns, sharing the existing plan transform, from each long-edge guard to the corresponding upper stair handrail. Keep only the actual stair corridor open. Reimport the new exact GLB, rerender all mandatory views and phone boards, and obtain a fresh holistic review.

The proposed local x=+/-25.95 returns leaving y=-4.73..-0.57 open target the observed omission; joining contacts and clear stair access still require visual verification.

No other P0/P1 was found after the complete source/render/board inspection.

## Holistic findings

- **exact identity and programme (closed for architectural clay):** Twin inclined silver-grey tied arches, cross ties and thin hangers, red cycle lane, wider pale footway, continuous dividing planter, bridge-side guards and brick-coloured compact quays retain the exact variant identity.
- **opposite end skews and longer south tie (previous P1 closed):** Top and aerial evidence show opposite end skews and the longer south tie, rather than the previous uniform parallelogram shear. The single trapezoidal plan map is applied to bridge, quays, bearings and inferred approaches.
- **physical support contacts and whole assembly (closed for architectural clay):** Arch springings meet their quay plinths; deck bearings/shelves meet the compact quays. No obvious floating carry parts, major missing deck sections or large contact wedges appeared across the whole and underside views. No roof is part of this open bridge.
- **declared inferred approach stairs (stairs connect; landing guards remain P1):** Both stairs meet the raised paved quay and prepared grade. The approach is a declared pedestrian inference, and the cycle lane ends on raised quays with a dismount limitation. No accessible/cycle approach certification is inferred.
- **camera and evidence coverage (complete for this review):** All three exact sources, all 20 full-resolution original reimported-GLB renders and all four regenerated 1080x1920 phone boards were directly opened and inspected. Deterministic metadata did not substitute for pixel inspection.

## P2 follow-up

- **P2-01 planting detail:** Repeated angular foliage clumps read more coarsely than the fine dense grasses and shrubs in the locked source. The continuous planter identity and lane division remain legible.
- **P2-02 guard infill fidelity:** The guards use visibly thicker picket infill than the finer source mesh/pickets. The bridge-side guards remain permeable and continuous in the inspected evidence.
- **P2-03 clay material scope:** Uniform source-palette clay omits steel weathering and brick/paver bond texture. This is within the declared architectural-clay scope and does not support a textured keeper claim.
- **P2-04 arch and hanger detailing:** Faceted arch segments, small joints and simplified hanger fittings remain visible at close range. No gross open contact or detached arch/hanger assembly was apparent.
- **P2-05 bounded landscape presentation:** Flat dark water and hard canal/module cutoffs are apparent in whole views. City blocks and extending banks are intentionally omitted; external site integration and canal continuation remain untested.
- **P2-06 render framing and surface readability:** Some whole/end views and phone-board panels leave the model small on the neutral canvas; deck shadows soften lane/planter detail. Phone board 01 compares source top with an oblique aerial, although a separate true top render is available. Complementary full-size views permit the holistic review.

## Provenance and limits

The exact candidate GLB matches the build report. All three candidate source copies match their current locked catalogue originals; all ten copied as-built scripts match the prework manifest. The companion JSON records their exact hashes. The build report identifies actual optimized GLB reimport renders without geometry/material replacement. I did not independently regenerate these images.

The former plan-shape P1 is closed in this candidate: opposite end skews and the longer south tie appear in the top/aerial evidence, and one plan transform covers the assembly. That closure does not override the remaining landing-guard P1.

No runtime import, placement, reload, editing, traversal, slope or external-approach checks were performed. This review does not certify engineering, guard regulations, accessibility or cycle access. The inferred pedestrian stairs and compact banks are teaching assumptions. Preserve v004; review any v005 as a new exact candidate.
