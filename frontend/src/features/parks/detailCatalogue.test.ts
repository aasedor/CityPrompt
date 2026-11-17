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
    expect(DETAIL_CATALOGUE).toHaveLength(401 + people.length + inclusivePeople.length + recovered.length + safety.length + calgary.filter(a=>a.runtimeApproved).length);
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
    expect(plants).toHaveLength(85);
    expect(plants.filter((m) => m.kind === "tree")).toHaveLength(50);
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
    // Shrubs and hedges have seasonal forms too, so a winter or fall scene is consistent.
    expect(searchDetails("autumn", "Trees").filter((m) => m.label.endsWith("· autumn"))).toHaveLength(8);
    expect(searchDetails("winter", "Planting").map((m) => m.label).filter((label) => label.endsWith("· winter"))).toEqual([
      "Common lilac · winter",
      "Caragana hedge · winter",
      "Cotoneaster hedge · winter",
      "Saskatoon berry · winter",
      "Highbush cranberry · winter",
      "Prickly wild rose · winter",
      "Red-osier dogwood · winter",
    ]);
    expect(searchDetails("autumn", "Planting").map((m) => m.id).filter((id) => id.endsWith("-autumn"))).toEqual([
      "detail-prairie-cotoneaster-hedge-autumn",
      "detail-prairie-saskatoon-autumn",
    ]);
  });
  it("offers the Calgary site details in existing categories plus Winter city and Wildlife", () => {
    const site = extras.filter((m) => m.sourceKit === "calgary-details-v1");
    expect(site).toHaveLength(151);
    expect(site.reduce((bytes, m) => bytes + m.bytes, 0)).toBeLessThan(18_000_000);
    for (const model of site) {
      expect(model.id).toMatch(/^detail-yyc-[a-z-]+$/);
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
      // The card hash is locked in tools/detail_catalogue, not shipped in the bundle.
      expect("thumbnailSha256" in model).toBe(false);
    }
    // People spans two columns, so an even number of other tiles keeps the grid full.
    expect((DETAIL_CATEGORIES.length - 1) % 2).toBe(0);
    expect(searchDetails("", "Winter city")).toHaveLength(12);
    expect(searchDetails("", "Wildlife").map((m) => m.label)).toEqual([
      "White-tailed jackrabbit",
      "Black-billed magpies",
      "Canada geese",
      "Mule deer",
      "Richardson's ground squirrels",
      "Coyote",
      "Mallards",
      "American white pelicans",
      "Osprey nesting platform",
    ]);
    // Transit vehicles join the existing cars and trucks; ranch animals sit with the hay bale.
    expect(searchDetails("bus", "Vehicles").map((m) => m.label)).toEqual(["City bus", "School bus"]);
    expect(searchDetails("ranch", "Landscape").map((m) => m.label)).toEqual(expect.arrayContaining(["Horses", "Cattle"]));
    expect(searchDetails("excavator").map((m) => m.id)).toEqual(["detail-yyc-excavator"]);
    // Painted road barriers share the plain barrier's footprint, so one can replace another in a row.
    // The same eight designs are painted on the low-profile barrier, which has its own footprint.
    const everyMural = searchDetails("mural barrier", "Traffic & safety");
    expect(everyMural).toHaveLength(16);
    for (const [murals, plainId] of [
      [everyMural.filter((m) => m.id.startsWith("detail-yyc-mural-barrier-")), "detail-yyc-concrete-barrier"],
      [everyMural.filter((m) => m.id.startsWith("detail-yyc-low-profile-mural-")), "detail-yyc-low-profile-barrier"],
    ] as const) {
      expect(murals).toHaveLength(8);
      const plain = extras.find((m) => m.id === plainId)!;
      for (const mural of murals) {
        expect(mural.dimensions).toEqual(plain.dimensions);
        expect(mural.description).toContain("Original design.");
      }
    }
    expect(searchDetails("low-profile").map((m) => m.label)[0]).toBe("Low-profile barrier");
    // District barriers carry a business district's logo; each says whose logo it is.
    const districts = searchDetails("district barrier", "Traffic & safety");
    expect(districts.map((m) => m.label)).toEqual([
      "District barrier · Kensington",
      "District barrier · Inglewood",
      "District barrier · Fourth Street · purple",
      "District barrier · Fourth Street · green",
    ]);
    for (const district of districts) {
      expect(district.dimensions).toEqual(extras.find((m) => m.id === "detail-yyc-concrete-barrier")!.dimensions);
      expect(district.description).toContain("belongs to its business association");
    }
    // Planters for the road edge of a patio sit with the other planters and stay under 1.2 m.
    const planters = searchDetails("planter", "Planting").filter((m) => m.id.startsWith("detail-yyc-"));
    expect(planters.map((m) => m.label)).toEqual(["Barrier planter · pink petunias", "Barrier planter · purple petunias", "Long black planter"]);
    for (const planter of planters) expect(planter.dimensions[2]).toBeLessThan(1.2);
    // Seasonal patio pieces: boardwalk sections butt end to end at one width, every platform
    // stays under 1.2 m of guard above the street, and whole patios fit parking stalls.
    const everyBoardwalk = searchDetails("boardwalk", "Access & levels");
    expect(everyBoardwalk.map((m) => m.label)).toEqual([
      "Boardwalk section",
      "Boardwalk section · 1.5 m",
      "Boardwalk end · approach",
      "Boardwalk end · far",
      "Boardwalk module · 6 × 9 ft",
      "Boardwalk module · 6 × 12 ft",
      "Boardwalk corner · 6 × 6 ft",
      "Boardwalk corner · approach",
      "Boardwalk module · 6 × 9 ft · road-side rail",
      "Boardwalk module · 6 × 12 ft · road-side rail",
      "Boardwalk module · 6 × 9 ft · black",
      "Boardwalk module · 6 × 12 ft · black",
      "Boardwalk corner · 6 × 6 ft · black",
      "Boardwalk corner · approach · black",
      "Boardwalk module · 6 × 9 ft · road-side rail · black",
      "Boardwalk module · 6 × 12 ft · road-side rail · black",
    ]);
    for (const piece of everyBoardwalk) expect(piece.dimensions[2]).toBeLessThanOrEqual(1.2);
    const boardwalk = everyBoardwalk.slice(0, 4);
    for (const piece of boardwalk) expect(piece.dimensions[1]).toBe(2.5);
    expect(boardwalk.map((m) => m.dimensions[0])).toEqual([3, 1.5, 3, 3]);
    // The modules in feet are exact to the millimetre, so a run of them does not drift.
    const foot = 0.3048;
    const feet = (m: { dimensions: readonly number[] }) => [m.dimensions[0] / foot, m.dimensions[1] / foot].map((n) => Math.round(n * 100) / 100);
    const sizesInFeet = [[9, 6], [12, 6], [6, 6], [6, 6], [9, 6], [12, 6]];
    expect(everyBoardwalk.slice(4).map(feet)).toEqual([...sizesInFeet, ...sizesInFeet]);
    const patios = extras.filter((m) => /^detail-yyc-(street-patio|parklet)-/.test(m.id));
    expect(patios.map((m) => [m.dimensions[0], m.dimensions[1]])).toEqual([[6, 2.5], [11, 2.5], [6, 2.5], [11, 2.5]]);
    expect(searchDetails("parklet").filter((m) => m.id.startsWith("detail-yyc-")).map((m) => m.label)).toEqual([
      "Parklet · one stall",
      "Parklet · two stalls",
    ]);
    expect(searchDetails("patio", "Seating").map((m) => m.label)).toEqual(expect.arrayContaining([
      "On-street patio · one stall",
      "On-street patio · two stalls",
      "Sidewalk patio",
    ]));
    expect(searchDetails("cart", "Street furniture").map((m) => m.id)).toEqual([
      "detail-yyc-waste-cart-black",
      "detail-yyc-waste-cart-blue",
      "detail-yyc-waste-cart-green",
      "detail-yyc-waste-cart-trio",
      "detail-yyc-shopping-cart",
    ]);
    // Everyday street, lane and yard objects are found by the plain words a student would type.
    expect(searchDetails("dumpster").map((m) => m.id)).toEqual(["detail-yyc-dumpster"]);
    expect(searchDetails("bicycle", "Vehicles").map((m) => m.id)).toEqual([
      "detail-yyc-parked-bicycle",
      "detail-yyc-bike-with-trailer",
    ]);
    expect(searchDetails("snow", "Winter city").map((m) => m.label)).toEqual([
      "Snow fence",
      "Snow windrow",
      "Snowman",
      "Snow shovel in a snowbank",
    ]);
    expect(searchDetails("rink", "Winter city").map((m) => m.id)).toEqual([
      "detail-yyc-outdoor-rink",
      "detail-yyc-rink-board-section",
      "detail-yyc-hockey-net",
      "detail-yyc-warming-hut",
    ]);
  });
});
