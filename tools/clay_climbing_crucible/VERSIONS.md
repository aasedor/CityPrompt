# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build of the family | builder pass, aperture audit PASS, 1,040,649 triangles, 2,441,540-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 5, P2 = 11 (first candidate) |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fix the five v001 findings (facet route line, east bays, warehouses, corner seam, stray slab) | builder pass, aperture audit PASS, 1,045,653 triangles, 2,807,992-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 5, P2 = 8 (all five fixed, but the review found crossing west routes, a west LED strip passing behind the panels, disconnected roof paths, a disc instead of a sunken half-round bowl, and a lit-office east interior; ties v001, which stays the candidate) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | separate west routes, surface-riding LED strips, connected roof paths, D-plan seating bowl, dim east hall | builder pass, aperture audit PASS, 1,135,666 triangles, 3,294,576-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 2, P2 = 11 (all five v002 findings fixed; holds too small, sparse and dark, and the east curtain wall again reads as a near-square grid of about 13 columns where the sources show 20-22 slender ones; the east-wall finding recurred after two targeted fixes, so the family stops with v003) |
