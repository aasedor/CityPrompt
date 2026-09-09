# Currie student community trial — 8 September 2026

## Scope and local project

Student-style browser trial, including boundary editing, Site DNA, compact
frontages, plot resizing, height changes, park access and connected streets.
All project mutations were made through the visible application controls.
API reads collected saved geometry and render evidence; they did not construct
the community behind the UI.

- Checkout: `C:/dev/CityPrompt-building-next3`
- Branch: `codex/currie-student-render-trial`
- Project: **Currie Commons - student community trial**
- Local URL: `http://127.0.0.1:5177/projects/bb4a6a7b-479f-45a1-b7f2-94f50b84e696`
- Evidence: `C:/dev-artifacts/CityPrompt/currie-student-trial-2026-09-08/`
- Saved plan: one boundary, eight building plots, two parks and two streets.
  Two widened infill plots each contain two complete houses.
- No catalogue assets published and no push performed for this initiative.

The public-road connection meets the existing street along the east side of
the site. Northern buildings face the local street; buildings beside the park
face the shared street. The initial dispersed layout was deliberately revised
after the user's feedback. Short entrance walkways were then saved for all
eight building plots. A repeated-house plot currently has only one anchor;
this is not a claim that every individual door has a correct connection.

## Student actions and findings

| Action | Result |
| --- | --- |
| Draw an empty Currie site and place catalogue objects | Saved successfully, but rough-ground validation initially hid buildings while the toolbar said 3D saved. |
| Review ground | A deliberate prepared redevelopment level made the trial usable. This is a flat-site workaround, not a solution for terrain-following parks. |
| Generate Site DNA | Completed after repairing the isolated local worker routing. DC dominates; missing height/FAR information remains missing. |
| Change a boundary vertex | Saved and survived reload. DNA is invalidated on the server, but the open panel can retain old results until reload. |
| Bring buildings closer to streets | Saved; whole-plot collision bounds matter, including setbacks around the visible model. |
| Widen an infill plot | 30 m and 24 m plots each fit two intact homes. A 42 m trial correctly hit a neighbouring plot. |
| Enlarge neighbourhood park | Width 40 → 54 m saved, retaining 35 m depth and an adapted layout. A 40 m depth conflicted with a house plot. |
| Increase the mid-rise height | Five → seven floors falls back to planned massing. Restored five floors / 20.43 m to retain the detailed asset. Advance explanation is needed. |
| Draw a street through a park | Rejected by overlap validation. Automatically cutting a corridor through park paths and amenities is not implemented. |
| Extend road to existing public street | Exposed backend geometric tolerance and prepared-ground bugs; fixed and saved. |
| Add a crossing | Explicit crossing saved on the shared street. This does not establish accessibility or engineering compliance. |
| Join shared street to local street | Route endpoint edited. Visual T-junction refinement is still needed; near alignment alone was not a reliable student workflow. |
| Connect house entrances | Northern plots work with local-street sidewalks; shared-street plots work after the flush-edge access fix. |
| Reload | Compact geometry and saved entrance settings remained. |

## Source fixes

1. Added a visible, touch-sized **Move selected object** handle. Dragging the
   model body could pan the camera instead; the explicit handle was exercised
   through the browser and its saved move survived reload.
2. Overlap messages identify the conflicting catalogue object or named plot.
3. Boundary-specific 409 responses preserve the actual cause instead of
   incorrectly reporting that another session changed the drawing.
4. Missing decorative foliage images use a bounded cached procedural fallback
   instead of throwing out the whole globe. The three missing authored texture
   files still need an asset-delivery audit; this fix does not replace them.
5. Public-road buffer validation now applies its existing 15 cm tolerance at
   the end caps too. The actual UI request differed by micrometres and was
   previously rejected. Tests still reject a one-metre displacement.
6. A road extending out of a prepared site keeps its inside stations at the
   declared site level and blends to measured ground over ten metres outside.
   Landscape/follow-terrain sites are excluded. This is conceptual grading,
   not a validated accessible or construction-ready gradient.
7. Sidewalk targets show catalogue street names, with ordinals for duplicates.
8. The yield-street pilot's paved flush edges can receive park and building
   approaches. Ordinary road shoulders are not treated as sidewalks. Vehicle
   bands, obstacles and the site boundary still prevent inappropriate links.
9. Park access can use the inside portion of a street that legitimately
   continues to a public road; the access corridor must still stay in the site.
10. Street-view cameras and video route samples use authored ground heights.
    The free preview exposed a camera underneath the prepared pad; a repeated
    preview after the fix showed the street, benches and building at eye level.
    Explicit terraces and measured park surfaces take precedence; retained
    terrain and landscape sites keep their measured ground.
11. Draft video captures now report only the complete geometry bundles sent
    to the server. Previously, six temporary semantic passes were counted as
    six complete checkpoints despite sending none, causing a free-check error.
    The corrected Draft aerial route passed preflight in the browser.
12. Video results now call the numerical metric **Image similarity**, omitting
    the reassuring `stable` verdict from the result badge. The comparison
    tooltip explains that unchanged surroundings can dominate the score.

## Render evidence

Authorized finite batch: three aerial images, three street views, two videos.
The local server's inherited daily cap was exhausted by earlier trials; it was
raised to 2,500 app tokens for this isolated test server only. This does not
change production limits or authorize more provider calls.

- **Charcoal aerial:** provider succeeded in about 126 seconds. Building
  identity changed: a modern house became a pitched-roof house. Geometry checks
  returned the original 3D source and retained the unverified AI original.
