# From a new building to the student catalogue

Use this workflow for one exact RLASM 6.1 architectural-clay variant at a time.
The building generator and independent visual reviewer still do the creative
work. The promotion tools handle the repeatable wiring and detect mismatches.
No command below buys renders, changes account credits, self-approves a model,
or automatically commits or pushes Git.

Read [Runtime integration for every archetype](ARCHETYPE_RUNTIME_INTEGRATION.md)
before building. Complete [its per-variant review](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md)
alongside the local student trial and include the record in the delivery/PR.
The promotion CLI does not yet enforce that complete checklist: a preflight
pass cannot substitute for measured entrance, terrain, edit/recovery and visual
evidence. Keep failing or untested applicable checks open.

## 1. Build and independently review

Start a clean `codex/<building-name>` worktree from `origin/main`. Read
`CLAUDE.md`, `RLASM_LATEST_METHOD.md` and `RLASM_REPOSITORY_POLICY.md`.
Lock the exact parent and variant's authoritative front, oblique and top images.
Build a versioned GLB, inspect every required view and phone board, then obtain
a separate holistic architectural-clay review with zero unresolved P0/P1 issues.
Keep the source package, previous candidates and full review images outside Git.
Use immutable evidence storage accessible to the collaborators; a path on the
builder's computer is not itself an evidence backup.

The review JSON must name `candidate`, `model_sha256`, `reviewer`,
`architectural_clay_pass: true`, `holistic_review_performed: true`,
`unresolved_p0: 0` and `unresolved_p1: 0`. Its `inspected_files` list must include
the SHA-256 hashes of the exact front, oblique and top references. Preserve its actual bytes. The importer
copies the review into Git and checks its hash against the delivered model.
These fields record a real independent review; they are not a substitute for it.

## 2. Make a promotion package

From the repository root:

```powershell
python -m tools.catalogue_promotion template C:/dev-artifacts/my-building/promotion.json
```

The template borrows the bungalow's *structure*, not approval. Replace all
identity, reference hashes/paths, measurements, floors, descriptions and picker
settings with this building's data. Set `model_file` and `review_file` relative
to the package file (absolute paths also work). The importer computes model
bytes, hash, mesh counts and actual transformed native bounds from the GLB.
Do not manually duplicate those measurements into frontend code.

Picker settings:

- A permanent unique `id`; never reuse it for another design.
- `group_id` from the building groups in `frontend/src/features/calgaryCatalogue/guide.ts`.
- `fixed_native` for a complete landmark; `repeat_native` for supported detached homes.
- A plot width/depth at least the complete native envelope plus 3m total clearance.
- A maximum plot size and clear student-facing reshape description.

New detached parents must first be supported by `DETACHED_ARCHETYPE_IDS` in
the backend and tested for unscaled, contained home repetition. The preflight
reports this dependency rather than silently stretching a house. For an existing
parent, use a distinct exact variant and family identity for each new choice.
For a wholly new archetype, first add its authoritative catalogue definition and
reference images using the repository's text-insertion rule; this tool does not
rewrite `buildingArchetypes.json` or invent reference pictures.

## 3. Trial locally before publication

```powershell
python -m tools.catalogue_promotion trial C:/dev-artifacts/my-building/promotion.json
python -m tools.catalogue_promotion trial C:/dev-artifacts/my-building/promotion.json --apply
```

The first command is a dry run. The second copies the exact reviewed GLB and
review, appends one manifest entry and generates its picker card as a pilot.
CI deliberately rejects these unpublished trial entries. Trial setup does not
require or invent the later human publication approval.

