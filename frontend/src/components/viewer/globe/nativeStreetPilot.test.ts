import { describe, expect, it } from 'vitest';
import { nativeStreetPilot, nativeStreetPilotForZone, placeNativeStreetModules } from './nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';

const main = nativeStreetPilot('student_main_street_v1')!;
const market = nativeStreetPilot('student_market_street_v1')!;

describe('candidate native street modules on route geometry', () => {
  it('keeps the authored section and native-size modules on straight and bent routes', () => {
    expect(main.widthM).toBe(23);
    expect(main.sections.reduce((sum, band) => sum + band.width, 0)).toBe(main.widthM);
    const straight = placeNativeStreetModules(main, [{ x: 0, y: 0 }, { x: 0, y: 96 }]);
    expect(straight.filter(item => item.kind === 'grove_tree')).toHaveLength(16);
    expect(straight.every(item => item.scale === 1 && item.x >= -main.widthM / 2 && item.x <= main.widthM / 2)).toBe(true);
    expect(straight.filter(item => item.kind === 'grove_tree').map(item => item.stationM))
      .toEqual(straight.filter(item => item.kind === 'tree_well_grate').map(item => item.stationM));
    const bent = placeNativeStreetModules(main, [{ x: 0, y: 0 }, { x: 0, y: 48 }, { x: 48, y: 48 }]);
    expect(bent.every(item => Math.hypot(item.x, item.y - 48) >= main.widthM / 2 + 4)).toBe(true);
    expect(bent.some(item => item.stationM > 63 && Math.abs(item.yaw + Math.PI / 2) < 0.1)).toBe(true);
  });

  it('leaves a clear junction and handles grade without scaling a component', () => {
    const route = [{ x: 0, y: 0, z: 0 }, { x: 0, y: 96, z: 4.8 }];
    const clear = placeNativeStreetModules(main, route, [{ x: 0, y: 24, clearanceM: 15 }]);
    expect(clear.every(item => Math.hypot(item.x, item.y - 24) >= 15)).toBe(true);
    expect(clear.some(item => item.z > 0 && item.z < 4.8)).toBe(true);
    expect(clear.every(item => item.scale === 1)).toBe(true);
  });

  it('keeps the pedestrian market route fully paved with its own rigid furniture', () => {
    expect(market.widthM).toBe(18);
    expect(market.sections.every(band => band.material === 'paving')).toBe(true);
    const placed = placeNativeStreetModules(market, [{ x: 0, y: 0 }, { x: 0, y: 48 }]);
    expect(placed.filter(item => item.kind === 'market_stall')).toHaveLength(4);
    expect(placed.filter(item => item.kind === 'stone_fountain')).toHaveLength(1);
    expect(placed.every(item => item.url.startsWith('/street-kits/pilots/student_market_street_v1/'))).toBe(true);
  });

  it('uses the source metric bands in the local procedural preview', () => {
    expect(nativeStreetPilotForZone({ zone_type: 'road', properties: {
      native_street_pilot_id: main.id, width: 22,
    } })).toBeUndefined();
    expect(nativeStreetPilotForZone({ zone_type: 'road', properties: {
      native_street_pilot_id: main.id, width: 23,
    } })?.sourceAssemblySha256).toBe(main.sourceAssemblySha256);
    const mainProfile = resolvePilotStreetSectionProfile({ properties: {
      road_archetype_id: main.sourceArchetypeId, road_selected_variant_id: 'neighborhood_main_street_v0',
      native_street_pilot_id: main.id, width: main.widthM,
    } });
    const marketProfile = resolvePilotStreetSectionProfile({ properties: {
      road_archetype_id: market.sourceArchetypeId, road_selected_variant_id: 'pedestrian_only_street_v0',
      native_street_pilot_id: market.id, width: market.widthM,
    } });
    expect(mainProfile?.rowM).toBe(23);
    expect(mainProfile?.bands.filter(band => band.kind === 'parking')).toHaveLength(2);
    expect(marketProfile?.rowM).toBe(18);
    expect(marketProfile?.renderCurbs).toBe(false);
    expect(marketProfile?.bands.every(band => band.kind === 'sidewalk' || band.kind === 'path')).toBe(true);
  });
});
