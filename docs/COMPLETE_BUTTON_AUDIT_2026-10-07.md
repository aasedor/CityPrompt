# Complete CityPrompt button audit — 7 October 2026

The interface has a useful core, but older workflows compete with it. Keep Site → Design → Present, make Walk prominent, and keep policy interpretation, object editing, free scene export, the planning report and sharing easy to find. Remove the student-facing **Generate to 3D** operation entirely: the scene is already in 3D. The cleanup proposals below have not been implemented.

This expands the [earlier secondary-button review](STUDENT_BUTTON_REVIEW_2026-10-07.md) to the whole frontend. Recommendations reflect students choosing a site, explaining planning decisions, designing and exploring a community, and presenting street/aerial images and optional video. No click-frequency analytics or new marking rubric were supplied.

## Coverage

Reviewed the local preview on port 5183, branch `codex/student-button-audit-2026-10-07`, source checkpoint `6679d9bad`. This is not a test of the older live Cityprompt.ca deployment. Browser checks used “Release model verification · 19 candidates” and an existing local saved-media QA fixture.

The source scan covered 509 non-test TypeScript/TSX files, recording **814 control definitions in 115 files**:

| Kind | Definitions |
| --- | ---: |
| Buttons, including explicit button roles | 535 |
| Links | 92 |
| Selects, checkboxes, radios and ranges | 97 |
| Disclosure headings | 28 |
| Other HTML/SVG click targets, including modal backdrops | 62 |

These are definitions, **not 535 buttons visible at once**. A catalogue/style button rendered in a loop has one definition and many instances. Counts include staff administration, feature-flagged legacy interfaces and developer fixtures. Native video controls, ordinary text/file inputs, keyboard shortcuts and 3D mesh handles are not separate button definitions. Pointer/keyboard events attached to inventoried controls are included.

The [complete CSV](ui-button-audit/button-inventory-2026-10-07.csv) has an individual row for every definition: label/expression, panel purpose, recommendation, source position, handler, form submission, other events, disabled/conditional state, target and route import scopes. The [component register](ui-button-audit/component-register-2026-10-07.md) covers every file. Import reachability does not establish visibility; missing route imports do not prove a fixture unused. Conditional columns record nearby source expressions, not the entire execution path. CSV text beginning with spreadsheet formula characters is prefixed with an apostrophe for safe viewing.

Evidence: **B** means browser inspection of the control/panel; **S** means source tracing without executing the downstream action. Grouped rows do not imply every member was clicked. Browser inspection is not a paid-generation or destructive-action acceptance test.

## Fixes and significant findings

