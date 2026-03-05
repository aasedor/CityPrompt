import { useMemo } from 'react';
import { offsetToSVG, type Transform } from '@/utils/coordTransform';
import type { LayoutBuildingData } from '@/types';
import type { DragState } from '@/store/blockEditorStore';

export interface SnapLine {
  x1: number; y1: number;
  x2: number; y2: number;
  type: 'center' | 'edge';
}

const SNAP_THRESHOLD_PX = 8;

export function useSnapLines(
  buildings: LayoutBuildingData[],
  dragState: DragState | null,
  transform: Transform | null,
  svgW: number,
  svgH: number,
): SnapLine[] {
  return useMemo(() => {
    if (!dragState || dragState.type !== 'move' || !transform || buildings.length < 2) return [];

    const dragIdx = dragState.blockIndex;
    const dragBlock = buildings[dragIdx];
    if (!dragBlock) return [];

    const [dragCx, dragCy] = offsetToSVG(dragBlock.center_x, dragBlock.center_y, transform);
    const lines: SnapLine[] = [];

    for (let i = 0; i < buildings.length; i++) {
      if (i === dragIdx) continue;
      const other = buildings[i];
      const [otherCx, otherCy] = offsetToSVG(other.center_x, other.center_y, transform);

      // Vertical center alignment
      if (Math.abs(dragCx - otherCx) < SNAP_THRESHOLD_PX) {
        lines.push({ x1: otherCx, y1: 0, x2: otherCx, y2: svgH, type: 'center' });
      }
      // Horizontal center alignment
      if (Math.abs(dragCy - otherCy) < SNAP_THRESHOLD_PX) {
        lines.push({ x1: 0, y1: otherCy, x2: svgW, y2: otherCy, type: 'center' });
      }
    }

    return lines;
  }, [buildings, dragState, transform, svgW, svgH]);
}
