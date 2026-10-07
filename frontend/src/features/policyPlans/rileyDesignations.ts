/** Student summaries of the pinned 38P2025 Riley plan, not zoning permissions.
 * Page numbers below are printed pages; pdfPage includes the five-page front matter.
 * Keep wording conditional where the plan says "may" or "should".
 */
export type RileyDesignation = {
  name: string; color: string; summary: string; considerations: string[];
  section: string; page: number; pdfPage: number; relatedSections?: string;
};

export const RILEY_DESIGNATIONS: RileyDesignation[] = [
  {
    name: 'Neighbourhood Commercial', color: '#e4002b', section: '2.2.1.2', page: 25, pdfPage: 30,
    relatedSections: 'Shared Commercial / Flex policies: section 2.2.1.1, p. 24.',
    summary: 'Shopping and gathering streets with a broad range of businesses and an active pedestrian environment. Buildings face the street, with commercial space along the busier ground-floor frontage.',
    considerations: [
      'Larger businesses and housing can sit above or behind smaller street-facing units. Ground-floor homes should face quieter streets or lanes.',
      'Frequent doors and windows, generous sidewalks, seating and lighting support a lively street.',
      'Where Active Frontage is also identified, additional policies discourage vehicle-oriented uses and parking access from the busier street. Check the full map for that overlay.',
    ],
  },
  {
    name: 'Neighbourhood Flex', color: '#ed9d4d', section: '2.2.1.3', page: 26, pdfPage: 31,
    relatedSections: 'Shared Commercial / Flex policies: section 2.2.1.1, p. 24.',
    summary: 'A flexible mix of homes and businesses, with buildings oriented toward the street. Different uses can sit beside one another within a block or on different floors of a building.',
    considerations: [
      'Ground floors can accommodate shops, offices, personal services, institutional or recreation uses, and housing.',
      'Design streets and public spaces for moderate to high pedestrian activity, with visible entrances and windows.',
      'Parking should not sit between buildings and the busier street; the shared policies favour lane access for parking and loading.',
    ],
  },
  {
    name: 'Neighbourhood Connector', color: '#fedb00', section: '2.2.1.5', page: 28, pdfPage: 33,
    relatedSections: 'Shared Connector / Local policies: section 2.2.1.4, p. 27.',
    summary: 'Primarily residential streets with more activity and connections to other communities. A variety of housing forms and some small local businesses help meet residents’ everyday needs.',
    considerations: [
      'The plan supports frequent homes and entrances facing the street, alongside walking and cycling connections.',
      'Commercial uses beyond work-live units and home businesses should be small and limited to corner parcels on collector or higher-class roads.',
      'Consider neighbouring homes when arranging building scale, noise, vehicle access and servicing.',
    ],
  },
  {
    name: 'Neighbourhood Local', color: '#fff4b2', section: '2.2.1.6', page: 29, pdfPage: 34,
    relatedSections: 'Shared Connector / Local policies: section 2.2.1.4, p. 27.',
    summary: 'Residential areas with a range of housing forms and building scales. Change should respond to the surrounding development pattern, heritage, trees and access to neighbourhood amenities.',
    considerations: [
      'Homes are the main use; work-live units and home businesses may also fit. Consider privacy, sunlight, setbacks and the street-facing character.',
      'Read the Building Scale map too: the pale-yellow colour alone does not identify a height or housing-form limit.',
      'If the site also has the Limited Scale modifier, additional policies apply. The plan does not support multi-residential building forms in that particular combination.',
    ],
  },
  {
    name: 'Commercial Centre', color: '#a5192e', section: '2.2.2.1', page: 32, pdfPage: 37,
    relatedSections: 'Vehicle-Oriented Commercial policies: section 2.2.2, pp. 30–31.',
    summary: 'Larger shopping destinations serving a wider area, often arranged around internal streets and parking. Redevelopment is intended to add activity and make these sites easier and more comfortable to walk through.',
    considerations: [
      'Commercial frontages should address busier streets; housing can be mixed in, with standalone housing, offices or institutions on quieter streets.',
      'Connect safe pedestrian routes, transit stops, patios and public spaces, with clear separation from vehicle aisles.',
      'As redevelopment occurs, the plan favours replacing surface parking with underground or structured parking.',
    ],
  },
  {
    name: 'Natural Areas', color: '#a9c23f', section: '2.2.3.1', page: 35, pdfPage: 40,
    relatedSections: 'Shared Parks, Civic and Recreation policies: section 2.2.3, p. 34.',
    summary: 'Land whose main role is ecological: supporting habitat, biodiversity, water and air quality, and natural processes. Public access and amenities should respect those functions.',
    considerations: [
      'Protect and restore habitat and ecological connections, particularly along the Bow River corridor and McHugh Bluff.',
      'Pathways and cycling access should avoid disturbing sensitive areas; buffers can separate nature from nearby development.',
      'Selected amenities, such as river access, gathering places, washrooms or interpretation, may be appropriate when ecological functions are maintained.',
    ],
  },
  {
    name: 'Parks and Open Space', color: '#70a355', section: '2.2.3.2', page: 36, pdfPage: 41,
    relatedSections: 'Shared Parks, Civic and Recreation policies: section 2.2.3, p. 34.',
    summary: 'Publicly accessible outdoor places for recreation and community life. These can include playgrounds, playing fields, plazas and off-leash areas, and may also contain schools or community facilities.',
    considerations: [
      'Activities, facilities and temporary commercial uses should complement the site’s main function.',
      'Protect trees and provide sunlight, shade, accessible paths and connections to the wider walking and cycling network.',
      'Plan for year-round use, adaptable gathering spaces, local culture and practical maintenance needs.',
    ],
  },
  {
    name: 'City Civic and Recreation', color: '#4db69f', section: '2.2.3.3', page: 37, pdfPage: 42,
    relatedSections: 'Shared Parks, Civic and Recreation policies: section 2.2.3, p. 34.',
    summary: 'Indoor and outdoor community facilities on public land, such as recreation, arts, cultural and civic amenities. Some facilities may charge fees or require membership.',
    considerations: [
      'Spaces should be adaptable, accessible to people of different ages and abilities, and support activities across the seasons.',
      'Care facilities and non-market housing are appropriate, especially when integrated with civic facilities near services and amenities.',
      'Building Scale modifiers do not apply to the recreation, civic, arts, cultural, emergency-service or municipal-infrastructure uses specified in section 2.2.3.3(g).',
    ],
  },
  {
    name: 'Private Institutional and Recreation', color: '#b2e0d5', section: '2.2.3.4', page: 38, pdfPage: 43,
    relatedSections: 'Shared Parks, Civic and Recreation policies: section 2.2.3, p. 34.',
    summary: 'Facilities on private land that serve education, worship, recreation, arts or culture. Examples include private schools, colleges and recreation centres; access may involve membership or fees.',
    considerations: [
      'A range of institutional, recreation and supporting commercial activities may be appropriate as these sites evolve.',
      'Multi-residential and non-market housing can fit where they complement the site’s primary function.',
      'Consider connections to transit, safe pedestrian routes, parking, neighbouring uses and the services needed for gatherings or events.',
    ],
  },
];

const byName = new Map(RILEY_DESIGNATIONS.map(designation => [designation.name, designation]));
export function rileyDesignation(name: string) { return byName.get(name); }
