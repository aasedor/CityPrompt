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
    selectedBlockIndex, deleteBlock, duplicateBlock, undo, redo, selectBlock,
    editedLayout, moveBlock, pushUndoSnapshot, panX, panY, setPan, zone,
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
        if (selectedBlockIndex !== null) {
          e.preventDefault();
          deleteBlock(selectedBlockIndex);
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (selectedBlockIndex !== null) {
          duplicateBlock(selectedBlockIndex);
        }
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

      // WASD and Arrow keys: move selected block or pan map
      if (MOVE_KEYS.has(e.key) && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();

        // Determine direction in screen space (dx right, dy down)
        let dx = 0;
        let dy = 0;
        if (e.key === 'ArrowLeft' || e.key === 'a') dx = -1;
        if (e.key === 'ArrowRight' || e.key === 'd') dx = 1;
        if (e.key === 'ArrowUp' || e.key === 'w') dy = -1;
        if (e.key === 'ArrowDown' || e.key === 's') dy = 1;

        if (selectedBlockIndex !== null && editedLayout) {
          // Move the selected block
          const bldg = editedLayout.buildings[selectedBlockIndex];
          if (!bldg) return;

          // Push undo only once per key-hold sequence
          if (!moveUndoPushedRef.current) {
            pushUndoSnapshot();
            moveUndoPushedRef.current = true;
          }

          const lat = zone?.coordinates?.[0]?.[1] ?? bldg.center_y;
          const degX = (BLOCK_MOVE_STEP_METERS * dx) / metersPerDegLon(lat);
          const degY = (BLOCK_MOVE_STEP_METERS * -dy) / METERS_PER_DEG_LAT; // screen-down is lat-negative
          moveBlock(selectedBlockIndex, bldg.center_x + degX, bldg.center_y + degY);
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
  }, [selectedBlockIndex, deleteBlock, duplicateBlock, undo, redo, selectBlock,
      editedLayout, moveBlock, pushUndoSnapshot, panX, panY, setPan, zone]);
}
