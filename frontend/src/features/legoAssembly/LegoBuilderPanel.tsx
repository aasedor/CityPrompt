import { Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { Canvas } from '@react-three/fiber';
import { Bounds, Grid, OrbitControls } from '@react-three/drei';
import { AlertTriangle, Blocks, Check, Copy, Loader2, RefreshCw, Save, X } from 'lucide-react';
import { getApiErrorMessage } from '@/services/api';
import type { SiteZone } from '@/types';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  type LegoAssemblyPlan,
} from './legoAssemblyApi';
import {
  ModuleInstance,
  PreviewErrorBoundary,
  Progress,
  deriveZoneTargets,
  familyGenerationCommands,
  findCatalogOption,
  fitIsStretched,
  normalizeArchetypeId,
} from './legoShared';

// Zone types that get a modular building even without an explicit archetype.
const BUILDABLE_ZONE_TYPES = new Set<string>(['building', 'residential', 'development_area', 'development']);

// Equirectangular metres-per-degree constants (matches the plan-scale
// approximations used elsewhere in the planner).
const METRES_PER_DEG_LAT = 110540;
const METRES_PER_DEG_LNG_EQUATOR = 111320;

function isBuildableZone(zone: SiteZone): boolean {
  return BUILDABLE_ZONE_TYPES.has(zone.zone_type) || Boolean(zone.properties?.development_archetype_id);
}

/** Mean of the polygon vertices as [lng, lat]; null when there is no usable ring. */
function polygonCentroid(coordinates: number[][] | undefined): [number, number] | null {
  if (!coordinates || coordinates.length === 0) return null;
  let lng = 0;
  let lat = 0;
  let count = 0;
  for (const vertex of coordinates) {
    if (!Array.isArray(vertex) || vertex.length < 2) continue;
    const [vLng, vLat] = vertex;
    if (!Number.isFinite(vLng) || !Number.isFinite(vLat)) continue;
    lng += vLng;
    lat += vLat;
    count += 1;
  }
  if (count === 0) return null;
  return [lng / count, lat / count];
}

interface ZoneBuildItem {
  zone: SiteZone;
  label: string;
  /** Normalized archetype id used for the generate-family hint commands. */
  archetypeId?: string;
  targets: { width_m: number; depth_m: number; floors: number };
  /** Local-metre offset [x, z] from the plan centroid; null when the zone has no usable polygon. */
  offset: [number, number] | null;
  plan?: LegoAssemblyPlan;
  error?: string;
  familyMissing?: boolean;
}

/** Buildable zones with catalogue-derived targets and centroid placement offsets. */
function deriveItems(zones: SiteZone[]): ZoneBuildItem[] {
  const buildable = zones.filter(isBuildableZone);
  const centroids = buildable.map((zone) => polygonCentroid(zone.coordinates));
  const anchors = centroids.filter((c): c is [number, number] => c !== null);

  let lng0 = 0;
  let lat0 = 0;
  for (const [lng, lat] of anchors) {
    lng0 += lng;
    lat0 += lat;
  }
  if (anchors.length > 0) {
    lng0 /= anchors.length;
    lat0 /= anchors.length;
  }
  const metresPerDegLng = METRES_PER_DEG_LNG_EQUATOR * Math.cos((lat0 * Math.PI) / 180);

  return buildable.map((zone, index) => {
    const context = legoArchetypeContextFromZone(zone.properties);
    const option = findCatalogOption(context.archetype_id);
    const centroid = centroids[index];
    const archetypeLabel = zone.properties?.development_archetype_label;
    return {
      zone,
      label:
        zone.name
        || option?.label
        || (typeof archetypeLabel === 'string' && archetypeLabel ? archetypeLabel : undefined)
        || normalizeArchetypeId(context.archetype_id)
        || zone.zone_type,
      archetypeId: normalizeArchetypeId(context.archetype_id),
      targets: deriveZoneTargets(option, zone.properties),
      // Negative z so north points away from the default camera.
      offset: centroid
        ? ([(centroid[0] - lng0) * metresPerDegLng, -(centroid[1] - lat0) * METRES_PER_DEG_LAT] as [number, number])
        : null,
    };
  });
}

function BuilderScene({ items }: { items: ZoneBuildItem[] }) {
  const placed = items.filter(
    (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan; offset: [number, number] } =>
      Boolean(item.plan && item.offset),
  );
  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight position={[8, 12, 7]} intensity={1.5} />
      <directionalLight position={[-8, 5, -6]} intensity={0.35} />
      {/* Neutral ground plane under the whole plan. */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <planeGeometry args={[4000, 4000]} />
        <meshStandardMaterial color="#262626" />
      </mesh>
      <Grid args={[600, 600]} cellSize={5} sectionSize={25} fadeDistance={500} />
      <Bounds fit clip observe margin={1.2}>
        <group>
          {placed.map((item) => (
            // Each assembly is stacked at the zone centroid without per-building
            // rotation — orienting modules to the parcel is a known v1 limitation.
            <group key={item.zone.id} position={[item.offset[0], 0, item.offset[1]]}>
              {item.plan.instances.map((instance, index) => (
                <ModuleInstance
                  key={`${item.zone.id}-${instance.asset_id}-${instance.level}-${index}`}
                  instance={instance}
                />
              ))}
            </group>
          ))}
        </group>
      </Bounds>
      <OrbitControls makeDefault enablePan />
    </>
  );
}

