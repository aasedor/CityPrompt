# CityPrompt button review by Astra

7 October 2026. Independent review by GPT-6 Astra of the application and the [first complete button audit](COMPLETE_BUTTON_AUDIT_2026-10-07.md), at source checkpoint `16343d676`.

**The first audit is a useful inventory and direction, but should not be implemented as a blanket cleanup specification.** Preserve Site → Design → Present and the prominent Walk and catalogue controls. Remove Generate to 3D, after replacing the initial-build dependency for retained custom and older projects. Recovery semantics, unsaved report text and modal keyboard ownership deserve attention before cosmetic consolidation.

## New findings

### History Restore undoes the selected event

**Important, verified in source.** Selecting a history row changes the action label to Restore in [HistoryPanel](../frontend/src/components/viewer/HistoryPanel.tsx), line 513. Its handler at line 393 calls `zoneHistoryApi.revert`. The [backend](../backend/app/api/v1/site_zones.py), line 3734, deletes the zone for a Created event; line 3752 chooses the previous snapshot for an Updated event.

For example, a displayed height change from 10 m to 20 m followed by Restore produces 10 m. Selecting Created and pressing Restore removes the object. The frontend records recovery actions, so this finding does not establish irreversible deletion. The problem is that the label suggests restoring the selected version, while the operation undoes the selected change.

Separate **Undo this change** from **Restore this version**, and explain the resulting state. Renaming the panel Version history alone will not resolve this. Test Created, Updated and Deleted events, then recovery from each, on a disposable project. No history mutation was executed during this review.

### Removing Generate to 3D needs automatic initial preparation

**Required before cleanup, verified source dependency.** [useAutomatic3D](../frontend/src/features/pickPlace/useAutomatic3D.ts), lines 54–57, makes a scene eligible for automatic building when it is catalogue-only or already has compilation metadata. Line 74 skips an ineligible scene. Its comment explicitly describes non-catalogue designs joining automatic rebuilding after their first explicit build.

[Workflow readiness](../frontend/src/features/workflow/cityPromptWorkflow.ts), line 89, still instructs users to run Generate to 3D, and line 109 gates rendering on `sceneReady`. Removing only the visible entry could therefore strand an uncompiled custom-only or older project, including retained custom drawing paths.

The button should still be removed. First provide automatic initial preparation or migration for every retained path and replace obsolete readiness messages. Verify catalogue-only, custom-only and mixed scenes, including interrupted preparation and retry. This is a predicted regression from a button-only cleanup, not a claim that the button has already been removed or that all current catalogue scenes are broken.

### Planning report navigation loses unsaved reasoning

**Important, verified in source.** [FindingCard](../frontend/src/features/studentReports/StudentPlanningReport.tsx), line 31, holds response choice, rationale and follow-through in local component state, with an explicit Save action. The report is conditionally mounted in [ProjectViewPage](../frontend/src/features/projects/ProjectViewPage.tsx), line 1372. Its finding-location action at line 1379 closes the report to inspect the object; the close callback at line 142 has no dirty-state guard. [StudioDialog](../frontend/src/features/projects/StudioControls.tsx), lines 47 and 59, also closes through Escape or a backdrop click. Changing saved reports changes the finding component keys in StudentPlanningReport, line 251.

A student can write an explanation, click the linked building to check the design, then return to find the unsaved text gone. This concerns local drafts, not previously saved server responses. Preserve drafts by project/report/finding, or provide clear save/discard handling before navigation. Verify object inspection, report switching and close/reopen with an unsaved response. No saved report response was changed in this review.

### Walk consumes Escape underneath the report dialog

**Important, browser reproduced and source confirmed.** In the review project, Astra clicked Walk, opened Report before choosing a starting point, then pressed Escape. Walk was cancelled underneath, while the Planning report dialog remained open. The underlying button changed from Cancel walk back to Walk.

[GlobeSitePlannerMap](../frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx), line 2533, installs a capturing window handler that stops immediate propagation. [StudioDialog](../frontend/src/features/projects/StudioControls.tsx), line 56, listens on document and therefore does not receive that first Escape. The project passes `interactionPaused` while the report is open at [ProjectViewPage](../frontend/src/features/projects/ProjectViewPage.tsx), line 1253, but the Walk handlers do not honor it.

Give the open dialog ownership of keyboard interaction, and suspend underlying transient modes. The active-walk handler at GlobeSitePlannerMap line 2489 has the same missing pause check. Movement behind a modal is a source-supported concern requiring an active-walk reproduction; only the picker/Escape conflict was browser-tested here.

### Touch Walk has no ordinary movement control

**Support limitation, verified in source; not tested on an iPad.** Walk movement uses keyboard state in [GlobeSitePlannerMap](../frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx), lines 2493 and 2517. The pointer surface at line 4795 turns the camera through `lookWalkPose` at line 4803. Its visible controls provide entrance/lift shortcuts, rendering and exit, but no continuous forward/backward movement pad.

An iPad without a keyboard therefore lacks the normal continuous walking interaction through these controls. Add touch movement if iPads become supported classroom devices. This is not an automatic desktop release blocker: the [release plan](STUDENT_READY_RELEASE_PLAN_2026-09-23.md), line 43, targets desktop/laptop Chrome and Edge, and line 62 defers mobile support.

## Changes to the first audit

