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
  it("offers the twenty site-finishing details with bounded geometry", () => {
    const slugs = ['outdoor-stairs', 'accessible-ramp', 'modular-handrail', 'retaining-wall',
      'refuge-island', 'planted-curb-extension', 'tactile-curb-ramp', 'covered-bike-parking',
      'bicycle-locker', 'ev-charger', 'accessible-parking', 'loading-zone', 'waste-enclosure',
      'privacy-screen', 'public-art', 'food-truck', 'cafe-barrier', 'community-noticeboard',
      'rainwater-cistern', 'public-washroom'];
    const batch = extras.filter(m => m.id.startsWith('detail-site-'));
    expect(batch.map(m => m.id).sort()).toEqual(slugs.map(s => `detail-site-${s}`).sort());
    expect(batch.reduce((sum, m) => sum + m.bytes, 0)).toBeLessThan(5_000_000);
    batch.forEach(m => { expect(m.triangles).toBeLessThan(25_000); expect(m.meshes).toBeLessThanOrEqual(10); });
    expect(searchDetails('ramp', 'Access & levels').map(m => m.id)).toContain('detail-site-accessible-ramp');
  });
  it("uses unique local asset paths and the existing source dimensions", () => {
    expect(DETAIL_CATALOGUE).toHaveLength(165);
    expect(new Set(DETAIL_CATALOGUE.map((a) => a.id)).size).toBe(165);
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
      "detail-classic-picnic-table",
    ]);
    expect(searchDetails("water", "Street furniture").map((a) => a.id)).toEqual(
      ["drinking-fountain-accessible"],
    );
    expect(searchDetails("", "Trees").length).toBeGreaterThanOrEqual(8);
    expect(searchDetails("zzzz")).toEqual([]);
  });
  it("exposes the second batch with bounded geometry and useful search terms", () => {
    const batch = extras.filter((m) => m.sourceKit === "standalone-details-v2");
    expect(batch).toHaveLength(35);
    expect(batch.reduce((bytes, m) => bytes + m.bytes, 0)).toBeLessThan(4_000_000);
    for (const model of batch) {
      expect(model.triangles).toBeLessThan(20_000);
      expect(model.meshes).toBeLessThanOrEqual(8);
    }
    expect(searchDetails("bicycle pump").map((m) => m.id)).toContain(
      "detail-bicycle-pump",
    );
    expect(searchDetails("dog", "Play").map((m) => m.id)).toEqual([
      "detail-dog-agility-hoop",
      "detail-dog-agility-tunnel",
    ]);
  });
});
