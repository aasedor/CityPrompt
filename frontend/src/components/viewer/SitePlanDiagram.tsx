import { computeTransform, toSVG, offsetToSVG } from '@/utils/coordTransform';
import { useMemo } from 'react';
import type { SiteZone, LayoutOption, OSMContext, LockedLayers } from '@/types';
import { ZONE_TYPE_CONFIG } from '@/types';

interface SitePlanDiagramProps {
  zone: SiteZone;
  option: LayoutOption;
  referenceContext?: OSMContext | null;
  lockedLayers?: LockedLayers | null;
  siblingZones?: SiteZone[];
  width?: number;
  height?: number;
  showLabels?: boolean;
  showDimensions?: boolean;
}


export function SitePlanDiagram({
  zone,
  option,
  referenceContext,
  lockedLayers,
  siblingZones,
  width = 260,
  height = 180,
  showLabels = true,
  showDimensions = true,
}: SitePlanDiagramProps) {
  const transform = useMemo(
    () => computeTransform(zone.coordinates, width, height),
    [zone.coordinates, width, height],
  );

  // Zone boundary polygon SVG points
  const boundaryPoints = useMemo(() => {
    return zone.coordinates
      .map((c) => toSVG(c[0], c[1], transform))
      .map(([x, y]) => `${x},${y}`)
      .join(' ');
  }, [zone.coordinates, transform]);

  // Compute zone dimensions in meters
  const dimensions = useMemo(() => {
    const lngs = zone.coordinates.map((c) => c[0]);
    const lats = zone.coordinates.map((c) => c[1]);
    const w = (Math.max(...lngs) - Math.min(...lngs)) * transform.mlon;
    const d = (Math.max(...lats) - Math.min(...lats)) * transform.mlat;
    return { width: Math.round(w), depth: Math.round(d) };
  }, [zone.coordinates, transform]);

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="rounded border border-gray-200 bg-gray-50"
    >
      {/* Background */}
      <rect width={width} height={height} fill="#f9fafb" />

      {/* Reference water features */}
      {referenceContext?.water.map((w, i) => {
        if (w.coordinates.length < 3) return null;
        const pts = w.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polygon
            key={`water-${i}`}
            points={pts}
            fill="#3b82f6"
            fillOpacity={0.3}
            stroke="#3b82f6"
            strokeWidth={0.5}
            strokeOpacity={0.5}
          />
        );
      })}

      {/* Reference parks */}
      {referenceContext?.parks.map((p, i) => {
        if (p.coordinates.length < 3) return null;
        const pts = p.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polygon
            key={`park-${i}`}
            points={pts}
            fill="#22c55e"
            fillOpacity={0.2}
            stroke="#22c55e"
            strokeWidth={0.5}
            strokeOpacity={0.4}
          />
        );
      })}

      {/* Reference buildings */}
      {referenceContext?.buildings.map((b, i) => {
        if (b.coordinates.length < 3) return null;
        const pts = b.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        return (
          <polygon
            key={`ref-bldg-${i}`}
            points={pts}
            fill="none"
            stroke="#9ca3af"
            strokeWidth={0.7}
            strokeDasharray="2,2"
            strokeOpacity={0.6}
          />
        );
      })}

      {/* Reference roads */}
      {referenceContext?.roads.map((r, i) => {
        if (r.coordinates.length < 2) return null;
        const pts = r.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        const strokeW = Math.max(1, (r.width_m * transform.scale) / 2);
        return (
          <polyline
            key={`ref-road-${i}`}
            points={pts}
            fill="none"
            stroke="#6b7280"
            strokeWidth={strokeW}
            strokeOpacity={0.3}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        );
      })}

      {/* User-drawn sibling zones */}
      {siblingZones?.map((sz, i) => {
        if (sz.id === zone.id || sz.coordinates.length < 3) return null;
        const color = ZONE_TYPE_CONFIG[sz.zone_type]?.color || sz.color;
        const pts = sz.coordinates
          .map((c) => toSVG(c[0], c[1], transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');

        // Roads render as polylines, everything else as polygons
        if (sz.zone_type === 'road') {
          const roadW = Math.max(2, ((sz.properties?.width as number) || 8) * transform.scale);
          return (
            <polyline
              key={`sib-${i}`}
              points={pts}
              fill="none"
              stroke={color}
              strokeWidth={roadW}
              strokeOpacity={0.45}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          );
        }

        return (
          <polygon
            key={`sib-${i}`}
            points={pts}
            fill={color}
            fillOpacity={sz.zone_type === 'site_boundary' ? 0 : 0.25}
            stroke={color}
            strokeWidth={sz.zone_type === 'site_boundary' ? 1.5 : 0.8}
            strokeDasharray={sz.zone_type === 'site_boundary' ? '4,3' : undefined}
            strokeOpacity={0.6}
          />
        );
      })}

      {/* Zone boundary */}
      <polygon
        points={boundaryPoints}
        fill="none"
        stroke="#f59e0b"
        strokeWidth={1.5}
        strokeDasharray="4,3"
        strokeOpacity={0.8}
      />

      {/* Generated green spaces */}
      {option.green_spaces.map((gs, i) => {
        const pts = gs.polygon
          .map(([dx, dy]) => offsetToSVG(dx, dy, transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        const isLocked = lockedLayers?.green_spaces.includes(i);
        return (
          <g key={`gs-${i}`}>
            <polygon
              points={pts}
              fill="#22c55e"
              fillOpacity={0.35}
              stroke="#16a34a"
              strokeWidth={0.5}
            />
            {isLocked && (
              <polygon
                points={pts}
                fill="#fbbf24"
                fillOpacity={0.2}
                stroke="#f59e0b"
                strokeWidth={1}
                strokeDasharray="3,2"
              />
            )}
          </g>
        );
      })}

      {/* Generated roads */}
      {option.roads.map((road, i) => {
        const pts = road.centerline
          .map(([dx, dy]) => offsetToSVG(dx, dy, transform))
          .map(([x, y]) => `${x},${y}`)
          .join(' ');
        const strokeW = Math.max(2, road.width_m * transform.scale);
        const isLocked = lockedLayers?.roads.includes(i);
        return (
          <g key={`road-${i}`}>
            <polyline
              points={pts}
              fill="none"
              stroke="#4b5563"
              strokeWidth={strokeW}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeOpacity={0.7}
            />
            {isLocked && (
              <polyline
                points={pts}
                fill="none"
                stroke="#f59e0b"
                strokeWidth={strokeW + 2}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity={0.3}
              />
            )}
          </g>
        );
      })}

      {/* Generated buildings */}
      {option.buildings.map((bldg, i) => {
        const [cx, cy] = offsetToSVG(bldg.center_x, bldg.center_y, transform);
        const w = bldg.width_m * transform.scale;
        const h = bldg.depth_m * transform.scale;
        const isLocked = lockedLayers?.buildings.includes(i);
        return (
          <g key={`bldg-${i}`}>
            <rect
              x={-w / 2}
              y={-h / 2}
              width={w}
              height={h}
              fill={bldg.building_type === 'commercial' ? '#8b5cf6' : '#ec4899'}
              fillOpacity={0.6}
              stroke={bldg.building_type === 'commercial' ? '#7c3aed' : '#db2777'}
              strokeWidth={0.8}
              transform={`translate(${cx},${cy}) rotate(${-bldg.rotation_deg})`}
              rx={1}
            />
            {isLocked && (
              <rect
                x={-w / 2 - 1}
                y={-h / 2 - 1}
                width={w + 2}
                height={h + 2}
                fill="none"
                stroke="#f59e0b"
                strokeWidth={1.5}
                strokeDasharray="3,2"
                transform={`translate(${cx},${cy}) rotate(${-bldg.rotation_deg})`}
              />
            )}
            {showLabels && w > 8 && (
              <text
                x={cx}
                y={cy}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={Math.min(8, w * 0.6)}
                fill="white"
                fontWeight="bold"
                style={{ pointerEvents: 'none' }}
              >
                {i + 1}
              </text>
            )}
          </g>
        );
      })}

      {/* Dimension annotations */}
      {showDimensions && (
        <>
          <text
            x={width / 2}
            y={height - 4}
            textAnchor="middle"
            fontSize={8}
            fill="#6b7280"
          >
            {dimensions.width}m x {dimensions.depth}m
          </text>
        </>
      )}
    </svg>
  );
}
