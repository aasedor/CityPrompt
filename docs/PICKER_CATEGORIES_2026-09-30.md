# Student catalogue categories

The catalogue now offers simple, mutually exclusive browsing categories while
retaining the existing district-code search, exact asset bindings and private
User generated category. Empty categories are omitted. Changing sections resets
the category and pagination; filtering does not place or modify an object.

Buildings: Low density; Townhomes & rowhouses; Apartments & mixed use; Towers;
Shops & workplaces; Civic & culture; Industry & infrastructure.

Parks: Gardens; Play & sport; Community parks; Nature & trails; Plazas & water.

Streets: Neighbourhood streets; Boulevards & bridges; Walking & cycling; Transit;
Alleys & mews.

Categories describe the authored form and activity, not legal land use or a
promise of geometry scaling. Exact-variant overrides correct inherited broad
groups (for example, pickleball gardens belong to Play & sport, and office
towers belong to Towers). Native buildings of twelve or more storeys default to
Towers. Calgary guide metadata remains intact.

Validation: 29 focused frontend tests pass, covering all 63 choices, selected
category membership, pagination, switching sections, placement callbacks,
private models and canonical browsing. TypeScript passes. No browser or paid
render testing performed during this batch. See the autumn building, park and
street checkpoint documents for model evidence and limitations.
