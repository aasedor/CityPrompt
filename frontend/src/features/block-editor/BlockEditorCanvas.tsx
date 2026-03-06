import { useMemo, useRef, useCallback, useState, useEffect } from 'react';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import { computeTransform, toSVG, offsetToSVG, metersToPixels } from '@/utils/coordTransform';
import { BlockGroup } from './components/BlockGroup';
import { useBlockDrag } from './hooks/useBlockDrag';
import { useSnapLines } from './hooks/useSnapLines';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface BlockEditorCanvasProps {
  width: number;
  height: number;
}

/**
 * Compute Mapbox Static API URL from zone coordinates.
 * Calculates center and zoom from bounding box.
 */
function getMapboxStaticUrl(
  coordinates: number[][],
  width: number,
  height: number,
): string | null {
  if (!MAPBOX_TOKEN || coordinates.length < 3) return null;

  let minLng = Infinity, maxLng = -Infinity;
  let minLat = Infinity, maxLat = -Infinity;
  for (const [lng, lat] of coordinates) {
    if (lng < minLng) minLng = lng;
    if (lng > maxLng) maxLng = lng;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }

  const centerLng = (minLng + maxLng) / 2;
  const centerLat = (minLat + maxLat) / 2;

  const lngSpan = maxLng - minLng;
  const latSpan = maxLat - minLat;
  const maxSpan = Math.max(lngSpan, latSpan);

  // Approximate zoom: 360 / 2^zoom ~ span in degrees, with padding
  let zoom = Math.floor(Math.log2(360 / (maxSpan * 1.5)));
  zoom = Math.max(10, Math.min(20, zoom));

  // Mapbox static images max 1280x1280
  const imgW = Math.min(1280, Math.round(width));
  const imgH = Math.min(1280, Math.round(height));

  return `https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/${centerLng.toFixed(6)},${centerLat.toFixed(6)},${zoom},0/${imgW}x${imgH}@2x?access_token=${MAPBOX_TOKEN}`;
}

