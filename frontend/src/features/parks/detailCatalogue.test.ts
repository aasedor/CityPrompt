import { describe, it, expect } from "vitest";
import {
  DETAIL_CATALOGUE,
  DETAIL_CATEGORIES,
  DETAIL_PROP_MODELS,
  searchDetails,
} from "./detailCatalogue";
import equipment from "../../../public/park-kits/shared-park-equipment-v1/kit_manifest.json";
import rustic from "../../../public/landscape-pilots/neighborhood-rustic-v5/manifest.json";
import extras from "./detailCatalogueExtras.json";
import recovered from "./recoveredDetails.json";
import safety from './trafficSafetyCatalogue.json';
import calgary from './calgarySafetyCatalogue.json';
import people from '../people/peopleCatalogue.json';
import inclusivePeople from '../people/inclusivePeopleCatalogue.json';

describe("standalone detail catalogue", () => {
  it('finds People by the clothing styles shown on their appearance cards', () => {
    expect(searchDetails('summer dress', 'People').map(asset => asset.id)).toContain('people-pilot-creative');
    expect(searchDetails('linen jumpsuit', 'People').map(asset => asset.id)).toContain('people-community-elena');
  });
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
    expect(DETAIL_CATALOGUE).toHaveLength(273 + people.length + inclusivePeople.length + recovered.length + safety.length + calgary.filter(a=>a.runtimeApproved).length);
    expect(new Set(DETAIL_CATALOGUE.map((a) => a.id)).size).toBe(DETAIL_CATALOGUE.length);
    for (const model of DETAIL_PROP_MODELS.filter(
      (m) => !m.id.startsWith("detail-") && !('safety' in m) && !('people' in m) && !('peopleRepresentation' in m),
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
      "detail-meshy-07_table_civic_picnic",
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
  it("offers the local prairie plants with trunk-anchored placement and seasonal forms", () => {
    const plants = extras.filter((m) => m.sourceKit === "prairie-foliage-v1");
    expect(plants).toHaveLength(70);
    expect(plants.filter((m) => m.kind === "tree")).toHaveLength(44);
    for (const model of plants) {
      expect(model.category).toBe(model.kind === "tree" ? "Trees" : "Planting");
      expect([model.offset[0], model.offset[2]]).toEqual([0, 0]);
      expect(model.triangles).toBeLessThanOrEqual(model.kind === "tree" ? 14_000 : 6_000);
      expect(model.meshes).toBeLessThanOrEqual(2);
    }
    expect(searchDetails("winter", "Trees")).toHaveLength(17);
    expect(searchDetails("snow", "Trees").map((m) => m.id)).toEqual([
      "detail-prairie-white-spruce-snow",
      "detail-prairie-colorado-blue-spruce-snow",
    ]);
    expect(searchDetails("crocus").map((m) => m.id)).toEqual(["detail-prairie-prairie-crocus"]);
  });
  it("offers the Calgary site details in existing categories plus Winter city and Wildlife", () => {
    const site = extras.filter((m) => m.sourceKit === "calgary-details-v1");
    expect(site).toHaveLength(38);
    expect(site.reduce((bytes, m) => bytes + m.bytes, 0)).toBeLessThan(4_000_000);
    for (const model of site) {
      expect(model.id).toMatch(/^detail-calgary-[a-z-]+$/);
      expect(model.kind).toBe("object");
      expect(model.triangles).toBeLessThan(3_500);
      expect(model.meshes).toBeLessThanOrEqual(2);
      expect([model.offset[0], model.offset[2]]).toEqual([0, 0]);
    }
    const start = DETAIL_CATEGORIES.indexOf("Winter city");
    expect(DETAIL_CATEGORIES.slice(start, start + 2)).toEqual(["Winter city", "Wildlife"]);
    // Both local kits ship a static card image, so browsing never downloads a model.
    for (const model of extras.filter((m) => m.sourceKit === "calgary-details-v1" || m.sourceKit === "prairie-foliage-v1")) {
      expect(model.thumbnailUrl).toBe(model.url.replace(/\.glb$/, ".webp"));
      expect(model.thumbnailSha256).toMatch(/^[a-f0-9]{64}$/);
    }
    // People spans two columns, so an even number of other tiles keeps the grid full.
    expect((DETAIL_CATEGORIES.length - 1) % 2).toBe(0);
    expect(searchDetails("", "Winter city")).toHaveLength(9);
    expect(searchDetails("", "Wildlife").map((m) => m.label)).toEqual([
      "White-tailed jackrabbit",
      "Black-billed magpies",
      "Canada geese",
      "Mule deer",
    ]);
    expect(searchDetails("cart", "Street furniture").map((m) => m.id)).toEqual([
      "detail-calgary-waste-cart-black",
      "detail-calgary-waste-cart-blue",
      "detail-calgary-waste-cart-green",
      "detail-calgary-waste-cart-trio",
    ]);
    expect(searchDetails("rink", "Winter city").map((m) => m.id)).toEqual([
      "detail-calgary-outdoor-rink",
      "detail-calgary-rink-board-section",
      "detail-calgary-hockey-net",
      "detail-calgary-warming-hut",
    ]);
  });
});
