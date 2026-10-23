# People and Claude catalogue release checkpoint

This checkpoint supersedes the pending activation status in the earlier trial
notes. It records local verification; it is not a production deployment receipt.

## Approved scope

The user approved publishing the original 93 People files, followed by 54 exact
additional files (89,588,125 bytes) under the existing LFS rules. The latter
includes twelve relaxed-standing People replacements, eighteen building GLBs,
and twelve public-realm GLB/preview pairs. No LFS policy change is included.

Eighteen Claude buildings are active in the canonical library and picker.
The original 63 library entries retain their metadata. Three parks and nine
fixed street scenes have complete runtime and visual records in the versioned
public-realm registry. Disabled parents, the held plaza and five Wave K candidates
remain excluded. Park-only derivatives omit the surrounding city buildings.

Fixed scenes move and rotate as complete assemblies on prepared level sites.
They do not become stretchable street sections or automatic network connections.
Unclassified additions retain zoning review status; no permitted uses are inferred.
Generic terrain, automatic approach connections, accessibility certification,
student-laptop and mobile performance remain outside the completed evidence.

## Executed local checks

- All 3,637 frontend tests across 436 files passed with two workers and unchanged
  timeouts; TypeScript passed. The bounded run avoids resource contention in the
  53-street paginated interaction test. Earlier failing logs are preserved.
- 173 hosted asset, LFS, promotion, seed, catalogue-readback and fixed public-realm
  backend tests passed; seven environment-dependent cases skipped.
- Fifteen Node delivery/registry tests passed; the additional changed runtime
  modules passed scoped ESLint. Existing generated precision diagnostics are
  documented separately rather than suppressed.
- All eighteen buildings were placed, rotated, checked at minimum/large plot
  sizes and saved/reloaded. Every model has inspected aerial and pedestrian
  captures. A mixed scene retained five compiled placements and inclusive People;
  delete/undo and People rotation survived reload.
- The 54 additional local HTTP payloads returned exact sizes and SHA-256 hashes.
  Small evidence snapshots are in `docs/showcase/claude-release-2026-10-23/`.

## Paid image checks and honest limits

The three authorized Sunburst image checks completed: mobility, relaxed family/
older adults, and an aerial development. No additional paid video was generated.
The final two provider originals visually preserve clothing and aids or improve
the surrounding photogrammetry, respectively. Their automated geometry checks
did **not** pass. The app correctly retained the clean 3D result and the separately
reviewable AI original. These are not certified faithful final renders, and this
release does not weaken the fidelity checks to accept them.

Immutable receipts and images are external under
`C:/dev-artifacts/CityPrompt/claude-live-release-2026-10-23` and the adjacent
`people-live-release-2026-10-23` directory. Test-only local app tokens were topped
up for the remaining authorized aerial check; no production balance or provider
subscription was changed.

## Deployment and rollback gates

Production is `https://www.cityprompt.ca`, repository `aasedor/CityPrompt`, branch
`deployment-version`. Before this release all three existing Render services
were verified at `056608657b2eb7582ad6dc2073f7c4426b5d87b4`:

| Service | Service ID | Baseline deployment |
| --- | --- | --- |
| API | srv-d6ehtvk1hm7c73f5ho9g | dep-dbdc5v3rjlhs73cp219g |
| Worker | srv-d6ehtvk1hm7c73f5hob0 | dep-dbdc6voae00c73flutbg |
| Frontend | srv-d6ehqtjh46gs73e28n50 | dep-dbdc8et9fdbs73akcijg |

Promotion still requires a clean hosted build of the exact commit, existing
private storage publication and readback for the finite eighteen-building cohort,
then the existing Render deployment process and live identity/workflow checks.
No migration, provider replacement, Blueprint synchronization or new paid resource
is required. Rollback uses the existing Render deployment history and the recorded
baseline; inspect active jobs before replacing API/worker processes. Preserve the
database, uploaded objects, environment and domains during rollback.
