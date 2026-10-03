# Claude Code prompt — Direct 3D render readiness recheck

Use the exact Git branch `codex/validation-public-realm-compile` from
`https://github.com/aasedor/CityPrompt.git`. Record `git rev-parse HEAD` and
`git status --short --branch` before testing. This is a focused student-browser
check of the automatic Community 3D build and Direct 3D render gate. Do not
claim that a rebuilt container is Andrew's Windows installation.

## Set up the same version

On Andrew's Windows machine, use the existing isolated checkout
`C:/dev/CityPrompt-approved-validation` and run
`C:/dev-artifacts/CityPrompt/approved-validation-2026-09-24/start.ps1`.
Open `http://127.0.0.1:5180/` and verify
`http://127.0.0.1:8006/health`. Use the existing local student account and
project `17a3fc93-4ace-496b-82b3-5db71266814a` if they are available.
Read the private login details from the local handoff directory; never print
or commit them. Do not touch the main CityPrompt checkout.

In a separate container, clone this branch into a fresh directory, then follow
`docs/CLAUDE_VALIDATION_SETUP.md` for the LFS packet, isolated services, and
generated test login. Substitute this branch name for the older branch in that
document's clone command. Do not reuse the Windows project ID or localhost;
create a disposable project through the UI in your own environment. If map
credentials, Docker/PostGIS, or browser access are unavailable, report BLOCKED
with the exact missing prerequisite. Do not build stand-in models or report a
browser pass from static checks.

## Finite browser check

1. Log in through the UI. Open the existing Windows project, or create a
   disposable project in a rebuilt copy. Wait for map tiles and the automatic
   3D status to settle. Record the status text and any console/network error.
2. Ensure a park and a street from the local validation catalogue are in the
   design. Prioritize `Neighbourhood orchard`, `Timber and stone square`,
   `Planted shared lane`, and `Quiet residential street`: their exact student
   archetype/variant IDs were previously absent from the backend trust index.
   On Windows, inspect already-saved items first; in a fresh copy, place them
   through normal student controls. Never seed design geometry by API or script.
3. Move one object, save, and wait for automatic Community 3D. Repeat after a
   second move or rotation. Expected: the status returns to `3D saved` without
   asking the student to manually run `Complete Community 3D` or `Retry 3D
   update`. Reload the page and confirm the saved design and ready state remain.
4. Choose Present > Image. Open Advanced image controls and select/inspect
   `DIRECT 3D`. Expected: no banner saying `New or changed objects need Complete
   Community 3D`; the Generate image control is enabled. Do **not** trigger a
   paid image generation. Use only free `Export current 3D view`, then inspect
   that the exported image reflects the current object positions rather than
   the pre-move scene. Record whether the three simplified public-realm layouts
   are visually faithful; this is a separate quality finding, not a readiness
   pass by itself.
5. If a step fails, capture the first reproducible failure: object/variant,
   project ID, steps, status text, console/network response, and one useful
   screenshot. Distinguish an untrusted catalogue ID, a failed automatic
   compile, stale scene fingerprints, disabled Direct 3D controls, export
   mismatch, and environmental/map failure. Do not silently repair or bypass
   the failure.

Save a short `RESULTS.md`, `results.json`, and indexed screenshots under
`.validation/claude-review/direct-3d-recheck/` (ignored local output). Include
the Git SHA, environment (Windows original or rebuilt copy), browser, project
ID, exact variants tested, PASS/FAIL/BLOCKED per step, and any remaining
limitations. Report findings first; do not change code, approval flags, or
model files, and do not push anything.
