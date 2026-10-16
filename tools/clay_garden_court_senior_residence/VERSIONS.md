# Version history

| version | purpose | result |
|---|---|---|
| v001 (1440 px, 32 spp, 18 views + 4 phone boards) | first full roster and independent review | builder pass, aperture audit PASS, 80,504 triangles, 4,180,388-byte GLB; carrier aperture audit FAIL (two ground windows behind the south-east loggia); VISUAL_REWORK_REQUIRED: 3 P0 (facade_close, garden_beds and pergola_terrace cameras inside solids), 5 P1 (dormers too deep, piercing the wing ridges; garden doors read flat-headed under the balconies; forecourt drive a straight slab, not a loop; court_view misses the fountain and beds; loggia_arcade blocked by a tree), 11 P2 |
| v002 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v001 findings | builder pass, aperture audit PASS, 79,242 triangles, 4,113,420-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 4 P1 / 10 P2 (down from 3 + 5, so v003 follows) |
| v003 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v002 findings | builder pass, aperture audit PASS, 80,042 triangles, 4,149,824-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 2 P1 / 11 P2 (down from 0 + 4, so v004 follows) |
| v004 (1440 px, 32 spp, 18 views + 4 phone boards) | fixes the v003 findings | builder pass, aperture audit PASS, 77,804 triangles, 4,038,812-byte GLB; VISUAL_REWORK_REQUIRED: 0 P0 / 2 P1 / 9 P2 (not lower than v003's 0 + 2, so v003 stays the candidate on a tie; one more version under the stopping rule) |
