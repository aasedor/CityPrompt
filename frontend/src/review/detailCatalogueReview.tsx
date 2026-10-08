/** Local visual and draw-call review; never mounted in the student application. */
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html, OrbitControls, useGLTF } from "@react-three/drei";
import { Group, Matrix4 } from "three";
import {
  DETAIL_CATALOGUE,
  detailAsset,
} from "../features/parks/detailCatalogue";
import {
  buildDetailInstances,
  disposeDetailInstances,
} from "../features/parks/detailInstances";

function Copies({
  asset,
  matrices,
  batched,
}: {
  asset: string;
  matrices: Matrix4[];
  batched: boolean;
}) {
  const { scene } = useGLTF(detailAsset(asset).url);
  const group = useMemo(() => {
    if (batched) return buildDetailInstances(scene, matrices);
    const result = new Group();
    matrices.forEach((matrix) => {
      const wrapper = new Group();
      wrapper.matrixAutoUpdate = false;
      wrapper.matrix.copy(matrix);
      wrapper.add(scene.clone(true));
      result.add(wrapper);
    });
    return result;
  }, [scene, matrices, batched]);
  useEffect(() => () => disposeDetailInstances(group), [group]);
  return <primitive object={group} dispose={null} />;
}
const ZERO_OFFSET = [0, 0, 0];
function Card({ asset, index }: { asset: string; index: number }) {
  const model = detailAsset(asset);
  const scale = 9 / Math.max(...model.dimensions);
  const offset = model.offset ?? ZERO_OFFSET;
  const matrices = useMemo(
    () => [
      new Matrix4()
        .makeRotationX(Math.PI / 2)
        .multiply(new Matrix4().makeScale(scale, scale, scale))
        .multiply(
          new Matrix4().makeTranslation(
            ...(offset as [number, number, number]),
          ),
        ),
    ],
    [scale, offset],
  );
  return (
    <group
      position={[((index % 5) - 2) * 17, (1.5 - Math.floor(index / 5)) * 18, 0]}
    >
      <Suspense fallback={<Html>Loading {model.label}…</Html>}>
        <Copies asset={asset} matrices={matrices} batched />
      </Suspense>
      <Html
        position={[0, -5, 0]}
        center
        style={{
          width: 135,
          textAlign: "center",
          font: "11px Arial",
          background: "#ffffffe6",
          padding: 3,
        }}
      >
        <strong>{model.label}</strong>
        <br />
        {model.dimensions.map((n) => n.toFixed(1)).join(" × ")} m
      </Html>
    </group>
  );
}
function Metrics({ onStats }: { onStats: (value: string) => void }) {
  const elapsed = useRef(0);
  useFrame(({ gl }, delta) => {
    elapsed.current += delta;
    if (elapsed.current > 1) {
      onStats(
        `${gl.info.render.calls} draw calls · ${gl.info.render.triangles.toLocaleString()} triangles`,
      );
      elapsed.current = 0;
    }
  });
  return null;
}
function Review() {
  const [page, setPage] = useState(0),
    [stress, setStress] = useState(false),
    [batched, setBatched] = useState(true),
    [stats, setStats] = useState("Loading");
  const matrices = useMemo(
    () =>
      Array.from({ length: 100 }, (_, i) =>
        new Matrix4()
          .makeTranslation(
            ((i % 10) - 4.5) * 7,
            (Math.floor(i / 10) - 4.5) * 7,
            0,
          )
          .multiply(new Matrix4().makeRotationX(Math.PI / 2)),
      ),
    [],
  );
  return (
    <>
      <div
        style={{
          position: "absolute",
          zIndex: 5,
          padding: 10,
          background: "#fffffff0",
          font: "14px Arial",
        }}
      >
        <b>100-object catalogue review</b> · {stats}
        <br />
        <button onClick={() => setStress(false)}>Catalogue</button>
        {[0, 1, 2, 3, 4].map((n) => (
          <button
            key={n}
            onClick={() => {
              setPage(n);
              setStress(false);
            }}
          >
            Page {n + 1}
          </button>
        ))}
        <button onClick={() => setStress(true)}>100 benches</button>
        <button onClick={() => setBatched((b) => !b)}>
          {batched ? "Use individual copies" : "Use batched copies"}
        </button>
        <br />
        {stress
          ? `${batched ? "Batched" : "Individual"} · 100 identical benches, same camera and geometry`
          : `Page ${page + 1} of 5 · normalized preview sizes; labels show real dimensions`}
      </div>
      <Canvas
        orthographic
        camera={{
          position: [0, -75, 130],
          zoom: 8.8,
          up: [0, 0, 1],
          near: 0.1,
          far: 500,
        }}
        dpr={1}
      >
        <color attach="background" args={["#e8eade"]} />
        <ambientLight intensity={1.6} />
        <directionalLight position={[30, -20, 80]} intensity={2.2} />
        <mesh position={[0, 0, -0.03]}>
          <planeGeometry args={[200, 200]} />
          <meshStandardMaterial color="#e0e1d2" />
        </mesh>
        {stress ? (
          <Suspense fallback={null}>
            <Copies
              asset="timber-bench"
              matrices={matrices}
              batched={batched}
            />
          </Suspense>
        ) : (
          DETAIL_CATALOGUE.slice(page * 20, page * 20 + 20).map((m, i) => (
            <Card key={m.id} asset={m.id} index={i} />
          ))
        )}
        <Metrics onStats={setStats} />
        <OrbitControls target={[0, 0, 0]} makeDefault />
      </Canvas>
    </>
  );
}
const root = createRoot(document.getElementById("root")!);
if (import.meta.hot) import.meta.hot.dispose(() => root.unmount());
root.render(<Review />);
