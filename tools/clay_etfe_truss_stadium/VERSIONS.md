# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked catalogue views | builder pass, aperture audit PASS, 47,632 triangles, 2,488,896-byte GLB; independent review VISUAL_REWORK_REQUIRED, 1 P0 / 10 P1 / 9 P2 |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fix every v001 P0/P1 (camera, pitch axis, diagonals, stand soffit, cushions, band edges, extent, radials, joints, aisles, streets) | builder pass, aperture audit PASS, 66,608 triangles, 3,464,928-byte GLB; independent review VISUAL_REWORK_REQUIRED, 1 P0 / 6 P1 / 6 P2 (6 of 11 v001 findings resolved, 2 partly) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | fix the v002 P0/P1s (camera, cushions, band contact, diagonals, perimeter truss, joints, hollow bowl) | builder pass, aperture audit PASS, 63,087 triangles, 2,906,576-byte GLB; independent review VISUAL_REWORK_REQUIRED, 0 P0 / 6 P1 / 8 P2 (5 of 7 v002 findings resolved); STOPPED: the steel-joint black holes survived two targeted fixes; v003 is the best-reviewed candidate |
