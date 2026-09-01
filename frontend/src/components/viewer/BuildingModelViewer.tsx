/**
 * BuildingModelViewer — a modal for the building representation that owns the
 * live scene. Persisted LEGO assemblies take precedence over historical whole-
 * model URLs, matching the globe's authored-model ownership contract.
 */

import { Component, Suspense, useEffect, useMemo, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { Canvas, useThree } from '@react-three/fiber';
import { Bounds, Center, Environment, Html, OrbitControls, useGLTF, useProgress } from '@react-three/drei';
import { Loader2, X } from 'lucide-react';
import { resolveApiFileUrl } from '@/services/api';
import { createKtx2LoaderExtension } from '@/lib/ktx2GltfLoader';
import type { BuildingModelSource } from '@/features/legoAssembly/buildingModelSource';
import { ModuleInstance } from '@/features/legoAssembly/legoShared';
import {
  disposeArchitecturalCloneMaterials,
  prepareArchitecturalClone,
  setArchitecturalGlazingLod,
} from './globe/modelMaterialQuality';

function Model({ url }: { url: string }) {
  const { gl } = useThree();
  const extendLoader = useMemo(() => createKtx2LoaderExtension(gl), [gl]);
  const { scene } = useGLTF(url, true, true, extendLoader);
  const model = useMemo(() => {
    const cloned = prepareArchitecturalClone(scene, {
      renderOrder: 0,
      maxAnisotropy: gl.capabilities.getMaxAnisotropy(),
    });
    setArchitecturalGlazingLod(cloned, 'near');
    return cloned;
  }, [gl, scene]);
  useEffect(() => () => disposeArchitecturalCloneMaterials(model), [model]);
  return <primitive object={model} />;
}

function AssemblyModel({ source }: { source: Extract<BuildingModelSource, { kind: 'lego_assembly' }> }) {
  return (
    <group>
      {source.recipe.instances.map((instance, index) => (
        <ModuleInstance
          key={`${instance.asset_id}-${instance.level}-${index}`}
          instance={instance}
        />
      ))}
    </group>
  );
}

function LoadProgress() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="flex items-center gap-2 whitespace-nowrap text-xs font-semibold text-white/80">
        <Loader2 className="h-4 w-4 animate-spin" />
        {progress > 0 ? `${progress.toFixed(0)}%` : 'Loading model…'}
      </div>
    </Html>
  );
}

/** useGLTF throws on a bad/broken model; Suspense doesn't catch errors. */
class ModelErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed) {
      return (
        <Html center>
          <div className="whitespace-nowrap text-xs font-semibold text-red-300">
            Couldn&apos;t load this model.
          </div>
        </Html>
      );
    }
    return this.props.children;
  }
}

export function BuildingModelViewer({
  source,
  name,
  onClose,
}: {
  source: BuildingModelSource;
  name: string;
  onClose: () => void;
}) {
  const legacyUrl = source.kind === 'legacy_model'
    ? resolveApiFileUrl(source.modelUrl)
    : null;
  const downloadUrl = source.downloadUrl ? resolveApiFileUrl(source.downloadUrl) : null;
  const presentationLabel = source.presentation === 'architectural_clay'
    ? 'architectural clay'
    : source.presentation === 'assembly'
      ? 'architectural assembly'
      : '3D model';

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4"
      onClick={onClose}
    >
      <div
        className="relative h-[80vh] w-[92vw] max-w-4xl overflow-hidden rounded-xl border-2 border-[#151515] bg-[#161616] shadow-[6px_6px_0_0_rgba(0,0,0,0.5)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between bg-black/50 px-3 py-2">
          <span className="truncate text-xs font-black uppercase text-white">
            {name} · {presentationLabel}
            {source.variantKey ? ` · ${source.variantKey.replace(/_/g, ' ')}` : ''}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-white/80 transition hover:bg-white/10 hover:text-white"
            aria-label="Close 3D model viewer"
          >
            <X size={16} />
          </button>
        </div>

        <Canvas shadows camera={{ position: [4, 3, 6], fov: 45 }} dpr={[1, 2]}>
          <ambientLight intensity={0.6} />
          <directionalLight castShadow position={[6, 9, 5]} intensity={1.2} />
          <directionalLight position={[-6, 3, -5]} intensity={0.4} />
          <Environment preset="city" background={false} />
          <ModelErrorBoundary>
            <Suspense fallback={<LoadProgress />}>
              {/* Center at origin + auto-frame — Meshy models arrive at any
                  scale/offset, so a fixed camera would miss most of them. */}
              <Bounds fit clip observe margin={1.2}>
                <Center>
                  {source.kind === 'lego_assembly'
                    ? <AssemblyModel source={source} />
                    : <Model url={legacyUrl!} />}
                </Center>
              </Bounds>
            </Suspense>
          </ModelErrorBoundary>
          <OrbitControls makeDefault autoRotate autoRotateSpeed={0.7} enablePan />
        </Canvas>

        {downloadUrl && (
          <a
            href={downloadUrl}
            download
            className="absolute bottom-3 right-3 z-10 rounded border-2 border-[#151515] bg-[#c9ff3d] px-2.5 py-1 text-[11px] font-black uppercase text-[#151515] shadow-[2px_2px_0_0_#151515] transition hover:bg-[#d8ff70]"
          >
            Download .glb
          </a>
        )}
        <span className="pointer-events-none absolute bottom-3 left-3 z-10 text-[10px] font-semibold text-white/40">
          drag to orbit · scroll to zoom
        </span>
      </div>
    </div>,
    document.body,
  );
}
