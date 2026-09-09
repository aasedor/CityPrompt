import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { applyManualParkAccessSnapshot, derivedParkAccessGuides, getDerivedParkAccess, resolveManualParkAccess, type ParkAccessPoint } from './parkAccessConnections';
import { parkGroundSourceSignature, resolveParkGroundProfile } from './parkGroundProfiles';
import { buildParkGroundPrompt } from './parkGroundTexture';
import { computeParkPlacements, parkPlacementClearsExclusions, resolveParkRecipeForZone } from './parkScatter';
import { resolveParkProgramAnchorLayout } from './parkLegoFamilies';

const ll = ([x, y]: number[]): ParkAccessPoint => [-114 + x / metersPerDegLon(51), 51 + y / METERS_PER_DEG_LAT];
const xy = ([lng, lat]: number[]): ParkAccessPoint => [(lng + 114) * metersPerDegLon(51), (lat - 51) * METERS_PER_DEG_LAT];
function zone(id: string, type: SiteZone['zone_type'], polygon: number[][], properties: SiteZone['properties'] = {}): SiteZone {
  return { id, project_id: 'pilot', zone_type: type, coordinates: polygon.map(ll), properties, color: '#777777', sort_order: 0, created_at: '2026-09-04', updated_at: '2026-09-04' };
}
function fixture() {
  const park = zone('park', 'green_space', [[0, 0], [40, 0], [40, 28], [0, 28]], { green_space_archetype_id: 'urban_pocket_park' });
  const line = [[-15, -6], [55, -6]].map(ll);
  const street = { ...zone('street', 'road', [], { road_archetype_id: 'narrow_residential_street', width: 10, plan_centerline: line }), coordinates: bufferLineToPolygon(line, 10) };
  const boundary = { ...zone('site', 'site_boundary', [[-50, -50], [120, -50], [120, 100], [-50, 100]], { terrain_elevation_m: 1000 }), is_active_boundary: true };
  return { park, street, boundary, zones: [park, street, boundary] };
}

