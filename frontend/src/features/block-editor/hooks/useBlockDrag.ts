import { useCallback, useRef } from 'react';
import { useBlockEditorStore, type DragType } from '@/store/blockEditorStore';
import { offsetToSVG, pixelsToMeters, type Transform } from '@/utils/coordTransform';

export function useBlockDrag(transform: Transform | null) {
  const {
    dragState, setDragState, moveBlock, resizeBlock, rotateBlock,
    pushUndoSnapshot, editedLayout, selectedBlockIndices, moveSelectedBlocks,
  } = useBlockEditorStore();
  const hasDraggedRef = useRef(false);

  const startDrag = useCallback((
    e: React.PointerEvent,
    blockIndex: number,
    type: DragType,
  ) => {
    if (!editedLayout || !transform) return;
    e.stopPropagation();
    e.preventDefault();
    (e.target as Element).setPointerCapture(e.pointerId);

    const bldg = editedLayout.buildings[blockIndex];
    pushUndoSnapshot();
    hasDraggedRef.current = false;

    // Capture starting positions of all selected blocks for multi-move
    const isMulti = type === 'move' && selectedBlockIndices.length > 1 && selectedBlockIndices.includes(blockIndex);
    const multiStartPositions = isMulti
      ? selectedBlockIndices.map((i) => ({
          cx: editedLayout.buildings[i].center_x,
          cy: editedLayout.buildings[i].center_y,
        }))
      : undefined;

    setDragState({
      type,
      blockIndex,
      startX: e.clientX,
      startY: e.clientY,
      startCenterX: bldg.center_x,
      startCenterY: bldg.center_y,
      startWidthM: bldg.width_m,
      startDepthM: bldg.depth_m,
      startRotation: bldg.rotation_deg,
      multiStartPositions,
    });
  }, [editedLayout, transform, pushUndoSnapshot, setDragState, selectedBlockIndices]);

  const onDrag = useCallback((e: React.PointerEvent) => {
    if (!dragState || !transform) return;
    hasDraggedRef.current = true;
    const dx = e.clientX - dragState.startX;
    const dy = e.clientY - dragState.startY;

    if (dragState.type === 'move') {
      // Convert pixel delta to degree delta
      const degDx = dx / (transform.scale * transform.mlon);
      const degDy = -dy / (transform.scale * transform.mlat);

      if (dragState.multiStartPositions && selectedBlockIndices.length > 1) {
        // Multi-select move: apply same delta to all selected blocks
        // We use moveSelectedBlocks which applies a delta, but we need absolute positioning
        // since drag accumulates. Use the start positions + current delta.
        const { editedLayout: layout } = useBlockEditorStore.getState();
        if (!layout) return;
        const cloned = JSON.parse(JSON.stringify(layout)) as typeof layout;
        for (let si = 0; si < selectedBlockIndices.length; si++) {
          const idx = selectedBlockIndices[si];
          const start = dragState.multiStartPositions[si];
          if (start && cloned.buildings[idx]) {
            cloned.buildings[idx].center_x = start.cx + degDx;
            cloned.buildings[idx].center_y = start.cy + degDy;
          }
        }
        useBlockEditorStore.setState({ editedLayout: cloned });
      } else {
        moveBlock(dragState.blockIndex, dragState.startCenterX + degDx, dragState.startCenterY + degDy);
      }
    } else if (dragState.type === 'rotate') {
      // Compute angle from block center to cursor using atan2
      // so rotation follows the cursor naturally in all directions.
      const bldg = useBlockEditorStore.getState().editedLayout?.buildings[dragState.blockIndex];
      if (!bldg) return;
      const [cx, cy] = offsetToSVG(bldg.center_x, bldg.center_y, transform);
      const svgRect = (e.currentTarget as Element).closest('svg')?.getBoundingClientRect();
      if (!svgRect) return;
      const cursorX = e.clientX - svgRect.left;
      const cursorY = e.clientY - svgRect.top;
      // atan2: angle from block center to cursor, 0° = up (north)
      const angle = Math.atan2(-(cursorX - cx), -(cursorY - cy)) * (180 / Math.PI);
      rotateBlock(dragState.blockIndex, ((angle % 360) + 360) % 360);
    } else if (dragState.type.startsWith('resize')) {
      // Rotate screen-space delta into the block's local coordinate system
      // so resizing works correctly regardless of block rotation.
      const rotRad = dragState.startRotation * Math.PI / 180;
      const cos = Math.cos(rotRad);
      const sin = Math.sin(rotRad);
      const localDx = dx * cos - dy * sin;
      const localDy = dx * sin + dy * cos;

      const metersDx = pixelsToMeters(localDx, transform);
      const metersDy = pixelsToMeters(localDy, transform);
      let newW = dragState.startWidthM;
      let newD = dragState.startDepthM;

      const handle = dragState.type;
      if (handle.includes('e')) newW = dragState.startWidthM + metersDx;
      if (handle.includes('w')) newW = dragState.startWidthM - metersDx;
      if (handle.includes('s')) newD = dragState.startDepthM + metersDy;
      if (handle.includes('n')) newD = dragState.startDepthM - metersDy;

      resizeBlock(dragState.blockIndex, newW, newD);
    }
  }, [dragState, transform, moveBlock, resizeBlock, rotateBlock, selectedBlockIndices, moveSelectedBlocks]);

  const endDrag = useCallback((e: React.PointerEvent) => {
    if (!dragState) return;
    (e.target as Element).releasePointerCapture(e.pointerId);
    setDragState(null);
  }, [dragState, setDragState]);

  return { startDrag, onDrag, endDrag, isDragging: !!dragState, hasDragged: hasDraggedRef };
}
