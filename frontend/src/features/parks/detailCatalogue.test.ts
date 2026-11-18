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
  it.each([
    ["calgary-details-v1", 165],
    ["prairie-foliage-v1", 85],
  ])("offers every imported %s model with its source thumbnail", (sourceKit, count) => {
    const models = extras.filter(model => model.sourceKit === sourceKit);
    expect(models).toHaveLength(count);
    for (const model of models) {
      expect(DETAIL_CATALOGUE.find(asset => asset.id === model.id)?.kind).toBe(model.kind);
      expect(model.thumbnailUrl).toBe(model.url.replace(/\.glb$/, ".webp"));
      expect(DETAIL_PROP_MODELS.some(asset => asset.id === model.id)).toBe(model.kind === "object");
    }
  });
  it("finds Calgary props and prairie trees through the existing picker search", () => {
    expect(searchDetails("city ghost pink").map(asset => asset.id)).toContain("detail-yyc-city-ghost-barrier-pink");
    // Shared micromobility: the City's pipe-and-panel corral, plain and in the eight original murals, and the older painted bay
    expect(DETAIL_CATEGORIES).toContain("Shared micromobility");
    const corrals = searchDetails("", "Shared micromobility").map(asset => asset.id);
    expect(corrals).toEqual(["detail-yyc-scooter-corral", ...["plain", "foothills", "chinook", "river", "mosaic", "chevron", "quilt", "aspen", "confetti"]
      .map(design => `detail-yyc-scooter-corral-${design}`), "detail-yyc-scooter-corral-bird-lime"]);
    expect(searchDetails("e-scooter corral", "Street furniture")).toHaveLength(0);
    expect(searchDetails("trembling aspen", "Trees").map(asset => asset.id)).toContain("detail-prairie-trembling-aspen");
    expect(searchDetails("swedish columnar aspen", "Trees").map(asset => asset.id)).toContain("detail-prairie-swedish-columnar-aspen");
  });
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
    expect(DETAIL_CATALOGUE).toHaveLength(415 + people.length + inclusivePeople.length + recovered.length + safety.length + calgary.filter(a=>a.runtimeApproved).length);
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
});
