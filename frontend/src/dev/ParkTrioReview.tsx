import React, { Suspense, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { GlobeParkTrioPilot } from "../components/viewer/globe/GlobeParkTrioPilot";
import {
  PARK_TRIO,
  PARK_TRIO_REVISION,
  parkTrioLayout,
  type ParkTrioKind,
} from "../components/viewer/globe/parkTrioLayout";
import type { SiteZone } from "../types";
import {
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from "../components/viewer/mapEngine/geoUtils";

const center = { lng: -114.04677, lat: 51.04542 };
function Pose({ view, size }: { view: string; size: number }) {
  const { camera } = useThree();
  React.useEffect(() => {
    const positions: Record<string, [number, number, number]> = {
      aerial: [size * 0.75, -size * 0.85, size * 0.7],
      overhead: [0, -0.01, size * 1.3],
      walk: [0, -size * 0.22, 1.75],
      detail: [-size * 0.2, size * 0.23, 6],
    };
    camera.position.set(...positions[view]);
    camera.up.set(0, 0, 1);
    camera.lookAt(
      0,
      view === "walk" || view === "detail" ? size * 0.25 : 0,
      view === "walk" ? 3 : 0,
    );
    camera.updateProjectionMatrix();
  }, [camera, view, size]);
  return null;
}
function App() {
  const [kind, setKind] = useState<ParkTrioKind>("cinema"),
    [shape, setShape] = useState("standard"),
    [view, setView] = useState("aerial"),
    [slope, setSlope] = useState(false);
  const info = PARK_TRIO[kind];
  const dims =
    shape === "compact"
      ? info.min
      : shape === "large"
        ? info.size.map((v) => v * 1.3)
        : info.size;
  const w = shape === "narrow" ? 12 : dims[0],
    d = dims[1];
  const zone = useMemo<SiteZone>(
    () => ({
      id: "park-trio-lab",
      project_id: "local",
      zone_type: "green_space",
      color: "#688452",
      sort_order: 0,
      created_at: "2026-09-06",
      updated_at: "2026-09-06",
      properties: {
        green_space_archetype_id: info.parent,
        green_space_selected_variant_id: info.variant,
        park_trio_layout: PARK_TRIO_REVISION,
      },
      coordinates: (shape === "concave"
        ? [
            [-w / 2, -d / 2],
            [w / 2, -d / 2],
            [w / 2, 0],
            [0, 0],
            [0, d / 2],
            [-w / 2, d / 2],
          ]
        : [
            [-w / 2, -d / 2],
            [w / 2, -d / 2],
            [w / 2, d / 2],
            [-w / 2, d / 2],
          ]
      ).map(([x, y]) => {
        const a = shape === "rotated" ? 0.44 : 0;
        return [
          center.lng +
            (x * Math.cos(a) - y * Math.sin(a)) / metersPerDegLon(center.lat),
          center.lat + (x * Math.sin(a) + y * Math.cos(a)) / METERS_PER_DEG_LAT,
        ];
      }),
    }),
    [info, w, d, shape],
  );
  const layout = useMemo(() => parkTrioLayout(zone, center), [zone]);
  const ground = useMemo(
    () => (x: number, y: number) => (slope ? 0.02 * x + 0.008 * y : 0),
    [slope],
  );
  const floor = useMemo(() => {
    const g = new THREE.PlaneGeometry(500, 500);
    const p = g.getAttribute("position");
    for (let i = 0; i < p.count; i++)
      p.setZ(i, ground(p.getX(i), p.getY(i)) - 0.02);
    g.computeVertexNormals();
    return g;
  }, [ground]);
  React.useEffect(() => () => floor.dispose(), [floor]);
  return (
    <main
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        fontFamily: "Arial,sans-serif",
        background: "#f4f3ea",
        color: "#203d30",
      }}
    >
      <header
        style={{
          padding: "18px 26px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <small>CITY PROMPT · NEW PARK PILOTS</small>
          <h1 style={{ fontSize: 25, margin: "6px 0" }}>{info.label}</h1>
        </div>
        <span>Geometry review · not a final AI render</span>
      </header>
      <section
        style={{
          display: "flex",
          gap: 14,
          padding: "8px 26px",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <label>
          Park{" "}
          <select
            aria-label="Park"
            value={kind}
            onChange={(e) => setKind(e.target.value as ParkTrioKind)}
          >
            {Object.entries(PARK_TRIO).map(([id, p]) => (
              <option key={id} value={id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Plot{" "}
          <select
            aria-label="Plot"
            value={shape}
            onChange={(e) => setShape(e.target.value)}
          >
            {[
              "standard",
              "compact",
              "large",
              "rotated",
              "concave",
              "narrow",
            ].map((id) => (
              <option key={id}>{id}</option>
            ))}
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={slope}
            onChange={(e) => setSlope(e.target.checked)}
          />
          Sloping ground
        </label>
        {["aerial", "overhead", "walk", "detail"].map((id) => (
          <button
            key={id}
            onClick={() => setView(id)}
            style={{
              padding: "9px 16px",
              background: view === id ? "#264e3a" : "white",
              color: view === id ? "white" : "#264e3a",
              border: "1px solid #8a9e8e",
              borderRadius: 6,
            }}
          >
            {id}
          </button>
        ))}
        <span>
          {w.toFixed(0)} × {d.toFixed(0)} m
        </span>
      </section>
      <div style={{ flex: 1, minHeight: 0 }}>
        <Canvas
          shadows
          camera={{
            position: [60, -80, 65],
            up: [0, 0, 1],
            fov: 48,
            near: 0.1,
            far: 700,
          }}
          gl={{
            antialias: true,
            preserveDrawingBuffer: true,
            logarithmicDepthBuffer: true,
          }}
          onCreated={({ gl, scene, camera }) => {
            gl.toneMapping = THREE.ACESFilmicToneMapping;
            gl.toneMappingExposure = 1.05;
            Object.assign(window, { __parkTrioReview: { gl, scene, camera } });
          }}
        >
          <color attach="background" args={["#dce5df"]} />
          <ambientLight intensity={0.65} />
          <hemisphereLight args={["#ecf3ff", "#66764b", 1.1]} />
          <directionalLight
            position={[-50, -40, 95]}
            intensity={3}
            castShadow
            shadow-mapSize={[2048, 2048]}
            shadow-camera-left={-115}
            shadow-camera-right={115}
            shadow-camera-top={115}
            shadow-camera-bottom={-115}
            shadow-camera-far={300}
            shadow-bias={-0.001}
            shadow-normalBias={0.12}
          />
          <mesh geometry={floor} receiveShadow>
            <meshStandardMaterial color="#b7b8a1" roughness={1} />
          </mesh>
          <Suspense fallback={null}>
            <GlobeParkTrioPilot
              key={`${kind}-${shape}`}
              zone={zone}
              centroid={center}
              terrainZ={ground}
            />
          </Suspense>
          <Pose view={view} size={Math.max(w, d)} />
          <OrbitControls
            key={`${kind}-${shape}-${view}`}
            makeDefault
            target={
              view === "walk" || view === "detail"
                ? [0, Math.max(w, d) * 0.25, view === "walk" ? 3 : 0]
                : [0, 0, 0]
            }
            enableDamping={false}
            maxPolarAngle={Math.PI * 0.49}
          />
        </Canvas>
      </div>
      <footer
        style={{
          padding: "15px 26px",
          borderTop: "1px solid #ced5c7",
          fontSize: 13,
          lineHeight: 1.6,
        }}
      >
        <strong>{layout.status.toUpperCase()}</strong> ·{" "}
        {layout.notes.join(" ")}
        <br />
        This lab uses the same assembly as the Google tiles scene, on synthetic
        test terrain.
      </footer>
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
