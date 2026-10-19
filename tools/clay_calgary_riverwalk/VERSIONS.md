# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build of the street option | builder pass, aperture audit PASS, 47,356 triangles, 2,726,232-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 1, P1 = 8 |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fix the v001 P0 and P1s: bridge landing on an abutment, lattice-tube bridge, 6 m bands, packed rip-rap, continuous riparian cover, planters with rails, rear and end facades, reframed cameras | builder pass, aperture audit PASS, 58,364 triangles, 3,684,432-byte GLB; VISUAL_REWORK_REQUIRED, P0 = 0, P1 = 2 (v001 P0 and P1s resolved except right_side framing; lowest so far, v002 becomes the candidate) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | rework of the two v002 findings: right_side over the river holding the whole street section, window mullions split at the transoms, darker bronze handrails | builder pass, aperture audit PASS, 59,876 triangles, 3,766,080-byte GLB; PASS_ZERO_P0_P1, P0 = 0, P1 = 0, P2 = 6 (both v002 findings fixed and every v001 fix holds; v003 becomes the candidate; family stops on the first stopping condition) |
