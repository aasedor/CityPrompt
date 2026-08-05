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
| Community pickleball bank | Two parallel banks of four around a shaded social spine | Eight 6.10 m x 13.41 m courts within 9.14 m x 18.29 m safety envelopes |
| School athletic oval | One track anchor with compatible soccer infield and field events | Eight marked lanes, 100 m x 64 m soccer pitch, long jump, shot put |
| Youth baseball pinwheel | Four outward-facing diamonds around one shared hub | Four 18.29 m base paths with 72 m youth outfields |
| Traditional cricket green | One open oval with central wicket and quiet pavilion edge | 22.56 m wicket, boundary rope, sight screens, practice nets |
| Mixed tournament campus | Two soccer and two softball blocks divided by public and service spines | Two 100 m x 64 m soccer pitches and two 18.29 m softball diamonds |

## Review images

- `comparison-mobile.png` is the complete mobile-friendly catalogue sheet.
- Each `*-comparison.png` file pairs the selected archetype image with three
  authored LEGO camera angles.

The reference photographs are comparison evidence only. Their pixels are not
projected onto the generated geometry.

## Reproduction

The bounded source schedule is
`tools/park_skin_compiler/park_archetype_batch3_skin_sources.json`.
Generate the skins with
`tools/park_skin_compiler/generate_park_archetype_batch3_skins.py`, render the
geometry with `tools/park_skin_compiler/render_park_archetype_batch3.py`, and
assemble review sheets with
`tools/park_skin_compiler/compose_archetype_owned_park_batch3.py`.
