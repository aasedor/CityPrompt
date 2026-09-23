import { useMemo } from 'react';
import { createRoot } from 'react-dom/client';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { nativeStreetPilot, placeNativeStreetModules } from '../components/viewer/globe/nativeStreetPilot';
import { GlobeNativeStreetPilotModules } from '../components/viewer/globe/GlobeNativeStreetPilotModules';
import { resolvePilotStreetSectionProfile } from '../components/viewer/globe/streetSectionProfiles';
import { buildRibbonBandGeometry } from '../components/viewer/globe/streetMesh3D';

const main = nativeStreetPilot('student_main_street_v1')!;
const market = nativeStreetPilot('student_market_street_v1')!;
const mainRoute = [{ x: -38, y: -48 }, { x: -38, y: 48 }];
const marketRoute = [{ x: 29, y: -48 }, { x: 29, y: 0 }, { x: 66, y: 0 }];

function Street({ pilot, route }: { pilot: typeof main; route: typeof mainRoute }) {
  const profile = resolvePilotStreetSectionProfile({ properties: {
    road_archetype_id: pilot.sourceArchetypeId, road_selected_variant_id: `${pilot.sourceArchetypeId}_v0`,
    native_street_pilot_id: pilot.id, width: pilot.widthM,
  } })!;
  const bands = useMemo(() => profile.bands.map(band => ({
    band, geometry: buildRibbonBandGeometry(route, band.startM, band.endM, band.liftM),
  })), [profile.bands, route]);
  const poses = useMemo(() => placeNativeStreetModules(pilot, route), [pilot, route]);
  return <group>
    {bands.map(({ band, geometry }) => geometry && <mesh key={band.label} geometry={geometry} receiveShadow>
      <meshStandardMaterial color={band.color} roughness={0.9} side={THREE.DoubleSide} />
    </mesh>)}
    <GlobeNativeStreetPilotModules poses={poses} />
  </group>;
}

const root = createRoot(document.getElementById('root')!);
if (import.meta.hot) import.meta.hot.dispose(() => root.unmount());
root.render(<>
  <div style={{ position: 'absolute', zIndex: 2, top: 14, left: 18, padding: 12,
    background: 'rgba(255,255,255,.9)', borderRadius: 8, fontFamily: 'Arial' }}>
    <b>Route-based native street pilot</b><br />Main street: 23 m × 96 m, two module cycles<br />
    Pedestrian market street: 18 m, with a 90° bend<br />Drag to orbit; wheel to zoom.
  </div>
  <Canvas shadows orthographic camera={{ position: [105, -120, 115], zoom: 5.2, near: 0.1, far: 500 }}>
    <ambientLight intensity={1.3} />
    <directionalLight position={[-25, 35, 90]} intensity={2} castShadow shadow-mapSize={[2048, 2048]} />
    <Street pilot={main} route={mainRoute} />
    <Street pilot={market} route={marketRoute} />
    <OrbitControls target={[0, 0, 0]} makeDefault />
  </Canvas>
</>);