| Priority | Finding | Evidence and action |
| --- | --- | --- |
| 1 | Generate to 3D and a second workflow remain. | [ProjectViewPage](../frontend/src/features/projects/ProjectViewPage.tsx) has entries in both branches; [LegoBuilderPanel](../frontend/src/features/legoAssembly/LegoBuilderPanel.tsx) has generation/rebuild controls. Remove the student scene-generation entry and duplicate stepper. Preserve automatic compilation and existing projects. Creation of a genuinely new custom asset is a separate advanced operation. B/S. |
| 1 | Generation progress navigates to a missing route. | [GenerationProgressBar](../frontend/src/components/GenerationProgressBar.tsx) targets `/projects/${projectId}/viewer`; [App](../frontend/src/App.tsx) has `/projects/:id`, without that suffix. Fix navigation and keyboard accessibility. Source-confirmed mismatch; no job was started to reproduce it. S. |
| 1 | Legacy PDF Report bypasses authenticated downloading. | Its direct anchor in ProjectViewPage does not attach the API client's Bearer header and defaults to port 8000. The [PDF endpoint](../backend/app/api/v1/reports.py) requires [Bearer authentication](../backend/app/core/security.py). Repair or retire this legacy entry in favour of a consistent authenticated export. Source integration issue, not a browser reproduction of the legacy branch. S. |
| 2 | Site analysis “Refresh” is another generation. | [SiteIntelligencePanel](../frontend/src/components/viewer/SiteIntelligencePanel.tsx) calls `handleGenerate`. Rename it **Regenerate site analysis** and explain effect/cost. It differs from reloading reports or checking saved image attempts. S. |
| 2 | Basic edits are repeated in two editors. | Reshape offers variant/height/plot edits; More settings opens Type → Archetype → Scale → Details. Merge basic controls; retain reference/custom settings as advanced. Both inspected, no edits saved. B/S. |
| 2 | Some icon controls lack accessible names. | New Project's close button was unnamed in the browser. Password visibility controls lack explicit names in reviewed source. Add Close / Show password / Hide password. Do not assume every dynamic label is missing. B/S. |
| 2 | Video/style wording can overpromise. | “Preserve every building” conflicts with the later AI-reinterpretation disclosure. Replace the absolute claim; Survey/Accurate style wording must not imply surveyed measurements or guaranteed geometry. B/S. |
| 3 | Collection dropdown offers one choice. | Only “Approved & validation candidates” is available. Use a badge until there are genuine alternatives. Keep real search/facet filters. B/S. |
| 3 | Saved-image labels can include entire prompts. | Project-list thumbnails use long prompts as image text. Use short captions and “Open [style] render”; put prompt text in Details. B/S. |
| 3 | Imported authoring-layer deletion deletes objects. | [LayersPanel](../frontend/src/features/projects/LayersPanel.tsx) confirms; the project handler deletes matching imported zones sequentially. Explain object count and verify partial-failure recovery before simplifying. Not the same as hiding a reference layer. S. |

## Site and planning controls

Source: [workflow](../frontend/src/features/projects/StudentWorkflow.tsx), [zoning editor](../frontend/src/features/referenceLayers/ZoningStudyEditor.tsx), [policy maps](../frontend/src/features/policyPlans/CityPolicyMapsPanel.tsx), [reference layers](../frontend/src/features/referenceLayers/ReferenceLayersPanel.tsx), [assessment](../frontend/src/features/referenceLayers/SiteAssessmentPanel.tsx).

| Controls and purpose | Recommendation | Evidence |
| --- | --- | --- |
| Site / Design / Present change the main stage. | **Keep as the only main workflow.** | B/S |
| Draw / Review boundary; Confirm site & design establish the site. | **Keep prominent in Site.** Remove equal duplicate shortcuts in Design. | B/S |
| Boundary opacity and preparation/level settings control visual fill and ground treatment. | **Keep opacity simple; collapse terrain numbers.** Explain transparency versus the placement surface. | S |
| Existing land-use switch/opacity, district details, permitted/discretionary catalogue matches and source links interpret City zoning. | **Keep.** Retain height/use/modifier/relaxation/DC caveats; keep existing and proposed layers separate. | B panel; matches S |
| Local-plan selector/switch/opacity, legend, designation details/source/close and plans-in-progress disclosure interpret neighbourhood policy. | **Keep in Site**, with in-progress material collapsed and distinguished from approved maps. | B/S |
| MDP / CTP groups, individual switches, opacity and Legend and meaning compare city policy maps. | **Keep grouped, independently toggleable.** | B/S |
| Zoning studio, City/custom district choices, Draw/Finish/Cancel/Select, polygon edits and Undo/Redo author proposals. | **Keep together.** Distinguish custom entries from City codes. | B panel; drawing writes S |
| Copy City outlines/existing zones and clip to boundary establish starting geometry. | **Keep contextual.** Explain add/replace effects before execution. | S |
| Save, shared-version reload and revision warnings persist/reconcile zoning studies. | **Keep recovery; protect unsaved work.** | S |
| Labels, map key, SVG/PNG export and sources produce a zoning presentation. | **Keep**; styling options can be collapsed. | B key; export S |
| Open 2D corner editor / Return Google 3D offer a polygon-editing fallback. | **Keep advanced**, useful for precise geometry. | B/S |
| Load nearby Calgary streets & paths fetches/saves circulation context. | **Keep in Site/context**; explain centreline/path data limits. | S |
| GIS file choice, preview/import/cancel imports reference data. | **Keep in advanced Layers.** | S |
| Layer show/hide, attributes, Go to layer, source, Remove/Delete/Cancel inspect/manage datasets. | **Keep contextual**; visibility, reference removal and authoring-zone deletion need distinct labels. | B panel; mutations S |
| Calculate assessed value, breakdown and source support approximate feasibility. | **Keep** with coverage and assessed-value-versus-purchase-price explanation. | B entry; calculation S |
| Elevation disclosure/Retry shows a location estimate. | **Keep collapsed in site information**, not as surveyed grading. | B panel; retry S |

