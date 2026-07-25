# Generate Your First Archetype Family

A five-minute, one-command walkthrough. You install Blender; everything else is
automated.

## 1. Install Blender (one time)

Download Blender (4.2 or newer — 5.x works) from <https://www.blender.org/download/>
and install it normally. No configuration needed: the tool finds it in
`C:\Program Files\Blender Foundation\` automatically. Installed somewhere else?
Set `BLENDER_PATH` to the full path of `blender.exe`.

You also need Python 3.11+ and Node.js 18+ on PATH (you already have both if you
run the app locally).

## 2. Pull the branch

```powershell
git fetch beeman
git checkout experiment/lego-assembly
```

## 3. Run one command

```powershell
.\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise"
```

First run installs frontend dependencies if they're missing (a few minutes).
After that a full family takes well under a minute. The command ends with
`=== SUCCESS - ... ===` and prints the output folder.

## 4. Look at the result

Open the printed folder, e.g.
`build\archetypes\nordic_timber_midrise\`:

- **`nordic-timber-midrise_preview.png`** — double-click; this is the fastest
  way to judge the architecture.
- **`nordic-timber-midrise_assembled.glb`** — drag into Blender, or any GLB
  viewer, to orbit around the assembled building.
- The four module GLBs (`_podium`, `_floor`, `_setback`, `_roof`) are the actual
  LEGO pieces the composer stacks.

## 5. Try another archetype or variant

```powershell
# every available id (223 building archetypes)
.\scripts\generate-archetype-family.ps1 -List

# a dark charred-timber variant with a gabled roof, 6 floors
.\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise" `
  -VariantId "nordic_timber_charred_wood" -Floors 6

# a mixed-use archetype with a glazed retail podium
.\scripts\generate-archetype-family.ps1 -ArchetypeId "rndsqr_terraced_mixed_use_midrise"
```

## 6. Put the family into the app

With the local backend running (Docker):

```powershell
python tools\archetype_compiler\import_manifest.py build\archetypes\nordic_timber_midrise `
  --email <your-login-email> --password <your-password>
```

This registers the modules in your model library. Then in the app: select a zone
with a generated building → open the zone panel → **Build with LEGO modules** →
**Auto assemble**. Save the recipe when you like the result.

## 7. Where to give aesthetic feedback

Open `grammar.json` in the output folder — the `notes` array explains every
derivation ("materials.primary: 'shou sugi ban' → #2e2a26" etc.). The quickest
feedback loop is:

1. Say what looks wrong on the preview PNG (e.g. "balconies too frequent",
   "glass too pale", "roof should be mono-pitch").
2. Those map to grammar fields (`facade.balcony_frequency`,
   `materials.glass.base_color`, `roof.type`) — tweakable in
   `tools/archetype_compiler/compiler.py` derivation rules for everyone, or
   per-run by editing `grammar.json` and re-running just Blender:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup `
  --python tools\archetype_compiler\blender_generate.py -- `
  --grammar build\archetypes\nordic_timber_midrise\grammar.json `
  --output build\archetypes\nordic_timber_midrise
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Blender was not found` | Install Blender, or `set BLENDER_PATH=C:\...\blender.exe`, or pass `-BlenderPath` |
| `frontend dependencies are not installed` | `cd frontend; npm install` (wrapper normally does this) |
| `Archetype '...' not found` | run with `-List`; ids use underscores (`nordic_timber_midrise`) |
| `validation: FAIL` | read `validation_report.json` — it names the file and the measurement that failed |
| Import says 401 | check email/password; the backend must be running on localhost:8000 |
