# Git history migration runbook

## Status

Prepared, not executed. Ordinary cleanup must not rewrite shared history.

The current object database contains approximately 8.60 GiB of packs and zero
reported garbage. Historical raw Git content includes roughly 5.7 GB of PNG,
430 MB of JPG, 324 MB of JSON, 98 MB of DOCX, and 19 MB of PPTX data above
1 MiB. A normal `git gc` cannot remove reachable history and may require
substantial temporary disk space.

## Preconditions

Do not schedule cutover until every item is true:

- PRs that must survive are merged or rebased onto the freeze point;
- all collaborators acknowledge a write freeze and mandatory reclone;
- historical exposed credentials, including the documented Cloudflare
  credentials, are rotated;
- GitHub branch/tag protection and Actions requirements are recorded;
- an external destination exists for non-runtime evidence;
- required runtime LFS objects are available and `git lfs fsck` passes; and
- free disk space is at least twice the mirror size plus expected LFS staging.

## Rehearsal

Use a separate mirror outside OneDrive. Never rehearse in the recovery
workspace.

1. Fetch and record all heads, tags, notes, pull-request refs required for audit,
   and LFS objects from `aasedor/CityPrompt`.
2. Create two independent backups:
   - a read-only mirror copy; and
   - a `git bundle --all` with a recorded SHA-256.
3. Export a pre-migration inventory containing ref names/OIDs, object counts,
   largest blobs, LFS OIDs, and protected release tags.
4. Define the migration map:
   - runtime images/models retained in Git move to Git LFS;
   - rejected renders, old office documents, and generated experiments move to
     content-addressed artifact storage;
   - required source text remains ordinary Git; and
   - active RLASM keeper evidence remains compact and LFS-backed.
5. Run `git filter-repo` or `git lfs migrate import --everything` only in the
   rehearsal mirror with an explicit reviewed include/remove map. Do not use an
   extension-only rule when an extension mixes source and generated content.
6. Expire reflogs and repack only inside the disposable rehearsal mirror.
7. Write an old-OID/new-OID mapping and compare every expected ref.

## Validation gates

A rehearsal passes only when all are true:

- `git fsck --full` passes;
- `git lfs fsck` passes after a fresh LFS fetch;
- head and tag counts match the approved ref inventory;
- every current keeper manifest, source hash, and review record resolves;
- the runtime asset manifest resolves after LFS hydration;
- a depth-one fresh clone and a full audit clone both work;
- backend, frontend, browser, Docker, compiler/RLASM, and blob-policy checks
  pass; and
- the rewritten repository and LFS size reductions are measured.

Keep the original mirror and bundle until at least one release has shipped from
rewritten history.

## Cutover

Cutover requires a new explicit user approval after rehearsal results are
reviewed.

1. Announce and enforce the remote write freeze.
2. Disable merges and automation that can write refs.
3. Take a final mirror, bundle, ref inventory, and SHA-256 checkpoint.
4. Apply the already validated rewrite to the final mirror.
5. Force-update only the approved `aasedor/CityPrompt` heads/tags.
6. Re-enable branch protection and required checks.
7. Require every collaborator and deployment worker to reclone; do not merge
   old clones back into rewritten history.
8. Run the fresh-clone validation suite again against the live remote.

## Rollback

If validation fails before reopening writes, restore refs from the final mirror
or bundle and verify their recorded OIDs. Once collaborators write new commits
on rewritten history, rollback becomes a coordinated migration of its own.
