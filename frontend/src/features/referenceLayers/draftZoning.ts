import type { CalgaryDistrict } from './calgaryDistricts';

/** Pinned discussion draft; not the current bylaw or an adopted zoning map. */
export const DRAFT_ZONING_SOURCE = 'https://www.calgary.ca/content/dam/www/pda/pd/documents/city-building-program/cbp.annotated-draft-zoning-bylaw-may2025.pdf';
type DraftInfo = { code: string; title: string; page: number; summary: string; color: string; source: string };
const housing = '#f4dc91', mixed = '#e6a0b5', downtown = '#ca807f', commercial = '#e98779', industrial = '#bdabd2', park = '#bad19c', utility = '#bdc7cb';
const rows: [string, string, number, string, string][] = [
  ['H-1I','Housing – Small Scale Infill',29,'Limited-scale, low-density housing and home businesses serving local residents.',housing],
  ['H-1G','Housing – Small Scale General',41,'Low-density housing in master-planned communities and comprehensive development sites.',housing],
  ['H-1Gm','Housing – Small Scale General · attached housing',41,'The H-1G variant promoting semi-detached and rowhouse buildings on comprehensive development sites.',housing],
  ['H-2','Housing – Middle Scale',48,'Limited-scale housing at low or medium density, with home businesses and neighbourhood commercial uses.',housing],
  ['H-3','Housing – Multi-Residential',57,'Low-scale housing at medium or high density, community-serving commercial uses and heights set through an h modifier.',housing],
  ['MU-1','Mixed Use – Low-Rise',64,'Low-scale mixed-use or residential development, with street-facing institutional and community-serving commercial uses.',mixed],
  ['MU-1c','Mixed Use – Low-Rise · commercial frontage',64,'The MU-1 variant requiring street-facing commercial uses in the storey closest to grade.',mixed],
  ['MU-2','Mixed Use – Mid-Rise',72,'Low- to mid-scale mixed-use or residential development, including street-facing institutions, small-scale manufacturing and commerce.',mixed],
  ['MU-2c','Mixed Use – Mid-Rise · commercial frontage',72,'The MU-2 variant requiring street-facing commercial uses in the storey closest to grade.',mixed],
  ['MU-3','Mixed Use – High-Rise',79,'Mid- to high-scale, high-density mixed-use or residential development, with street-facing institutional, manufacturing and commercial uses.',mixed],
  ['MU-3c','Mixed Use – High-Rise · commercial frontage',79,'The MU-3 variant requiring street-facing commercial uses in the storey closest to grade.',mixed],
  ['GD-1','Greater Downtown – Housing',87,'High-density downtown housing and community-serving commerce in street-oriented mid- to high-scale buildings.',downtown],
  ['GD-2','Greater Downtown – Mixed Use',93,'Medium- to high-density downtown mixed use, with active uses at grade on specified streets and public-amenity density incentives.',downtown],
  ['GD-3','Greater Downtown – Core',101,'Intensive downtown mixed-use development, with street-oriented buildings and public-amenity density incentives.',downtown],
  ['C-1','Commercial – Community',109,'Limited-scale commercial or mixed-use development with street-facing institutions, small-scale manufacturing and neighbourhood commerce.',commercial],
  ['C-1v','Commercial – Community · vehicle-oriented',109,'The C-1 variant accommodating vehicle-oriented uses; consult the variant rules in the draft.',commercial],
  ['C-2','Commercial – General',114,'Low- to mid-scale commercial or mixed use serving surrounding communities, intended for areas of one to eight hectares.',commercial],
  ['C-3','Commercial – Large Format',119,'Low- to high-scale commercial or mixed use, facing public or internal private streets, intended for areas of at least six hectares.',commercial],
  ['I-F','Industrial – Flex',125,'Light and medium industry alongside commercial uses, including employment hubs near the primary transit network.',industrial],
  ['I-G','Industrial – General',130,'Light and medium industry with goods-network access, and commercial uses on parcels with primary transit access.',industrial],
  ['I-H','Industrial – Heavy',136,'Heavy industry, including off-site impacts, with access to hazardous-goods routes and railways.',industrial],
  ['S-NA','Special Purpose – Natural Areas',138,'Natural landforms, vegetation, wetlands and environmental or conservation reserve, with limited development and passive recreation.',park],
  ['S-PS','Special Purpose – Public Parks and Schools',139,'Reserve lands for schools, parks and compatible public-benefit uses, with public spaces and educational, recreational and cultural programming.',park],
  ['S-RC','Special Purpose – Recreation and Community',141,'Parks, schools, recreation and community uses on non-reserve lands, including indoor facilities and outdoor recreation.',park],
  ['S-PI','Special Purpose – Public Facilities and Infrastructure',143,'Public infrastructure, utilities, depots, training and transportation facilities, and government-operated uses.',utility],
  ['S-TC','Special Purpose – Transportation Corridor',146,'Provincial transportation and utility corridors, including temporary and removable uses.',utility],
  ['S-FD','Special Purpose – Future Development',149,'Land awaiting urban development and servicing, with interim agriculture and removable uses to protect future development opportunities.',utility],
];
export const DRAFT_ZONE_INFO: DraftInfo[] = rows.map(([code,title,page,summary,color]) => ({code,title,page,summary,color,source:`${DRAFT_ZONING_SOURCE}#page=${page}`}));
export const DRAFT_DISTRICTS: CalgaryDistrict[] = DRAFT_ZONE_INFO.map(row => ({code:row.code,designation:row.code,description:row.title,bylaw:'draft-2025'}));
export const draftDistrictInfo = (designation: string) => DRAFT_ZONE_INFO.find(row => row.code === designation);
/** Illustrative classroom palette: this draft does not publish zoning maps. */
export const draftDistrictColor = (designation: string) => draftDistrictInfo(designation)?.color ?? '#bdc7cb';
