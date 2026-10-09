# Planner demonstration implementation and verification plan

**Goal:** Default new site boundaries to level redevelopment and rehearse the complete student workflow, producing three aerial images, three street images, one saved-render animation and one route video.

**Architecture:** Reuse the site boundary defaults, existing project persistence, catalogue, reports and billed render/video flows. Preserve existing projects' explicit terrain choices. Use a separate demonstration project and bounded paid generation batch.

**Execution:** Inline, with the existing worktree and separate named initiative branches for fixes. No deployment or push requested.

- [x] Change the shared new-boundary default to prepared ground; check properties and terrain tests, TypeScript and the browser-created boundary.
- [x] Create a compact, plausibly planned demonstration with buildings, parks, paths/streets and individual details; review existing zoning, local/city policy and transit, draw proposed zoning and retrieve assessments.
- [x] Exercise selection, moving, rotating, undo, walking, report generation and export, then save/reopen.
- [x] Generate and inspect three aerial and three street-view images. Use deliberate camera compositions and the existing engine choices; retain source comparisons.
- [x] Animate one approved image, then capture and render a short route video. Check job status, recovery, saved outputs, playback and downloads without duplicate submissions.
- [x] Record exact evidence, visual limitations and remaining failures. Keep generated media outside Git. Commit coherent verified fixes without pushing.

**Review focus:** Existing terrain preferences survive; details remain selectable; zoning overlays do not steal drawing; capture modes remain honestly labelled; video recovery does not submit another paid request. An attractive AI output is not evidence of exact geometric fidelity.
