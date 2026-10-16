You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/parkade/v003
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, tower_crown, retail_base, vehicle_entry, roof_deck, stair_penthouse, interior, north_lane)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a five-level campus parking structure on a corner with streets south and east: a red-brick frame of piers and a parapet holding four open parking decks over a ground storey of glazed retail bays, brick spandrels on the south face and pale precast spandrels on the east face, dark horizontal guard screens in each deck opening; at the south-east street corner a square stair tower in a dark bronze frame rising above the parapet, its faces divided into strips of precast panel, glass and vertical louvres, with a bronze band at the first deck and a louvred crown with a patinated coping; a larger tower of the same kind at the north-east corner, a narrow glazed stair tower at the west end of the south face; an open roof deck with stall stripes and light poles round a dark ribbed lift overrun, rooftop units and an open stair well with a guard rail; vehicle entry and exit on the east street. The north and west faces are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (brick-framed open parking decks with spandrels and screens, bronze louvred corner stair tower above the parapet, glazed retail base, roof deck with lift overrun and stair well),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/parkade/v003/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, level count, bay rhythm and piers, spandrels (brick south, precast east) and screens, retail base, corner tower (strips, band, crown, coping), north-east tower, west glazed stair, roof deck (stripes, poles, overrun, stair well), materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/parkade/v003/review/independent-review.md. Do not run the build.
This is version 3. The previous independent review (v002) found: P1 the two southern east-face deck bays read pale and open where the source shows dark mullioned ribbon bands; P1 the south face's open-deck zone split by two extra brick piers into three punched bays where the source has one wide brick-framed opening with recessed concrete columns and pale concrete spandrel upstands, with brick (not precast) between the ribbons and the curtain wall running through deck 1 where the source has a punched window. P2s: pale patina, bronze slightly light, split SE corner posts, black stair well, light lift overrun, deck-1 lintel bands, interpenetrating cars, thin west-stair head, tree-occluded close-ups. The builder claims: dark bronze screens with close vertical mullions in the two southern east-face bays on every deck; the south open-deck zone is one wide opening per deck with a pale upstand and recessed concrete columns at the old bay lines; pale precast panels between the ribbons over a brick deck-1 band; the curtain wall starts at deck 2 over a punched deck-1 window; darker bronze, patina and lift overrun. Verify each in the pixels and record for each v002 finding whether it is resolved.
