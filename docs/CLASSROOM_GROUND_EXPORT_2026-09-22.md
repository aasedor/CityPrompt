# Currie ground edges, public connection and download — 22 September 2026

## Result

The bounded next stage uses the same disposable mixed-use/garden project
`3a52b4df-8508-408e-ac20-2f674d7c23b9` in the irregular vacant Currie parcel.
The conspicuous white prepared-site edge is closed with measured retaining
faces. A public-road extension now clears its own Google tiles and opens the
site retaining face. Its endpoint was extended through normal UI to the visible
existing road edge. The final exact PNG was downloaded through the real button.
This is a concept-design runtime check, not an engineered junction approval.

Branch: `codex/classroom-ground-export`, based on `f09da9700`.
Isolated services remain 5175/8001, with paid providers disabled.

## Source changes

- `preparedPublicRoadMasks` selects explicit, supported, bounded public-road
  connections at a prepared site. Both mask selection and the tile patcher now
  retain these outside footprints. Constructed bands own the cut; transparent
  setbacks retain Google ground. Unrelated, interior-only, invalid and opted-out
  roads do not receive this additional mask.
- The same footprints open the prepared boundary's retaining faces. Bent road
  polygons are triangulated before convex subtraction. The site outline and
  level do not move, and the remaining measured faces stay intact.
- Prepared street alignment preserves its complete measured cross sections
  instead of replacing endpoint heights with the fitted interior plane. Small
  cut/fill faces close the sides using those same measurements. No additional
  raycasts, invented deep skirts, weakened capture checks or saved road elevations
  were introduced. Natural-mode fitting remains unchanged.
- Review ground labels its existing option **Close gaps at site edges** and
  explains how to preserve the current design level. Applying remains explicit.

React review: derived road footprints and geometry are memoized; owned geometry
uses deferred disposal; no per-frame state updates or extra network requests were
added. The added terrain state resets with the existing edit/source lifecycle.

## Live verification

1. Reproduced the automated download cancellation in a new browser session.
   The same existing link downloaded successfully after setting the browser's
   download directory using native Windows backslashes and clicking normally.
   The downloaded bytes equalled the preview. This was test-harness path handling;
   the app's download implementation was not changed.
2. Used Review ground to apply 359 repeatable perimeter samples at the saved
   1102.226382517856 m level. The measured envelope is approximately 6.4 m fill
   and 3.8 m cut. The white foreground strip became a visible retaining face.
   Ground review rejects natural-mode discontinuities on this site; perimeter
   repeatability is a separate check, not a natural-ground pass.
3. Removing/restoring the edge setting through Apply, Undo and Redo persisted
   the expected absent/present profile; reload retained the final profile.
4. A low view exposed Google geometry burying the outside road. After the source
   repair, its pavement and sidewalks remained visible through the site boundary.
   An overhead review then showed that the prior endpoint was short of the actual
   road. Dragging its white handle from (759,269) to (759,243) extended it about
   15 m. Final endpoint: (-114.12500603335546, 51.017929233271); other route points
   remain unchanged. Undo restored the original route and Redo restored the new
   coordinates exactly. Reload and the low view from inside the site passed.
5. Editing the road reset residual landscaping to `placed_objects_only` under
   the existing workflow. Reapplied the free neighbourhood-gardens preset through
   Generate 3D Site Landscape / Apply landscape. No paid image was regenerated.
6. Reloaded, focused the plan and used Render this view → Image → Export current
   3D view → Download render. The actual saved PNG is 1440 × 936, 3,130,892 bytes,
   byte-identical to the preview. Both buildings, the teaching garden, extended
   street, free landscape and repaired edge appear. Final street status: ready;
   grounding issues: none; scene settled. Browser error inventory was empty.

The two building and garden designs remain unchanged, including their geometry,
recipes and source/representation hashes. Reapplying the free landscape refreshed
their `updated_at` and `community_3d.compiled_at` timestamps; preservation compares
all other fields. The intended design changes are the street endpoint and boundary
edge/landscape settings. The accepted GPT landscape project remains unchanged,
including timestamps (normalizing only renewed surface-image access URLs to paths).
QA account credits remained 4,057.

## Checks, evidence and limits

40 focused tests across eight files passed, including live tile-patcher mask
retention/removal, invalid road exclusions, concave openings, measured cut/fill
faces, missing measurements, ground controls and existing street transitions.
Type-check and focused ESLint passed. No backend, asset generation or RLASM method
changes were made. Human and machine evidence are paired in this report and
`CLASSROOM_GROUND_EXPORT_2026-09-22.json`.

External evidence: `C:/dev-artifacts/CityPrompt/ground-export-2026-09-22/`.
Key images: `edge-before.png`, `edges-applied.png`, `junction-before.png`,
`junction-connected-from-site.png`, `road-extended-top.png`, `final-export.png`.
JSON snapshots record the original, edge recovery, road Undo/Redo and final zones.
Local artifacts are not a shared durable backup; preserve them before migration.

Small close-view seams, existing Google cars/curbs and photogrammetry artifacts
remain. The saved profile represents sampled visible surfaces, not surveyed
earth. Natural-ground readiness, accessible curb design, many simultaneous
public connections and the existing 8-mask/32-edge shader capacity were not
accepted here. These changes do not authorize catalogue publication or Wave 2.

## Next practical stage

Run one short independent student trial: find a site, place several building
types and a park, edit the street, recover with Undo, finish landscaping, reload
and download a presentation. Record moments requiring help. Then fill specific
starter-catalogue gaps using the shared runtime checklist. Do not spend another
cycle polishing every close-view tile seam before that trial.
