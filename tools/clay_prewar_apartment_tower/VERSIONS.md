# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first build from the locked views | builder pass, aperture audit PASS, 76,376 triangles, 3,940,656-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 5 P1 / 9 P2, so v002 follows |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v001 findings | builder pass, aperture audit PASS, 79,052 triangles, 4,079,552-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 5 P1 / 12 P2 (not lower than v001's 0 + 5, so v001 stays the candidate on a tie; one more version under the stopping rule) |
