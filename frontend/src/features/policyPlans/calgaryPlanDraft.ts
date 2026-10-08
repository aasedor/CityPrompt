import type { CityPlanMap } from './citywidePlans';

export const CALGARY_PLAN_SOURCE = 'https://www.calgary.ca/content/dam/www/pda/pd/documents/city-building-program/calgary-plan/calgary-plan-annotated-2026-05-21.pdf';
export const CALGARY_PLAN_EDITION = 'Proposed · 21 May 2026 · annotated draft';
const rows: [number, number, string, string, string, string[]][] = [
  [1,25,'City Structure',
    'The proposed city structure: neighbourhood activity, downtown, employment areas and the networks that connect them.',
    'Greater Downtown; Neighbourhood – High, Moderate and Light Activity; Industrial – Core and Mixed; Landfills; Ecological Network; Airport; Transportation Utility Corridor; Water; Major wheeling network; Primary transit network – rapid, regular and conceptual; Roads.',
    ['Activity colours describe the proposed planning role of an area. They are not existing or draft zoning districts.', 'Compare neighbourhood activity with transit access and ecological connections when preparing a student proposal.']],
  [2,26,'Downtown Streets',
    'The proposed downtown street framework for transit, wheeling, active frontages and enhanced landscaping.',
    'Greater Downtown; Transit street; Transit priority area; Wheeling street; Multi-use pathway; Streets with enhanced landscaping; High activity street; Transit line and stop.',
    ['Several functions may share a street. Read line styles together rather than treating each line as a separate road.', 'Use the framework to consider frontages and connections; it is not an engineering layout or current service map.']],
  [3,51,'Natural Systems',
    'The proposed ecological network and its major, supporting and local connections.',
    'Ecological network – Major, Supporting and Local; Existing Major, Supporting and Local Corridor; Future Ecological Corridor; Potential natural area park; Major regional connection; Parks; Greater Downtown; Airport; Water.',
    ['Distinguish existing corridors from future corridors and potential natural-area parks using the legend.', 'Consider habitat continuity alongside public access. A mapped ecological area is not a development permission.']],
  [4,59,'Wheeling Network',
    'The proposed major and supporting wheeling networks and pedestrian or wheeling structures.',
    'Major wheeling network; Supporting wheeling network; Pedestrian/wheeling structure; Greater Downtown; Major parks; Water.',
    ['Major and supporting lines have different network roles. Structures identify crossings or connections.', 'This proposed network is separate from the current CTP 5A layer and does not establish construction timing.']],
  [5,61,'Primary Transit Network',
    'The proposed long-term transit framework, including rapid, conceptual and regional connections and hubs.',
    'Primary transit network – rapid, regular and conceptual; Regional transit corridor; Regional transit hub; Transit hub; Blue line; Green line; Red line; Roads; Greater Downtown; Major parks; Water.',
    ['Use the line and hub symbols together when considering access and development intensity.', 'Conceptual connections are proposals, not confirmation of operating routes, funded projects or final alignments.']],
  [6,63,'Road and Street Network',
    'The proposed hierarchy of skeletal, arterial and collector roads and streets.',
    'Skeletal; Arterial; Collector; Major parks; Greater Downtown; Transportation Utility Corridor; Water.',
    ['The three line categories describe network functions. They do not specify lane counts, setbacks or exact rights of way.', 'Compare the proposed network with current transportation layers when explaining a student design.']],
  [7,65,'Goods Movement Network',
    'The proposed freight framework connecting goods corridors, railways, industrial areas, the airport and intermodal terminals.',
    'Goods movement corridor; Major rail lines; Airport; Intermodal terminal; Industrial areas; Greater Downtown; Major parks; Transportation Utility Corridor; Water.',
    ['Consider freight access alongside pedestrian crossings and the relationship between industrial and residential uses.', 'This policy map is not a truck-routing service or a statement of present vehicle restrictions.']],
  [8,83,'Developing, Redeveloping and Industrial Areas',
    'The proposed distinction between developing, redeveloping and industrial parts of Calgary.',
    'Developing Area; Industrial Area; Redeveloping Area; Landfills; Greater Downtown; Major parks; Airport; Transportation Utility Corridor.',
    ['These areas describe different growth contexts; they are not parcel zoning designations.', 'Read the growth policies and relevant local plan when explaining how a proposal fits its context.']],
];
export const CALGARY_PLAN_MAPS: CityPlanMap[] = rows.map(([number,page,title,summary,legendText,guidance]) => ({
  id:`calgary-plan-${number}`,group:'Calgary Plan',number,page,printedPage:page-4,title,summary,legendText,
  guidance:[...guidance,'Proposed May 2026 edition supplied for classroom comparison. Current MDP and CTP maps remain available separately.'],
  edition:CALGARY_PLAN_EDITION,source:`${CALGARY_PLAN_SOURCE}#page=${page}`,
}));
