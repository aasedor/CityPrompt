/**
 * useGlobeZoneEditing.ts — Zone selection, movement, reshape, and rotation on the globe.
 *
 * Mirrors SitePlannerMap's editing interactions:
 * - Click to select zone
 * - Drag zone body to move
 * - Drag vertex handle to reshape
 * - Delete/Copy/Paste via keyboard
 */

import { useCallback, useRef, useState, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import type { SiteZone } from '@/types';
import { useViewerStore } from '@/store';
import { useGlobeRaycast } from './useGlobeRaycast';
import { geodesicArea } from '../mapEngine/geoUtils';

interface UseGlobeZoneEditingOptions {
  controlsRef: React.RefObject<any>;
  zones: SiteZone[];
  onZoneUpdated: (zoneId: string, coordinates: number[][]) => void;
  onZoneDeleted?: (zoneId: string) => void;
  onZoneSelected: (zoneId: string | null) => void;
}

export function useGlobeZoneEditing({
  controlsRef,
  zones,
  onZoneUpdated,
  onZoneDeleted,
  onZoneSelected,
}: UseGlobeZoneEditingOptions) {
  const { gl } = useThree();
  const { selectedZoneId, activeSitePlannerTool } = useViewerStore();
  const { raycastToLatLng } = useGlobeRaycast();

  const [isDragging, setIsDragging] = useState(false);
  const [dragVertexIndex, setDragVertexIndex] = useState<number | null>(null);
  const [dragArea, setDragArea] = useState(0);

  const dragStartRef = useRef<[number, number] | null>(null);
  const originalCoordsRef = useRef<number[][] | null>(null);
  const clipboardRef = useRef<{ coords: number[][]; zoneType: string; properties: any } | null>(null);

  const selectedZone = zones.find(z => z.id === selectedZoneId) || null;

  // Keyboard shortcuts for editing
  useEffect(() => {
    if (activeSitePlannerTool) return; // Drawing mode takes priority

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedZoneId) return;

      if (e.key === 'Delete' || e.key === 'Backspace') {
        onZoneDeleted?.(selectedZoneId);
        onZoneSelected(null);
      } else if (e.key === 'Escape') {
        onZoneSelected(null);
      } else if (e.key === 'c' && (e.ctrlKey || e.metaKey)) {
        // Copy
        const zone = zones.find(z => z.id === selectedZoneId);
        if (zone) {
          clipboardRef.current = {
            coords: zone.coordinates.map(c => [...c]),
            zoneType: zone.zone_type,
            properties: { ...(zone.properties || {}) },
          };
        }
      } else if (e.key === 'v' && (e.ctrlKey || e.metaKey)) {
        // Paste — offset by ~20m
        // (Would need onZoneCreated — skip for now, handled in parent)
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedZoneId, activeSitePlannerTool, zones, onZoneDeleted, onZoneSelected]);

  /**
   * Start dragging a zone body.
   */
  const startZoneDrag = useCallback((zoneId: string, startLngLat: [number, number]) => {
    const zone = zones.find(z => z.id === zoneId);
    if (!zone) return;

    dragStartRef.current = startLngLat;
    originalCoordsRef.current = zone.coordinates.map(c => [...c]);
    setIsDragging(true);

    if (controlsRef.current) controlsRef.current.enabled = false;
  }, [zones, controlsRef]);

  /**
   * Start dragging a vertex handle.
   */
  const startVertexDrag = useCallback((vertexIndex: number) => {
    if (!selectedZone) return;

    setDragVertexIndex(vertexIndex);
    originalCoordsRef.current = selectedZone.coordinates.map(c => [...c]);
    setIsDragging(true);

    if (controlsRef.current) controlsRef.current.enabled = false;
  }, [selectedZone, controlsRef]);

  /**
   * Handle mouse move during drag.
   * Throttled to ~60fps to avoid overwhelming the GPU with re-renders
   * while Google 3D Tiles are loaded.
   */
  const lastDragTimeRef = useRef(0);
  const handleDragMove = useCallback((event: MouseEvent) => {
    if (!isDragging || !selectedZoneId || !originalCoordsRef.current) return;

    // Throttle to ~60fps (16ms) — prevents GPU overload with 3D tiles
    const now = performance.now();
    if (now - lastDragTimeRef.current < 16) return;
    lastDragTimeRef.current = now;

    const currentLngLat = raycastToLatLng(event);
    if (!currentLngLat) return;

    const zone = zones.find(z => z.id === selectedZoneId);
    if (!zone) return;

    let newCoords: number[][];

    if (dragVertexIndex !== null) {
      // Vertex drag — move single vertex
      newCoords = originalCoordsRef.current.map((c, i) =>
        i === dragVertexIndex ? [...currentLngLat] : [...c]
      );
    } else if (dragStartRef.current) {
      // Body drag — move all vertices by delta
      const dLng = currentLngLat[0] - dragStartRef.current[0];
      const dLat = currentLngLat[1] - dragStartRef.current[1];
      newCoords = originalCoordsRef.current.map(c => [c[0] + dLng, c[1] + dLat]);
    } else {
      return;
    }

    setDragArea(geodesicArea(newCoords));
    onZoneUpdated(selectedZoneId, newCoords);
  }, [isDragging, selectedZoneId, dragVertexIndex, zones, raycastToLatLng, onZoneUpdated]);

  /**
   * End drag operation.
   */
  const endDrag = useCallback(() => {
    setIsDragging(false);
    setDragVertexIndex(null);
    setDragArea(0);
    dragStartRef.current = null;
    originalCoordsRef.current = null;

    if (controlsRef.current) controlsRef.current.enabled = true;
  }, [controlsRef]);

  // Attach drag event listeners
  useEffect(() => {
    if (!isDragging) return;

    const canvas = gl.domElement;
    canvas.addEventListener('mousemove', handleDragMove);
    window.addEventListener('mouseup', endDrag);

    return () => {
      canvas.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', endDrag);
    };
  }, [isDragging, gl, handleDragMove, endDrag]);

  return {
    isDragging,
    dragArea,
    selectedZone,
    startZoneDrag,
    startVertexDrag,
  };
}
