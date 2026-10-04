# Repository and storage policy

CityPrompt source includes application code, runtime assets, database migrations,
dependency locks, tests, build tools, and the small metadata needed to reproduce
approved models. These are intentional development requirements. New source
commits must pass the existing blob policy and asset-delivery checks.

Future reference photographs, alternative designs, render experiments, old
review images, and retired checkout snapshots belong in external storage.
Keep a small provenance manifest with original name, SHA-256, intended use,
approval state, and archive location. A future reference does not become an
advertised catalogue asset until its reviewed runtime delivery passes checks.
Required current assets and saved-project dependencies must remain available.

## Storage locations

| Purpose | Location |
| --- | --- |
| Active source | One named initiative per local Git worktree |
| Runtime delivery | Versioned delivery manifest and the configured public/model storage |
| Temporary local evidence | `C:/dev-artifacts/CityPrompt/<initiative>` or ignored `artifacts/` |
| Future references | `G:/My Drive/CityPrompt/Reference Library/<family>` |
| Cloud preservation | `G:/My Drive/CityPrompt/Archives/<dated-batch>` |
| Local restore staging | `D:/CityPrompt-preservation/<dated-batch>` |
| Private environment files | Local private staging; never plain-text cloud archives |

Google Drive is archive storage. Keep executable source, dependencies, databases,
and the assets needed by a running app on reliable local/runtime storage.
Reading back a file on G: verifies the local Drive filesystem copy; it does not
prove the upload has completed. Record cloud confirmation separately, using
the Drive web app or another authoritative cloud receipt.

## Retiring a worktree

1. Record the exact root, branch, HEAD, index, sparse settings, pending source,
   ignored evidence, and links. Check processes, paused jobs, and inbound links.
2. Preserve all unique files and commits. Reinstallable dependencies and transient
   caches may be excluded explicitly. Keep private configuration in local storage.
3. Verify every preserved payload by SHA-256 and test restoring a pilot to a new
   directory. Retain an independent verified copy while cloud uploads are pending.
4. Remove only the explicitly inventoried checkout. Handle junctions as links;
   never recurse into their targets. Keep branch history and asset provenance.
5. Recheck worktree count, live catalogue delivery, saved-project dependencies,
   and remaining dependency links. Record actual disk space separately from
   logical file sizes.

`scripts/archive_content_addressed.ps1` supports ordinary physical evidence
directories. It rejects junctions and stores inside a source. Worktree snapshots
also need Git/index/private-configuration preservation before retirement.
An archive is not permission to delete an unverified or inaccessible source.

## Workspace budget

Use two to four active worktrees for normal development; nine is the hard local
budget. Keep temporarily necessary dependency providers until their consumers
are migrated and verified. Run:

```powershell
pwsh -File scripts/audit_git_worktrees.ps1 -SummaryOnly -FailOnBudget
```

Before creating a worktree, its addition must still leave the total at nine or
fewer. Completed work should leave a branch/commit and an archive receipt,
instead of an indefinitely running preview or another full checkout.

## Preventing regressions

Record the source commit, launcher, frontend public directory, API/database,
model storage, and delivery-manifest hash together. A good version is this
complete combination. Switching only a branch or launcher can pair current UI
with old models or unavailable asset paths. Validate the configured combination
before promoting it; cleanup by itself does not fix incompatible launches.
Keep failed/missing assets visible to delivery checks rather than silently
substituting older catalogue versions.
