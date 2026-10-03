# Large civic local pilot

Two original church designs using RLASM 6.1 architectural clay. Source PNGs are
generated concepts, not photographs. The source locks record exact bytes and
panel roles. Gothic's conflicting lower-left reference panel is excluded;
the companion high-oblique roof image governs its roof.

Run from the repository root with Blender's Python environment:

```powershell
blender --background --python tools/large_civic_pilot/build_church.py -- --lock tools/large_civic_pilot/gothic-source-lock.json --output C:/dev-artifacts/CityPrompt/your-batch/gothic --version 5 --dry-run
blender --background --python tools/large_civic_pilot/build_timber.py -- --lock tools/large_civic_pilot/timber-source-lock.json --output C:/dev-artifacts/CityPrompt/your-batch/timber --version 2 --dry-run
```

Remove `--dry-run` to build one fresh candidate directory. Never overwrite a
reviewed or failed candidate. Each build exports native GLB geometry and renders
sixteen views of the actual reimported asset. Review the complete building and
phone board before independent verification and local registration.

The reviewed models and render evidence remain in the external batch directory
listed in `docs/LARGE_CIVIC_PILOT_2026-10-02.md`. To hydrate a preview from that
reviewed package without changing catalogue source:

```powershell
python tools/large_civic_pilot/register_local.py C:/dev-artifacts/CityPrompt/large-civic-archetypes-2026-10-02/gothic-v005 --public-root C:/path/to/preview/public --assets-only
python tools/large_civic_pilot/register_local.py C:/dev-artifacts/CityPrompt/large-civic-archetypes-2026-10-02/timber-v002 --public-root C:/path/to/preview/public --assets-only
```

Set `CITYPROMPT_PUBLIC_DIR` to that public directory before starting Vite. Restart
Vite after adding files: its public asset inventory can miss files copied after
startup while public-directory watching is disabled.

`register_local.py` without `--assets-only` adds a previously unregistered,
independently reviewed candidate to the local validation catalogue. It does not
publish, change the approved model library or activate seed data. Entrances and
bounded public circulation are embedded by `walking.py`; the tower is visual
architecture and has no climbing route. Models retain their authored dimensions.
