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

interface GlobeDrawingToolProps {
  onZoneCreated: (coordinates: number[][], zoneType: SiteZoneType, properties?: SiteZoneProperties) => void;
}

export function GlobeDrawingTool({ onZoneCreated }: GlobeDrawingToolProps) {
  const { camera, gl } = useThree();
  const { activeSitePlannerTool, activeToolProperties } = useViewerStore();

  const [drawingPoints, setDrawingPoints] = useState<number[][]>([]);
  const drawingPointsRef = useRef<number[][]>([]);
  const lastClickTime = useRef(0);
  const mouseDownPos = useRef<{ x: number; y: number } | null>(null);

  const isActive = activeSitePlannerTool !== null;
  const linear = isLinearTool(activeSitePlannerTool);

  // Debug — log on every render
  console.log('[GlobeDrawingTool] RENDER isActive:', isActive, 'tool:', activeSitePlannerTool, 'points:', drawingPoints.length);

  // Keep ref in sync
  useEffect(() => {
    drawingPointsRef.current = drawingPoints;
  }, [drawingPoints]);

  // Raycast mouse position to lat/lng on globe surface
  const mouseToLatLng = useCallback((event: MouseEvent): [number, number] | null => {
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

    const handleMouseDown = (e: MouseEvent) => {
      mouseDownPos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = (e: MouseEvent) => {
      if (!mouseDownPos.current) return;

      // Only place a point if mouse didn't move much (click, not drag)
      const dx = e.clientX - mouseDownPos.current.x;
      const dy = e.clientY - mouseDownPos.current.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      mouseDownPos.current = null;

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

      const lngLat = mouseToLatLng(e);
      if (!lngLat) return;

      console.log('[GlobeDrawingTool] Point placed:', lngLat, 'total:', drawingPointsRef.current.length + 1);
      const newPts = [...drawingPointsRef.current, lngLat];
      drawingPointsRef.current = newPts;
      setDrawingPoints(newPts);
    };

    console.log('[GlobeDrawingTool] Attaching click handlers to canvas:', canvas.tagName, canvas.width, canvas.height);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.style.cursor = 'crosshair';

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mouseup', handleMouseUp);
      canvas.style.cursor = '';
    };
  }, [isActive, gl, mouseToLatLng, finishDrawing]);

  // Clear drawing when tool changes
  useEffect(() => {
    setDrawingPoints([]);
    drawingPointsRef.current = [];
  }, [activeSitePlannerTool]);

  if (!isActive || drawingPoints.length === 0) return null;

  return <DrawingPreview points={drawingPoints} linear={linear} />;
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
          <Html center style={{ pointerEvents: 'none' }}>
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
        <Html center style={{ pointerEvents: 'none' }}>
          <div className="rounded-full bg-amber-500 px-2 py-0.5 text-xs font-bold text-white shadow-lg">
            {points.length} pts
          </div>
        </Html>
      </EastNorthUpFrame>
    </>
  );
}
