You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/magasin/v006
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, corner_dome, marquise_sign, gilded_balconies, mansard_dormers, roof_domes, interior, rear_court)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a Belle Epoque department store on a corner with streets south and west around an inner light well: a double-height ground floor of continuous display windows under a glass marquise carrying a dark red sign band, four upper storeys of tall iron-and-glass bays with gilded balcony fronts between limestone pilasters, the top storey round-arched under a bracketed cornice, a zinc mansard with dormers, a curved glazed corner bay crowned by a glazed drum standing above the mansard and a ribbed glass dome with a lantern, and a smaller glass dome at the far end of the west face. The north and east faces are not visible in any source; signage text is not required in clay; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (glass corner dome over the curved glazed bay, gilded balcony fronts on iron-and-glass bays between limestone pilasters, marquise with sign band over continuous display windows, zinc mansard, second glass dome),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/magasin/v006/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, corner bay and dome (drum, ribs, lantern), bay rhythm and pilasters, gilded balconies, ground-floor display windows and marquise, arched top storey and cornice, mansard and dormers, second dome, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/magasin/v006/review/independent-review.md. Do not run the build.

This is version 6. The v005 review found 0 P0 and 2 P1, the same count as v004 (which stays the candidate): the corner drum still sat sunk in a zinc funnel (lower glass bowl-shaped, outer posts cut mid-tier at staggered heights with no plinth or sill) where the locked front shows the drum's lower tier fully exposed on the balustrade; the light-well dome's ribs did not join up (short radial rods stopping short of the lantern, arched rib pieces lifting off the glass, a separate faceted ring crossing them) where the locked top shows 16 continuous ribs from the base ring to a central cap. The drum burial has survived one targeted fix; say plainly whether it survives this second fix. The builder claims both are fixed: the corner roofs are cut back in a terrace ring round the drum, floored by the corner cornice and closed by a zinc skirt that follows the cut roof edges, so the drum's lower tier stands fully exposed with full-height posts from its stone plinth; the court dome has 16 continuous ribs from the ring beam up to a central zinc cap. To stay under the 4 MiB GLB limit the gilded fronts carry fewer relief elements and the court dome has no purlin ring. This is the second consecutive attempt after a review that did not lower P0 + P1. Verify each in the pixels; do not take the builder's word.
