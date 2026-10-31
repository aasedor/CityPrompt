export interface PublicDataset {
  id: string;
  name: string;
  sourceId: string;
  geometry: 'point' | 'multipolygon' | 'multilinestring' | 'the_geom';
  fields: Record<string, string>;
  label: string;
  color: string;
  note: string;
  vintage: string;
  recent?: 'roll_year' | 'applieddate';
}

/** Only these public columns are requested; no applicant or owner names. */
export const PUBLIC_DATASETS: readonly PublicDataset[] = [
  { id: 'assessments', name: 'Property assessment history', sourceId: '4ur7-wsgc', geometry: 'multipolygon', label: 'roll_number', color: '#b45309',
    fields: { roll_number: 'Roll number', roll_year: 'Roll year', assessed_value: 'Assessed value (CAD)', year_of_construction: 'Year of construction' },
    recent: 'roll_year', vintage: 'Latest five calendar roll years',
    note: 'Assessed values are not sale prices. History combines exact roll numbers only; parcel splits and changes are not reconstructed.' },
  { id: 'building-permits', name: 'Building permits', sourceId: 'c2es-76ed', geometry: 'point', label: 'permitnum', color: '#c2410c',
    fields: { permitnum: 'Permit', statuscurrent: 'Status', applieddate: 'Applied', issueddate: 'Issued', completeddate: 'Completed date', originaladdress: 'Address', description: 'Description', housingunits: 'Housing units', estprojectcost: 'Estimated construction value (CAD)' },
    recent: 'applieddate', vintage: 'Applications in the latest five calendar years',
    note: 'A permit is not proof of construction or completion. Cost is the permit’s estimated construction value, not a property value or development budget.' },
  { id: 'development-permits', name: 'Development permits', sourceId: '6933-unw5', geometry: 'point', label: 'permitnum', color: '#9333ea',
    fields: { permitnum: 'Permit', address: 'Address', statuscurrent: 'Status', applieddate: 'Applied', decisiondate: 'Decision date', decision: 'Decision', proposedusedescription: 'Proposed use', description: 'Description' },
    recent: 'applieddate', vintage: 'Applications in the latest five calendar years',
    note: 'Applications and decisions do not establish that a project was built. Check status and dates.' },
  { id: 'water-mains', name: 'Public water mains', sourceId: 'w6h9-w33i', geometry: 'multilinestring', label: 'globalid', color: '#0284c7',
    fields: { globalid: 'Asset ID', diam: 'Diameter (mm)', material: 'Material', year: 'Installation year', status_ind: 'Status' },
    vintage: 'City public feed; normally updated monthly',
    note: 'City-owned drinking-water mains. Location and diameter do not establish spare capacity, connection approval or engineering suitability.' },
  { id: 'growth', name: 'Suburban growth and servicing', sourceId: '2icx-iwek', geometry: 'multipolygon', label: 'community_name', color: '#a16207',
    fields: { community_name: 'Community', policy_name: 'Policy', land_status: 'Land status', subdivision_status: 'Subdivision status', land_use: 'Land use', water: 'Water', sanitary: 'Sanitary', storm: 'Storm', transportation: 'Transportation', emergency_services: 'Emergency services', mod_dt_local: 'Source modified date' },
    vintage: 'City suburban land-supply feed; normally updated twice yearly',
    note: 'Suburban growth areas only. Servicing fields are planning context, not a citywide utility-capacity assessment.' },
  { id: 'community', name: 'Community profiles: population', sourceId: 'f9wk-wej9', geometry: 'the_geom', label: 'community_name', color: '#7c3aed',
    fields: { community_code: 'Community code', community_name: 'Community', total_pop_household: 'Population in private households', pop_age_0_to_14: 'Age 0–14', pop_age_15_to_64: 'Age 15–64', pop_age_65_to_84: 'Age 65–84', pop_age_85_and_over: 'Age 85+' },
    vintage: '2021 Census',
    note: 'Values describe the entire community, not the part inside your site. Private households only. Open the full community profiles for income and housing tenure.' },
  { id: 'heritage', name: 'Historic resources', sourceId: '99yf-6c5u', geometry: 'point', label: 'name', color: '#be123c',
    fields: { name: 'Resource', address: 'Address', construction_yr: 'Construction year', development_era: 'Era', architecture_style: 'Architectural style', orig_use_ty: 'Original use', municipal_dsgtn: 'Municipal designation', provincial_dsgtn: 'Provincial designation', federal_dsgtn: 'Federal designation', is_domlished: 'Demolished (source flag)', is_decomm: 'Decommissioned (source flag)' },
    vintage: 'City historic-resource inventory',
    note: 'Inventory inclusion and legal heritage designation are different. Check designation and demolition flags; this is not a complete cultural or Indigenous heritage inventory.' },
  { id: 'trees', name: 'Public trees', sourceId: 'tfs4-3wwa', geometry: 'point', label: 'common_name', color: '#15803d',
    fields: { common_name: 'Common name', species: 'Species', dbh_cm: 'Trunk diameter (cm)', mature_size: 'Mature size', heritage_trees: 'Heritage tree', modified_dt: 'Source modified date' },
    vintage: 'City public-tree inventory',
    note: 'Public-land trees only. Absence from this layer does not mean that a site has no trees.' },
  { id: 'canopy', name: 'Tree canopy (2022)', sourceId: 'mn2n-4z98', geometry: 'multipolygon', label: 'objectid', color: '#4d7c0f',
    fields: { objectid: 'Canopy ID' }, vintage: '2022 survey',
    note: 'Historic canopy coverage across land ownership types. It is not a current tree inventory.' },
  { id: 'services', name: 'Community services', sourceId: 'x34e-bcjz', geometry: 'point', label: 'name', color: '#0f766e',
    fields: { name: 'Name', address: 'Address', type: 'Service type' }, vintage: 'City community-services feed',
    note: 'Selected public/community amenities. This does not show operating hours, service capacity or all local businesses.' },
  { id: 'schools', name: 'Schools', sourceId: 'fd9t-tdn2', geometry: 'point', label: 'name', color: '#1d4ed8',
    fields: { name: 'School', address_ab: 'Address', board: 'Board', grades: 'Grades' }, vintage: 'City schools feed',
    note: 'Locations and grades do not establish enrolment capacity or catchment eligibility. Private early-childhood operators are excluded.' },
];

export const PUBLIC_REFERENCES = [
  { id: 'rental-context', name: 'Rental market context (CMHC)', url: 'https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market',
    note: 'Official rent and vacancy tables. Choose the survey year and Calgary market area. These are area-level statistics, not the rent of an individual building.' },
  { id: 'levies', name: 'Off-site levy information', url: 'https://www.calgary.ca/planning/land-use/off-site-levy/bylaw-current-rates.html',
    note: 'Official current rates and applicability. A levy is one infrastructure contribution; it is not the full cost of development. No cost calculator is applied to your design.' },
] as const;

export const PUBLIC_DATA_TERMS = 'https://data.calgary.ca/d/Open-Data-Terms/u45n-7awa';
