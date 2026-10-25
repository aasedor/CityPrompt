# Undergraduate catalogue teaching layer

The user wants City Prompt to explain architectural styles and planning ideas,
and allow browsing by those ideas as an alternative to building use. They asked
to keep working autonomously while asleep. This design records the choices
made for the next finite local implementation; no further question round is
needed for the already requested direction.

## Intent and scope

Keep use, architectural style and planning approach separate. Provide a style
name, a short explanation, visible features and an associated design idea.
Keep the language introductory. Design associations do not establish a
designer's beliefs, social outcomes or measured building performance.

Reuse the 2026-10-25 audit of 196 current local choices and its sources. The
underlying source catalogue has 497 families and is a different population.
An extra research record must never activate a model. New exact revisions and
unknown future placements must not silently inherit a sibling's lesson.

This phase adds browsing metadata and UI only. The Prairie/Postmodern models
remain outside the student catalogue. No model, geometry, render prompt,
placement identity, database or production deployment changes are authorized by
this implementation choice.

## Approaches considered

1. Rewrite legacy categories: fewer files, but mixes use with style and risks
   changing generation metadata. Rejected.
2. Add exact-placement teaching metadata alongside the existing catalogue:
   chosen because it preserves runtime identities and permits honest review
   status, citations and future revision invalidation.
3. Build a separate teaching site: useful for a lecture, but students would
   leave the design workflow. Rejected for this phase.

The implementation choice is mine under the user's instruction to continue.
Use existing React/TypeScript controls and the existing catalogue dialog.

## Behavior

- Keep the default use/category tiles. Add visible "Browse by style" and
  "Browse by planning idea" actions, so students can skip choosing a use.
- Reuse the existing style/size/purpose filters. Add a planning-idea filter and
  open the filter panel when entering through either teaching action.
- Keep filter intersections, empty-state reset, section changes, pagination
  and exact placement callbacks working. Reading details never places an asset.
- Show a concise style/idea explanation for a selected filter. Cards expose
  the corresponding lesson in their existing expanded information region.
- Use six introductory planning ideas: New Urbanism, TOD, Garden City, green
  infrastructure, Complete Streets and car-oriented layouts. Complete Streets
  replaces City Beautiful in this first interactive set because it directly
  supports the current street tools. Other researched associations remain
  supporting metadata, not an exhaustive syllabus.
- Planning matches mean "components to explore", never certification of a
  neighbourhood. Preserve this qualification beside the filter explanation.
- Match lessons to placement ID, domain, archetype, variant and recorded model
  revision. Changed identities/revisions withhold teaching classifications.
- Hold all eight conflicting identities as "Style to be confirmed". Do not
  expose their contradictory style/ideology as settled. Of 29 previously blank
  building labels, 25 have High/Medium proposed classifications; four stay held.
- Fill the four court-only presentation entries missing at the clean baseline.
  That baseline test failure is catalogue metadata coverage, not a model defect.

## Evidence and verification

Use primary institutional sources already recorded in the audit. Recheck the
introductory planning definitions against CNU, ITDP, TCPA, EPA and Smart Growth
America. Citations are expandable reference links; no account or payment flow.

Verify source-data hashes and runtime registrations are unchanged. Tests must
catch stale/sibling lesson leakage, uncertain classifications, crossed domains,
filter reset, teaching actions that accidentally place, and changed exact
placement callbacks. Run narrow Vitest files and TypeScript checking, then a
bounded student browser trial in the actual local app. Record any unrun gates.

Keep generated browser evidence outside source or in ignored artifacts. No
push/deployment/catalogue activation. Keep source changes on the separate
`codex/teaching-catalogue-20261025` branch based on `44930bc3f`.
