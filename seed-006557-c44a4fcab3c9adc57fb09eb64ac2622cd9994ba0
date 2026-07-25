/**
 * useGlobeDrawing.ts — Drawing state machine for the 3D globe.
 *
 * Mirrors SitePlannerMap's drawing flow:
 * Click → place points → preview → double-click/Enter to finish
 *
 * Disables GlobeControls during drawing mode.
 */

import { useCallback, useRef, useState, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import type { SiteZoneType, SiteZoneProperties } from '@/types';
import { useViewerStore } from '@/store';
import { useGlobeRaycast } from './useGlobeRaycast';
import {
  isLinearTool,
  minPointsForTool,
  smoothPolyline,
  bufferLineToPolygon,
} from '../mapEngine/geoUtils';

interface UseGlobeDrawingOptions {
  controlsRef: React.RefObject<any>;
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
}

export function useGlobeDrawing({ controlsRef, onZoneCreated }: UseGlobeDrawingOptions) {
  const { gl } = useThree();
  const { activeSitePlannerTool, activeToolProperties } = useViewerStore();
  const { raycastToLatLng } = useGlobeRaycast();

  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const [cursorPosition, setCursorPosition] = useState<[number, number] | null>(null);
  const drawingPointsRef = useRef<number[][]>([]);
  const isDrawing = activeSitePlannerTool !== null;
  const linear = isLinearTool(activeSitePlannerTool);

  // Sync ref with state
  useEffect(() => {
    drawingPointsRef.current = drawingPoints;
  }, [drawingPoints]);

  // Disable controls during drawing, enable when not drawing
  useEffect(() => {
    const controls = controlsRef.current;
    if (controls) {
      controls.enabled = !isDrawing;
      console.log('[GlobeDrawing] controls.enabled =', !isDrawing, 'isDrawing =', isDrawing);
    }
  }, [isDrawing, controlsRef]);

  const finishDrawing = useCallback(() => {
    const pts = drawingPointsRef.current;
    if (!activeSitePlannerTool) return;

    const minPts = minPointsForTool(activeSitePlannerTool);
    if (pts.length < minPts) return;

    let finalCoords: number[][];

    if (linear) {
      // Smooth the polyline then buffer to polygon
      const smoothed = smoothPolyline(pts);
      const width = (activeToolProperties?.width as number) || 10;
      finalCoords = bufferLineToPolygon(smoothed, width);
    } else {
      finalCoords = [...pts];
    }

    onZoneCreated(finalCoords, activeSitePlannerTool, activeToolProperties || undefined);

    // Clear drawing state
    setDrawingPoints([]);
    setCursorPosition(null);
    drawingPointsRef.current = [];
  }, [activeSitePlannerTool, activeToolProperties, linear, onZoneCreated]);

  // Attach event listeners to canvas
  useEffect(() => {
    if (!isDrawing) return;

    const canvas = gl.domElement;

    const handleClick = (e: MouseEvent) => {
      const lngLat = raycastToLatLng(e);
      if (!lngLat) return;

      const newPoints = [...drawingPointsRef.current, lngLat];
      drawingPointsRef.current = newPoints;
      setDrawingPoints(newPoints);
    };

    const handleDblClick = (e: MouseEvent) => {
      e.preventDefault();
      // Remove the duplicate point added by the second click
      if (drawingPointsRef.current.length > 1) {
        drawingPointsRef.current.pop();
        setDrawingPoints([...drawingPointsRef.current]);
      }
      finishDrawing();
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (drawingPointsRef.current.length === 0) return;
      const lngLat = raycastToLatLng(e);
      setCursorPosition(lngLat);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        finishDrawing();
      } else if (e.key === 'Escape') {
        setDrawingPoints([]);
        setCursorPosition(null);
        drawingPointsRef.current = [];
      } else if (e.key === 'Backspace') {
        if (drawingPointsRef.current.length > 0) {
          drawingPointsRef.current.pop();
          setDrawingPoints([...drawingPointsRef.current]);
        }
      } else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        // Undo last point
        if (drawingPointsRef.current.length > 0) {
          drawingPointsRef.current.pop();
          setDrawingPoints([...drawingPointsRef.current]);
        }
      }
    };

    canvas.addEventListener('click', handleClick);
    canvas.addEventListener('dblclick', handleDblClick);
    canvas.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('keydown', handleKeyDown);

    // Set cursor
    canvas.style.cursor = 'crosshair';

    return () => {
      canvas.removeEventListener('click', handleClick);
      canvas.removeEventListener('dblclick', handleDblClick);
      canvas.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('keydown', handleKeyDown);
      canvas.style.cursor = '';
    };
  }, [isDrawing, gl, raycastToLatLng, finishDrawing]);

  return {
    drawingPoints,
    cursorPosition,
    isDrawing,
    linear,
  };
}
