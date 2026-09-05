# Student Studio browser verification — 2026-09-04

This records the student-experience checks performed on `codex/student-studio-2027` in the isolated `artifacts/worktrees/student-studio-2027` worktree. It is a feature verification record, not a classroom-readiness certification or the complete integration test total.

## Automated checks

| Scope | Passing tests | Files |
| --- | ---: | --- |
| Reference import, geometry and layers; toolbar and guide; invitations and public presentation UI | 24 | 9 frontend Vitest files |
| Optional site elevation UI | 5 | `SiteElevation.test.tsx` |
| Drawing save recovery, explicit rejected-draft discard, failed-edit status and asynchronous ordering | 33 | `useSiteZones.test.ts` |
| Zone properties, including explicit reload and custom-style autosave recovery | 21 | `ZonePropertiesPanel.test.tsx` |
| Reference parser/API and compatibility with explicit shapefile design import | 40 | `test_reference_import.py`, `test_reference_layers_api.py`, `test_shapefile_import.py` |
| Elevation provider validation, network failures and numeric fallback metadata | 20 | `test_elevation.py` |

These runs total **83 frontend tests in 12 files** and **60 backend tests in 4 files**. The nine initial frontend files were `api.test.ts`, `referenceGeometry.test.ts`, `ReferenceImportButton.test.tsx`, `ReferenceLayersPanel.test.tsx`, `SitePlannerToolbar.test.tsx`, `OnboardingTour.test.tsx`, `ShareModal.test.tsx`, `InvitationPage.test.tsx` and `SharedProjectPage.test.tsx`.

Frontend type-check and scoped ESLint passed at the reference/toolbar/sharing checkpoint and again after the save-recovery follow-up; the elevation component's scoped ESLint also passed. Scoped `git diff --check` passed. Final combined integration/build results are recorded separately by the integrating agent. Elevation unit tests mocked Google responses and made no provider calls.

The initial save-recovery review added 14 hook regressions to the existing 12: definitive 400/422 create failures can be explicitly discarded; retries immediately protect those drafts again; 401/403/server/network failures remain protected. Failed property and geometry edits remain visible until the affected drawing saves or an explicit reload succeeds. Tests cover unrelated saves, project navigation, late responses, and authored saves during a separate undo. This follow-up was automated hook verification, not an additional browser usability session.

Seven additional real-panel regressions verify successful explicit reload restores saved fields, failed reload preserves edits, stale custom-style debounces cannot save during reload/unmount, late project A replies do not reset project B, and ordinary fresh edits still autosave. The combined panel/hook run passed **47/47** tests; full TypeScript, scoped ESLint and diff checks passed afterward.

A later real drawing test exposed a distinct create rejection: **409**, `The new zone must stay completely inside the active site boundary.` The backend checks this before insertion and after the idempotency lookup. Recovery now records this exact response as `outside_site_boundary`, enabling explicit **Delete Zone** or **Discard rejected drawing** for the local draft. Seven additional hook cases bring that file to **33/33 passing**: they cover reload persistence, local deletion preserving saved zones, unknown/revision/request-ID conflicts, legacy errors requiring verification, and a retry whose response is lost. Existing-zone conflicts still use server reconciliation; a status or error string alone does not enable 409 discard. Older local drafts lacking response metadata need one retry with their original request ID before discard is enabled. TypeScript, scoped ESLint and diff checks passed. This fix's acceptance here is automated; the original live failure is recorded in `artifacts/student-studio/media-fidelity/drawing-ui/traffic.json`.

## Successful browser flows

Playwright drove local Chromium against Vite at `127.0.0.1:5175` and the isolated backend at `127.0.0.1:8001`. Layout checks covered **1440×1000** and **1280×800**; invitation and elevation checks used 1280×800.

- **Toolbar and help:** Building, Park and Road controls remained visible at both sizes; optional tools were inspected under More Tools. Help received focus, Shift+Tab stayed within the guide, Enter advanced it, and Escape closed it and returned focus to Help. Settled screenshots checked the corrected workspace/header positioning and layer-panel scrolling.
- **Reference import:** Imported a small GeoJSON zoning fixture through the UI, read its `TEST-R2` attribute, hid the reference, reloaded, and confirmed its hidden state persisted. Saved design-zone count remained **0 before and 0 after** import. This verifies that this reference import did not create proposal buildings.
- **Planning report:** Requested a deterministic report, chose **Adapt**, saved reasoning and follow-through, reloaded and confirmed both persisted. Downloaded printable HTML contained the saved reasoning. No image/video or language-model generation was invoked by this flow.
- **Invitation and viewer access:** The owner created a pending viewer invitation and public link through Team. A separate browser opened the invitation, signed in with the invited account, returned to the invitation, explicitly accepted, and opened the saved plan. The viewer inspected the fixture's library outline and opened the read-only report, without drawing, sharing or report-request controls. A direct viewer attempt to add a zone returned **403**. The owner's team list changed from Pending acceptance to Accepted after reload.
- **Public presentation and revocation:** Anonymous and expired-login browsers loaded the actual saved plan without being redirected to login. After the owner disabled the public link, the request returned **204**; reloading in both browsers showed **Presentation unavailable**, with no plan. The check exposed a static/dynamic DELETE route collision; the backend owner corrected it and the browser continuation passed.
- **Elevation:** The open Layers panel correctly displayed an unavailable state without inventing a zero height. A subsequent live request displayed **approximately 1,044 m above sea level**, with Google source, approximately 10 m data resolution and an explicit statement that this is not a site survey. Details were optional and readable at 1280×800.
- **Saved image source labels and access:** A later owner-browser check used existing media in project `2e9d03e2-d212-48c7-8937-1e2c25226276`. Its seven saved records appeared as three presentation images, with four provider originals hidden until the checkbox was selected. Replay result `a8225a6b-e61f-4982-9bc9-6837fd8ced96` showed **3D source**; its lightbox explained that the AI finish could not be verified and was retained separately. **View source record** opened its JSON record successfully with a `project_asset` ticket scoped to this project (**200**); removing that ticket returned **401**. Selecting the opt-in revealed original `cdb0ca82-2d4a-4c7c-be40-9da157defa4c`, labelled **Original AI attempt**; its lightbox warned it may differ from the design. All seven saved image requests and the source-record browser request returned **200**, and no uncaught page errors were recorded. This check made no generation calls.