Install on an isolated local database and storage service. Set connection
credentials through environment variables, not committed files or chat. The
seeder reads `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`,
`DATABASE_URL_SYNC`, and `MODEL_LIBRARY_SEED_OWNER_ID` (an existing user's UUID).
For the current student test stack the ports are storage **59002** and database
**55432**; do not assume those ports apply to another computer. Check which
backend the frontend actually uses before installing.

```powershell
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --local-trial --dry-run
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --local-trial
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --local-trial --verify
```

`--local-trial` requires an explicit candidate and loopback database/storage
addresses. `--verify` reads actual stored GLB bytes and public exact-variant
database bindings. It performs no writes. An HTTP 200 or matching file size
alone does not establish that the right model is installed.

Serve this worktree's frontend with the correct runtime assets, open
localhost:5174, and trial the building like a student on empty land. Record
the project URL, date, tester, exact model hash and screenshot/evidence locations
in `trial` in the package. Check:

- Card image/name and the exact placed variant.
- Ground contact from low and aerial cameras.
- Small and large plots, complete houses versus giant stretched houses.
- Rotation, save, reload and reopening the project.
- Close capture and a partially occluded or out-of-frame building.
- Browser console errors and visible responsiveness.

Before scaling a batch, also complete the mixed-scene and oversized-candidate
cases in the runtime review template. Use a separate genuinely vacant parcel for
a warehouse or other fixed-native asset that cannot plausibly fit the residential
pilot. Preserve its complete envelope and verify the terrain mode it advertises.
The [September 22 Currie trial](CURRIE_EMPTY_LOT_CATALOGUE_TRIAL_2026-09-22.md)
shows the expected neighbourhood/edit/landscape/export sequence and records why
paid image cost must be shown before generation.

The capture check can use the free direct-capture preview. Paid AI image/video
trials require the already agreed budget and remain a separate quality result;
do not describe a successful capture as a verified AI render. Record any LOD,
ground blending or performance limitations alongside the trial evidence.

## 4. Promote the exact successful candidate

Record the user's real approval in `approval`: `authorized_by: human_user`,
the actual `quote`, `date`, and exact `model_sha256`. Existing session approval
can be recorded; do not ask for it again. Keep all trial check values truthful.

```powershell
python -m tools.catalogue_promotion prepare C:/dev-artifacts/my-building/promotion.json
python -m tools.catalogue_promotion prepare C:/dev-artifacts/my-building/promotion.json --apply
python -m tools.catalogue_promotion check
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --dry-run
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate>
python tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --verify
```

Promotion upgrades the matching pilot using the same saved picker ID and model
URL. It can also import a previously reviewed and trialed package directly.
It rejects duplicate published identities, altered review/model bytes, missing
approval, incomplete trials, undersized plots and unsupported home families.
No other catalogue entries are removed. Existing database rows are skipped;
use verification to detect a stale binding and investigate it rather than
blindly adding `--replace`. Keep old object URLs for saved student projects.
Replacing an already published model is a separate versioned migration.

## 5. Check and merge one finite publication

```powershell
python -m pytest tools/archetype_compiler/tests/test_catalogue_promotion.py tools/archetype_compiler/tests/test_published_building_trio.py -q
python -m tools.catalogue_promotion check
cd frontend
npx vitest run src/features/pickPlace/publishedBuildingAssets.test.ts src/features/pickPlace/assetRegistry.test.ts src/features/pickPlace/catalogue.test.ts
npm run type-check
npm run generate:runtime-assets
npm run check:runtime-assets
cd ..
git diff --check
git diff --stat
git status --short
```

The runtime manifest must be generated with the required public asset tree
present. Hydrate only the exact source images/models needed for full model
checks; do not fetch the entire historic asset collection unnecessarily.
Run additional narrow backend tests if new-family assembly support changed.

Stage **only** the exact model, copied review, manifest, generated picker,
runtime manifest and intentional support changes printed by the workflow.
Never `git add .` across a mixed workspace or stage an external evidence folder.
Check `git check-attr filter -- <model-path>` reports `lfs`, and verify the
staged GLB is an LFS pointer using `git show :<model-path>` before committing.
Commit the coherent publication. With user authorization to publish:

```powershell
git fetch origin
git push -u origin <your-codex-branch>
gh pr create --repo aasedor/CityPrompt --base main --head <your-codex-branch> --title "Publish reviewed <building>" --body-file <reviewed-pr-description-file>
gh pr checks <PR-number> --repo aasedor/CityPrompt
gh pr merge <PR-number> --repo aasedor/CityPrompt --squash
```

Merge only after required checks pass; never bypass them. Routine CI checks
picker/review drift without heavyweight LFS downloads and exercises the full
promotion sequence against small real GLB fixtures. The hydrated local check
and actual student trial remain mandatory evidence in the PR.

On another local machine: pull main, hydrate the published models and their
locked reference images, run the clay seed dry run/install/verify against that
machine's services, then refresh City Prompt. **Git main, local database
installation and live website deployment are three separate checkpoints.**
Publishing to Git does not silently modify cityprompt.ca.

## Contributor prompt

> Build one exact RLASM 6.1 architectural-clay building using the canonical
> method. Follow docs/BUILDING_CATALOGUE_WORKFLOW.md and complete
> docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md against
> docs/ARCHETYPE_RUNTIME_INTEGRATION.md for this exact variant. Work on an
> isolated codex branch, keep generated evidence external, obtain an independent
> holistic review, use the promotion package tools, and trial the exact GLB
> on an empty local site. Preserve native scale and saved identities. Report
> the review, student trial, local install/readback, and Git publication
> statuses separately. Do not invent approval or publish unrelated candidates.
