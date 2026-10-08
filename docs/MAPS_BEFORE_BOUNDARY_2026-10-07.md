# Browse maps before drawing a site

Students can enable zoning and local policy maps in an empty project. MDP, CTP,
5A, transit routes and stops retain their existing boundary-independent controls.

- Zoning uses a 1 km square around the map centre when no active site exists.
  Camera positions are quantized and sampled every 750 ms; two matching samples
  update the area. Fetching remains opt-in, cancellable and cached. No authored
  site polygon is created or saved by exploration.
- The project location supplies the initial area; the globe's existing viewport
  centre reader follows panning. The 2D map supplies its centre when available.
- Local area plans automatically match this area, or can be selected directly.
  A saved site-clipping preference cannot hide the full plan when no site exists.
- With a site boundary, the existing site-specific zoning and clipping behavior
  continues. Site assessment totals and drawing a proposed zoning study still
  require a boundary to define the calculation or design area.
- Existing zoning selections are scoped to their query result so panning cannot
  change an open catalogue card to another district with the same row-index ID.

## Verification

60 focused tests passed across policy maps, zoning controls, map exploration and
zoning inspection. TypeScript checking passed. Read-only review found a zoning
selection identity issue; it was fixed and re-reviewed with no outstanding
important findings.

Browser trial: **Map exploration · no boundary trial**, project
`c2bc4b6b-a471-4546-b6fb-69d52ec2c4b6`, located at Riley Park Trail. No site or
design geometry was drawn. Verified zoning loading (73 districts), clicking S-R
for catalogue suggestions, Riley Urban Form and clicking Neighbourhood Connector,
then panning to a new query area (61 districts) while the old selection cleared.
Screenshots are outside the repository under
`C:/dev-artifacts/CityPrompt/maps-before-boundary-2026-10-07/`.
