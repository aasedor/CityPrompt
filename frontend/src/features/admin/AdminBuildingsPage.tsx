import { useEffect, useState, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Search, ExternalLink, LayoutGrid, List, Sparkles, BookmarkPlus, ImageDown, Camera, Tag } from 'lucide-react';
import toast from 'react-hot-toast';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { adminApi, modelLibraryApi, resolveApiFileUrl } from '@/services/api';
import type { AdminBuilding } from '@/services/api';
import {
  BUILDING_AESTHETIC_OPTIONS_V2,
  BUILDING_AESTHETIC_CATEGORIES_V2,
} from '@/components/viewer/aestheticCatalog';

const STATUS_COLORS: Record<string, string> = {
  idle: 'bg-primary-950/[0.04] text-primary-950/60',
  generating: 'bg-amber-500/15 text-amber-600',
  completed: 'bg-green-500/15 text-green-600',
  failed: 'bg-red-500/15 text-red-600',
};

const ENGINE_LABELS: Record<string, string> = {
  meshy: 'Meshy.ai',
  tripo: 'Tripo3D',
  procedural: 'Procedural',
};

const THUMB_SIZE = 512;

/**
 * Render a GLB model to a PNG blob using an offscreen Three.js renderer.
 */
async function renderGlbThumbnail(glbUrl: string): Promise<Blob> {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setSize(THUMB_SIZE, THUMB_SIZE);
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f2f5);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(5, 8, 5);
  scene.add(dirLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
  fillLight.position.set(-3, 2, -3);
  scene.add(fillLight);

  // Load the model
  const loader = new GLTFLoader();
  const gltf = await new Promise<THREE.Group>((resolve, reject) => {
    loader.load(
      glbUrl,
      (result) => resolve(result.scene),
      undefined,
      reject,
    );
  });

  scene.add(gltf);

  // Compute bounding box and center/fit camera
  const box = new THREE.Box3().setFromObject(gltf);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, maxDim * 20);
  const distance = maxDim * 1.8;

  // Position camera at a nice 3/4 angle
  camera.position.set(
    center.x + distance * 0.7,
    center.y + distance * 0.5,
    center.z + distance * 0.7,
  );
  camera.lookAt(center);

  // Render
  renderer.render(scene, camera);

  // Extract as blob
  const canvas = renderer.domElement;
  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('toBlob failed'))), 'image/png');
  });

  // Cleanup
  renderer.dispose();
  scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.geometry.dispose();
      if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
      else obj.material.dispose();
    }
  });

  return blob;
}

