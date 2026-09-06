# Sandstone courtyard civic hall

RLASM 6.1 exact-source architectural clay. Candidate **calgary-sandstone-heritage-clay-v007** passed independent architectural review with zero unresolved P0/P1 findings. This is a local trial asset, not an approved public catalogue entry.

The GLB, authoring blend, three source images, 13 full-resolution GLB-reimport renders and review boards live outside Git at `C:/dev-artifacts/CityPrompt/building-trio-2026-09-06/sandstone-v007`. Small source locks, assumptions, hashes and reviews are retained here. Previous candidates remain preserved externally.

## Reproduce

Run Blender 5.2 with `--background --python tools/catalogue_sandstone_pilot/build.py -- --source-root <hydrated CityPrompt source> --output <new external candidate directory> --version <new number> --dry-run` first. Remove `--dry-run` for the finite build. Then run `python tools/catalogue_sandstone_pilot/proof.py <directory>` and the RLASM skill's `validate_candidate.py`. All source views must already be hydrated. Never overwrite a candidate or treat the deterministic checks as visual approval.

## Trial

The separate `codex/catalogue-trio-local-trial` branch provides the gated catalogue entries and isolated-database installer. The local trial project is `0c5c0816-3c68-4eea-8b74-150b84c59259`. No paid render calls or production seed modifications are part of this checkpoint.

Runtime dimensions come from the actual GLB bounds in `candidate.json`. This civic landmark retains its complete native dimensions when moved or rotated; it does not stretch. Native zero meets the building foundation. City Prompt supplies site elevation.
