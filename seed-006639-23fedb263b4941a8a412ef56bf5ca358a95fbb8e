import { useMemo, useState } from 'react';
import { ChevronDown, ChevronUp, Eye, EyeOff, Layers, Loader2, Trash2 } from 'lucide-react';
import type { SiteZone } from '@/types';

interface LayerInfo {
  name: string;
  zones: SiteZone[];
  color: string;
}

interface LayersPanelProps {
  siteZones: SiteZone[];
  hiddenLayers: Set<string>;
  onToggleLayer: (name: string) => void;
  onDeleteLayer: (name: string) => void | Promise<void>;
  deletingLayer?: string | null;
}

/**
 * Lists imported shapefile "layers" (zones grouped by `properties._imported_from`)
 * with per-layer show/hide and delete. Renders nothing when no layers exist.
 */
export function LayersPanel({
  siteZones,
  hiddenLayers,
  onToggleLayer,
  onDeleteLayer,
  deletingLayer,
}: LayersPanelProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const layers: LayerInfo[] = useMemo(() => {
    const map = new Map<string, SiteZone[]>();
    for (const z of siteZones) {
      const src = z.properties?._imported_from;
      if (typeof src === 'string' && src) {
        const arr = map.get(src) ?? [];
        arr.push(z);
        map.set(src, arr);
      }
    }
    return Array.from(map.entries()).map(([name, zones]) => ({
      name,
      zones,
      color: zones[0]?.color ?? '#888888',
    }));
  }, [siteZones]);

  if (layers.length === 0) return null;

  return (
    <div className="pointer-events-auto w-72 max-w-[calc(100vw-2rem)] overflow-hidden rounded-xl border-2 border-[#151515] bg-white shadow-[4px_4px_0_0_#151515]">
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="flex w-full items-center justify-between gap-2 bg-[#151515] px-3 py-2 text-left text-white"
      >
        <span className="flex items-center gap-2 text-sm font-black uppercase">
          <Layers size={15} /> Imported Layers ({layers.length})
        </span>
        {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
      </button>

      {!collapsed && (
        <ul className="max-h-[50vh] divide-y divide-gray-200 overflow-y-auto">
          {layers.map(({ name, zones, color }) => {
            const hidden = hiddenLayers.has(name);
            const isDeleting = deletingLayer === name;
            const isConfirming = confirmDelete === name;
            return (
              <li key={name} className="flex items-center gap-2 px-3 py-2">
                <button
                  onClick={() => onToggleLayer(name)}
                  title={hidden ? 'Show layer' : 'Hide layer'}
                  className="shrink-0 text-gray-600 transition hover:text-[#151515]"
                >
                  {hidden ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
                <span
                  className="h-3 w-3 shrink-0 rounded-sm border border-black/30"
                  style={{ backgroundColor: color, opacity: hidden ? 0.4 : 1 }}
                />
                <span
                  className={`min-w-0 flex-1 truncate text-xs ${hidden ? 'text-gray-400 line-through' : 'text-gray-900'}`}
                  title={name}
                >
                  {name} <span className="text-gray-400">· {zones.length}</span>
                </span>

                {isConfirming ? (
                  <span className="flex shrink-0 items-center gap-1">
                    <button
                      onClick={() => {
                        setConfirmDelete(null);
                        void onDeleteLayer(name);
                      }}
                      disabled={isDeleting}
                      className="rounded bg-red-600 px-1.5 py-0.5 text-[10px] font-bold uppercase text-white hover:bg-red-700"
                    >
                      {isDeleting ? <Loader2 size={11} className="animate-spin" /> : 'Delete'}
                    </button>
                    <button
                      onClick={() => setConfirmDelete(null)}
                      className="text-[10px] uppercase text-gray-500 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                  </span>
                ) : (
                  <button
                    onClick={() => setConfirmDelete(name)}
                    disabled={isDeleting}
                    title="Delete layer"
                    className="shrink-0 text-gray-400 transition hover:text-red-600"
                  >
                    {isDeleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