describe('manual park access planning', () => {
  it('keeps park access inside the site when its street continues to the public road',()=>{
    const {park,street,boundary}=fixture();
    const line=[[-60,-6],[55,-6]].map(ll);
    const extended={...street,coordinates:bufferLineToPolygon(line,10),properties:{...street.properties,plan_centerline:line,connect_to_public_road:true}};
    const plan=resolveManualParkAccess([park,extended,boundary]).parks[0];
    expect(plan.status).toBe('connected');
    expect(plan.connections.every(connection=>xy(connection.streetPoint)[0]>-50)).toBe(true);
    const outside={...park,coordinates:park.coordinates.map(point=>ll([xy(point)[0]-70,xy(point)[1]]))};
    expect(resolveManualParkAccess([outside,extended,boundary]).parks[0].connections).toHaveLength(0);
  });
  it('joins the paved edge of the shared-street pilot, without crossing its carriageway',()=>{
    const {park,street,boundary}=fixture(),line=[[-15,-4],[55,-4]].map(ll);
    const shared={...street,coordinates:bufferLineToPolygon(line,6),properties:{road_archetype_id:'yield_street',width:6,lane_count:1,plan_centerline:line}};
    const plan=resolveManualParkAccess([park,shared,boundary]).parks[0];
    expect(plan.status).toBe('connected');
    expect(xy(plan.connections[0].streetPoint)[1]).toBeCloseTo(-1.15,2);
  });
  it('connects to a selected existing path, preserves boundary limits and invalidates removed context',()=>{
    const {park,boundary}=fixture();
    const transport={lines:[{id:'existing:path',label:'Mapped path',kind:'path' as const,widthM:null,points:[ll([-10,-3]),ll([50,-3])]}]};
    const selected={...park,properties:{...park.properties,pedestrian_park_entrance:{version:1,edge:0,position:0.5,streetId:'existing:path',existingGroundConfirmed:true}}};
    const snapshot=resolveManualParkAccess([selected,boundary],{},[],transport);
    expect(snapshot.parks[0].status).toBe('connected');
    expect(xy(snapshot.parks[0].connections[0].streetPoint)[1]).toBeCloseTo(-3,5);
    expect(getDerivedParkAccess(applyManualParkAccessSnapshot([selected,boundary],snapshot,transport)[0])).not.toBeNull();
    expect(getDerivedParkAccess(applyManualParkAccessSnapshot([selected,boundary],snapshot)[0])).toBeNull();
    const unconfirmed={...selected,properties:{...selected.properties,pedestrian_park_entrance:{...selected.properties.pedestrian_park_entrance,existingGroundConfirmed:false}}};
    expect(resolveManualParkAccess([unconfirmed,boundary],{},[],transport).parks[0].reason).toContain('ground level');
    const road={id:'road',label:'Road',kind:'road' as const,widthM:null,points:[ll([-10,-1.5]),ll([50,-1.5])]};
    expect(resolveManualParkAccess([selected,boundary],{},[],{lines:[...transport.lines,road]}).parks[0].connections).toHaveLength(0);
    const smaller={...boundary,coordinates:[[-10,0],[50,0],[50,50],[-10,50]].map(ll)};
    expect(resolveManualParkAccess([selected,smaller],{},[],transport).parks[0].connections).toHaveLength(0);
    expect(resolveManualParkAccess([park,boundary],{},[],transport).parks[0].connections).toHaveLength(0);
    const edgeBoundary={...boundary,coordinates:[[-10,-2],[50,-2],[50,50],[-10,50]].map(ll)};
    const widePath={lines:[{...transport.lines[0],widthM:4}]};
    const edgePlan=resolveManualParkAccess([selected,edgeBoundary],{},[],widePath).parks[0];
    expect(edgePlan.status).toBe('connected');
    expect(xy(edgePlan.connections[0].streetPoint)[1]).toBeCloseTo(-1.15,5);
  });
  it('honours an editable entrance and does not silently choose another edge', () => {
    const {park,street,boundary}=fixture();
    const locked={...park,properties:{...park.properties,pedestrian_park_entrance:{version:1,edge:0,position:0.25,streetId:street.id}}};
    const plan=resolveManualParkAccess([locked,street,boundary]).parks[0];
    expect(plan.status).toBe('connected');expect(xy(plan.connections[0].gateway)[0]).toBeCloseTo(10,3);
    const away={...locked,properties:{...locked.properties,pedestrian_park_entrance:{version:1,edge:2,position:0.5,streetId:street.id}}};
    expect(resolveManualParkAccess([away,street,boundary]).parks[0].connections).toHaveLength(0);
    const missing={...locked,properties:{...locked.properties,pedestrian_park_entrance:{version:1,edge:0,position:0.5,streetId:'deleted'}}};
    expect(resolveManualParkAccess([missing,street,boundary]).parks[0].connections).toHaveLength(0);
  });
  it('connects a pocket park to the near-side authored sidewalk and its own complete lawn loop', () => {
    const { zones } = fixture(); const plan = resolveManualParkAccess(zones).parks[0];
    expect(plan.status).toBe('connected');
    expect(plan.connections).toHaveLength(1);
    const connection = plan.connections[0];
    expect(connection.streetBand).toBe('sidewalk');
    expect(xy(connection.streetPoint)[1]).toBeGreaterThan(-3);
    expect(xy(connection.gateway)[1]).toBeCloseTo(0, 4);
    expect(plan.paths).toHaveLength(2);
    expect(plan.paths[0].points[0]).toEqual(plan.paths[0].points[plan.paths[0].points.length - 1]);
    expect(connection.path.slice(1).map(xy).every(([x, y]) => x >= -1e-5 && x <= 40.00001 && y >= -1e-5 && y <= 28.00001)).toBe(true);
  });
  it('is deterministic under input order, does not mutate zones, and invalidates a road move', () => {
    const { zones, park, street, boundary } = fixture(); const before = JSON.stringify(zones);
    const first = resolveManualParkAccess(zones);
    expect(resolveManualParkAccess([...zones].reverse())).toEqual(first);
    const derived = applyManualParkAccessSnapshot(zones, first);
    expect(JSON.stringify(zones)).toBe(before);
    expect(getDerivedParkAccess(derived[0])).not.toBeNull();
    expect(derivedParkAccessGuides(derived[0])).toHaveLength(2);
    const moved = { ...street, coordinates: street.coordinates.map((p) => ll([xy(p)[0], xy(p)[1] - 30])), properties: { ...street.properties, plan_centerline: [[-15, -36], [55, -36]].map(ll) }, updated_at: '2026-09-05' };
    const next = resolveManualParkAccess([park, moved, boundary]);
    expect(next.sourceSignature).not.toBe(first.sourceSignature);
    expect(next.parks[0].connections).toEqual([]);
    expect(getDerivedParkAccess(applyManualParkAccessSnapshot([derived[0], moved, boundary], first)[0])).toBeNull();
  });
  it.each([{ points: [] }, { points: [ll([3, 0])] }])('preserves explicit master-plan access verbatim, including an empty list', ({ points }) => {
    const { park, street } = fixture(); const explicit = { ...park, properties: { ...park.properties, park_access_points: points } };
    const snapshot = resolveManualParkAccess([explicit, street]);
    expect(snapshot.parks[0].status).toBe('explicit');
    expect(applyManualParkAccessSnapshot([explicit, street], snapshot)[0]).toBe(explicit);
  });
  it.each(['building', 'water', 'road'] as const)('does not cross an intervening %s to reach the street', (type) => {
    const { zones } = fixture();
    const barrier = zone('barrier', type, [[-20, -0.9], [60, -0.9], [60, -0.1], [-20, -0.1]]);
    const snapshot = resolveManualParkAccess([...zones, barrier]);
    expect(snapshot.parks[0].connections).toEqual([]);
    expect(snapshot.parks[0].paths).toEqual([]);
  });
  it('does not invent pedestrian access to a vehicle-only laneway or an unannotated building', () => {
    const { park, street, boundary } = fixture();
    const vehicleOnly = { ...street, properties: { ...street.properties, road_archetype_id: 'toronto_laneway', width: 5 } };
    expect(resolveManualParkAccess([park, vehicleOnly, boundary]).parks[0].connections).toEqual([]);
    expect(resolveManualParkAccess([park, zone('clay', 'building', [[10, -4], [20, -4], [20, -1], [10, -1]]), boundary]).parks[0].connections).toEqual([]);
  });
  it('refuses a full-width lawn loop cut by a concave parcel notch', () => {
    const { park, street, boundary } = fixture();
    const concave = { ...park, coordinates: [[0, 0], [40, 0], [40, 28], [28, 28], [28, 9], [12, 9], [12, 28], [0, 28]].map(ll) };
    const snapshot = resolveManualParkAccess([concave, street, boundary]);
    expect(snapshot.parks[0].connections).toEqual([]);
    expect(snapshot.parks[0].paths).toEqual([]);
  });
  it('keeps fixed program geometry unchanged and does not retrofit reference-locked neighborhood v0', () => {
    const { park, street } = fixture();
    const exact = { ...park, properties: { green_space_archetype_id: 'neighborhood_park', green_space_selected_variant_id: 'neighborhood_park_v0' } };
    const profile = resolveParkGroundProfile(exact);
    expect(resolveManualParkAccess([exact, street]).parks).toEqual([]);
    expect(resolveParkGroundProfile(exact)).toEqual(profile);
  });
  it('joins the existing neighborhood path network without rewriting its fixed guides', () => {
    const { street, boundary } = fixture();
    const park = zone('park', 'green_space', [[0, 0], [80, 0], [80, 65], [0, 65]], { green_space_archetype_id: 'neighborhood_park', green_space_selected_variant_id: 'neighborhood_park_v1' });
    const before = resolveParkGroundProfile(park).guides;
    const snapshot = resolveManualParkAccess([park, street, boundary]);
    expect(snapshot.parks[0].status).toBe('connected');
    const derived = applyManualParkAccessSnapshot([park, street, boundary], snapshot)[0];
    expect(resolveParkGroundProfile(derived).guides).toEqual(before);
    expect(snapshot.parks[0].paths).toHaveLength(snapshot.parks[0].connections.length);
  });
  it('connects the opt-in rustic pilot to a sidewalk without changing its composed programme', () => {
    const { street, boundary } = fixture();
    const park = zone('park', 'green_space', [[0, 0], [70, 0], [70, 55], [0, 55]], {
      green_space_archetype_id: 'neighborhood_park', green_space_selected_variant_id: 'neighborhood_park_v0',
      neighborhood_park_layout: 'adaptive_rustic_v1',
    });
    const profile = resolveParkGroundProfile(park);
    const snapshot = resolveManualParkAccess([park, street, boundary]);
    expect(snapshot.parks[0].status).toBe('connected');
    expect(snapshot.parks[0].connections[0].streetBand).toBe('sidewalk');
    const connected = applyManualParkAccessSnapshot([park, street, boundary], snapshot)[0];
    expect(resolveParkGroundProfile(connected).guides).toEqual(profile.guides);
    expect(parkGroundSourceSignature(connected)).not.toBe(parkGroundSourceSignature(park));
    const barrier = zone('barrier', 'building', [[-20, -.9], [90, -.9], [90, -.1], [-20, -.1]]);
    expect(resolveManualParkAccess([park, street, boundary, barrier]).parks[0].connections).toEqual([]);
  });
  it('connects to both safe arms of a T while keeping gateway separation and determinism', () => {
    const { zones } = fixture();
    const line = [[-6, -6], [-6, 45]].map(ll);
    const side = { ...zone('side', 'road', [], { road_archetype_id: 'narrow_residential_street', width: 10, plan_centerline: line }), coordinates: bufferLineToPolygon(line, 10) };
    const plan = resolveManualParkAccess([...zones, side]).parks[0];
    expect(plan.status).toBe('connected');
    expect(plan.connections.map((c) => c.streetZoneId).sort()).toEqual(['side', 'street']);
  });
  it('uses only eligible visible streets as targets while retaining hidden streets in the source inventory', () => {
    const { zones } = fixture();
    const hiddenOnly = resolveManualParkAccess(zones, {}, []);
    expect(hiddenOnly.parks[0].status).toBe('unresolved');
    expect(hiddenOnly.parks[0].paths).toEqual([]);
    expect(hiddenOnly.eligibleStreetZoneIds).toEqual([]);
    expect(hiddenOnly.sources.map((source) => source.zoneId)).toContain('street');
    const line = [[-6, -6], [-6, 45]].map(ll);
    const side = { ...zone('side', 'road', [], { road_archetype_id: 'narrow_residential_street', width: 10, plan_centerline: line }), coordinates: bufferLineToPolygon(line, 10) };
    const inventory = [...zones, side];
    const visibleSide = resolveManualParkAccess(inventory, {}, ['side', 'side', 'unknown']);
    expect(visibleSide.eligibleStreetZoneIds).toEqual(['side']);
    expect(visibleSide.parks[0].connections.map((connection) => connection.streetZoneId)).toEqual(['side']);
    const visibleBottom = resolveManualParkAccess(inventory, {}, ['street']);
    expect(visibleBottom.parks[0].connections.map((connection) => connection.streetZoneId)).toEqual(['street']);
    expect(visibleBottom.sourceSignature).not.toBe(visibleSide.sourceSignature);
    expect(visibleBottom.sources).toEqual(visibleSide.sources);
  });
  it('treats malformed derived metadata as unavailable rather than drawing it', () => {
    const { park } = fixture();
    expect(getDerivedParkAccess({ ...park, properties: { ...park.properties, park_access_connections: { version: 1, sourceSignature: 'old', status: 'connected', paths: [{ points: null }], connections: [null] } } })).toBeNull();
  });
  it('requires a common site boundary and invalidates switching to shared retained-ground geometry', () => {
    const { park, street, boundary, zones } = fixture();
    const snapshot = resolveManualParkAccess(zones);
    expect(snapshot.parks[0].status).toBe('connected');
    const inactive = { ...boundary, is_active_boundary: false };
    const retained = { ...boundary, properties: { ...boundary.properties, community_3d_mask_existing_tiles: false } };
    for (const next of [[park, street], [park, street, inactive]]) {
      const changed = resolveManualParkAccess(next);
      expect(changed.parks[0].status).toBe('unresolved');
      expect(changed.parks[0].paths).toEqual([]);
      expect(changed.sourceSignature).not.toBe(snapshot.sourceSignature);
      expect(getDerivedParkAccess(applyManualParkAccessSnapshot(next, snapshot)[0])).toBeNull();
    }
    const retainedSnapshot = resolveManualParkAccess([park, street, retained]);
    expect(retainedSnapshot.parks[0].status).toBe('connected');
    expect(retainedSnapshot.sourceSignature).not.toBe(snapshot.sourceSignature);
    expect(getDerivedParkAccess(applyManualParkAccessSnapshot([park, street, retained], snapshot)[0])).toBeNull();
    // A street's near edge may appear adjacent while the rest uses external ground.
    const partialBoundary = { ...boundary, coordinates: [[-1, -12], [41, -12], [41, 35], [-1, 35]].map(ll) };
    expect(resolveManualParkAccess([park, street, partialBoundary]).parks[0].connections).toEqual([]);
  });
  it('changes ground cache identity with the derived connection revision while preserving legacy signatures', () => {
    const { zones, park } = fixture();
    const original = parkGroundSourceSignature(park);
    const snapshot = resolveManualParkAccess(zones);
    const connected = applyManualParkAccessSnapshot(zones, snapshot)[0];
    expect(parkGroundSourceSignature(connected)).not.toBe(original);
    expect(parkGroundSourceSignature(park)).toBe(original);
  });
  it('keeps fixed modules while standing trees and benches clear the exact derived paths', () => {
    const { zones, park } = fixture();
    const snapshot = resolveManualParkAccess(zones);
    const connected = applyManualParkAccessSnapshot(zones, snapshot)[0];
    const centroid = park.coordinates.reduce((sum, p) => [sum[0] + p[0] / park.coordinates.length, sum[1] + p[1] / park.coordinates.length], [0, 0]);
    const exclusions = snapshot.parks[0].paths.map((path) => ({ widthM: path.widthM, bufferM: 0.4,
      points: path.points.map(([lng, lat]) => ({ x: (lng - centroid[0]) * metersPerDegLon(centroid[1]), y: (lat - centroid[1]) * METERS_PER_DEG_LAT })) }));
    const recipe = resolveParkRecipeForZone(park), profile = resolveParkGroundProfile(park), anchors = resolveParkProgramAnchorLayout(park);
    const before = computeParkPlacements(park, recipe, profile.plantingStructure, anchors);
    const after = computeParkPlacements(park, recipe, profile.plantingStructure, anchors, exclusions);
    const fixed = (items: typeof before) => items.filter((p) => p.propId === 'playground' || p.propId === 'pavilion');
    expect(fixed(after)).toEqual(fixed(before));
    expect(after.some((p) => p.propId === 'tree')).toBe(true);
    for (const placement of after.filter((p) => p.propId === 'tree' || p.propId === 'bench')) {
      expect(parkPlacementClearsExclusions((placement.lng - centroid[0]) * metersPerDegLon(centroid[1]),
        (placement.lat - centroid[1]) * METERS_PER_DEG_LAT, placement.propId === 'bench' ? 0.9 : 1.05, exclusions)).toBe(true);
    }
    expect(buildParkGroundPrompt(connected, { width: 40, height: 28 }, { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 1 })).toContain('Preserve every path centerline and width exactly');
  });
});
