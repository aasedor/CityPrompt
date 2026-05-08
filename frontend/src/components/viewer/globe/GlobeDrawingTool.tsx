/**
 * GlobeDrawingTool.tsx — Drawing tool for placing polygon points on the globe.
 *
 * Uses DOM click events on the R3F canvas for point placement.
 * Renders vertex markers and polygon preview using EastNorthUpFrame.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import { Html } from '@react-three/drei';
import type { SiteZoneType, SiteZoneProperties } from '@/types';
import { useViewerStore } from '@/store';
import {
  isLinearTool,
  minPointsForTool,
  smoothPolyline,
  bufferLineToPolygon,
  computeCentroid,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
} from '../mapEngine/geoUtils';

const RAD_TO_DEG = 180 / Math.PI;
const DEG_TO_RAD = Math.PI / 180;
const CONNECT_VERTEX_RADIUS_METERS = 30;
const GLOBE_SCENE_HTML_Z_INDEX_RANGE: [number, number] = [1, 0];

function distanceMeters(a: number[], b: number[]): number {
  const lat = ((a[1] + b[1]) / 2) * DEG_TO_RAD;
  const dx = (a[0] - b[0]) * 111320 * Math.cos(lat);
  const dy = (a[1] - b[1]) * 110540;
  return Math.sqrt(dx * dx + dy * dy);
}

interface GlobeDrawingToolProps {
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
}

export function GlobeDrawingTool({ onZoneCreated }: GlobeDrawingToolProps) {
  const { camera, gl } = useThree();
  const { activeSitePlannerTool, activeToolProperties } = useViewerStore();

  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const [centerNearStartVertex, setCenterNearStartVertex] = useState(false);
  const drawingPointsRef = useRef<number[][]>([]);
  const lastClickTime = useRef(0);
  const pointerDownPos = useRef<{ x: number; y: number } | null>(null);

  const isActive = activeSitePlannerTool !== null;
  const linear = isLinearTool(activeSitePlannerTool);

  // Debug — log on every render
  console.log('[GlobeDrawingTool] RENDER isActive:', isActive, 'tool:', activeSitePlannerTool, 'points:', drawingPoints.length);

  // Keep ref in sync
  useEffect(() => {
    drawingPointsRef.current = drawingPoints;
  }, [drawingPoints]);

  // Raycast mouse position to lat/lng on globe surface
  const pointerToLatLng = useCallback((event: Pick<PointerEvent, 'clientX' | 'clientY'>): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    const ndcX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

    const hit = new THREE.Vector3();
    const result = WGS84_ELLIPSOID.intersectRay(raycaster.ray, hit);
    if (!result) return null;

    const cartographic = WGS84_ELLIPSOID.getPositionToCartographic(hit, {} as any);
    return [cartographic.lon * RAD_TO_DEG, cartographic.lat * RAD_TO_DEG];
  }, [camera, gl]);

  const getCanvasCenterLatLng = useCallback((): [number, number] | null => {
    const rect = gl.domElement.getBoundingClientRect();
    return pointerToLatLng({
      clientX: rect.left + rect.width / 2,
      clientY: rect.top + rect.height / 2,
    });
  }, [gl, pointerToLatLng]);

  const updateCenterConnectionState = useCallback(() => {
    const center = getCanvasCenterLatLng();
    const pts = drawingPointsRef.current;
    if (
      !center ||
      !activeSitePlannerTool ||
      linear ||
      pts.length < minPointsForTool(activeSitePlannerTool)
    ) {
      setCenterNearStartVertex(false);
      return;
    }

    setCenterNearStartVertex(distanceMeters(center, pts[0]) <= CONNECT_VERTEX_RADIUS_METERS);
  }, [activeSitePlannerTool, getCanvasCenterLatLng, linear]);

  const addDrawingPoint = useCallback((lngLat: [number, number]) => {
    console.log('[GlobeDrawingTool] Point placed:', lngLat, 'total:', drawingPointsRef.current.length + 1);
    const newPts = [...drawingPointsRef.current, lngLat];
    drawingPointsRef.current = newPts;
    setDrawingPoints(newPts);
    requestAnimationFrame(updateCenterConnectionState);
  }, [updateCenterConnectionState]);

  const finishDrawing = useCallback(() => {
    const pts = drawingPointsRef.current;
    if (!activeSitePlannerTool) return;
    if (pts.length < minPointsForTool(activeSitePlannerTool)) return;

    let finalCoords: number[][];
    if (linear) {
      const smoothed = smoothPolyline(pts);
      const width = (activeToolProperties?.width as number) || 10;
      finalCoords = bufferLineToPolygon(smoothed, width);
    } else {
      finalCoords = [...pts];
    }

    console.log('[GlobeDrawingTool] Creating zone with', finalCoords.length, 'points');
    onZoneCreated(finalCoords, activeSitePlannerTool, activeToolProperties || undefined);
    setDrawingPoints([]);
    drawingPointsRef.current = [];
    setCenterNearStartVertex(false);
  }, [activeSitePlannerTool, activeToolProperties, linear, onZoneCreated]);

  // Keyboard handlers
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        console.log('[GlobeDrawingTool] Enter pressed, points:', drawingPointsRef.current.length);
        finishDrawing();
      } else if (e.key === 'Escape') {
        setDrawingPoints([]);
        drawingPointsRef.current = [];
      } else if (e.key === 'Backspace') {
        if (drawingPointsRef.current.length > 0) {
          const newPts = drawingPointsRef.current.slice(0, -1);
          drawingPointsRef.current = newPts;
          setDrawingPoints(newPts);
        }
      } else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        if (drawingPointsRef.current.length > 0) {
          const newPts = drawingPointsRef.current.slice(0, -1);
          drawingPointsRef.current = newPts;
          setDrawingPoints(newPts);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, finishDrawing]);

  // Click handler — uses mousedown+mouseup to distinguish clicks from drags
  // GlobeControls stay enabled so user can zoom/pan while drawing
  useEffect(() => {
    if (!isActive) return;

    const canvas = gl.domElement;

    const handlePointerDown = (e: PointerEvent) => {
      pointerDownPos.current = { x: e.clientX, y: e.clientY };
    };

    const handlePointerUp = (e: PointerEvent) => {
      if (!pointerDownPos.current) return;

      // Only place a point if mouse didn't move much (click, not drag)
      const dx = e.clientX - pointerDownPos.current.x;
      const dy = e.clientY - pointerDownPos.current.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      pointerDownPos.current = null;

      if (dist > 5) return; // Was a drag, not a click

      const now = Date.now();
      const isDoubleClick = now - lastClickTime.current < 400;
      lastClickTime.current = now;

      if (isDoubleClick) {
        if (drawingPointsRef.current.length > 0) {
          drawingPointsRef.current.pop();
          setDrawingPoints([...drawingPointsRef.current]);
        }
        finishDrawing();
        return;
      }

      const lngLat = pointerToLatLng(e);
      if (!lngLat) return;

      addDrawingPoint(lngLat);
    };

    console.log('[GlobeDrawingTool] Attaching click handlers to canvas:', canvas.tagName, canvas.width, canvas.height);
    canvas.addEventListener('pointerdown', handlePointerDown);
    canvas.addEventListener('pointerup', handlePointerUp);
    canvas.style.cursor = 'crosshair';

    return () => {
      canvas.removeEventListener('pointerdown', handlePointerDown);
      canvas.removeEventListener('pointerup', handlePointerUp);
      canvas.style.cursor = '';
    };
  }, [isActive, gl, pointerToLatLng, finishDrawing, addDrawingPoint]);

  // Clear drawing when tool changes
  useEffect(() => {
    setDrawingPoints([]);
    drawingPointsRef.current = [];
    setCenterNearStartVertex(false);
  }, [activeSitePlannerTool]);

  const cancelDrawing = useCallback(() => {
    setDrawingPoints([]);
    drawingPointsRef.current = [];
    setCenterNearStartVertex(false);
  }, []);

  const undoLastPoint = useCallback(() => {
    if (drawingPointsRef.current.length === 0) return;
    const newPts = drawingPointsRef.current.slice(0, -1);
    drawingPointsRef.current = newPts;
    setDrawingPoints(newPts);
    requestAnimationFrame(updateCenterConnectionState);
  }, [updateCenterConnectionState]);

  const placeCenterVertex = useCallback(() => {
    if (!activeSitePlannerTool) return;
    if (centerNearStartVertex && drawingPointsRef.current.length >= minPointsForTool(activeSitePlannerTool)) {
      finishDrawing();
      return;
    }

    const lngLat = getCanvasCenterLatLng();
    if (lngLat) addDrawingPoint(lngLat);
  }, [activeSitePlannerTool, addDrawingPoint, centerNearStartVertex, finishDrawing, getCanvasCenterLatLng]);

  useEffect(() => {
    if (!isActive) {
      setCenterNearStartVertex(false);
      return;
    }

    updateCenterConnectionState();
    const interval = window.setInterval(updateCenterConnectionState, 150);
    return () => window.clearInterval(interval);
  }, [drawingPoints.length, isActive, updateCenterConnectionState]);

  if (!isActive) return null;

  const canFinish = activeSitePlannerTool
    ? drawingPoints.length >= minPointsForTool(activeSitePlannerTool)
    : false;
  const canConnectToStart = !!activeSitePlannerTool && !linear && centerNearStartVertex && canFinish;
  const placeVertexLabel = canConnectToStart
    ? 'Connect & Finish'
    : drawingPoints.length === 0
      ? 'Place First Vertex'
      : linear
        ? 'Place Waypoint'
        : 'Place Vertex';

  return (
    <>
      {drawingPoints.length > 0 && <DrawingPreview points={drawingPoints} linear={linear} />}
      <Html fullscreen>
        <div className="pointer-events-none absolute left-1/2 top-1/2 z-40 -translate-x-1/2 -translate-y-1/2 sm:hidden">
          <div className={`h-8 w-8 rounded-full border-2 ${canConnectToStart ? 'border-emerald-300 bg-emerald-400/20' : 'border-white/90 bg-black/15'} shadow-[0_0_0_1px_rgba(0,0,0,0.35),0_8px_24px_rgba(0,0,0,0.35)]`}>
            <div className="absolute left-1/2 top-[-10px] h-8 w-px -translate-x-1/2 bg-white/90" />
            <div className="absolute left-[-10px] top-1/2 h-px w-8 -translate-y-1/2 bg-white/90" />
          </div>
        </div>
        <div className="pointer-events-none absolute inset-x-3 top-24 z-50 mx-auto max-w-[34rem] sm:hidden">
          <div
            className="pointer-events-auto grid grid-cols-3 gap-2"
            onPointerDown={(event) => event.stopPropagation()}
            onPointerUp={(event) => event.stopPropagation()}
          >
            <button
              type="button"
              onClick={placeCenterVertex}
              className={`col-span-3 min-h-12 rounded-xl px-3 py-2 text-sm font-black shadow-lg ${canConnectToStart ? 'bg-emerald-400 text-slate-950 shadow-emerald-500/25' : 'bg-amber-500 text-slate-950 shadow-amber-500/25'}`}
            >
              {placeVertexLabel}
            </button>
            <button
              type="button"
              onClick={undoLastPoint}
              disabled={drawingPoints.length === 0}
              className="min-h-11 rounded-xl bg-white px-3 py-2 text-xs font-semibold text-slate-950 shadow-lg disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-white/50"
            >
              Undo
            </button>
            <button
              type="button"
              onClick={cancelDrawing}
              className="min-h-11 rounded-xl bg-slate-950/85 px-3 py-2 text-xs font-semibold text-white shadow-lg ring-1 ring-white/10"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={finishDrawing}
              disabled={!canFinish}
              className="min-h-11 rounded-xl bg-amber-500 px-3 py-2 text-xs font-semibold text-slate-950 shadow-lg shadow-amber-500/25 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-white/50 disabled:shadow-none"
            >
              Finish
            </button>
          </div>
        </div>
      </Html>
    </>
  );
}

/** Visual preview of the polygon being drawn */
function DrawingPreview({ points, linear }: { points: number[][]; linear: boolean }) {
  if (points.length === 0) return null;

  const centroid = computeCentroid(points);
  const mLon = metersPerDegLon(centroid[1]);

  // Convert to local meters for line/fill geometry
  const localPts = points.map(p => ({
    x: (p[0] - centroid[0]) * mLon,
    y: (p[1] - centroid[1]) * METERS_PER_DEG_LAT,
  }));

  // Line positions (close polygon if 3+ points)
  const linePts = [...localPts];
  if (!linear && linePts.length >= 3) linePts.push(linePts[0]);
  const lineArray = new Float32Array(linePts.flatMap(p => [p.x, p.y, 5]));

  // Fill shape
  let fillGeo: THREE.ShapeGeometry | null = null;
  if (!linear && localPts.length >= 3) {
    const shape = new THREE.Shape();
    shape.moveTo(localPts[0].x, localPts[0].y);
    for (let i = 1; i < localPts.length; i++) shape.lineTo(localPts[i].x, localPts[i].y);
    shape.closePath();
    fillGeo = new THREE.ShapeGeometry(shape);
  }

  return (
    <>
      {/* Vertex markers — HTML labels are always visible regardless of depth */}
      {points.map((pt, i) => (
        <EastNorthUpFrame key={`dot-${i}`} lat={pt[1] * DEG_TO_RAD} lon={pt[0] * DEG_TO_RAD} height={5}>
          {/* 3D sphere marker */}
          <mesh renderOrder={999}>
            <sphereGeometry args={[20, 12, 12]} />
            <meshBasicMaterial
              color="#f59e0b"
              depthTest={false}
              depthWrite={false}
              transparent
              opacity={0.95}
            />
          </mesh>

          {/* HTML marker — guaranteed visible */}
          <Html
            center
            zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
            style={{ pointerEvents: 'none' }}
          >
            <div className="h-4 w-4 rounded-full border-2 border-white bg-amber-500 shadow-lg" />
          </Html>
        </EastNorthUpFrame>
      ))}

      {/* Lines + fill at centroid */}
      {localPts.length >= 2 && (
        <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={0}>
          {/* Edge lines */}
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                array={lineArray}
                count={lineArray.length / 3}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#f59e0b" linewidth={2} depthTest={false} depthWrite={false} />
          </line>

          {/* Fill preview */}
          {fillGeo && (
            <mesh geometry={fillGeo} position={[0, 0, 3]} renderOrder={997}>
              <meshBasicMaterial
                color="#f59e0b"
                transparent
                opacity={0.25}
                side={THREE.DoubleSide}
                depthTest={false}
                depthWrite={false}
              />
            </mesh>
          )}
        </EastNorthUpFrame>
      )}

      {/* Point count indicator */}
      <EastNorthUpFrame lat={centroid[1] * DEG_TO_RAD} lon={centroid[0] * DEG_TO_RAD} height={30}>
        <Html
          center
          zIndexRange={GLOBE_SCENE_HTML_Z_INDEX_RANGE}
          style={{ pointerEvents: 'none' }}
        >
          <div className="rounded-full bg-amber-500 px-2 py-0.5 text-xs font-bold text-white shadow-lg">
            {points.length} pts
          </div>
        </Html>
      </EastNorthUpFrame>
    </>
  );
}
