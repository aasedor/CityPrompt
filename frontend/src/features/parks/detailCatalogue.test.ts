import { describe, it, expect } from "vitest";
import {
  DETAIL_CATALOGUE,
  DETAIL_PROP_MODELS,
  searchDetails,
} from "./detailCatalogue";
import equipment from "../../../public/park-kits/shared-park-equipment-v1/kit_manifest.json";
import rustic from "../../../public/landscape-pilots/neighborhood-rustic-v5/manifest.json";
import extras from "./detailCatalogueExtras.json";

describe("standalone detail catalogue", () => {
  it("uses unique local asset paths and the existing source dimensions", () => {
    expect(DETAIL_CATALOGUE).toHaveLength(100);
    expect(new Set(DETAIL_CATALOGUE.map((a) => a.id)).size).toBe(100);
    for (const model of DETAIL_PROP_MODELS.filter(
      (m) => !m.id.startsWith("detail-"),
    )) {
      const source =
        equipment.assets.find((a) => model.url.endsWith("/" + a.file)) ??
        Object.values(rustic.assets).find((a) => a.url === model.url);
      expect(source, model.id).toBeDefined();
      model.dimensions.forEach((dimension, i) =>
        expect(dimension).toBeCloseTo(source!.dimensionsM[i], 2),
      );
    }
  });
  it("has finite metric anchors and locked local assets", () => {
    for (const model of extras) {
      expect(model.url).toMatch(/^\/(park-kits|street-kits)\/[\w/-]+\.glb$/);
      expect(model.sha256).toMatch(/^[a-f0-9]{64}$/);
      expect(model.offset).toHaveLength(3);
      expect(model.offset.every(Number.isFinite)).toBe(true);
      expect(model.dimensions.every((n) => Number.isFinite(n) && n > 0)).toBe(
        true,
      );
    }
  });
  it("filters by category and searchable purpose", () => {
    expect(searchDetails("picnic", "Seating").map((a) => a.id)).toEqual([
      "picnic-table-accessible",
    ]);
    expect(searchDetails("water", "Street furniture").map((a) => a.id)).toEqual(
      ["drinking-fountain-accessible"],
    );
    expect(searchDetails("", "Trees").length).toBeGreaterThanOrEqual(8);
    expect(searchDetails("zzzz")).toEqual([]);
  });
});
