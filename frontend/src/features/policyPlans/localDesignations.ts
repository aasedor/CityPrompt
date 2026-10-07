import { RILEY_DESIGNATIONS, type RileyDesignation } from './rileyDesignations';

type Explanation = Pick<RileyDesignation, 'summary' | 'considerations'>;
/** Shared descriptions verified against each plan's category introduction.
 * Numeric limits and area-specific permissions belong to the linked plan, not
 * this shared glossary. Each plan supplies its own colour, section and pages.
 */
const explanations: Record<string, Explanation> = {
  'Neighbourhood Commercial': {
    summary: 'Shopping and gathering streets with a broad range of businesses. Street-facing commercial units, frequent entrances and windows support an active pedestrian environment, with other uses above or behind them.',
    considerations: ['Place shops along the busier frontage and consider quieter streets or lanes for ground-floor housing.', 'Design comfortable walking space, visible entrances, seating and lighting for year-round activity.', 'Check the source map for Active Frontage and other additional policies before arranging parking, loading or ground-floor uses.'],
  },
  'Neighbourhood Flex': {
    summary: 'A flexible mix of homes and businesses in street-oriented buildings. Uses can sit beside one another on a block or occupy different floors, including offices, personal services, institutions and recreation.',
    considerations: ['Consider a range of ground-floor uses and entrances that face the street.', 'Provide public spaces for moderate to high pedestrian activity.', 'Some plans identify Industrial Transition or other additional policies. Read the site-specific guidance before including industrial activities.'],
  },
  'Neighbourhood Connector': {
    summary: 'Primarily residential areas along busier neighbourhood streets, often connecting communities. A variety of housing and small local businesses can support everyday needs, walking and cycling.',
    considerations: ['Support homes and entrances facing the street, with useful walking and cycling connections.', 'The conditions for small commercial uses vary by plan. Consult the linked policies for eligible locations and limits.', 'Consider the neighbouring residential context when arranging scale, noise, vehicle access and servicing.'],
  },
  'Neighbourhood Local': {
    summary: 'Residential areas with a range of housing types and home-based businesses. Their development pattern, heritage, trees and access to parks and amenities influence how they change.',
    considerations: ['Read the Building Scale map alongside this colour; Urban Form alone does not set a building height or unit count.', 'Additional Limited Scale policies may apply. Use this plan’s wording when assessing a proposal.', 'Consider the surrounding homes, sunlight, privacy, established landscaping and the relationship to the street.'],
  },
  'Commercial Centre': {
    summary: 'Larger commercial destinations serving a wider area, often on substantial blocks with internal streets and parking. Redevelopment is intended to add activity and improve pedestrian access and connections.',
    considerations: ['Arrange buildings to frame public or internal streets and make entrances easy to reach.', 'Connect pedestrian routes, transit stops and public gathering places.', 'Review the plan’s mix-of-use, parking and comprehensive planning policies before proposing redevelopment.'],
  },
  'Commercial Corridor': {
    summary: 'Commercial areas at important nodes or along major corridors. Existing sites may face parking lots; redevelopment is intended to create more street-oriented buildings, better connections and a comfortable walking environment.',
    considerations: ['Consider commercial frontage along public streets or publicly accessible internal streets.', 'Create safe walking routes through larger sites and manage crossings of vehicle access points.', 'Read any Industrial Transition, comprehensive planning or special policies shown for the site in the source plan.'],
  },
  'Industrial General': {
    summary: 'Areas for light and medium industrial activities, with varied building sizes and some outdoor work or storage. They form part of Calgary’s industrial land supply and can have impacts on neighbouring uses.',
    considerations: ['Consider compatibility between industrial operations, neighbouring activities and sensitive uses.', 'Provide safe pedestrian connections within the site and to public transit.', 'Check the plan’s industrial and area-specific policies before proposing a different use or including housing.'],
  },
  'Industrial Heavy': {
    summary: 'Large sites for heavy industrial operations, often involving outdoor activity and substantial machinery. Noise, dust, vibration or odour can affect neighbouring land.',
    considerations: ['The linked plans state that Industrial Heavy areas should not contain residential or commercial uses.', 'Plan for mitigation of impacts beyond the site, including noise, dust and vehicle movements.', 'Consider landscaping and opportunities for renewable energy alongside operational needs.'],
  },
  'Natural Areas': {
    summary: 'Land whose main role is ecological, supporting habitat, biodiversity, water and air quality and natural processes. Recreation and public access need to respect those functions.',
    considerations: ['Protect ecological features and connections when considering nearby development.', 'Locate pathways and amenities with care for sensitive habitat.', 'Read the plan’s local environmental and area-specific policies for this location.'],
  },
  'Parks and Open Space': {
    summary: 'Publicly accessible outdoor places for recreation and community life, including fields, playgrounds, plazas and gathering areas. Some also contain schools, community buildings or significant cultural sites.',
    considerations: ['Make walking and cycling connections and access for different ages and abilities part of the design.', 'Consider year-round activities, shade, trees and practical maintenance.', 'Buildings and programming should complement the park’s role and any cultural or ecological features.'],
  },
  'City Civic and Recreation': {
    summary: 'Public-land facilities for recreation, civic services, arts and culture, indoors or outdoors. Examples include recreation centres, arenas and integrated community facilities; some activities may require fees or membership.',
    considerations: ['Consider community needs, accessible facilities and use across the seasons.', 'Connect entrances and public spaces to walking routes and nearby transit.', 'Consult the plan for permitted supporting activities, housing and any exceptions to Building Scale policies.'],
  },
  'Private Institutional and Recreation': {
    summary: 'Private-land facilities for education, worship, recreation, arts or culture. These can include private schools, colleges and recreation centres, with access sometimes limited by fees or membership.',
    considerations: ['Consider how proposed activities support the institution or recreation use as the site evolves.', 'Plan safe pedestrian connections to transit and manage parking, servicing and event traffic.', 'Read the plan’s policies on supporting uses and redevelopment before proposing a change.'],
  },
  'Regional Campus': {
    summary: 'Large sites serving regional institutional or transportation functions, such as hospitals, post-secondary institutions or railyards. They often contain multiple buildings and internal streets and may fall under provincial or federal regulation.',
    considerations: ['Use the plan’s campus-specific policies and any applicable master plan when studying redevelopment.', 'Consider connections between the campus, surrounding communities and transit.', 'This colour does not establish a general height allowance or permission to replace the campus use.'],
  },
  'No Urban Form Category': {
    summary: 'The published Urban Form map leaves this land without an assigned urban form category. The grey fill is a legend entry, not a proposed development designation.',
    considerations: ['Do not infer a development use, height or rezoning permission from this colour.', 'Consult the original map and written plan to understand the location’s context.', 'Check current zoning, ownership and any applicable infrastructure or other policy constraints separately.'],
  },
};

export type DesignationReference = Pick<RileyDesignation, 'name' | 'color' | 'section' | 'page' | 'pdfPage'>;
export function localDesignations(id: string, references: DesignationReference[]): RileyDesignation[] {
  if (id === 'riley') return RILEY_DESIGNATIONS;
  return references.map(reference => {
    const explanation = explanations[reference.name];
    if (!explanation) throw new Error(`Missing policy explanation: ${reference.name}`);
    return { ...reference, ...explanation };
  });
}
