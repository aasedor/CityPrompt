# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked views | builder pass, aperture audit PASS, 15,188 triangles, 873,492-byte GLB; VISUAL_REWORK_REQUIRED: 1 P0 / 8 P1 / 8 P2, so v002 follows |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v001 findings | builder pass, aperture audit PASS, 46,258 triangles, 3,001,876-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 4 P1 / 11 P2 (down from 1 + 8, so v003 follows) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v002 findings | builder pass, aperture audit PASS, 59,122 triangles, 3,900,644-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 4 P1 / 9 P2; stopped by the rework rule (P0+P1 not lower than v002, and the roof-garden/dome finding survived two targeted fixes); v002 and v003 tie, so v002 stays the candidate |
