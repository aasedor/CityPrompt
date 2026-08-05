import { useEffect, useMemo } from 'react';
import * as THREE from 'three';

import { PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS } from './publicRealmDepthPolicy';
import {
  buildCricketGroundLayout,
  resolveCricketGroundAssetProfile,
  type CricketGroundProgramFrame,
  type CricketPavilionStyle,
  type CricketPerimeterStyle,
} from './parkCricketAssets';
import type { ParkGroundGuide } from './parkGroundProfiles';

const CRICKET_RENDER_ORDER = 147;

type CricketZone = {
  properties?: unknown;
};

function CricketWicket({ x }: { x: number }) {
  return (
    <group position={[x, 0, 0.02]}>
      {[-0.114, 0, 0.114].map((y) => (
        <mesh
          key={`stump-${y}`}
          position={[0, y, 0.355]}
          rotation={[Math.PI / 2, 0, 0]}
          renderOrder={CRICKET_RENDER_ORDER + 3}
        >
          <cylinderGeometry args={[0.018, 0.021, 0.71, 8]} />
          <meshStandardMaterial color="#e8e0c6" roughness={0.76} />
        </mesh>
      ))}
      {[-0.057, 0.057].map((y) => (
        <mesh
          key={`bail-${y}`}
          position={[0, y, 0.72]}
          renderOrder={CRICKET_RENDER_ORDER + 4}
        >
          <boxGeometry args={[0.035, 0.13, 0.018]} />
          <meshStandardMaterial color="#eee6ce" roughness={0.72} />
        </mesh>
      ))}
    </group>
  );
}

function SightScreen({ x }: { x: number }) {
  return (
    <group position={[x, 0, 0.02]}>
      {[-2.65, 0, 2.65].map((y) => (
        <mesh
          key={`screen-post-${y}`}
          position={[0, y, 1.85]}
          renderOrder={CRICKET_RENDER_ORDER + 2}
        >
          <boxGeometry args={[0.12, 0.12, 3.7]} />
          <meshStandardMaterial color="#d9ddd7" metalness={0.12} roughness={0.7} />
        </mesh>
      ))}
      {[-2.25, -1.5, -0.75, 0, 0.75, 1.5, 2.25].map((y) => (
        <mesh
          key={`screen-slat-${y}`}
          position={[0, y, 2.25]}
          renderOrder={CRICKET_RENDER_ORDER + 3}
        >
          <boxGeometry args={[0.075, 0.67, 2.8]} />
          <meshStandardMaterial color="#f1f1e9" roughness={0.74} />
        </mesh>
      ))}
    </group>
  );
}

function TudorPavilion({
  width,
  depth,
  primary,
  secondary,
  roof,
}: PavilionProps) {
  const facadeY = -depth / 2 - 0.02;
  return (
    <group>
      <mesh position={[0, 0, 1.35]} renderOrder={CRICKET_RENDER_ORDER}>
        <boxGeometry args={[width, depth, 2.7]} />
        <meshStandardMaterial color={primary} roughness={0.92} />
      </mesh>
      {[-0.42, 0.42].map((side) => (
        <mesh
          key={`thatch-${side}`}
          position={[0, side * depth * 0.28, 3.22]}
          rotation={[side * 0.58, 0, 0]}
          renderOrder={CRICKET_RENDER_ORDER + 1}
        >
          <boxGeometry args={[width + 1.2, depth * 0.63, 0.28]} />
          <meshStandardMaterial color={roof} roughness={1} />
        </mesh>
      ))}
      {[-width * 0.36, -width * 0.12, width * 0.12, width * 0.36].map((x) => (
        <mesh
          key={`tudor-upright-${x}`}
          position={[x, facadeY, 1.35]}
          renderOrder={CRICKET_RENDER_ORDER + 2}
        >
          <boxGeometry args={[0.18, 0.12, 2.7]} />
          <meshStandardMaterial color={secondary} roughness={0.88} />
        </mesh>
      ))}
      {[-1, 1].map((direction) => (
        <mesh
          key={`tudor-diagonal-${direction}`}
          position={[direction * width * 0.24, facadeY - 0.015, 1.42]}
          rotation={[0, direction * 0.58, 0]}
          renderOrder={CRICKET_RENDER_ORDER + 3}
        >
          <boxGeometry args={[0.16, 0.1, 2.65]} />
          <meshStandardMaterial color={secondary} roughness={0.88} />
        </mesh>
      ))}
      <mesh position={[0, facadeY - 0.55, 0.35]} renderOrder={CRICKET_RENDER_ORDER + 2}>
        <boxGeometry args={[width * 0.82, 1.1, 0.18]} />
        <meshStandardMaterial color={secondary} roughness={0.84} />
      </mesh>
    </group>
  );
}

