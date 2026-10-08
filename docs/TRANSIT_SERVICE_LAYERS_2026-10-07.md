# Calgary Transit routes and stops

In Site > City-wide policy maps, expand **Calgary Transit · service routes & stops**.
Routes and stops have independent visibility and opacity controls. Choose a route
to isolate overlapping services. Stop markers remain independent of the route
filter. Click a line for its route number, name and category; click a stop for its
number, name and published serving routes.

The shipped snapshot contains 261 routes and 6,213 active stops. It was retrieved
on October 8 UTC (October 7 in Calgary). Source updates are shown separately:

- Routes: https://data.calgary.ca/d/hpnd-riq4
- Stops: https://data.calgary.ca/d/muzh-c9qc
- Stop-to-route associations: https://data.calgary.ca/d/pm3p-838w

These are published service snapshots, separate from the long-term MDP/CTP
network. They do not provide live arrivals, frequency, detours or confirmed
accessible walking routes. Colours distinguish service categories; they are not
individual route branding. Data is loaded only when a layer is enabled and
cached in the browser query cache. Lines are batched and stops are instanced.

## Refresh

Run from the repository root with Python and requests available:

```powershell
python tools/policy_maps/fetch_transit_service.py --output C:/dev-artifacts/CityPrompt/transit-service-refresh
python -m unittest discover -s tools/policy_maps -p test_transit_service.py
```

The downloader uses bounded pages and rejects changed sources or invalid
geometry. Review the two output files before promoting them individually to
`frontend/public/policy-maps/transport-vectors-v1/`. Update the shipped-count
assertions in `TransitService.test.tsx` when source counts change. Restart Vite
if its public-file index or an external hydrated asset root needs refreshing.

## Verification

- 44 policy-map Vitest tests passed, including service toggles, route filtering,
  project preferences, details and shipped snapshot integrity.
- Two Python pipeline tests passed; TypeScript type-check passed.
- Browser trial verified both layers in the Google 3D environment, route 90
  filtering and line selection, stop 4642 selection and serving route, independent
  stop visibility, and keyboard opacity adjustment. No console errors were
  reported during that trial.
- Read-only code review found no actionable issues. Laptop performance remains
  for the user's hardware trial.

Browser evidence is outside Git under
`C:/dev-artifacts/CityPrompt/transit-service-2026-10-07/browser/`.
