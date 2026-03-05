import { offsetToSVG, metersToPixels, type Transform } from '@/utils/coordTransform';
import type { LayoutBuildingData } from '@/types';
import type { DragType } from '@/store/blockEditorStore';

interface BlockGroupProps {
  block: LayoutBuildingData;
  index: number;
  transform: Transform;
  isSelected: boolean;
  isHovered: boolean;
  showDimensions: boolean;
  onPointerDown: (e: React.PointerEvent, index: number, type: DragType) => void;
  onHover: (index: number | null) => void;
  onClick: (index: number) => void;
}

const BUILDING_COLORS: Record<string, { fill: string; stroke: string }> = {
  residential: { fill: '#ec4899', stroke: '#db2777' },
  commercial: { fill: '#8b5cf6', stroke: '#7c3aed' },
  mixed_use: { fill: '#f59e0b', stroke: '#d97706' },
  institutional: { fill: '#06b6d4', stroke: '#0891b2' },
  park_plaza: { fill: '#22c55e', stroke: '#16a34a' },
};

export function BlockGroup({
  block, index, transform, isSelected, isHovered,
  showDimensions, onPointerDown, onHover, onClick,
}: BlockGroupProps) {
  const [cx, cy] = offsetToSVG(block.center_x, block.center_y, transform);
  const w = metersToPixels(block.width_m, transform);
  const h = metersToPixels(block.depth_m, transform);
  const colors = BUILDING_COLORS[block.building_type] || BUILDING_COLORS.residential;
  const handleSize = 6;

  return (
    <g
      onPointerEnter={() => onHover(index)}
      onPointerLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Main block rectangle */}
      <rect
        x={-w / 2}
        y={-h / 2}
        width={w}
        height={h}
        fill={colors.fill}
        fillOpacity={isSelected ? 0.8 : isHovered ? 0.7 : 0.55}
        stroke={isSelected ? '#ffffff' : isHovered ? '#e2e8f0' : colors.stroke}
        strokeWidth={isSelected ? 2 : 1}
        transform={`translate(${cx},${cy}) rotate(${-block.rotation_deg})`}
        rx={2}
        onPointerDown={(e) => {
          e.stopPropagation();
          onClick(index);
          onPointerDown(e, index, 'move');
        }}
      />

      {/* Block label */}
      {w > 16 && (
        <text
          x={cx}
          y={cy - (showDimensions && w > 30 ? 4 : 0)}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={Math.min(11, w * 0.35)}
          fill="white"
          fontWeight="bold"
          style={{ pointerEvents: 'none', userSelect: 'none' }}
        >
          {(block as any).name || `#${index + 1}`}
        </text>
      )}

      {/* Dimensions label */}
      {showDimensions && w > 30 && (
        <text
          x={cx}
          y={cy + 8}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={Math.min(8, w * 0.25)}
          fill="rgba(255,255,255,0.7)"
          style={{ pointerEvents: 'none', userSelect: 'none' }}
        >
          {Math.round(block.width_m)}x{Math.round(block.depth_m)}m
        </text>
      )}

      {/* Selection handles */}
      {isSelected && (
        <g transform={`translate(${cx},${cy}) rotate(${-block.rotation_deg})`}>
          {/* Corner resize handles */}
          {([
            ['resize-nw', -w / 2, -h / 2],
            ['resize-ne', w / 2, -h / 2],
            ['resize-se', w / 2, h / 2],
            ['resize-sw', -w / 2, h / 2],
          ] as [DragType, number, number][]).map(([type, hx, hy]) => (
            <rect
              key={type}
              x={hx - handleSize / 2}
              y={hy - handleSize / 2}
              width={handleSize}
              height={handleSize}
              fill="white"
              stroke="#6366f1"
              strokeWidth={1.5}
              rx={1}
              style={{ cursor: type.includes('nw') || type.includes('se') ? 'nwse-resize' : 'nesw-resize' }}
              onPointerDown={(e) => onPointerDown(e, index, type)}
            />
          ))}

          {/* Edge resize handles */}
          {([
            ['resize-n', 0, -h / 2, 'ns-resize'],
            ['resize-s', 0, h / 2, 'ns-resize'],
            ['resize-e', w / 2, 0, 'ew-resize'],
            ['resize-w', -w / 2, 0, 'ew-resize'],
          ] as [DragType, number, number, string][]).map(([type, hx, hy, cursor]) => (
            <rect
              key={type}
              x={hx - handleSize / 2}
              y={hy - handleSize / 2}
              width={handleSize}
              height={handleSize}
              fill="white"
              stroke="#6366f1"
              strokeWidth={1}
              rx={1}
              style={{ cursor }}
              onPointerDown={(e) => onPointerDown(e, index, type)}
            />
          ))}

          {/* Rotate handle */}
          <line
            x1={0} y1={-h / 2}
            x2={0} y2={-h / 2 - 18}
            stroke="#6366f1"
            strokeWidth={1.5}
            strokeDasharray="3,2"
          />
          <circle
            cx={0}
            cy={-h / 2 - 22}
            r={5}
            fill="#6366f1"
            stroke="white"
            strokeWidth={1.5}
            style={{ cursor: 'grab' }}
            onPointerDown={(e) => onPointerDown(e, index, 'rotate')}
          />
        </g>
      )}
    </g>
  );
}
