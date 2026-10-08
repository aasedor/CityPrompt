# City Prompt button review for student final projects

Expanded review: [Complete button audit](COMPLETE_BUTTON_AUDIT_2026-10-07.md), including all 535 button definitions and a full control inventory. This report records the earlier, narrower inspection; later findings and runtime observations are in the expanded report.

7 October 2026 · Recommendations for Andrew

City Prompt should keep its planning, walking and presentation capabilities while reducing duplicate entry points and technical choices in the everyday student interface. The strongest cleanup opportunities are the duplicate Help and Guide buttons, the second project stepper, generic drawing modes that resemble zoning tools, and the large initial selection of render styles.

This review recommends interface changes only. Application source was not changed, and nothing was pushed or deployed.

## Student value and review scope

The useful final-project sequence is to understand a real site and its policy context, propose land uses, design a connected community, explore it at walking height, and present the proposal with images and a reasoned explanation. Keep controls that help students make or explain these decisions, recover their work, or create submission material. Put technical diagnostics and experimental generators behind a clearer advanced entry point.

This follows Andrew's described workflow and the repository's [student studio brief](STUDENT_STUDIO_IMPLEMENTATION_PLAN.md) and [release exercise](STUDENT_READY_RELEASE_PLAN_2026-09-23.md). The student-inspired catalogue round includes live/work, courtyard housing, student residence, co-housing and garden hotel proposals; [those programme examples](UBST_RLASM_BUILDING_ROUND_2026-10-07.md) reinforce the value of mixed uses, landscape and pedestrian connections. They do not establish the course marking rubric.

The reviewed build is the local preview on port 5183, at source revision `3a1f30b77`. It is not an audit of the deployed Cityprompt.ca build. No usage analytics were examined: “lesser used” here means secondary or advanced controls, rather than measured button frequency.

Evidence labels in the tables:

- **B**: opened or activated in the browser and inspected. This establishes the visible interaction, not a complete downstream acceptance test.
- **S**: traced in source. The associated generation, edit, download or external action was not executed during this review.

## Changes to make first

1. **Keep one Help entry point.** Help and Guide both open the same tutorial. Retain Help in the project toolbar and offer contextual tips in the drawing panel; remove the duplicate Guide button.
2. **Use one student workflow.** Keep Site → Design → Present. Remove the second Site → Plan → 3D → Render stepper from the student interface and give its remaining advanced operations a separate home.
3. **Remove Generate to 3D.** Andrew confirmed that there should be no such button: the scene is already generated in 3D. Remove it from the student interface rather than renaming or relocating it. Preserve any internal compilation needed for automatic updates and older projects; designing and walking should lead directly to presentation.
4. **Consolidate generic area drawing.** Remove the Residential and Development Area shortcuts from the standard student menu after preserving access to existing drawings. Use the zoning studio for proposed land uses and the catalogue or a single custom-building entry for architecture. Put Water and custom park drawing with Parks.
5. **Make presentation controls shorter.** Show a small initial style set and an obvious free 3D export. Keep the other styles in “More styles” and retain their examples.
6. **Keep review tools available when relevant.** Ground and entrance review belong in advanced/contextual panels, where they already largely reside. Surface them when a terrain or connection problem occurs, rather than making them ordinary prerequisites to walking or rendering.

Removing an entry point should not delete stored objects, older recipes, recovery history or support tools. Generate to 3D is an explicit removal requirement; the other changes remain recommendations for the subsequent interface cleanup.

## Drawing and viewing controls

Source: [drawing toolbar](../frontend/src/components/viewer/SitePlannerToolbar.tsx), [project workflow and handlers](../frontend/src/features/projects/ProjectViewPage.tsx), [globe controls](../frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx), [custom builder](../frontend/src/features/legoAssembly/LegoBuilderPanel.tsx).

