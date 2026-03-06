import { useMemo, useRef, useCallback, useState, useEffect } from 'react';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import { computeTransform, toSVG, offsetToSVG, metersToPixels, type Transform } from '@/utils/coordTransform';
import { BlockGroup } from './components/BlockGroup';
import { useBlockDrag } from './hooks/useBlockDrag';
import { useSnapLines } from './hooks/useSnapLines';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

// Fetch satellite imagery covering more area than the zone so zooming out still shows map
const SATELLITE_EXPAND = 12;

interface BlockEditorCanvasProps {
  width: number;
  height: number;
  allZones?: import('@/types').SiteZone[];
  onSelectZone?: (zoneId: string) => void;
}

interface SatelliteInfo {
  url: string;
  halfLonDeg: number; // half-width of image in degrees longitude
  halfLatDeg: number; // half-height of image in degrees latitude
}

/**
 * Compute Mapbox Static API URL and the exact geographic extent of the image.
 *
 * Key insight: the Mapbox Static API with @2x returns an image with 2× the
 * pixels but covering the SAME geographic area as the non-@2x version.
 * The geographic extent is determined by (imgW, imgH) "CSS pixels" at the
 * given zoom, NOT the actual pixel count of the returned image.
 *
 * We derive the zoom so that 1 CSS-pixel ≈ SATELLITE_EXPAND / baseScale meters,
 * giving a wider satellite coverage for zoom-out headroom.
 */
function getSatelliteInfo(
  baseTransform: Transform,
  svgWidth: number,
  svgHeight: number,
): SatelliteInfo | null {
  if (!MAPBOX_TOKEN) return null;

  const { cx, cy, mlon, mlat } = baseTransform;

  // Mapbox static images max 1280x1280 CSS pixels
  const imgW = Math.min(1280, Math.round(svgWidth));
  const imgH = Math.min(1280, Math.round(svgHeight));

  // Use exact Mapbox tile-math: at zoom z, the full world is 256·2^z pixels wide.
  // So W CSS-pixels of a static image span  W · 360 / (256·2^z)  degrees of longitude.
  // For latitude (Mercator), the local degrees-per-pixel at lat φ is:
  //   dLat/px ≈ 360·cos(φ) / (256·2^z)
  //
  // We want the satellite to cover SATELLITE_EXPAND times the viewport area.
  // At the base SVG transform, the viewport shows roughly svgW/scale meters.
  // So we want the satellite to cover svgW/scale * SATELLITE_EXPAND meters.
  //
  // Solving for zoom:
  //   imgW · 360 / (256·2^z) · mlon = imgW · metersPerCSSPx
  //   metersPerCSSPx should = SATELLITE_EXPAND / baseScale
  //   → 2^z = 360 · mlon / (256 · metersPerCSSPx)   ... but this is complex.
  //
  // Simpler: just use the standard formula and compute extent from the ACTUAL zoom.

  const cosLat = Math.cos((cy * Math.PI) / 180);
  const scale = baseTransform.scale;

  // Zoom where 1 CSS-pixel = 1/scale meters, then back off by SATELLITE_EXPAND
  const zoom = Math.min(22, Math.max(0,
    Math.log2(156543.03392 * cosLat * scale) - Math.log2(SATELLITE_EXPAND),
  ));

  // Mapbox Static API uses 512-pixel tiles (like Mapbox GL v2), not 256.
  // At zoom z, the full world is 512·2^z pixels wide.
  // So imgW CSS-pixels span: imgW * 360 / (512 * 2^z) degrees of longitude.
  const TILE_SIZE = 512;

  const halfLonDeg = (imgW / 2) * 360 / (TILE_SIZE * Math.pow(2, zoom));

  // For latitude, use the Mercator inverse to get EXACT top/bottom latitudes
  const latRad = (cy * Math.PI) / 180;
  const worldPx = TILE_SIZE * Math.pow(2, zoom);
  const mercY_center = worldPx * (1 - Math.log(Math.tan(Math.PI / 4 + latRad / 2)) / Math.PI) / 2;
  const mercY_top = mercY_center - imgH / 2;
  const mercY_bottom = mercY_center + imgH / 2;
  const latTop = (2 * Math.atan(Math.exp(Math.PI * (1 - 2 * mercY_top / worldPx))) - Math.PI / 2) * 180 / Math.PI;
  const latBottom = (2 * Math.atan(Math.exp(Math.PI * (1 - 2 * mercY_bottom / worldPx))) - Math.PI / 2) * 180 / Math.PI;
  const halfLatDeg = (latTop - latBottom) / 2;

  const url = `https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/${cx.toFixed(6)},${cy.toFixed(6)},${zoom.toFixed(4)},0/${imgW}x${imgH}@2x?access_token=${MAPBOX_TOKEN}`;

  console.log('[Satellite Debug]', {
    zoom: zoom.toFixed(4),
    imgW, imgH, TILE_SIZE,
    halfLonDeg: halfLonDeg.toFixed(6),
    halfLatDeg: halfLatDeg.toFixed(6),
    coverageW_m: (2 * halfLonDeg * mlon).toFixed(1),
    coverageH_m: (2 * halfLatDeg * mlat).toFixed(1),
    scale: scale.toFixed(2),
  });

  return { url, halfLonDeg, halfLatDeg };
}

