import { useEffect, useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import type { SiteZone } from "@/types";
import { Surface, Woodland } from "./GlobeNeighborhoodParkPilot";
import {
  PARK_TRIO_REVISION,
  parkTrioLayout,
  type TrioModule,
} from "./parkTrioLayout";
import { getDerivedParkAccess } from "./parkAccessConnections";
import { METERS_PER_DEG_LAT, metersPerDegLon } from "../mapEngine/geoUtils";
import type { SharedGroundTriangulation } from "./sharedGroundGeometry";
import { distanceToSegment } from "./neighborhoodParkLayout";

type Ground = (x: number, y: number) => number;
function FixedModule({
  module,
  ground,
}: {
  module: TrioModule;
  ground: Ground;
}) {
  const url =
    module.asset === "shared/bench"
      ? "/landscape-pilots/neighborhood-rustic-v5/timber-bench.glb"
      : module.asset.startsWith("sports/")
        ? `/landscape-pilots/sports-parks-v1/${module.asset.split("/")[1]}/court.glb`
        : `/landscape-pilots/${PARK_TRIO_REVISION}/${module.asset}.glb`;
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const c = scene.clone(true);
    c.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
        if (module.asset.startsWith("sports/")) {
          // Near-coplanar paint must be drawn after the pad and playing surface.
          // Keep normal depth testing: buildings and equipment still occlude it.
          o.renderOrder = o.name === "white" ? 154 : o.name === "red" ? 153
            : o.name === "blue" || o.name === "stripe" ? 152 : 151;
        }
      }
    });
    return c;
  }, [scene, module.asset]);
  const datum = useMemo(() => {
    const elevations: number[] = [];
    for (let i = 0; i <= 4; i++)
      for (let j = 0; j <= 4; j++) {
        const x = -module.width / 2 + (module.width * i) / 4,
          y = -module.depth / 2 + (module.depth * j) / 4;
        elevations.push(
          ground(
            module.center.x +
              x * Math.cos(module.yaw) -
              y * Math.sin(module.yaw),
            module.center.y +
              x * Math.sin(module.yaw) +
              y * Math.cos(module.yaw),
          ),
        );
      }
    return {
      high: Math.max(...elevations) + 0.1,
      low: Math.min(...elevations),
    };
  }, [module, ground]);
  const pad = useMemo(() => {
    const ring = module.envelope,
      shape = new THREE.Shape(ring.map((p) => new THREE.Vector2(p.x, p.y)));
    const indexed = new THREE.ShapeGeometry(shape);
    const top = indexed.toNonIndexed();
    indexed.dispose();
    // Sports modules already include their own continuous slab. A second cap
    // just centimetres below it competes for depth at globe camera distances.
    // Retain the terrain skirt, but let the delivered court own its top surface.
    const coordinates: number[] = module.asset.startsWith("sports/")
      ? [] : Array.from(top.getAttribute("position").array);
    for (let i = 2; i < coordinates.length; i += 3) coordinates[i] = datum.high;
    top.dispose();
    ring.forEach((a, i) => {
      const b = ring[(i + 1) % ring.length],
        az = ground(a.x, a.y) + 0.07,
        bz = ground(b.x, b.y) + 0.07,
        z = datum.high;
      coordinates.push(
        a.x,
        a.y,
        az,
        b.x,
        b.y,
        bz,
        b.x,
        b.y,
        z,
        a.x,
        a.y,
        az,
        b.x,
        b.y,
        z,
        a.x,
        a.y,
        z,
      );
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(coordinates, 3),
    );
    g.computeVertexNormals();
    return g;
  }, [module, ground, datum]);
  useEffect(() => () => pad.dispose(), [pad]);
  return (
    <group
      name={`park-trio-${module.id}`}
      userData={{
        semanticRole: module.asset,
        fixedMetricObject: true,
        nonuniformScalingAllowed: false,
        gradingDepthM: datum.high - datum.low,
        gradingReviewRequired: datum.high - datum.low > 0.8,
      }}
    >
      <mesh geometry={pad} receiveShadow>
        <meshStandardMaterial
          color={module.asset.includes("bed") ? "#83705a" : "#b3ac97"}
          roughness={0.96}
        />
      </mesh>
      <group
        position={[module.center.x, module.center.y, datum.high]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <group rotation={[0, module.yaw, 0]}>
          <primitive object={clone} />
        </group>
      </group>
    </group>
  );
}

export function GlobeParkTrioPilot({
  zone,
  centroid,
  terrainZ,
  groundGrid,
}: {
  zone: SiteZone;
  centroid: { lng: number; lat: number };
  terrainZ: Ground;
  groundGrid?: SharedGroundTriangulation | null;
}) {
  const layout = useMemo(
    () => parkTrioLayout(zone, centroid),
    [zone, centroid],
  );
  const ground = terrainZ;
  const access = getDerivedParkAccess(zone);
  const entries = useMemo(
    () =>
      (access?.paths ?? []).map((path) =>
        path.points.map(([lng, lat]) => ({
          x: (lng - centroid.lng) * metersPerDegLon(centroid.lat),
          y: (lat - centroid.lat) * METERS_PER_DEG_LAT,
        })),
      ),
    [access, centroid],
  );
  const trees = layout.trees.filter((p) =>
    entries.every((path) =>
      path.every((q, i) => i === 0 || distanceToSegment(p, path[i - 1], q) > 4),
    ),
  );
  return (
    <group
      name={`park-trio-${layout.kind}`}
      userData={{
        parkPilot: true,
        layoutStatus: layout.status,
        notes: layout.notes,
      }}
    >
      <Surface
        ring={layout.boundary}
        role="lawn"
        terrainZ={ground}
        grid={groundGrid}
        tint={layout.kind === "garden" ? "#bebba0" : "#c0cdaa"}
      />
      {layout.courtyard && (
        <Surface
          ring={layout.courtyard}
          role="safety"
          terrainZ={ground}
          grid={groundGrid}
          extraLift={0.002}
        />
      )}
      {layout.paths.map((path, i) => (
        <Surface
          key={`path-${i}`}
          ring={path.points}
          pathWidth={path.width}
          closed={path.closed}
          role={layout.kind === "garden" ? "paver" : "safety"}
          terrainZ={ground}
          grid={groundGrid}
        />
      ))}
      {entries.map((path, i) => (
        <Surface
          key={`entry-${i}`}
          ring={path}
          pathWidth={2.4}
          role="safety"
          terrainZ={ground}
          grid={groundGrid}
        />
      ))}
      {layout.modules.map((module) => (
        <FixedModule key={module.id} module={module} ground={ground} />
      ))}
      {[0, 1, 2].map((variant) => (
        <Woodland
          key={variant}
          variant={variant}
          points={trees.filter((_, i) => i % 3 === variant)}
          terrainZ={ground}
        />
      ))}
    </group>
  );
}
