"""Planning Agents — expert LLM panel over the Urban DNA.

Invariants (per the approved architecture):
- Agents consume UrbanDNA ONLY — never GIS, never raw datasets.
- Agents ADVISE, the existing layout/master-plan engines DRAW: outputs are
  PlanParameters keyed to the zone-properties vocabulary the geometry
  pipeline already reads, plus trade-off ValidationNotes.
- An expert failure degrades the panel (EXPERT_UNAVAILABLE warning) — a
  scenario run always completes.
"""
