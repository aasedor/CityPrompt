"""Look-sheet prompts for geometry-first video finishing.

City Prompt owns the geometry, camera and timing of a video: the deterministic
route preview (and, for depth-guided engines, the depth control track) carry
them as data. The prompt therefore only has to say what the finished footage
should look like and remind the model to leave everything else alone. A short
end-state description plus one preservation sentence is what the current
video editors follow best; the long per-zone lock prose that
``build_cinematic_prompt`` emits stays available as the ``legacy`` profile.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, get_args

LookStyle = Literal[
    "photorealistic",
    "photomontage",
    "development",
    "atmospheric",
    "night",
    "winter",
    "survey",
    "documentary",
    "overcast",
    "after_rain",
]
PromptProfile = Literal["look_sheet", "legacy"]

DEFAULT_LOOK_STYLE: LookStyle = "photorealistic"
LOOK_STYLE_IDS: tuple[str, ...] = get_args(LookStyle)

# One sentence fragment per look, sharing the vocabulary of the Direct 3D
# image art directions (frontend useDirect3DRender.ts) so a student's image
# and video of the same view read as one presentation. Each stays under 160
# characters: everything described here is something the model may repaint.
VIDEO_LOOKS: dict[str, str] = {
    "photorealistic": (
        "photographic finish in soft natural daylight: balanced exposure, realistic surface texture, "
        "subtle reflections in existing glazing, natural contact shadows"
    ),
    "photomontage": (
        "photomontage realism: one sun direction, shadow length, haze, grain and colour temperature "
        "shared by the proposal and the surrounding city, muted natural colour"
    ),
    "development": (
        "polished completed-development look: crisp clean facades in their current materials, clean "
        "glazing, tidy planting and paving, bright optimistic daylight"
    ),
    "atmospheric": (
        "cinematic late-day light raking across the facades, long soft shadows, gentle golden haze, "
        "layered atmospheric depth, faint warm glow behind existing windows"
    ),
    "night": (
        "blue-hour night: indigo sky, faint warm horizon, facades lit only through existing windows "
        "and fixtures, soft reflections in glazing and paving, no neon"
    ),
    "winter": (
        "convincing winter: thin snow on roofs, lawns and planting, cleared walks, bare deciduous "
        "branches, cold overcast daylight, pale grey-blue sky, muted palette"
    ),
    "survey": (
        "neutral survey photography: even daylight, true-to-life colour, edge-to-edge clarity, highly "
        "legible materials, buildings, streets and landscape"
    ),
    "documentary": (
        "calm documentary photography: flat natural daylight, restrained true-to-life colour, honest "
        "material variation, ordinary inhabited quality, no dramatization"
    ),
    "overcast": (
        "soft overcast daylight: diffuse shadowless light, cool neutral colour, gentle contrast, clean "
        "legible facades and landscape"
    ),
    "after_rain": (
        "just after rain: damp paving with subtle plausible reflections, clearing overcast sky, fresh "
        "saturated planting, cool soft light"
    ),
}

ENTOURAGE: dict[tuple[bool, bool], str] = {
    (False, False): "No people or vehicles.",
    (True, False): "A few pedestrians at natural scale on existing sidewalks and paths; no vehicles.",
    (False, True): "Sparse slow traffic only in existing road lanes; no pedestrians.",
    (True, True): (
        "A few pedestrians on existing sidewalks and paths and sparse slow traffic in existing lanes."
    ),
}

CAMERA_SENTENCE = "Same camera path, speed and timing as the source video."
CONTROL_CAMERA_SENTENCE = "Same camera path, speed and timing as the control video."
PRESERVATION_SENTENCE = (
    "Keep everything else the same: every building, roof, courtyard, park, path, street and the "
    "surrounding city stay exactly where they are with the same shapes and counts."
)
CLEAN_PLATE_SENTENCE = "No text, labels or markers."
ANCHOR_SENTENCE = "Match the materials, light and colour of the reference image."
VACE_SCENE_SENTENCE = (
    "Architectural drone footage of this exact scene: every building, park, path and street sits "
    "where the depth video places it, with the same shapes and counts."
)
VACE_NEGATIVE_PROMPT = (
    "text, watermark, labels, captions, extra buildings, merged buildings, missing buildings, warped "
    "facades, floating objects, flicker, jitter, morphing, blur, cartoon, painting, low quality"
)

STUDENT_NOTE_MAX_CHARS = 240
MAX_LOOK_SHEET_PROMPT_CHARS = 800

_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class LookSheet:
    look_style: str
    add_people: bool
    add_vehicles: bool
    note: str
    anchor_attached: bool = False

    @property
    def look(self) -> str:
        return VIDEO_LOOKS[self.look_style]

    @property
    def entourage(self) -> str:
        return ENTOURAGE[(self.add_people, self.add_vehicles)]

    @property
    def note_sentence(self) -> str:
        return f"Note: {self.note}" if self.note else ""


def sanitize_student_note(note: str | None) -> str:
    """Collapse the student's free text to one clean line of at most 240 characters."""
    if not note:
        return ""
    collapsed = _WHITESPACE.sub(" ", str(note)).strip()
    if len(collapsed) > STUDENT_NOTE_MAX_CHARS:
        collapsed = collapsed[:STUDENT_NOTE_MAX_CHARS].rstrip()
    if collapsed and collapsed[-1] not in ".!?":
        collapsed = f"{collapsed}."
    return collapsed