| First-audit item | Astra assessment |
| --- | --- |
| Missing progress-bar `/projects/:id/viewer` route | Confirmed. Repair its navigation target and keyboard accessibility. |
| Legacy PDF download bypasses Bearer authentication | Confirmed, but lower priority than normal-path recovery and draft issues. It is in the non-globe branch; the default viewer setting is globe. |
| Site analysis Refresh starts another generation | Confirmed. Regenerate site analysis describes its effect more accurately. |
| Help/Guide duplication and one-choice collection dropdown | Confirmed. These are straightforward simplification candidates. |
| Generate to 3D removal | Confirmed user requirement, with automatic initial preparation as a concrete prerequisite. |
| Repeated object editors | Consolidation opportunity, not proof of equivalent behavior. Compare fixed-model restrictions, custom fields and advanced capabilities before merging. |
| Walk and Streets need prominence | Preserve their existing prominent placement: the default browser already shows Buildings, Parks, Streets and Walk together. |
| Recovery controls look repetitive | Different effects must remain distinguishable: check an existing media attempt, recompile geometry, reload drawings and restore/undo history are not interchangeable. |
| Exactly five initial image styles | A proposal, not a validated shortlist. Assignment needs and novice trials should determine the default set; preserve remaining styles and examples. |
| No Walk inside gate | Confirmed. Optional entrance-return and lift controls can remain navigation aids without becoming entry requirements. |
| Staff and read-only controls | Keep their scope clear. Admin routes are role-gated in App; ProjectViewPage line 1150 routes viewers to ReadOnlyProject. They are not ordinary student-toolbar clutter. |

## Inventory limits

The inventory reconciles to 535 button definitions, 97 choices, 62 other click targets, 28 disclosures and 92 links: 814 definitions. The original report correctly distinguishes these from simultaneously visible controls. The AST-based scan is useful for finding code, and the component register provides broad coverage.

It is not a set of 814 independently tested action contracts. Most recommendation cells are assigned by file/group or label matching. The CSV evidence wording **Source traced** should be read as inventory/source inspection, not proof that every downstream API effect was independently validated.

Nested dynamic labels can omit decisive states. C0209 records Restoring… but misses the Restore/Undo distinction; C0799 records Preparing… without Request report / Request a new report. Nearby conditional expressions omit early returns, caller conditions and state-machine reachability. Import scopes cannot establish actual student visibility. Native controls, ordinary inputs and mesh/pointer interactions are outside the definition count.

Keep the CSV as a navigation aid. Before changing a control, specify its trigger, actual effect, allowed user role, failure/recovery behavior and retained replacement. Implementing its recommendation column mechanically would be unsafe.

## Recommended disposition

| Decision | Controls |
| --- | --- |
| Keep or promote | Site/Design/Present; boundary and policy interpretation; separate existing/proposed zoning; assessment with coverage caveats; Buildings/Parks/Streets; Walk; Select/Undo/Redo; faithful free export; saved media; planning report; Share; save/error recovery; working-view quality. |
| Keep contextual or advanced | Object connections, terrain and entrance diagnostics; GIS imports; custom asset creation; master-planning scenarios; provider trials and technical statistics. Relevant failures should still lead directly to recovery. |
| Merge or rename | One Help entry; consistent media-library name; Report → Planning report; Team → Share; analysis Refresh → Regenerate site analysis; precise history actions; genuinely equivalent editor fields after capability mapping. |
| Remove after dependencies are resolved | Duplicate student stepper and Generate to 3D; inert collection dropdown; redundant generic drawing shortcuts once retained destinations are verified. Update conversion/readiness language throughout the workflow. |

## Acceptance checks before cleanup

Use a bounded project of approximately 20 buildings, five parks and eight street segments. Include these checks:

1. Catalogue-only, custom-only older and mixed projects prepare automatically, including failure and retry.
2. Created/Updated/Deleted history entries have predictable results and recover correctly.
3. Unsaved report text survives or receives clear save/discard handling during object inspection, report switching and closing.
4. Walk transitions to Report, catalogue and Present without keyboard commands reaching the wrong mode.
5. Close-up street/aerial free captures download, and saved media reopens.
6. Editor and view-only collaborator controls remain appropriate to their roles.

Measure performance on representative basic Windows hardware. Control counts or choosing Economy do not establish classroom capacity. A touch trial is a separate condition if iPads are added to the supported environment.

## Verification and scope

Astra inspected application source before comparing the prior reports, CSV and extraction scripts. It opened the named local project in a temporary hidden browser tab, observed the 8,970-token balance, reproduced the Walk/report Escape issue, returned the project to Design and closed its temporary tab. The coordinating agent rechecked the main history, compilation, draft-state and keyboard source paths before saving this report.

Application code, account state and saved project data were not changed. Paid media generation, invitation/public-link creation, history mutations, report submission, deployed-site behavior and device-specific movement were outside this read-only pass. These remain explicit acceptance work rather than silently assumed passes. App tests were not run for a documentation-only review.

Fine construction detail, legal/code certification and exhaustive provider-output quality were set aside because this review concerns student controls and safe interface cleanup. Mobile navigation remains a support decision under the existing desktop-first scope. No other discovered control behavior was silently excluded.

**Verdict: proceed with a revised, staged cleanup plan, not the first audit as an automatic removal checklist.** The useful features and the prominent Walk layout should remain; resolve recovery and initial-preparation dependencies before simplifying their entry points.