| Control | What it does | Recommendation and student value | Evidence |
| --- | --- | --- | --- |
| More Tools | Opens optional drawing modes and viewing/review controls. | **Keep, reorganize.** Group viewing, measurement/recovery and advanced creation; the current mixture is difficult to scan. | B, S |
| 3D Models On | Shows or hides generated building models. It is separate from the original Google context. | **Keep in viewing tools.** Useful for checking the underlying proposal and diagnosing obscured drawings. Use a stable “Show 3D models” toggle label. | B menu, S handler |
| Clean 3D / Plan Overlay | Toggles editable planning polygon overlays; it does not clear Google buildings. The text changes with the current state. | **Keep, rename to “Show planning outlines.”** A clean presentation and an editable plan both matter; the current wording does not make the action clear. | B menu, S handler |
| Review ground | Reviews prepared terrain, offers existing-terrain mode or an explicit redevelopment level, and optional measured edge closure. | **Keep, contextual.** Terrain failures can spoil the entire proposal. Put advanced datum numbers behind a disclosure and explain the effect before applying. | B, S |
| Review entrances | Lists building approaches and missing entrance/sidewalk selections, then offers Select and review. | **Keep, contextual.** Useful for pedestrian connections and plausible access. It must not become a button students have to use to enable walking inside buildings. | B, S |
| Site Boundary in More Tools | Selects an existing boundary, or begins drawing one. | **Remove the duplicate shortcut from the standard Design menu.** Keep boundary drawing/review in Site, with an “Edit site” link if necessary. | B menu, S handler |
| Master Plan | Selects the boundary and opens its properties; optional AI site analysis contains Site DNA and subsequent scenario controls. | **Move and rename.** “Optional site analysis” in Site is clearer. Keep AI scenarios advanced so students retain responsibility for the proposal. | B entry, S subsequent actions |
| Street View | Activates a map pin for a street-level camera; the associated panel supports direction and rendering. | **Keep, relabel “Set street-level camera,” near Present.** It is useful for framing an image but is distinct from walking. | B activation, S camera/render panel |
| Measure | Activates point-based distance measurement. | **Keep in More Tools.** Supports block sizes, path lengths and a defensible sense of scale. | B activation, S measurement |
| History | Shows persisted per-zone change records and zone-specific Undo/Redo. | **Keep, rename “Version history.”** Valuable recovery and process evidence; ordinary Undo/Redo do not replace this view. | B, S |
| Draw custom building | Starts a building polygon drawing mode rather than picking a catalogue model. | **Keep under Buildings → Custom.** Useful for a proposal beyond the catalogue. Explain which representation and edits that custom object supports. | B menu, S handler |
| Draw custom park | Starts a green-space polygon drawing mode. | **Keep under Parks → Custom outline.** Supports irregular spaces; distinguish it from reshaping an existing catalogue park. | B menu, S handler |
| Parks / Plazas in More Tools | Starts generic green-space or plaza area drawing; the plaza shortcut maps to the internal parking zone type. | **Remove the duplicate menu row; retain both choices in Parks.** Public space matters, but these controls should not compete with the catalogue entry point. Review plaza naming and downstream behaviour before consolidation. | B menu, S handler |
| Residential | Starts a generic residential polygon with a building-development workflow. It does not select a Calgary bylaw district. | **Remove from the standard menu.** Students can use Buildings for architecture and zoning studio for official district selections. Preserve older projects. | B menu, S properties |
| Development Area | Starts a polygon with development-type and archetype selection. | **Move to custom/advanced creation.** It overlaps the clearer building workflow and can be confused with proposed zoning. | B menu, S properties |
| Water | Starts a water-area polygon. | **Keep with Parks and landscape.** Waterfronts, canals and stormwater features can add considerable project value; specify that this is an area tool, not the canal route tool. | B menu, S handler |
| Project steps & custom 3D | Expands a second four-step workflow and Generate to 3D. | **Remove the duplicate stepper and its Generate to 3D entry.** Keep Site → Design → Present as the student sequence. | B, S |
| Generate to 3D | Opens the builder, starts planning/assembly, and enables automatic compilation/rebuilding after initial planning. | **Remove.** Explicit requirement from Andrew: the scene already exists in 3D. Preserve necessary automatic compilation internally, without a replacement generation button. | B assembly entry, S automatic rebuild |
| Connections | Opens object access/connection editing. | **Keep with the selected object.** Connections to streets, sidewalks and paths are central to a realistic community. Consider a clearer object-specific label such as “Connect to a path.” | S |
| Terrace & path | Opens terrace/path editing for supported objects; unavailable for native parks. | **Keep contextual and advanced.** Useful on sloped sites, but irrelevant to many simple flat-site exercises. | S |
| More settings | Opens the fuller properties editor for a selected object. | **Keep collapsed.** Specialized edits add value without filling the initial object panel. Avoid repeating basic reshaping controls unnecessarily. | S |

Ground review correctly reported that this large review boundary exceeds the retaining-edge pilot's supported size/detail. Entrance review also reported missing selections and unavailable measurements for some models. Retaining those diagnostics is more useful than hiding the underlying limitations. Their recommendations are concept checks, not proof of accessibility or a surveyed grading design.

