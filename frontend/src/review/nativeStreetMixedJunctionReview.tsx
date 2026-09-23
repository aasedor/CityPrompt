import { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import type { SiteZone } from '../types';
import { bufferLineToPolygon } from '../utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../components/viewer/mapEngine/geoUtils';
import { nativeStreetPilot, placeNativeStreetModules } from '../components/viewer/globe/nativeStreetPilot';
import { GlobeNativeStreetPilotModules } from '../components/viewer/globe/GlobeNativeStreetPilotModules';
import { detectConnectedStreetIntersections } from '../components/viewer/globe/streetGraphIntersections';
import { buildSectionJunctionGeometry, clipStreetGeometryOutsideJunction, resolveStreetJunctionLayout,
  type StreetJunctionLayout } from '../components/viewer/globe/streetJunctionGeometry';
import { resolvePilotStreetSectionProfile } from '../components/viewer/globe/streetSectionProfiles';
import { buildRibbonBandGeometry } from '../components/viewer/globe/streetMesh3D';

const latitude = 51;
const longitude = -114.095;
const main = nativeStreetPilot('student_main_street_v1')!;
const market = nativeStreetPilot('student_market_street_v1')!;
const mainRoute = [{ x: -48, y: 0 }, { x: 48, y: 0 }];
const marketXRoute = [{ x: 0, y: -48 }, { x: 0, y: 48 }];
const marketTRoute = [{ x: 0, y: 0 }, { x: 0, y: 48 }];

function zone(id: string, pilot: typeof main, route: typeof mainRoute): SiteZone {
  const line = route.map((point) => [longitude + point.x / metersPerDegLon(latitude),
    latitude + point.y / METERS_PER_DEG_LAT]);
  return {
    id, project_id: 'review', zone_type: 'road', coordinates: bufferLineToPolygon(line, pilot.widthM),
    color: '#777', sort_order: 0, created_at: '2026-09-23T00:00:00Z', updated_at: '2026-09-23T00:00:00Z',
    properties: { width: pilot.widthM, lane_count: pilot.id === market.id ? 0 : 2,
      road_archetype_id: pilot.sourceArchetypeId, road_selected_variant_id: `${pilot.sourceArchetypeId}_v0`,
      native_street_pilot_id: pilot.id, plan_centerline: line },
  } as SiteZone;
}

function ReviewStreet({ pilot, route, layout }: {
  pilot: typeof main; route: typeof mainRoute; layout: StreetJunctionLayout;
}) {
  const profile = resolvePilotStreetSectionProfile({ properties: {
    road_archetype_id: pilot.sourceArchetypeId, road_selected_variant_id: `${pilot.sourceArchetypeId}_v0`,
    native_street_pilot_id: pilot.id, width: pilot.widthM,
  } })!;
  const bands = useMemo(() => profile.bands.map((band) => {
    const source = buildRibbonBandGeometry(route, band.startM, band.endM, band.liftM);
    if (!source) return null;
    const geometry = clipStreetGeometryOutsideJunction(source, layout);
    source.dispose();
    return { band, geometry };
  }).filter((item): item is NonNullable<typeof item> => item !== null), [profile.bands, route, layout]);
  const poses = useMemo(() => placeNativeStreetModules(pilot, route, [{ x: 0, y: 0, clearanceM: 16 }]), [pilot, route]);
  return <group>
    {bands.map(({ band, geometry }) => <mesh key={band.label} geometry={geometry} receiveShadow>
      <meshStandardMaterial color={pilot.id === market.id ? '#b8b5ac' : band.color} roughness={0.9} side={THREE.DoubleSide} />
    </mesh>)}
    <GlobeNativeStreetPilotModules poses={poses} />
  </group>;
}

function MixedJunction({ kind }: { kind: 'T' | 'X' }) {
  const marketRoute = kind === 'T' ? marketTRoute : marketXRoute;
  const layout = useMemo(() => {
    const zones = [zone('main', main, mainRoute), zone('market', market, marketRoute)];
    const node = detectConnectedStreetIntersections(zones)[0];
    return node && resolveStreetJunctionLayout(node, zones);
  }, [marketRoute]);
  const geometry = useMemo(() => layout && buildSectionJunctionGeometry(layout), [layout]);
  if (!layout || !geometry) return null;
  return <group>
    <ReviewStreet pilot={main} route={mainRoute} layout={layout} />
    <ReviewStreet pilot={market} route={marketRoute} layout={layout} />
    <mesh geometry={geometry.pavement}><meshStandardMaterial color="#555a5d" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.sidewalks}><meshStandardMaterial color="#b8b5ac" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.promenadePaving}><meshStandardMaterial color="#b8b5ac" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.curbs}><meshStandardMaterial color="#aaa9a3" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.crosswalks}><meshStandardMaterial color="#f1eee5" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.curbRamps}><meshStandardMaterial color="#b8b5ac" side={THREE.DoubleSide} /></mesh>
    <mesh geometry={geometry.tactilePads}><meshStandardMaterial color="#d0a83d" side={THREE.DoubleSide} /></mesh>
  </group>;
}

function App() {
  const [kind, setKind] = useState<'T' | 'X'>('T');
  return <>
    <div style={{ position: 'absolute', zIndex: 2, top: 14, left: 18, padding: 12,
      background: 'rgba(255,255,255,.93)', borderRadius: 8, fontFamily: 'Arial' }}>
      <b>Mixed native street junction</b><br />23 m vehicle main street × 18 m pedestrian market street<br />
      <button onClick={() => setKind('T')} disabled={kind === 'T'}>T junction</button>{' '}
      <button onClick={() => setKind('X')} disabled={kind === 'X'}>X junction</button><br />Drag to orbit; wheel to zoom.
    </div>
    <Canvas key={kind} shadows orthographic camera={{ position: [75, -85, 100], zoom: 7.3, near: 0.1, far: 400 }}>
      <ambientLight intensity={1.3} />
      <directionalLight position={[-25, 35, 90]} intensity={2} castShadow />
      <MixedJunction kind={kind} />
      <OrbitControls target={[0, 0, 0]} makeDefault />
    </Canvas>
  </>;
}

const root = createRoot(document.getElementById('root')!);
if (import.meta.hot) import.meta.hot.dispose(() => root.unmount());
root.render(<App />);