The outlying review site had no matching approved local plan. Its panel explained this and disabled the overlay: useful empty-state behaviour.

## Design, walking and editing controls

Source: [toolbar](../frontend/src/components/viewer/SitePlannerToolbar.tsx), [globe](../frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx), [catalogue](../frontend/src/features/pickPlace/PlacementPalette.tsx), [reshape](../frontend/src/features/pickPlace/ReshapePanel.tsx), [full properties](../frontend/src/components/viewer/ZonePropertiesPanel.tsx).

| Controls and purpose | Recommendation | Evidence |
| --- | --- | --- |
| Buildings / Parks / Streets open catalogue categories. | **Keep prominent**; street drawing belongs in Streets. | B/S |
| Search/group/land-use/size/style filters, Reset/Clear and variants narrow choices. | **Keep.** Modernist narrowed buildings to five choices; Reset restored results. | B/S |
| Collection selector and Show more choices choose collection/page results. | **Simplify single-choice collection; keep pagination.** | B/S |
| Choose & place / draw outline / draw route initiate asset placement. | **Keep contextual**, with consistent instructions. | S; catalogue B |
| Rotation/Q-E, Place at centre and Cancel orient/complete placement. | **Keep** keyboard and touch alternatives. | S |
| Select, Move, point/rotation interactions, Delete manipulate placed objects. | **Keep contextual**, with appropriate recovery. | S |
| Variant/height/storeys, Apply building/shape and Place another edit/repeat buildings. | **Keep; consolidate repeated basic fields/Apply.** Explain fixed-model limits. | B panel; saves S |
| Park components/outline points/layout preview/apply/seating shape parks. | **Keep inside selected park editing**; Preview and Apply have different effects. | S |
| Street design/width/cross-section, Add bend point edit routes. | **Keep contextual**, with cross-section details collapsed. | S |
| Duplicate street, side/offset, Create copy/Cancel create parallel segments. | **Keep in selected street.** | S |
| Add/Move/Remove stop edits supported transit stops. | **Keep only for applicable streets.** | S |
| Connections, target, Pick entrance in 3D, offsets and Save/Cancel connect access to circulation. | **Keep a simple connection first; numerical/scale options advanced.** | B panel; saves S |
| Terrace/path, level terrace, clear-connection suggestion, Save/Cancel and notes support sloped access. | **Keep contextual/advanced**, never as permission to walk. | B panel; writes/export S |
| More settings with Type/Archetype/Scale/Details, Back/Next and reference fields opens the older editor. | **Merge basic duplicates; preserve specialized details.** | B/S |
| Walk, ground start selection, Cancel and Exit walk enter/leave immersive exploration. | **Keep very prominent**, no Walk inside gate. | B start/cancel; movement S in this audit |
| Return to entrances, lift, Street view render assist within a walk. | **Keep contextual aids.** Walking should ordinarily continue through entrances/across parks. | S |
| Top View / Focus Plan frame the proposal; quality presets reduce working-view load. | **Keep easily accessible**, especially for basic laptops. | B/S |
| Proposed models, planning overlays and existing-building toggles manage different visibility layers. | **Keep in viewing tools with stable labels**, replacing ambiguous Clean 3D wording. | B menu; handlers S |
| Measure, History rows/Locate/Load more, zone Undo/Redo inspect scale and recover edits. | **Keep under More Tools**; call persisted records Version history, ordinary Undo/Redo beside Select. | B panels; restoration S |
| Ground review/terrain modes/redevelopment level diagnose and apply ground fixes. | **Keep contextual recovery**, explain effects before Apply. | B panel; writes S |
| Entrance/ground problems, Select and review, Retry alignment diagnose placement/access. | **Keep contextual**, never prerequisites for ordinary walking. | B review/select; other writes S |
| Custom building/park, Water, generic Residential/Development Area/Parks-Plazas start overlapping drawings. | **Consolidate into their categories**; zoning studio is for districts. Preserve old drawings. | B menu; handlers S |
| Project steps & custom 3D, Generate to 3D and normal scene Rebuild repeat scene generation. | **Remove student entry and duplicate stepper**, preserve automatic updates. | B/S |

