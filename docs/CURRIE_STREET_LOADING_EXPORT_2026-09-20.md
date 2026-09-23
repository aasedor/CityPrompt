# Prepared street loading and export repair — 20 September 2026

The irregular Currie mixed scene now seats the prepared part of its bent street
at the site level on the first render. A fresh export waits for the public-road
end to finish measuring instead of capturing the street under the grass.
The disposable project is `7e1e9037-b98c-4d18-8502-839160315869`;
no saved geometry or protected original project was changed.

## Cause and shared repair

A street extending beyond the prepared boundary has no single wholly-contained
zone level. Its old startup path therefore used a stored terrain height until
the station sampler finished. The sampler applied the prepared level only at
completion. Meanwhile, capture checked natural street ground providers but the
prepared extension had no readiness marker, so the early scene could pass.

The street now uses the prepared datum and a shared per-station preview for
pavement, sidewalk bands and furniture immediately. Inside probes use the known
level directly and do not spend the ray budget. Outside probes begin after
visible tiles settle; every centre, left and right sample must be finite before
the prepared extension is marked ready. Missing measurements retain an editable
preview and reject capture with recovery guidance, rather than accepting a
fitted fallback as measured ground. Tile waiting and sampling retries are bounded.

Prepared extensions publish sampling/ready/unavailable status through the
existing street capture guard. Capture waits, then checks readiness again
before returning an image or video frame. A street-view screenshot fallback
cannot bypass this check. Geometry, site-level and boundary edits remount the
street sampler so a prior completed profile cannot certify a changed route.
This applies to shared street ribbons using the prepared public-road extension
path, not only Narrow Residential Street. Roundabout and natural-ground
grading behavior were not redesigned.

## Verification

- 75 focused tests passed: initial prepared pavement/sidewalk heights, missing
  cross-section samples, capture rejection/recovery, mesh/furniture behavior,
  tile readiness, and the existing natural street extension. TypeScript and
  changed-file lint passed.
- Browser check held 25 Google terrain requests while the road reported
  `sampling`. The road was already above the grass. A diagnostic capture with
  the separate tile wait bypassed did not complete during the hold. Releasing
  the requests produced `ready` and a successful capture, with no remaining
  grounding issues or page errors. This isolates the road guard itself.
- A separate fresh browser session used the ordinary Image → Export current
  3D view action immediately after loading. It produced a preview in 10,623 ms
  and downloaded the PNG with the street visible above the grass. No page errors
  or grounding issues remained. This timing is local evidence, not a guarantee.

External evidence under
`C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-clear-route/`:
`street-pending-prepared.png`, `street-readiness-result.json`,
`street-ui-export-result.json`, `street-readiness-final-preview.png`, and
`street-readiness-final-exact.png`. No paid rendering was used.

This closes the reproduced startup/export timing blocker. The large prepared
pad edge, source-image fidelity and quantitative public-junction grading remain
separate limitations. New street variants must repeat a fresh-load/early-export
check as well as inspecting a settled scene.