export function BlockEditorCanvas({ width, height }: BlockEditorCanvasProps) {
  const {
    zone, editedLayout, selectedBlockIndex, hoveredBlockIndex, selectedElementType, selectedElementIndex,
    selectBlock, selectElement, hoverBlock, zoom, panX, panY, setZoom, setPan, dragState,
    showGrid, gridSizeMeters, showDimensions,
  } = useBlockEditorStore();

  const svgRef = useRef<SVGSVGElement>(null);
  const isPanningRef = useRef(false);
  const lastPanRef = useRef({ x: 0, y: 0 });

  // Satellite background URL
  const satelliteUrl = useMemo(
    () => zone ? getMapboxStaticUrl(zone.coordinates, width, height) : null,
    [zone, width, height],
  );
  const [satelliteLoaded, setSatelliteLoaded] = useState(false);
  const [satelliteError, setSatelliteError] = useState(false);

  // Reset satellite state when URL changes
  useEffect(() => {
    setSatelliteLoaded(false);
    setSatelliteError(false);
  }, [satelliteUrl]);

  const baseTransform = useMemo(
    () => zone ? computeTransform(zone.coordinates, width, height, 40) : null,
    [zone, width, height],
  );

  const transform = useMemo(() => {
    if (!baseTransform) return null;
    return {
      ...baseTransform,
      scale: baseTransform.scale * zoom,
      offsetX: baseTransform.offsetX + panX,
      offsetY: baseTransform.offsetY + panY,
    };
  }, [baseTransform, zoom, panX, panY]);

  const { startDrag, onDrag, endDrag, isDragging } = useBlockDrag(transform);

  const snapLines = useSnapLines(
    editedLayout?.buildings ?? [],
    dragState,
    transform,
    width,
    height,
  );

  const boundaryPoints = useMemo(() => {
    if (!zone || !transform) return '';
    return zone.coordinates
      .map((c) => toSVG(c[0], c[1], transform))
      .map(([x, y]) => `${x},${y}`)
      .join(' ');
  }, [zone, transform]);

  const gridLines = useMemo(() => {
    if (!transform || !showGrid || !zone) return [];
    const gridPixels = metersToPixels(gridSizeMeters, transform);
    if (gridPixels < 8) return [];
    const lines: { x1: number; y1: number; x2: number; y2: number; isAxis: boolean }[] = [];

    const [cxSvg, cySvg] = offsetToSVG(0, 0, transform);

    for (let x = cxSvg % gridPixels; x < width; x += gridPixels) {
      lines.push({ x1: x, y1: 0, x2: x, y2: height, isAxis: Math.abs(x - cxSvg) < 1 });
    }
    for (let y = cySvg % gridPixels; y < height; y += gridPixels) {
      lines.push({ x1: 0, y1: y, x2: width, y2: y, isAxis: Math.abs(y - cySvg) < 1 });
    }
    return lines;
  }, [transform, showGrid, gridSizeMeters, width, height, zone]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(zoom * factor);
  }, [zoom, setZoom]);

  const handleCanvasPointerDown = useCallback((e: React.PointerEvent) => {
    if (isDragging) return;
    if (e.button === 1 || (e.button === 0 && (e.ctrlKey || e.metaKey))) {
      isPanningRef.current = true;
      lastPanRef.current = { x: e.clientX, y: e.clientY };
      (e.target as Element).setPointerCapture(e.pointerId);
      e.preventDefault();
    } else if (e.button === 0 && !e.ctrlKey && !e.metaKey) {
      selectBlock(null);
    }
  }, [isDragging, selectBlock]);

  const handleCanvasPointerMove = useCallback((e: React.PointerEvent) => {
    if (isDragging) {
      onDrag(e);
      return;
    }
    if (isPanningRef.current) {
      const dx = e.clientX - lastPanRef.current.x;
      const dy = e.clientY - lastPanRef.current.y;
      lastPanRef.current = { x: e.clientX, y: e.clientY };
      setPan(panX + dx, panY + dy);
    }
  }, [isDragging, onDrag, panX, panY, setPan]);

  const handleCanvasPointerUp = useCallback((e: React.PointerEvent) => {
    if (isDragging) {
      endDrag(e);
      return;
    }
    if (isPanningRef.current) {
      isPanningRef.current = false;
      (e.target as Element).releasePointerCapture(e.pointerId);
    }
  }, [isDragging, endDrag]);

  if (!zone || !transform || !editedLayout) {
    return (
      <div className="flex items-center justify-center h-full text-neutral-500">
        No layout data available
      </div>
    );
  }

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="select-none"
      style={{ background: '#1a1a2e' }}
      onWheel={handleWheel}
      onPointerDown={handleCanvasPointerDown}
      onPointerMove={handleCanvasPointerMove}
      onPointerUp={handleCanvasPointerUp}
    >
      {/* Satellite map background — wrapped in a group that zooms/pans with everything else */}
      <g transform={baseTransform ? `translate(${baseTransform.offsetX + panX}, ${baseTransform.offsetY + panY}) scale(${zoom}) translate(${-baseTransform.offsetX}, ${-baseTransform.offsetY})` : undefined}>
        {satelliteUrl && !satelliteError && (
          <image
            href={satelliteUrl}
            x={0}
            y={0}
            width={width}
            height={height}
            preserveAspectRatio="xMidYMid slice"
            opacity={satelliteLoaded ? 0.7 : 0}
            onLoad={() => setSatelliteLoaded(true)}
            onError={() => setSatelliteError(true)}
            style={{ pointerEvents: 'none' }}
          />
        )}

        {/* Dark overlay on top of satellite for contrast */}
        {satelliteLoaded && !satelliteError && (
          <rect x={0} y={0} width={width} height={height} fill="rgba(15, 15, 26, 0.4)" style={{ pointerEvents: 'none' }} />
        )}
      </g>

      {/* Grid */}
      {gridLines.map((line, i) => (
        <line
          key={i}
          x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2}
          stroke={line.isAxis ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)'}
          strokeWidth={line.isAxis ? 1 : 0.5}
        />
      ))}

      {/* Zone boundary */}
      <polygon
        points={boundaryPoints}
        fill="rgba(245,158,11,0.05)"
        stroke="#f59e0b"
        strokeWidth={2}
        strokeDasharray="8,4"
        strokeOpacity={0.6}
      />

      {/* Green spaces */}
      {editedLayout.green_spaces.map((gs, i) => {
        const pts = gs.polygon
          .map(([dx, dy]) => offsetToSVG(dx, dy, transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polygon
            key={`gs-${i}`}
            points={pts}
            fill="#22c55e"
            fillOpacity={selectedElementType === 'green_space' && selectedElementIndex === i ? 0.5 : 0.25}
            stroke={selectedElementType === 'green_space' && selectedElementIndex === i ? '#4ade80' : '#16a34a'}
            strokeWidth={selectedElementType === 'green_space' && selectedElementIndex === i ? 2.5 : 1}
            strokeOpacity={0.7}
            style={{ cursor: 'pointer' }}
            onPointerDown={(e) => { e.stopPropagation(); selectElement('green_space', i); }}
          />
        );
      })}

      {/* Roads */}
      {editedLayout.roads.map((road, i) => {
        const pts = road.centerline
          .map(([dx, dy]) => offsetToSVG(dx, dy, transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        const strokeW = Math.max(3, metersToPixels(road.width_m, transform));
        return (
          <polyline
            key={`road-${i}`}
            points={pts}
            fill="none"
            stroke={selectedElementType === 'road' && selectedElementIndex === i ? '#60a5fa' : '#374151'}
            strokeWidth={strokeW}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeOpacity={selectedElementType === 'road' && selectedElementIndex === i ? 1 : 0.7}
            style={{ cursor: 'pointer' }}
            onPointerDown={(e) => { e.stopPropagation(); selectElement('road', i); }}
          />
        );
      })}

      {/* Road centerlines */}
      {editedLayout.roads.map((road, i) => {
        const pts = road.centerline
          .map(([dx, dy]) => offsetToSVG(dx, dy, transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polyline
            key={`road-center-${i}`}
            points={pts}
            fill="none"
            stroke="#fbbf24"
            strokeWidth={1}
            strokeDasharray="4,4"
            strokeOpacity={0.4}
            strokeLinecap="round"
          />
        );
      })}

      {/* Snap lines */}
      {snapLines.map((line, i) => (
        <line
          key={`snap-${i}`}
          x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2}
          stroke="#6366f1"
          strokeWidth={0.5}
          strokeDasharray="4,4"
          strokeOpacity={0.6}
          style={{ pointerEvents: 'none' }}
        />
      ))}

      {/* Buildings (blocks) */}
      {editedLayout.buildings.map((bldg, i) => (
        <BlockGroup
          key={i}
          block={bldg}
          index={i}
          transform={transform}
          isSelected={selectedBlockIndex === i}
          isHovered={hoveredBlockIndex === i}
          showDimensions={showDimensions}
          onPointerDown={startDrag}
          onHover={hoverBlock}
          onClick={selectBlock}
        />
      ))}
    </svg>
  );
}
