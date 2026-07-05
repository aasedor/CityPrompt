"""Planning philosophies -> prompt conditioning + merge-math affinities.

Intensity bands control how hard the philosophy pushes; the same number also
weights the coordinator's merge, so language and math stay in sync.
"""

from __future__ import annotations

from app.services.planning_agents.schemas import PhilosophyWeights

PHILOSOPHY_FRAGMENTS: dict[str, str] = {
    "balanced": "Weigh all planning goals evenly; recommend defensible middle-ground parameters.",
    "new_urbanism": (
        "Fine-grained walkable blocks (120-180m), connected street grid, mixed use at corners, "
        "buildings address the street, parking behind, 5-minute-walk neighbourhood structure."
    ),
    "transit_oriented": (
        "Organize density as a gradient from the transit node — highest within 400m of stops, "
        "minimal parking, active ground floors on walking routes to transit."
    ),
    "fifteen_minute": (
        "Every dwelling within a short walk of daily needs; favour mixed use, mid-rise intensity, "
        "and non-residential floorspace that serves the neighbourhood."
    ),
    "landscape_urbanism": (
        "The open-space network is the ordering system; buildings follow the landscape structure, "
        "green corridors and water define the plan before roads do."
    ),
    "climate_resilience": (
        "Maximize tree canopy and shade continuity, prioritize green stormwater infrastructure over "
        "piped, avoid flood-prone ground, orient blocks for passive solar and winter comfort."
    ),
    "missing_middle": (
        "Cap intensity around 3-4 storeys; maximize rowhouse, fourplex and courtyard formats; "
        "gentle density that fits established streets."
    ),
    "developer_feasibility": (
        "Prefer parameters that minimize servicing cost and construction complexity and maximize "
        "sellable frontage and unit yield within market-supportable formats."
    ),
    "garden_city": (
        "Generous greens and commons structure the plan; moderate density clusters around shared "
        "open space; strong landscape edges."
    ),
    "tactical_urbanism": (
        "Prefer incremental, low-capex, reversible moves; pilot-scale interventions over permanent "
        "heavy infrastructure."
    ),
}


def _band(intensity: float) -> str:
    if intensity < 0.4:
        return "Prefer this direction where it adds little cost or conflict."
    if intensity <= 0.7:
        return "Prioritize this direction when trading off against other goals."
    return (
        "Treat this as the primary organizing principle; concede only for life-safety "
        "or statutory barriers."
    )


def philosophy_prompt_block(philosophy: PhilosophyWeights) -> str:
    primary_fragment = PHILOSOPHY_FRAGMENTS.get(philosophy.primary, PHILOSOPHY_FRAGMENTS["balanced"])
    lines = [
        f"PLANNING PHILOSOPHY — weight {philosophy.intensity:.2f}. {_band(philosophy.intensity)}",
        f"PRIMARY — {philosophy.primary.replace('_', ' ').title()}: {primary_fragment}",
    ]
    if philosophy.secondary and philosophy.secondary in PHILOSOPHY_FRAGMENTS:
        lines.append(
            f"SECONDARY — {philosophy.secondary.replace('_', ' ').title()}: "
            f"{PHILOSOPHY_FRAGMENTS[philosophy.secondary]}"
        )
        lines.append(
            "When these conflict, PRIMARY wins unless the SECONDARY concern is "
            "life-safety or flood/heat related."
        )
    return "\n".join(lines)