The successful sharing continuation exited with code 0 and an empty uncaught-browser-error list. Earlier failed captures remain as debugging evidence; they are not final acceptance screenshots. The invitation flow and corrected revocation were verified in successive bounded runs using the same local fixture.

The media check's first attempt had a harness timing error before opening the tray. After that was corrected, the requested functional assertions passed and three useful screenshots were captured and visually reviewed. An extra original-lightbox screenshot exceeded Chromium's 15-second compositor timeout after its warning had passed the DOM assertion. The script therefore exited with a capture failure; `gallery-source-evidence.json` preserves that failure alongside the successful functional evidence. This is not represented as an entirely passing capture script or a 1280px media check.

## Local evidence, intentionally ignored

Evidence is under the worktree's ignored `artifacts/student-studio/student-experience/` directory. At verification time its absolute location was:

`C:/Users/andre/OneDrive/Documents/CityPrompt/artifacts/worktrees/student-studio-2027/artifacts/student-studio/student-experience/`

| Evidence | Files |
| --- | --- |
| Toolbar, guide and layers | `settled-toolbar-1440.png`, `settled-toolbar-1280.png`, `settled-guide-1280.png`, `polished-layers-1280.png` |
| Report persistence/export | `report-response-1280.png`, `report-1440.png`, `smoke-planning-report.html` |
| Invitation and read-only access | `sharing-owner-pending.png`, `sharing-invite-after-login.png`, `sharing-viewer-readonly-report.png` |
| Public access and revocation | `sharing-public-anonymous.png`, `sharing-public-stale-login.png`, `sharing-owner-revoked.png`, `sharing-public-revoked.png` |
| Elevation | `elevation-live-1280.png` |
| Saved source image, provenance and original opt-in | `gallery-source-default-1440.png`, `gallery-source-lightbox-1440.png`, `gallery-original-opt-in-1440.png`, `gallery-source-evidence.json`, `gallery-source-check.cjs` |
| Reproduction and diagnostics | `ui-check.cjs`, `settled-views.cjs`, `sharing-check.cjs`, `sharing-revoke-check.cjs`, corresponding `.txt` snapshots and error JSON files |

Pytest temporary fixtures are under ignored `artifacts/reference-tests/`. No generated screenshots, browser credentials or runtime data are intended for the source checkpoint.

## Final drawing and report exercise

A subsequent bounded check used actual toolbar/map clicks in project
`32b52157-4f5c-4b87-866f-87b9ca8e1405`, **Studio drawing and reload acceptance — local QA**.
No geometry was seeded by API in this exercise. Boundary, building, road and
green-space creates each returned 201. The building name and development type
were changed through the properties panel. All four complete saved records
matched exactly after a browser reload. An intermediate outside-site road also
confirmed the new explicit rejected-draft discard control works in the browser.

Requesting a report on this nonempty plan succeeded and displayed measured
areas, a park-connection suggestion and questions about missing policy evidence.
The retained default ten storeys is a conceptual test value; this exercise does
not validate an approved house archetype or a compiled 3D model. It used no paid
generation and did not measure a novice's first 15 minutes.

Evidence is in `artifacts/student-studio/media-fidelity/drawing-ui/`:
`acceptance-reloaded.png`, `acceptance-report.png`, `zones-before-reload.json`
and `zones-after-reload.json`. The browser session closed successfully. Earlier
sharing fixtures remain API-seeded as stated below; this later exercise supplies
the separate real drawing evidence.

The final report lifecycle follow-up added nine deferred-response regressions
to four existing report tests. All 13 passed, retaining written rationale after
conflict while preventing a previous project's late response, error, busy-state
cleanup or export from affecting the new project. The combined source checkpoint
passed 366 frontend cases across 32 files, TypeScript, scoped lint and production
build; these counts include earlier focused suites and must not be added together.

## Practical limits

- Chromium used a development **software GPU** (SwiftShader). These checks do not establish production GPU performance, device compatibility, terrain alignment or rendering fidelity across machines.
- There was **no 60-student rehearsal**, simultaneous eight-person editing test, university-network trial or observed usability session with students or older first-time users. A successful first 15 minutes of drawing and rendering has not been demonstrated by these checks.
- The sharing fixture's plan was seeded through the local API. These checks verify viewing and access control, not a full building/park/road placement exercise.
- The earlier sharing fixture contained **no saved images or videos**. The later owner-only media fixture verified saved-image delivery and provenance access; it did not verify media delivery to invited/anonymous viewers, video playback, or image quality. These browser flows did not invoke paid image/video generation.
- Google elevation is approximate map context, not surveyed site data. The single successful live estimate does not prove availability or accuracy for every location.
- Cold development pages sometimes exceeded a five-second assertion window; the continuation used a 30-second readiness window. This is not a measured page-load performance result.
