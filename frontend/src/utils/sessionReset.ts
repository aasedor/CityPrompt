import type { QueryClient } from '@tanstack/react-query';
import { useProjectStore, useViewerStore } from '@/store';
import { useGenerationStore } from '@/store/generationStore';
import { useUndoRedoStore } from '@/store/undoRedo';

export function resetSessionState(queryClient?: QueryClient) {
  useUndoRedoStore.getState().setProjectScope(null);
  useUndoRedoStore.getState().clearHistory();
  queryClient?.clear();
  useProjectStore.setState({
    projects: [],
    activeProject: null,
    isLoading: false,
    error: null,
  });
  useGenerationStore.getState().clearAll();
  useViewerStore.setState({
    selectedBuildingId: null,
    hoveredBuildingId: null,
    isInfoPanelOpen: false,
    measurements: [],
    pendingPoint: null,
    pendingPolygon: [],
    pendingAngle: [],
    measurementMode: 'distance',
    measurementUnit: 'metric',
    cameraTarget: null,
    isComparing: false,
    comparePhase: null,
    compareDivider: 50,
    cameraPath: [],
    isRecording: false,
    isPlaying: false,
    isAnnotating: false,
    isMovingBuilding: false,
    isWalkthroughActive: false,
    walkthroughReturnPos: null,
    walkthroughReturnTarget: null,
    isSitePlannerActive: false,
    activeSitePlannerTool: null,
    activeToolProperties: null,
    selectedZoneId: null,
    isDraggingZone: false,
    mapInstance: null,
    layoutPreview: null,
    sitePreview: null,
    masterPlan3D: null,
    streetViewPegman: null,
    lightboxImageUrl: null,
    lightboxActions: null,
    osmContext: null,
    lockedLayers: null,
    siteMassing: null,
    workflowStep: 1,
  });
}
