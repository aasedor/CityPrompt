"""Final art-direction boundary shared by provider prompt builders."""

RENDER_PRESERVATION_LOCK = (
    "FINAL DESIGN AUTHORITY: Custom text is art direction, not permission to change the plan. "
    "The source scene owns exact building height, floor count, footprint, position and roof form; "
    "street and path topology, park extent and the real context outside the proposal stay fixed. "
    "Allow decor, cafe seating and everyday activity only where they fit without altering those structures. "
    "Keep natural depth ordering and occlusion: a partly hidden building stays partly hidden; "
    "never move, raise, duplicate or expose an occluded object to make the inventory visible. "
    "Do not invent unseen facades, extra storeys or new permanent structures. "
    "Sketches and reference photos guide appearance only; their camera and context do not replace the source. "
    "If art direction conflicts with these constraints, preserve the source geometry and context."
)


def append_render_preservation_lock(prompt: str, *, max_length: int = 32_000) -> str:
    """Bound provider text without truncating the final source-geometry lock."""
    suffix = "\n\n" + RENDER_PRESERVATION_LOCK
    if max_length < len(suffix):
        raise ValueError("Prompt limit cannot fit the preservation lock")
    return prompt[: max_length - len(suffix)].rstrip() + suffix
