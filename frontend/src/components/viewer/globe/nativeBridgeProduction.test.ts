import { afterAll, expect, it, vi } from 'vitest';
import * as THREE from 'three';

vi.stubEnv('DEV', false);
vi.stubEnv('MODE', 'production');
const { nativeStreetSources } = await import('./nativeStreetSources');
const { modularBridgeProgramFor, modularBridgeWalkingHeight } = await import('./modularBridgeProgram');
const { nativeStreetPilot, nativeStreetLocalRouteProblem, placeNativeStreetModules } = await import('./nativeStreetPilot');
const { buildNativeStreetProgram } = await import('./nativeStreetProgram');
const { instanceStreetModule } = await import('./nativeStreetInstances');
const { MODULAR_BRIDGE_ASSETS, CATALOGUE_ASSETS, hasDrawnBridgeReplacement } = await import('@/features/pickPlace/assetRegistry');
const { publicRealmReleaseRow } = await import('@/features/pickPlace/publicRealmRelease');
const { CANONICAL_CHOICES } = await import('@/features/pickPlace/canonicalCatalogue');
const { appendStreetDrawingValue, finishDoubleClickValues } = await import('@/features/pickPlace/streetDrawingGeometry');
afterAll(() => vi.unstubAllEnvs());
const id = 'timber_covered_bridge_route_v1';

it('replaces only the exact reviewed fixed timber card and keeps its historical metadata readable', () => {
  const fixed = publicRealmReleaseRow('claude_public_realm:timber-covered-footbridge:0dbeb2731dbe');
  expect(fixed).toBeDefined();
  if (!fixed) throw new Error('The historical fixed timber identity is missing');
  expect(hasDrawnBridgeReplacement(fixed.asset)).toBe(true);
  expect(hasDrawnBridgeReplacement({...fixed.asset,id:'an-unrelated-saved-bridge'})).toBe(false);
  expect(hasDrawnBridgeReplacement({...fixed.asset,model:{...fixed.asset.model,variantId:'urban_pedestrian_footbridge_v0'}})).toBe(false);
  expect(CANONICAL_CHOICES.some(choice=>choice.placements.some(asset=>asset.id===fixed.asset.id))).toBe(false);
  expect(publicRealmReleaseRow(fixed.asset.id)?.runtime_sha256).toBe('0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad');
});

it('offers only the reviewed timber route in production while retaining old fixed saved identities', () => {
  expect(MODULAR_BRIDGE_ASSETS.map(asset => asset.id)).toEqual([id]);
  expect(nativeStreetSources.filter(row => row.id.endsWith('_route_v1')).map(row => row.id)).toEqual([id]);
  expect(CANONICAL_CHOICES.some(choice => choice.placements.some(asset => asset.id === id))).toBe(true);
  expect(CATALOGUE_ASSETS.some(asset => asset.id.startsWith('claude_public_realm:steel-truss-road-bridge:'))).toBe(true);
  expect(modularBridgeProgramFor('planted_green_bridge_route_v1')).toBeUndefined();
});

it('builds a bounded bridge-only production route with fixed stairs and repeated bays', () => {
  const pilot = nativeStreetPilot(id);
  expect(pilot).toBeDefined();
  if (!pilot?.program) throw new Error('Production timber route is missing');
  const route = [{ x: 0, y: 0 }, { x: 48, y: 64 }];
  expect(nativeStreetLocalRouteProblem(pilot, route)).toBeNull();
  expect(nativeStreetLocalRouteProblem(pilot, [{x:0,y:0},{x:0,y:241}])).toBeTruthy();
  const poses = placeNativeStreetModules(pilot, route);
  expect(poses[0].kind).toBe('bridge_left_stair');
  expect(poses[poses.length - 1].kind).toBe('bridge_right_stair');
  expect(poses.filter(pose => pose.kind === 'bridge_bay').length).toBeGreaterThan(10);
  expect(buildNativeStreetProgram(pilot.program, 6, pilot.fixtureLengthM, route)).toEqual([]);
  const source = new THREE.Group();
  source.add(new THREE.Mesh(new THREE.BoxGeometry(6, 8, 4), new THREE.MeshStandardMaterial()));
  const size = new THREE.Box3().setFromObject(instanceStreetModule(source, [{...poses[0],x:0,y:0,yaw:0,longitudinalScale:1.25}])).getSize(new THREE.Vector3());
  expect(size.x).toBeCloseTo(6); expect(size.y).toBeCloseTo(5); expect(size.z).toBeCloseTo(8);
});

it('retains exactly two endpoints through production extra-click and double-click completion', () => {
  const properties = {road_selected_variant_id:id};
  const points = [[1,2],[3,4]];
  expect(appendStreetDrawingValue(points,[5,6],properties)).toEqual([[1,2],[5,6]]);
  expect(finishDoubleClickValues(points,properties)).toEqual(points);
  expect(finishDoubleClickValues(points,{road_selected_variant_id:'calgary_local_v0'})).toEqual([[1,2]]);
});

it('walks the production stairs and deck without turning the space beneath into paving', () => {
  const program = modularBridgeProgramFor(id);
  expect(program).toBeDefined();
  if (!program) throw new Error('Production timber walking programme is missing');
  expect(modularBridgeWalkingHeight(program,0,.01,80)).toBeCloseTo(3.45/18);
  expect(modularBridgeWalkingHeight(program,0,40,80)).toBeCloseTo(3.45);
  expect(modularBridgeWalkingHeight(program,2.1,40,80)).toBeNull();
});

it('rejects a held topology deformation instead of silently mounting an undeformed production bridge', () => {
  const source = new THREE.Group();
  source.add(new THREE.Mesh(new THREE.BoxGeometry(6,8,60),new THREE.MeshStandardMaterial()));
  expect(() => instanceStreetModule(source,[{
    kind:'bridge_topology',url:'/street-kits/pilots/swooping_cycle_flyover_route_v1/bridge_topology.glb',
    sha256:'b'.repeat(64),x:0,y:0,z:0,yaw:0,scale:1,stationM:0,surfaceLiftM:0,
    bridgeDeformation:{mode:'longitudinal-core-v1',nativeLengthM:60,requestedLengthM:80,rigidEndM:10},
  }])).toThrow(/released bridge deformation/i);
});
