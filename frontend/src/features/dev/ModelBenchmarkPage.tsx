import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three-stdlib';
import {
  Activity,
  Check,
  Download,
  Gauge,
  Loader2,
  Play,
  RotateCcw,
  Triangle,
} from 'lucide-react';
import {
  disposeArchitecturalCloneMaterials,
  prepareArchitecturalClone,
} from '@/components/viewer/globe/modelMaterialQuality';
import {
  MODEL_BENCHMARK_ASSETS,
  MODEL_BENCHMARK_COUNTS,
  type ModelBenchmarkAsset,
} from './modelBenchmarkAssets';
import {
  buildInstanceGrid,
  compareBenchmarkRuns,
  formatBytes,
  summarizeFrameTimings,
  type BenchmarkComparison,
  type FrameTimingSummary,
} from './modelBenchmarkMetrics';

type BenchmarkVariant = 'original' | 'optimized';

interface BenchmarkRun {
  variant: BenchmarkVariant;
  instances: number;
  loadMs: number;
  setupMs: number;
  totalDrawCalls: number;
  modelDrawCalls: number;
  triangles: number;
  geometries: number;
  textures: number;
  heapMiB: number | null;
  heapDeltaMiB: number | null;
  minY: number;
  extents: [number, number, number];
  timing: FrameTimingSummary;
  previewDataUrl: string;
}

interface BenchmarkCase {
  instances: number;
  original: BenchmarkRun;
  optimized: BenchmarkRun;
  comparison: BenchmarkComparison;
}

type BenchmarkReportRun = Omit<BenchmarkRun, 'previewDataUrl'>;

interface BenchmarkReportCase {
  instances: number;
  original: BenchmarkReportRun;
  optimized: BenchmarkReportRun;
  comparison: BenchmarkComparison;
}

interface ModelBenchmarkReport {
  schemaVersion: 1;
  assetId: string;
  assetName: string;
  generatedAt: string;
  viewport: { width: number; height: number; devicePixelRatio: number };
  userAgent: string;
  samplesPerRun: number;
  cases: BenchmarkReportCase[];
}

declare global {
  interface Window {
    __CITYPROMPT_MODEL_BENCHMARK__?: ModelBenchmarkReport;
  }
}

const VIEWPORT_WIDTH = 960;
const VIEWPORT_HEIGHT = 540;
const SAMPLE_FRAMES = 20;
const WARMUP_FRAMES = 3;
const GROUND_DRAW_CALLS = 1;

function benchmarkAssetUrl(asset: ModelBenchmarkAsset, variant: BenchmarkVariant): string {
  const nonce = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `/__model-benchmark/${variant}/${asset.id}.glb?benchmark=${nonce}`;
}

function yieldToBrowser(): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, 0));
}

function usedHeapMiB(): number | null {
  const memory = (performance as Performance & {
    memory?: { usedJSHeapSize?: number };
  }).memory;
  return memory?.usedJSHeapSize
    ? Number((memory.usedJSHeapSize / 1_048_576).toFixed(1))
    : null;
}

function disposeLoadedScene(root: THREE.Object3D): void {
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>();
  root.traverse((object) => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    geometries.add(mesh.geometry);
    const meshMaterials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const material of meshMaterials) {
      materials.add(material);
      for (const value of Object.values(material as unknown as Record<string, unknown>)) {
        if (value instanceof THREE.Texture) textures.add(value);
      }
    }
  });
  materials.forEach((material) => material.dispose());
  textures.forEach((texture) => texture.dispose());
  geometries.forEach((geometry) => geometry.dispose());
}

function applyCameraPose(
  camera: THREE.PerspectiveCamera,
  bounds: THREE.Box3,
  phase: number,
): void {
  const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  const horizontal = Math.max(size.x, size.z, 10);
  const distance = Math.max(horizontal * 1.18, size.y * 3.2, 32);
  const angle = -0.82 + phase * 0.72;
  camera.position.set(
    center.x + Math.cos(angle) * distance,
    center.y + distance * 0.5,
    center.z + Math.sin(angle) * distance,
  );
  camera.lookAt(center.x, center.y + size.y * 0.16, center.z);
  camera.near = Math.max(0.05, distance / 1_000);
  camera.far = distance * 10;
  camera.updateProjectionMatrix();
}

