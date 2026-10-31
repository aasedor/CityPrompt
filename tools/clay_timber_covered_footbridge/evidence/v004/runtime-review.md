# Timber covered footbridge v004 — bounded local runtime review

Exact GLB SHA-256: `0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad`. Local asset: `claude_public_realm:timber-covered-footbridge:0dbeb2731dbe`. Exact source: `urban_pedestrian_footbridge / variant_2`; runtime variant `urban_pedestrian_footbridge_v2`. Original pinned family/GLB unchanged; this is a newly constructed v004.

Scope: ordinary Edge student simulation at 1681 × 1233, localhost:5176/API:8003, project `467025e9-4f3c-432c-ba76-066a52467eb2`. The user's 5174/8000 stack is unchanged. Review follows `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and its template; production/publication remains gated.

| Gate | Status | Evidence and limits |
| --- | --- | --- |
| C1 Exact identity | PASS | Picker selected exact variant; HTTP GLB/thumbnail/hero hashes match source and manifest; frontend/backend manifests match. |
| C2 Dimensions/transforms | PASS | Native 43.6216 × 8.87 × 7.55 m; fixed 44 × 9.2 m plot. UI rotation 0 → 15°, no corner handles, width/depth disabled. |
| C3 Ground support | NOT TESTED | Level prepared site only. Pixels show seated piers, abutments, bounded banks and grade-connected approach stairs; no sloped terrain matrix. |
| C4 Late results | NOT TESTED | No delayed-load or interrupted-save race simulation. |
| C5 Pedestrian/public-road access | NOT TESTED | Both stairs pass source visual contact review; actual first-person stair traversal, accessibility and external road approaches untested. |
| C6 Edit/Undo/save/reopen | PASS | Placement, 15° rotation, Undo 0°, Redo 15°, clean-tab reload preserving dimensions/rotation, Delete and Undo restoring the same settings. Move/drag and interrupted-save cases remain untested. |
| C7 Failure/recovery | NOT TESTED | Exact source/hero registration rejection and identity guards tested; full live failure/retry matrix untested. |
| C8 Capture | NOT TESTED | Free exact-3D source PNG content captured and visually inspected. Actual browser Download button, paid images/videos and all low/aerial viewpoints untested. |
| C9 Controls | PASS | Fixed dimensions and only supported rotation/move affordances; no resize vertices. Generic rotate-handle label still says building (minor inherited wording). |
| S1 Metric section | PASS | Exact measured native assembly and bounded plot; teaching dimensions, no civil/engineering compliance claim. |
| S2 Arbitrary routes/junctions | N/A | Fixed native bridge object; stretching, bending and automatic intersections are unsupported. |
| S3 Connection/grade | NOT TESTED | Inferred steps connect prepared grade visually; surveyed or adjoining cycle/road connections untested. |
| S4 Clearance/targets | NOT TESTED | No complete clearance or navigation matrix. |
| Building/park-specific gates | N/A | Street/crossing delivery, not a building or park. |

Independent architectural-clay review inspected all three references, 20 actual GLB-reimport renders and four phone boards: zero P0/P1, eight recorded P2s. Source review does not grant runtime activation. The local rehearsal binding retains pending runtime approval and cannot enter production discovery.

Pixel evidence and checksums: `C:/dev-artifacts/CityPrompt/claude-crossings-practical-20261029/timber-v004/`. Files labelled screenshot contain app UI; `exact-3d-source.png` is a free original source capture without AI changes. Visible rough background geometry belongs to the Google context tiles. No paid generations, credit purchase, push or deployment.