export function BlockEditorCanvas({ width, height, allZones, onSelectZone }: BlockEditorCanvasProps) {
  const {
    zone, editedLayout, selectedBlockIndex, hoveredBlockIndex, selectedElementType, selectedElementIndex,
    selectBlock, selectElement, hoverBlock, zoom, panX, panY, setZoom, setPan, dragState,
    showGrid, gridSizeMeters, showDimensions,
  } = useBlockEditorStore();

  const svgRef = useRef<SVGSVGElement>(null);
  const isPanningRef = useRef(false);
  const lastPanRef = useRef({ x: 0, y: 0 });

  // When multiple zones exist, fit ALL zone coordinates so neighbors are visible
  const baseTransform = useMemo(() => {
    if (!zone) return null;
    const otherZones = allZones?.filter((z) => z.id !== zone.id && z.coordinates.length >= 3) ?? [];
    if (otherZones.length > 0) {
      const allCoords = [...zone.coordinates, ...otherZones.flatMap((z) => z.coordinates)];
      return computeTransform(allCoords, width, height, 40);
    }
    return computeTransform(zone.coordinates, width, height, 40);
  }, [zone, allZones, width, height]);


  // Debug: log zone dimensions and satellite info for alignment verification
  useEffect(() => {
    if (!zone || !baseTransform) return;
    const coords = zone.coordinates;
    const mlon = baseTransform.mlon;
    const mlat = baseTransform.mlat;
    const mCoords = coords.map((c) => [(c[0] - baseTransform.cx) * mlon, (c[1] - baseTransform.cy) * mlat]);
    const xs = mCoords.map((c) => c[0]);
    const ys = mCoords.map((c) => c[1]);
    const zoneW = Math.max(...xs) - Math.min(...xs);
    const zoneD = Math.max(...ys) - Math.min(...ys);
    console.log('[BlockEditor Debug]', {
      zoneId: zone.id,
      numCoords: coords.length,
      centroid: [baseTransform.cx.toFixed(6), baseTransform.cy.toFixed(6)],
      zoneWidthM: zoneW.toFixed(1),
      zoneDepthM: zoneD.toFixed(1),
      zoneAreaM2: (zoneW * zoneD).toFixed(0),
      svgScale: baseTransform.scale.toFixed(2),
      canvasSize: `${width}x${height}`,
      firstCoord: coords[0],
      lastCoord: coords[coords.length - 1],
    });
  }, [zone, baseTransform, width, height]);

  // Satellite info — URL + geographic extent (stable, doesn't change with zoom/pan)
  const satelliteInfo = useMemo(
    () => baseTransform ? getSatelliteInfo(baseTransform, width, height) : null,
    [baseTransform, width, height],
  );
  const satelliteUrl = satelliteInfo?.url ?? null;
  const [satelliteLoaded, setSatelliteLoaded] = useState(false);
  const [satelliteError, setSatelliteError] = useState(false);

  // Reset satellite state when URL changes
  useEffect(() => {
    setSatelliteLoaded(false);
    setSatelliteError(false);
  }, [satelliteUrl]);

  const transform = useMemo(() => {
    if (!baseTransform) return null;
    return {
      ...baseTransform,
      scale: baseTransform.scale * zoom,
      offsetX: baseTransform.offsetX + panX,
      offsetY: baseTransform.offsetY + panY,
    };
  }, [baseTransform, zoom, panX, panY]);

  // Transform for building/road/greenspace positions, which are stored as
  // degree offsets from the active zone's centroid. We adjust offsetX/offsetY
  // so that offsetToSVG(0,0) maps to the zone centroid's position on screen.
  const zoneTransform = useMemo(() => {
    if (!transform || !zone) return null;
    const zcx = zone.coordinates.reduce((s, c) => s + c[0], 0) / zone.coordinates.length;
    const zcy = zone.coordinates.reduce((s, c) => s + c[1], 0) / zone.coordinates.length;
    // toSVG(zcx, zcy) using the combined transform gives the zone centroid's SVG position.
    // offsetToSVG(0, 0, zt) should equal that, i.e. zt.offsetX = that x, zt.offsetY = that y.
    const zoneOriginX = (zcx - transform.cx) * transform.mlon * transform.scale + transform.offsetX;
    const zoneOriginY = -(zcy - transform.cy) * transform.mlat * transform.scale + transform.offsetY;
    return { ...transform, cx: zcx, cy: zcy, offsetX: zoneOriginX, offsetY: zoneOriginY };
  }, [transform, zone]);

  const { startDrag, onDrag, endDrag, isDragging } = useBlockDrag(zoneTransform);

  const snapLines = useSnapLines(
    editedLayout?.buildings ?? [],
    dragState,
    zoneTransform,
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

  // Attach native wheel listener with { passive: false } so preventDefault
  // actually stops the page from scrolling when the mouse is over the canvas.
  // React's onWheel is passive by default and cannot prevent scroll.
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      const factor = e.deltaY > 0 ? 0.9 : 1.1;
      setZoom(zoom * factor);
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
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
      onPointerDown={handleCanvasPointerDown}
      onPointerMove={handleCanvasPointerMove}
      onPointerUp={handleCanvasPointerUp}
    >
      {/* Satellite map background — positioned using the same geographic transform as everything else */}
      {satelliteUrl && !satelliteError && satelliteInfo && transform && (() => {
        const cx = baseTransform!.cx;
        const cy = baseTransform!.cy;
        const [x1, y1] = toSVG(cx - satelliteInfo.halfLonDeg, cy + satelliteInfo.halfLatDeg, transform);
        const [x2, y2] = toSVG(cx + satelliteInfo.halfLonDeg, cy - satelliteInfo.halfLatDeg, transform);
        return (
          <>
            <image
              href={satelliteUrl}
              x={x1}
              y={y1}
              width={x2 - x1}
              height={y2 - y1}
              preserveAspectRatio="none"
              opacity={satelliteLoaded ? 0.7 : 0}
              onLoad={() => setSatelliteLoaded(true)}
              onError={() => setSatelliteError(true)}
              style={{ pointerEvents: 'none' }}
            />
            {/* Dark overlay on top of satellite for contrast */}
            {satelliteLoaded && (
              <rect
                x={x1}
                y={y1}
                width={x2 - x1}
                height={y2 - y1}
                fill="rgba(15, 15, 26, 0.4)"
                style={{ pointerEvents: 'none' }}
              />
            )}
          </>
        );
      })()}

      {/* Grid */}
      {gridLines.map((line, i) => (
        <line
          key={i}
          x1={line.x1} y1={line.y1} x2={line.x2} y2={line.y2}
          stroke={line.isAxis ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)'}
          strokeWidth={line.isAxis ? 1 : 0.5}
        />
      ))}

      {/* Neighboring zones — clickable to switch */}
      {allZones?.filter((z) => z.id !== zone.id && z.coordinates.length >= 3).map((z) => {
        const pts = z.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polygon
            key={z.id}
            points={pts}
            fill={z.color || '#6366f1'}
            fillOpacity={0.15}
            stroke={z.color || '#6366f1'}
            strokeWidth={1.5}
            strokeOpacity={0.5}
            strokeDasharray="6,4"
            style={{ cursor: 'pointer' }}
            onPointerDown={(e) => { e.stopPropagation(); onSelectZone?.(z.id); }}
          />
        );
      })}

      {/* Active zone boundary */}
      <polygon
        points={boundaryPoints}
        fill={zone.color || 'rgba(245,158,11,0.3)'}
        fillOpacity={0.15}
        stroke={zone.color || '#f59e0b'}
        strokeWidth={2}
        strokeOpacity={0.7}
      />
      {/* Dashed inner outline for precision */}
      <polygon
        points={boundaryPoints}
        fill="none"
        stroke="#ffffff"
        strokeWidth={1}
        strokeDasharray="6,4"
        strokeOpacity={0.3}
      />

      {/* Green spaces */}
      {editedLayout.green_spaces.map((gs, i) => {
        const pts = gs.polygon
          .map(([dx, dy]) => offsetToSVG(dx, dy, zoneTransform!))
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
          .map(([dx, dy]) => offsetToSVG(dx, dy, zoneTransform!))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        const strokeW = Math.max(3, metersToPixels(road.width_m, zoneTransform!));
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
          .map(([dx, dy]) => offsetToSVG(dx, dy, zoneTransform!))
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

      {/* Scale bar — 10m reference */}
      {(() => {
        const barMeters = 10;
        const barPx = metersToPixels(barMeters, transform);
        const barY = height - 40;
        const barX = width - 20 - barPx;
        return (
          <g>
            <line x1={barX} y1={barY} x2={barX + barPx} y2={barY}
              stroke="white" strokeWidth={2} />
            <line x1={barX} y1={barY - 4} x2={barX} y2={barY + 4}
              stroke="white" strokeWidth={2} />
            <line x1={barX + barPx} y1={barY - 4} x2={barX + barPx} y2={barY + 4}
              stroke="white" strokeWidth={2} />
            <text x={barX + barPx / 2} y={barY - 8}
              fill="white" fontSize={11} fontWeight="bold" textAnchor="middle"
              style={{ textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>
              {barMeters}m
            </text>
          </g>
        );
      })()}

      {/* Buildings (blocks) */}
      {editedLayout.buildings.map((bldg, i) => (
        <BlockGroup
          key={i}
          block={bldg}
          index={i}
          transform={zoneTransform!}
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
