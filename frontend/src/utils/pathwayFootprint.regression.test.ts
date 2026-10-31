import { describe, expect, it } from 'vitest';
import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
import { densifyPolyline } from '@/components/viewer/globe/streetMesh3D';
import { nativeStreetPilot } from '@/components/viewer/globe/nativeStreetPilot';
import { buildNativeStreetProgram } from '@/components/viewer/globe/nativeStreetProgram';
import { pathwaySurfacePolygons } from './pathwayFootprint';

// Metre-only live QA route with <1 nm numerical variation, reproducing the
// polygon union failure between equivalent coordinate conversions. No location data.
const route: number[][] = [
  [-43.37040387945421, -9.368474848169068],
  [-42.13290613056446, -9.368399122654022],
  [-41.17642913331813, -9.20701756067177],
  [-40.32579628625503, -8.740845155971384],
  [-27.736610875620602, 1.2006311861213177],
  [-26.164380870922674, 2.1704366669234316],
  [-24.411626314236127, 2.753771172179644],
  [-22.571802952096423, 2.9195316820410873],
  [-20.74300898741743, 2.6588799549466153],
  [-19.022754535770286, 1.9857137745607765],
  [-17.5027624563027, 0.9359259243633231],
  [-11.078081150951565, -4.700531320805685],
  [-9.487784878528247, -5.7872559534204395],
  [-7.683837745519605, -6.462374291478596],
  [-5.770812929120765, -6.68675034116033],
  [-3.8596067424596443, -6.447377226361994],
  [-2.0610100687507438, -5.758131186411682],
  [-0.47928592179056356, -4.658967188150676],
  [8.835855620879604, 3.643519685363112],
  [10.459286499234395, 4.764592329487395],
  [12.307711035494036, 5.45427022421105],
  [14.268712051878241, 5.670608655510485],
  [16.223025716497204, 5.40045038607902],
  [18.05179491172861, 4.6602258566911665],
  [24.333409669740114, 1.1611343611352858],
  [26.076951637626827, 0.4441771706896767],
  [27.93985714944196, 0.15513098507520237],
  [29.818677398655673, 0.31004679792696915],
  [31.60907981072311, 0.9003219970953781],
  [33.211641738999646, 1.8931780738944692],
  [34.537371489801565, 3.233480839743568],
  [35.51265010071175, 4.846802081385866],
  [42.39287701955774, 20.023294390714305],
];

describe('winding pathway surface regression', () => {
  it.each([
    [0, 0, 0], [1e-8, -1e-8, 0], [100, 200, 0], [-500, 700, 0],
    [0, 0, 15], [0, 0, 30], [0, 0, 45], [0, 0, 90],
    [100, 200, 15], [-500, 700, 30],
  ])('builds the saved path in equivalent local frame %s/%s/%s', (dx, dy, degrees) => {
    const angle = degrees * Math.PI / 180;
    const local = route.map(([x, y]) => ({
      x: x * Math.cos(angle) - y * Math.sin(angle) + dx,
      y: x * Math.sin(angle) + y * Math.cos(angle) + dy,
    }));
    const dense = densifyPolyline(local, 4).map(({ x, y }) => [x, y]);
    const original = JSON.stringify(dense);
    const surface = pathwaySurfacePolygons(dense, 1.8);
    expect(surface).toHaveLength(1);
    expect(surface.flat(3).every(Number.isFinite)).toBe(true);
    for (const point of dense) {
      expect(booleanPointInPolygon(point, { type: 'MultiPolygon', coordinates: surface })).toBe(true);
    }
    expect(JSON.stringify(dense)).toBe(original);
  });
  it('renders the saved surface at different terrain sampling densities', () => {
    const pilot = nativeStreetPilot('concrete_neighbourhood_walk_v1')!;
    for (const step of [.5, 2, 4, 8]) {
      const dense = densifyPolyline(route.map(([x, y]) => ({ x, y })), step);
      const parts = buildNativeStreetProgram(pilot.program!, pilot.widthM, pilot.fixtureLengthM, dense);
      expect(parts.length).toBeGreaterThan(0);
      for (const { geometry } of parts) {
        expect(geometry.getIndex()!.count).toBeGreaterThan(0);
        expect(Array.from(geometry.getAttribute('position').array).every(Number.isFinite)).toBe(true);
        geometry.dispose();
      }
    }
  });
});
