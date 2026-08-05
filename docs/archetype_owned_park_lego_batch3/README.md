# Archetype-owned park LEGO batch 3

This reviewed batch applies the composition methodology recorded in
`docs/PARK_COMPOSITION_API_STUDY_2026-08-05.md` to five additional park
archetypes. Each pilot is a deterministic metric Blender scene with its own
reference-derived PBR skin and reusable GLB equipment family.

The archetype image supplies spatial hierarchy, feature relationships, edge
conditions, social zones, and landscape character. People visible in a source
image are used only to judge scale, occupancy, circulation, supervision, and
spectator behavior. No people are generated. Large buildings remain a separate
City Prompt layer; park scenes include only reserved pads or forecourts where an
interface is needed.

| Pilot | Composition grammar | Regulation / standard anchors |
| --- | --- | --- |
| Community pickleball hub | One four-court bank plus a separate court, playground, and shaded social edge | Five 6.10 m x 13.41 m courts within 9.14 m x 18.29 m safety envelopes |
| School athletic oval | One track anchor with compatible soccer infield and field events | Eight marked lanes, 100 m x 64 m soccer pitch, long jump, shot put |
| Three-field baseball club hub | Three diamonds around a shared club forecourt, batting cages, and a reserved building pad | Three 18.29 m base paths with 66-72 m youth outfields |
| Traditional cricket green | One open oval with central wicket and quiet pavilion edge | 22.56 m wicket, boundary rope, sight screens, practice nets |
| Mixed tournament campus | Two soccer and two softball blocks divided by public and service spines | Two 100 m x 64 m soccer pitches and two 18.29 m softball diamonds |

## Review images

- `comparison-mobile.png` is the complete mobile-friendly catalogue sheet.
- Each `*-comparison.png` file pairs the hero, 60-degree, and nadir archetype
  references with the same three authored LEGO camera angles. This makes
  geometry, spacing, edge conditions, and missing detail directly auditable.
- `baseball-youth-pinwheel-skin-v2-comparison.png` records the texture-corrected
  baseball pilot: multi-angle reference crops now drive distinct red infield
  clay, warning track, mown turf passes, concrete, and planted-edge materials.
- `baseball-youth-pinwheel-skin-v2-city-prompt.png` records the promoted GLB in
  the live City Prompt viewer with its trusted baseball LEGO-family recipe.
- Each `cityprompt-*-building-pilot.png` records a live City Prompt trial with
  exactly one park and one separately compiled building LEGO family. No Master
  Planner was used.

The reference photographs are comparison evidence and role-specific skin
sources. Their pixels are not projected onto the generated geometry: each
material role derives its own repeatable PBR maps from an intentional crop of
the hero, 60-degree, or nadir reference.

Baseball skin v2 also writes metre-scaled UV0 coordinates into every textured
mesh before glTF export. This prevents the 230 m site plate and field polygons
from collapsing to a few blurred repeats or losing their textures in Three.js.
`verify_park_glb_materials.py` checks the promoted GLB for textured meshes that
lost UV0 during export.

## City Prompt verification

All five park families compiled in the `Regulation Park LEGO Trials` project
one at a time. Each run reported one assembled detailed building, zero missing
building families, and one compiled archetype-owned park layer. The paired
building uses the existing `contemporary-midrise-brick-bronze-renderlocked-v1`
family. Large park-support buildings remain reserved pads or forecourts and are
not included in the park GLBs.

## Reproduction

The bounded source schedule is
`tools/park_skin_compiler/park_archetype_batch3_skin_sources.json`.
Generate the skins with
`tools/park_skin_compiler/generate_park_archetype_batch3_skins.py`, render the
geometry with `tools/park_skin_compiler/render_park_archetype_batch3.py`, and
assemble review sheets with
`tools/park_skin_compiler/compose_archetype_owned_park_batch3.py`.
