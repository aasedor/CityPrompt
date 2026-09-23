# Currie student trial — 2026-09-23

Disposable project: **Currie — Curved Streets Student Trial 2026-09-23** (`81da9efb-43bc-4a3f-8bf2-98d86126c50b`). Local URL while the trial server is running: `http://127.0.0.1:5178/projects/81da9efb-43bc-4a3f-8bf2-98d86126c50b`. No paid image generation was used.

## Exercise result

- Started at the vacant CFB Currie field and drew a nine-corner, 4.7 ha boundary between the curving west road and straight east road. Chose **Clear site for redevelopment**.
- Placed five buildings: a Beltline brick mixed-use mid-rise, two modern infill homes and two post-war bungalows. Added a neighbourhood park with a pavilion and play area.
- Drew two 16 m Calgary local streets. Bent the main route by dragging its control point, made an internal T-junction, then extended the east branch to the mapped road edge using **Connect to a public road**. The Present screen recognized the proposed connection.
- Undid and redid a bungalow placement. The first Redo exposed a server failure restoring a deleted compiled-building link; the fix in `backend/app/api/v1/site_zones.py` was verified with focused tests and a fresh browser Undo/Redo sequence.
- Generated and applied **Neighbourhood gardens** (48 trees; about 37,310 m² of residual landscape after the road edit). The design and compiled landscape survived a page reload. In a close view, the detailed mid-rise, park furniture, sidewalks and planting resolved; at wide scale the five homes look small on a 4.7 ha site.
- **Export current 3D view · free** generated an exact, non-AI preview in roughly four seconds in the 1280×720 in-app browser. In ultrawide Edge, an offsite view timed out at about 53 seconds with a ground-alignment message; after **Focus Plan**, the preview completed in about 18 seconds.

## Release checks still open

1. **PNG download:** The preview's **Download render** link did not produce a detectable browser download event or file in the Windows Downloads folder in either browser. This could be browser-automation handling of data-URL links; verify with a manual browser click or change the handoff before calling the end-to-end export complete.
2. **First-use location:** Typing the Currie address into project creation without selecting the autocomplete suggestion left the project at its downtown default. Selecting the suggestion in Edit correctly saved `51.01848, -114.12376`. Make the required selection clearer or accept the typed address deliberately.
3. **Site save feedback:** Saving the initial boundary showed a context-load 500 toast even though the boundary persisted and design continued. Reproduce before treating it as a release blocker.
4. **Local asset setup:** The three trial building GLBs existed in the recovery MinIO `student-studio-2027` bucket while the backend served `cityprompt-studio`. The mid-rise, infill and bungalow GLBs were copied to the served local bucket for this trial. Release setup should verify referenced runtime assets in its configured bucket; this was a local data repair, not a source change.
5. **Landscape after edits:** Extending the street invalidated the applied landscape, so it had to be generated and applied again. The workflow behaved consistently, but students need a visible prompt to regenerate it before presentation.

The street and site geometry are ideation-scale. This trial checked visual continuity and normal student operations, not survey-accurate access, legal parcel lines or construction-standard intersection geometry.
