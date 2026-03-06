import { useCallback, useRef } from 'react';
import { useBlockEditorStore, type DragType } from '@/store/blockEditorStore';
import { pixelsToMeters, type Transform } from '@/utils/coordTransform';

export function useBlockDrag(transform: Transform | null) {
  const {
    dragState, setDragState, moveBlock, resizeBlock, rotateBlock,
    pushUndoSnapshot, editedLayout,
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
    });
  }, [editedLayout, transform, pushUndoSnapshot, setDragState]);

  const onDrag = useCallback((e: React.PointerEvent) => {
    if (!dragState || !transform) return;
    hasDraggedRef.current = true;
    const dx = e.clientX - dragState.startX;
    const dy = e.clientY - dragState.startY;

    if (dragState.type === 'move') {
      // Convert pixel delta to degree delta
      const degDx = dx / (transform.scale * transform.mlon);
      const degDy = -dy / (transform.scale * transform.mlat);
      moveBlock(dragState.blockIndex, dragState.startCenterX + degDx, dragState.startCenterY + degDy);
    } else if (dragState.type === 'rotate') {
      const angleDelta = dx * 0.5; // 0.5 degrees per pixel
      rotateBlock(dragState.blockIndex, dragState.startRotation + angleDelta);
    } else if (dragState.type.startsWith('resize')) {
      // Rotate screen-space delta into the block's local coordinate system
      // so resizing works correctly regardless of block rotation.
      // SVG renders with rotate(-rotation_deg), so local-to-screen rotation angle is -rotation_deg.
      const rotRad = dragState.startRotation * Math.PI / 180;
      const cos = Math.cos(rotRad);
      const sin = Math.sin(rotRad);
      // Project screen delta onto block-local axes
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
  }, [dragState, transform, moveBlock, resizeBlock, rotateBlock]);

  const endDrag = useCallback((e: React.PointerEvent) => {
    if (!dragState) return;
    (e.target as Element).releasePointerCapture(e.pointerId);
    setDragState(null);
  }, [dragState, setDragState]);

  return { startDrag, onDrag, endDrag, isDragging: !!dragState, hasDragged: hasDraggedRef };
}