Connections exposed several technical offsets and a scale option when enabled. With no target street on this QA site, Save was disabled. That state was reasonable; scaling defaults/wording merit review against native model dimensions. No connection was saved.

## Presentation and recovery controls

Source: [image panel](../frontend/src/components/viewer/globe/GlobeAIRenderPanel.tsx), [image editor](../frontend/src/components/viewer/RenderEditModal.tsx), [video](../frontend/src/components/viewer/VideoGeneratePanel.tsx), [animation](../frontend/src/components/viewer/AnimateRenderButton.tsx), [image recovery](../frontend/src/components/viewer/globe/RecoverImageAttempts.tsx).

| Controls and purpose | Recommendation | Evidence |
| --- | --- | --- |
| Render this view, street camera/direction and close frame an image. | **Keep**, distinguish camera setup from Walk. | B entry; capture S |
| Free current-3D export, preview/download capture the actual authored scene. | **Promote as the baseline submission.** | B entry; export S |
| Style buttons, example comparison/view choice and Use style select an AI finish. | **Short initial set plus More styles**, retaining examples and other styles. | B controls; generation S |
| People/vehicles and custom prompt add finishing instructions. | **Keep simple choices, collapse prompt.** Generated additions do not become authored objects. | B/S |
| Engines/local-GPT/quality/pipeline/fidelity options select generation behaviour. | **Keep advanced; preserve local image and regular GPT choices.** Defaults should suffice. | B/S |
| Generate/Stop/Cancel, source checks and result fidelity review submit/manage/check images. | **Keep with costs/readiness/source warnings**; Stop is not a guaranteed provider refund. | S; panels B |
| Legacy flag-gated Community 3D/optional AI ground controls duplicate workflow. | **Remove duplicate student scene-generation prompts**, review internal compatibility. | S |
| Saved Renders/Project Renders, thumbnail retry/close open stored media. | **One consistent library name**, useful contextual shortcuts and retrieval recovery. | B/S |
| Lightbox/source-result comparison, previous/next/zoom and image/GLB downloads inspect outputs. | **Keep contextual**, label formats and shorten accessible captions. | B entry; downloads S |
| Edit render, mask/brush, Undo/Clear/zoom, engine and Reprocess edit image pixels. | **Keep beside saved image**; does not edit the 3D design. | B controls; reprocess S |
| Compare all three engines submits separate GPT Image 2/Flare/Sunburst calls. | **Advanced trial**; Edit render correctly showed three separately billed calls. | B/S |
| Animate this render, create/check request, playback and MP4 download animate saved stills. | **Keep optional with selected image**, distinct from an authored route. | B existing clip; creation/download S |
| Route capture/reset/points, camera modes, free preview/download establish video motion. | **Free preview first**, simple drone/walk/bicycle framing before experiments. | B panel; route/export S |
| Free check, provider/quality and Generate video validate/submit video jobs. | **Keep optional**, preserve fidelity checks and explicit costs. | B panel; generation S |
| Benchmark/Score saved video, archived attempts and download evaluate/recover trials. | **Specialist QA/recovery**, outside normal student path. | S |
| Local trial prompt/model/run/check/missing-job reconciliation trials local images. | **Advanced research tools**; normal image options remain. Do not restore local video as standard. | B panel; run/mutations S |
| Check saved image/attempt, recover/acknowledge stopped output and download retrieve existing jobs. | **Keep recovery**, distinguish checking an existing call from resubmission. | S |
| Progress, Stop individual/all and Dismiss manage background jobs. | **Keep; repair navigation.** | S |

