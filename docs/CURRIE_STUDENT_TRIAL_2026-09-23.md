# Currie student trial — 2026-09-23

Disposable project: **Currie — Curved Streets Student Trial 2026-09-23** (`81da9efb-43bc-4a3f-8bf2-98d86126c50b`). Local URL while the trial server is running: `http://127.0.0.1:5178/projects/81da9efb-43bc-4a3f-8bf2-98d86126c50b`.

## Exercise result

- Started at the vacant CFB Currie field and drew a nine-corner, 4.7 ha boundary between the curving west road and straight east road. Chose **Clear site for redevelopment**.
- Placed five buildings: a Beltline brick mixed-use mid-rise, two modern infill homes and two post-war bungalows. Added a neighbourhood park with a pavilion and play area.
- Drew two 16 m Calgary local streets. Bent the main route by dragging its control point, made an internal T-junction, then extended the east branch to the mapped road edge using **Connect to a public road**. The Present screen recognized the proposed connection.
- Undid and redid a bungalow placement. The first Redo exposed a server failure restoring a deleted compiled-building link; the fix in `backend/app/api/v1/site_zones.py` was verified with focused tests and a fresh browser Undo/Redo sequence.
- Generated and applied **Neighbourhood gardens** (48 trees; about 37,310 m² of residual landscape after the road edit). The design and compiled landscape survived a page reload. In a close view, the detailed mid-rise, park furniture, sidewalks and planting resolved; at wide scale the five homes look small on a 4.7 ha site.
- **Export current 3D view · free** generated an exact, non-AI preview in roughly four seconds in the 1280×720 in-app browser. In ultrawide Edge, an offsite view timed out at about 53 seconds with a ground-alignment message; after **Focus Plan**, the preview completed in about 18 seconds.

## Image trial and export follow-up

- Generated two GPT Image 2.5 Sunburst images in the same disposable project: a close photorealistic park/mixed-use view and a wider documentary neighbourhood view. Both AI originals are visually appealing and were saved alongside their exact 3D source images in **Project Renders** (four saved files). The site, main building, bent street, T-junction and park remain recognizable in the documentary original, but the automatic fidelity checks flagged changed source structure and correctly returned the exact 3D capture as the safe result. Treat the AI originals as **illustrative, unverified** studies until visually reviewed; do not present them as exact design evidence.
- The first call used 212 tokens from a 328-token local test balance. A standard 1280×720 viewport brought the second call to 102 tokens. With 14 tokens left, a third paid 2.5 call was unavailable. A third, free exact 3D capture from overhead showed the irregular parcel, all five buildings, two streets and park, including the east public-road tie-in.
- The saved-render **Download render** link initially failed because `C:\Users\andre\Downloads` was a junction to unmounted `D:\C-drive-archive\Downloads`. The junction was renamed to `Downloads.broken-d-junction-2026-09-23` and replaced with a real folder on C:. A saved source render then downloaded as a valid 1280×656 PNG (1,181,917 bytes).
- The free exact-view preview's large data-URL link did not download in the in-app browser, even with the repaired folder. Its image download now uses a temporary Blob URL. The same control in Edge wrote a valid 2048×742 PNG (3,534,944 bytes) into Downloads. The in-app browser still did not save that Blob download; its host-specific handling remains unconfirmed for students using a regular browser.
- The typed-location error from project creation is fixed in `ProjectListPage.tsx`: creation now resolves a typed address before saving, and blocks with an actionable message if no location can be found. Two focused tests cover successful resolution and failure; frontend type-check passes.

## Release checks still open

1. **Image fidelity:** Both 2.5 finishes failed the automated source checks despite plausible visual results. Review the two saved source/original pairs to determine whether vegetation, lawn and tile blending are causing false positives, while retaining strict checks for building footprints, street topology and new structures. Do not loosen thresholds solely to pass these examples.
2. **PNG download:** Saved-render download is verified in the in-app browser; free exact-view download is verified in Edge. The in-app browser still does not save the free Blob export, so confirm whether that embedded browser needs a separate delivery path before treating it as supported.
3. **Site save feedback:** Saving the initial boundary showed a context-load 500 toast even though the boundary persisted and design continued. Reproduce before treating it as a release blocker.
4. **Local asset setup:** The three trial building GLBs existed in the recovery MinIO `student-studio-2027` bucket while the backend served `cityprompt-studio`. The mid-rise, infill and bungalow GLBs were copied to the served local bucket for this trial. Release setup should verify referenced runtime assets in its configured bucket; this was a local data repair, not a source change.
5. **Landscape after edits:** Extending the street invalidated the applied landscape, so it had to be generated and applied again. The Present step now detects the stale landscape and offers **Refresh site landscape**, which opens the boundary editor. This notice is covered by a focused UI test; the full edit-to-present path has not yet been repeated in the browser.

The street and site geometry are ideation-scale. This trial checked visual continuity and normal student operations, not survey-accurate access, legal parcel lines or construction-standard intersection geometry.
