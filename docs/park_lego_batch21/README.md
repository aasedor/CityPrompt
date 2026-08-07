# Park LEGO Batch 21

Batch 21 closes thirty more catalogue variants across ten program and
landscape parents: athletics precincts, community gardens, fountain courts,
ponds, market squares, formal civic plazas, linear greenways, promenades,
swimming complexes and rooftop gardens.

Each new selection has an explicit backend capability, frontend family
mapping, variant-owned planting/program identity and six-role PBR skin derived
from its own catalogue reference. The comparison sheet keeps all four variants
of each parent together so geometry, material palette and program differences
remain reviewable. People appear only in the source references as scale and
use cues; the LEGO output contains no people, AI drape or embedded large
buildings.

The one-park-at-a-time City Prompt trial used Formal Civic Plaza / Green Civic
beside a separately compiled Parisian Boulevard building. A first 39.7 m by
31.2 m parcel was below the catalogue's 40 m by 35 m and 1,400 m2 minimum, so
the trial parcel was extended only enough to provide a valid 42.2 m by 37.0 m,
1,501.8 m2 civic-plaza field. Generate to 3D then persisted the exact Batch 21
family, appearance kit and Green Civic program.

Live review exposed that the compiled polygon mask was still receiving the
generic plaza material even when its LEGO family owned an exact variant skin.
Batch 21 compiled parcels now load their role-appropriate metric PBR base skin
directly (paver, lawn or planting). The Green Civic depth kit also adds the
reference-defining central fountain, paired raised planter terraces, rain-
garden planting and timber seating while preserving a clear civic event field.
The park remains level on the prepared datum and fully masks Google tiles; the
adjacent large building remains a separate family.

Reviewed outputs:

- `park_lego_batch21_four_variant_sheet.jpg` — ten-parent, four-variant source
  and skin comparison.
- `city_prompt_green_civic_live_trial.png` — compiled one-park City Prompt
  trial beside the separate Parisian building.
