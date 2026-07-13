import { Component, Suspense, useMemo, useState, type ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';
import { Bounds, Grid, Html, OrbitControls, useGLTF, useProgress } from '@react-three/drei';
import { Box, Loader2, RefreshCw, X } from 'lucide-react';
import { resolveApiFileUrl } from '@/services/api';
import type { SiteZoneProperties } from '@/types';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  type LegoAssemblyInstance,
  type LegoAssemblyPlan,
} from './legoAssemblyApi';

function Progress() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex items-center gap-2 whitespace-nowrap rounded bg-black/70 px-3 py-2 text-xs font-semibold text-white">
        <Loader2 className="h-4 w-4 animate-spin" />
        {progress > 0 ? `${progress.toFixed(0)}%` : 'Loading modules…'}
      </div>
    </Html>
  );
}

class PreviewErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <Html center>
        <div className="rounded bg-red-950/90 px-3 py-2 text-xs font-semibold text-red-200">
          A module could not be loaded.
        </div>
      </Html>
    ) : this.props.children;
  }
}

function ModuleInstance({ instance }: { instance: LegoAssemblyInstance }) {
  const url = resolveApiFileUrl(instance.model_url);
  const { scene } = useGLTF(url);
  const model = useMemo(() => scene.clone(true), [scene]);
  const [sx, sy, sz] = instance.scale;
  const [x, y, z] = instance.position;

  return (
    <primitive
      object={model}
      position={[x, z, y]}
      scale={[sx, sz, sy]}
      rotation={[0, -instance.rotation_degrees * Math.PI / 180, 0]}
    />
  );
}

function AssemblyScene({ plan }: { plan: LegoAssemblyPlan }) {
  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight position={[8, 12, 7]} intensity={1.5} />
      <directionalLight position={[-8, 5, -6]} intensity={0.35} />
      <Grid args={[80, 80]} cellSize={1} sectionSize={5} fadeDistance={70} />
      <Bounds fit clip observe margin={1.25}>
        <group>
          {plan.instances.map((instance, index) => (
            <ModuleInstance key={`${instance.asset_id}-${instance.level}-${index}`} instance={instance} />
          ))}
        </group>
      </Bounds>
      <OrbitControls makeDefault enablePan />
    </>
  );
}

export function LegoAssemblyPreview({
  widthM,
  depthM,
  floors,
  properties,
  onClose,
}: {
  widthM: number;
  depthM: number;
  floors: number;
  properties?: SiteZoneProperties;
  onClose: () => void;
}) {
  const [plan, setPlan] = useState<LegoAssemblyPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const assemble = async () => {
    setLoading(true);
    setError(null);
    try {
      const archetype = legoArchetypeContextFromZone(properties);
      const result = await legoAssemblyApi.plan({
        target_width_m: widthM,
        target_depth_m: depthM,
        target_floors: floors,
        ...archetype,
      });
      setPlan(result);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Could not assemble this building.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/75 p-4" onClick={onClose}>
      <div
        className="relative flex h-[84vh] w-[94vw] max-w-6xl overflow-hidden rounded-xl border-2 border-[#151515] bg-[#f7f7f1] shadow-[8px_8px_0_0_rgba(0,0,0,0.45)]"
        onClick={(event) => event.stopPropagation()}
      >
        <aside className="w-72 shrink-0 border-r-2 border-[#151515] bg-white p-4">
          <div className="mb-4 flex items-center gap-2">
            <Box className="h-5 w-5" />
            <h2 className="text-sm font-black uppercase">LEGO Assembly</h2>
          </div>

          <dl className="space-y-2 text-xs">
            <div className="flex justify-between"><dt>Footprint</dt><dd className="font-bold">{widthM.toFixed(1)} × {depthM.toFixed(1)} m</dd></div>
            <div className="flex justify-between"><dt>Floors</dt><dd className="font-bold">{floors}</dd></div>
            {plan && <div className="flex justify-between"><dt>Family</dt><dd className="max-w-32 truncate font-bold">{plan.family}</dd></div>}
            {plan && <div className="flex justify-between"><dt>Height</dt><dd className="font-bold">{plan.assembled_height_m.toFixed(1)} m</dd></div>}
            {plan && <div className="flex justify-between"><dt>Modules</dt><dd className="font-bold">{plan.instances.length}</dd></div>}
          </dl>

          <button
            type="button"
            onClick={assemble}
            disabled={loading}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            {plan ? 'Reassemble' : 'Auto assemble'}
          </button>

          {error && <p className="mt-4 rounded border border-red-300 bg-red-50 p-2 text-xs text-red-800">{error}</p>}

          <p className="mt-5 text-[11px] leading-relaxed text-black/55">
            Uses the selected Urban Intelligence archetype ID and reuse keys to choose a compatible podium, repeating floor, setback and roof family.
          </p>
        </aside>

        <main className="relative min-w-0 flex-1 bg-[#1b1b1b]">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-3 top-3 z-10 rounded bg-black/60 p-2 text-white hover:bg-black"
            aria-label="Close LEGO assembly preview"
          >
            <X className="h-4 w-4" />
          </button>

          {plan ? (
            <Canvas camera={{ position: [12, 10, 16], fov: 42 }} dpr={[1, 2]}>
              <PreviewErrorBoundary>
                <Suspense fallback={<Progress />}>
                  <AssemblyScene plan={plan} />
                </Suspense>
              </PreviewErrorBoundary>
            </Canvas>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-white/55">
              <div>
                <Box className="mx-auto mb-3 h-10 w-10" />
                <p className="text-sm font-bold">Choose Auto Assemble to preview the archetype as reusable modules.</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
