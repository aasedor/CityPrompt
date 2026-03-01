import { useState, useEffect, useRef } from 'react';
import { Trash2, Sparkles, Loader2, X, RefreshCw, Building2, Route, TreePine, Droplets, ParkingCircle, MapPin, LayoutGrid } from 'lucide-react';
import toast from 'react-hot-toast';
import type { SiteZone, SiteZoneProperties, Building, BoundaryAnalysisResponse, LayoutOption } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { siteZonesApi, buildingsApi } from '@/services/api';
import { useViewerStore } from '@/store';
import { LayoutPreviewPanel } from './LayoutPreviewPanel';

interface ZonePropertiesPanelProps {
  zone: SiteZone;
  onUpdate: (zoneId: string, data: { name?: string; properties?: SiteZoneProperties }) => void;
  onDelete: (zoneId: string) => void;
  onClose: () => void;
  onAIGenerate?: (buildingId: string, initialPrompt?: string) => void;
  buildings?: Building[];
  allZones?: SiteZone[];
}

export function ZonePropertiesPanel({ zone, onUpdate, onDelete, onClose, onAIGenerate, buildings, allZones }: ZonePropertiesPanelProps) {
  const config = ZONE_TYPE_CONFIG[zone.zone_type];
  const osmContext = useViewerStore((s) => s.osmContext);
  const layoutPreview = useViewerStore((s) => s.layoutPreview);
  const [name, setName] = useState(zone.name || '');
  const [props, setProps] = useState<SiteZoneProperties>(zone.properties || {});
  const panelRef = useRef<HTMLDivElement>(null);

  // Scroll panel to top when zone changes (e.g. after "Preview All" switches to buildable zone)
  useEffect(() => {
    panelRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [zone.id]);

  // Sync when zone changes — only on zone.id since key={zone.id} forces remount.
  // Do NOT depend on zone.properties — React Query background refetches would
  // overwrite the user's unsaved edits (e.g. reference images added but not yet saved).
  useEffect(() => {
    setName(zone.name || '');
    setProps(zone.properties || {});
  }, [zone.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = () => {
    onUpdate(zone.id, {
      name: name || undefined,
      properties: props,
    });
  };

  // Compute approximate area from coordinates (in square meters)
  const area = computePolygonAreaM2(zone.coordinates);

  return (
    <>
      {/* Backdrop overlay — mobile only */}
      <div
        className="fixed inset-0 z-20 bg-black/30 sm:hidden"
        onClick={onClose}
      />
      <div ref={panelRef} className="fixed inset-x-0 bottom-0 z-30 max-h-[70vh] w-full overflow-y-auto rounded-t-2xl bg-white/95 p-4 shadow-2xl backdrop-blur-sm sm:absolute sm:inset-auto sm:right-4 sm:top-16 sm:bottom-auto sm:left-auto sm:z-20 sm:w-80 sm:max-h-[calc(100%-5rem)] sm:rounded-xl">
        {/* Drag handle — mobile visual cue */}
        <div className="mb-3 flex justify-center sm:hidden">
          <div className="h-1 w-10 rounded-full bg-gray-300" />
        </div>
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
        {/* LAYOUT PREVIEW — shown at top when preview is active           */}
        {/* ============================================================= */}
        {layoutPreview?.zoneId === zone.id &&
          (zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') &&
          onAIGenerate && (
          <LayoutPreviewPanel
            zone={zone}
            onApplied={() => {}}
            onAIGenerate={onAIGenerate}
            referenceContext={osmContext}
            siblingZones={allZones?.filter((z) => z.id !== zone.id)}
          />
        )}

        {/* ============================================================= */}
        {/* SITE BOUNDARY — analysis + generate                           */}
        {/* ============================================================= */}
        {zone.zone_type === 'site_boundary' && (
          <SiteBoundarySection zone={zone} allZones={allZones} />
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
            <div>
              <label className="block text-xs text-gray-500">Sidewalks</label>
              <select
                value={
                  props.sidewalks === 'left' ? 'left'
                    : props.sidewalks === 'right' ? 'right'
                    : props.sidewalks === 'none' || props.has_sidewalks === false ? 'none'
                    : 'both'
                }
                onChange={(e) => setProps((p) => ({
                  ...p,
                  sidewalks: e.target.value,
                  has_sidewalks: e.target.value !== 'none',
                }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="both">Both Sides</option>
                <option value="left">Left Only</option>
                <option value="right">Right Only</option>
                <option value="none">None</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500">Road Surface</label>
              <select
                value={(props.road_surface as string) || 'asphalt'}
                onChange={(e) => setProps((p) => ({ ...p, road_surface: e.target.value }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              >
                <option value="asphalt">Asphalt</option>
                <option value="concrete">Concrete</option>
                <option value="cobblestone">Cobblestone</option>
                <option value="brick">Brick</option>
                <option value="paver">Paver</option>
                <option value="gravel">Gravel</option>
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
          <>
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
                <option value="institutional">Institutional</option>
                <option value="industrial">Industrial</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500">Target Units</label>
              <input
                type="number"
                min="2"
                max="100"
                step="1"
                value={(props.unit_count as number) ?? 10}
                onChange={(e) => setProps((p) => ({ ...p, unit_count: parseInt(e.target.value) || 2 }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
              <span className="text-[10px] text-gray-400">Number of buildings to generate within this development area</span>
            </div>
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
                value={props.height ?? ''}
                onChange={(e) => setProps((p) => ({ ...p, height: parseFloat(e.target.value) || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Floors</label>
              <input
                type="number"
                step="1"
                value={props.floors ?? ''}
                onChange={(e) => setProps((p) => ({ ...p, floors: parseInt(e.target.value) || undefined }))}
                className="mt-0.5 w-full rounded border border-gray-200 px-2 py-1 text-sm"
              />
            </div>
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
          </>
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

        {(zone.zone_type === 'building' || zone.zone_type === 'residential') && onAIGenerate && !zone.building_id && layoutPreview?.zoneId !== zone.id && (() => {
          const unitCount = Math.max(
            (props.unit_count as number) || 1,
            (() => {
              const desc = (props.description_text as string) || '';
              const m = desc.match(/(\d+)\s*(homes?|houses?|units?|buildings?|townhomes?|condos?)/i);
              return m ? parseInt(m[1]) : 0;
            })(),
            1,
          );
          if (unitCount > 1) {
            return (
              <LayoutPreviewPanel
                zone={zone}
                onApplied={() => {
                  // Refresh by triggering a re-fetch — the parent will pick up building_ids
                }}
                onAIGenerate={onAIGenerate}
                referenceContext={osmContext}
                siblingZones={allZones?.filter((z) => z.id !== zone.id)}
              />
            );
          }
          return <AIGenerateZoneButton zone={zone} onAIGenerate={onAIGenerate} />;
        })()}

        {/* Development Area Layout Preview */}
        {zone.zone_type === 'development_area' && onAIGenerate && !zone.building_id && layoutPreview?.zoneId !== zone.id && (() => {
          const unitCount = (props.unit_count as number) || 10;
          if (unitCount > 1) {
            return (
              <LayoutPreviewPanel
                zone={zone}
                onApplied={() => {}}
                onAIGenerate={onAIGenerate}
                referenceContext={osmContext}
                siblingZones={allZones?.filter((z) => z.id !== zone.id)}
              />
            );
          }
          return null;
        })()}

        {(zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') && onAIGenerate && zone.building_id && (
          <AIGenerateZoneButton zone={zone} onAIGenerate={onAIGenerate} />
        )}

        {/* Quick Regenerate — visible when zone already has a generated building */}
        {(zone.zone_type === 'building' || zone.zone_type === 'residential' || zone.zone_type === 'development_area') && zone.building_id && (() => {
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
    </>
  );
}

// =============================================================================
// Site Boundary Section
// =============================================================================

const ZONE_TYPE_ICONS: Record<string, typeof Building2> = {
  building: Building2,
  residential: Building2,
  road: Route,
  green_space: TreePine,
  water: Droplets,
  parking: ParkingCircle,
  development_area: MapPin,
};

/** Capture two screenshots from the Mapbox map: satellite-only and with zones drawn */
async function captureMapScreenshots(
  mapInstance: unknown,
  boundaryCoords?: number[][],
  allZones?: SiteZone[],
): Promise<{ satellite: string; withZones: string } | null> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const map = mapInstance as any;
  if (!map || typeof map.getCanvas !== 'function') return null;

  const ZONE_LAYERS = [
    'site-zones-fill', 'site-zones-outline', 'site-zones-selected',
    'site-zones-labels', 'zone-edit-vertices-layer',
    'drawing-preview-fill', 'drawing-preview-line',
  ];

  /** Wait for the map to finish rendering after a change */
  const waitForIdle = (): Promise<void> =>
    new Promise((resolve) => {
      const onIdle = () => resolve();
      if (map.isMoving() || map.isZooming()) {
        map.once('idle', onIdle);
      } else {
        map.once('render', () => resolve());
        map.triggerRepaint();
      }
    });

  try {
    // 0. Fit the map EXACTLY to the inner zones — zero padding.
    //    Gemini receives ONLY the development area filling the entire frame.
    const innerZones = (allZones || []).filter((z) => z.zone_type !== 'site_boundary');
    const cropCoords = innerZones.length > 0
      ? innerZones.flatMap((z) => z.coordinates || [])
      : boundaryCoords || [];

    if (cropCoords.length > 0) {
      let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
      for (const [lng, lat] of cropCoords) {
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
      }
      // Zero expand — the zones should fill the entire frame
      map.fitBounds(
        [[minLng, minLat], [maxLng, maxLat]],
        { padding: 10, animate: false },
      );
      await waitForIdle();
    }

    // 1. Hide ALL zone layers and capture clean satellite of just the development area
    const prevVisibility: Record<string, string> = {};
    for (const layerId of ZONE_LAYERS) {
      try {
        prevVisibility[layerId] = map.getLayoutProperty(layerId, 'visibility') || 'visible';
        map.setLayoutProperty(layerId, 'visibility', 'none');
      } catch { /* layer might not exist */ }
    }
    await waitForIdle();

    // 2. Pixel-crop the canvas to exactly the zone bounding box.
    //    fitBounds respects the canvas aspect ratio, so if zones are portrait
    //    but the canvas is landscape, there's wasted space on the sides.
    //    We solve this by projecting zone coords to pixels and cropping.
    let satellite: string;
    const mapCanvas = map.getCanvas();
    if (cropCoords.length > 0) {
      let pxMinX = Infinity, pxMaxX = -Infinity, pxMinY = Infinity, pxMaxY = -Infinity;
      for (const [lng, lat] of cropCoords) {
        const pt = map.project([lng, lat]);
        if (pt.x < pxMinX) pxMinX = pt.x;
        if (pt.x > pxMaxX) pxMaxX = pt.x;
        if (pt.y < pxMinY) pxMinY = pt.y;
        if (pt.y > pxMaxY) pxMaxY = pt.y;
      }
      // Add a tiny margin (2% of zone dimensions) so edges aren't cut off
      const marginX = (pxMaxX - pxMinX) * 0.02;
      const marginY = (pxMaxY - pxMinY) * 0.02;
      pxMinX = Math.max(0, pxMinX - marginX);
      pxMinY = Math.max(0, pxMinY - marginY);
      pxMaxX = Math.min(mapCanvas.width, pxMaxX + marginX);
      pxMaxY = Math.min(mapCanvas.height, pxMaxY + marginY);

      const cropW = Math.round(pxMaxX - pxMinX);
      const cropH = Math.round(pxMaxY - pxMinY);

      // Account for devicePixelRatio — canvas pixels != CSS pixels
      const dpr = window.devicePixelRatio || 1;
      const offscreen = document.createElement('canvas');
      offscreen.width = Math.round(cropW * dpr);
      offscreen.height = Math.round(cropH * dpr);
      const ctx = offscreen.getContext('2d')!;
      ctx.drawImage(
        mapCanvas,
        Math.round(pxMinX * dpr), Math.round(pxMinY * dpr),
        offscreen.width, offscreen.height,
        0, 0,
        offscreen.width, offscreen.height,
      );
      satellite = offscreen.toDataURL('image/jpeg', 0.92);
    } else {
      satellite = mapCanvas.toDataURL('image/jpeg', 0.92);
    }

    // 3. Restore zone layers
    for (const layerId of ZONE_LAYERS) {
      try {
        map.setLayoutProperty(layerId, 'visibility', prevVisibility[layerId] || 'visible');
      } catch { /* ignore */ }
    }

    return { satellite, withZones: satellite };
  } catch (e) {
    console.warn('Failed to capture map screenshots:', e);
    return null;
  }
}

function SiteBoundarySection({ zone, allZones }: { zone: SiteZone; allZones?: SiteZone[] }) {
  const [analysis, setAnalysis] = useState<BoundaryAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [previewingAll, setPreviewingAll] = useState(false);
  const [renderingIndices, setRenderingIndices] = useState<Set<number>>(new Set());
  const autoRenderTriggered = useRef(false);
  const mapScreenshotsRef = useRef<{ satellite: string; withZones: string } | null>(null);
  const selectZone = useViewerStore((s) => s.selectZone);
  const mapInstance = useViewerStore((s) => s.mapInstance);
  const {
    sitePreview, setSitePreview, clearSitePreview,
    setActiveSitePreviewIndex, setSitePreviewImageUrl,
    setLightboxImage,
    clearLockedLayers,
  } = useViewerStore();

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    siteZonesApi.getBoundaryAnalysis(zone.id)
      .then((data) => { if (!cancelled) setAnalysis(data); })
      .catch(() => { if (!cancelled) setAnalysis(null); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [zone.id]);

  const isSitePreviewActive = sitePreview?.boundaryZoneId === zone.id;
  const siteOptions = isSitePreviewActive ? sitePreview!.zoneLayouts : {};
  const siteImageUrls = isSitePreviewActive ? sitePreview!.imageUrls : {};
  const siteActiveIndex = isSitePreviewActive ? sitePreview!.activeIndex : 0;

  // Figure out how many option sets we have (max across zones, typically 3)
  const optionCount = Object.values(siteOptions).reduce(
    (max, opts) => Math.max(max, opts.length), 0
  );

  // Auto-render site previews after layout generation
  useEffect(() => {
    if (!isSitePreviewActive || optionCount === 0 || autoRenderTriggered.current) return;
    const allRendered = Array.from({ length: optionCount }, (_, i) => i).every((i) => siteImageUrls[i]);
    if (allRendered) return;

    autoRenderTriggered.current = true;
    for (let idx = 0; idx < optionCount; idx++) {
      if (siteImageUrls[idx]) continue;
      renderSiteOption(idx);
    }
  }, [isSitePreviewActive, optionCount]); // eslint-disable-line react-hooks/exhaustive-deps

  // Reset auto-render flag when zone changes
  useEffect(() => {
    autoRenderTriggered.current = false;
  }, [zone.id]);

  const renderSiteOption = async (idx: number) => {
    setRenderingIndices((prev) => new Set(prev).add(idx));
    try {
      // Build a map of zoneId → chosen option for this index
      const zoneLayoutsForOption: Record<string, LayoutOption> = {};
      for (const [zid, opts] of Object.entries(siteOptions)) {
        if (opts[idx]) {
          zoneLayoutsForOption[zid] = opts[idx];
        }
      }
      // Build zone metadata (color, name, type) for Gemini prompt context
      const zoneMeta: Record<string, { color: string; name: string; zone_type: string }> = {};
      if (allZones) {
        for (const z of allZones) {
          if (z.id !== zone.id) { // skip the boundary itself
            zoneMeta[z.id] = {
              color: z.color,
              name: z.name || ZONE_TYPE_CONFIG[z.zone_type as keyof typeof ZONE_TYPE_CONFIG]?.label || z.zone_type,
              zone_type: z.zone_type,
            };
          }
        }
      }
      const result = await siteZonesApi.renderSitePreview(
        zone.id, idx, zoneLayoutsForOption,
        mapScreenshotsRef.current || undefined,
        Object.keys(zoneMeta).length > 0 ? zoneMeta : undefined,
      );
      setSitePreviewImageUrl(idx, result.image_url);
    } catch {
      // Silently fail — we'll show a placeholder
    } finally {
      setRenderingIndices((prev) => {
        const next = new Set(prev);
        next.delete(idx);
        return next;
      });
    }
  };

  const handlePreviewAll = async () => {
    if (!analysis) return;
    const buildableZones = analysis.contained_zones.filter(
      (z) => z.zone_type === 'building' || z.zone_type === 'residential' || z.zone_type === 'development_area'
    );
    if (buildableZones.length === 0) return;

    // Capture map screenshots BEFORE anything changes
    mapScreenshotsRef.current = await captureMapScreenshots(mapInstance, zone.coordinates, allZones);

    setPreviewingAll(true);
    autoRenderTriggered.current = false;
    try {
      // Run all zone previews in parallel
      const results = await Promise.allSettled(
        buildableZones.map((cz) => siteZonesApi.previewLayouts(cz.id))
      );
      // Collect all zone layouts into a single map
      const allZoneLayouts: Record<string, LayoutOption[]> = {};
      let generated = 0;
      for (let i = 0; i < results.length; i++) {
        if (results[i].status === 'fulfilled') {
          const res = (results[i] as PromiseFulfilledResult<{ options: LayoutOption[] }>).value;
          allZoneLayouts[buildableZones[i].id] = res.options;
          generated++;
        }
      }
      clearLockedLayers();
      if (generated > 0) {
        // Store site-wide preview — stay on boundary
        setSitePreview(zone.id, allZoneLayouts);
        toast.success(`Generated layouts for ${generated} zone${generated > 1 ? 's' : ''} — rendering site previews...`);
      } else {
        toast.error('No layout previews could be generated');
      }
    } catch {
      toast.error('Failed to generate layout previews');
    } finally {
      setPreviewingAll(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      // Auto-apply any active site preview selections before generating
      if (isSitePreviewActive) {
        let appliedCount = 0;
        const applyResults = await Promise.all(
          Object.entries(siteOptions).map(async ([zoneId, options]) => {
            if (!options[siteActiveIndex]) return null;
            try {
              await siteZonesApi.applyLayout(zoneId, siteActiveIndex, options[siteActiveIndex]);
              return zoneId;
            } catch (e) {
              console.warn(`Failed to apply layout for zone ${zoneId}:`, e);
              return null;
            }
          })
        );
        appliedCount = applyResults.filter(Boolean).length;
        clearSitePreview();
        clearLockedLayers();
        if (appliedCount > 0) {
          toast.success(`Applied ${appliedCount} previewed layout${appliedCount > 1 ? 's' : ''}`);
        }
      }

      const result = await siteZonesApi.generateForBoundary(zone.project_id, zone.id);
      toast.success(
        `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
      );
    } catch {
      toast.error('Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <Loader2 size={12} className="animate-spin" />
        Analyzing boundary...
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-xs text-gray-400 italic">
        Could not analyze boundary contents.
      </div>
    );
  }

  const hasZones = analysis.total_contained > 0;
  const buildableTypes = ['building', 'residential', 'development_area'];
  const buildableZones = analysis.contained_zones.filter(
    (z) => buildableTypes.includes(z.zone_type)
  );
  const hasBuildableZones = buildableZones.length > 0;
  const osmBuildings = analysis.osm_context?.buildings;
  const osmRoads = analysis.osm_context?.roads;
  const hasOsm = (osmBuildings?.count ?? 0) > 0 || (osmRoads?.count ?? 0) > 0;

  const renderingCount = renderingIndices.size;

  return (
    <div className="space-y-2">
      {/* Contained zones — clickable to select */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Contained Zones ({analysis.total_contained})
        </label>
        {hasZones ? (
          <div className="space-y-0.5">
            {analysis.contained_zones.map((cz) => {
              const config = ZONE_TYPE_CONFIG[cz.zone_type as keyof typeof ZONE_TYPE_CONFIG];
              const Icon = ZONE_TYPE_ICONS[cz.zone_type] || MapPin;
              const isBuildable = buildableTypes.includes(cz.zone_type);
              return (
                <button
                  key={cz.id}
                  onClick={() => selectZone(cz.id)}
                  className={`flex w-full items-center gap-2 rounded px-1.5 py-1 text-xs text-left transition-colors ${
                    isBuildable
                      ? 'text-gray-700 hover:bg-indigo-50 cursor-pointer'
                      : 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                  }`}
                  title={isBuildable ? 'Click to edit & preview layout' : 'Click to edit zone'}
                >
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: cz.color || config?.color || '#999' }}
                  />
                  <Icon size={11} className="text-gray-400 flex-shrink-0" />
                  <span className="truncate">{cz.name || config?.label || cz.zone_type}</span>
                  {isBuildable && (
                    <span className="ml-auto text-[10px] text-indigo-400 flex-shrink-0">edit</span>
                  )}
                </button>
              );
            })}
          </div>
        ) : (
          <div className="text-xs text-gray-400 italic">
            No zones inside this boundary. Draw zones within the boundary to get started.
          </div>
        )}
      </div>

      {/* OSM Infrastructure */}
      {hasOsm && (
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Nearby Infrastructure (OSM)
          </label>
          <div className="space-y-0.5 text-xs text-gray-500">
            {osmBuildings?.count ? (
              <div className="flex items-center gap-1.5">
                <Building2 size={10} />
                <span>{osmBuildings.count} existing buildings</span>
                {osmBuildings.avg_height ? (
                  <span className="text-gray-400">(avg {osmBuildings.avg_height.toFixed(0)}m)</span>
                ) : null}
              </div>
            ) : null}
            {osmRoads?.count ? (
              <div className="flex items-center gap-1.5">
                <Route size={10} />
                <span>{osmRoads.count} existing roads</span>
                {osmRoads.named_roads?.length ? (
                  <span className="text-gray-400 truncate">
                    ({osmRoads.named_roads.slice(0, 3).join(', ')})
                  </span>
                ) : null}
              </div>
            ) : null}
          </div>
          <p className="mt-0.5 text-[10px] text-gray-400">
            Real-world data from OpenStreetMap used for context
          </p>
        </div>
      )}

      {/* Step 1: Preview 2D Layouts */}
      {hasBuildableZones && !isSitePreviewActive && (
        <div className="space-y-1.5">
          <label className="block text-xs font-medium text-gray-600">
            Step 1: Preview 2D Layouts
          </label>
          <button
            onClick={handlePreviewAll}
            disabled={previewingAll}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            title="Generate AI 2D layout options for each buildable zone"
          >
            {previewingAll ? <Loader2 size={12} className="animate-spin" /> : <LayoutGrid size={12} />}
            {previewingAll ? 'Generating previews...' : `Preview Layouts (${buildableZones.length} zone${buildableZones.length > 1 ? 's' : ''})`}
          </button>
          <p className="text-[10px] text-gray-400 text-center">
            AI generates comprehensive site layout options — one image per option
          </p>
        </div>
      )}

      {/* Site-wide preview options */}
      {isSitePreviewActive && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-700">Site Layout Options</span>
            <div className="flex items-center gap-2">
              {renderingCount > 0 && (
                <span className="flex items-center gap-1 text-[10px] text-purple-500">
                  <Loader2 size={9} className="animate-spin" />
                  Rendering {renderingCount}...
                </span>
              )}
              <button
                onClick={() => { autoRenderTriggered.current = false; handlePreviewAll(); }}
                disabled={previewingAll}
                className="flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] text-indigo-600 hover:bg-indigo-50"
                title="Regenerate all options"
              >
                <RefreshCw size={10} className={previewingAll ? 'animate-spin' : ''} />
                Regenerate
              </button>
            </div>
          </div>

          {/* Option cards */}
          {Array.from({ length: optionCount }, (_, idx) => {
            const isActive = idx === siteActiveIndex;
            const imageUrl = siteImageUrls[idx];
            const isRendering = renderingIndices.has(idx);
            // Collect stats for this option across all zones
            let totalBuildings = 0;
            let totalRoads = 0;
            let totalGreen = 0;
            for (const opts of Object.values(siteOptions)) {
              if (opts[idx]) {
                totalBuildings += opts[idx].buildings.length;
                totalRoads += opts[idx].roads.length;
                totalGreen += opts[idx].green_spaces.length;
              }
            }
            // Get label from first zone's option
            const firstOpts = Object.values(siteOptions)[0];
            const label = firstOpts?.[idx]?.option_label || `Option ${idx + 1}`;
            const reasoning = firstOpts?.[idx]?.reasoning || '';

            return (
              <div
                key={idx}
                onClick={() => setActiveSitePreviewIndex(idx)}
                className={`w-full cursor-pointer rounded-lg border p-2 text-left transition-all ${
                  isActive
                    ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-xs font-semibold ${isActive ? 'text-indigo-700' : 'text-gray-700'}`}>
                    {label}
                  </span>
                  <span className="text-[10px] text-gray-400">
                    {totalBuildings} buildings, {totalRoads} roads, {totalGreen} green
                  </span>
                </div>

                {imageUrl ? (
                  <div className="relative">
                    <img
                      src={imageUrl}
                      alt={`Site layout option ${idx + 1}`}
                      className="w-full rounded cursor-zoom-in"
                      onClick={(e) => { e.stopPropagation(); setLightboxImage(imageUrl); }}
                    />
                    <button
                      onClick={(e) => { e.stopPropagation(); renderSiteOption(idx); }}
                      className="absolute bottom-1 right-1 rounded bg-black/50 p-1 text-white/80 hover:bg-black/70 hover:text-white"
                      title="Re-render preview"
                    >
                      <RefreshCw size={10} />
                    </button>
                  </div>
                ) : isRendering ? (
                  <div className="flex h-[160px] items-center justify-center rounded bg-gray-100">
                    <div className="flex flex-col items-center gap-1.5">
                      <Loader2 size={16} className="animate-spin text-purple-400" />
                      <span className="text-[9px] text-gray-400">Rendering site preview...</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex h-[80px] items-center justify-center rounded bg-gray-100">
                    <span className="text-[10px] text-gray-400">Waiting to render...</span>
                  </div>
                )}

                <p className="mt-0.5 text-[10px] leading-tight text-gray-500 line-clamp-2">
                  {reasoning}
                </p>
              </div>
            );
          })}

          {/* Expanded active option */}
          {siteImageUrls[siteActiveIndex] && (
            <div className="rounded-lg border border-indigo-200 bg-indigo-50/30 p-2">
              <img
                src={siteImageUrls[siteActiveIndex]}
                alt="Selected site layout"
                className="w-full rounded cursor-zoom-in"
                onClick={() => setLightboxImage(siteImageUrls[siteActiveIndex])}
              />
              <p className="mt-1 text-[10px] text-center text-gray-400">Click image to expand</p>
            </div>
          )}

          <button
            onClick={() => { clearSitePreview(); clearLockedLayers(); }}
            className="w-full rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50"
          >
            Cancel Preview
          </button>
        </div>
      )}

      {/* Step 2: Generate 3D */}
      {hasBuildableZones && (
        <div className="space-y-1.5">
          <label className="block text-xs font-medium text-gray-600">
            {isSitePreviewActive ? 'Step 2: ' : ''}Generate 3D Models
          </label>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50"
            title="Generate 3D models for zones within this boundary"
          >
            {generating ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
            {generating ? 'Generating...' : 'Generate 3D Neighborhood'}
          </button>
        </div>
      )}

      {!hasBuildableZones && hasZones && (
        <p className="text-[10px] text-gray-400 text-center">
          Add building or residential zones inside the boundary to generate
        </p>
      )}
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
            placeholder="Paste image URL and press Enter"
            className="flex-1 rounded border border-gray-200 px-2 py-1 text-xs"
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd(); } }}
          />
          <button
            onClick={handleAdd}
            disabled={!url.trim()}
            className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200 disabled:opacity-40"
          >
            Add
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
