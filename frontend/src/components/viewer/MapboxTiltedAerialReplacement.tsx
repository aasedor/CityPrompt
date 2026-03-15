/**
 * MapboxTiltedAerialReplacement — Oblique aerial 3D massing map with AI render overlay.
 *
 * Shows site zones as 3D extruded buildings on a satellite basemap at an
 * oblique camera angle (Google Earth–style site study view). Includes the
 * AIRenderPanel for generating photorealistic renders via fal.ai FLUX.1 Depth
 * that are composited back as a raster overlay pinned to geographic bounds.
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type { SiteZone } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { AIRenderPanel } from './AIRenderPanel';
import ViewpointRenderPanel from './ViewpointRenderPanel';
import type { AIRenderResult } from './useAIRender';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

const AI_RENDER_SOURCE_ID = 'ai-render-overlay';
const AI_RENDER_LAYER_ID = 'ai-render-overlay-layer';

// Ground texture colors for development_area zones
const GROUND_TEXTURE_COLORS: Record<string, string> = {
  grass: '#7cba3f',
  concrete: '#b0b0b0',
  gravel: '#a0958a',
  dirt: '#8b7355',
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface MapboxTiltedAerialReplacementProps {
  /** Project center [lng, lat] */
  center?: [number, number];
  /** Starting zoom level */
  zoom?: number;
  /** Starting pitch (degrees) — default 60 for oblique aerial */
  pitch?: number;
  /** Starting bearing (degrees) */
  bearing?: number;
  /** Site zones to render as 3D massing + ground fills */
  siteZones?: SiteZone[];
  /** Whether to show the AI render panel — default true */
  showAIPanel?: boolean;
  /** Whether to show the viewpoint street render panel — default true */
  showViewpointPanel?: boolean;
  /** Optional callback when the map is ready */
  onMapReady?: (map: mapboxgl.Map) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function MapboxTiltedAerialReplacement({
  center,
  zoom = 16,
  pitch = 60,
  bearing = -30,
  siteZones = [],
  showAIPanel = true,
  showViewpointPanel = true,
  onMapReady,
}: MapboxTiltedAerialReplacementProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedRenderStyle, setSelectedRenderStyle] = useState('modern-glass');
  const [viewMode, setViewMode] = useState<'massing' | 'render'>('massing');
  const [hasOverlay, setHasOverlay] = useState(false);
  const siteZonesRef = useRef(siteZones);
  siteZonesRef.current = siteZones;

  // Track whether zone layers have been added
  const zoneLayersAddedRef = useRef(false);

  // ─── Map initialisation ───────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current || !MAPBOX_TOKEN) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: center || [-114.07, 51.045],
      zoom,
      pitch,
      bearing,
      antialias: true,
      preserveDrawingBuffer: true, // Required for canvas screenshot capture
      attributionControl: false,
      maxPitch: 85, // Allow street-level pitch (62°+) for viewpoint renders
    });

    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'top-left');
    mapRef.current = map;

    map.on('style.load', () => {
      // Add 3D terrain for realism
      if (!map.getSource('mapbox-dem')) {
        map.addSource('mapbox-dem', {
          type: 'raster-dem',
          url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
          tileSize: 512,
          maxzoom: 14,
        });
        map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.2 });
      }

      // Add sky + fog for aerial atmosphere
      map.setFog({
        color: 'rgb(186, 210, 235)',
        'high-color': 'rgb(36, 92, 223)',
        'horizon-blend': 0.02,
        'star-intensity': 0.0,
        'space-color': 'rgb(11, 11, 25)',
      });

      setMapLoaded(true);
      onMapReady?.(map);
    });

    return () => {
      mapRef.current = null;
      zoneLayersAddedRef.current = false;
      setMapLoaded(false);
      map.remove();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ─── Build zone GeoJSON and sync to map ───────────────────────────────
  const syncZoneLayers = useCallback((map: mapboxgl.Map, zones: SiteZone[]) => {
    // Remove existing zone layers
    removeZoneLayers(map);

    if (!zones.length) {
      zoneLayersAddedRef.current = false;
      return;
    }

    // Classify features
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const extrudedFeatures: any[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fillFeatures: any[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const roadFeatures: any[] = [];

    for (const zone of zones) {
      if (!zone.coordinates || zone.coordinates.length < 2) continue;

      if (zone.zone_type === 'road') {
        // Extract centerline from road polygon
        const coords = zone.coordinates;
        const n = coords.length;
        const half = Math.floor(n / 2);
        const centerline: number[][] = [];
        for (let i = 0; i < half; i++) {
          const opposite = n - 1 - i;
          if (opposite >= 0 && opposite < n) {
            centerline.push([
              (coords[i][0] + coords[opposite][0]) / 2,
              (coords[i][1] + coords[opposite][1]) / 2,
            ]);
          }
        }
        if (centerline.length >= 2) {
          roadFeatures.push({
            type: 'Feature',
            properties: {
              id: zone.id,
              width: zone.properties?.width || 10,
              color: zone.color || '#444444',
            },
            geometry: { type: 'LineString', coordinates: centerline },
          });
        }
      } else if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
        const ring = closeRing(zone.coordinates);
        extrudedFeatures.push({
          type: 'Feature',
          properties: {
            id: zone.id,
            height: zone.properties?.height || (zone.zone_type === 'building' ? 30 : 12),
            base_height: 0,
            color: zone.color || ZONE_TYPE_CONFIG[zone.zone_type]?.color || '#9b59b6',
            type: zone.zone_type,
          },
          geometry: { type: 'Polygon', coordinates: [ring] },
        });
      } else {
        const ring = closeRing(zone.coordinates);
        let zoneColor = zone.color || ZONE_TYPE_CONFIG[zone.zone_type]?.color || '#95a5a6';
        if (zone.zone_type === 'development_area') {
          const texture = (zone.properties?.ground_texture as string) || 'grass';
          zoneColor = GROUND_TEXTURE_COLORS[texture] || GROUND_TEXTURE_COLORS.grass;
        }
        fillFeatures.push({
          type: 'Feature',
          properties: { id: zone.id, color: zoneColor, type: zone.zone_type },
          geometry: { type: 'Polygon', coordinates: [ring] },
        });
      }
    }

    try {
      // Extruded buildings (3D massing)
      if (extrudedFeatures.length > 0) {
        map.addSource('tz-extruded', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: extrudedFeatures },
        });
        map.addLayer({
          id: 'tz-extruded-layer',
          type: 'fill-extrusion',
          source: 'tz-extruded',
          paint: {
            'fill-extrusion-color': ['get', 'color'],
            'fill-extrusion-height': ['get', 'height'],
            'fill-extrusion-base': ['get', 'base_height'],
            'fill-extrusion-opacity': 0.9,
            'fill-extrusion-vertical-gradient': true,
          },
        });
      }

      // Ground fill zones
      if (fillFeatures.length > 0) {
        map.addSource('tz-fill', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: fillFeatures },
        });
        map.addLayer({
          id: 'tz-fill-layer',
          type: 'fill',
          source: 'tz-fill',
          paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.55 },
        });
        map.addLayer({
          id: 'tz-fill-outline',
          type: 'line',
          source: 'tz-fill',
          paint: { 'line-color': ['get', 'color'], 'line-width': 2, 'line-opacity': 0.8 },
        });
      }

      // Roads
      if (roadFeatures.length > 0) {
        map.addSource('tz-roads', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: roadFeatures },
        });
        // Road surface
        map.addLayer({
          id: 'tz-road-surface',
          type: 'line',
          source: 'tz-roads',
          paint: { 'line-color': '#3a3a3a', 'line-width': ['get', 'width'], 'line-opacity': 0.85 },
          layout: { 'line-cap': 'round', 'line-join': 'round' },
        });
        // Centerline dashes
        map.addLayer({
          id: 'tz-road-center',
          type: 'line',
          source: 'tz-roads',
          paint: { 'line-color': '#ffffff', 'line-width': 1, 'line-dasharray': [4, 4], 'line-opacity': 0.7 },
        });
      }

      zoneLayersAddedRef.current = true;
    } catch (err) {
      console.warn('[MapboxTiltedAerial] Failed to add zone layers:', err);
    }
  }, []);

  // Sync zones when data or map readiness changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;
    syncZoneLayers(map, siteZones);
  }, [siteZones, mapLoaded, syncZoneLayers]);

  // ─── AI Render Overlay ────────────────────────────────────────────────

  const applyAIRenderOverlay = useCallback((result: AIRenderResult) => {
    const map = mapRef.current;
    if (!map) return;

    // Remove existing overlay
    removeOverlayLayer(map);

    try {
      map.addSource(AI_RENDER_SOURCE_ID, {
        type: 'image',
        url: result.imageUrl,
        coordinates: result.bounds,
      });

      // Insert the raster layer below the extrusion layer if it exists,
      // or at the top of the stack
      const beforeLayer = map.getLayer('tz-extruded-layer') ? 'tz-extruded-layer' : undefined;

      map.addLayer(
        {
          id: AI_RENDER_LAYER_ID,
          type: 'raster',
          source: AI_RENDER_SOURCE_ID,
          paint: {
            'raster-opacity': 0.95,
            'raster-fade-duration': 500,
          },
        },
        beforeLayer,
      );

      setHasOverlay(true);
      setViewMode('render');

      // Hide extrusions when in render mode
      if (map.getLayer('tz-extruded-layer')) {
        map.setLayoutProperty('tz-extruded-layer', 'visibility', 'none');
      }
    } catch (err) {
      console.warn('[MapboxTiltedAerial] Failed to add AI render overlay:', err);
    }
  }, []);

  const clearAIRenderOverlay = useCallback(() => {
    const map = mapRef.current;
    if (map) {
      removeOverlayLayer(map);
      // Restore extrusions
      if (map.getLayer('tz-extruded-layer')) {
        map.setLayoutProperty('tz-extruded-layer', 'visibility', 'visible');
      }
    }
    setHasOverlay(false);
    setViewMode('massing');
  }, []);

  // Toggle between massing and render view modes
  const toggleViewMode = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const newMode = viewMode === 'massing' ? 'render' : 'massing';
    setViewMode(newMode);

    if (newMode === 'render') {
      // Show overlay, hide extrusions
      if (map.getLayer(AI_RENDER_LAYER_ID)) {
        map.setLayoutProperty(AI_RENDER_LAYER_ID, 'visibility', 'visible');
      }
      if (map.getLayer('tz-extruded-layer')) {
        map.setLayoutProperty('tz-extruded-layer', 'visibility', 'none');
      }
    } else {
      // Hide overlay, show extrusions
      if (map.getLayer(AI_RENDER_LAYER_ID)) {
        map.setLayoutProperty(AI_RENDER_LAYER_ID, 'visibility', 'none');
      }
      if (map.getLayer('tz-extruded-layer')) {
        map.setLayoutProperty('tz-extruded-layer', 'visibility', 'visible');
      }
    }
  }, [viewMode]);

  // ─── Render ───────────────────────────────────────────────────────────

  if (!MAPBOX_TOKEN) {
    return (
      <div className="relative flex h-full w-full items-center justify-center bg-gray-900 text-gray-400 text-sm">
        Set VITE_MAPBOX_TOKEN in your .env file to enable the map
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <div ref={containerRef} className="h-full w-full" />

      {/* Massing / Render toggle — only visible when an overlay exists */}
      {hasOverlay && (
        <div className="absolute left-1/2 top-4 z-40 -translate-x-1/2">
          <div className="flex rounded-lg bg-gray-900/90 p-0.5 shadow-lg backdrop-blur-sm">
            <button
              onClick={viewMode === 'massing' ? undefined : toggleViewMode}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                viewMode === 'massing'
                  ? 'bg-white/15 text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Massing
            </button>
            <button
              onClick={viewMode === 'render' ? undefined : toggleViewMode}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                viewMode === 'render'
                  ? 'bg-amber-500/20 text-amber-300'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Render
            </button>
          </div>
        </div>
      )}

      {showAIPanel && (
        <AIRenderPanel
          mapRef={mapRef}
          onRenderComplete={applyAIRenderOverlay}
          onClearOverlay={clearAIRenderOverlay}
          siteZones={siteZones}
          onStyleChange={setSelectedRenderStyle}
        />
      )}

      {showViewpointPanel && (
        <ViewpointRenderPanel
          map={mapRef.current}
          renderStyleId={selectedRenderStyle}
          siteZones={siteZones}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Ensure a coordinate ring is closed (first == last) */
function closeRing(coords: number[][]): number[][] {
  const ring = coords.map((c) => [c[0], c[1]]);
  if (ring.length >= 3) {
    const first = ring[0];
    const last = ring[ring.length - 1];
    if (first[0] !== last[0] || first[1] !== last[1]) {
      ring.push([first[0], first[1]]);
    }
  }
  return ring;
}

/** Zone layer + source IDs used by this component */
const ZONE_LAYER_IDS = [
  'tz-road-center',
  'tz-road-surface',
  'tz-fill-outline',
  'tz-fill-layer',
  'tz-extruded-layer',
];
const ZONE_SOURCE_IDS = ['tz-roads', 'tz-fill', 'tz-extruded'];

function removeZoneLayers(map: mapboxgl.Map) {
  for (const id of ZONE_LAYER_IDS) {
    try { if (map.getLayer(id)) map.removeLayer(id); } catch { /* ok */ }
  }
  for (const id of ZONE_SOURCE_IDS) {
    try { if (map.getSource(id)) map.removeSource(id); } catch { /* ok */ }
  }
}

function removeOverlayLayer(map: mapboxgl.Map) {
  try { if (map.getLayer(AI_RENDER_LAYER_ID)) map.removeLayer(AI_RENDER_LAYER_ID); } catch { /* ok */ }
  try { if (map.getSource(AI_RENDER_SOURCE_ID)) map.removeSource(AI_RENDER_SOURCE_ID); } catch { /* ok */ }
}