function MunicipalPavilion({
  width,
  depth,
  primary,
  secondary,
  roof,
  accent,
}: PavilionProps) {
  return (
    <group>
      <mesh position={[0, 0, 1.4]} renderOrder={CRICKET_RENDER_ORDER}>
        <boxGeometry args={[width, depth, 2.8]} />
        <meshStandardMaterial color={primary} roughness={0.84} />
      </mesh>
      <mesh position={[0, -depth / 2 - 0.035, 1.55]} renderOrder={CRICKET_RENDER_ORDER + 2}>
        <boxGeometry args={[width * 0.72, 0.12, 1.65]} />
        <meshPhysicalMaterial
          color={secondary}
          transparent
          opacity={0.55}
          roughness={0.18}
          metalness={0.08}
        />
      </mesh>
      <mesh position={[0, -depth / 2 - 0.75, 2.75]} renderOrder={CRICKET_RENDER_ORDER + 2}>
        <boxGeometry args={[width + 1.3, 1.55, 0.18]} />
        <meshStandardMaterial color={roof} metalness={0.28} roughness={0.58} />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh
          key={`municipal-score-${side}`}
          position={[side * (width / 2 + 0.75), 0, 2.25]}
          renderOrder={CRICKET_RENDER_ORDER + 2}
        >
          <boxGeometry args={[1.15, 0.22, 2.1]} />
          <meshStandardMaterial color="#273033" roughness={0.66} />
        </mesh>
      ))}
      <mesh position={[0, 0, 2.88]} renderOrder={CRICKET_RENDER_ORDER + 1}>
        <boxGeometry args={[width + 0.5, depth + 0.45, 0.22]} />
        <meshStandardMaterial color={accent} roughness={0.7} />
      </mesh>
    </group>
  );
}

