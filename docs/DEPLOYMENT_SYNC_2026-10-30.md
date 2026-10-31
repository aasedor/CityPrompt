# Deployment sync — 30 October 2026

The user requested synchronizing the current tested version with the existing
`deployment-version` release. Preserve the live database, bucket, domain, JWT
secret, all 191 existing placements and the current service configuration.
Use PR #38; do not merge the distant Claude authoring branch.

## Newly completed publication cohort

The seven exact approved candidates below completed a bounded browser simulation
in project `77c257a6-a2c4-45b0-8099-582338966c5d` on the isolated QA application.
Their packages contain the user's existing exact-byte approval, current trial
records and the limitations. Canonical activation uses the existing promotion
CLI; no approval or publication guard was removed.

| Model | Exact candidate |
| --- | --- |
| Crucible climbing centre | `clay-climbing-crucible-clay-v004` |
| Overhang climbing centre | `clay-climbing-overhang-clay-v007` |
| Reef climbing centre | `clay-climbing-reef-clay-v009` |
| Sandstone clock-tower block | `clay-calgary-sandstone-heritage-clay-v006` |
| Modern fire station | `clay-cantilever-fire-station-clay-v010` |
| Regional teaching hospital | `clay-braced-frame-hospital-clay-v006` |
| Student residence tower | `clay-student-residence-tower-clay-v004` |

Evidence and exact free 3D captures are in the private review folder:
https://drive.google.com/drive/folders/19o9gPoRPIgGLi4bZNoZY2iS62Pxah0eD.
Screenshots and source originals are separately labelled. No paid images or
videos were submitted. The boundary is an API-prepared vacant QA fixture;
building selection, placement, rotation, reopen and capture used ordinary UI.
Half/native/triple plot limits are separate authenticated API proofs, not UI
resizing evidence. Accepted plans preserve unit model scale; half-size plots
reject. Low close views also exercise partially out-of-frame façades.

These trials found and repaired a real Q/E regression: rotating raw longitude
and latitude distorted fixed building plots at Calgary's latitude, causing
detailed models to fall back to massing. Keyboard rotation now uses local metres.
All seven retain detailed assemblies after keyboard and numeric rotation and
reopen. Natural terrain, interior navigation, independent novice studies,
construction/accessibility compliance and paid-output fidelity remain unverified.
Per-variant mixed-route and deletion/recovery stress remains explicitly open.

The publisher also now writes metadata through temporary files and atomic
replacement. Windows background Git readers can hold memory mappings that reject
truncation. A finite retry handles that conflict; persistent failures preserve
the last valid manifest and remove only this operation's new deliveries.

## Production profile and cutover

With `VITE_CLAUDE_FIVE_TRIAL=true`, production discovery has 199 choices. Keep
that existing flag for parity with the five already-live showcase models. This
count includes the newly discoverable native 40-storey option and these seven
buildings. Development remains a separate validation collection; this release
does not silently publish held teaching pilots, bridge-route derivatives or the
known-P1 stepped plaza.

Follow `docs/RENDER_RELEASE_2026-10-13.md` and its predecessor. Before cutover:

1. Require passing current-head CI and production asset/build checks.
2. Inspect actual Render auto-deploy settings and active jobs. The October 23
   receipt recorded auto-deploy Off; that historical receipt is not current
   configuration proof.
3. Preserve a production database/media backup and the prior deployments.
4. Install only these exact candidates with the explicit canonical clay-library
   manifest and finite `--candidate` selections. Dry-run first; no `--replace`.
   Check missing original bindings (including native 40) with the full hosted
   verifier, and restore only exact approved bytes if needed.
5. Verify exact storage bytes, database bindings and hosted staging browser
   behavior before updating API, worker and frontend together.
6. Verify frontend `/version.json`, backend `/health` and `/ready`, the production
   picker and a saved project after cutover. Git synchronization alone does not
   establish a live update or install private models.

At preparation time, live frontend/API still identify `62e31ad62`. Render access
requires completing the existing GitHub 2FA verification or connecting the Render
plugin. No live deployment has been claimed from the local trial results.
