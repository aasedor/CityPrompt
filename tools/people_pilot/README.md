# Local animated people pilot

Three bounded adult derivatives for the photographic video pilot. These scripts
do not register a catalogue, publish assets, download paid models or call an AI
provider. Heavy inputs, editable Blender files, exact runtime GLBs and free QA
renders stay under
`C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/characters/`.

The [provenance manifest](character_provenance.json) records the official free
Standard archives, CC0 license-file hashes, exact runtime hashes, dimensions,
materials, bones, animation durations, decoded cost estimates and limitations.
The source anatomy, hairstyles and animation are Quaternius derivatives. The
simple clothing geometry and palette are original pilot work. Free Standard
includes the adult `Superhero` base meshes; the paid `Regular` bases were not used.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/people_pilot/build_characters.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/people_pilot/measure_characters.py
python tools/people_pilot/verify_characters.py
```

`build_characters.py -- --only people-pilot-commuter` rebuilds one actor. Preserve
the official extracted archive layout below `characters/sources/`. The output
uses metres, Y-up and +Z forward, with feet at the local ground datum. `Walk`
maps to source `Walk_Loop` (1.333333 seconds); `Idle` maps to `Idle_Loop` (2.5
seconds). A root-bone vertical correction measured at every 24 fps frame adapts
the source bare-foot motion to the authored sneakers. Independent skinned
vertices are measured at 41 times per clip after GLB re-import. The measurement
excludes Blender's generated bone-display helper mesh, which is absent from
the exported GLBs.

At 41 uniform cycle samples, the estimated distance per walk cycle is 1.293318 m
for commuter, 1.325206 m for neighbour and 1.264602 m for creative. This is the sum
of the two ankle forward-axis ranges, a practical initial calibration rather
than measured ground locomotion. At an authored translation speed `v`, set the
clip playback rate to `v * durationSeconds / strideEstimateMetresPerWalkCycle`.
Root correction preserves the source pelvis bob. Between-frame sole residuals
range from -2.04 mm to +6.48 mm; idle sole residuals are below 0.007 mm.

The artifact folder contains `preview.html` and `serve_preview.py`; start the
server to review all three at `http://127.0.0.1:9029/preview.html`. The page has
Walk/Idle, time seek, pause, orbit and a turntable. `qa/{id}.png` files show the
idle pose. The integrated local pilot passed browser placement, selection,
move/rotate/delete, undo/redo and save/reload checks. Six four-second Omni
trials and the deterministic capture checks are recorded in the
[pilot report](../../docs/video-pilots/PEOPLE_VIDEO_PILOT_2026-10-21.md) and
[hash-bound results](pilot_results.json). The comparison player is
`http://127.0.0.1:18121/#take-6`; Add Details → People is available in the local
app on port 5184. These checks do not establish exact photographic identity,
unchanged architectural detail or human approval for production publication.

These models remain visibly stylized, with simple collar/shoulder seams, no
cloth simulation and source hand animation. Do not describe them as original
human anatomy, motion capture or photorealistic source characters.
