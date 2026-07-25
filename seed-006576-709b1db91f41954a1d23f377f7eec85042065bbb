import { useCallback, useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import type { Map as MapboxMap, Marker } from 'mapbox-gl';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Viewpoint {
  id: string;
  label: string;
  /** Camera position on the map */
  lng: number;
  lat: number;
  /** Which direction the camera looks (0 = north, 90 = east) */
  bearing: number;
  /** Street-level camera pitch — 60° gives a natural eye-level feel */
  pitch: number;
  /** Zoom level for the street view capture */
  zoom: number;
}

export interface UseViewpointPickerReturn {
  /** All saved viewpoints for this session */
  viewpoints: Viewpoint[];
  /** The viewpoint currently being previewed on the map */
  activeViewpoint: Viewpoint | null;
  /** Enter pin-placement mode — next map click drops a viewpoint pin */
  startPlacing: () => void;
  /** Cancel pin-placement mode without placing */
  cancelPlacing: () => void;
  /** Whether the user is currently in pin-placement mode */
  isPlacing: boolean;
  /** Fly the map to a street-level preview of this viewpoint */
  previewViewpoint: (vp: Viewpoint) => void;
  /** Fly back to the aerial massing view */
  returnToAerial: () => void;
  /** Remove a viewpoint by id */
  removeViewpoint: (id: string) => void;
  /** Update the label of a viewpoint */
  renameViewpoint: (id: string, label: string) => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STREET_PITCH   = 62;   // degrees — natural eye-level perspective
const STREET_ZOOM    = 18.5; // close enough to read building facades clearly
const AERIAL_PITCH   = 48;   // return pitch after street preview
const AERIAL_ZOOM    = 16;   // return zoom

// ---------------------------------------------------------------------------
// Marker HTML — the pin shown on the map for each viewpoint
// ---------------------------------------------------------------------------

function createPinElement(label: string, bearing: number, active: boolean): HTMLElement {
  const el = document.createElement('div');
  el.style.cssText = `
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    user-select: none;
  `;

  // Direction arrow
  const arrow = document.createElement('div');
  arrow.style.cssText = `
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 14px solid ${active ? '#6366f1' : '#f59e0b'};
    transform: rotate(${bearing}deg);
    transform-origin: center bottom;
    margin-bottom: -2px;
    transition: border-bottom-color 0.2s;
  `;

  // Pin circle
  const pin = document.createElement('div');
  pin.style.cssText = `
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: ${active ? '#6366f1' : '#f59e0b'};
    border: 2px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    transition: background 0.2s;
  `;
  pin.textContent = '👁';

  // Label
  const lbl = document.createElement('div');
  lbl.style.cssText = `
    margin-top: 4px;
    background: rgba(14,17,23,0.85);
    color: white;
    font-size: 11px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 6px;
    white-space: nowrap;
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
  `;
  lbl.textContent = label;

  el.appendChild(arrow);
  el.appendChild(pin);
  el.appendChild(lbl);
  return el;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useViewpointPicker(map: MapboxMap | null): UseViewpointPickerReturn {
  const [viewpoints, setViewpoints]             = useState<Viewpoint[]>([]);
  const [activeViewpoint, setActiveViewpoint]   = useState<Viewpoint | null>(null);
  const [isPlacing, setIsPlacing]               = useState(false);

  // Map from viewpoint id → Mapbox Marker instance
  const markersRef   = useRef<globalThis.Map<string, Marker>>(new globalThis.Map());
  // Store aerial camera state so we can return to it
  const aerialCamRef = useRef<{ center: [number,number]; zoom: number; pitch: number; bearing: number } | null>(null);
  // Rotation drag state
  const dragRef      = useRef<{ active: boolean; startX: number; startBearing: number; vpId: string } | null>(null);

  // ── Sync markers to viewpoints state ──────────────────────────────────────
  useEffect(() => {
    if (!map) return;

    // Remove markers for deleted viewpoints
    markersRef.current.forEach((marker, id) => {
      if (!viewpoints.find(vp => vp.id === id)) {
        marker.remove();
        markersRef.current.delete(id);
      }
    });

    // Add or update markers
    viewpoints.forEach(vp => {
      const isActive = activeViewpoint?.id === vp.id;
      const existing = markersRef.current.get(vp.id);

      if (existing) {
        // Update element in place
        const el = createPinElement(vp.label, vp.bearing, isActive);
        attachMarkerDrag(el, vp.id);
        existing.getElement().replaceWith(el);
        // Re-attach the replaced element reference isn't needed — marker handles DOM
      } else {
        const el = createPinElement(vp.label, vp.bearing, isActive);
        attachMarkerDrag(el, vp.id);
        const marker = new mapboxgl.Marker({ element: el, draggable: true })
          .setLngLat([vp.lng, vp.lat])
          .addTo(map);

        // Update position when dragged
        marker.on('dragend', () => {
          const { lng, lat } = marker.getLngLat();
          setViewpoints(prev =>
            prev.map(v => v.id === vp.id ? { ...v, lng, lat } : v)
          );
        });

        markersRef.current.set(vp.id, marker);
      }
    });
  }, [viewpoints, activeViewpoint, map]);

  // ── Arrow rotation drag ───────────────────────────────────────────────────
  function attachMarkerDrag(el: HTMLElement, vpId: string) {
    const arrow = el.querySelector('div') as HTMLElement;
    if (!arrow) return;

    arrow.style.cursor = 'grab';

    arrow.addEventListener('mousedown', (e) => {
      e.stopPropagation();
      const vp = viewpoints.find(v => v.id === vpId);
      if (!vp) return;
      dragRef.current = { active: true, startX: e.clientX, startBearing: vp.bearing, vpId };
    });
  }

  useEffect(() => {
    function onMouseMove(e: MouseEvent) {
      if (!dragRef.current?.active) return;
      const delta = e.clientX - dragRef.current.startX;
      const newBearing = (dragRef.current.startBearing + delta * 1.5) % 360;
      setViewpoints(prev =>
        prev.map(v => v.id === dragRef.current!.vpId ? { ...v, bearing: newBearing } : v)
      );
    }
    function onMouseUp() {
      if (dragRef.current) dragRef.current.active = false;
    }
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [viewpoints]);

  // ── Click handler for pin placement ───────────────────────────────────────
  useEffect(() => {
    if (!map || !isPlacing) return;

    map.getCanvas().style.cursor = 'crosshair';

    function onClick(e: mapboxgl.MapMouseEvent) {
      const { lng, lat } = e.lngLat;
      const bearing = map!.getBearing();
      const id = `vp-${Date.now()}`;
      const count = viewpoints.length + 1;

      const newVP: Viewpoint = {
        id,
        label: `View ${count}`,
        lng,
        lat,
        bearing,
        pitch: STREET_PITCH,
        zoom: STREET_ZOOM,
      };

      setViewpoints(prev => [...prev, newVP]);
      setIsPlacing(false);
      map!.getCanvas().style.cursor = '';

      // Immediately preview the new viewpoint
      previewViewpointInternal(map!, newVP);
      setActiveViewpoint(newVP);
    }

    map.once('click', onClick);
    return () => {
      map.off('click', onClick);
      map.getCanvas().style.cursor = '';
    };
  }, [isPlacing, map, viewpoints.length]);

  // ── Internal fly-to ───────────────────────────────────────────────────────
  function previewViewpointInternal(m: MapboxMap, vp: Viewpoint) {
    // Save aerial state before flying down
    const c = m.getCenter();
    aerialCamRef.current = {
      center: [c.lng, c.lat],
      zoom: m.getZoom(),
      pitch: m.getPitch(),
      bearing: m.getBearing(),
    };

    m.easeTo({
      center: [vp.lng, vp.lat],
      zoom: vp.zoom,
      pitch: vp.pitch,
      bearing: vp.bearing,
      duration: 1200,
      essential: true,
    });
  }

  // ── Public API ────────────────────────────────────────────────────────────
  const startPlacing = useCallback(() => {
    setIsPlacing(true);
  }, []);

  const cancelPlacing = useCallback(() => {
    setIsPlacing(false);
    if (map) map.getCanvas().style.cursor = '';
  }, [map]);

  const previewViewpoint = useCallback((vp: Viewpoint) => {
    if (!map) return;
    setActiveViewpoint(vp);
    previewViewpointInternal(map, vp);
  }, [map]);

  const returnToAerial = useCallback(() => {
    if (!map) return;
    setActiveViewpoint(null);
    const cam = aerialCamRef.current;
    map.easeTo({
      center: cam ? cam.center : map.getCenter(),
      zoom: cam?.zoom ?? AERIAL_ZOOM,
      pitch: cam?.pitch ?? AERIAL_PITCH,
      bearing: cam?.bearing ?? map.getBearing(),
      duration: 1000,
      essential: true,
    });
  }, [map]);

  const removeViewpoint = useCallback((id: string) => {
    setViewpoints(prev => prev.filter(v => v.id !== id));
    if (activeViewpoint?.id === id) setActiveViewpoint(null);
  }, [activeViewpoint]);

  const renameViewpoint = useCallback((id: string, label: string) => {
    setViewpoints(prev => prev.map(v => v.id === id ? { ...v, label } : v));
  }, []);

  return {
    viewpoints,
    activeViewpoint,
    startPlacing,
    cancelPlacing,
    isPlacing,
    previewViewpoint,
    returnToAerial,
    removeViewpoint,
    renameViewpoint,
  };
}