export function AdminBuildingsPage() {
  const [buildings, setBuildings] = useState<AdminBuilding[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('completed');
  const [engineFilter, setEngineFilter] = useState('');
  const [viewMode, setViewMode] = useState<'gallery' | 'table'>('gallery');
  const [savingToLibrary, setSavingToLibrary] = useState<string | null>(null);
  const [renderProgress, setRenderProgress] = useState<{ current: number; total: number; name: string } | null>(null);
  const cancelRef = useRef(false);

  const fetchBuildings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminApi.listAllBuildings({
        search: search || undefined,
        status: statusFilter || undefined,
        engine: engineFilter || undefined,
        limit: 200,
      });
      setBuildings(data);
    } catch {
      toast.error('Failed to load buildings');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, engineFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchBuildings, 300);
    return () => clearTimeout(timer);
  }, [fetchBuildings]);

  const handleSaveToLibrary = async (b: AdminBuilding) => {
    setSavingToLibrary(b.id);
    try {
      const name = b.name || b.generation_prompt?.slice(0, 60) || 'Untitled Model';
      await modelLibraryApi.saveFromBuilding(b.id, name, b.generation_prompt || undefined);
      toast.success('Saved to model library!');
    } catch {
      toast.error('Failed to save to library');
    } finally {
      setSavingToLibrary(null);
    }
  };

  const handleRenderThumbnails = async () => {
    const missing = buildings.filter((b) => !b.preview_url && b.model_url && b.generation_status === 'completed');
    if (missing.length === 0) {
      toast.success('All buildings already have thumbnails!');
      return;
    }

    cancelRef.current = false;
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    let success = 0;
    let failed = 0;

    for (let i = 0; i < missing.length; i++) {
      if (cancelRef.current) {
        toast('Thumbnail rendering cancelled', { icon: '⏹' });
        break;
      }

      const b = missing[i];
      setRenderProgress({ current: i + 1, total: missing.length, name: b.name || 'Unnamed' });

      try {
        const modelUrl = `${apiBase}/api/v1/buildings/${b.id}/model/file`;
        const blob = await renderGlbThumbnail(modelUrl);
        await adminApi.uploadBuildingThumbnail(b.id, blob);

        // Update local state so the thumbnail shows immediately
        setBuildings((prev) =>
          prev.map((pb) =>
            pb.id === b.id ? { ...pb, preview_url: `/api/v1/files/projects/${b.project_id}/thumbnails/${b.id}.png` } : pb,
          ),
        );
        success++;
      } catch (err) {
        console.warn(`Failed to render thumbnail for ${b.id}:`, err);
        failed++;
      }
    }

    setRenderProgress(null);
    if (success > 0 || failed > 0) {
      toast.success(`Rendered ${success} thumbnail${success !== 1 ? 's' : ''}${failed > 0 ? `, ${failed} failed` : ''}`);
    }
  };

  const completedCount = buildings.length;
  const missingThumbnails = buildings.filter((b) => !b.preview_url && b.model_url && b.generation_status === 'completed').length;

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/admin" className="rounded-lg p-1.5 text-primary-950/50 hover:bg-primary-950/[0.04] hover:text-primary-950/70">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-primary-950">Generated Models</h1>
            <p className="text-sm text-primary-950/50">
              {loading ? 'Loading...' : `${completedCount} model${completedCount !== 1 ? 's' : ''} found`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {missingThumbnails > 0 && !renderProgress && (
            <button
              onClick={handleRenderThumbnails}
              className="flex items-center gap-1.5 rounded-lg border border-primary-500/30 bg-primary-500/10 px-3 py-1.5 text-xs font-medium text-primary-600 transition-colors hover:bg-primary-500/20"
            >
              <Camera size={14} />
              Render Thumbnails ({missingThumbnails})
            </button>
          )}
          {renderProgress && (
            <button
              onClick={() => { cancelRef.current = true; }}
              className="flex items-center gap-1.5 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-500/20"
            >
              Stop
            </button>
          )}
          <div className="flex items-center gap-1 rounded-lg border border-primary-950/[0.1] p-0.5">
            <button
              onClick={() => setViewMode('gallery')}
              className={`rounded-md p-1.5 ${viewMode === 'gallery' ? 'bg-primary-600 text-white' : 'text-primary-950/50 hover:text-primary-950'}`}
              title="Gallery view"
            >
              <LayoutGrid size={16} />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`rounded-md p-1.5 ${viewMode === 'table' ? 'bg-primary-600 text-white' : 'text-primary-950/50 hover:text-primary-950'}`}
              title="Table view"
            >
              <List size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Render progress bar */}
      {renderProgress && (
        <div className="mb-5 rounded-lg border border-primary-500/20 bg-primary-500/5 p-3">
          <div className="mb-1.5 flex items-center justify-between text-xs">
            <span className="font-medium text-primary-700">
              Rendering: {renderProgress.name} ({renderProgress.current}/{renderProgress.total})
            </span>
            <span className="text-primary-500">
              {Math.round((renderProgress.current / renderProgress.total) * 100)}%
            </span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-primary-500/10">
            <div
              className="h-full rounded-full bg-primary-500 transition-all duration-300"
              style={{ width: `${(renderProgress.current / renderProgress.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-5 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/50" />
          <input
            type="text"
            placeholder="Search by name, prompt, or project..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-primary-950/[0.1] bg-white py-2 pl-9 pr-3 text-sm text-primary-950 placeholder:text-primary-950/40 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-primary-950 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          <option value="">All statuses</option>
          <option value="completed">Completed</option>
          <option value="idle">Idle</option>
          <option value="generating">Generating</option>
          <option value="failed">Failed</option>
        </select>
        <select
          value={engineFilter}
          onChange={(e) => setEngineFilter(e.target.value)}
          className="rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-primary-950 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          <option value="">All engines</option>
          <option value="meshy">Meshy</option>
          <option value="tripo">Tripo</option>
          <option value="procedural">Procedural</option>
        </select>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : buildings.length === 0 ? (
        <div className="py-16 text-center">
          <Sparkles className="mx-auto mb-3 h-10 w-10 text-primary-950/20" />
          <p className="text-sm text-primary-950/50">No models found matching your filters.</p>
        </div>
      ) : viewMode === 'gallery' ? (
        <GalleryView
          buildings={buildings}
          onSaveToLibrary={handleSaveToLibrary}
          savingId={savingToLibrary}
          onArchetypeAssigned={(buildingId, _archetypeId, categoryId) => {
            setBuildings((prev) =>
              prev.map((b) =>
                b.id === buildingId
                  ? { ...b, architectural_style: categoryId }
                  : b,
              ),
            );
          }}
        />
      ) : (
        <TableView buildings={buildings} />
      )}
    </div>
  );
}

// Group archetypes by category for the dropdown
const CATEGORY_ARCHETYPES = (() => {
  const map: Record<string, { id: string; label: string }[]> = {};
  for (const opt of BUILDING_AESTHETIC_OPTIONS_V2) {
    const cat = opt.categoryId || 'other';
    if (!map[cat]) map[cat] = [];
    map[cat].push({ id: opt.id, label: opt.label });
  }
  return map;
})();

function ArchetypeAssigner({
  buildingId,
  onAssigned,
}: {
  buildingId: string;
  onAssigned: (archetypeId: string, categoryId: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [categoryId, setCategoryId] = useState('');
  const [archetypeId, setArchetypeId] = useState('');
  const [saving, setSaving] = useState(false);

  const archetypes = categoryId ? (CATEGORY_ARCHETYPES[categoryId] || []) : [];

  const handleSave = async () => {
    if (!archetypeId || !categoryId) return;
    setSaving(true);
    try {
      await adminApi.assignArchetype(buildingId, archetypeId, categoryId);
      toast.success('Archetype assigned!');
      onAssigned(archetypeId, categoryId);
      setOpen(false);
    } catch {
      toast.error('Failed to assign archetype');
    } finally {
      setSaving(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 rounded-md bg-primary-950/[0.04] px-2 py-1 text-[10px] font-medium text-primary-950/60 transition-colors hover:bg-primary-950/[0.08] hover:text-primary-950/80"
      >
        <Tag size={10} />
        Assign Archetype
      </button>
    );
  }

  return (
    <div className="mt-2 space-y-1.5 rounded-lg border border-primary-500/20 bg-primary-50/50 p-2">
      <select
        value={categoryId}
        onChange={(e) => {
          setCategoryId(e.target.value);
          setArchetypeId('');
        }}
        className="w-full rounded border border-primary-950/[0.1] bg-white px-2 py-1 text-[11px] text-primary-950 focus:border-primary-500 focus:outline-none"
      >
        <option value="">Select category...</option>
        {BUILDING_AESTHETIC_CATEGORIES_V2.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.label}
          </option>
        ))}
      </select>

      {categoryId && (
        <select
          value={archetypeId}
          onChange={(e) => setArchetypeId(e.target.value)}
          className="w-full rounded border border-primary-950/[0.1] bg-white px-2 py-1 text-[11px] text-primary-950 focus:border-primary-500 focus:outline-none"
        >
          <option value="">Select archetype...</option>
          {archetypes.map((a) => (
            <option key={a.id} value={a.id}>
              {a.label}
            </option>
          ))}
        </select>
      )}

      <div className="flex gap-1.5">
        <button
          onClick={handleSave}
          disabled={!archetypeId || saving}
          className="flex-1 rounded bg-primary-600 px-2 py-1 text-[10px] font-medium text-white transition-colors hover:bg-primary-700 disabled:opacity-40"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={() => setOpen(false)}
          className="rounded px-2 py-1 text-[10px] text-primary-950/50 hover:bg-primary-950/[0.04]"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function GalleryView({
  buildings,
  onSaveToLibrary,
  savingId,
  onArchetypeAssigned,
}: {
  buildings: AdminBuilding[];
  onSaveToLibrary: (b: AdminBuilding) => void;
  savingId: string | null;
  onArchetypeAssigned: (buildingId: string, archetypeId: string, categoryId: string) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {buildings.map((b) => (
        <div
          key={b.id}
          className="group overflow-hidden rounded-xl border border-primary-950/[0.08] bg-white shadow-sm transition-shadow hover:shadow-md"
        >
          {/* Preview image */}
          <div className="relative aspect-square bg-gradient-to-br from-primary-950/[0.02] to-primary-950/[0.06]">
            {b.preview_url ? (
              <img
                src={resolveApiFileUrl(b.preview_url)}
                alt={b.name || 'Building model'}
                className="h-full w-full object-cover"
              />
            ) : b.model_url ? (
              <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-primary-950/30">
                <Sparkles size={32} />
                <span className="text-xs">3D Model</span>
              </div>
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xs text-primary-950/20">
                No preview
              </div>
            )}

            {/* Status badge */}
            <div className="absolute left-2 top-2">
              <span
                className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize backdrop-blur-sm ${STATUS_COLORS[b.generation_status || 'idle'] || STATUS_COLORS.idle}`}
              >
                {b.generation_status || 'idle'}
              </span>
            </div>

            {/* Engine badge */}
            {b.generation_engine && (
              <div className="absolute right-2 top-2">
                <span className="inline-flex rounded-full bg-white/80 px-2 py-0.5 text-[10px] font-medium text-primary-950/70 backdrop-blur-sm">
                  {ENGINE_LABELS[b.generation_engine] || b.generation_engine}
                </span>
              </div>
            )}

            {/* Save to library button - appears on hover */}
            {b.model_url && b.generation_status === 'completed' && (
              <button
                onClick={() => onSaveToLibrary(b)}
                disabled={savingId === b.id}
                className="absolute bottom-2 right-2 flex items-center gap-1 rounded-lg bg-emerald-500/90 px-2.5 py-1 text-[10px] font-medium text-white opacity-0 backdrop-blur-sm transition-opacity hover:bg-emerald-600 group-hover:opacity-100 disabled:opacity-50"
              >
                {savingId === b.id ? (
                  <Loader2 size={10} className="animate-spin" />
                ) : (
                  <BookmarkPlus size={10} />
                )}
                Save to Library
              </button>
            )}
          </div>

          {/* Info */}
          <div className="p-3">
            <h3 className="truncate text-sm font-semibold text-primary-950">
              {b.name || 'Unnamed Building'}
            </h3>

            {b.generation_prompt && (
              <p className="mt-0.5 line-clamp-2 text-xs text-primary-950/50">
                {b.generation_prompt}
              </p>
            )}

            <div className="mt-2 flex items-center justify-between">
              <Link
                to={`/projects/${b.project_id}`}
                className="flex items-center gap-1 text-xs text-primary-500 hover:text-primary-600"
              >
                {b.project_name}
                <ExternalLink size={10} />
              </Link>
              <span className="text-[10px] text-primary-950/40">
                {new Date(b.created_at).toLocaleDateString()}
              </span>
            </div>

            {b.architectural_style && (
              <div className="mt-1.5">
                <span className="inline-flex rounded-full bg-primary-950/[0.04] px-2 py-0.5 text-[10px] capitalize text-primary-950/60">
                  {b.architectural_style.replace(/-/g, ' ')}
                </span>
              </div>
            )}

            <ArchetypeAssigner
              buildingId={b.id}
              onAssigned={(archetypeId, categoryId) => onArchetypeAssigned(b.id, archetypeId, categoryId)}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function TableView({ buildings }: { buildings: AdminBuilding[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-primary-950/[0.08]">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-primary-950/[0.08] bg-primary-950/[0.02] text-left text-xs font-medium uppercase text-primary-950/50">
            <th className="px-4 py-3">Preview</th>
            <th className="px-4 py-3">Building</th>
            <th className="px-4 py-3">Project</th>
            <th className="px-4 py-3">Owner</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Engine</th>
            <th className="px-4 py-3">Style</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-primary-950/[0.06]">
          {buildings.map((b) => (
            <tr key={b.id} className="hover:bg-primary-950/[0.02]">
              <td className="px-4 py-3">
                {b.preview_url ? (
                  <img
                    src={resolveApiFileUrl(b.preview_url)}
                    alt={b.name || 'Building'}
                    className="h-12 w-12 rounded-lg object-cover"
                  />
                ) : (
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-950/[0.04] text-xs text-primary-950/30">
                    N/A
                  </div>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="font-medium text-primary-950">{b.name || 'Unnamed'}</div>
                {b.generation_prompt && (
                  <p className="mt-0.5 truncate text-xs text-primary-950/50" style={{ maxWidth: 250 }}>
                    {b.generation_prompt}
                  </p>
                )}
              </td>
              <td className="px-4 py-3">
                <Link
                  to={`/projects/${b.project_id}`}
                  className="flex items-center gap-1 text-primary-500 hover:text-primary-600"
                >
                  {b.project_name}
                  <ExternalLink size={12} />
                </Link>
              </td>
              <td className="px-4 py-3 text-primary-950/50">{b.owner_email}</td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[b.generation_status || 'idle'] || STATUS_COLORS.idle}`}
                >
                  {b.generation_status || 'idle'}
                </span>
              </td>
              <td className="px-4 py-3">
                {b.generation_engine ? (
                  <span className="text-xs capitalize text-primary-950/70">
                    {ENGINE_LABELS[b.generation_engine] || b.generation_engine}
                  </span>
                ) : (
                  <span className="text-xs text-primary-950/30">-</span>
                )}
              </td>
              <td className="px-4 py-3">
                {b.architectural_style ? (
                  <span className="text-xs capitalize text-primary-950/70">{b.architectural_style.replace(/-/g, ' ')}</span>
                ) : (
                  <span className="text-xs text-primary-950/30">-</span>
                )}
              </td>
              <td className="px-4 py-3 text-primary-950/50">
                {new Date(b.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
