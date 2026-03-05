import { create } from 'zustand';
import type { SiteZone, LayoutOption, LayoutBuildingData } from '@/types';

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
}

interface BlockEditorState {
  zoneId: string | null;
  zone: SiteZone | null;
  projectId: string | null;
  options: LayoutOption[];
  activeOptionIndex: number;
  editedLayout: LayoutOption | null;
  selectedBlockIndex: number | null;
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

  initEditor: (projectId: string, zone: SiteZone, options: LayoutOption[]) => void;
  resetEditor: () => void;
  switchOption: (index: number) => void;
  setDragState: (state: DragState | null) => void;
  selectBlock: (index: number | null) => void;
  hoverBlock: (index: number | null) => void;
  moveBlock: (index: number, newCenterX: number, newCenterY: number) => void;
  resizeBlock: (index: number, newWidthM: number, newDepthM: number) => void;
  rotateBlock: (index: number, newRotationDeg: number) => void;
  updateBlockProperties: (index: number, props: Partial<LayoutBuildingData>) => void;
  addBlock: (block: LayoutBuildingData) => void;
  deleteBlock: (index: number) => void;
  duplicateBlock: (index: number) => void;
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

export const useBlockEditorStore = create<BlockEditorState>((set, get) => ({
  zoneId: null,
  zone: null,
  projectId: null,
  options: [],
  activeOptionIndex: 0,
  editedLayout: null,
  selectedBlockIndex: null,
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

  initEditor: (projectId, zone, options) => {
    const editedLayout = options.length > 0 ? cloneLayout(options[0]) : null;
    set({
      projectId, zoneId: zone.id, zone, options,
      activeOptionIndex: 0, editedLayout,
      selectedBlockIndex: null, hoveredBlockIndex: null, dragState: null,
      undoStack: [], redoStack: [],
      zoom: 1, panX: 0, panY: 0,
    });
  },

  resetEditor: () => set({
    zoneId: null, zone: null, projectId: null, options: [],
    activeOptionIndex: 0, editedLayout: null,
    selectedBlockIndex: null, hoveredBlockIndex: null, dragState: null,
    undoStack: [], redoStack: [],
  }),

  switchOption: (index) => {
    const { options } = get();
    if (index < 0 || index >= options.length) return;
    set({
      activeOptionIndex: index,
      editedLayout: cloneLayout(options[index]),
      selectedBlockIndex: null,
      undoStack: [], redoStack: [],
    });
  },

  setDragState: (dragState) => set({ dragState }),
  selectBlock: (index) => set({ selectedBlockIndex: index }),
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
    set({ editedLayout: layout, selectedBlockIndex: layout.buildings.length - 1 });
  },

  deleteBlock: (index) => {
    const { editedLayout, selectedBlockIndex } = get();
    if (!editedLayout) return;
    get().pushUndoSnapshot();
    const layout = cloneLayout(editedLayout);
    layout.buildings.splice(index, 1);
    set({
      editedLayout: layout,
      selectedBlockIndex: selectedBlockIndex === index ? null : selectedBlockIndex,
    });
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
    set({ editedLayout: layout, selectedBlockIndex: layout.buildings.length - 1 });
  },

  undo: () => {
    const { undoStack, editedLayout, redoStack } = get();
    if (undoStack.length === 0 || !editedLayout) return;
    const prev = undoStack[undoStack.length - 1];
    set({
      undoStack: undoStack.slice(0, -1),
      redoStack: [...redoStack, cloneLayout(editedLayout)],
      editedLayout: prev,
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
    });
  },

  setZoom: (zoom) => set({ zoom: Math.max(0.2, Math.min(5, zoom)) }),
  setPan: (panX, panY) => set({ panX, panY }),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),
  toggleSnapToGrid: () => set((s) => ({ snapToGrid: !s.snapToGrid })),
  toggleDimensions: () => set((s) => ({ showDimensions: !s.showDimensions })),
}));