class ModelBenchmarkRunner {
  private renderer: THREE.WebGLRenderer;

  private camera = new THREE.PerspectiveCamera(
    38,
    VIEWPORT_WIDTH / VIEWPORT_HEIGHT,
    0.05,
    5_000,
  );

  constructor(canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      preserveDrawingBuffer: true,
      powerPreference: 'high-performance',
    });
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(VIEWPORT_WIDTH, VIEWPORT_HEIGHT, false);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.08;
  }

  dispose(): void {
    this.renderer.dispose();
  }

  async run(
    asset: ModelBenchmarkAsset,
    variant: BenchmarkVariant,
    instances: number,
    onProgress: (message: string) => void,
  ): Promise<BenchmarkRun> {
    onProgress(`Loading ${variant} ${asset.name}…`);
    const loadStarted = performance.now();
    const loaded = await new GLTFLoader().loadAsync(benchmarkAssetUrl(asset, variant));
    const loadMs = performance.now() - loadStarted;
    const source = loaded.scene;
    source.updateMatrixWorld(true);
    const sourceBounds = new THREE.Box3().setFromObject(source);
    const sourceSize = sourceBounds.getSize(new THREE.Vector3());
    const sourceCenter = sourceBounds.getCenter(new THREE.Vector3());

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#c8d9ea');
    scene.add(new THREE.HemisphereLight('#eef7ff', '#4b4740', 2.4));
    const key = new THREE.DirectionalLight('#fff4df', 3.2);
    key.position.set(80, 120, 70);
    scene.add(key);
    const fill = new THREE.DirectionalLight('#bad7ff', 1.35);
    fill.position.set(-70, 45, -60);
    scene.add(fill);

    onProgress(`Preparing ${instances} ${variant} instance${instances === 1 ? '' : 's'}…`);
    const heapBeforeSetup = usedHeapMiB();
    const setupStarted = performance.now();
    const modelGroup = new THREE.Group();
    const clones: THREE.Object3D[] = [];
    const positions = buildInstanceGrid(
      instances,
      Math.max(sourceSize.x * 1.08, 10),
      Math.max(sourceSize.z * 1.08, 10),
    );
    const maxAnisotropy = this.renderer.capabilities.getMaxAnisotropy();
    for (let index = 0; index < positions.length; index += 1) {
      const clone = prepareArchitecturalClone(source, {
        renderOrder: 150,
        maxAnisotropy,
        ambientOcclusion: 'disable',
      });
      clone.position.set(
        positions[index].x - sourceCenter.x,
        -sourceBounds.min.y,
        positions[index].z - sourceCenter.z,
      );
      modelGroup.add(clone);
      clones.push(clone);
      if (index > 0 && index % 5 === 0) await yieldToBrowser();
    }
    scene.add(modelGroup);
    modelGroup.updateMatrixWorld(true);
    const worldBounds = new THREE.Box3().setFromObject(modelGroup);
    const worldSize = worldBounds.getSize(new THREE.Vector3());
    const worldCenter = worldBounds.getCenter(new THREE.Vector3());
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(worldSize.x * 1.25, worldSize.z * 1.25),
      new THREE.MeshStandardMaterial({ color: '#ddd8ca', roughness: 1 }),
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.set(worldCenter.x, -0.015, worldCenter.z);
    scene.add(ground);
    const setupMs = performance.now() - setupStarted;

    applyCameraPose(this.camera, worldBounds, 0.5);
    onProgress(`Warming ${variant} shaders…`);
    await this.renderer.compileAsync(scene, this.camera);
    const graphics = this.renderer.getContext();
    for (let index = 0; index < WARMUP_FRAMES; index += 1) {
      applyCameraPose(this.camera, worldBounds, index / Math.max(1, WARMUP_FRAMES - 1));
      this.renderer.render(scene, this.camera);
      graphics.finish();
    }

    onProgress(`Measuring ${variant}: ${SAMPLE_FRAMES} deterministic frames…`);
    const timings: number[] = [];
    let totalDrawCalls = 0;
    let triangles = 0;
    for (let index = 0; index < SAMPLE_FRAMES; index += 1) {
      applyCameraPose(this.camera, worldBounds, index / Math.max(1, SAMPLE_FRAMES - 1));
      const frameStarted = performance.now();
      this.renderer.render(scene, this.camera);
      graphics.finish();
      timings.push(performance.now() - frameStarted);
      totalDrawCalls = Math.max(totalDrawCalls, this.renderer.info.render.calls);
      triangles = Math.max(triangles, this.renderer.info.render.triangles - 2);
      if (index > 0 && index % 4 === 0) {
        onProgress(`Measuring ${variant}: frame ${index + 1}/${SAMPLE_FRAMES}…`);
        await yieldToBrowser();
      }
    }
    const previewDataUrl = this.renderer.domElement.toDataURL('image/png');
    const heapAfterRun = usedHeapMiB();
    const result: BenchmarkRun = {
      variant,
      instances,
      loadMs: Number(loadMs.toFixed(1)),
      setupMs: Number(setupMs.toFixed(1)),
      totalDrawCalls,
      modelDrawCalls: Math.max(0, totalDrawCalls - GROUND_DRAW_CALLS),
      triangles,
      geometries: this.renderer.info.memory.geometries,
      textures: this.renderer.info.memory.textures,
      heapMiB: heapAfterRun,
      heapDeltaMiB: heapBeforeSetup === null || heapAfterRun === null
        ? null
        : Number((heapAfterRun - heapBeforeSetup).toFixed(1)),
      minY: sourceBounds.min.y,
      extents: [sourceSize.x, sourceSize.y, sourceSize.z],
      timing: summarizeFrameTimings(timings),
      previewDataUrl,
    };

    scene.remove(modelGroup, ground);
    clones.forEach((clone) => disposeArchitecturalCloneMaterials(clone));
    ground.geometry.dispose();
    (ground.material as THREE.Material).dispose();
    disposeLoadedScene(source);
    this.renderer.renderLists.dispose();
    return result;
  }
}