## Policy context and project submission

Source: [project panel composition](../frontend/src/features/projects/ProjectViewPage.tsx), [planning report](../frontend/src/features/studentReports/StudentPlanningReport.tsx), [sharing](../frontend/src/components/sharing/ShareModal.tsx), [reference import](../frontend/src/features/referenceLayers/ReferenceImportButton.tsx), [nearby routes](../frontend/src/features/referenceLayers/CalgaryContextButton.tsx).

| Control | What it does | Recommendation and student value | Evidence |
| --- | --- | --- | --- |
| Layers and policy map toggles | Opens zoning, local plans, MDP/CTP maps and reference layers. | **Keep prominent in Site.** These directly support site selection and planning rationale. Group extra datasets below the core policy maps. | B panel, S composition |
| Legend & meaning | Provides interpretation for individual policy maps. | **Keep beside each map.** Students need the meaning of a designation, not just a coloured overlay. | B menu, S composition |
| Open zoning map studio | Opens proposed land-use drawing with Calgary district choices and a custom option. | **Keep in Site.** This is the proper home for proposed zoning, separate from existing City land use and generic building areas. | B menu, S composition |
| Calculate assessed value | Requests assessment information for properties within the boundary. | **Keep in Site.** Useful for approximate project feasibility; retain the distinction between assessed value and purchase price. | B menu, S composition |
| Import reference | Selects a GeoJSON or zipped shapefile; preserves it as a separate reference layer with attributes/source metadata. | **Keep under advanced Layers.** Useful for instructor datasets and specialized sites; most students should not need to prepare GIS files. | B menu, S import flow |
| Load nearby Calgary streets & paths | Fetches routes within the site extent plus 100 m and saves a separate reference layer for context/connections. | **Keep in Site/context tools.** Helps tie a proposal into existing circulation. Explain that mapped centreline/path routes are not surveyed curb or complete sidewalk geometry. | B menu, S request |
| Site elevation | Shows an elevation estimate from the project's location. | **Collapse into site information.** Helpful background, but not a separate everyday design operation or surveyed terrain. | B panel, S composition |
| Report / Request report | Opens a saved-proposal advisory review with student responses and rationale. The UI states there is no AI-generation charge. | **Keep, rename entry “Planning report.”** Strong value for explaining decisions. Findings must remain advisory, with students able to adopt, adapt or decline them. | B entry, S report creation |
| Report Refresh | Reloads the selected report/history; requesting a new report is a different action. | **Keep as a small refresh icon or recovery action.** Do not present it as re-analysis of the current design. Distinguish “Reload report” from “Create updated report.” | B entry, S handler |
| Download printable report / Save response | Downloads HTML for printing to PDF, and saves the student's response to a finding. | **Keep and explain the submission format.** These convert review into a usable written deliverable. A direct PDF would be a later improvement, not a reason to remove the current export. | S |
| Team | Opens email-specific view/edit invitations and an optional public presentation link. | **Keep, rename “Share.”** Both group work and instructor review add value. Preserve view/edit distinctions and link revocation. | B panel, S actions |
| Help and Guide | Both invoke the same quick-start tour. | **Keep one Help button; remove duplicate Guide.** Retain contextual hints without two equal navigation choices. | B Help, S shared handler |
| Send feedback | Opens the feedback entry point. | **Keep in Help/support.** Useful during classroom trials, but it contributes indirectly to the final project and need not occupy a separate floating control. | B visible, S entry only |

The outlying review site has no matching approved local area plan in the current collection. The panel clearly said so and disabled that overlay. This is useful empty-state behaviour, not a reason to remove the local-plan control.

## Image and video presentation

Source: [image panel](../frontend/src/components/viewer/globe/GlobeAIRenderPanel.tsx), [style controls](../frontend/src/components/viewer/globe/ImagePresentationControls.tsx), [video panel](../frontend/src/components/viewer/VideoGeneratePanel.tsx), [saved-render animation](../frontend/src/components/viewer/AnimateRenderButton.tsx), [working-view quality](../frontend/src/components/viewer/globe/WorkingViewPerformance.tsx).

