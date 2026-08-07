import { useEffect, useMemo } from 'react';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import { batch20ParkSkinForSelection } from './parkBatch20Skins';
import { batch21ParkSkinForSelection } from './parkBatch21Skins';
import { batch22ParkSkinForSelection } from './parkBatch22Skins';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { resolveParkGuideDimensionsM, type ParkGroundGuide } from './parkGroundProfiles';
import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';

interface ProgramFrame {
  minX: number; maxX: number; minY: number; maxY: number; width: number; height: number;
}
interface Point { x: number; y: number }
interface Maps { map: THREE.Texture; normalMap: THREE.Texture; roughnessMap: THREE.Texture; aoMap: THREE.Texture }

function useMaps(slug: string, role: string, repeat = 4): Maps {
  const root = `/park-skins/${slug}/adaptive-v1/${role}`;
  const source = useTexture({
    map: `${root}/albedo.jpg`, normalMap: `${root}/normal.png`,
    roughnessMap: `${root}/roughness.jpg`, aoMap: `${root}/ao.jpg`,
  });
  const maps = useMemo(() => Object.fromEntries(Object.entries(source).map(([key, value]) => {
    const texture = value.clone();
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat, repeat);
    texture.needsUpdate = true;
    return [key, texture];
  })) as unknown as Maps, [repeat, source]);
  maps.map.colorSpace = THREE.SRGBColorSpace;
  useEffect(() => () => Object.values(maps).forEach((texture) => texture.dispose()), [maps]);
  return maps;
}

const center = (guide: ParkGroundGuide, frame: ProgramFrame): Point => ({
  x: frame.minX + frame.width * guide.x,
  y: frame.maxY - frame.height * guide.y,
});

function route(guide: ParkGroundGuide, frame: ProgramFrame): Point[] {
  if (guide.points && guide.points.length > 1) {
    return guide.points.map(([x, y]) => ({ x: frame.minX + frame.width * x, y: frame.maxY - frame.height * y }));
  }
  const c = center(guide, frame);
  const length = guide.widthM ?? guide.width * frame.width;
  const angle = ((guide.rotationDeg ?? 0) * Math.PI) / 180;
  return [
    { x: c.x - Math.cos(angle) * length / 2, y: c.y - Math.sin(angle) * length / 2 },
    { x: c.x + Math.cos(angle) * length / 2, y: c.y + Math.sin(angle) * length / 2 },
  ];
}

function Segment({ a, b, width, z, maps }: { a: Point; b: Point; width: number; z: number; maps: Maps }) {
  const length = Math.max(0.1, Math.hypot(b.x - a.x, b.y - a.y));
  return <mesh position={[(a.x + b.x) / 2, (a.y + b.y) / 2, z + 0.045]} rotation={[0, 0, Math.atan2(b.y - a.y, b.x - a.x)]} renderOrder={145}>
    <boxGeometry args={[length, width, 0.09]} />
    <meshStandardMaterial {...maps} color="#ffffff" roughness={0.9} />
  </mesh>;
}

/** Reference-textured program surfaces for older core families whose original
 * depth kits supplied objects but not an archetype-owned material layer. */
interface CoreSurfaceProps {
  archetypeId: string;
  variantId: string;
  guides: ParkGroundGuide[];
  frame: ProgramFrame;
  terrainZ: (x: number, y: number) => number;
}

export function GlobeParkBatch20CoreSurfaces(props: CoreSurfaceProps) {
  const skin = batch23ParkSkinForSelection(props.archetypeId, props.variantId)
    ?? batch22ParkSkinForSelection(props.archetypeId, props.variantId)
    ?? batch21ParkSkinForSelection(props.archetypeId, props.variantId)
    ?? batch20ParkSkinForSelection(props.archetypeId, props.variantId);
  return skin ? <Batch20CoreSurfacesImpl {...props} slug={skin.slug} /> : null;
}

function Batch20CoreSurfacesImpl({ archetypeId, guides, frame, terrainZ, slug }: CoreSurfaceProps & { slug: string }) {
  const paver = useMaps(slug, 'paver');
  const lawn = useMaps(slug, 'lawn', 5);
  const planting = useMaps(slug, 'planting', 5);
  const safety = useMaps(slug, 'safety');
  const timber = useMaps(slug, 'timber');
  const lift = PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const isEcology = archetypeId === 'riparian_buffer' || archetypeId === 'wetland_rain_garden';
  const isPlay = archetypeId === 'playground_adventure';
  return <group>
    {guides.flatMap((guide, index) => {
      if (guide.kind === 'line' || guide.kind === 'polyline' || guide.kind === 'axis') {
        const points = route(guide, frame);
        const maps = isEcology ? timber : paver;
        return points.slice(0, -1).map((point, segmentIndex) => (
          <Segment
            key={`${index}-${segmentIndex}`}
            a={point}
            b={points[segmentIndex + 1]}
            width={guide.strokeWidthM ?? (isEcology ? 2.4 : 2.0)}
            z={Math.max(terrainZ(point.x, point.y), terrainZ(points[segmentIndex + 1].x, points[segmentIndex + 1].y)) + lift}
            maps={maps}
          />
        ));
      }
      if (!['rectangle', 'rounded_rectangle', 'ellipse'].includes(guide.kind)) return [];
      const c = center(guide, frame);
      const size = resolveParkGuideDimensionsM(guide, frame);
      const green = ['#4', '#5', '#6', '#7'].includes(guide.color.slice(0, 2));
      const maps = isPlay && guide.kind === 'rounded_rectangle'
        ? safety
        : isEcology
          ? (guide.kind === 'ellipse' ? planting : lawn)
          : green ? lawn : paver;
      const z = terrainZ(c.x, c.y) + lift + 0.045;
      return [<mesh
        key={index}
        position={[c.x, c.y, z]}
        rotation={guide.kind === 'ellipse'
          ? [Math.PI / 2, 0, ((guide.rotationDeg ?? 0) * Math.PI) / 180]
          : [0, 0, -((guide.rotationDeg ?? 0) * Math.PI) / 180]}
        scale={guide.kind === 'ellipse' ? [size.width / 2, size.height / 2, 1] : [1, 1, 1]}
        renderOrder={145}
      >
        {guide.kind === 'ellipse'
          ? <cylinderGeometry args={[1, 1, 0.09, 48]} />
          : <boxGeometry args={[size.width, size.height, 0.09]} />}
        <meshStandardMaterial {...maps} color="#ffffff" roughness={0.92} />
      </mesh>];
    })}
  </group>;
}
