import type { PlaceAsset } from "./assetRegistry";
import {
  PARK_TRIO,
  PARK_TRIO_REVISION,
  type ParkTrioKind,
} from "@/components/viewer/globe/parkTrioLayout";

/** Published park assemblies; source references remain the student's selection images. */
export const PARK_TRIO_ASSETS: PlaceAsset[] = (
  Object.keys(PARK_TRIO) as ParkTrioKind[]
).map((kind) => {
  const p = PARK_TRIO[kind];
  return {
    id: `park_trio_${kind}`,
    kind: "object",
    definitionVersion: 1,
    readiness: "pilot",
    label: p.label,
    description:
      kind === "basketball" ? "28 × 15 m playing court, clear run-off, hoops and fenced edges."
        : kind === "tennis" ? "Two 23.77 × 10.97 m doubles courts with nets and separate run-off."
        : kind === "soccer" ? "105 × 68 m pitch with goals, markings and a six-metre perimeter reserve."
        : kind === "cinema"
        ? "A fixed cinema screen, seating and an open viewing lawn."
        : kind === "garden"
          ? "Planted demonstration beds and a curved timber teaching shelter."
          : "A sculpted metal canopy, stage, seating and an open audience lawn.",
    thumbnail: p.image,
    model: {
      variantId: p.variant,
      revision: PARK_TRIO_REVISION,
      method: "source-informed metric landscape",
    },
    calgaryGuide: {
      groupId: ["basketball", "tennis", "soccer"].includes(kind) ? "play_sport" : kind === "garden" ? "gardens" : kind === "concert" ? "regional" : "neighbourhood",
      basis: "form_reference",
    },
    zoneType: "green_space",
    reshapeMode: "adaptive_layout",
    width: p.min[0],
    depth: p.min[1],
    minWidth: p.min[0],
    minDepth: p.min[1],
    maxSize: ["basketball", "tennis", "soccer"].includes(kind) ? 240 : 160,
    reshapeDescription:
      "Playing areas and structures keep their real size. Paths, planting and whole activity elements adapt to the plot; unsuitable shapes are reported.",
    properties: {
      green_space_archetype_id: p.parent,
      green_space_selected_variant_id: p.variant,
      park_trio_layout: PARK_TRIO_REVISION,
    },
  };
});