def build_look_sheet(
    *,
    look_style: str = DEFAULT_LOOK_STYLE,
    add_people: bool = False,
    add_vehicles: bool = False,
    student_note: str | None = "",
    anchor_attached: bool = False,
) -> LookSheet:
    if look_style not in VIDEO_LOOKS:
        raise ValueError(f"Unknown video look '{look_style}'.")
    return LookSheet(
        look_style=look_style,
        add_people=bool(add_people),
        add_vehicles=bool(add_vehicles),
        note=sanitize_student_note(student_note),
        anchor_attached=bool(anchor_attached),
    )


def _join(parts: list[str]) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def assert_prompt_budget(prompt: str) -> str:
    if len(prompt) > MAX_LOOK_SHEET_PROMPT_CHARS:
        raise ValueError(
            f"The video prompt is {len(prompt)} characters; the look sheet allows {MAX_LOOK_SHEET_PROMPT_CHARS}."
        )
    return prompt


def build_omni_look_prompt(sheet: LookSheet) -> str:
    """Gemini Omni edit: name the one change, then keep everything else the same."""
    return assert_prompt_budget(
        _join(
            [
                f"Change only the look of this video: {sheet.look}.",
                ANCHOR_SENTENCE if sheet.anchor_attached else "",
                sheet.entourage,
                sheet.note_sentence,
                CAMERA_SENTENCE,
                PRESERVATION_SENTENCE,
                CLEAN_PLATE_SENTENCE,
            ]
        )
    )


def build_grok_look_prompt(sheet: LookSheet) -> str:
    """xAI Grok video edit takes the route video only, so there is no reference sentence."""
    return assert_prompt_budget(
        _join(
            [
                f"Change only the look of this video: {sheet.look}.",
                sheet.entourage,
                sheet.note_sentence,
                CAMERA_SENTENCE,
                PRESERVATION_SENTENCE,
                CLEAN_PLATE_SENTENCE,
            ]
        )
    )


def build_vace_depth_prompt(sheet: LookSheet) -> tuple[str, str]:
    """Wan VACE depth control: a positive end-state description plus a fixed negative prompt."""
    look = sheet.look[0].upper() + sheet.look[1:]
    positive = assert_prompt_budget(
        _join(
            [
                f"{look}.",
                VACE_SCENE_SENTENCE,
                sheet.entourage,
                sheet.note_sentence,
                CONTROL_CAMERA_SENTENCE,
            ]
        )
    )
    return positive, VACE_NEGATIVE_PROMPT
