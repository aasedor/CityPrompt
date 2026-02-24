import { useState, useEffect } from 'react';
import { Trash2, Sparkles, Loader2, Plus, X, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZone, SiteZoneProperties, Building } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { siteZonesApi, buildingsApi } from '@/services/api';

interface ZonePropertiesPanelProps {
  zone: SiteZone;
  onUpdate: (zoneId: string, data: { name?: string; properties?: SiteZoneProperties }) => void;
  onDelete: (zoneId: string) => void;
  onClose: () => void;
  onAIGenerate?: (buildingId: string, initialPrompt?: string) => void;
  buildings?: Building[];
}

export function ZonePropertiesPanel({ zone, onUpdate, onDelete, onClose, onAIGenerate, buildings }: ZonePropertiesPanelProps) {
  const config = ZONE_TYPE_CONFIG[zone.zone_type];
  const [name, setName] = useState(zone.name || '');
  const [props, setProps] = useState<SiteZoneProperties>(zone.properties || {});

  // Sync when zone changes
  useEffect(() => {
    setName(zone.name || '');
    setProps(zone.properties || {});
  }, [zone.id, zone.name, zone.properties]);

  const handleSave = () => {
    onUpdate(zone.id, {
      name: name || undefined,
      properties: props,
    });
  };

  // Compute approximate area from coordinates (in square meters)
  const area = computePolygonAreaM2(zone.coordinates);

  return (
    <div className="absolute right-4 top-16 z-20 w-80 max-h-[calc(100vh-6rem)] overflow-y-auto rounded-xl bg-white/95 p-4 shadow-2xl backdrop-blur-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-4 w-4 rounded"
            style={{ backgroundColor: zone.color }}
          />
          <h3 className="text-sm font-semibold text-gray-900">{config?.label || zone.zone_type}</h3>
        </div>
        <button
          onClick={onClose}
          className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
        >
          <X size={14} />
        </button>
      </div>

      <div className="mt-3 space-y-2.5 text-sm">
        {/* Name */}
        <div>
          <label className="block text-xs text-gray-500">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={config?.label || 'Zone'}
            className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
          />
        </div>

        {/* Area display */}
        <div className="flex justify-between">
          <span className="text-xs text-gray-500">Area</span>
          <span className="text-xs font-medium text-gray-700">
            {area >= 10000
              ? `${(area / 10000).toFixed(2)} ha`
              : `${Math.round(area).toLocaleString()} m\u00B2`}
          </span>
        </div>

        {/* ============================================================= */}
        {/* SITE BOUNDARY — minimal properties                            */}
        {/* ============================================================= */}
        {zone.zone_type === 'site_boundary' && (
          <div className="text-xs text-gray-400 italic">
            Site boundary outline. No additional properties.
          </div>
        )}

        {/* ============================================================= */}
        {/* BUILDING / RESIDENTIAL                                         */}
        {/* ============================================================= */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && (
          <>
            {/* Development Type */}
            <div>
              <label className="block text-xs text-gray-500">Development Type</label>
              <select
                value={(props.development_type as string) || ''}
                onChange={(e) => setProps((p) => ({ ...p, development_type: e.target.value || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="">-- Select --</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="mixed_use">Mixed Use</option>
                <option value="park_plaza">Park / Plaza</option>
                <option value="institutional">Institutional</option>
                <option value="industrial">Industrial</option>
                <option value="other">Other</option>
              </select>
            </div>
            {/* Development Aesthetic */}
            <div>
              <label className="block text-xs text-gray-500">Development Aesthetic</label>
              <select
                value={(props.development_aesthetic as string) || ''}
                onChange={(e) => setProps((p) => ({ ...p, development_aesthetic: e.target.value || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="">-- Select --</option>
                <option value="historic_traditional">Historic / Traditional</option>
                <option value="modern">Modern</option>
                <option value="futuristic">Futuristic</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500">Height (m)</label>
              <input
                type="number"
                step="1"
                value={props.height ?? config?.defaultProperties.height ?? ''}
                onChange={(e) => setProps((p) => ({ ...p, height: parseFloat(e.target.value) || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Floors</label>
              <input
                type="number"
                step="1"
                value={props.floors ?? config?.defaultProperties.floors ?? ''}
                onChange={(e) => setProps((p) => ({ ...p, floors: parseInt(e.target.value) || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Facade Material</label>
              <select
                value={(props.facade_material as string) || 'concrete'}
                onChange={(e) => setProps((p) => ({ ...p, facade_material: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="glass">Glass</option>
                <option value="brick">Brick</option>
                <option value="concrete">Concrete</option>
                <option value="stone">Stone</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500">Roof Style</label>
              <select
                value={(props.roof_style as string) || 'flat'}
                onChange={(e) => setProps((p) => ({ ...p, roof_style: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="flat">Flat</option>
                <option value="gabled">Gabled</option>
                <option value="hip">Hip</option>
              </select>
            </div>
          </>
        )}

        {zone.zone_type === 'residential' && (
          <>
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500">Balconies</label>
              <input
                type="checkbox"
                checked={!!props.balconies}
                onChange={(e) => setProps((p) => ({ ...p, balconies: e.target.checked }))}
                className="rounded border-gray-300"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Unit Count</label>
              <input
                type="number"
                min="1"
                max="50"
                step="1"
                value={(props.unit_count as number) ?? 1}
                onChange={(e) => setProps((p) => ({ ...p, unit_count: parseInt(e.target.value) || 1 }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
              <span className="text-[10px] text-gray-400">Number of buildings to generate within this zone</span>
            </div>
          </>
        )}

        {/* ============================================================= */}
        {/* GREEN SPACE                                                    */}
        {/* ============================================================= */}
        {zone.zone_type === 'green_space' && (
          <>
            <div>
              <label className="block text-xs text-gray-500">Tree Density</label>
              <select
                value={(props.tree_density_level as string) || 'medium'}
                onChange={(e) => setProps((p) => ({ ...p, tree_density_level: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="sparse">Sparse</option>
                <option value="medium">Medium</option>
                <option value="dense">Dense</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500">Tree Density Value (0-1)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={props.tree_density ?? config?.defaultProperties.tree_density ?? 0.3}
                onChange={(e) => setProps((p) => ({ ...p, tree_density: parseFloat(e.target.value) || 0 }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500">Has Benches</label>
              <input
                type="checkbox"
                checked={!!props.has_benches}
                onChange={(e) => setProps((p) => ({ ...p, has_benches: e.target.checked }))}
                className="rounded border-gray-300"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500">Has Paths</label>
              <input
                type="checkbox"
                checked={!!props.has_paths}
                onChange={(e) => setProps((p) => ({ ...p, has_paths: e.target.checked }))}
                className="rounded border-gray-300"
              />
            </div>
          </>
        )}

        {/* ============================================================= */}
        {/* ROAD                                                           */}
        {/* ============================================================= */}
        {zone.zone_type === 'road' && (
          <>
            {/* Roadway Aesthetic */}
            <div>
              <label className="block text-xs text-gray-500">Roadway Aesthetic</label>
              <select
                value={(props.road_aesthetic as string) || ''}
                onChange={(e) => setProps((p) => ({ ...p, road_aesthetic: e.target.value || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="">-- Select --</option>
                <option value="grand_boulevard">Grand Boulevard</option>
                <option value="pedestrian_focused">Pedestrian Focused</option>
                <option value="water_centric">Water Centric</option>
                <option value="curvilinear_residential">Curvilinear Residential</option>
                <option value="neighborhood_high_street">Neighborhood High Street</option>
                <option value="industrial_collector">Industrial Collector</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Mode Priority */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mode Priority (1-4 rank)</label>
              <div className="grid grid-cols-2 gap-x-3 gap-y-1.5">
                <div>
                  <label className="block text-xs text-gray-500">Pedestrian</label>
                  <input
                    type="number"
                    min="1"
                    max="4"
                    placeholder="--"
                    value={(props.priority_pedestrian as number) ?? ''}
                    onChange={(e) => setProps((p) => ({ ...p, priority_pedestrian: e.target.value ? parseInt(e.target.value) : undefined }))}
                    className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Cycling</label>
                  <input
                    type="number"
                    min="1"
                    max="4"
                    placeholder="--"
                    value={(props.priority_cycling as number) ?? ''}
                    onChange={(e) => setProps((p) => ({ ...p, priority_cycling: e.target.value ? parseInt(e.target.value) : undefined }))}
                    className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Transit</label>
                  <input
                    type="number"
                    min="1"
                    max="4"
                    placeholder="--"
                    value={(props.priority_transit as number) ?? ''}
                    onChange={(e) => setProps((p) => ({ ...p, priority_transit: e.target.value ? parseInt(e.target.value) : undefined }))}
                    className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Automobiles</label>
                  <input
                    type="number"
                    min="1"
                    max="4"
                    placeholder="--"
                    value={(props.priority_auto as number) ?? ''}
                    onChange={(e) => setProps((p) => ({ ...p, priority_auto: e.target.value ? parseInt(e.target.value) : undefined }))}
                    className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Volume */}
            <div>
              <label className="block text-xs text-gray-500">Volume</label>
              <select
                value={(props.volume as string) || ''}
                onChange={(e) => setProps((p) => ({ ...p, volume: e.target.value || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="">-- Select --</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-500">Width (m)</label>
              <input
                type="number"
                step="1"
                value={props.width ?? config?.defaultProperties.width ?? 10}
                onChange={(e) => setProps((p) => ({ ...p, width: parseFloat(e.target.value) || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Lane Count</label>
              <input
                type="number"
                step="1"
                min="1"
                max="6"
                value={(props.lane_count as number) ?? 2}
                onChange={(e) => setProps((p) => ({ ...p, lane_count: parseInt(e.target.value) || 2 }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500">Has Sidewalks</label>
              <input
                type="checkbox"
                checked={props.has_sidewalks !== false}
                onChange={(e) => setProps((p) => ({ ...p, has_sidewalks: e.target.checked }))}
                className="rounded border-gray-300"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Road Surface</label>
              <select
                value={(props.road_surface as string) || 'asphalt'}
                onChange={(e) => setProps((p) => ({ ...p, road_surface: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="asphalt">Asphalt</option>
                <option value="cobblestone">Cobblestone</option>
              </select>
            </div>
          </>
        )}

        {/* ============================================================= */}
        {/* PARKING                                                        */}
        {/* ============================================================= */}
        {zone.zone_type === 'parking' && (
          <>
            <div>
              <label className="block text-xs text-gray-500">Parking Layout</label>
              <select
                value={(props.parking_layout as string) || 'perpendicular'}
                onChange={(e) => setProps((p) => ({ ...p, parking_layout: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="angled">Angled</option>
                <option value="perpendicular">Perpendicular</option>
                <option value="parallel">Parallel</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500">Covered</label>
              <input
                type="checkbox"
                checked={!!props.covered}
                onChange={(e) => setProps((p) => ({ ...p, covered: e.target.checked }))}
                className="rounded border-gray-300"
              />
            </div>
          </>
        )}

        {/* ============================================================= */}
        {/* WATER                                                          */}
        {/* ============================================================= */}
        {zone.zone_type === 'water' && (
          <div>
            <label className="block text-xs text-gray-500">Water Type</label>
            <select
              value={(props.water_type as string) || 'pond'}
              onChange={(e) => setProps((p) => ({ ...p, water_type: e.target.value }))}
              className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
            >
              <option value="pond">Pond</option>
              <option value="stream">Stream</option>
              <option value="fountain">Fountain</option>
            </select>
          </div>
        )}

        {/* ============================================================= */}
        {/* DEVELOPMENT AREA                                               */}
        {/* ============================================================= */}
        {zone.zone_type === 'development_area' && (
          <div>
            <label className="block text-xs text-gray-500">Ground Texture</label>
            <select
              value={(props.ground_texture as string) || 'grass'}
              onChange={(e) => setProps((p) => ({ ...p, ground_texture: e.target.value }))}
              className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
            >
              <option value="grass">Grass</option>
              <option value="concrete">Concrete</option>
              <option value="gravel">Gravel</option>
              <option value="dirt">Dirt</option>
            </select>
          </div>
        )}

        {/* ============================================================= */}
        {/* SHARED: Descriptive Text (all zone types except site_boundary) */}
        {/* ============================================================= */}
        {zone.zone_type !== 'site_boundary' && (
          <div>
            <label className="block text-xs text-gray-500">Descriptive Text</label>
            <textarea
              value={(props.description_text as string) || ''}
              onChange={(e) => setProps((p) => ({ ...p, description_text: e.target.value || undefined }))}
              placeholder="E.g. Make the trees maple trees. Use cobblestone for the sidewalk."
              rows={2}
              className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm resize-none"
            />
          </div>
        )}

        {/* ============================================================= */}
        {/* SHARED: Reference Images (all zone types except site_boundary) */}
        {/* ============================================================= */}
        {zone.zone_type !== 'site_boundary' && (
          <ReferenceImagesSection
            images={(props.reference_images as string[]) || []}
            onChange={(imgs) => setProps((p) => ({ ...p, reference_images: imgs.length > 0 ? imgs : undefined }))}
          />
        )}

        <button
          onClick={handleSave}
          className="mt-1 w-full rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700"
        >
          Save Changes
        </button>

        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && onAIGenerate && (
          <AIGenerateZoneButton zone={zone} onAIGenerate={onAIGenerate} />
        )}

        {/* Quick Regenerate — visible when zone already has a generated building */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && zone.building_id && (() => {
          const linkedBuilding = buildings?.find((b) => b.id === zone.building_id);
          if (!linkedBuilding || linkedBuilding.generation_status !== 'completed') return null;
          return (
            <QuickRegenerateSection
              building={linkedBuilding}
            />
          );
        })()}

        <button
          onClick={() => onDelete(zone.id)}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100"
        >
          <Trash2 size={12} />
          Delete Zone
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Reference Images sub-component
// =============================================================================

function ReferenceImagesSection({
  images,
  onChange,
}: {
  images: string[];
  onChange: (imgs: string[]) => void;
}) {
  const [url, setUrl] = useState('');

  const handleAdd = () => {
    const trimmed = url.trim();
    if (!trimmed) return;
    if (images.length >= 3) return;
    onChange([...images, trimmed]);
    setUrl('');
  };

  const handleRemove = (idx: number) => {
    onChange(images.filter((_, i) => i !== idx));
  };

  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">Reference Images</label>
      {/* Thumbnails */}
      {images.length > 0 && (
        <div className="flex gap-1.5 mb-1.5 flex-wrap">
          {images.map((imgUrl, idx) => (
            <div key={idx} className="relative group w-16 h-16 rounded border border-gray-200 overflow-hidden bg-gray-100">
              <img
                src={imgUrl}
                alt={`Ref ${idx + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
              <button
                onClick={() => handleRemove(idx)}
                className="absolute top-0 right-0 bg-red-500 text-white rounded-bl p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X size={10} />
              </button>
            </div>
          ))}
        </div>
      )}
      {/* Add input */}
      {images.length < 3 && (
        <div className="flex gap-1">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Image URL..."
            className="flex-1 rounded border border-gray-200 px-2 py-1 text-xs"
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd(); } }}
          />
          <button
            onClick={handleAdd}
            disabled={!url.trim()}
            className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600 hover:bg-gray-200 disabled:opacity-40"
          >
            <Plus size={12} />
          </button>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Quick Regenerate section
// =============================================================================

function QuickRegenerateSection({ building }: { building: Building }) {
  const [prompt, setPrompt] = useState(building.generation_prompt || '');
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    setPrompt(building.generation_prompt || '');
  }, [building.generation_prompt]);

  const handleRegenerate = async () => {
    if (!prompt.trim()) return;
    setRegenerating(true);
    try {
      await buildingsApi.generate(building.id, prompt.trim());
      toast.success('Regeneration started');
    } catch {
      toast.error('Regeneration failed');
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div className="rounded-lg border border-purple-200 bg-purple-50/50 p-2.5">
      <label className="mb-1 block text-[11px] font-medium text-purple-700">Regenerate with modified prompt</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        className="mb-1.5 w-full rounded border border-purple-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-purple-400 focus:outline-none"
      />
      <button
        onClick={handleRegenerate}
        disabled={regenerating || !prompt.trim()}
        className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-purple-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-600 disabled:opacity-50"
      >
        {regenerating ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
        {regenerating ? 'Regenerating...' : 'Regenerate'}
      </button>
    </div>
  );
}

// =============================================================================
// AI Generate button
// =============================================================================

function AIGenerateZoneButton({ zone, onAIGenerate }: { zone: SiteZone; onAIGenerate: (buildingId: string, initialPrompt?: string) => void }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const building = await siteZonesApi.createBuildingFromZone(zone.id);
      const prompt = composeZonePrompt(zone);
      onAIGenerate(building.id, prompt);
    } catch {
      // Error will be shown in the AI modal
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50"
    >
      {loading ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
      {loading ? 'Creating...' : 'AI Generate 3D'}
    </button>
  );
}

/**
 * Compose a rich AI generation prompt from zone properties.
 * Mirrors the backend compose_zone_prompt logic.
 */
function composeZonePrompt(zone: SiteZone): string {
  const props = zone.properties || {};
  const parts: string[] = [];

  // Determine unit count from properties or description text
  let unitCount = (props.unit_count as number) || 1;
  const descText = (props.description_text as string) || '';
  const unitMatch = descText.match(/(\d+)\s*(homes?|houses?|units?|buildings?|townhomes?|condos?)/i);
  if (unitMatch) {
    const parsed = parseInt(unitMatch[1]);
    if (parsed > unitCount) unitCount = parsed;
  }

  // 1. Building type + aesthetic
  const aesthetic = ((props.development_aesthetic as string) || '').replace(/_/g, ' ').trim();
  const devType = ((props.development_type as string) || zone.zone_type).replace(/_/g, ' ');
  const typeLabel = devType.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  if (unitCount > 1) {
    if (aesthetic) {
      const aestheticLabel = aesthetic.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
      parts.push(`A single ${aestheticLabel} ${typeLabel} home suitable for a neighborhood of ${unitCount} homes`);
    } else {
      parts.push(`A single ${typeLabel} home suitable for a neighborhood of ${unitCount} homes`);
    }
  } else if (aesthetic) {
    const aestheticLabel = aesthetic.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    parts.push(`A ${aestheticLabel} ${typeLabel} building`);
  } else {
    parts.push(`A ${typeLabel} building`);
  }

  // 2. Approximate dimensions from coordinates
  if (zone.coordinates.length >= 3) {
    const area = computePolygonAreaM2(zone.coordinates);
    if (area > 1) {
      // Approximate bounding box dimensions
      const centerLat = zone.coordinates.reduce((s, c) => s + c[1], 0) / zone.coordinates.length;
      const metersPerDegLat = 111320;
      const metersPerDegLon = metersPerDegLat * Math.cos((centerLat * Math.PI) / 180);
      const lngs = zone.coordinates.map(c => c[0]);
      const lats = zone.coordinates.map(c => c[1]);
      const width = (Math.max(...lngs) - Math.min(...lngs)) * metersPerDegLon;
      const depth = (Math.max(...lats) - Math.min(...lats)) * metersPerDegLat;
      if (width > 1 && depth > 1) {
        parts.push(`Building footprint approximately ${width.toFixed(0)}m wide by ${depth.toFixed(0)}m deep (${area.toFixed(0)} sq meters)`);
      }
    }
  }

  // 3. Height / floors
  const floors = props.floors as number | undefined;
  const height = props.height as number | undefined;
  const floorHeight = (props.floor_height as number) || 3;
  if (floors && height) {
    parts.push(`${floors} stories tall (${height}m total height), each floor ${floorHeight}m high`);
  } else if (floors) {
    const total = floors * floorHeight;
    parts.push(`${floors} stories tall (${total}m total height), each floor ${floorHeight}m high`);
  }

  // 4. Facade material + roof style
  const facade = props.facade_material as string | undefined;
  const roof = props.roof_style as string | undefined;
  if (facade && roof) {
    parts.push(`${facade} facade material, ${roof} roof style`);
  } else if (facade) {
    parts.push(`${facade} facade material`);
  } else if (roof) {
    parts.push(`${roof} roof style`);
  }

  // 5. User description text
  const desc = props.description_text as string | undefined;
  if (desc) {
    parts.push(desc);
  }

  // 6. Quality directives
  if (unitCount > 1) {
    parts.push(
      'Realistic architectural style with detailed facade, visible windows, ' +
      'entrance doors, and appropriate material textures. ' +
      'Suitable for close-up walkthrough viewing. ' +
      'Single standalone unit, no surrounding buildings or landscape, no background or ground plane.'
    );
  } else {
    parts.push(
      'Realistic architectural style with detailed facade, visible windows, ' +
      'entrance doors, and appropriate material textures. ' +
      'Suitable for close-up walkthrough viewing. ' +
      'Single standalone building, no background or ground plane.'
    );
  }

  return parts.join('. ');
}

/**
 * Compute area of a polygon given in [lng, lat] coordinates.
 * Uses the Shoelace formula projected to meters.
 */
function computePolygonAreaM2(coords: number[][]): number {
  if (coords.length < 3) return 0;

  // Approximate center for projection
  const centerLat = coords.reduce((s, c) => s + c[1], 0) / coords.length;
  const metersPerDegLat = 111320;
  const metersPerDegLon = metersPerDegLat * Math.cos((centerLat * Math.PI) / 180);

  // Convert to meters
  const mCoords = coords.map((c) => [c[0] * metersPerDegLon, c[1] * metersPerDegLat]);

  // Shoelace
  let area = 0;
  for (let i = 0; i < mCoords.length; i++) {
    const j = (i + 1) % mCoords.length;
    area += mCoords[i][0] * mCoords[j][1];
    area -= mCoords[j][0] * mCoords[i][1];
  }
  return Math.abs(area) / 2;
}
