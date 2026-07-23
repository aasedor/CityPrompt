"""Plan Geometry Engine — deterministic street/block/parcel/open-space/massing.

Implements the community-layout-pipeline spec's rule layer for the Urban DNA
planner: agents advise (PlanParameters), THIS engine draws. No LLM anywhere in
this package; every stage returns geometry + ValidationNote dicts and never
raises for data reasons.

Entirely additive: layout_planner.py and the existing preview/master-plan
endpoints are untouched.
"""
