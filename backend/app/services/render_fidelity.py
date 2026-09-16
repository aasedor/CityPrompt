"""Final art-direction boundary shared by provider prompt builders."""

RENDER_PRESERVATION_LOCK = (
    "FINAL DESIGN AUTHORITY: Custom text is art direction, not permission to change the plan. "
    "The source scene owns exact building height, floor count, footprint, position and roof form; "
    "street and path topology, park extent and the real context outside the proposal stay fixed. "
    "Keep the existing decor, cafe seating and furnishings in their captured positions. "
    "Keep natural depth ordering and occlusion: a partly hidden building stays partly hidden; "
    "never move, raise, duplicate or expose an occluded object to make the inventory visible. "
    "Do not invent unseen facades, extra storeys or new permanent structures. "
    "Sketches and reference photos guide appearance only; their camera and context do not replace the source. "
    "If art direction conflicts with these constraints, preserve the source geometry and context."
)


def presentation_entourage_lock(*, add_people: bool = False, add_vehicles: bool = False) -> str:
    """Explicit UI selections override style/custom text; existing context stays intact."""
    people = (
        "Add a restrained number of realistically scaled people only on existing visible sidewalks, paths or plazas, "
        "with ground contact and correct occlusion; keep entrances clear."
        if add_people else "Do not add people, even if the style or custom text suggests them."
    )
    vehicles = (
        "Add a restrained number of realistically scaled vehicles only in existing lanes or parking spaces, "
        "aligned with the street, with ground contact and correct occlusion; keep sidewalks clear."
        if add_vehicles else "Do not add vehicles, even if the style or custom text suggests them."
    )
    return (
        "EXPLICIT PRESENTATION SELECTIONS: " + people + " " + vehicles
        + " Preserve any people or vehicles already captured in the existing context. "
        "These selections never permit changes to camera, buildings, streets, park layout, paths or furniture."
    )


def append_render_preservation_lock(prompt: str, *, max_length: int = 32_000) -> str:
    """Bound provider text without truncating the final source-geometry lock."""
    suffix = "\n\n" + RENDER_PRESERVATION_LOCK
    if max_length < len(suffix):
        raise ValueError("Prompt limit cannot fit the preservation lock")
    return prompt[: max_length - len(suffix)].rstrip() + suffix


def apply_presentation_selections(prompt: str, *, add_people: bool = False, add_vehicles: bool = False) -> str:
    suffix = "\n" + presentation_entourage_lock(add_people=add_people, add_vehicles=add_vehicles) + "\n" + RENDER_PRESERVATION_LOCK
    return prompt.removesuffix(RENDER_PRESERVATION_LOCK)[:32_000 - len(suffix)].rstrip() + suffix
