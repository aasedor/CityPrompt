import { useEffect, useRef, useCallback, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type { SiteZone, SiteZoneType, SiteZoneProperties } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';
import { useViewerStore } from '@/store';
import { useUndoRedoStore } from '@/store/undoRedo';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

// Zone types that are drawn as a line path (buffered into a polygon on finish)
const LINEAR_ZONE_TYPES: SiteZoneType[] = ['road'];

function isLinearTool(tool: SiteZoneType | null): boolean {
  return tool != null && LINEAR_ZONE_TYPES.includes(tool);
}

/**
 * Haversine distance between two [lng, lat] points in meters.
 */
function haversineDistance(a: number[], b: number[]): number {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const R = 6371000;
  const dLat = toRad(b[1] - a[1]);
  const dLon = toRad(b[0] - a[0]);
  const sinLat = Math.sin(dLat / 2);
  const sinLon = Math.sin(dLon / 2);
  const h = sinLat * sinLat + Math.cos(toRad(a[1])) * Math.cos(toRad(b[1])) * sinLon * sinLon;
  return 2 * R * Math.asin(Math.sqrt(h));
}

/** Total polyline length in meters */
function polylineLength(pts: number[][]): number {
  let total = 0;
  for (let i = 1; i < pts.length; i++) {
    total += haversineDistance(pts[i - 1], pts[i]);
  }
  return total;
}

/** Format meters into a human-readable string */
function formatDistance(meters: number): string {
  if (meters < 1000) return `${Math.round(meters)} m`;
  return `${(meters / 1000).toFixed(2)} km`;
}

/**
 * Catmull-Rom spline interpolation for smooth road curves.
 * Takes raw waypoints and returns a denser set of smoothly interpolated points.
 */
function smoothPolyline(points: number[][], segmentsPerSpan = 8): number[][] {
  if (points.length < 3) return points;

  const result: number[][] = [points[0]];

  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[Math.max(0, i - 1)];
    const p1 = points[i];
    const p2 = points[Math.min(points.length - 1, i + 1)];
    const p3 = points[Math.min(points.length - 1, i + 2)];

    for (let s = 1; s <= segmentsPerSpan; s++) {
      const t = s / segmentsPerSpan;
      const t2 = t * t;
      const t3 = t2 * t;

      const lng =
        0.5 * (
          (2 * p1[0]) +
          (-p0[0] + p2[0]) * t +
          (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
          (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
        );
      const lat =
        0.5 * (
          (2 * p1[1]) +
          (-p0[1] + p2[1]) * t +
          (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
          (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
        );

      result.push([lng, lat]);
    }
  }

  return result;
}

/**
 * Buffer a polyline into a polygon strip of given width in meters.
 * Coordinates are [lng, lat]. Width is in meters.
 */
function bufferLineToPolygon(points: number[][], widthMeters: number): number[][] {
  if (points.length < 2) return points;

  const halfWidth = widthMeters / 2;
  const lat = points[0][1];
  const metersPerDegLat = 111320;
  const metersPerDegLon = metersPerDegLat * Math.cos((lat * Math.PI) / 180);

  const left: number[][] = [];
  const right: number[][] = [];

  for (let i = 0; i < points.length; i++) {
    let dx: number, dy: number;

    if (i === 0) {
      dx = points[1][0] - points[0][0];
      dy = points[1][1] - points[0][1];
    } else if (i === points.length - 1) {
      dx = points[i][0] - points[i - 1][0];
      dy = points[i][1] - points[i - 1][1];
    } else {
      // Average of adjacent segment directions for smooth corners
      dx = points[i + 1][0] - points[i - 1][0];
      dy = points[i + 1][1] - points[i - 1][1];
    }

    const len = Math.sqrt(dx * dx + dy * dy);
    if (len === 0) continue;

    // Perpendicular offset in degrees
    const perpLng = (-dy / len) * (halfWidth / metersPerDegLon);
    const perpLat = (dx / len) * (halfWidth / metersPerDegLat);

    left.push([points[i][0] + perpLng, points[i][1] + perpLat]);
    right.push([points[i][0] - perpLng, points[i][1] - perpLat]);
  }

  // Polygon: left side forward, right side backward
  return [...left, ...right.reverse()];
}

/** Minimum points needed to finish a shape */
function minPointsForTool(tool: SiteZoneType | null): number {
  return isLinearTool(tool) ? 2 : 3;
}

function getToolDisplayLabel(tool: SiteZoneType): string {
  if (tool === 'site_boundary') return 'Site Boundary';
  if (tool === 'building' || tool === 'residential') return 'Buildings';
  if (tool === 'road') return 'Streets and Paths';
  if (tool === 'green_space' || tool === 'parking') return 'Parks / Plazas';
  return ZONE_TYPE_CONFIG[tool]?.label || tool;
}

/**
 * From overlapping features at a click point, pick the one with the smallest
 * polygon area (the innermost / most specific zone). Uses the shoelace formula
 * on raw coordinates — absolute value is fine for relative comparison.
 */
function pickSmallestFeature(features: mapboxgl.MapGeoJSONFeature[]): mapboxgl.MapGeoJSONFeature {
  if (features.length <= 1) return features[0];

  let best = features[0];
  let bestArea = Infinity;

  for (const f of features) {
    const geom = f.geometry;
    if (geom.type !== 'Polygon') continue;
    const ring = (geom as GeoJSON.Polygon).coordinates[0];
    if (!ring || ring.length < 3) continue;

    // Shoelace formula (absolute value)
    let area = 0;
    for (let i = 0; i < ring.length - 1; i++) {
      area += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1];
    }
    area = Math.abs(area) / 2;

    if (area < bestArea) {
      bestArea = area;
      best = f;
    }
  }
  return best;
}

interface DragState {
  type: 'zone' | 'vertex';
  zoneId: string;
  vertexIndex?: number;
  startLngLat: [number, number];
  originalCoords: number[][];
}

interface SitePlannerMapProps {
  latitude?: number;
  longitude?: number;
  siteZones: SiteZone[];
  massingFeatures?: GeoJSON.FeatureCollection;
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
  onZoneSelected: (zoneId: string | null) => void;
  onZoneDeleted?: (zoneId: string) => void;
}

export function SitePlannerMap({
  latitude,
  longitude,
  siteZones,
  massingFeatures,
  onZoneCreated,
  onZoneUpdated,
  onZoneSelected,
  onZoneDeleted,
}: SitePlannerMapProps) {
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { activeSitePlannerTool, activeToolProperties, selectedZoneId, setDraggingZone, setMapInstance } = useViewerStore();

  // Drawing state
  const drawingPointsRef = useRef<number[][]>([]);
  const removedPointsRef = useRef<number[][]>([]);  // stack for redo of removed vertices
  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const onZoneCreatedRef = useRef(onZoneCreated);
  onZoneCreatedRef.current = onZoneCreated;
  const onZoneDeletedRef = useRef(onZoneDeleted);
  onZoneDeletedRef.current = onZoneDeleted;
  const onZoneSelectedRef = useRef(onZoneSelected);
  onZoneSelectedRef.current = onZoneSelected;
  const onZoneUpdatedRef = useRef(onZoneUpdated);
  onZoneUpdatedRef.current = onZoneUpdated;
  const activeSitePlannerToolRef = useRef(activeSitePlannerTool);
  activeSitePlannerToolRef.current = activeSitePlannerTool;
  const activeToolPropertiesRef = useRef(activeToolProperties);
  activeToolPropertiesRef.current = activeToolProperties;
  const siteZonesRef = useRef(siteZones);
  siteZonesRef.current = siteZones;
  const mapLoadedRef = useRef(false);
  const [mapReady, setMapReady] = useState(false);

  // Drag state for zone/vertex editing
  const dragStateRef = useRef<DragState | null>(null);
  // Ref to track pending coords during drag for persistence on mouseup
  const pendingCoordsRef = useRef<{ zoneId: string; coords: number[][] } | null>(null);

  /** Build GeoJSON preview features for the current drawing */
  const buildPreviewFeatures = useCallback((pts: number[][], tool: SiteZoneType | null): GeoJSON.Feature[] => {
    if (pts.length === 0) return [];
    const features: GeoJSON.Feature[] = [];
    const linear = isLinearTool(tool);

    // Vertex dots
    for (const p of pts) {
      features.push({
        type: 'Feature',
        properties: {},
        geometry: { type: 'Point', coordinates: p },
      });
    }

    if (linear) {
      // Road: open polyline (no closing back to start) — smoothed
      if (pts.length >= 2) {
        const smooth = smoothPolyline(pts);
        features.push({
          type: 'Feature',
          properties: {},
          geometry: { type: 'LineString', coordinates: smooth },
        });
        // Show buffered polygon preview using smoothed line
        const width = activeToolPropertiesRef.current?.width ?? ZONE_TYPE_CONFIG[tool!]?.defaultProperties?.width ?? 10;
        const buffered = bufferLineToPolygon(smooth, width);
        features.push({
          type: 'Feature',
          properties: {},
          geometry: { type: 'Polygon', coordinates: [[...buffered, buffered[0]]] },
        });
      }
    } else {
      // Polygon: close back to start
      if (pts.length >= 2) {
        features.push({
          type: 'Feature',
          properties: {},
          geometry: { type: 'LineString', coordinates: [...pts, pts[0]] },
        });
      }
      if (pts.length >= 3) {
        features.push({
          type: 'Feature',
          properties: {},
          geometry: { type: 'Polygon', coordinates: [[...pts, pts[0]]] },
        });
      }
    }

    return features;
  }, []);

  /** Push the current drawing preview to the map */
  const updateDrawingPreview = useCallback(() => {
    const map = mapRef.current;
    if (!map || !mapLoadedRef.current) return;

    const src = map.getSource('drawing-preview') as mapboxgl.GeoJSONSource | undefined;
    if (!src) return;

    const tool = activeSitePlannerToolRef.current;
    const color = tool ? ZONE_TYPE_CONFIG[tool].color : '#fbbf24';
    try {
      map.setPaintProperty('drawing-preview-fill', 'fill-color', color);
      map.setPaintProperty('drawing-preview-line', 'line-color', color);
      map.setPaintProperty('drawing-preview-points', 'circle-color', color);
    } catch {
      // layers may not exist yet
    }

    const pts = drawingPointsRef.current;
    const features = buildPreviewFeatures(pts, tool);
    src.setData({ type: 'FeatureCollection', features });
  }, [buildPreviewFeatures]);

  // ─── Drawing interceptor: lets undo button / Ctrl+Z remove vertices ───
  const { setDrawingInterceptor, clearDrawingInterceptor } = useUndoRedoStore.getState();

  // Helper to remove last drawing vertex (shared by interceptor and Backspace handler)
  const undoLastVertex = useCallback(() => {
    if (drawingPointsRef.current.length === 0) return false;
    const removed = drawingPointsRef.current.pop()!;
    removedPointsRef.current.push(removed);
    setDrawingPoints([...drawingPointsRef.current]);
    updateDrawingPreview();
    return true;
  }, [updateDrawingPreview]);

  // Helper to redo a removed vertex
  const redoLastVertex = useCallback(() => {
    if (removedPointsRef.current.length === 0) return false;
    const restored = removedPointsRef.current.pop()!;
    drawingPointsRef.current.push(restored);
    setDrawingPoints([...drawingPointsRef.current]);
    updateDrawingPreview();
    return true;
  }, [updateDrawingPreview]);

  // Register / clear interceptor whenever drawing points change
  useEffect(() => {
    if (drawingPoints.length > 0) {
      setDrawingInterceptor({
        undo: () => undoLastVertex(),
        redo: () => redoLastVertex(),
        canUndo: () => drawingPointsRef.current.length > 0,
        canRedo: () => removedPointsRef.current.length > 0,
      });
    } else {
      clearDrawingInterceptor();
    }
  }, [drawingPoints, undoLastVertex, redoLastVertex, setDrawingInterceptor, clearDrawingInterceptor]);

  // Clean up interceptor on unmount
  useEffect(() => {
    return () => clearDrawingInterceptor();
  }, [clearDrawingInterceptor]);

  /** Finish the current drawing and create a zone */
  const finishDrawing = useCallback((tool: SiteZoneType, pts: number[][], properties?: SiteZoneProperties | null) => {
    const props = properties ?? activeToolPropertiesRef.current;
    let coords: number[][];
    if (isLinearTool(tool)) {
      const width = (props?.width as number) ?? ZONE_TYPE_CONFIG[tool]?.defaultProperties?.width ?? 10;
      const smooth = smoothPolyline(pts);
      coords = bufferLineToPolygon(smooth, width);
    } else {
      coords = [...pts];
    }
    onZoneCreatedRef.current(coords, tool, props ?? undefined);
  }, []);

  /** Finish current polygon via keyboard or explicit action */
  const finishPolygon = useCallback(() => {
    const tool = activeSitePlannerToolRef.current;
    if (!tool || drawingPointsRef.current.length < minPointsForTool(tool)) return;
    finishDrawing(tool, [...drawingPointsRef.current]);
    drawingPointsRef.current = [];
    removedPointsRef.current = [];
    setDrawingPoints([]);
    updateDrawingPreview();
  }, [updateDrawingPreview, finishDrawing]);

  /** Build zone features for the map source, optionally with modified coords for a specific zone */
  const buildZoneFeatures = useCallback((zones: SiteZone[], overrideZoneId?: string, overrideCoords?: number[][]): GeoJSON.Feature[] => {
    return zones.map((zone) => {
      if (overrideZoneId && zone.id === overrideZoneId && overrideCoords) {
        const closed = [...overrideCoords];
        if (closed.length > 0 && (closed[0][0] !== closed[closed.length - 1][0] || closed[0][1] !== closed[closed.length - 1][1])) {
          closed.push(closed[0]);
        }
        const zoneHeight = typeof zone.properties?.height === 'number' ? zone.properties.height : undefined;
        return {
          type: 'Feature' as const,
          properties: {
            id: zone.id,
            color: zone.color,
            label: zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type,
            zone_type: zone.zone_type,
            ...(zoneHeight != null && { height: zoneHeight }),
          },
          geometry: {
            type: 'Polygon' as const,
            coordinates: [closed],
          },
        };
      }

      const zoneCoords = [...zone.coordinates];
      if (
        zoneCoords.length > 0 &&
        (zoneCoords[0][0] !== zoneCoords[zoneCoords.length - 1][0] ||
          zoneCoords[0][1] !== zoneCoords[zoneCoords.length - 1][1])
      ) {
        zoneCoords.push(zoneCoords[0]);
      }
      const height = typeof zone.properties?.height === 'number' ? zone.properties.height : undefined;
      return {
        type: 'Feature' as const,
        properties: {
          id: zone.id,
          color: zone.color,
          label: zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type,
          zone_type: zone.zone_type,
          ...(height != null && { height }),
        },
        geometry: {
          type: 'Polygon' as const,
          coordinates: [zoneCoords],
        },
      };
    });
  }, []);

  /** Sync saved siteZones to the map GeoJSON source */
  const syncZonesToMap = useCallback((zones: SiteZone[]) => {
    const map = mapRef.current;
    if (!map || !mapLoadedRef.current) return;

    // Debug: log zone dimensions for alignment comparison with block editor
    for (const z of zones) {
      if (z.coordinates.length >= 3) {
        const lat = z.coordinates[0][1];
        const mlon = 111320 * Math.abs(Math.cos((lat * Math.PI) / 180));
        const cx = z.coordinates.reduce((s, c) => s + c[0], 0) / z.coordinates.length;
        const cy = z.coordinates.reduce((s, c) => s + c[1], 0) / z.coordinates.length;
        const xs = z.coordinates.map((c) => (c[0] - cx) * mlon);
        const ys = z.coordinates.map((c) => (c[1] - cy) * 111320);
        const w = Math.max(...xs) - Math.min(...xs);
        const d = Math.max(...ys) - Math.min(...ys);
        console.log('[MasterPlan Debug]', {
          zoneId: z.id, zoneName: z.name, zoneType: z.zone_type,
          numCoords: z.coordinates.length,
          centroid: [cx.toFixed(6), cy.toFixed(6)],
          zoneWidthM: w.toFixed(1), zoneDepthM: d.toFixed(1),
          firstCoord: z.coordinates[0], lastCoord: z.coordinates[z.coordinates.length - 1],
        });
      }
    }

    const source = map.getSource('site-zones') as mapboxgl.GeoJSONSource | undefined;
    if (!source) return;

    const features = buildZoneFeatures(zones);
    source.setData({ type: 'FeatureCollection', features });
  }, [buildZoneFeatures]);

  // Update massing preview layer when massingFeatures prop changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoadedRef.current) return;

    const src = map.getSource('massing-preview') as mapboxgl.GeoJSONSource | undefined;
    if (!src) return;

    if (massingFeatures && massingFeatures.features.length > 0) {
      src.setData(massingFeatures);
      // Hide zone extrusion to avoid overlap with massing blocks
      if (map.getLayer('site-zones-extrusion')) {
        map.setLayoutProperty('site-zones-extrusion', 'visibility', 'none');
      }
    } else {
      src.setData({ type: 'FeatureCollection', features: [] });
      // Restore zone extrusion when massing is cleared
      if (map.getLayer('site-zones-extrusion')) {
        map.setLayoutProperty('site-zones-extrusion', 'visibility', 'visible');
      }
    }
  }, [massingFeatures]);

  /** Update vertex handles for the selected zone */
  const updateVertexHandles = useCallback((zoneId: string | null, zones: SiteZone[], overrideCoords?: number[][]) => {
    const map = mapRef.current;
    if (!map || !mapLoadedRef.current) return;

    const src = map.getSource('zone-edit-vertices') as mapboxgl.GeoJSONSource | undefined;
    if (!src) return;

    if (!zoneId) {
      src.setData({ type: 'FeatureCollection', features: [] });
      return;
    }

    const zone = zones.find((z) => z.id === zoneId);
    if (!zone) {
      src.setData({ type: 'FeatureCollection', features: [] });
      return;
    }

    const coords = overrideCoords || zone.coordinates;
    const features: GeoJSON.Feature[] = coords.map((c, i) => ({
      type: 'Feature',
      properties: { zoneId, vertexIndex: i },
      geometry: { type: 'Point', coordinates: c },
    }));

    src.setData({ type: 'FeatureCollection', features });
  }, []);

  // ─── Initialize map ───
  useEffect(() => {
    if (!containerRef.current || !MAPBOX_TOKEN) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [longitude || -114.07, latitude || 51.045],
      zoom: 16,
      minZoom: 2,
      maxZoom: 22,
      pitch: 60,
      bearing: -30,
      maxPitch: 85,
      doubleClickZoom: false,
      preserveDrawingBuffer: true, // Needed for canvas screenshot capture
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    mapRef.current = map;
    setMapInstance(map);

    map.on('load', () => {
      mapLoadedRef.current = true;

      // --- 3D Terrain ---
      map.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14,
      });
      map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.2 });

      // --- 3D Buildings from Mapbox composite source ---
      const layers = map.getStyle().layers;
      // Find the first symbol layer to insert buildings below labels
      let labelLayerId: string | undefined;
      if (layers) {
        for (const layer of layers) {
          if (layer.type === 'symbol' && (layer as any).layout?.['text-field']) {
            labelLayerId = layer.id;
            break;
          }
        }
      }
      map.addLayer(
        {
          id: '3d-buildings',
          source: 'composite',
          'source-layer': 'building',
          filter: ['==', 'extrude', 'true'],
          type: 'fill-extrusion',
          minzoom: 13,
          paint: {
            // Height-based color: short buildings warm beige, tall buildings cool steel blue
            'fill-extrusion-color': [
              'interpolate', ['linear'], ['get', 'height'],
              0, '#e8dcc8',    // warm beige (low-rise)
              15, '#c9bfb0',   // tan (mid-rise)
              40, '#a8b4bf',   // cool grey-blue (high-rise)
              100, '#8a9bab',  // steel blue (towers)
            ],
            'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 13, 0, 13.05, ['get', 'height']],
            'fill-extrusion-base': ['interpolate', ['linear'], ['zoom'], 13, 0, 13.05, ['get', 'min_height']],
            'fill-extrusion-opacity': 0.8,
          },
        },
        labelLayerId,
      );

      // --- Atmosphere / fog for depth ---
      map.setFog({
        color: 'rgb(186, 210, 235)',
        'high-color': 'rgb(36, 92, 223)',
        'horizon-blend': 0.02,
        'space-color': 'rgb(11, 11, 25)',
        'star-intensity': 0.6,
      });

      // --- Existing zones source + layers ---
      map.addSource('site-zones', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      // Extruded 3D zone massing blocks (for building/residential zones with height)
      map.addLayer({
        id: 'site-zones-extrusion',
        type: 'fill-extrusion',
        source: 'site-zones',
        filter: ['has', 'height'],
        paint: {
          'fill-extrusion-color': ['get', 'color'],
          'fill-extrusion-height': ['get', 'height'],
          'fill-extrusion-base': 0,
          'fill-extrusion-opacity': 0.75,
        },
      });

      // Flat fill for zones without height (green space, roads, site boundary, etc.)
      map.addLayer({
        id: 'site-zones-fill',
        type: 'fill',
        source: 'site-zones',
        filter: ['!', ['has', 'height']],
        paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.5 },
      });

      map.addLayer({
        id: 'site-zones-outline',
        type: 'line',
        source: 'site-zones',
        paint: { 'line-color': ['get', 'color'], 'line-width': 2 },
      });

      map.addLayer({
        id: 'site-zones-selected',
        type: 'line',
        source: 'site-zones',
        paint: { 'line-color': '#ffffff', 'line-width': 3 },
        filter: ['==', ['get', 'id'], ''],
      });

      map.addLayer({
        id: 'site-zones-labels',
        type: 'symbol',
        source: 'site-zones',
        layout: {
          'text-field': ['get', 'label'],
          'text-size': 12,
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-allow-overlap': false,
        },
        paint: {
          'text-color': '#ffffff',
          'text-halo-color': 'rgba(0,0,0,0.7)',
          'text-halo-width': 1,
        },
      });

      // --- Massing preview source + layer (for AI-generated massing blocks) ---
      map.addSource('massing-preview', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'massing-preview-extrusion',
        type: 'fill-extrusion',
        source: 'massing-preview',
        filter: ['==', ['get', 'type'], 'building'],
        paint: {
          'fill-extrusion-color': ['get', 'color'],
          'fill-extrusion-height': ['get', 'height'],
          'fill-extrusion-base': 0,
          'fill-extrusion-opacity': 0.85,
        },
      });

      map.addLayer({
        id: 'massing-preview-green',
        type: 'fill',
        source: 'massing-preview',
        filter: ['==', ['get', 'type'], 'green_space'],
        paint: {
          'fill-color': ['get', 'color'],
          'fill-opacity': 0.6,
        },
      });

      // --- Vertex edit handles source + layer ---
      map.addSource('zone-edit-vertices', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'zone-edit-vertices-layer',
        type: 'circle',
        source: 'zone-edit-vertices',
        paint: {
          'circle-radius': 7,
          'circle-color': '#ffffff',
          'circle-stroke-color': '#3b82f6',
          'circle-stroke-width': 2,
        },
      });

      // --- Drawing preview source + layers ---
      map.addSource('drawing-preview', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'drawing-preview-fill',
        type: 'fill',
        source: 'drawing-preview',
        filter: ['==', '$type', 'Polygon'],
        paint: { 'fill-color': '#fbbf24', 'fill-opacity': 0.35 },
      });

      map.addLayer({
        id: 'drawing-preview-line',
        type: 'line',
        source: 'drawing-preview',
        filter: ['==', '$type', 'LineString'],
        paint: { 'line-color': '#fbbf24', 'line-width': 2, 'line-dasharray': [3, 2] },
      });

      map.addLayer({
        id: 'drawing-preview-points',
        type: 'circle',
        source: 'drawing-preview',
        filter: ['==', '$type', 'Point'],
        paint: {
          'circle-radius': 6,
          'circle-color': '#fbbf24',
          'circle-stroke-color': '#ffffff',
          'circle-stroke-width': 2,
        },
      });

      // Signal that the map is ready so zone data can be synced
      setMapReady(true);
    });

    // ─── Click to place points (drawing mode) OR select zones ───
    map.on('click', (e) => {
      // Don't process click events during/right after drag
      if (dragStateRef.current) return;

      const tool = activeSitePlannerToolRef.current;
      if (tool) {
        drawingPointsRef.current = [
          ...drawingPointsRef.current,
          [e.lngLat.lng, e.lngLat.lat],
        ];
        removedPointsRef.current = [];  // clear redo stack on new point
        setDrawingPoints([...drawingPointsRef.current]);
        requestAnimationFrame(() => {
          const m = mapRef.current;
          if (!m || !mapLoadedRef.current) return;
          const src = m.getSource('drawing-preview') as mapboxgl.GeoJSONSource | undefined;
          if (!src) return;

          const currentTool = activeSitePlannerToolRef.current;
          const color = currentTool ? ZONE_TYPE_CONFIG[currentTool].color : '#fbbf24';
          try {
            m.setPaintProperty('drawing-preview-fill', 'fill-color', color);
            m.setPaintProperty('drawing-preview-line', 'line-color', color);
            m.setPaintProperty('drawing-preview-points', 'circle-color', color);
          } catch { /* layers may not exist yet */ }

          const pts = drawingPointsRef.current;
          const features = buildPreviewFeatures(pts, currentTool);
          src.setData({ type: 'FeatureCollection', features });
        });
      } else {
        // Selection mode — but only if not coming from a drag
        // Query both flat fill and extruded layers so building zones (with height) are clickable
        const queryLayers = ['site-zones-fill', 'site-zones-extrusion'].filter(
          (l) => map.getLayer(l),
        );
        const features = map.queryRenderedFeatures(e.point, {
          layers: queryLayers,
        });
        if (features.length > 0) {
          const zoneId = pickSmallestFeature(features).properties?.id;
          if (zoneId) {
            onZoneSelectedRef.current(zoneId);
            return;
          }
        }
        onZoneSelectedRef.current(null);
      }
    });

    // ─── Double-click to finish ───
    map.on('dblclick', (e) => {
      const tool = activeSitePlannerToolRef.current;
      const minPts = minPointsForTool(tool);
      // +1 because the first click of the dblclick already added a point
      if (tool && drawingPointsRef.current.length >= minPts + 1) {
        e.preventDefault();
        // Remove the last duplicate point from the first click of the dblclick
        drawingPointsRef.current = drawingPointsRef.current.slice(0, -1);
        finishDrawing(tool, [...drawingPointsRef.current]);
        drawingPointsRef.current = [];
        removedPointsRef.current = [];
        setDrawingPoints([]);
        requestAnimationFrame(() => {
          const m = mapRef.current;
          if (!m || !mapLoadedRef.current) return;
          const src = m.getSource('drawing-preview') as mapboxgl.GeoJSONSource | undefined;
          if (src) src.setData({ type: 'FeatureCollection', features: [] });
        });
      }
    });

    // ─── Mousedown: start drag (zone body or vertex) ───
    map.on('mousedown', (e) => {
      const tool = activeSitePlannerToolRef.current;
      if (tool) return; // Drawing mode — don't interfere

      // Check vertex handles first (higher priority)
      const vertexFeatures = map.queryRenderedFeatures(e.point, {
        layers: ['zone-edit-vertices-layer'],
      });
      if (vertexFeatures.length > 0) {
        const props = vertexFeatures[0].properties;
        const zoneId = props?.zoneId as string;
        const vertexIndex = props?.vertexIndex as number;
        const zone = siteZonesRef.current.find((z) => z.id === zoneId);
        if (zone) {
          e.preventDefault();
          dragStateRef.current = {
            type: 'vertex',
            zoneId,
            vertexIndex,
            startLngLat: [e.lngLat.lng, e.lngLat.lat],
            originalCoords: zone.coordinates.map((c) => [...c]),
          };
          map.dragPan.disable();
          map.getCanvas().style.cursor = 'crosshair';
          setDraggingZone(true);
          return;
        }
      }

      // Check zone body for zone dragging
      const zoneFeatures = map.queryRenderedFeatures(e.point, {
        layers: ['site-zones-fill'],
      });
      if (zoneFeatures.length > 0) {
        const zoneId = pickSmallestFeature(zoneFeatures).properties?.id as string;
        const zone = siteZonesRef.current.find((z) => z.id === zoneId);
        if (zone) {
          e.preventDefault();
          dragStateRef.current = {
            type: 'zone',
            zoneId,
            startLngLat: [e.lngLat.lng, e.lngLat.lat],
            originalCoords: zone.coordinates.map((c) => [...c]),
          };
          map.dragPan.disable();
          map.getCanvas().style.cursor = 'grabbing';
          setDraggingZone(true);
        }
      }
    });

    // ─── Mousemove: update drag position ───
    map.on('mousemove', (e) => {
      const ds = dragStateRef.current;
      if (!ds) {
        // Cursor hints when not dragging
        const tool = activeSitePlannerToolRef.current;
        if (tool) {
          map.getCanvas().style.cursor = 'crosshair';
          return;
        }
        // Check if hovering vertex handle
        const vertexHits = map.queryRenderedFeatures(e.point, {
          layers: ['zone-edit-vertices-layer'],
        });
        if (vertexHits.length > 0) {
          map.getCanvas().style.cursor = 'crosshair';
          return;
        }
        // Check if hovering zone body
        const zoneHits = map.queryRenderedFeatures(e.point, {
          layers: ['site-zones-fill'],
        });
        if (zoneHits.length > 0) {
          map.getCanvas().style.cursor = 'grab';
          return;
        }
        map.getCanvas().style.cursor = '';
        return;
      }

      const dlng = e.lngLat.lng - ds.startLngLat[0];
      const dlat = e.lngLat.lat - ds.startLngLat[1];

      if (ds.type === 'zone') {
        // Move all vertices by delta
        const newCoords = ds.originalCoords.map((c) => [c[0] + dlng, c[1] + dlat]);
        updateZoneOnMap(ds.zoneId, newCoords);
        updateVertexHandles(ds.zoneId, siteZonesRef.current, newCoords);
      } else if (ds.type === 'vertex' && ds.vertexIndex != null) {
        // Move only the dragged vertex
        const newCoords = ds.originalCoords.map((c) => [...c]);
        newCoords[ds.vertexIndex] = [
          ds.originalCoords[ds.vertexIndex][0] + dlng,
          ds.originalCoords[ds.vertexIndex][1] + dlat,
        ];
        updateZoneOnMap(ds.zoneId, newCoords);
        updateVertexHandles(ds.zoneId, siteZonesRef.current, newCoords);
      }
    });

    // Mouseup on map is handled by the window-level listener below

    return () => {
      mapLoadedRef.current = false;
      setMapReady(false);
      map.remove();
      mapRef.current = null;
      setMapInstance(null);
    };
  }, [latitude, longitude, buildPreviewFeatures, finishDrawing, setDraggingZone, setMapInstance, updateVertexHandles]);

  // Helper to update a zone's geometry on the map in real-time
  function updateZoneOnMap(zoneId: string, newCoords: number[][]) {
    const map = mapRef.current;
    if (!map || !mapLoadedRef.current) return;

    const source = map.getSource('site-zones') as mapboxgl.GeoJSONSource | undefined;
    if (!source) return;

    const features = buildZoneFeatures(siteZonesRef.current, zoneId, newCoords);
    source.setData({ type: 'FeatureCollection', features });

    // Store the pending coordinates for persistence on mouseup
    pendingCoordsRef.current = { zoneId, coords: newCoords };
  }

  // We need to handle mouseup more cleanly - use a window listener to catch mouseup even outside map
  useEffect(() => {
    const handleMouseUp = () => {
      const ds = dragStateRef.current;
      if (!ds) return;

      const map = mapRef.current;
      if (map) {
        map.dragPan.enable();
        map.getCanvas().style.cursor = '';
      }
      setDraggingZone(false);
      dragStateRef.current = null;

      // Persist the pending coordinates
      const pending = pendingCoordsRef.current;
      if (pending) {
        onZoneUpdatedRef.current(pending.zoneId, pending.coords);
        pendingCoordsRef.current = null;
      }
    };

    window.addEventListener('mouseup', handleMouseUp);
    return () => window.removeEventListener('mouseup', handleMouseUp);
  }, [setDraggingZone]);

  // ─── Auto-finish polygon when switching tools ───
  const prevToolRef = useRef(activeSitePlannerTool);
  const prevToolPropertiesRef = useRef(activeToolProperties);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.getCanvas().style.cursor = activeSitePlannerTool ? 'crosshair' : '';

    const pts = drawingPointsRef.current;
    const prevTool = prevToolRef.current;
    const prevToolProperties = prevToolPropertiesRef.current;
    prevToolRef.current = activeSitePlannerTool;
    prevToolPropertiesRef.current = activeToolProperties;

    if (pts.length > 0) {
      const minPts = minPointsForTool(prevTool);
      if (pts.length >= minPts && prevTool) {
        // Auto-finish with the PREVIOUS tool type and its properties
        finishDrawing(prevTool, [...pts], prevToolProperties);
      }
      drawingPointsRef.current = [];
      removedPointsRef.current = [];
      setDrawingPoints([]);
      updateDrawingPreview();
    }
  }, [activeSitePlannerTool, activeToolProperties, updateDrawingPreview, finishDrawing]);

  // ─── Auto-finish any in-progress drawing on unmount ───
  // (e.g. user clicks "View in 3D" without finishing their drawing)
  useEffect(() => {
    return () => {
      const pts = drawingPointsRef.current;
      const tool = activeSitePlannerToolRef.current;
      if (pts.length > 0 && tool && pts.length >= minPointsForTool(tool)) {
        finishDrawing(tool, [...pts]);
      }
    };
  }, [finishDrawing]);

  // ─── Sync saved zones to map (re-runs when map becomes ready OR zones change) ───
  useEffect(() => {
    if (mapReady) {
      syncZonesToMap(siteZones);
    }
  }, [siteZones, mapReady, syncZonesToMap]);

  // ─── Selected zone highlight + vertex handles ───
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReady) return;
    try {
      map.setFilter('site-zones-selected', ['==', ['get', 'id'], selectedZoneId || '']);
    } catch { /* Layer might not be ready yet */ }

    // Update vertex handles for selected zone (only in select mode)
    if (!activeSitePlannerTool) {
      updateVertexHandles(selectedZoneId, siteZones);
    } else {
      updateVertexHandles(null, siteZones);
    }
  }, [selectedZoneId, mapReady, siteZones, activeSitePlannerTool, updateVertexHandles]);

  // ─── Keyboard shortcuts ───
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      // Skip when focus is in an editable element
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if ((e.target as HTMLElement)?.isContentEditable) return;

      const tool = activeSitePlannerToolRef.current;

      if (e.key === 'Escape' && drawingPointsRef.current.length > 0) {
        drawingPointsRef.current = [];
        removedPointsRef.current = [];
        setDrawingPoints([]);
        updateDrawingPreview();
      }
      if (e.key === 'Enter' && tool && drawingPointsRef.current.length >= minPointsForTool(tool)) {
        finishPolygon();
      }
      // Backspace removes last vertex while drawing
      if (e.key === 'Backspace' && drawingPointsRef.current.length > 0) {
        undoLastVertex();
      }
      // Delete key: remove last vertex while drawing, OR delete selected zone
      if (e.key === 'Delete') {
        if (drawingPointsRef.current.length > 0) {
          undoLastVertex();
        } else if (!tool && selectedZoneId && onZoneDeletedRef.current) {
          onZoneDeletedRef.current(selectedZoneId);
        }
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [updateDrawingPreview, finishPolygon, undoLastVertex, selectedZoneId]);

  if (!MAPBOX_TOKEN) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-gray-800 text-gray-400">
        Set VITE_MAPBOX_TOKEN to enable satellite map
      </div>
    );
  }

  const linear = isLinearTool(activeSitePlannerTool);
  const minPts = minPointsForTool(activeSitePlannerTool);
  const currentLength = linear && drawingPoints.length >= 2 ? polylineLength(drawingPoints) : 0;

  return (
    <>
      <div ref={containerRef} className="h-full w-full" />
      {/* Drawing hint */}
      {activeSitePlannerTool && (
        <div className="absolute left-1/2 top-16 z-30 max-w-[90vw] -translate-x-1/2 rounded-lg bg-gray-900/80 px-4 py-2 text-center text-xs text-white backdrop-blur-sm">
          {drawingPoints.length === 0
            ? linear
              ? `Click to start drawing ${getToolDisplayLabel(activeSitePlannerTool)} (Line)`
              : `Click to start drawing ${getToolDisplayLabel(activeSitePlannerTool)} (Polygon)`
            : drawingPoints.length < minPts
            ? linear
              ? `Click to add waypoints (${drawingPoints.length}/${minPts} min) — Ctrl+Z to undo`
              : `Click to add points (${drawingPoints.length}/${minPts} min) — Ctrl+Z to undo`
            : linear
            ? `${drawingPoints.length} waypoints · ${formatDistance(currentLength)} — Double-click or Enter to finish — Esc to cancel`
            : `${drawingPoints.length} points — Double-click or Enter to finish — Esc to cancel`}
        </div>
      )}
      {/* Live distance badge for roads */}
      {activeSitePlannerTool && linear && currentLength > 0 && (
        <div className="absolute left-1/2 top-[6.5rem] z-30 -translate-x-1/2 rounded-full bg-emerald-500/90 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm shadow-lg">
          {formatDistance(currentLength)}
        </div>
      )}
      {/* Select mode hint */}
      {!activeSitePlannerTool && (
        <div className="absolute left-1/2 top-16 z-30 max-w-[90vw] -translate-x-1/2 rounded-lg bg-gray-900/80 px-4 py-2 text-center text-xs text-white backdrop-blur-sm">
          Click a zone to select — Drag to move — Drag vertices to reshape — Del to delete
        </div>
      )}
    </>
  );
}

