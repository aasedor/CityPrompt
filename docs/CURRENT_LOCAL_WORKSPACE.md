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
