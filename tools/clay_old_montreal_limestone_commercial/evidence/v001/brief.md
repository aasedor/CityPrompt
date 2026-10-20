You are the independent holistic reviewer for one RLASM v6.1 architectural-clay candidate.
You did not build it. You have no relationship with the builder. Be adversarial and specific.

Candidate directory: /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/oldmtl/v001
- Locked sources (the only truth): sources/front.png, sources/oblique.jpg, sources/top.jpg
- Renders: renders/*.png (18 views; whole-envelope: front, front_corner, aerial, top, left_side, right_side, rear, rear_side;
  details: facade_close, architecture_close, glass_close, portico, dome_drum, end_pavilion_arches, balconettes, east_door, long_facade, roofs_dormers, west_range, interior, rear_north)
- Phone boards: boards/*.png

Rules (from the method):
- Judge only rendered pixels against locked source pixels. Ignore metadata, counts, hashes and the builder's notes as proof.
- The building is a domed public-market hall of grey limestone ashlar in Old Montreal (Bonsecours type), on a city block with streets, sidewalks and cobbled squares (the top view governs the plan): a long three-storey hall over a low basement in two offset ranges, the west range in line with a square dome block and the east range stepped south of it by a full range depth; regular bays of six-over-six windows on three floors with stone sills and flat lintels, small barred basement vents, dressed pilaster strips, a plinth, sill bands and a modillioned eave cornice; low hipped slate roofs with stone chimneys, small vent dormers on the court slope and a skylight; at the east end an end pavilion, flush with the range, with round-arched windows and radial fanlights on all three floors, keystones, iron balconettes on the first floor, an eaves balustrade on both long sides and a full-width pediment with a blind oculus on the east front, and a corniced square door on consoles with steps in the middle of the east face; on the south street a tetrastyle Tuscan portico on a stepped podium with an entablature, triglyphs and a pediment with an oculus, in front of an arched doorway at the west end of the east range; over the dome block a square stone attic with sunk panels and corner pedestals with urns, a drum of sixteen round-arched windows between engaged columns, a ribbed silver tin dome and an open lantern with a cupola and cross; a flat-roofed three-arch porch with a balustrade on the north front of the dome block; trees on the south sidewalk, the south-west cobbled square and the north sidewalk. The north and west fronts, the dome block east face and the porch are not visible in the front or oblique; because the plan follows the top view, the dome stands about 30 m behind the south portico and is largely hidden by the near pavilion at street level in the front view; judge faces that no source shows only for coherence with the visible grammar, not for fidelity.
- This is clay: untextured source-palette colours. Do not fail it for missing photoreal texture, people, vehicles beyond simple massing, or
  signage text. Do fail it for wrong geometry, wrong rhythm, missing or extra storeys, missing identity elements (long grey limestone market hall with a pedimented Tuscan portico, a silver ribbed dome on an arcaded drum over a square attic, and an arched east end pavilion with iron balconettes, an eaves balustrade and a pediment),
  openings without visible depth/returns, floating or intersecting parts, elements that read as a different building, or an invalid camera
  (target occluded, asset clipped, nothing legible).
- Severity: P0 = source-identity, topology, envelope, opening, contact, program, camera or provenance defect that invalidates the candidate.
  P1 = clearly visible fidelity, material, optical, finish, landscape or coherence defect that blocks production-quality approval.
  P2 = polish only.

Open EVERY render at full resolution with the Read tool, and the three sources, before writing anything. Compare matched roles
(front vs front, oblique vs front_corner/aerial, top vs top/aerial). Then inspect every detail view for contact and depth.

Write your review to /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/oldmtl/v001/review/independent-review.md as markdown with exactly these sections:
1. Verdict: one of PASS_ZERO_P0_P1 / VISUAL_REWORK_REQUIRED, with one sentence.
2. Findings table: | # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |  (list every P0 and P1; P2s briefly)
3. Source conformance checklist: silhouette, storey count, plan (offset ranges, dome block, portico, porch), limestone coursing, window tiers (vents, three tiers of sashes, pavilion arches and fanlights), pilaster strips, plinth, sill bands and eave cornice, end pavilion (balconettes, balustrade, pediment, oculus, east door and hood), portico (podium, steps, columns, entablature, pediment), attic (panels, pedestals, urns), drum (arched windows, columns, entablature), dome (ribs, profile), lantern, cupola and cross, roofs (hips, gable ends, chimneys, vent dormers, skylight), north porch, streets, squares and trees, materials hierarchy. Mark each conforms / deviates / not visible, with the view you used.
4. Camera validity: any view where the target is occluded, clipped or illegible.
Do not modify any file other than /tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/dev-artifacts/CityPrompt/oldmtl/v001/review/independent-review.md. Do not run the build.
