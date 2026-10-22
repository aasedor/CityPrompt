# Photographic video release candidate — 2026-10-21

The optional Video Render photographic finish uses one Sunburst 2.5 guide,
explicit visual review, then the original native route MP4 plus that guide in
Omni 1.1. The default video flow is unchanged. Each paid step is explicit and
has no automatic provider retry. Guide recovery retains the original recording,
and source, scene and image hashes are checked before video spending.

Three previously reviewed rigged people are included in the existing Add Details
People group and hosted asset packet. Editing uses their idle pose; opt-in capture
walks them forward at 1.2 m/s. Clear paths are required. Door choreography,
obstacle avoidance and seated animation are not app features.

## Verification recorded before promotion

- Full backend suite: 2,403 passed, five optional tests skipped.
- Full frontend suite: 3,523 passed. After the final restored-clip cache fix,
  15 focused video/guide/cache tests and TypeScript passed.
- Post-review backend suite: 109 passed, two optional tests skipped.
- Scoped frontend ESLint, Python lint/format and hosted-asset tests passed.
- Hosted catalogue: 161 choices, 524 model/image dependencies, no failures;
  3,595 published files, 1,542,365,005 bytes, including six exact people files.
- Local browser: six current canonical buildings, native street, people and
  landscape; four-second HQ aerial preview and zero-cost preflight passed.
- Independent code review covered recovery, stale-scene spending, hidden
  reference state, LFS pointer compatibility and restored keyframe caching.

Evidence is outside source at
`C:/dev-artifacts/CityPrompt/omni-live-release-2026-10-21/`.
Generated video and build directories are not Git deliverables. The sparse
developer checkout contains historical unhydrated assets; the complete active
hosted packet is checked separately. No student-laptop performance claim is made.

## Production identity and rollback

Verified baseline: https://www.cityprompt.ca/ and
https://threed-platform-api.onrender.com/health both served
`cec2c93cd978ee2d82d66e13ed434b52f47a0fde`.
Repository: `aasedor/CityPrompt`, branch `deployment-version` (user-selected).
Existing Render services and baseline deployments:

| Service | Service ID | Baseline deployment |
| --- | --- | --- |
| API | srv-d6ehtvk1hm7c73f5ho9g | dep-dbb7iie7bikc73ese36g |
| Worker | srv-d6ehtvk1hm7c73f5hob0 | dep-dbb7imc9v7es73aefum0 |
| Frontend | srv-d6ehqtjh46gs73e28n50 | dep-dbb7kb67bikc73esjs30 |

Deploy the verified API and worker before the frontend. No database schema or
provider configuration change is required. The frontend uses the existing
`scripts/build_hosted_frontend.py --fetch-lfs` build process.

If frontend rollout fails, restore its recorded Render deployment while retaining
the compatible additive API/worker so any newly saved guide jobs remain
recoverable. A full service rollback to the recorded baseline is available through
normal Render deployment controls, but old code does not understand new guide
jobs; assess pending work before that action. Preserve database/object storage and
Git history. Rollback procedure is recorded, not exercised.

## Remaining release gates

At candidate preparation, push/deployment and paid live acceptance are pending.
Verify exact commit identities, people asset hashes and actual live UI recovery.
The user authorized exactly one guide and one four-second Omni aerial video,
combined provider cost ceiling US$2. Record attempts before dispatch and do not
repeat them automatically. Compare the result with its native source; AI footage
can reinterpret geometry despite a valid request.