| Control | What it does | Recommendation and student value | Evidence |
| --- | --- | --- | --- |
| 3D detail | Offers Economy, Balanced and High working-view quality, with live rendering statistics. Lower quality reduces drawn screen pixels. | **Keep easily accessible.** Basic laptops need this. Collapse draw-call/triangle statistics into diagnostics; keep the reminder that working-view detail affects still capture. | B, S |
| 22 image style buttons | Offers photographic, technical, concept, plan and stylized treatments. | **Keep styles, simplify the first view.** Initially show Photo Realistic, Development, Atmospheric, Watercolour and Site Plan; put the remainder in More styles. Label projection-changing styles clearly. | B, S |
| Compare styles & examples | Opens the render-style guide and selection examples. | **Keep beside style selection.** Helps students choose an appropriate presentation rather than spend tokens guessing. | B menu, S component |
| Add People / Add Vehicles | Adds people/vehicle instructions to image generation. | **Keep in the simple panel.** People communicate scale and public-space use. Avoid implying the generated additions exist in the authored 3D design. | B, S |
| Custom prompt | Adds optional image directions. | **Keep collapsed or optional.** Useful for lighting and atmosphere; a good default should not require students to write a long prompt. | B, S |
| Advanced image controls | Exposes engines and other advanced image options; unavailable local engines are disabled. | **Keep advanced.** Preserve Andrew's GPT/local choices, but do not require every student to understand model selection. The local ComfyUI options were unavailable in this preview. | B visible options, S |
| Source checks | Offers Concept finish, Strict detail and Expressive modes. | **Keep advanced, retain visible result warnings.** Students need to know when an attractive AI finish differs from their design. Do not hide fidelity status with the advanced controls. | B visible options, S |
| Saved Renders / Project Renders | Opens project media from the image panel or the project view. | **Keep one consistent media library with contextual shortcuts.** Both locations are useful, but naming should be consistent, such as “Project images & videos.” | B entries, S handlers |
| Export current 3D view · free | Captures the authored current view and opens a downloadable image preview without an AI finish. | **Make more prominent.** It is the dependable baseline submission and comparison image; a paid generation should not be necessary to show the actual proposal. | B entry, S capture/download flow |
| Video / route settings | Offers route capture/preview, camera modes, quality, providers and paid generation controls. | **Keep video optional; simplify.** Expose drone/walk/bicycle framing and free preview first. Move experimental motion modes, provider trials and technical settings to advanced tools. | B panel, S |
| Run free check | Performs video preflight before a paid trial. | **Keep, integrate with clear readiness feedback.** Useful to avoid failed paid calls. Never remove the underlying validation just to reduce buttons. | B entry, S |
| Animate this render | Starts animation from a finished saved still. | **Keep with the selected saved image.** This is a simpler optional cinematic deliverable. Clearly distinguish it from a video following an authored 3D route. | S; review project had no saved still |

The video panel's opening sentence says “Preserve every building,” while its later disclosure correctly says AI can reinterpret geometry. Replace the absolute promise with language such as “Preview your route and review the finished video against your design.” Similarly, an AI style called Survey or grouped under Accurate must not imply surveyed measurements or certified design fidelity.

## Suggested student interface

Keep Site, Design and Present as the only main stages. Site contains the boundary, existing zoning, local/city policy, proposed zoning and assessment. Design leads with Buildings, Parks, Streets, Walk, Select and Undo/Redo. Present leads with free 3D export, AI images, the saved media library, and optional video. Planning report and Share remain readily accessible.

More Tools can hold measurement, version history and viewing toggles. Keep specialized object settings and experimental providers in Advanced tools, with ground and entrance review accessible there and at relevant objects/errors. There should be no Generate to 3D button or equivalent replacement: ordinary edits should update the existing 3D scene. A student should be able to produce a complete basic submission without opening Advanced tools.

## Verification and implementation limits

Browser inspection covered More Tools, history, entrance review, ground review, the planning-report entry, sharing, Help, the Master Plan entry and optional site analysis, Layers, street-camera activation, performance settings, image options, video options, the custom builder entry and measurement activation. Temporary modes/panels were closed and the review project was returned to Design.

The custom builder was opened and closed during its assembly phase. Source inspection establishes its later automatic rebuild path; rebuild completion was not an acceptance test here. No paid image/video generation, invitation/public-link creation, assessment request, GIS import, terrain application, report creation, or intentional layout edit was performed for this audit. The 8,970-token balance remained unchanged in the browser observations.

Only this report was added to the repository. No production code or assets changed. Code tests were not rerun for a documentation-only review. Before any cleanup is implemented, verify that older drawings still reopen, hidden tools remain reachable where needed, save/error feedback stays visible, and free export plus planning-report/share flows remain usable. A short student rehearsal should then test whether the simplified interface is easier to understand; this review is not usage telemetry or a novice usability study.
