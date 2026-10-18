# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked catalogue views | builder pass, aperture audit PASS, 13,724 triangles, 738,680-byte GLB; independent review VISUAL_REWORK_REQUIRED, 2 P0 / 8 P1 / 7 P2 |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fix every v001 P0/P1 (interior, roof masses, louvres, vault, cushions, slots, base, nodes, fins, rib feet) | builder pass, aperture audit PASS, 16,910 triangles, 968,548-byte GLB; independent review VISUAL_REWORK_REQUIRED, 1 P0 / 4 P1 / 7 P2 (7 of 10 v001 findings resolved, 2 partly) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | fix the v002 P0/P1s (pinwheel masses, faceted mass, swept ribs, fin return, soffit grid) | builder pass, aperture audit PASS, 23,190 triangles, 1,210,444-byte GLB; independent review VISUAL_REWORK_REQUIRED, 0 P0 / 6 P1 / 7 P2 (3 of 5 v002 findings resolved, the P0 lowered to P1); STOPPED: the roof-mass and white-mass findings survived two targeted fixes and P0+P1 did not fall; v003 kept as the candidate because it has no P0 (v002 had 1 P0 / 4 P1) |
