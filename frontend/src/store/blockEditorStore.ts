import { create } from 'zustand';
import type { SiteZone, LayoutOption, LayoutBuildingData, LayoutRoadData, LayoutGreenSpaceData } from '@/types';

export type DragType = 'move' | 'resize-nw' | 'resize-ne' | 'resize-se' | 'resize-sw'
  | 'resize-n' | 'resize-e' | 'resize-s' | 'resize-w' | 'rotate';

export interface DragState {
  type: DragType;
  blockIndex: number;
  startX: number;
  startY: number;
  startCenterX: number;
  startCenterY: number;
  startWidthM: number;
  startDepthM: number;
  startRotation: number;
  /** For multi-select move: starting positions of all selected blocks */
  multiStartPositions?: { cx: number; cy: number }[];
}

interface BlockEditorState {
  zoneId: string | null;
  zone: SiteZone | null;
  projectId: string | null;
  options: LayoutOption[];
  activeOptionIndex: number;
  editedLayout: LayoutOption | null;
  /** Primary selected block (used by properties panel) */
  selectedBlockIndex: number | null;
  /** All selected block indices (for multi-select) */
  selectedBlockIndices: number[];
  selectedElementType: 'building' | 'road' | 'green_space' | null;
  selectedElementIndex: number | null;
  hoveredBlockIndex: number | null;
  dragState: DragState | null;
  zoom: number;
  panX: number;
  panY: number;
  showGrid: boolean;
  snapToGrid: boolean;
  gridSizeMeters: number;
  showDimensions: boolean;
  undoStack: LayoutOption[];
  redoStack: LayoutOption[];
  layoutCache: Record<string, LayoutOption[]>;
  clipboard: LayoutBuildingData[] | null;

  initEditor: (projectId: string, zone: SiteZone, options: LayoutOption[]) => void;
  resetEditor: () => void;
  getCachedLayout: (zoneId: string) => LayoutOption[] | null;
  cacheLayout: (zoneId: string, options: LayoutOption[]) => void;
  switchOption: (index: number) => void;
  setDragState: (state: DragState | null) => void;
  /** Plain click — replace selection with single block */
  selectBlock: (index: number | null) => void;
  /** Shift/Ctrl click — toggle block in multi-selection */
  toggleBlockSelection: (index: number) => void;
  selectElement: (type: 'building' | 'road' | 'green_space' | null, index: number | null) => void;
  updateRoadProperties: (index: number, props: Partial<LayoutRoadData>) => void;
  updateGreenSpaceProperties: (index: number, props: Partial<LayoutGreenSpaceData>) => void;
  hoverBlock: (index: number | null) => void;
  moveBlock: (index: number, newCenterX: number, newCenterY: number) => void;
  /** Move all selected blocks by a delta (degrees) */
  moveSelectedBlocks: (dxDeg: number, dyDeg: number) => void;
  resizeBlock: (index: number, newWidthM: number, newDepthM: number) => void;
  rotateBlock: (index: number, newRotationDeg: number) => void;
  updateBlockProperties: (index: number, props: Partial<LayoutBuildingData>) => void;
  addBlock: (block: LayoutBuildingData) => void;
  deleteBlock: (index: number) => void;
  /** Delete all selected blocks */
  deleteSelectedBlocks: () => void;
  duplicateBlock: (index: number) => void;
  /** Duplicate all selected blocks */
  duplicateSelectedBlocks: () => void;
  copyBlock: (index: number) => void;
  /** Copy all selected blocks to clipboard */
  copySelectedBlocks: () => void;
  pasteBlock: () => void;
  undo: () => void;
  redo: () => void;
  pushUndoSnapshot: () => void;
  setZoom: (zoom: number) => void;
  setPan: (x: number, y: number) => void;
  toggleGrid: () => void;
  toggleSnapToGrid: () => void;
  toggleDimensions: () => void;
}

function cloneLayout(layout: LayoutOption): LayoutOption {
  return JSON.parse(JSON.stringify(layout));
}

const CLEAR_SELECTION = {
  selectedBlockIndex: null as number | null,
  selectedBlockIndices: [] as number[],
  selectedElementType: null as BlockEditorState['selectedElementType'],
  selectedElementIndex: null as number | null,
};

