You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sand/v004
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, clock_tower, portal_arch, gables_pinnacles, east_side, roofs_court, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a Richardsonian Romanesque civic block of rock-faced buff sandstone round a square light court on a city block with streets on all four sides (the top view governs the plan): four storeys over a rusticated basement; corner pavilions stepping forward of the wings and rising into steep slate pyramids, each with a coped gable and pinnacles on its outward faces; steep slate hipped roofs over the wings; small basement windows, paired rectangular first-floor windows, tall round-arched second-floor windows and third-floor arcades of small arches, with deep reveals and stone string courses; a deep round-arched portal in the south-west pavilion; at the middle of the east front a square clock tower projecting from the wing, with tall lancets, clock faces on four sides, a belfry arcade, round corner turrets with copper caps and a tall copper spire; sidewalks, streets and trees. The north and west fronts are not visible in the front or oblique; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (rock-faced sandstone Romanesque block with round-arched arcades, gabled corner pavilions under slate pyramids and a clock tower with turrets and a copper spire),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sand/v004/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, plan, court and pavilion projection, sandstone coursing, window tiers (basement, paired, arched, arcades), string courses and eave cornice, gables and pinnacles, roofs (wing hips, pavilion pyramids, cross gables), portal, clock tower (projection, lancets, clocks, belfry, turrets, spire), streets and trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/sand/v004/review/independent-review.md. Do not run the build.
This is version 4. The v003 review found 0 P0 and 1 P1 (v002: 1 P0, 2 P1, all three fixed in v003): the clock tower too short and squat — its top cornice below the corner-pavilion pyramid finials, the clock faces below the pavilion apexes, the whole tower about 1.3x the pavilion height against about 2x in source front, and a broad four-sided pyramid spire with height:base about 1.0 where the source has a slender octagonal or conical copper spire. The builder claims it is fixed: the tower crown rises from 26.0 m to 36.5 m, the clock-stage string course sits at 29.5 m with the clock faces centred at 31.4 m (above the 27.3 m pavilion pyramid apexes) and a five-arch belfry above them; the spire is an octagonal copper spire on an octagonal stone base rising to 48.7 m (height about 1.7x its base) with a finial, between four corner turrets with taller copper caps; the shaft carries a cluster of four tall lancets on the east face and paired lancets on the north and south faces; the east_side, clock_tower, front and front_corner cameras are re-aimed so the whole tower and spire stay in frame. Verify each in the pixels; do not take the builder's word.
