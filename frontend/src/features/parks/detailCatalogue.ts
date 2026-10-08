import extras from "./detailCatalogueExtras.json";
export interface DetailAsset {
  id: string;
  label: string;
  category: string;
  description: string;
  dimensions: readonly number[];
  url: string;
  color: string;
  kind: "bench" | "tree" | "object";
  /** Translation in source Y-up coordinates, before the globe conversion. */
  offset?: readonly number[];
}
const extraModels = extras as DetailAsset[];
/** Existing metric assets only. No user-provided paths or nonuniform scaling. */
const RUSTIC = "/landscape-pilots/neighborhood-rustic-v5";
const EQUIPMENT = "/park-kits/shared-park-equipment-v1";
const ORIGINAL_PROP_MODELS = [
  {
    id: "picnic-table-accessible",
    label: "Accessible picnic table",
    category: "Seating",
    description: "Shared outdoor dining with an extended table end.",
    dimensions: [2.76, 1.73, 0.78],
    url: `${EQUIPMENT}/picnic-table-accessible.glb`,
    color: "#a78555",
  },
  {
    id: "dual-stream-bin",
    label: "Waste & recycling bin",
    category: "Street furniture",
    description: "Two compartments for paths, plazas and building entrances.",
    dimensions: [0.84, 0.537, 1.08],
    url: `${EQUIPMENT}/dual-stream-bin.glb`,
    color: "#455f65",
  },
  {
    id: "bike-rack-three-stall",
    label: "Three-space bicycle rack",
    category: "Street furniture",
    description: "Place beside a street or entrance; leave room for bicycles.",
    dimensions: [1.946, 0.15, 0.861],
    url: `${EQUIPMENT}/bike-rack-three-stall.glb`,
    color: "#77828b",
  },
  {
    id: "drinking-fountain-accessible",
    label: "Drinking fountain",
    category: "Street furniture",
    description: "A drinking-water point for parks, paths and plazas.",
    dimensions: [0.925, 0.68, 1.04],
    url: `${EQUIPMENT}/drinking-fountain-accessible.glb`,
    color: "#567785",
  },
  {
    id: "boulders",
    label: "Boulder group",
    category: "Landscape",
    description: "A small group of natural rocks for landscape edges.",
    dimensions: [4.31, 2.812, 1.24],
    url: `${RUSTIC}/boulders.glb`,
    color: "#8c8b7e",
  },
  {
    id: "split-rail",
    label: "Timber fence section",
    category: "Landscape",
    description:
      "One 4.3 m rustic fence section. Rotate and repeat to form an edge.",
    dimensions: [4.328, 0.201, 1.561],
    url: `${RUSTIC}/split-rail.glb`,
    color: "#957856",
  },
] as const;
export const DETAIL_PROP_MODELS = [
  ...ORIGINAL_PROP_MODELS,
  ...extraModels.filter((m) => m.kind === "object"),
];
export type DetailPropVariant = string;
export const DETAIL_CATALOGUE: readonly DetailAsset[] = [
  {
    id: "timber-bench",
    label: "Timber bench",
    category: "Seating",
    description: "A detailed 1.9 m timber bench.",
    dimensions: [1.9, 0.585, 1.075],
    url: `${RUSTIC}/timber-bench.glb`,
    color: "#855633",
    kind: "bench",
  },
  ...(["oak-0", "oak-1", "oak-2"] as const).map((id, i) => ({
    id,
    label: `Oak · shape ${i + 1}`,
    category: "Trees",
    description: "Existing oak model with a natural branching canopy.",
    dimensions: [
      [5.953, 5.853, 9.694],
      [5.964, 5.606, 9.609],
      [5.928, 5.685, 9.037],
    ][i],
    url: `${RUSTIC}/${id}.glb`,
    color: "#76a65c",
    kind: "tree" as const,
  })),
  ...DETAIL_PROP_MODELS.map((model) => ({ ...model, kind: "object" as const })),
  ...extraModels.filter((m) => m.kind === "tree"),
] as const;
export const DETAIL_CATEGORIES = [
  ...new Set(DETAIL_CATALOGUE.map((m) => m.category)),
];
export type DetailAssetId = (typeof DETAIL_CATALOGUE)[number]["id"];
export const detailAsset = (id: DetailAssetId) =>
  DETAIL_CATALOGUE.find((model) => model.id === id)!;
export function searchDetails(query: string, category = "All") {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return DETAIL_CATALOGUE.filter(
    (model) =>
      (category === "All" || category === model.category) &&
      words.every((word) =>
        `${model.label} ${model.description} ${model.category}`
          .toLowerCase()
          .includes(word),
      ),
  );
}