export const useBlockEditorStore = create<BlockEditorState>((set, get) => ({
  zoneId: null,
  zone: null,
  projectId: null,
  options: [],
  activeOptionIndex: 0,
  editedLayout: null,
  selectedBlockIndex: null,
  selectedBlockIndices: [],
  selectedElementType: null,
  selectedElementIndex: null,
  hoveredBlockIndex: null,
  dragState: null,
  zoom: 1,
  panX: 0,
  panY: 0,
  showGrid: true,
  snapToGrid: false,
  gridSizeMeters: 5,
  showDimensions: true,
  undoStack: [],
  redoStack: [],
  layoutCache: {},
  clipboard: null,

  initEditor: (projectId, zone, options) => {
    const editedLayout = options.length > 0 ? cloneLayout(options[0]) : null;
    set({
      projectId, zoneId: zone.id, zone, options,
      activeOptionIndex: 0, editedLayout,
      ...CLEAR_SELECTION, hoveredBlockIndex: null, dragState: null,
      undoStack: [], redoStack: [],
      zoom: 1, panX: 0, panY: 0,
    });
  },

  resetEditor: () => set({
    zoneId: null, zone: null, projectId: null, options: [],
    activeOptionIndex: 0, editedLayout: null,
    ...CLEAR_SELECTION, hoveredBlockIndex: null, dragState: null,
    undoStack: [], redoStack: [],
  }),

  getCachedLayout: (zoneId) => {
    const cached = get().layoutCache[zoneId];
    return cached?.length ? cached : null;
  },

  cacheLayout: (zoneId, options) => {
    set({ layoutCache: { ...get().layoutCache, [zoneId]: options } });
  },

  switchOption: (index) => {
    const { options } = get();
    if (index < 0 || index >= options.length) return;
    set({
      activeOptionIndex: index,
      editedLayout: cloneLayout(options[index]),
      ...CLEAR_SELECTION,
      undoStack: [], redoStack: [],
    });
  },

  setDragState: (dragState) => set({ dragState }),

  selectBlock: (index) => set({
    selectedBlockIndex: index,
    selectedBlockIndices: index !== null ? [index] : [],
    selectedElementType: index !== null ? 'building' : null,
    selectedElementIndex: index,
  }),

  toggleBlockSelection: (index) => {
    const { selectedBlockIndices } = get();
    let next: number[];
    if (selectedBlockIndices.includes(index)) {
      next = selectedBlockIndices.filter((i) => i !== index);
    } else {
      next = [...selectedBlockIndices, index];
    }
    // Primary = last toggled-on, or last in list
    const primary = next.length > 0 ? next[next.length - 1] : null;
    set({
      selectedBlockIndices: next,
      selectedBlockIndex: primary,
      selectedElementType: primary !== null ? 'building' : null,
      selectedElementIndex: primary,
    });
  },

  selectElement: (type, index) => set({
    selectedElementType: type,
    selectedElementIndex: index,
    selectedBlockIndex: type === 'building' ? index : null,
    selectedBlockIndices: type === 'building' && index !== null ? [index] : [],
  }),

  updateRoadProperties: (index, props) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.roads[index] = { ...layout.roads[index], ...props };
    set({ editedLayout: layout });
  },
  updateGreenSpaceProperties: (index, props) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.green_spaces[index] = { ...layout.green_spaces[index], ...props };
    set({ editedLayout: layout });
  },
  hoverBlock: (index) => set({ hoveredBlockIndex: index }),

  pushUndoSnapshot: () => {
    const { editedLayout, undoStack } = get();
    if (!editedLayout) return;
    set({ undoStack: [...undoStack.slice(-49), cloneLayout(editedLayout)], redoStack: [] });
  },

  moveBlock: (index, newCenterX, newCenterY) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    const layout = cloneLayout(editedLayout);
    layout.buildings[index].center_x = newCenterX;
    layout.buildings[index].center_y = newCenterY;
    set({ editedLayout: layout });
  },

  moveSelectedBlocks: (dxDeg, dyDeg) => {
    const { editedLayout, selectedBlockIndices } = get();
    if (!editedLayout || selectedBlockIndices.length === 0) return;
    const layout = cloneLayout(editedLayout);
    for (const idx of selectedBlockIndices) {
      const b = layout.buildings[idx];
      if (b) {
        b.center_x += dxDeg;
        b.center_y += dyDeg;
      }
    }
    set({ editedLayout: layout });
  },

  resizeBlock: (index, newWidthM, newDepthM) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    const layout = cloneLayout(editedLayout);
    layout.buildings[index].width_m = Math.max(3, newWidthM);
    layout.buildings[index].depth_m = Math.max(3, newDepthM);
    set({ editedLayout: layout });
  },

  rotateBlock: (index, newRotationDeg) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    const layout = cloneLayout(editedLayout);
    layout.buildings[index].rotation_deg = ((newRotationDeg % 360) + 360) % 360;
    set({ editedLayout: layout });
  },

  updateBlockProperties: (index, props) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.buildings[index] = { ...layout.buildings[index], ...props };
    set({ editedLayout: layout });
  },

  addBlock: (block) => {
    const { editedLayout } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.buildings.push({ ...block });
    const newIdx = layout.buildings.length - 1;
    set({ editedLayout: layout, selectedBlockIndex: newIdx, selectedBlockIndices: [newIdx] });
  },

  deleteBlock: (index) => {
    const { editedLayout, selectedBlockIndex, selectedBlockIndices } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.buildings.splice(index, 1);
    // Adjust indices after removal
    const newIndices = selectedBlockIndices
      .filter((i) => i !== index)
      .map((i) => (i > index ? i - 1 : i));
    const newPrimary = newIndices.length > 0 ? newIndices[newIndices.length - 1]
      : selectedBlockIndex === index ? null : selectedBlockIndex;
    set({
      editedLayout: layout,
      selectedBlockIndex: newPrimary,
      selectedBlockIndices: newIndices,
    });
  },

  deleteSelectedBlocks: () => {
    const { editedLayout, selectedBlockIndices } = get();
    if (!editedLayout || selectedBlockIndices.length === 0) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    // Remove from highest index first so splice doesn't shift earlier indices
    const sorted = [...selectedBlockIndices].sort((a, b) => b - a);
    for (const idx of sorted) {
      layout.buildings.splice(idx, 1);
    }
    set({ editedLayout: layout, ...CLEAR_SELECTION });
  },

  duplicateBlock: (index) => {
    const { editedLayout } = get();
    if (!editedLayout || !editedLayout.buildings[index]) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    const dup = JSON.parse(JSON.stringify(layout.buildings[index]));
    dup.center_x += 0.00005;
    dup.center_y += 0.00005;
    layout.buildings.push(dup);
    const newIdx = layout.buildings.length - 1;
    set({ editedLayout: layout, selectedBlockIndex: newIdx, selectedBlockIndices: [newIdx] });
  },

  duplicateSelectedBlocks: () => {
    const { editedLayout, selectedBlockIndices } = get();
    if (!editedLayout || selectedBlockIndices.length === 0) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    const newIndices: number[] = [];
    for (const idx of selectedBlockIndices) {
      const dup: LayoutBuildingData = JSON.parse(JSON.stringify(layout.buildings[idx]));
      dup.center_x += 0.00005;
      dup.center_y += 0.00005;
      layout.buildings.push(dup);
      newIndices.push(layout.buildings.length - 1);
    }
    set({
      editedLayout: layout,
      selectedBlockIndex: newIndices[newIndices.length - 1],
      selectedBlockIndices: newIndices,
    });
  },

  copyBlock: (index) => {
    const { editedLayout } = get();
    if (!editedLayout || !editedLayout.buildings[index]) return;
    set({ clipboard: [JSON.parse(JSON.stringify(editedLayout.buildings[index]))] });
  },

  copySelectedBlocks: () => {
    const { editedLayout, selectedBlockIndices } = get();
    if (!editedLayout || selectedBlockIndices.length === 0) return;
    const blocks = selectedBlockIndices
      .map((i) => editedLayout.buildings[i])
      .filter(Boolean)
      .map((b) => JSON.parse(JSON.stringify(b)));
    set({ clipboard: blocks });
  },

  pasteBlock: () => {
    const { clipboard, editedLayout } = get();
    if (!clipboard || clipboard.length === 0 || !editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    const newIndices: number[] = [];
    for (const block of clipboard) {
      const pasted: LayoutBuildingData = JSON.parse(JSON.stringify(block));
      pasted.center_x += 0.00008;
      pasted.center_y += 0.00008;
      layout.buildings.push(pasted);
      newIndices.push(layout.buildings.length - 1);
    }
    set({
      editedLayout: layout,
      selectedBlockIndex: newIndices[newIndices.length - 1],
      selectedBlockIndices: newIndices,
    });
  },

  undo: () => {
    const { undoStack, editedLayout, redoStack } = get();
    if (undoStack.length === 0 || !editedLayout) return;
    const prev = undoStack[undoStack.length - 1];
    set({
      undoStack: undoStack.slice(0, -1),
      redoStack: [...redoStack, cloneLayout(editedLayout)],
      editedLayout: prev,
      ...CLEAR_SELECTION,
    });
  },

  redo: () => {
    const { redoStack, editedLayout, undoStack } = get();
    if (redoStack.length === 0 || !editedLayout) return;
    const next = redoStack[redoStack.length - 1];
    set({
      redoStack: redoStack.slice(0, -1),
      undoStack: [...undoStack, cloneLayout(editedLayout)],
      editedLayout: next,
      ...CLEAR_SELECTION,
    });
  },

  setZoom: (zoom) => set({ zoom: Math.max(0.1, Math.min(5, zoom)) }),
  setPan: (panX, panY) => set({ panX, panY }),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),
  toggleSnapToGrid: () => set((s) => ({ snapToGrid: !s.snapToGrid })),
  toggleDimensions: () => set((s) => ({ showDimensions: !s.showDimensions })),
}));
