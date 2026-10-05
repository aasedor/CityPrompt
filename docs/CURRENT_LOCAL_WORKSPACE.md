# Confirmed local CityPrompt version

On 2026-10-04, the user inspected Currie Commons and confirmed that the version
at `http://127.0.0.1:5176` is the version to preserve during workspace cleanup.

| Binding | Confirmed value |
| --- | --- |
| Source | `C:/Users/andre/.codex/worktrees/public-realm-recovery/CityPrompt` |
| Branch | `codex/public-realm-recovery` |
| Source commit | `0d7a9ddad515b862bdd332656738fbee0962f2c6` |
| Frontend / API | `http://127.0.0.1:5176` / `http://127.0.0.1:8004` |
| Startup helper | `C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03/start-recovered-render-trial.ps1` |
| Delivery packet | `C:/dev-artifacts/CityPrompt/catalogue-delivery-2026-10-04-v004` |
| Fixture receipt | `C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03/main-app-runtime/sealed-ten-fixtures.json` |
| Fixture receipt SHA-256 | `43fb056d74d449e288f9536ca448a3e49f09429fcde4a65534bbdbac66966303` |

The source, asset bindings, API/database and object storage form one running
version. Use its startup helper when returning to this version. A checkout's
name, modification time or branch name alone does not establish that it has
the same models, picker images, saved projects or walking behavior.

The original OneDrive checkout contains pre-existing user changes and separate
local-Qwen work. Preserve it independently. The cleanup source changes live on
`codex/cleanup-structure-2026-10-04`; its sparse checkout is for maintenance.
Hosted releases and `main` have not been changed by this cleanup. The paused
catalogue expansion remains paused, and unapproved prototypes remain local.

Worktree retirement records, verified content-addressed snapshots and a Git
history bundle are under `D:/CityPrompt-preservation/cleanup-2026-10-04`.
Cloud archive copies belong under
`G:/My Drive/CityPrompt/Archives/cleanup-2026-10-04`.
Future reference-image collections and their archive index belong under
`G:/My Drive/CityPrompt/Reference Library`.
Private configuration stays in local preservation storage.

Follow [the storage policy](REPOSITORY_STORAGE_POLICY.md) when creating new
worktrees or promoting reference material into runtime delivery.

## Completed cleanup checkpoint

The cleanup reduced the original 66 registered worktrees to nine. One sparse
maintenance checkout was added and 58 old checkouts were retired. Each retired
checkout has an independently verified snapshot and an archive Git ref; original
branches remain available. Common payloads are stored once by SHA-256.

| Retained checkout | Reason |
| --- | --- |
| Original OneDrive checkout | Preserve user changes and the separate local-Qwen initiative |
| `public-realm-recovery` | User-confirmed running version |
| `neighborhood-refinement` | Preserve paused work |
| `C:/dev/CityPrompt-place` | Preserve pending source and shared dependencies |
| `C:/dev/CityPrompt-sol-empty-lot-trial` | Dependency provider for the retained house trial |
| `C:/dev/CityPrompt-student-design-transformation` | Preserve pending source and dependencies |
| `calgary-elevation-trial` | Dependency provider for the confirmed app |
| `house-flex-pilot` | Preserve the older house version the user likes |
| `C:/dev/CityPrompt-maintenance` | Verified cleanup policy and delivery-check changes |

Normal development should use two to four active checkouts. Nine remains the
hard budget while these dependency providers and pending initiatives are kept.
The house trial's dependency junction now points directly to the retained provider,
instead of passing through a retired checkout.

Four legacy folders under the original checkout's ignored `artifacts/worktrees/`
remain as preserved source/evidence directories, with no active Git registration
or `.git` marker. Windows denied normal cleanup or OneDrive could not supply
some original files. Unverified originals and protected test output were retained;
no permission or ownership changes were made. Their exceptions are recorded in
the external snapshot and retirement receipts.

The final read-only audit passed 105 catalogue choices, 359 distinct image/model
dependencies, and all 19 expected Model Library readbacks. The saved-project audit
passed all 32 dependencies present at its checkpoint. Users may continue editing
projects and generating renders independently while cleanup checks run.

The future-reference index records 2,789 original image paths and 244 distinct
image payloads. It is stored in the external Reference Library with a hash-checking
extractor. The detailed cleanup and restore receipts live in the dated archive;
private configuration and the full Git-history bundle remain on D: only.

The startup helper checks the confirmed clean source commit and the frontend's
sealed fixture receipt. Review a changed source/runtime pairing before updating
those locks. Cleanup does not automatically merge the maintenance branch into
`main` or publish a new release.