- **Risograph aerial:** provider succeeded in about 108 seconds. The style is
  convincing, but a garden became a house and building identities/counts are
  not trustworthy. Again returned the source with the AI original retained.
- **Wood Block aerial:** provider succeeded in about 103 seconds. It produced
  a woodcut-like illustration rather than a physical wooden scale model. The
  context registration check returned the original source. Camera and broad
  layout are closer than the Charcoal trial, but the finish remains unverified.
- **Documentary street:** provider succeeded in about 95 seconds (105 seconds
  end to end). On 2026-09-08 Andrew explicitly approved this image as very close
  to the intended product standard. Saved AI original:
  `355f6261-072b-49f5-ba7b-7f23a0d28ff3`. This is the positive calibration
  example: preserve recognizable building identity, placement and street/park
  relationships while allowing substantial photographic finishing. Its
  automated `review_required` status must not be interpreted as human rejection.
- **Watercolour street:** provider succeeded in about 127 seconds end to end.
  House, park and shared-street relationships are recognizable; paper texture,
  painted foliage and paving demonstrate that large pixel differences alone
  do not make an illustration unsuccessful. Human approval remains specific
  to the Documentary example above.
- **Survey street:** provider succeeded in about 94 seconds (112 seconds end
  to end). The three house fronts, sidewalk and street remain recognizable.
  Browser verification showed the AI image selected first, saved, with the
  source thumbnail available for comparison under the corrected UI.
- **Omni video:** eight-second Draft aerial route completed in about 84
  seconds. Saved attempt `02df0ff1-1cc6-499d-8015-c64a2dcc8fba`.
  The automated score was 90.5/100, labelled stable. Inspection of frames at
  0/2/4/6 seconds showed extra buildings and roads inside the site despite
  stable surrounding Google context. Do not treat this score as proof of
  design fidelity. Draft lacks instance control maps, so whole-frame image
  similarity can be dominated by unchanged surroundings. This route also
  stayed too distant to inspect the design closely.
- **Seedance Mini video:** eight-second Draft aerial route with preview plus
  three reference views completed and saved as
  `611b3e32-c68c-4804-8b16-185a35cc5dfb`. Score 81.2/100. Inspected frames at
  0/2/4/6 seconds retain the original site layout much more closely than Omni,
  but offer little visual improvement over the 3D source. Both video trials
  were too distant for a useful close architectural inspection; the three
  street image trials provide the close-view evidence.

Batch complete: six paid image calls and two paid video submissions. All
returned and were saved. No paid retries were made. The UI estimated $0.80 for
Omni and $1.98 for Seedance; image calls used 83 app credits each. These are
estimates/app accounting, not a reconciled provider invoice.

Final reload confirmed all 13 zones, all eight saved building entrance targets,
12 saved image records (six AI originals plus six returned comparisons), and
two complete videos. `53-final-community.png` records the final compact layout.
Unused prepared-site margins remain visible and are not claimed as finished
landscape design.

The source screenshots remain the record of the designed geometry. AI images
are illustrations, not certified geometric replicas. Andrew's approved
Documentary image establishes the acceptable visual target. Obvious park/house
swaps are still defects; realistic materials and vegetation are welcome.

### Review presentation correction

The app previously selected its source fallback and hid AI originals by
default. The student now sees the saved AI illustration first when a check
returns a source fallback, with the original 3D view available for comparison.
The project gallery and shared viewer expose AI originals. Automated check
details remain available but do not reject or delete an illustration. This is
a presentation change, not a claim that failed geometry checks have passed.
No provider safeguards or source-capture validations were removed.

## Remaining product priorities

1. Keep students' objects visible and clearly explain ground readiness on a
   newly drawn rough site; do not require a flat prepared pad as a workaround.
2. Snap edited road endpoints to compatible existing centreline junctions and
   visibly preview the joined intersection, including continuity of curbs,
   sidewalks, crossings and planting interruptions.
3. Give each repeated native house its own entrance anchor and preview the
   exact doorway before saving. Current plot-centre defaults are approximate.
4. Provide an intentional park-corridor operation that replans amenities around
   a street/path, rather than disabling collision checks.
5. Explain detailed-model height limits before replacing a model with massing.
6. Tighten render identity handling; attractive style alone is not fidelity.
   Investigate conflicting reference attachments and park/building swaps.
7. Improve Site DNA's uncertainty and stale-result messaging. A mapped land-use
   mix is not permission to develop and straight-line proximity is not access.
8. Show the rejected source checkpoint in low-flight video preparation. The
   current edge/colour heuristic reports clipped/blank foreground without
   showing the student its evidence. The low-flight trial stopped before a
   paid call. Changing camera modes also clears the route and requires redrawing.
9. Describe video scores as image similarity, not a guarantee of object
   identity. Include proposal-focused evidence and useful close source views.

## Verification

- 40 focused connection/editor/park-access tests passed.
- 91 focused geometry, saving, foliage, street-ground and section tests passed.
- Eight backend public-road-connection tests passed.
- Frontend TypeScript check passed after the production changes.
- Three camera-ground regression tests passed, followed by another successful
  TypeScript check.
- 28 focused image-result/presentation tests passed (including a subsequent
  additional regression for the AI-first street result).
- 11 video route/profile tests passed; TypeScript check passed again.

Screenshots, render files, runtime scripts and local database contents remain
external trial evidence. Pre-existing tower thumbnails, publication registry
edits and generated tower packages are unrelated work and are excluded from
this initiative's source checkpoint.
