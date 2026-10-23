# People actions and simple Omni video

User direction: complete the previously requested People category, about twenty
additional characters, saved actions that guide images and videos, and a video
menu using only Omni 1.1 with two or three primary steps. The user explicitly
delegated design choices to the recommendation; no new design approval is needed.

## Design

Extend existing Add Details, the three licensed rigged adults, exact capture,
project-details saves/Undo/Redo and paid video attempt machinery. People gets a
prominent first category tile and a persistent shortcut. Keep placement, selection
highlight, movement, rotation and deletion consistent with other details.

Selected people expose one labelled Action selector. Fifteen stable action IDs:
`standing`, `walking`, `running`, `sitting`, `talking`, `lying_down`, `waving`,
`using_phone`, `reading`, `waiting`, `looking_around`, `pointing`, `stretching`,
`dancing`, `cheering`. Save `people_action` per prop. Missing legacy values mean
`standing`; invalid values must not silently become other actions. Preserve the
field through every editor, move/copy/history path and backend round trip.
Actions guide still-image and Omni prompts. Native posed/animated previews must
represent the supported action honestly; no pathfinding, chair detection or
working-door choreography is claimed. Seated actors need student-provided seats;
lying actors use their placement surface. No automatic crowd or background work.

Create twenty additional adult designs with tasteful contemporary clothes,
mostly athletic/fit proportions, varied faces/hair, skin tones, heights and
outfit silhouettes. Adapt the already-verified CC0 sources. Preserve original
three IDs and bytes. Export lightweight metre-scale +Y-up rigs, exact hashes,
license/source provenance, measured dimensions and actual-model thumbnails.
Generate externally, then promote only reviewed files into the established local
public tree. No paid generation or new dependencies/resources are authorized.

Video main flow: choose a shot (street / aerial / follow a person), optional
plain-language detail prompt, Preview (free preparation and validation), Generate
(explicit paid Omni 1.1 submission with quoted cost). Sensible default route uses
current view; two route endpoints need not be manually drawn for the default
shot. Preserve manual route editing and quality/duration/reference options under
Advanced. No alternative video-provider/control-mode selectors in student UI.
Preserve old video history/replay; changing controls, scene or people actions
invalidates prepared inputs. No automatic paid retries or guide purchases.

## Acceptance

Local only; do not push or deploy. Check new character assets and all action IDs,
pose/grounding, independent instance state, action persistence/undo/editors,
image/video prompt propagation, explicit cost/preflight and stale-scene rejection.
Use current actual app for catalogue, authoring, reload and free preview/capture.
Run focused tests, TypeScript, scoped lint, relevant backend tests and independent
review. Report paid AI output and unavailable hardware as untested. Preserve the
previous park integration and all inherited hydrated LFS changes.
