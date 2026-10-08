import { CALGARY_PLAN_MAPS } from './calgaryPlanDraft';
export type CityPlanGroup = "MDP" | "CTP" | "TRANSIT" | "Calgary Plan";
export type CityPlanMap = {
  id: string;
  group: CityPlanGroup;
  number?: number;
  title: string;
  page?: number;
  printedPage?: number;
  summary: string;
  guidance: string[];
  legendText: string;
  source: string;
  edition?: string;
};
const MDP =
  "https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgAction=Download&msgID=OTTKcgyTerX";
const CTP =
  "https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgAction=Download&msgID=ETerrTTsycC";
export const CITY_PLAN_EDITION =
  "Office consolidation · 23 June 2026 · 18P2026";
const maps: Omit<CityPlanMap, "source">[] = [
  {
    id: "mdp-1",
    group: "MDP",
    number: 1,
    title: "Urban Structure",
    page: 188,
    printedPage: 160,
    summary:
      "The city-wide pattern of activity centres, main streets, residential areas, employment land and major open spaces that guides Calgary’s growth.",
    guidance: [
      "Activity centres and main streets concentrate a mix of people, jobs and services. Their colours describe a planning role, not a Land Use Bylaw district.",
      "Inner City, Established and greenfield areas have different growth contexts. Read the relevant typology policies and the local area plan before designing.",
      "The Balanced Growth Boundary distinguishes developed and developing areas for the plan’s growth framework.",
    ],
    legendText:
      "Greater Downtown; Major Activity Centre; Community Activity Centre; Urban Main Street; Neighbourhood Main Street; Inner City; Established; Planned Greenfield with Area Structure Plan; Future Greenfield; Industrial – Employee Intensive; Standard Industrial; Major Public Open Space; Public Utility; Balanced Growth Boundary.",
  },
  {
    id: "mdp-2",
    group: "MDP",
    number: 2,
    title: "Primary Transit Network",
    page: 189,
    printedPage: 161,
    summary:
      "The long-term transit network and its relationship to centres, main streets and employment areas.",
    guidance: [
      "Use the line and station symbols together: rail lines, frequent transit corridors and transit connections have different roles.",
      "A planned corridor or station on this policy map is not confirmation of an operating service, a final alignment or a funded construction date.",
      "Compare with Urban Structure and the local area plan when considering access and development intensity.",
    ],
    legendText:
      "Primary Transit Network, LRT lines and stations, transit corridors and connections, plus Urban Structure context. Read the original legend below for line and symbol distinctions.",
  },
  {
    id: "mdp-3",
    group: "MDP",
    number: 3,
    title: "Road and Street Network",
    page: 190,
    printedPage: 162,
    summary:
      "The planned roles of major roads and streets, including routes that move across the city and streets that also support places and neighbourhood life.",
    guidance: [
      "Skeletal roads, arterial streets, urban and neighbourhood boulevards, industrial arterials and parkways have different functions.",
      "A line is a conceptual network designation, not a surveyed right of way or a detailed street design.",
      "Some roads remain to be classified through future local area plans. Read the road policies alongside the land-use context.",
    ],
    legendText:
      "Skeletal Road; Arterial Street; Urban Boulevard; Industrial Arterial; Neighbourhood Boulevard; Parkway; roads awaiting classification; regional connections; Collector Roads.",
  },
  {
    id: "mdp-4",
    group: "MDP",
    number: 4,
    title: "Open Space and Naturally Vegetated Lands",
    page: 191,
    printedPage: 163,
    summary:
      "The city-wide distribution of natural areas, parks, open space and provincial park lands.",
    guidance: [
      "The different greens distinguish land with ecological functions from parks and other open spaces; they are not interchangeable development opportunities.",
      "Consider habitat connections, access and neighbouring open spaces when shaping a site.",
      "Map 4 was updated through 57P2025. Check detailed City inventories and site conditions before drawing conclusions about a particular parcel.",
    ],
    legendText: "Natural Areas; Parks; Open Space; Provincial Park.",
  },
  {
    id: "mdp-5",
    group: "MDP",
    number: 5,
    title: "Jurisdictional Areas",
    page: 192,
    printedPage: 164,
    summary:
      "Calgary’s relationship with neighbouring municipalities and Tsuut’ina Nation, including intermunicipal planning and identified growth areas.",
    guidance: [
      "Municipal boundaries, intermunicipal development areas and long-term growth areas mean different things. Use the hatching and outlines in the legend.",
      "A growth-area designation does not itself annex land or grant permission to develop.",
      "For sites near the city edge, read the applicable intermunicipal plan and confirm which jurisdiction administers the land.",
    ],
    legendText:
      "City Limits; Transportation/Utility Corridor; Identified City of Calgary Long-Term Growth Areas; Calgary Growth Area; Chestermere–Calgary interface; intermunicipal development areas for Foothills, Rocky View County and Chestermere; Tsuut’ina Nation.",
  },
  {
    id: "mdp-6",
    group: "MDP",
    number: 6,
    title: "Major Development Influences",
    page: 193,
    printedPage: 165,
    summary:
      "A screening map of major environmental, infrastructure and operational influences that may affect development.",
    guidance: [
      "Airport noise and vicinity protection, flood areas, slopes, facilities, gas infrastructure and their mapped setbacks can affect what needs further investigation.",
      "Hatching, lines, buffers and solid areas represent different influences; more than one may apply at the same place.",
      "This is a conceptual policy snapshot. Confirm current boundaries, regulations and site-specific studies before treating a mapped buffer as an exact constraint.",
    ],
    legendText:
      "Airport 30NEF; Airport Vicinity Protection Area; landfill sites; gravel operations; wastewater treatment; floodway/flood fringe; major parks; slopes of at least 15%; correctional facility; sour gas lines, buffers, facilities and residential setbacks; gas plant and setback; Tsuut’ina Nation; Transportation/Utility Corridor.",
  },
  {
    id: "ctp-1",
    group: "CTP",
    number: 1,
    title: "5A Network",
    page: 100,
    printedPage: 92,
    summary:
      "The Always Available for All Ages and Abilities network for walking and wheeling, showing existing and recommended pathways and on-street bikeways.",
    guidance: [
      "Blue represents on-street bikeways and red represents pathways. Solid and dashed symbols distinguish existing and recommended routes.",
      "The map describes the future planned build-out. Existing routes may still need upgrades to meet 5A standards.",
      "Recommended grade-separated crossings, transit, schools and recreation facilities help explain network connections. Consult the exact legend and its footnotes.",
    ],
    legendText:
      "Recommended On-Street Bikeway – 5A; Recommended Pathway – 5A; Existing On-Street Bikeway – 5A; Existing Pathway – 5A; Recommended Grade-Separated Crossing; schools; recreation; LRT; MAX BRT; Future LRT.",
  },
  {
    id: "ctp-2",
    group: "CTP",
    number: 2,
    title: "Primary Transit Network",
    page: 101,
    printedPage: 93,
    summary:
      "The transportation plan’s long-term Primary Transit Network, connecting communities and key destinations.",
    guidance: [
      "Read the different transit line and station symbols in the legend; the map includes planned network elements.",
      "The network supports high-quality transit access and the land-use pattern shown in the MDP.",
      "Use current transit information for today’s services. This policy map does not establish project funding, opening dates or final engineering.",
    ],
    legendText:
      "Primary Transit Network, LRT lines and stations, transit corridors and regional connections, with Urban Structure context.",
  },
  {
    id: "ctp-3",
    group: "CTP",
    number: 3,
    title: "Downtown Transit Network",
    page: 102,
    printedPage: 94,
    summary:
      "A closer view of downtown transit corridors, LRT lines and stations in the transportation plan.",
    guidance: [
      "The published page is rotated. The overlay is geographically aligned, so it follows the globe when viewed north-up.",
      "Purple corridors and the different LRT symbols have distinct meanings; planned routes are not necessarily operating today.",
      "Use this map to study downtown connections, then consult the current transit and project information for implementation details.",
    ],
    legendText:
      "Transit Corridors; Proposed LRT; Centre City; Red LRT Line; Blue LRT Line; Blue/Red LRT Line; Future Green Line and Station.",
  },
  {
    id: "ctp-5",
    group: "CTP",
    number: 5,
    title: "Primary Goods Movement Network",
    page: 104,
    printedPage: 96,
    summary:
      "The main network and destinations supporting movement of goods through Calgary.",
    guidance: [
      "Consider freight access and the relationship between major routes, industrial areas, rail and logistics destinations.",
      "The policy network is not a turn-by-turn truck route or a statement of current vehicle restrictions.",
      "When placing homes or public spaces near freight routes, consider access, crossings, noise and the relevant local policies.",
    ],
    legendText:
      "Primary Goods Movement Network, connections to routes in the region, rail and major freight destinations, with industrial and activity-centre context.",
  },
  {
    id: "ctp-6",
    group: "CTP",
    number: 6,
    title: "Primary HOV Network",
    page: 105,
    printedPage: 97,
    summary:
      "The planned network for high-occupancy vehicles, intended to help move more people efficiently in shared vehicles.",
    guidance: [
      "The HOV lines describe a policy network, not confirmation that an HOV lane operates on every marked road today.",
      "Compare the network with transit routes, activity centres and major employment destinations.",
      "Read the plan’s HOV policies and current road information for how a specific corridor is implemented.",
    ],
    legendText:
      "HOV Network (Auto and/or Transit Focus); Provincial HOV Network (to be confirmed with Province); Urban Structure context; Transportation/Utility Corridor; City Limits.",
  },
  {
    id: "ctp-7",
    group: "CTP",
    number: 7,
    title: "Road and Street Network",
    page: 106,
    printedPage: 98,
    summary:
      "The transportation plan’s network of road and street types and connections to the region.",
    guidance: [
      "Distinguish skeletal roads, arterials, boulevards, industrial arterials and parkways using the original colours.",
      "These are long-term functional roles. They do not specify an exact carriageway, building setback or final project alignment.",
      "Read with the MDP land-use structure and the applicable local area plan.",
    ],
    legendText:
      "Skeletal Road; Arterial Street; Urban Boulevard; Industrial Arterial; Neighbourhood Boulevard; Parkway; unclassified future roads; regional connections; Collector Roads.",
  },
];
export const CITY_PLAN_MAPS: CityPlanMap[] = [...maps.map((map) => ({
  ...map,
  source: `${map.group === "MDP" ? MDP : CTP}#page=${map.page}`,
})), ...CALGARY_PLAN_MAPS];
export const CITY_MAP_LAYERS: CityPlanMap[] = [...CITY_PLAN_MAPS, {
  id: 'service-routes', group: 'TRANSIT', title: 'Calgary Transit routes',
  source: 'https://data.calgary.ca/Transportation-Transit/Calgary-Transit-Routes/hpnd-riq4',
  summary: 'Published Calgary Transit service routes. Select a route to see its number, name and service category.',
  guidance: ['These service routes are separate from the MDP/CTP long-term policy network.',
    'School, express and special routes may run only at particular times. Route presence does not establish frequency or all-day service.',
    'Use Calgary Transit trip planning for current schedules, detours and arrivals.'],
  legendText: 'Lines show the route categories supplied by Calgary Transit. Overlapping routes can be inspected individually using Choose transit route.',
}, {
  id: 'service-stops', group: 'TRANSIT', title: 'Calgary Transit stops',
  source: 'https://data.calgary.ca/Transportation-Transit/Calgary-Transit-Stops/muzh-c9qc',
  summary: 'Active stop locations in the City snapshot. Click a stop for its name, stop number and published serving routes.',
  guidance: ['Only stops marked ACTIVE in the source are shown.',
    'Serving routes come from the City’s separately updated stop-to-route table. An empty list means no association was available in this snapshot.',
    'Stop locations are useful for access planning; this layer does not show live arrivals or confirm step-free access.'],
  legendText: 'Teal circles indicate active Calgary Transit stops.',
}];
export const CITY_PLAN_ASSETS = "/policy-maps/citywide-2026-v1";
export type MapPreference = { enabled: boolean; opacity: number; format?: 'vector' | 'pdf'; routeId?: string };
export function readCityPlanPreferences(
  raw: string | null,
): Record<string, MapPreference> {
  let value: Record<string, unknown> = {};
  try {
    const parsed = JSON.parse(raw ?? "{}");
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed))
      value = parsed;
  } catch {
    /* Optional browser storage. */
  }
  return Object.fromEntries(
    CITY_MAP_LAYERS.map((map) => {
      const saved = value[map.id] as Partial<MapPreference> | undefined;
      return [
        map.id,
        {
          enabled: saved?.enabled === true,
          ...(map.group !== 'TRANSIT' && saved?.format === 'pdf' ? { format: 'pdf' as const } : {}),
          ...(map.id === 'service-routes' && typeof saved?.routeId === 'string' ? { routeId: saved.routeId } : {}),
          opacity:
            typeof saved?.opacity === "number" && Number.isFinite(saved.opacity)
              ? Math.max(0, Math.min(1, saved.opacity))
              : 0.7,
        },
      ];
    }),
  );
}
export type PlanTile = {
  id: string;
  rect: [number, number, number, number];
  grid: [number, number][];
};
export type PlanRaster = {
  id: string;
  overview: string;
  tiles: PlanTile[];
  gridSize: number;
  bounds: [number, number, number, number];
  accuracy: string;
};