export function LegoBuilderPanel({ zones, onClose }: { zones: SiteZone[]; onClose: () => void }) {
  const [items, setItems] = useState<ZoneBuildItem[]>(() => deriveItems(zones));
  const [planning, setPlanning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const runBatch = useCallback(async () => {
    const base = deriveItems(zones);
    setItems(base);
    setSaveResult(null);
    if (base.length === 0) return;
    setPlanning(true);
    const results = await Promise.allSettled(
      base.map((item) =>
        legoAssemblyApi.plan({
          target_width_m: item.targets.width_m,
          target_depth_m: item.targets.depth_m,
          target_floors: item.targets.floors,
          allow_setback: true,
          ...legoArchetypeContextFromZone(item.zone.properties),
        }),
      ),
    );
    setItems(
      base.map((item, index) => {
        const result = results[index];
        if (result.status === 'fulfilled') return { ...item, plan: result.value };
        const status = (result.reason as { response?: { status?: number } })?.response?.status;
        return {
          ...item,
          error: getApiErrorMessage(result.reason, 'Could not assemble this zone.'),
          familyMissing: status === 422,
        };
      }),
    );
    setPlanning(false);
  }, [zones]);

  // Plan every buildable zone once when the panel opens; "Rebuild all" re-runs it.
  useEffect(() => {
    void runBatch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const assembledCount = items.filter((item) => item.plan).length;
  const noFamilyCount = items.filter((item) => item.familyMissing).length;
  const otherFailedCount = items.filter((item) => item.error && !item.familyMissing).length;
  const skippedCount = items.filter((item) => !item.offset).length;
  const placedCount = items.filter((item) => item.plan && item.offset).length;

  const missingArchetypeIds = useMemo(
    () => [...new Set(items.filter((item) => item.familyMissing).map((item) => item.archetypeId ?? '<archetype-id>'))],
    [items],
  );
  const hintCommands = missingArchetypeIds.map((id) => familyGenerationCommands(id)).join('\n');

  const savable = items.filter(
    (item): item is ZoneBuildItem & { plan: LegoAssemblyPlan } =>
      Boolean(item.plan && (item.zone.building_id ?? item.zone.building_ids?.[0])),
  );

  const handleSaveAll = async () => {
    if (savable.length === 0 || saving) return;
    setSaving(true);
    setSaveResult(null);
    const results = await Promise.allSettled(
      savable.map((item) => {
        const buildingId = (item.zone.building_id ?? item.zone.building_ids?.[0]) as string;
        const context = legoArchetypeContextFromZone(item.zone.properties);
        return legoAssemblyApi.saveRecipe(buildingId, {
          schema_version: 1,
          module_family: item.plan.family,
          archetype_id: item.plan.archetype_id ?? context.archetype_id ?? null,
          reuse_keys: item.plan.reuse_keys,
          target: item.plan.target,
          instances: item.plan.instances,
          assembled_height_m: item.plan.assembled_height_m,
          fit: item.plan.fit,
          assembled_preview_url: null,
        });
      }),
    );
    const savedCount = results.filter((result) => result.status === 'fulfilled').length;
    setSaveResult(`Saved ${savedCount} of ${savable.length} recipe${savable.length === 1 ? '' : 's'}`);
    setSaving(false);
  };

  const copyHintCommands = async () => {
    try {
      await navigator.clipboard.writeText(hintCommands);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard unavailable (e.g. insecure context) — the commands stay selectable.
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/75 p-4" onClick={onClose}>
      <div
        className="relative flex h-[88vh] w-[96vw] max-w-7xl overflow-hidden rounded-xl border-2 border-[#151515] bg-[#f7f7f1] shadow-[8px_8px_0_0_rgba(0,0,0,0.45)]"
        onClick={(event) => event.stopPropagation()}
      >
        <aside className="flex w-80 shrink-0 flex-col border-r-2 border-[#151515] bg-white">
          <div className="border-b-2 border-[#151515]/15 p-4 pb-3">
            <div className="mb-2 flex items-center gap-2">
              <Blocks className="h-5 w-5" />
              <h2 className="text-sm font-black uppercase">LEGO Builder</h2>
            </div>
            <p className="text-xs font-bold">
              {`Assembled ${assembledCount} · No family ${noFamilyCount} · Skipped ${skippedCount}`}
              {otherFailedCount > 0 ? ` · Failed ${otherFailedCount}` : ''}
            </p>
            {planning && (
              <p className="mt-1 flex items-center gap-1.5 text-[11px] text-black/55">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Assembling {items.length} zone{items.length === 1 ? '' : 's'}…
              </p>
            )}
          </div>

          <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-4 pt-3">
            {items.length === 0 && (
              <p className="text-xs text-black/55">
                No buildable zones in this plan yet — draw building zones or assign development archetypes first.
              </p>
            )}

            {items.map((item) => (
              <div
                key={item.zone.id}
                className={`rounded border-2 p-2 text-[11px] ${
                  item.error ? 'border-red-300 bg-red-50' : 'border-[#151515]/15 bg-white'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-bold" title={item.label}>{item.label}</span>
                  {item.plan && fitIsStretched(item.plan.fit) && (
                    <span className="flex shrink-0 items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-bold text-amber-800">
                      <AlertTriangle className="h-3 w-3" />
                      stretched
                    </span>
                  )}
                </div>
                {item.plan && (
                  <p className="mt-0.5 truncate text-black/60" title={item.plan.family}>
                    {item.plan.family} · fit {item.plan.fit.score.toFixed(2)}
                  </p>
                )}
                {item.error && (
                  <p className="mt-0.5 text-red-800">
                    {item.familyMissing && <span className="font-black uppercase">No family · </span>}
                    {item.error}
                  </p>
                )}
                {!item.plan && !item.error && planning && (
                  <p className="mt-0.5 text-black/50">Assembling…</p>
                )}
                {!item.offset && (
                  <p className="mt-0.5 text-black/50">No polygon coordinates — listed only, not placed in the scene.</p>
                )}
              </div>
            ))}

            {missingArchetypeIds.length > 0 && (
              <div className="rounded border border-red-300 bg-red-50 p-2 text-[11px] text-red-900">
                <p className="font-bold">
                  {missingArchetypeIds.length === 1
                    ? 'One archetype has no module family yet.'
                    : `${missingArchetypeIds.length} archetypes have no module family yet.`}
                </p>
                <p className="mt-1">Generate the families, then import their manifests:</p>
                <pre className="mt-1.5 select-all overflow-x-auto whitespace-pre-wrap break-all rounded bg-red-100 p-1.5 font-mono text-[10px] leading-relaxed">{hintCommands}</pre>
                <button
                  type="button"
                  onClick={copyHintCommands}
                  className="mt-1.5 flex items-center gap-1 rounded border border-red-400 bg-white px-2 py-0.5 text-[10px] font-bold text-red-800 hover:bg-red-100"
                >
                  {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  {copied ? 'Copied' : 'Copy commands'}
                </button>
              </div>
            )}
          </div>

          <div className="border-t-2 border-[#151515]/15 p-4 pt-3">
            {saveResult && (
              <p className="mb-2 rounded border-2 border-emerald-600 bg-emerald-50 p-2 text-[11px] font-bold text-emerald-800">
                {saveResult}
              </p>
            )}

            <button
              type="button"
              onClick={() => void runBatch()}
              disabled={planning || saving}
              className="flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {planning ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Rebuild all
            </button>

            <button
              type="button"
              onClick={() => void handleSaveAll()}
              disabled={savable.length === 0 || saving || planning}
              title={savable.length === 0
                ? 'No assembled zone has a generated building yet — generate buildings first, then save their recipes.'
                : 'Save every assembled zone as its building’s recipe.'}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-[#28c7e8] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] disabled:opacity-50"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save all recipes
            </button>

            <button
              type="button"
              onClick={onClose}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded border-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515]"
            >
              <X className="h-4 w-4" />
              Close
            </button>
          </div>
        </aside>

        <main className="relative min-w-0 flex-1 bg-[#1b1b1b]">
          <button
            type="button"
            onClick={onClose}
            className="absolute right-3 top-3 z-10 rounded bg-black/60 p-2 text-white hover:bg-black"
            aria-label="Close LEGO builder"
          >
            <X className="h-4 w-4" />
          </button>

          {placedCount > 0 ? (
            <Canvas camera={{ position: [110, 90, 150], fov: 42 }} dpr={[1, 2]}>
              <PreviewErrorBoundary>
                <Suspense fallback={<Progress />}>
                  <BuilderScene items={items} />
                </Suspense>
              </PreviewErrorBoundary>
            </Canvas>
          ) : (
            <div className="flex h-full items-center justify-center text-center text-white/55">
              <div>
                <Blocks className="mx-auto mb-3 h-10 w-10" />
                <p className="max-w-md text-sm font-bold">
                  {planning
                    ? 'Assembling the plan from LEGO modules…'
                    : items.length === 0
                      ? 'No buildable zones in this plan yet — draw building zones or assign archetypes first.'
                      : 'Nothing could be placed — see the zone list for details.'}
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>,
    document.body,
  );
}
