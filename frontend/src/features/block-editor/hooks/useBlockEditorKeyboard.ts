import { useEffect, useRef } from 'react';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/utils/coordTransform';

/** How many meters a single key press moves a selected block */
const BLOCK_MOVE_STEP_METERS = 1;
/** How many pixels a single key press pans the map */
const PAN_STEP_PX = 20;

const MOVE_KEYS = new Set(['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']);

export function useBlockEditorKeyboard() {
  const {
    selectedBlockIndex, selectedBlockIndices,
    deleteBlock, deleteSelectedBlocks,
    duplicateBlock, duplicateSelectedBlocks,
    copyBlock, copySelectedBlocks, pasteBlock,
    undo, redo, selectBlock,
    editedLayout, moveBlock, moveSelectedBlocks, pushUndoSnapshot,
    panX, panY, setPan, zone,
  } = useBlockEditorStore();

  // Track whether we've already pushed an undo snapshot for the current key-move sequence
  const moveUndoPushedRef = useRef(false);

  useEffect(() => {
    const handleKeyUp = (e: KeyboardEvent) => {
      if (MOVE_KEYS.has(e.key)) {
        moveUndoPushedRef.current = false;
      }
    };

    const handler = (e: KeyboardEvent) => {
      // Don't intercept when typing in inputs
      const tag = (e.target as HTMLElement).tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      if (e.key === 'Escape') {
        selectBlock(null);
        return;
      }

      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedBlockIndices.length > 1) {
          e.preventDefault();
          deleteSelectedBlocks();
        } else if (selectedBlockIndex !== null) {
          e.preventDefault();
          deleteBlock(selectedBlockIndex);
        }
        return;
      }

      // Ctrl+A — select all blocks
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        if (editedLayout && editedLayout.buildings.length > 0) {
          const allIndices = editedLayout.buildings.map((_, i) => i);
          useBlockEditorStore.setState({
            selectedBlockIndices: allIndices,
            selectedBlockIndex: allIndices[allIndices.length - 1],
            selectedElementType: 'building',
            selectedElementIndex: allIndices[allIndices.length - 1],
          });
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (selectedBlockIndices.length > 1) {
          duplicateSelectedBlocks();
        } else if (selectedBlockIndex !== null) {
          duplicateBlock(selectedBlockIndex);
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        if (selectedBlockIndices.length > 1) {
          e.preventDefault();
          copySelectedBlocks();
        } else if (selectedBlockIndex !== null) {
          e.preventDefault();
          copyBlock(selectedBlockIndex);
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        e.preventDefault();
        pasteBlock();
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          redo();
        } else {
          undo();
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
        e.preventDefault();
        redo();
        return;
      }

      // WASD and Arrow keys: move selected block(s) or pan map
      if (MOVE_KEYS.has(e.key) && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();

        // Determine direction in screen space (dx right, dy down)
        let dx = 0;
        let dy = 0;
        if (e.key === 'ArrowLeft' || e.key === 'a') dx = -1;
        if (e.key === 'ArrowRight' || e.key === 'd') dx = 1;
        if (e.key === 'ArrowUp' || e.key === 'w') dy = -1;
        if (e.key === 'ArrowDown' || e.key === 's') dy = 1;

        if (selectedBlockIndices.length > 0 && editedLayout) {
          // Move selected block(s)
          const refBlock = editedLayout.buildings[selectedBlockIndices[0]];
          if (!refBlock) return;

          // Push undo only once per key-hold sequence
          if (!moveUndoPushedRef.current) {
            pushUndoSnapshot();
            moveUndoPushedRef.current = true;
          }

          const lat = zone?.coordinates?.[0]?.[1] ?? refBlock.center_y;
          const degX = (BLOCK_MOVE_STEP_METERS * dx) / metersPerDegLon(lat);
          const degY = (BLOCK_MOVE_STEP_METERS * -dy) / METERS_PER_DEG_LAT;

          if (selectedBlockIndices.length > 1) {
            moveSelectedBlocks(degX, degY);
          } else if (selectedBlockIndex !== null) {
            const bldg = editedLayout.buildings[selectedBlockIndex];
            if (bldg) moveBlock(selectedBlockIndex, bldg.center_x + degX, bldg.center_y + degY);
          }
        } else {
          // Pan the map
          setPan(panX - dx * PAN_STEP_PX, panY - dy * PAN_STEP_PX);
        }
        return;
      }
    };

    window.addEventListener('keydown', handler);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handler);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [selectedBlockIndex, selectedBlockIndices,
      deleteBlock, deleteSelectedBlocks,
      duplicateBlock, duplicateSelectedBlocks,
      copyBlock, copySelectedBlocks, pasteBlock,
      undo, redo, selectBlock,
      editedLayout, moveBlock, moveSelectedBlocks, pushUndoSnapshot,
      panX, panY, setPan, zone]);
}