The local trial panel reported Qwen Image 2.1 High Quality ready at 2752 px/40 steps and FLUX.2 Klein 4B as fast preview. No trial ran. The earlier report's unavailable local options reflected its earlier runtime observation, not a conclusion about all local generation.

An existing five-second silent animation opened through a saved-image fixture. This verifies access to existing playback, not completion/quality of a new paid video. Keep native playback controls even though they are not separate TSX definitions.

## Advanced creation, analysis and reports

| Controls and purpose | Recommendation | Evidence |
| --- | --- | --- |
| Custom Add building/roof/Add/Cancel create a record. | **Custom buildings**, distinct from catalogue placement. | S |
| AI asset tabs/templates/styles/engines/Generate model create a new custom asset. | **Advanced creation**, not a conversion step for the scene. | S |
| Prepare/search/select reference views, source/licence, recover views and Generate model manage reference-driven creation. | **Advanced**, preserve attribution/recovery and generation costs. | S |
| Custom style/preset/attachments/remove/Expand prompt edit or AI-expand instructions. | **Advanced**, distinguish plain editing from expansion/upload. | S |
| LEGO Load/floors/setback/assemble/Place/Save/Clear recipe/Close edit specialized assemblies. | **Advanced recipe editing**, preserve saved recipes; remove mandatory scene generation. | B builder entry; later actions S |
| Reviewed street-atlas import and recipe persistence maintain specialist content. | **Staff/advanced**, not ordinary classroom navigation. | S |
| Site DNA/Regenerate analysis run optional analysis. | **Optional site analysis in Site**, clearer effects/costs. | B entry; generation S |
| Scenario Run/custom Run, Solo/All, Draw plan, Sheet/PDF/Pack, Apply/Delete generate/compare/export/apply plans. | **Advanced/instructor**, clearly separate preview, export and mutations. Students retain authorship/rationale. | S |
| Layout preview/regenerate unlocked/locks/Apply/Cancel compare alternatives. | **Advanced**, protect authored objects and require clear Apply. | S |
| Landscape presets/custom/preview/apply/discard/remove add landscape. | **Optional landscape editing**; rename Generate 3D Site Landscape to Preview landscape. | S |
| Planning report/Request/selector/Refresh create or reload advisory reports. | **Keep readily available**, distinguish reload from updated analysis. | B entry; requests S |
| Finding/object selection, Adopt/Adapt/Decline and Save response record rationale. | **Keep**, directly supports final-project explanation. | S |
| Printable report/details/source and terrace-notes export support submission. | **Keep and label format**; current printable report is HTML for printing to PDF. Consolidate competing exports. | S |

## Account, sharing, help and back office

