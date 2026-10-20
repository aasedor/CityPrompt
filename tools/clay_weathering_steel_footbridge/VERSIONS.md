# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build of the family | builder pass, aperture audit PASS, 24,536 triangles, 1,318,608-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 6 (first candidate) |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fix the six v001 P1s: one mitred V with a single apex node, plan rotated per the source top, zig-zag roof bracing, diamond cable-net infill, whole Warren panels to the towers, left_side cleared | builder pass, aperture audit PASS, 24,952 triangles, 1,441,196-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 1 (all six v001 P1s fixed; lowest so far, v002 becomes the candidate) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | rework of the v002 bend finding: collar tie across the corner and two struts from the inner node replacing the apex fan, capped corner posts | builder pass, aperture audit PASS, 24,976 triangles, 1,442,444-byte GLB; PASS_ZERO_P0_P1, P0 = 0, P1 = 0, P2 = 12 (the v002 bend finding fixed and earlier fixes hold; v003 becomes the candidate; family stops on the first stopping condition) |
