# Currie boundary exclusion labels — 20 September 2026

The fresh disposable student project `0320bb4f-395c-41c6-a6c0-ad28bb1572ef`
has an unnamed street, native infill plot and park. When a boundary edit would
exclude them, the API used to return three UUIDs. This made a correct 409
rejection hard to act on in the student editor.

The shared boundary validator now orders authored zones by saved sort/creation
order and gives unnamed objects stable type ordinals and their selected variant.
A street also shows its width. Saved user names still take precedence. No
containment tolerance or public-road exception changed.

After restarting the isolated local backend, an authenticated browser request
with a deliberately tiny candidate boundary returned:

> Outside the proposed boundary: Street #1 (Yield Street, 6 m), Building #1 (Infill Flat Roof Minimal), Park #1 (Neighborhood Park).

The response was 409. Readback confirmed the saved boundary coordinates and
revision were unchanged. The first live request against the pre-restart server
still showed UUIDs, confirming that the check had to run against the updated
process. Three focused backend tests passed. This was an API/browser response
check; a full drag-and-undo gesture was already exercised in the earlier
student workflow pilot and was not repeated for this copy change.

For future archetypes, populate a useful object name at authoring when one is
available. The generic validator fallback must still identify unnamed objects
without exposing an opaque database ID. Test a rejected boundary edit with at
least one candidate of each newly supported object type, and confirm the draft
and saved boundary survive.
