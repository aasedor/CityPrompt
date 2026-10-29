/** Plan-specific summaries of Beltline ARP source maps and written sections.
 * These classifications differ from the newer LAP Urban Form categories. */
import type { RileyDesignation } from './rileyDesignations';
const map1 = {page:23,pdfPage:25,section:'Map 3 legend'};
const map2 = {page:18,pdfPage:20,section:'Map 4 legend'};
export const BELTLINE_DESIGNATIONS: Record<string,RileyDesignation[]> = {
  'beltline-part-1': [
    {name:'Primarily Residential',color:'#ffe282',page:29,pdfPage:31,section:'4.2',
      summary:'A primarily residential area in the Beltline land-use concept. Policies address housing at grade, entrances and the conditions for non-residential activities. This colour does not establish a building height or a universal permission for commercial uses.',
      considerations:['Consult Map 3B for at-grade residential and non-residential policy areas.','Provide legible residential entrances and consider privacy alongside an active sidewalk.','Read density, building design, heritage and site-specific policies before proposing a land-use change.']},
    {name:'Urban Mixed-Use Areas',color:'#f8ada3',page:32,pdfPage:34,section:'4.3',
      summary:'Mixed-use areas and business streetscapes intended to be accessible, active and pedestrian scaled. The source plan provides policies for combining activities and shaping the street edge; the concept colour alone does not set density or approve a particular development.',
      considerations:['Arrange compatible activities and support an active pedestrian street edge.','Check the separate density areas and applicable bonusing policies.','Read Warehouse District, heritage commercial concentration and Special Policy Area overlays in the original map.']},
    {name:'Public Park, Pathways, Open Space & Recreation',color:'#a6c492',...map1,
      summary:'Public park, pathway, open-space and recreation land identified by the published Land Use Concept map. This is the map’s open-space classification, separate from residential and urban mixed-use policy areas and from current zoning.',
      considerations:['Retain public access and connections when studying surrounding development.','Use the full plan for parks, recreation, heritage and public-realm direction.','A conceptual map is not a parcel survey or a measurement of developable land.']},
  ],
  'beltline-part-2': [
    {name:'Mixed-Use - High Density',color:'#ffd4b4',page:20,pdfPage:22,section:'3.2.1',
      summary:'A compact mix of compatible activities with street-oriented, pedestrian-scaled buildings. The source policies describe non-residential activity at lower levels to activate the street. Density and composition are addressed separately in section 3.4.',
      considerations:['Consult section 3.4 and the density map before assigning scale or floor area.','Support active lower levels and a comfortable pedestrian environment.','Read the additional character-area and site-design policies for the location.']},
    {name:'Conference, Events and Education',color:'#d1bcd0',page:20,pdfPage:22,section:'3.2.2',
      summary:'An area accommodating conference and Stampede Park facilities, with varied indoor and outdoor activities through the year. The source plan describes complementary commercial and event activities, while additional policies guide access, built form and development scale.',
      considerations:['Consider year-round event activities and the adjoining public realm.','Minimize interruptions to the Stampede Trail pedestrian environment from servicing and driveways.','Read the density, composition and character-area policies alongside the concept map.']},
    {name:'Open Space',color:'#71bf44',...map2,
      summary:'Open space shown by the published Part 2 Land Use Concept map. This fill identifies an open-space role within the culture and entertainment district; it does not establish current ownership, a precise park boundary or development permission.',
      considerations:['Consider walking connections and the river environment.','Consult the plan’s public-realm and character-area policies.','Use the original concept map rather than this overlay for policy interpretation.']},
    {name:'Potential Open Space',color:'#9ad1be',...map2,
      summary:'Potential open space identified by the Part 2 concept map. The word potential is part of the City’s legend: this colour must not be read as confirmation that a public park currently exists or that a particular acquisition or project has been approved.',
      considerations:['Distinguish proposed or potential open space from existing publicly accessible land.','Read the plan’s character-area and public-realm policies for the location.','Confirm current ownership, access and project status separately.']},
    {name:'Railway Corridor',color:'#cdcfd0',...map2,
      summary:'The railway corridor represented in the Part 2 Land Use Concept map. It provides context for nearby policy areas and infrastructure constraints; the map colour does not authorize redevelopment or establish an engineering setback.',
      considerations:['Check current railway and infrastructure requirements independently.','Consider noise, safety and the relationship of nearby uses to the rail corridor.','Read the full plan and applicable technical requirements before proposing adjacent development.']},
  ],
};