function metric(value: number, suffix = ''): string {
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
}

function comparisonStatus(comparison: BenchmarkComparison): { label: string; className: string } {
  const passes = comparison.geometryMatches && comparison.groundDatumMatches;
  return passes
    ? { label: 'Parity pass', className: 'bg-lime-300 text-primary-950' }
    : { label: 'Investigate', className: 'bg-red-500 text-white' };
}

function withoutPreview(run: BenchmarkRun): BenchmarkReportRun {
  const { previewDataUrl: _previewDataUrl, ...reportRun } = run;
  return reportRun;
}

export function ModelBenchmarkPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const runnerRef = useRef<ModelBenchmarkRunner | null>(null);
  const [assetId, setAssetId] = useState(MODEL_BENCHMARK_ASSETS[0].id);
  const [selectedCount, setSelectedCount] = useState<number>(10);
  const [results, setResults] = useState<BenchmarkCase[]>([]);
  const [status, setStatus] = useState('Ready to benchmark');
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const asset = useMemo(
    () => MODEL_BENCHMARK_ASSETS.find((candidate) => candidate.id === assetId)
      ?? MODEL_BENCHMARK_ASSETS[0],
    [assetId],
  );

  useEffect(() => {
    if (!canvasRef.current) return undefined;
    const runner = new ModelBenchmarkRunner(canvasRef.current);
    runnerRef.current = runner;
    return () => {
      runner.dispose();
      runnerRef.current = null;
    };
  }, []);

  const runCounts = async (counts: readonly number[]) => {
    const runner = runnerRef.current;
    if (!runner || running) return;
    setRunning(true);
    setError(null);
    setResults([]);
    const completed: BenchmarkCase[] = [];
    try {
      for (let caseIndex = 0; caseIndex < counts.length; caseIndex += 1) {
        const instances = counts[caseIndex];
        const order: BenchmarkVariant[] = caseIndex % 2 === 0
          ? ['original', 'optimized']
          : ['optimized', 'original'];
        const runs = new Map<BenchmarkVariant, BenchmarkRun>();
        for (const variant of order) {
          runs.set(variant, await runner.run(asset, variant, instances, setStatus));
        }
        const original = runs.get('original');
        const optimized = runs.get('optimized');
        if (!original || !optimized) throw new Error('Benchmark pair did not complete.');
        const benchmarkCase: BenchmarkCase = {
          instances,
          original,
          optimized,
          comparison: compareBenchmarkRuns(original, optimized),
        };
        completed.push(benchmarkCase);
        setResults([...completed]);
      }
      const report: ModelBenchmarkReport = {
        schemaVersion: 1,
        assetId: asset.id,
        assetName: asset.name,
        generatedAt: new Date().toISOString(),
        viewport: {
          width: VIEWPORT_WIDTH,
          height: VIEWPORT_HEIGHT,
          devicePixelRatio: 1,
        },
        userAgent: navigator.userAgent,
        samplesPerRun: SAMPLE_FRAMES,
        cases: completed.map((benchmarkCase) => ({
          instances: benchmarkCase.instances,
          original: withoutPreview(benchmarkCase.original),
          optimized: withoutPreview(benchmarkCase.optimized),
          comparison: benchmarkCase.comparison,
        })),
      };
      window.__CITYPROMPT_MODEL_BENCHMARK__ = report;
      setStatus(`Complete · ${completed.length} A/B pair${completed.length === 1 ? '' : 's'}`);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : String(caught);
      setError(message);
      setStatus('Benchmark failed');
    } finally {
      setRunning(false);
    }
  };

  const downloadReport = () => {
    const report = window.__CITYPROMPT_MODEL_BENCHMARK__;
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `cityprompt-model-benchmark-${report.assetId}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const preview = results.length > 0 ? results[results.length - 1] : undefined;
  const statusTone = error
    ? 'bg-red-500 text-white'
    : running
      ? 'bg-cyan-300 text-primary-950'
      : 'bg-lime-300 text-primary-950';

  return (
    <main className="min-h-screen bg-[#d7e7f5] p-4 text-primary-950 sm:p-6 lg:p-8">
      <div className="mx-auto flex max-w-[1500px] flex-col gap-5">
        <header className="flex flex-col gap-4 rounded-[28px] border-2 border-primary-950 bg-[#fff9ec] p-5 shadow-[6px_6px_0_#151515] lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border-2 border-primary-950 bg-lime-300 px-3 py-1 text-xs font-black uppercase tracking-[0.16em]">
              <Gauge size={14} /> Developer-only laboratory
            </div>
            <h1 className="text-3xl font-black tracking-tight sm:text-4xl">Sticker Method performance benchmark</h1>
            <p className="mt-2 max-w-3xl text-sm font-medium text-primary-950/65 sm:text-base">
              Original Git LFS object versus optimized seed, measured in one renderer with identical camera,
              lighting, material preparation, viewport, and GPU synchronization.
            </p>
          </div>
          <div
            data-testid="benchmark-status"
            className={`inline-flex min-w-64 items-center justify-center gap-2 rounded-full border-2 border-primary-950 px-4 py-2 text-sm font-black shadow-[3px_3px_0_#151515] ${statusTone}`}
          >
            {running ? <Loader2 className="animate-spin" size={17} /> : error ? <Triangle size={17} /> : <Check size={17} />}
            {status}
          </div>
        </header>

        <section className="grid gap-4 rounded-[24px] border-2 border-primary-950 bg-white p-4 shadow-[5px_5px_0_#151515] lg:grid-cols-[minmax(0,1fr)_auto_auto] lg:items-end">
          <label className="flex flex-col gap-2 text-xs font-black uppercase tracking-[0.12em]">
            Building asset
            <select
              aria-label="Building asset"
              className="rounded-xl border-2 border-primary-950 bg-[#fff9ec] px-3 py-3 text-sm font-bold normal-case tracking-normal"
              disabled={running}
              value={assetId}
              onChange={(event) => setAssetId(event.target.value)}
            >
              {MODEL_BENCHMARK_ASSETS.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>{candidate.name}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-2 text-xs font-black uppercase tracking-[0.12em]">
            Selected load
            <select
              aria-label="Selected load"
              className="rounded-xl border-2 border-primary-950 bg-[#fff9ec] px-3 py-3 text-sm font-bold normal-case tracking-normal"
              disabled={running}
              value={selectedCount}
              onChange={(event) => setSelectedCount(Number(event.target.value))}
            >
              {MODEL_BENCHMARK_COUNTS.map((count) => (
                <option key={count} value={count}>{count} instance{count === 1 ? '' : 's'}</option>
              ))}
            </select>
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-xl border-2 border-primary-950 bg-cyan-300 px-4 py-3 text-sm font-black shadow-[3px_3px_0_#151515] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={running}
              onClick={() => void runCounts([selectedCount])}
            >
              <Play size={16} /> Run selected
            </button>
            <button
              type="button"
              data-testid="run-benchmark-suite"
              className="inline-flex items-center gap-2 rounded-xl border-2 border-primary-950 bg-lime-300 px-4 py-3 text-sm font-black shadow-[3px_3px_0_#151515] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={running}
              onClick={() => void runCounts(MODEL_BENCHMARK_COUNTS)}
            >
              {running ? <Loader2 className="animate-spin" size={16} /> : <Activity size={16} />}
              Run 1 / 10 / 25 suite
            </button>
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(330px,0.55fr)]">
          <div className="overflow-hidden rounded-[24px] border-2 border-primary-950 bg-primary-950 shadow-[5px_5px_0_#151515]">
            <div className="flex items-center justify-between border-b-2 border-primary-950 bg-[#fff9ec] px-4 py-3 text-sm font-black">
              <span>Live deterministic viewport</span>
              <span className="text-primary-950/55">960 × 540 · DPR 1 · GPU finish enabled</span>
            </div>
            <canvas
              ref={canvasRef}
              className="aspect-video h-auto w-full bg-[#c8d9ea]"
              width={VIEWPORT_WIDTH}
              height={VIEWPORT_HEIGHT}
            />
          </div>

          <aside className="grid content-start gap-4">
            <div className="rounded-[24px] border-2 border-primary-950 bg-[#fff9ec] p-5 shadow-[5px_5px_0_#151515]">
              <h2 className="text-lg font-black">
                {asset.comparisonKind === 'delivery-control' ? 'Delivery A/A control' : 'Expected structural gain'}
              </h2>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl border-2 border-primary-950 bg-white p-3">
                  <dt className="font-bold text-primary-950/55">Original</dt>
                  <dd className="mt-1 text-xl font-black">{asset.original.primitives.toLocaleString()}</dd>
                  <dd className="text-xs font-semibold">primitives</dd>
                </div>
                <div className="rounded-xl border-2 border-primary-950 bg-lime-200 p-3">
                  <dt className="font-bold text-primary-950/55">Optimized</dt>
                  <dd className="mt-1 text-xl font-black">{asset.optimized.primitives.toLocaleString()}</dd>
                  <dd className="text-xs font-semibold">primitives</dd>
                </div>
                <div className="rounded-xl border-2 border-primary-950 bg-white p-3">
                  <dt className="font-bold text-primary-950/55">Original size</dt>
                  <dd className="mt-1 font-black">{formatBytes(asset.original.bytes)}</dd>
                </div>
                <div className="rounded-xl border-2 border-primary-950 bg-cyan-100 p-3">
                  <dt className="font-bold text-primary-950/55">Optimized size</dt>
                  <dd className="mt-1 font-black">{formatBytes(asset.optimized.bytes)}</dd>
                </div>
              </dl>
            </div>

            <div className="rounded-[24px] border-2 border-primary-950 bg-white p-5 shadow-[5px_5px_0_#151515]">
              <h2 className="text-lg font-black">Measurement contract</h2>
              <ul className="mt-3 space-y-2 text-sm font-semibold text-primary-950/70">
                <li>• Production architectural material preparation</li>
                <li>• Three warm-up frames before 20 samples</li>
                <li>• Forced GPU completion per measured frame</li>
                <li>• Alternating A/B order across the suite</li>
                <li>• Bounds, triangles, and Y=0 parity checks</li>
                <li>• Heap allocation delta and GPU resource counts</li>
              </ul>
            </div>
          </aside>
        </section>

        {error && (
          <div className="rounded-2xl border-2 border-red-900 bg-red-100 p-4 font-bold text-red-900">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <section className="rounded-[24px] border-2 border-primary-950 bg-white p-4 shadow-[5px_5px_0_#151515] sm:p-5">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-2xl font-black">Measured results</h2>
                <p className="text-sm font-medium text-primary-950/60">Lower frame time is better. Speedup is original median ÷ optimized median.</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="inline-flex items-center gap-2 rounded-xl border-2 border-primary-950 bg-[#fff9ec] px-3 py-2 text-sm font-black"
                  disabled={running}
                  onClick={() => void runCounts(results.map(({ instances }) => instances))}
                >
                  <RotateCcw size={15} /> Rerun
                </button>
                <button
                  type="button"
                  className="inline-flex items-center gap-2 rounded-xl border-2 border-primary-950 bg-cyan-200 px-3 py-2 text-sm font-black"
                  disabled={running || !window.__CITYPROMPT_MODEL_BENCHMARK__}
                  onClick={downloadReport}
                >
                  <Download size={15} /> JSON report
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1320px] border-separate border-spacing-0 text-left text-sm">
                <thead>
                  <tr className="bg-primary-950 text-white">
                    {['Instances', 'Model calls O → N', 'Reduction', 'Median O → N', 'p95 O → N', 'FPS O → N', 'Speedup', 'Load O → N', 'Setup O → N', 'Heap Δ O → N', 'GPU g/t O → N', 'Parity'].map((label) => (
                      <th key={label} className="border-r border-white/20 px-3 py-3 font-black last:border-r-0">{label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => {
                    const parity = comparisonStatus(result.comparison);
                    return (
                      <tr key={result.instances} data-testid={`benchmark-row-${result.instances}`} className="odd:bg-[#fff9ec]">
                        <td className="border-b border-primary-950/15 px-3 py-3 text-lg font-black">{result.instances}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 font-bold">{metric(result.original.modelDrawCalls)} → {metric(result.optimized.modelDrawCalls)}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 font-black text-emerald-700">{metric(result.comparison.drawCallReductionPercent, '%')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 font-bold">{metric(result.original.timing.medianMs, ' ms')} → {metric(result.optimized.timing.medianMs, ' ms')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 font-bold">{metric(result.original.timing.p95Ms, ' ms')} → {metric(result.optimized.timing.p95Ms, ' ms')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 font-bold">{metric(result.original.timing.fpsFromMedian)} → {metric(result.optimized.timing.fpsFromMedian)}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3 text-lg font-black">{metric(result.comparison.medianSpeedup, '×')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3">{metric(result.original.loadMs, ' ms')} → {metric(result.optimized.loadMs, ' ms')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3">{metric(result.original.setupMs, ' ms')} → {metric(result.optimized.setupMs, ' ms')}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3">{result.original.heapDeltaMiB === null ? 'n/a' : `${result.original.heapDeltaMiB} MiB`} → {result.optimized.heapDeltaMiB === null ? 'n/a' : `${result.optimized.heapDeltaMiB} MiB`}</td>
                        <td className="border-b border-primary-950/15 px-3 py-3">{result.original.geometries}g/{result.original.textures}t → {result.optimized.geometries}g/{result.optimized.textures}t</td>
                        <td className="border-b border-primary-950/15 px-3 py-3"><span className={`rounded-full border border-primary-950 px-2 py-1 text-xs font-black ${parity.className}`}>{parity.label}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {preview && (
              <p
                className="mt-4 rounded-xl border-2 border-primary-950 bg-lime-100 px-4 py-3 text-sm font-bold"
                data-testid="benchmark-grounding"
              >
                Ground Y O / N: {preview.original.minY.toFixed(4)} m / {preview.optimized.minY.toFixed(4)} m
                {' | '}Bounds O: {preview.original.extents.map((value) => value.toFixed(3)).join(' x ')} m
                {' | '}Bounds N: {preview.optimized.extents.map((value) => value.toFixed(3)).join(' x ')} m
              </p>
            )}
          </section>
        )}

        {preview && (
          <section className="grid gap-4 lg:grid-cols-2">
            {([
              ['Original', preview.original],
              ['Optimized', preview.optimized],
            ] as const).map(([label, run]) => (
              <figure key={label} className="overflow-hidden rounded-[24px] border-2 border-primary-950 bg-white shadow-[5px_5px_0_#151515]">
                <figcaption className="flex items-center justify-between border-b-2 border-primary-950 bg-[#fff9ec] px-4 py-3">
                  <span className="text-lg font-black">{label} · {run.instances} instance{run.instances === 1 ? '' : 's'}</span>
                  <span className="text-sm font-bold">{run.modelDrawCalls.toLocaleString()} calls · {run.timing.medianMs} ms median</span>
                </figcaption>
                <img className="aspect-video w-full bg-[#c8d9ea] object-cover" src={run.previewDataUrl} alt={`${label} benchmark render`} />
              </figure>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