function MaidanPavilion({
  width,
  depth,
  primary,
  secondary,
  roof,
  accent,
}: PavilionProps) {
  return (
    <group>
      <mesh position={[0, 0, 1.25]} renderOrder={CRICKET_RENDER_ORDER}>
        <boxGeometry args={[width, depth, 2.5]} />
        <meshStandardMaterial color={primary} roughness={0.94} />
      </mesh>
      {[-width * 0.3, 0, width * 0.3].map((x) => (
        <mesh
          key={`maidan-opening-${x}`}
          position={[x, -depth / 2 - 0.04, 1.18]}
          renderOrder={CRICKET_RENDER_ORDER + 2}
        >
          <boxGeometry args={[width * 0.2, 0.13, 1.55]} />
          <meshStandardMaterial color="#343737" roughness={0.82} />
        </mesh>
      ))}
      <mesh position={[0, -depth / 2 - 0.92, 2.45]} rotation={[0.08, 0, 0]} renderOrder={CRICKET_RENDER_ORDER + 2}>
        <boxGeometry args={[width + 1.2, 1.85, 0.15]} />
        <meshStandardMaterial color={roof} metalness={0.26} roughness={0.68} />
      </mesh>
      {[-width * 0.42, width * 0.42].map((x, index) => (
        <group key={`vendor-${x}`} position={[x, -depth / 2 - 1.3, 0]}>
          <mesh position={[0, 0, 0.58]} renderOrder={CRICKET_RENDER_ORDER + 2}>
            <boxGeometry args={[2.1, 1.1, 1.16]} />
            <meshStandardMaterial color={secondary} roughness={0.9} />
          </mesh>
          <mesh position={[0, -0.18, 1.3]} renderOrder={CRICKET_RENDER_ORDER + 3}>
            <boxGeometry args={[2.35, 1.45, 0.12]} />
            <meshStandardMaterial color={index === 0 ? accent : '#5d9a67'} roughness={0.82} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function CaribbeanPavilion({
  width,
  depth,
  primary,
  secondary,
  roof,
  accent,
}: PavilionProps) {
  return (
    <group>
      {[0, 1, 2].map((row) => (
        <mesh
          key={`caribbean-stand-${row}`}
          position={[0, -depth * 0.24 + row * 0.62, 0.28 + row * 0.34]}
          renderOrder={CRICKET_RENDER_ORDER + 1}
        >
          <boxGeometry args={[width * 0.88, 0.72, 0.22]} />
          <meshStandardMaterial
            color={row === 0 ? primary : row === 1 ? secondary : accent}
            roughness={0.86}
          />
        </mesh>
      ))}
      {[-width * 0.43, width * 0.43].flatMap((x) => [-depth * 0.35, depth * 0.35].map((y) => (
        <mesh
          key={`caribbean-post-${x}-${y}`}
          position={[x, y, 1.75]}
          renderOrder={CRICKET_RENDER_ORDER + 1}
        >
          <boxGeometry args={[0.18, 0.18, 3.5]} />
          <meshStandardMaterial color="#60452f" roughness={0.88} />
        </mesh>
      )))}
      <mesh position={[0, 0, 3.55]} rotation={[0.08, 0, 0]} renderOrder={CRICKET_RENDER_ORDER + 2}>
        <boxGeometry args={[width + 1.3, depth + 1.1, 0.22]} />
        <meshStandardMaterial color={roof} roughness={0.78} />
      </mesh>
    </group>
  );
}

interface PavilionProps {
  width: number;
  depth: number;
  primary: string;
  secondary: string;
  roof: string;
  accent: string;
}

function CricketPavilion({
  style,
  ...props
}: PavilionProps & { style: CricketPavilionStyle }) {
  if (style === 'municipal_clubhouse') return <MunicipalPavilion {...props} />;
  if (style === 'maidan_pavilion') return <MaidanPavilion {...props} />;
  if (style === 'caribbean_grandstand') return <CaribbeanPavilion {...props} />;
  return <TudorPavilion {...props} />;
}

function CricketPerimeter({
  style,
  radiusX,
  radiusY,
  color,
}: {
  style: CricketPerimeterStyle;
  radiusX: number;
  radiusY: number;
  color: string;
}) {
  const count = style === 'white_picket' ? 48 : 28;
  const height = style === 'low_concrete_wall' ? 0.62 : style === 'chainlink' ? 1.45 : 0.92;
  const offset = style === 'low_concrete_wall' ? 1.2 : 0.8;
  return (
    <group>
      {Array.from({ length: count }, (_, index) => {
        const angle = (index / count) * Math.PI * 2;
        const x = Math.cos(angle) * (radiusX + offset);
        const y = Math.sin(angle) * (radiusY + offset);
        if (style === 'chainlink' && index % 2 === 1) return null;
        return (
          <mesh
            key={`cricket-perimeter-${index}`}
            position={[x, y, height / 2]}
            rotation={[0, 0, angle]}
            renderOrder={CRICKET_RENDER_ORDER + 1}
          >
            <boxGeometry args={[
              style === 'low_concrete_wall' ? Math.max(1.6, Math.PI * radiusX / count) : 0.085,
              style === 'low_concrete_wall' ? 0.32 : 0.085,
              height,
            ]} />
            <meshStandardMaterial
              color={style === 'chainlink' ? '#647170' : color}
              metalness={style === 'chainlink' ? 0.38 : 0.02}
              roughness={style === 'low_concrete_wall' ? 0.92 : 0.76}
            />
          </mesh>
        );
      })}
    </group>
  );
}

export function GlobeCricketGroundAssembly({
  zone,
  guide,
  frame,
  terrainZ,
}: {
  zone: CricketZone;
  guide: ParkGroundGuide;
  frame: CricketGroundProgramFrame;
  terrainZ: (x: number, y: number) => number;
}) {
  const profile = resolveCricketGroundAssetProfile(zone);
  const layout = useMemo(
    () => buildCricketGroundLayout(guide, frame),
    [frame, guide],
  );
  const ropeGeometry = useMemo(() => {
    const points = Array.from({ length: 96 }, (_, index) => {
      const angle = (index / 96) * Math.PI * 2;
      return new THREE.Vector3(
        Math.cos(angle) * layout.radiusX,
        Math.sin(angle) * layout.radiusY,
        0.08,
      );
    });
    return new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3(points, true, 'catmullrom', 0.22),
      192,
      0.045,
      6,
      true,
    );
  }, [layout.radiusX, layout.radiusY]);
  useEffect(() => () => ropeGeometry.dispose(), [ropeGeometry]);

  if (!profile) return null;
  const fieldZ = terrainZ(layout.center.x, layout.center.y)
    + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const pavilionZ = terrainZ(layout.pavilion.x, layout.pavilion.y)
    + PUBLIC_REALM_PROGRAM_BASE_LIFT_METERS;
  const pavilionRotation = layout.rotationRad
    + (layout.pavilion.facingSign < 0 ? Math.PI : 0);

  return (
    <group renderOrder={CRICKET_RENDER_ORDER}>
      <group
        position={[layout.center.x, layout.center.y, fieldZ]}
        rotation={[0, 0, layout.rotationRad]}
      >
        <mesh
          scale={[layout.radiusX, layout.radiusY, 1]}
          renderOrder={CRICKET_RENDER_ORDER}
        >
          <circleGeometry args={[1, 96]} />
          <meshStandardMaterial
            color={profile.outfieldColor}
            transparent
            // Preserve the AI orthophoto's detail while guaranteeing that a
            // delayed/missing texture never turns the playable oval into the
            // site's white flattening mask.
            opacity={0.56}
            roughness={0.98}
            depthWrite={false}
          />
        </mesh>
        <mesh geometry={ropeGeometry} renderOrder={CRICKET_RENDER_ORDER + 3}>
          <meshStandardMaterial color="#f5f2df" roughness={0.68} />
        </mesh>
        <mesh position={[0, 0, 0.055]} renderOrder={CRICKET_RENDER_ORDER + 2}>
          <boxGeometry args={[layout.pitchLengthM, layout.pitchWidthM, 0.07]} />
          <meshStandardMaterial color={profile.pitchColor} roughness={0.94} />
        </mesh>
        {[-layout.wicketOffsetM, layout.wicketOffsetM].flatMap((x) => (
          [0, x < 0 ? 1.22 : -1.22].map((offset, index) => (
            <mesh
              key={`crease-${x}-${index}`}
              position={[x + offset, 0, 0.102]}
              renderOrder={CRICKET_RENDER_ORDER + 4}
            >
              <boxGeometry args={[0.045, layout.pitchWidthM + 0.55, 0.018]} />
              <meshStandardMaterial color="#f1ecda" roughness={0.72} />
            </mesh>
          ))
        ))}
        <CricketWicket x={-layout.wicketOffsetM} />
        <CricketWicket x={layout.wicketOffsetM} />
        <SightScreen x={-layout.sightScreenOffsetM} />
        <SightScreen x={layout.sightScreenOffsetM} />
        <CricketPerimeter
          style={profile.perimeterStyle}
          radiusX={layout.radiusX}
          radiusY={layout.radiusY}
          color={profile.accentColor}
        />
      </group>
      <group
        position={[layout.pavilion.x, layout.pavilion.y, pavilionZ]}
        rotation={[0, 0, pavilionRotation]}
        renderOrder={CRICKET_RENDER_ORDER + 1}
      >
        <CricketPavilion
          style={profile.pavilionStyle}
          width={layout.pavilion.widthM}
          depth={layout.pavilion.depthM}
          primary={profile.structurePrimary}
          secondary={profile.structureSecondary}
          roof={profile.roofColor}
          accent={profile.accentColor}
        />
      </group>
    </group>
  );
}