| Controls and purpose | Recommendation | Evidence |
| --- | --- | --- |
| New Project/address/Create/Cancel/close and project Open/Edit/Save manage projects. | **Keep**, add close label and retain explicit save/cancel. | B forms/open/cancel; writes S |
| Account menu/password/sign out/mobile menu and Light/System/Dark theme manage account/navigation/appearance. | **Keep away from design toolbar.** | B menu/visible theme; mutations S |
| Sign in/Google/Register/password recovery/change/visibility/navigation authenticate. | **Keep needed flows**, accessible toggle names and clear status. | S |
| Share/invite/permission/remove/revoke/public link/copy/close manage collaboration. | **Keep; call entry Share**, preserve view/edit and revocation. | B panel; access changes S |
| Accept invitation/account switch/retry and shared-plan/media inspection support project access/presentation. | **Keep appropriate page controls**, shared viewers remain read-only. | S |
| Help/Guide/Back/Next/Close navigate the same tutorial. | **One Help entry**, contextual tips; remove duplicate Guide. | B/S |
| Feedback category/Send/Cancel/Close submit support requests. | **Help/support**, avoid another competing floating design control. | S |
| Crash Try Again and load/save/reload/discard reconcile failures. | **Keep recovery**, protect unsaved work; separate technical diagnostics. | S |
| Admin users Add/reset tokens/role/activate/deactivate/delete change accounts. | **Retain staff-only**, confirmations/permissions; do not audit by changing student accounts. | S |
| Admin buildings filter/gallery/table/render thumbnails/assign/save library maintain assets. | **Retain staff-only**, explicit generation/save effects. | S |
| Admin project/dashboard links navigate back office. | **Retain staff-only.** | S |
| Admin feedback status/notes/save/delete manage support. | **Retain staff-only.** | S |
| Render-log input/output/lightbox/expand/select/delete/load manage diagnostics. | **Retain staff-only**, pagination and protected deletion. | S |
| Analytics ranges/series/balance refresh and role confirmation manage restricted operations. | **Retain role restrictions**, no student toolbar entries. | S |
| Developer park/street review selectors/capture controls operate visual QA. | **Outside classroom navigation**, not automatically dead code. | S |

## Recommended cleanup sequence

1. Fix route/authentication/accessibility issues. Remove student Generate to 3D and duplicate stepper while preserving automatic updates and old projects.
2. Consolidate Help, gallery naming, generic drawing shortcuts and repeated basic editing. Keep recovery, warnings and source interpretation.
3. Shorten Present: free export, small visible style set with examples, saved media, optional video/animation. Provider trials and technical settings move to Advanced.
4. Rehearse a normal project with about 20 buildings, five parks and eight street segments: site/policy/proposed zoning; place/rotate/edit/delete/undo; walk buildings/parks; close-up images; report/share. Trial a basic Windows laptop and touch access before release.

A complete basic submission should be possible without Advanced. No UI/code changes were made for this investigation.

## Verification and limits

This pass inspected project/account forms, catalogue filters/tabs/reset, Walk start/cancel, selected-object Connections/Terrace/More settings, zoning studio/2D fallback, policy meaning, saved image/animation playback, local readiness and image-edit/model-comparison controls. The preceding review additionally inspected ground/entrance review, history, Help, sharing/report entries, measurement, source/style/video/performance panels and builder entry. The CSV's browser flag means **containing panel observed**, not every action passed end-to-end.

No paid generation, account/password/token change, invitation/public-link creation, intentional deletion, GIS import, assessment request, terrain/layout application or report submission was performed. Unsaved transient choices were discarded, the temporary project-list tab closed, and the review editor returned to Design. Observed balance remained 8,970.

Source tracing identifies handler intent and integration mismatches; it does not prove every provider, export, permission, recovery or destructive operation succeeds. Authentication/account/admin mutations, legacy flag paths and developer fixtures received source review only. App tests were not rerun for documentation-only changes; inventory coverage, source/link existence and Git whitespace/status are the relevant checks.

Intentional deliverables: this report, full CSV, component register and earlier-report link. Raw scan JSON/scripts remain outside the repository at `C:/dev-artifacts/CityPrompt/button-audit-2026-10-07/`. No production source, assets or runtime configuration changed. Saved locally; no push/deployment requested.
