import { useCallback, useRef, useState, useEffect, Component, type ReactNode, type ErrorInfo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ArrowLeft, Camera, Download, Video, Square, MessageSquarePlus, X, Users, Eye, EyeOff, Map as MapIcon, Trash2, Sparkles, Move, RotateCw, Loader2, Footprints } from 'lucide-react';
import { projectsApi, buildingsApi, contextApi, annotationsApi, siteZonesApi } from '@/services/api';
import { AIGenerateModal } from '@/components/buildings/AIGenerateModal';
import { UndoRedoButtons } from '@/components/ui/UndoRedoButtons';
import { useUndoRedoKeyboard } from '@/hooks/useUndoRedoKeyboard';
import { useUndoRedoStore } from '@/store/undoRedo';
import {
  createBuildingDeleteAction,
  createBuildingUpdateAction,
  createBuildingMoveAction,
  createBuildingRotationAction,
  createBuildingMaterialAction,
} from '@/store/undoActions';
// Annotation type used implicitly via annotationsApi
import { useSiteZones } from '@/hooks/useSiteZones';
import { SceneViewer } from '@/components/viewer/SceneViewer';
import { ViewerControls } from '@/components/viewer/ViewerControls';
import { SitePlannerMap } from '@/components/viewer/SitePlannerMap';
import { SitePlannerToolbar } from '@/components/viewer/SitePlannerToolbar';
import { ZonePropertiesPanel } from '@/components/viewer/ZonePropertiesPanel';
import { WalkthroughHUD } from '@/components/viewer/WalkthroughHUD';
import { SitePlannerGuide } from '@/components/viewer/SitePlannerGuide';
import { ImageLightbox } from '@/components/ui/ImageLightbox';
import { useViewerStore, useAuthStore } from '@/store';
import { useGenerationStore } from '@/store/generationStore';
import { useCollaboration } from '@/services/collaboration';

class SceneErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null; retryKey: number }> {
  state = { error: null as Error | null, retryKey: 0 };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('3D Scene crashed:', error, info); }
  render() {
    if (this.state.error) {
      const isWebGLError = this.state.error.message?.includes('WebGL');
      return (
        <div className="flex h-full w-full flex-col items-center justify-center gap-3 bg-gray-900 text-primary-950 dark:text-accent-50">
          <p className="text-lg font-semibold">3D Scene Error</p>
          <pre className="max-w-xl overflow-auto rounded bg-red-900/50 p-3 text-xs text-red-200">{this.state.error.toString()}</pre>
          {isWebGLError && (
            <p className="max-w-md text-center text-sm text-primary-950/50 dark:text-white/50">
              Browser ran out of WebGL contexts. Close other tabs using 3D/maps and reload the page.
            </p>
          )}
          <div className="flex gap-2">
            <button onClick={() => this.setState((s) => ({ error: null, retryKey: s.retryKey + 1 }))} className="rounded bg-blue-600 px-4 py-2 text-sm hover:bg-blue-700">Retry</button>
            {isWebGLError && (
              <button onClick={() => window.location.reload()} className="rounded bg-gray-600 px-4 py-2 text-sm hover:bg-gray-700">Reload Page</button>
            )}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export function ViewerPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { selectedBuildingId, selectBuilding, hoverBuilding, isInfoPanelOpen, settings, updateSettings, isComparing, comparePhase, compareDivider, setCompareDivider, isAnnotating, setAnnotating, isSitePlannerActive, setSitePlannerActive, selectedZoneId, selectZone, setCameraTarget, setCameraMode, isMovingBuilding, setMovingBuilding, isWalkthroughActive, startWalkthrough, exitWalkthrough } = useViewerStore();
  const { user } = useAuthStore();

  // Undo/Redo keyboard shortcuts
  useUndoRedoKeyboard();

  // Track rotation value before drag starts for undo
  const rotationBeforeDrag = useRef<number | null>(null);

  // Real-time collaboration
  const collaboration = useCollaboration(id, user?.full_name || user?.email || 'Anonymous');

  // Broadcast building selections to collaborators
  const handleSelectBuilding = useCallback((buildingId: string | null) => {
    selectBuilding(buildingId);
    if (!buildingId) setMovingBuilding(false);
    collaboration.sendSelect(buildingId || '');
  }, [selectBuilding, setMovingBuilding, collaboration]);

  // Follow camera state — holds the latest camera from the followed user
  const [followCamera, setFollowCamera] = useState<{ position: [number, number, number]; target: [number, number, number] } | null>(null);

  // Listen for remote edits and refresh data
  useEffect(() => {
    collaboration.onEdit((msg) => {
      toast(`${msg.name} edited a building`, { icon: '✏️', duration: 2000 });
      queryClient.invalidateQueries({ queryKey: ['project', id] });
    });
  }, [collaboration, queryClient, id]);

  // Listen for camera updates from followed user
  useEffect(() => {
    collaboration.onCamera((cursor) => {
      if (collaboration.followingUserId && cursor.userId === collaboration.followingUserId) {
        setFollowCamera({ position: cursor.position, target: cursor.target });
      }
    });
  }, [collaboration]);

  // Clear follow camera when unfollowing
  useEffect(() => {
    if (!collaboration.followingUserId) {
      setFollowCamera(null);
    }
  }, [collaboration.followingUserId]);

  const { data: project } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
  });

  // Fetch context buildings from OSM when project has a location
  const { data: contextBuildings } = useQuery({
    queryKey: ['context-buildings', project?.location?.latitude, project?.location?.longitude],
    queryFn: () =>
      contextApi.getBuildings(project!.location!.latitude, project!.location!.longitude),
    enabled: !!project?.location && settings.showExistingBuildings,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Fetch context roads from OSM when project has a location
  const { data: contextRoads } = useQuery({
    queryKey: ['context-roads', project?.location?.latitude, project?.location?.longitude],
    queryFn: () =>
      contextApi.getRoads(project!.location!.latitude, project!.location!.longitude),
    enabled: !!project?.location && settings.showRoads,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch annotations
  const { data: annotations = [] } = useQuery({
    queryKey: ['annotations', id],
    queryFn: () => annotationsApi.list(id!),
    enabled: !!id,
  });

  const createAnnotation = useMutation({
    mutationFn: (vars: { text: string; position_x: number; position_y: number; position_z: number }) =>
      annotationsApi.create(id!, vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations', id] });
      toast.success('Annotation added');
    },
  });

  const resolveAnnotation = useMutation({
    mutationFn: (annotationId: string) => annotationsApi.update(annotationId, { resolved: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['annotations', id] }),
  });

  const deleteAnnotation = useMutation({
    mutationFn: (annotationId: string) => annotationsApi.delete(annotationId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['annotations', id] }),
  });

  // Site zones via shared hook
  const {
    siteZones,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  } = useSiteZones(id);

  // Load OSM context from site_boundary zone on mount
  const { setOSMContext } = useViewerStore();
  useEffect(() => {
    if (!siteZones.length) return;
    const boundary = siteZones.find((z) => z.zone_type === 'site_boundary');
    if (boundary?.properties?._osm_context) {
      setOSMContext(boundary.properties._osm_context as import('@/types').OSMContext);
    }
  }, [siteZones, setOSMContext]);

  // =========================================================================
  // Generation status — backed by global store (persists across pages)
  // =========================================================================
  const genBuildings = useGenerationStore((s) => s.buildings);
  const generationStatuses = (() => {
    const map = new Map<string, { status: string; progress?: number }>();
    for (const [bid, entry] of genBuildings) {
      map.set(bid, { status: entry.status, progress: entry.progress });
    }
    return map;
  })();

  // Seed generation store when buildings are already generating (page load / refresh)
  useEffect(() => {
    const generating = (project?.buildings || []).filter(
      (b) => b.generation_status === 'generating',
    );
    if (generating.length > 0 && !useGenerationStore.getState().isActive()) {
      useGenerationStore.getState().startBatch(
        id!,
        generating.map((b) => ({ id: b.id, name: b.name || 'Building' })),
      );
    }
  }, [project?.buildings, id]);

  const selectedZone = siteZones.find((z) => z.id === selectedZoneId);

  const selectedBuilding = project?.buildings?.find((b) => b.id === selectedBuildingId);

  // All buildings passed to viewer — phase visibility animated per-building
  const allBuildings = project?.buildings || [];

  // Effective location: use project location, or fall back to centroid of site zones
  const effectiveLocation = (() => {
    if (project?.location?.latitude && project?.location?.longitude) {
      return { latitude: project.location.latitude, longitude: project.location.longitude };
    }
    // Derive from zone coordinates if available
    if (siteZones.length > 0) {
      let sumLat = 0, sumLng = 0, count = 0;
      for (const zone of siteZones) {
        for (const coord of zone.coordinates) {
          sumLng += coord[0];
          sumLat += coord[1];
          count++;
        }
      }
      if (count > 0) {
        return { latitude: sumLat / count, longitude: sumLng / count };
      }
    }
    return null;
  })();

  // Fly camera to encompass zones when switching from site planner to 3D
  const flyToZones = useCallback(() => {
    if (siteZones.length === 0 || !effectiveLocation) return;
    const lat = effectiveLocation.latitude;
    const lng = effectiveLocation.longitude;
    const metersPerDegLat = 111320;
    const metersPerDegLon = metersPerDegLat * Math.cos((lat * Math.PI) / 180);

    // Compute bounding box of all zone coordinates in local meters
    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const zone of siteZones) {
      for (const p of zone.coordinates) {
        const x = (p[0] - lng) * metersPerDegLon;
        const z = -(p[1] - lat) * metersPerDegLat;
        minX = Math.min(minX, x);
        maxX = Math.max(maxX, x);
        minZ = Math.min(minZ, z);
        maxZ = Math.max(maxZ, z);
      }
    }

    const cx = (minX + maxX) / 2;
    const cz = (minZ + maxZ) / 2;
    const span = Math.max(maxX - minX, maxZ - minZ, 50);
    const dist = span * 1.2; // Camera distance to see the full extent

    setCameraTarget({
      position: [cx + dist * 0.5, dist * 0.7, cz + dist * 0.5],
      target: [cx, 0, cz],
      label: 'Zones',
    });
  }, [siteZones, effectiveLocation, setCameraTarget]);

  const handleExitSitePlanner = useCallback(() => {
    // Always reset to orbit mode when returning to 3D viewer
    if (isWalkthroughActive) exitWalkthrough();
    setCameraMode('orbit');
    // Reset map layer to 'none' so the satellite background doesn't persist
    updateSettings({ mapLayer: 'none' });
    setSitePlannerActive(false);
    // After a short delay to allow the 3D scene to mount, fly to zones
    setTimeout(flyToZones, 300);
  }, [setSitePlannerActive, flyToZones, isWalkthroughActive, exitWalkthrough, setCameraMode, updateSettings]);

  // Compute a good walkthrough start position from zone data
  const computeWalkthroughEntry = useCallback((): { position: [number, number, number]; target: [number, number, number] } => {
    if (siteZones.length === 0 || !effectiveLocation) {
      // Fallback: start near origin at eye level looking north
      return { position: [0, 1.7, 10], target: [0, 1.7, 0] };
    }
    const lat = effectiveLocation.latitude;
    const lng = effectiveLocation.longitude;
    const metersPerDegLat = 111320;
    const metersPerDegLon = metersPerDegLat * Math.cos((lat * Math.PI) / 180);

    // Compute centroid of all zone coordinates in local meters
    let sumX = 0, sumZ = 0, count = 0;
    for (const zone of siteZones) {
      for (const p of zone.coordinates) {
        sumX += (p[0] - lng) * metersPerDegLon;
        sumZ += -(p[1] - lat) * metersPerDegLat;
        count++;
      }
    }
    const cx = count > 0 ? sumX / count : 0;
    const cz = count > 0 ? sumZ / count : 0;

    // If road zones exist, find the road zone closest to the centroid and use its midpoint
    const roadZones = siteZones.filter((z) => z.zone_type === 'road');
    if (roadZones.length > 0) {
      let bestDist = Infinity;
      let bestPos: [number, number, number] = [cx, 1.7, cz];
      for (const road of roadZones) {
        let rx = 0, rz = 0;
        for (const p of road.coordinates) {
          rx += (p[0] - lng) * metersPerDegLon;
          rz += -(p[1] - lat) * metersPerDegLat;
        }
        rx /= road.coordinates.length;
        rz /= road.coordinates.length;
        const d = Math.hypot(rx - cx, rz - cz);
        if (d < bestDist) {
          bestDist = d;
          bestPos = [rx, 1.7, rz];
        }
      }
      // Look toward the centroid from the road position
      return { position: bestPos, target: [cx, 1.7, cz] };
    }

    // Start slightly south of centroid, looking north
    return { position: [cx, 1.7, cz + 15], target: [cx, 1.7, cz] };
  }, [siteZones, effectiveLocation]);

  // Handle "Explore" — enter walkthrough at street level
  const handleExplore = useCallback(() => {
    const { position, target } = computeWalkthroughEntry();
    startWalkthrough(
      [position[0] + 50, 50, position[2] + 50],
      [position[0], 0, position[2]],
    );
    setCameraMode('firstPerson');
    setCameraTarget({ position, target, label: 'Walkthrough' });
  }, [computeWalkthroughEntry, startWalkthrough, setCameraTarget, setCameraMode]);

  // Handle "Walk Through" from site planner — set all state at once, no timeouts
  const handleWalkThrough = useCallback(() => {
    const { position, target } = computeWalkthroughEntry();
    startWalkthrough(
      [position[0] + 50, 50, position[2] + 50],
      [position[0], 0, position[2]],
    );
    setCameraMode('firstPerson');
    setCameraTarget({ position, target, label: 'Walkthrough' });
    // Reset map layer to 'none' so the satellite background doesn't persist
    updateSettings({ mapLayer: 'none' });
    setSitePlannerActive(false);
  }, [computeWalkthroughEntry, startWalkthrough, setCameraTarget, setCameraMode, setSitePlannerActive, updateSettings]);

  const updateBuilding = useMutation({
    mutationFn: (vars: { buildingId: string; data: Record<string, unknown>; silent?: boolean; _undoPrevious?: Record<string, unknown>; _undoLabel?: string }) =>
      buildingsApi.update(vars.buildingId, vars.data),
    onMutate: async (vars) => {
      // Optimistically update cache for silent updates (move/rotation)
      // so the building doesn't flicker/shrink during refetch
      if (vars.silent) {
        await queryClient.cancelQueries({ queryKey: ['project', id] });
        const prev = queryClient.getQueryData(['project', id]);
        queryClient.setQueryData(['project', id], (old: any) => {
          if (!old?.buildings) return old;
          return {
            ...old,
            buildings: old.buildings.map((b: any) =>
              b.id === vars.buildingId ? { ...b, ...vars.data } : b
            ),
          };
        });
        return { prev };
      }
    },
    onSuccess: (_data, vars) => {
      if (!vars.silent) {
        queryClient.invalidateQueries({ queryKey: ['project', id] });
        toast.success('Building updated');
        setEditingBuilding(false);
      }
      // Broadcast edit to collaborators
      collaboration.sendEdit(vars.buildingId, vars.data);
      // Push undo action when previous data is provided
      if (!useUndoRedoStore.getState()._isSystemAction && id && vars._undoPrevious) {
        useUndoRedoStore.getState().pushAction(
          createBuildingUpdateAction(
            id,
            vars.buildingId,
            vars._undoPrevious,
            vars.data,
            vars._undoLabel || 'Update building',
            queryClient,
          ),
        );
      }
    },
    onError: (_err, vars, context) => {
      // Roll back optimistic update on error
      if (vars.silent && context?.prev) {
        queryClient.setQueryData(['project', id], context.prev);
      }
    },
    onSettled: (_data, _err, vars) => {
      // Refetch after silent updates settle to sync with server
      if (vars.silent) {
        queryClient.invalidateQueries({ queryKey: ['project', id] });
      }
    },
  });

  const deleteBuilding = useMutation({
    mutationFn: (buildingId: string) => buildingsApi.delete(buildingId),
    onMutate: (buildingId) => {
      // Capture building snapshot before deletion for undo
      const project = queryClient.getQueryData<any>(['project', id]);
      const building = project?.buildings?.find((b: any) => b.id === buildingId);
      return { building };
    },
    onSuccess: (_data, _buildingId, context) => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      selectBuilding(null);
      toast.success('Building deleted');
      // Push undo action
      if (!useUndoRedoStore.getState()._isSystemAction && id && context?.building) {
        useUndoRedoStore.getState().pushAction(
          createBuildingDeleteAction(id, context.building, queryClient),
        );
      }
    },
    onError: () => {
      toast.error('Failed to delete building');
    },
  });

  // Handle annotation placement from scene click
  const [pendingAnnotationPos, setPendingAnnotationPos] = useState<[number, number, number] | null>(null);
  const [annotationText, setAnnotationText] = useState('');

  const handleSceneAnnotationClick = useCallback((position: [number, number, number]) => {
    if (!isAnnotating) return;
    setPendingAnnotationPos(position);
    setAnnotationText('');
  }, [isAnnotating]);

  // Handle building move — convert scene position back to geographic footprint
  const handleBuildingMove = useCallback((buildingId: string, position: [number, number, number]) => {
    const building = allBuildings.find((b) => b.id === buildingId);
    if (!building || !effectiveLocation) return;

    const lat = effectiveLocation.latitude;
    const lng = effectiveLocation.longitude;
    const metersPerDegLat = 111320;
    const metersPerDegLon = 111320 * Math.cos((lat * Math.PI) / 180);

    // Capture previous coordinates for undo
    const previousCoords = building.footprint_coordinates ? [...building.footprint_coordinates.map(c => [...c])] : undefined;

    if (building.footprint_coordinates && building.footprint_coordinates.length >= 3) {
      // Existing footprint — shift it by the delta
      let oldCx = 0, oldCy = 0;
      for (const p of building.footprint_coordinates) {
        oldCx += p[0]; oldCy += p[1];
      }
      oldCx /= building.footprint_coordinates.length;
      oldCy /= building.footprint_coordinates.length;
      const oldSceneX = (oldCx - lng) * metersPerDegLon;
      const oldSceneZ = -(oldCy - lat) * metersPerDegLat;

      const dx = position[0] - oldSceneX;
      const dz = position[2] - oldSceneZ;
      const dLng = dx / metersPerDegLon;
      const dLat = -dz / metersPerDegLat;

      const newCoords = building.footprint_coordinates.map(([pLng, pLat]) => [pLng + dLng, pLat + dLat]);
      updateBuilding.mutate({ buildingId, data: { footprint_coordinates: newCoords }, silent: true });
      // Push undo action for move
      if (!useUndoRedoStore.getState()._isSystemAction && id && previousCoords) {
        useUndoRedoStore.getState().pushAction(
          createBuildingMoveAction(id, buildingId, previousCoords, newCoords, queryClient),
        );
      }
    } else {
      // No footprint yet — create a footprint proportional to the building height
      const clickLng = lng + position[0] / metersPerDegLon;
      const clickLat = lat - position[2] / metersPerDegLat;
      const h = building.height_meters || 10;
      // Make footprint roughly 1:1 aspect ratio, sized relative to height
      const sideMeters = Math.max(h * 0.8, 10);
      const halfW = (sideMeters / 2) / metersPerDegLon;
      const halfH = (sideMeters / 2) / metersPerDegLat;
      const newCoords = [
        [clickLng - halfW, clickLat - halfH],
        [clickLng + halfW, clickLat - halfH],
        [clickLng + halfW, clickLat + halfH],
        [clickLng - halfW, clickLat + halfH],
      ];
      updateBuilding.mutate({ buildingId, data: { footprint_coordinates: newCoords }, silent: true });
    }

    setMovingBuilding(false);
  }, [allBuildings, effectiveLocation, updateBuilding, setMovingBuilding, id, queryClient]);

  const handleSubmitAnnotation = useCallback(() => {
    if (!pendingAnnotationPos || !annotationText.trim()) return;
    createAnnotation.mutate({
      text: annotationText.trim(),
      position_x: pendingAnnotationPos[0],
      position_y: pendingAnnotationPos[1],
      position_z: pendingAnnotationPos[2],
    });
    setPendingAnnotationPos(null);
    setAnnotationText('');
  }, [pendingAnnotationPos, annotationText, createAnnotation]);

  // Show map background when mapLayer is set (always has a value)
  const showMap = settings.mapLayer !== 'none';

  const [screenshotMenuOpen, setScreenshotMenuOpen] = useState(false);
  const [showAIGenerateModal, setShowAIGenerateModal] = useState(false);
  const [generatingNeighborhood, setGeneratingNeighborhood] = useState(false);
  const [showGenerateConfirm, setShowGenerateConfirm] = useState(false);

  // Compute buildable zone counts for the confirmation dialog
  const buildableZones = siteZones.filter(z => ['building', 'residential', 'development_area'].includes(z.zone_type));
  const totalBuildableCount = buildableZones.length;
  const totalUnits = buildableZones.reduce((sum, z) => sum + ((z.properties?.unit_count as number) || 1), 0);

  const selectedBoundary = selectedZone?.zone_type === 'site_boundary' ? selectedZone : null;

  const runGenerate = useCallback(async (mode: 'boundary' | 'all') => {
    if (!id) return;
    setShowGenerateConfirm(false);
    setGeneratingNeighborhood(true);
    try {
      // Auto-apply any active layout preview selections before generating
      const { sitePreview, layoutPreview, clearSitePreview, clearLayoutPreview, clearLockedLayers } = useViewerStore.getState();
      let appliedCount = 0;

      if (sitePreview) {
        const { zoneLayouts, activeIndex } = sitePreview;
        const applyResults = await Promise.all(
          Object.entries(zoneLayouts).map(async ([zoneId, options]) => {
            if (!options[activeIndex]) return null;
            try {
              await siteZonesApi.applyLayout(zoneId, activeIndex, options[activeIndex]);
              return zoneId;
            } catch (e) {
              console.warn(`Failed to apply layout for zone ${zoneId}:`, e);
              return null;
            }
          })
        );
        appliedCount = applyResults.filter(Boolean).length;
        clearSitePreview();
        clearLockedLayers();
      } else if (layoutPreview) {
        const { zoneId, options, activeIndex } = layoutPreview;
        if (options[activeIndex]) {
          try {
            await siteZonesApi.applyLayout(zoneId, activeIndex, options[activeIndex]);
            appliedCount = 1;
          } catch (e) {
            console.warn(`Failed to apply layout for zone ${zoneId}:`, e);
          }
        }
        clearLayoutPreview();
        clearLockedLayers();
      }

      if (appliedCount > 0) {
        toast.success(`Applied ${appliedCount} previewed layout${appliedCount > 1 ? 's' : ''}`);
      }

      let result;
      if (mode === 'boundary' && selectedBoundary) {
        result = await siteZonesApi.generateForBoundary(id, selectedBoundary.id);
      } else {
        result = await siteZonesApi.generateAll(id);
      }
      toast.success(
        `${result.buildings_created} buildings created, ${result.generations_queued} generations queued`,
      );
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      queryClient.invalidateQueries({ queryKey: ['site-zones', id] });

      // Seed global generation store with newly generating buildings
      try {
        const freshProject = await projectsApi.get(id);
        const generatingBuildings = (freshProject.buildings || [])
          .filter((b) => b.generation_status === 'generating')
          .map((b) => ({ id: b.id, name: b.name || 'Building' }));
        if (generatingBuildings.length > 0) {
          useGenerationStore.getState().startBatch(id, generatingBuildings);
        }
      } catch {
        // Non-critical — polling will pick it up
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Generation failed';
      toast.error(message);
    } finally {
      setGeneratingNeighborhood(false);
    }
  }, [id, queryClient, selectedBoundary]);
  const [aiGenerateFromZoneBuildingId, setAiGenerateFromZoneBuildingId] = useState<string | null>(null);
  const [aiGenerateFromZonePrompt, setAiGenerateFromZonePrompt] = useState<string | null>(null);
  const [editingBuilding, setEditingBuilding] = useState(false);
  const [editValues, setEditValues] = useState<{
    height_meters?: number;
    floor_count?: number;
    floor_height_meters?: number;
    roof_type?: string;
  }>({});
  const handleScreenshot = useCallback((multiplier = 1) => {
    const canvas = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!canvas) return;
    setScreenshotMenuOpen(false);

    if (multiplier === 1) {
      const link = document.createElement('a');
      link.download = `${project?.name || 'scene'}-screenshot.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      return;
    }

    // High-res: create an offscreen canvas at multiplied resolution
    const offscreen = document.createElement('canvas');
    offscreen.width = canvas.width * multiplier;
    offscreen.height = canvas.height * multiplier;
    const ctx = offscreen.getContext('2d');
    if (!ctx) return;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(canvas, 0, 0, offscreen.width, offscreen.height);
    const link = document.createElement('a');
    link.download = `${project?.name || 'scene'}-${multiplier}x.png`;
    link.href = offscreen.toDataURL('image/png');
    link.click();
    toast.success(`${multiplier}x screenshot saved (${offscreen.width}x${offscreen.height})`);
  }, [project?.name]);

  const handleExportScene = useCallback(() => {
    window.dispatchEvent(new Event('export-scene-glb'));
  }, []);

  // Video recording state
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isRecordingVideo, setIsRecordingVideo] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showGuide, setShowGuide] = useState(false);

  // '?' key toggles shortcuts modal + ESC handler
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === '?' || (e.key === '/' && e.shiftKey)) {
        // Ignore if typing in an input
        if ((e.target as HTMLElement).tagName === 'INPUT' || (e.target as HTMLElement).tagName === 'TEXTAREA') return;
        setShowShortcuts((v) => !v);
      }
      if (e.key === 'Escape' && isWalkthroughActive) {
        if (document.pointerLockElement) document.exitPointerLock();
        exitWalkthrough();
        return;
      }
      if (e.key === 'Escape' && isMovingBuilding) {
        setMovingBuilding(false);
        return;
      }
      if (e.key === 'Escape' && showShortcuts) {
        setShowShortcuts(false);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [showShortcuts, isMovingBuilding, setMovingBuilding, isWalkthroughActive, exitWalkthrough]);

  // When browser exits pointer lock (ESC consumed by browser before JS keydown),
  // also exit walkthrough mode so user isn't stuck in firstPerson.
  // Track whether pointer lock was ever acquired to avoid false triggers.
  const hadPointerLock = useRef(false);
  useEffect(() => {
    const handlePointerLockChange = () => {
      if (document.pointerLockElement) {
        hadPointerLock.current = true;
      } else if (hadPointerLock.current && isWalkthroughActive) {
        hadPointerLock.current = false;
        exitWalkthrough();
      }
    };
    document.addEventListener('pointerlockchange', handlePointerLockChange);
    return () => document.removeEventListener('pointerlockchange', handlePointerLockChange);
  }, [isWalkthroughActive, exitWalkthrough]);

  const handleToggleVideoRecord = useCallback(() => {
    if (isRecordingVideo) {
      // Stop recording
      mediaRecorderRef.current?.stop();
      setIsRecordingVideo(false);
      return;
    }

    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const stream = canvas.captureStream(30); // 30 FPS
    const recorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
        ? 'video/webm;codecs=vp9'
        : 'video/webm',
      videoBitsPerSecond: 5_000_000,
    });

    chunksRef.current = [];
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${project?.name || 'scene'}-recording.webm`;
      link.click();
      URL.revokeObjectURL(url);
    };

    recorder.start(100); // Collect data every 100ms
    mediaRecorderRef.current = recorder;
    setIsRecordingVideo(true);
  }, [isRecordingVideo, project?.name]);

  const handleDownloadGLB = useCallback((buildingId: string, buildingName?: string) => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const link = document.createElement('a');
    link.href = `${apiBase}/api/v1/buildings/${buildingId}/model/file`;
    link.download = `${buildingName || buildingId}.glb`;
    link.click();
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-gray-900">
      {/* Top Bar */}
      <div className="absolute left-0 right-0 top-0 z-20 flex items-center justify-between bg-white/95 backdrop-blur-sm shadow-lg px-3 py-2 sm:px-4 sm:py-3">
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            to={`/projects/${id}`}
            className="rounded-lg bg-primary-950/[0.04] dark:bg-white/[0.04] p-2 text-primary-950 dark:text-accent-50 backdrop-blur-sm hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]"
          >
            <ArrowLeft size={18} />
          </Link>
          <div className="min-w-0">
            <h1 className="truncate text-sm font-semibold text-primary-950 dark:text-accent-50 sm:text-lg">{project?.name || 'Loading...'}</h1>
            <p className="text-xs text-primary-950/60 dark:text-white/60">{project?.buildings?.length || 0} buildings</p>
          </div>
          <UndoRedoButtons />
          {/* Presence indicators with follow mode */}
          {collaboration.users.length > 1 && (
            <div className="ml-2 flex items-center gap-1" title={`${collaboration.users.length} viewers online`}>
              <Users size={14} className="text-primary-950/60 dark:text-white/60" />
              <div className="flex -space-x-1.5">
                {collaboration.users
                  .filter((u) => u.id !== collaboration.connectionId)
                  .slice(0, 5)
                  .map((u) => {
                    const isFollowing = collaboration.followingUserId === u.id;
                    return (
                      <button
                        key={u.id}
                        onClick={() => {
                          if (isFollowing) {
                            collaboration.setFollowing(null);
                            toast('Stopped following', { duration: 1500 });
                          } else {
                            collaboration.setFollowing(u.id);
                            toast(`Following ${u.name}`, { icon: '👁', duration: 2000 });
                          }
                        }}
                        className={`relative flex h-6 w-6 items-center justify-center rounded-full border-2 text-[10px] font-bold text-primary-950 transition-all ${
                          isFollowing
                            ? 'border-white ring-2 ring-white/50 scale-110'
                            : 'border-gray-900/80 hover:scale-110'
                        }`}
                        style={{ backgroundColor: u.color }}
                        title={isFollowing ? `Stop following ${u.name}` : `Follow ${u.name}`}
                      >
                        {u.name.charAt(0).toUpperCase()}
                        {isFollowing && (
                          <Eye size={8} className="absolute -bottom-1 -right-1 rounded-full bg-white dark:bg-primary-900 text-neutral-900 p-px" />
                        )}
                      </button>
                    );
                  })}
                {collaboration.users.length > 6 && (
                  <div className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-gray-900/80 bg-gray-600 text-[9px] font-bold text-primary-950 dark:text-accent-50">
                    +{collaboration.users.length - 6}
                  </div>
                )}
              </div>
              {collaboration.followingUserId && (
                <button
                  onClick={() => collaboration.setFollowing(null)}
                  className="ml-1 flex items-center gap-1 rounded-md bg-primary-950/[0.06] dark:bg-white/[0.06] px-2 py-0.5 text-[10px] font-medium text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.1] dark:hover:bg-white/[0.1]"
                >
                  <EyeOff size={10} />
                  Stop
                </button>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => isSitePlannerActive ? handleExitSitePlanner() : setSitePlannerActive(true)}
            className={`flex items-center gap-1.5 rounded-lg p-2 text-sm font-medium backdrop-blur-sm sm:px-3 sm:py-1.5 ${
              isSitePlannerActive
                ? 'bg-emerald-500/80 text-white hover:bg-emerald-600/80'
                : 'bg-primary-950/[0.04] dark:bg-white/[0.04] text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]'
            }`}
          >
            <MapIcon size={14} />
            <span className="hidden sm:inline">{isSitePlannerActive ? 'Exit Site Plan' : 'Site Plan'}</span>
          </button>
          {!isSitePlannerActive && (
          <button
            onClick={() => setShowAIGenerateModal(true)}
            className="flex items-center gap-1.5 rounded-lg bg-purple-500/80 p-2 text-sm font-medium text-primary-950 dark:text-accent-50 backdrop-blur-sm hover:bg-purple-600/80 sm:px-3 sm:py-1.5"
            title="AI 3D Generation"
          >
            <Sparkles size={14} />
            <span className="hidden sm:inline">AI Generate</span>
          </button>
          )}
          {!isSitePlannerActive && siteZones.length > 0 && (
          <button
            onClick={() => setShowGenerateConfirm(true)}
            disabled={generatingNeighborhood}
            className="flex items-center gap-1.5 rounded-lg bg-purple-700/80 p-2 text-sm font-medium text-primary-950 dark:text-accent-50 backdrop-blur-sm hover:bg-purple-800/80 disabled:opacity-50 sm:px-3 sm:py-1.5"
            title="Generate 3D models for all building/residential zones"
          >
            {generatingNeighborhood ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            <span className="hidden sm:inline">{generatingNeighborhood ? 'Generating...' : 'Generate Neighborhood'}</span>
          </button>
          )}
          {!isSitePlannerActive && (
          <button
            onClick={handleExplore}
            className="flex items-center gap-1.5 rounded-lg bg-emerald-600/80 p-2 text-sm font-medium text-white backdrop-blur-sm hover:bg-emerald-700/80 sm:px-3 sm:py-1.5"
            title="Walk through the site at street level"
          >
            <Footprints size={14} />
            <span className="hidden sm:inline">Explore</span>
          </button>
          )}
          {!isSitePlannerActive && (
          <button
            onClick={() => { setAnnotating(!isAnnotating); setPendingAnnotationPos(null); }}
            className={`flex items-center gap-1.5 rounded-lg p-2 text-sm font-medium backdrop-blur-sm sm:px-3 sm:py-1.5 ${
              isAnnotating
                ? 'bg-yellow-500/80 text-primary-950 dark:text-accent-50 hover:bg-yellow-600/80'
                : 'bg-primary-950/[0.04] dark:bg-white/[0.04] text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]'
            }`}
          >
            <MessageSquarePlus size={14} />
            <span className="hidden sm:inline">{isAnnotating ? 'Done' : 'Annotate'}</span>
          </button>
          )}
          {!isSitePlannerActive && (
          <>
          <button
            onClick={handleToggleVideoRecord}
            className={`flex items-center gap-1.5 rounded-lg p-2 text-sm font-medium backdrop-blur-sm sm:px-3 sm:py-1.5 ${
              isRecordingVideo
                ? 'bg-red-500/80 text-white hover:bg-red-600/80'
                : 'bg-primary-950/[0.04] dark:bg-white/[0.04] text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]'
            }`}
          >
            {isRecordingVideo ? <Square size={14} /> : <Video size={14} />}
            <span className="hidden sm:inline">{isRecordingVideo ? 'Stop' : 'Record'}</span>
          </button>
          <button
            onClick={handleExportScene}
            className="flex items-center gap-1.5 rounded-lg bg-primary-950/[0.04] dark:bg-white/[0.04] p-2 text-sm font-medium text-primary-950 dark:text-accent-50 backdrop-blur-sm hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06] sm:px-3 sm:py-1.5"
          >
            <Download size={14} />
            <span className="hidden sm:inline">Export</span>
          </button>
          <div className="relative">
            <button
              onClick={() => setScreenshotMenuOpen((v) => !v)}
              className="flex items-center gap-1.5 rounded-lg bg-primary-950/[0.04] dark:bg-white/[0.04] p-2 text-sm font-medium text-primary-950 dark:text-accent-50 backdrop-blur-sm hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06] sm:px-3 sm:py-1.5"
            >
              <Camera size={14} />
              <span className="hidden sm:inline">Screenshot</span>
            </button>
            {screenshotMenuOpen && (
              <div className="absolute right-0 top-full mt-1 rounded-lg bg-gray-900/95 p-1 shadow-xl backdrop-blur-sm">
                {[
                  { label: '1x', mult: 1 },
                  { label: '2x', mult: 2 },
                  { label: '4x', mult: 4 },
                ].map(({ label, mult }) => (
                  <button
                    key={mult}
                    onClick={() => handleScreenshot(mult)}
                    className="block w-full whitespace-nowrap rounded px-3 py-1.5 text-left text-xs text-primary-950 dark:text-accent-50 hover:bg-primary-950/[0.06] dark:hover:bg-white/[0.06]"
                  >
                    {label} Resolution
                  </button>
                ))}
              </div>
            )}
          </div>
          </>
          )}
        </div>
      </div>

      {/* Site Planner Mode */}
      {isSitePlannerActive ? (
        <div className="absolute inset-0 flex flex-col">
          <div className="relative min-h-0 flex-1">
            <SitePlannerGuide forceShow={showGuide} onDismiss={() => setShowGuide(false)} />
            <SitePlannerMap
              latitude={effectiveLocation?.latitude}
              longitude={effectiveLocation?.longitude}
              siteZones={siteZones}
              onZoneCreated={handleZoneCreated}
              onZoneUpdated={handleZoneUpdated}
              onZoneSelected={selectZone}
              onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
            />
            {selectedZone && (
              <ZonePropertiesPanel
                key={selectedZone.id}
                zone={selectedZone}
                onUpdate={(zoneId, data) => updateZone.mutate({ zoneId, data })}
                onDelete={(zoneId) => deleteZone.mutate(zoneId)}
                onClose={() => selectZone(null)}
                onAIGenerate={(buildingId, initialPrompt) => {
                  setAiGenerateFromZoneBuildingId(buildingId);
                  setAiGenerateFromZonePrompt(initialPrompt || null);
                  queryClient.invalidateQueries({ queryKey: ['project', id] });
                  queryClient.invalidateQueries({ queryKey: ['site-zones', id] });
                }}
                buildings={allBuildings}
                allZones={siteZones}
              />
            )}
          </div>
          <SitePlannerToolbar onViewIn3D={handleExitSitePlanner} onWalkThrough={handleWalkThrough} onShowGuide={() => setShowGuide(true)} />
        </div>
      ) : (
        <>
          {/* 3D Scene */}
          <div className="absolute inset-0" style={{ cursor: isMovingBuilding ? 'crosshair' : undefined }}>
            <SceneErrorBoundary>
              <SceneViewer
                buildings={allBuildings}
                documents={project?.documents || []}
                contextBuildings={contextBuildings}
                contextRoads={contextRoads}
                onBuildingClick={handleSelectBuilding}
                onBuildingHover={hoverBuilding}
                showMapBackground={showMap}
                latitude={effectiveLocation?.latitude}
                longitude={effectiveLocation?.longitude}
                annotations={annotations}
                onAnnotationClick={handleSceneAnnotationClick}
                onResolveAnnotation={(aId) => resolveAnnotation.mutate(aId)}
                onDeleteAnnotation={(aId) => deleteAnnotation.mutate(aId)}
                onCameraMove={collaboration.sendCursor}
                followCamera={followCamera}
                siteZones={siteZones}
                onZoneClick={selectZone}
                onBuildingMove={handleBuildingMove}
                buildingStatuses={generationStatuses}
                remoteUsers={collaboration.users
                  .filter((u) => u.id !== collaboration.connectionId)
                  .map((u) => {
                    const cursor = collaboration.cursors.get(u.id);
                    return {
                      id: u.id,
                      name: u.name,
                      color: u.color,
                      position: cursor?.position || [0, 1.7, 0],
                      target: cursor?.target || [0, 1.7, -1],
                    };
                  })
                  .filter((u) => u.position[0] !== 0 || u.position[2] !== 0)
                }
              />
            </SceneErrorBoundary>
          </div>

          <WalkthroughHUD />

          {/* Phase Comparison Overlay */}
          {isComparing && (
            <ComparisonOverlay
              activePhase={settings.activePhase}
              comparePhase={comparePhase}
              dividerPct={compareDivider}
              onDividerChange={setCompareDivider}
              phases={project?.construction_phases}
            />
          )}

          {/* Controls */}
          <ViewerControls constructionPhases={project?.construction_phases} buildings={project?.buildings} />

          {/* Legend */}
          <ViewerLegend
            phases={project?.construction_phases}
            activePhase={settings.activePhase}
            showMeasurements={settings.showMeasurements}
            showExistingBuildings={settings.showExistingBuildings}
          />

          {/* Zone properties panel — shown when a zone is clicked in 3D */}
          {selectedZone && (
            <ZonePropertiesPanel
              key={selectedZone.id}
              zone={selectedZone}
              onUpdate={(zoneId, data) => updateZone.mutate({ zoneId, data })}
              onDelete={(zoneId) => deleteZone.mutate(zoneId)}
              onClose={() => selectZone(null)}
              onAIGenerate={(buildingId, initialPrompt) => {
                setAiGenerateFromZoneBuildingId(buildingId);
                setAiGenerateFromZonePrompt(initialPrompt || null);
                queryClient.invalidateQueries({ queryKey: ['project', id] });
                queryClient.invalidateQueries({ queryKey: ['site-zones', id] });
              }}
              buildings={allBuildings}
              allZones={siteZones}
            />
          )}
        </>
      )}

      {/* Info Panel — bottom sheet on mobile, card on desktop */}
      {isInfoPanelOpen && selectedBuilding && (
        <div className="absolute bottom-0 left-0 right-0 z-20 rounded-t-xl bg-white/95 p-4 shadow-2xl backdrop-blur-sm sm:bottom-4 sm:left-auto sm:right-4 sm:w-80 sm:rounded-xl sm:p-5">
          {/* Drag handle for mobile */}
          <div className="mx-auto mb-3 h-1 w-10 rounded-full bg-neutral-300 sm:hidden" />
          <div className="flex items-start justify-between">
            <h3 className="font-semibold text-neutral-900">
              {selectedBuilding.name || 'Building Details'}
            </h3>
            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  if (!editingBuilding) {
                    setEditValues({
                      height_meters: selectedBuilding.height_meters,
                      floor_count: selectedBuilding.floor_count,
                      floor_height_meters: selectedBuilding.floor_height_meters,
                      roof_type: selectedBuilding.roof_type,
                    });
                  }
                  setEditingBuilding(!editingBuilding);
                }}
                className={`rounded-md px-2 py-0.5 text-xs font-medium ${
                  editingBuilding
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-neutral-100 text-primary-950/40 dark:text-white/40 hover:bg-neutral-200'
                }`}
              >
                {editingBuilding ? 'Cancel' : 'Edit'}
              </button>
              <button
                onClick={() => setMovingBuilding(!isMovingBuilding)}
                className={`rounded-md p-1 ${
                  isMovingBuilding
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-primary-950/50 dark:text-white/50 hover:bg-neutral-100 hover:text-primary-950/30'
                }`}
                title={isMovingBuilding ? 'Cancel move' : 'Move building'}
              >
                <Move size={14} />
              </button>
              <button
                onClick={() => deleteBuilding.mutate(selectedBuilding.id)}
                className="rounded-md p-1 text-primary-950/50 dark:text-white/50 hover:bg-red-100 hover:text-red-600"
                title="Delete building (Ctrl+Z to undo)"
              >
                <Trash2 size={14} />
              </button>
              <button
                onClick={() => selectBuilding(null)}
                className="rounded-md p-1 text-primary-950/50 dark:text-white/50 hover:bg-neutral-100 hover:text-primary-950/30"
              >
                ✕
              </button>
            </div>
          </div>

          {isMovingBuilding && (
            <div className="mt-2 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
              Click on the ground to move this building. Press Escape to cancel.
            </div>
          )}

          {editingBuilding ? (
            <div className="mt-3 space-y-2 text-sm">
              <div>
                <label className="block text-xs text-primary-950/40 dark:text-white/40">Height (m)</label>
                <input
                  type="number"
                  step="0.1"
                  value={editValues.height_meters ?? ''}
                  onChange={(e) => setEditValues((v) => ({ ...v, height_meters: parseFloat(e.target.value) || undefined }))}
                  className="mt-0.5 w-full rounded border border-neutral-200 px-2 py-1 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-primary-950/40 dark:text-white/40">Floors</label>
                <input
                  type="number"
                  step="1"
                  value={editValues.floor_count ?? ''}
                  onChange={(e) => setEditValues((v) => ({ ...v, floor_count: parseInt(e.target.value) || undefined }))}
                  className="mt-0.5 w-full rounded border border-neutral-200 px-2 py-1 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-primary-950/40 dark:text-white/40">Floor Height (m)</label>
                <input
                  type="number"
                  step="0.1"
                  value={editValues.floor_height_meters ?? ''}
                  onChange={(e) => setEditValues((v) => ({ ...v, floor_height_meters: parseFloat(e.target.value) || undefined }))}
                  className="mt-0.5 w-full rounded border border-neutral-200 px-2 py-1 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-primary-950/40 dark:text-white/40">Roof Type</label>
                <select
                  value={editValues.roof_type || 'flat'}
                  onChange={(e) => setEditValues((v) => ({ ...v, roof_type: e.target.value }))}
                  className="mt-0.5 w-full rounded border border-neutral-200 px-2 py-1 text-sm"
                >
                  <option value="flat">Flat</option>
                  <option value="gabled">Gabled</option>
                  <option value="hipped">Hipped</option>
                </select>
              </div>
              <button
                onClick={() =>
                  updateBuilding.mutate({
                    buildingId: selectedBuilding.id,
                    data: editValues,
                    _undoPrevious: {
                      height_meters: selectedBuilding.height_meters,
                      floor_count: selectedBuilding.floor_count,
                      floor_height_meters: selectedBuilding.floor_height_meters,
                      roof_type: selectedBuilding.roof_type,
                    },
                    _undoLabel: 'Edit building',
                  })
                }
                disabled={updateBuilding.isPending}
                className="mt-2 w-full rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {updateBuilding.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          ) : (
            <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-1 sm:gap-x-0">
              {selectedBuilding.height_meters && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">Height</dt>
                  <dd className="font-medium">{selectedBuilding.height_meters}m</dd>
                </div>
              )}
              {selectedBuilding.floor_count && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">Floors</dt>
                  <dd className="font-medium">{selectedBuilding.floor_count}</dd>
                </div>
              )}
              {selectedBuilding.roof_type && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">Roof Type</dt>
                  <dd className="font-medium capitalize">{selectedBuilding.roof_type}</dd>
                </div>
              )}
              {selectedBuilding.specifications?.total_area_sqm && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">Total Area</dt>
                  <dd className="font-medium">
                    {selectedBuilding.specifications.total_area_sqm.toLocaleString()} m²
                  </dd>
                </div>
              )}
              {selectedBuilding.specifications?.residential_units && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">Units</dt>
                  <dd className="font-medium">{selectedBuilding.specifications.residential_units}</dd>
                </div>
              )}
              {selectedBuilding.specifications?.ai_confidence != null && (
                <div className="flex justify-between">
                  <dt className="text-primary-950/40 dark:text-white/40">AI Confidence</dt>
                  <dd className="font-medium">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        (selectedBuilding.specifications.ai_confidence as number) >= 0.7
                          ? 'bg-green-100 text-green-700'
                          : (selectedBuilding.specifications.ai_confidence as number) >= 0.4
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {Math.round((selectedBuilding.specifications.ai_confidence as number) * 100)}%
                    </span>
                  </dd>
                </div>
              )}
            </dl>
          )}
          {/* Rotation control */}
          <RotationSlider
            buildingId={selectedBuilding.id}
            value={selectedBuilding.rotation_degrees ?? 0}
            onDrag={(deg) => {
              // Capture the rotation before drag starts for undo
              if (rotationBeforeDrag.current === null) {
                rotationBeforeDrag.current = selectedBuilding.rotation_degrees ?? 0;
              }
              // Optimistic cache update for instant 3D feedback (no API call)
              queryClient.setQueryData(['project', id], (old: any) => {
                if (!old?.buildings) return old;
                return {
                  ...old,
                  buildings: old.buildings.map((b: any) =>
                    b.id === selectedBuilding.id ? { ...b, rotation_degrees: deg } : b
                  ),
                };
              });
            }}
            onCommit={(deg) => {
              // Push undo action for rotation change
              const prevDeg = rotationBeforeDrag.current;
              rotationBeforeDrag.current = null;
              if (!useUndoRedoStore.getState()._isSystemAction && id && prevDeg !== null && prevDeg !== deg) {
                useUndoRedoStore.getState().pushAction(
                  createBuildingRotationAction(id, selectedBuilding.id, prevDeg, deg, queryClient),
                );
              }
              // Save to API only when user releases the slider
              updateBuilding.mutate({
                buildingId: selectedBuilding.id,
                data: { rotation_degrees: deg },
                silent: true,
              });
            }}
          />
          {/* Material picker */}
          <div className="mt-3 border-t border-neutral-100 pt-3">
            <label className="mb-1.5 block text-xs font-medium text-primary-950/40 dark:text-white/40">Facade Material</label>
            <div className="flex flex-wrap gap-1.5">
              {(['concrete', 'glass', 'brick', 'metal', 'wood', 'green_roof'] as const).map((mat) => {
                const colors: Record<string, string> = {
                  concrete: 'bg-gray-300',
                  glass: 'bg-sky-200',
                  brick: 'bg-orange-400',
                  metal: 'bg-slate-400',
                  wood: 'bg-amber-600',
                  green_roof: 'bg-green-500',
                };
                const isActive = (selectedBuilding.specifications?.facade_material as string) === mat;
                return (
                  <button
                    key={mat}
                    title={mat}
                    onClick={() => {
                      const prevSpecs = selectedBuilding.specifications ? { ...selectedBuilding.specifications } : undefined;
                      const newSpecs = { ...selectedBuilding.specifications, facade_material: mat };
                      // Push undo action for material change
                      if (!useUndoRedoStore.getState()._isSystemAction && id) {
                        useUndoRedoStore.getState().pushAction(
                          createBuildingMaterialAction(id, selectedBuilding.id, prevSpecs, newSpecs, queryClient),
                        );
                      }
                      updateBuilding.mutate({
                        buildingId: selectedBuilding.id,
                        data: { specifications: newSpecs },
                      });
                    }}
                    className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium capitalize transition-all ${
                      isActive
                        ? 'ring-2 ring-primary-500 ring-offset-1 bg-primary-50 text-primary-700'
                        : 'bg-neutral-50 text-primary-950/30 dark:text-white/30 hover:bg-neutral-100'
                    }`}
                  >
                    <span className={`inline-block h-2.5 w-2.5 rounded-full ${colors[mat]}`} />
                    {mat}
                  </button>
                );
              })}
            </div>
          </div>
          {selectedBuilding.model_url && (
            <button
              onClick={() =>
                handleDownloadGLB(selectedBuilding.id, selectedBuilding.name || undefined)
              }
              className="mt-4 flex w-full items-center justify-center gap-1.5 rounded-lg bg-primary-50 px-3 py-2 text-sm font-medium text-primary-700 hover:bg-primary-100"
            >
              <Download size={14} />
              Download 3D Model
            </button>
          )}
        </div>
      )}

      {/* Annotation input popup */}
      {pendingAnnotationPos && (
        <div className="absolute bottom-4 left-1/2 z-30 -translate-x-1/2">
          <div className="rounded-xl bg-white/95 p-4 shadow-2xl backdrop-blur-sm" style={{ width: 320 }}>
            <p className="mb-2 text-xs font-medium text-primary-950/40 dark:text-white/40">Add annotation at this point</p>
            <textarea
              autoFocus
              value={annotationText}
              onChange={(e) => setAnnotationText(e.target.value)}
              placeholder="Enter your comment..."
              rows={2}
              className="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={handleSubmitAnnotation}
                disabled={!annotationText.trim()}
                className="btn-primary flex-1 text-sm disabled:opacity-50"
              >
                Add
              </button>
              <button
                onClick={() => setPendingAnnotationPos(null)}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Generate Modal */}
      {showAIGenerateModal && selectedBuildingId && (
        <AIGenerateModal
          buildingId={selectedBuildingId}
          buildingName={selectedBuilding?.name}
          onClose={() => setShowAIGenerateModal(false)}
          onComplete={() => {
            queryClient.invalidateQueries({ queryKey: ['project', id] });
            setShowAIGenerateModal(false);
          }}
        />
      )}
      {showAIGenerateModal && !selectedBuildingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="mx-4 w-full max-w-sm rounded-xl bg-white dark:bg-primary-900 p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={20} className="text-purple-500" />
              <h2 className="text-lg font-bold text-neutral-900">AI Generate</h2>
            </div>
            <p className="text-sm text-primary-950/30 dark:text-white/30 mb-4">
              Select a building first to generate a 3D model for it, or create a new building to get started.
            </p>
            <button
              onClick={() => setShowAIGenerateModal(false)}
              className="w-full rounded-lg bg-neutral-100 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-200"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Generate Neighborhood Confirmation Dialog */}
      {showGenerateConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowGenerateConfirm(false)}>
          <div className="mx-4 w-full max-w-sm rounded-xl bg-white dark:bg-primary-900 p-6 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={20} className="text-purple-600" />
              <h2 className="text-lg font-bold text-neutral-900">Generate Neighborhood</h2>
            </div>
            <p className="text-sm text-primary-950/30 dark:text-white/30 mb-4">
              Choose which zones to generate 3D models for:
            </p>
            <div className="flex flex-col gap-2">
              {selectedBoundary && (
                <button
                  onClick={() => runGenerate('boundary')}
                  className="w-full rounded-lg bg-purple-600 px-4 py-2.5 text-left text-sm font-medium text-primary-950 dark:text-accent-50 hover:bg-purple-700"
                >
                  <div>Generate for &ldquo;{selectedBoundary.name || 'Selected Boundary'}&rdquo;</div>
                  <div className="text-purple-200 text-xs mt-0.5">Boundary-scoped zones only</div>
                </button>
              )}
              <button
                onClick={() => runGenerate('all')}
                className="w-full rounded-lg bg-purple-700 px-4 py-2.5 text-left text-sm font-medium text-primary-950 dark:text-accent-50 hover:bg-purple-800"
              >
                <div>Generate all zones</div>
                <div className="text-purple-200 text-xs mt-0.5">{totalBuildableCount} zone{totalBuildableCount !== 1 ? 's' : ''}, ~{totalUnits} unit{totalUnits !== 1 ? 's' : ''}</div>
              </button>
              <button
                onClick={() => setShowGenerateConfirm(false)}
                className="w-full rounded-lg bg-neutral-100 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Generate Modal from Zone */}
      {aiGenerateFromZoneBuildingId && (
        <AIGenerateModal
          buildingId={aiGenerateFromZoneBuildingId}
          buildingName={selectedZone?.name || 'Zone Building'}
          initialPrompt={aiGenerateFromZonePrompt || undefined}
          onClose={() => {
            setAiGenerateFromZoneBuildingId(null);
            setAiGenerateFromZonePrompt(null);
          }}
          onComplete={() => {
            queryClient.invalidateQueries({ queryKey: ['project', id] });
            queryClient.invalidateQueries({ queryKey: ['site-zones', id] });
            setAiGenerateFromZoneBuildingId(null);
            setAiGenerateFromZonePrompt(null);
          }}
        />
      )}

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="mx-4 w-full max-w-lg rounded-xl bg-white dark:bg-primary-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-neutral-900">Keyboard Shortcuts</h2>
              <button onClick={() => setShowShortcuts(false)} className="rounded-md p-1 text-primary-950/50 dark:text-white/50 hover:bg-neutral-100 hover:text-primary-950/30">
                <X size={20} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-sm">
              <ShortcutSection title="Navigation">
                <ShortcutRow keys="W A S D" desc="Move camera" />
                <ShortcutRow keys="Q / Space" desc="Move up" />
                <ShortcutRow keys="E / Shift" desc="Move down" />
                <ShortcutRow keys="Arrow keys" desc="Move camera" />
                <ShortcutRow keys="Scroll" desc="Zoom in/out" />
              </ShortcutSection>
              <ShortcutSection title="Modes">
                <ShortcutRow keys="?" desc="Toggle this help" />
                <ShortcutRow keys="Esc" desc="Close panel/modal" />
                <ShortcutRow keys="Enter" desc="Close area measurement" />
              </ShortcutSection>
              <ShortcutSection title="First Person / Fly">
                <ShortcutRow keys="Click" desc="Enter pointer lock" />
                <ShortcutRow keys="Mouse" desc="Look around" />
                <ShortcutRow keys="W A S D" desc="Move" />
              </ShortcutSection>
              <ShortcutSection title="Tools">
                <ShortcutRow keys="Click" desc="Place measurement point" />
                <ShortcutRow keys="Dbl-click" desc="Close polygon" />
              </ShortcutSection>
            </div>
            <p className="mt-4 text-center text-xs text-primary-950/50 dark:text-white/50">Press ? or Esc to close</p>
          </div>
        </div>
      )}
      <ImageLightbox />
    </div>
  );
}

function ShortcutSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <h3 className="mb-1 text-xs font-semibold uppercase tracking-wider text-primary-950/50 dark:text-white/50">{title}</h3>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

function ShortcutRow({ keys, desc }: { keys: string; desc: string }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-primary-950/30 dark:text-white/30">{desc}</span>
      <div className="flex gap-1">
        {keys.split(' ').map((k, i) =>
          k === '/' ? (
            <span key={i} className="text-primary-950/50 dark:text-white/50">/</span>
          ) : (
            <kbd key={i} className="rounded bg-neutral-100 px-1.5 py-0.5 text-[11px] font-mono font-medium text-neutral-700">
              {k}
            </kbd>
          )
        )}
      </div>
    </div>
  );
}

/** Rotation slider: drags update 3D instantly via cache; saves to API on release. */
function RotationSlider({
  buildingId,
  value,
  onDrag,
  onCommit,
}: {
  buildingId: string;
  value: number;
  onDrag: (deg: number) => void;
  onCommit: (deg: number) => void;
}) {
  const [localDeg, setLocalDeg] = useState(value);

  // Sync with server value when building selection changes
  useEffect(() => { setLocalDeg(value); }, [value, buildingId]);

  return (
    <div className="mt-3 border-t border-neutral-100 pt-3">
      <label className="mb-1 flex items-center gap-1 text-xs font-medium text-primary-950/40 dark:text-white/40">
        <RotateCw size={12} />
        Rotation
        <span className="ml-auto tabular-nums text-primary-950/50 dark:text-white/50">{localDeg}°</span>
      </label>
      <input
        type="range"
        min="0"
        max="360"
        step="5"
        value={localDeg}
        onChange={(e) => {
          const deg = parseFloat(e.target.value);
          setLocalDeg(deg);
          onDrag(deg);
        }}
        onMouseUp={() => onCommit(localDeg)}
        onTouchEnd={() => onCommit(localDeg)}
        className="w-full accent-primary-600"
      />
    </div>
  );
}

function ViewerLegend({
  phases,
  activePhase,
  showMeasurements,
  showExistingBuildings,
}: {
  phases?: import('@/types').ConstructionPhase[];
  activePhase: number | null;
  showMeasurements: boolean;
  showExistingBuildings: boolean;
}) {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <div className="absolute bottom-4 left-4 z-20 hidden sm:block">
      <button
        onClick={() => setCollapsed((v) => !v)}
        className="rounded-lg bg-white/90 px-3 py-1.5 text-xs font-medium text-primary-950/30 dark:text-white/30 shadow-card backdrop-blur-sm hover:bg-white"
      >
        {collapsed ? 'Legend' : 'Hide Legend'}
      </button>
      {!collapsed && (
        <div className="mt-2 rounded-lg bg-white/90 p-3 shadow-card backdrop-blur-sm" style={{ minWidth: 160 }}>
          <div className="space-y-2 text-[11px]">
            {/* Phase colors */}
            {phases && phases.length > 0 && (
              <div>
                <div className="mb-1 font-semibold text-primary-950/30 dark:text-white/30">Construction Phases</div>
                {phases
                  .sort((a, b) => a.phase_number - b.phase_number)
                  .map((p) => (
                    <div key={p.phase_number} className="flex items-center gap-2 py-0.5">
                      <span
                        className="inline-block h-2.5 w-2.5 rounded-full border border-neutral-200"
                        style={{ backgroundColor: p.color || '#94a3b8' }}
                      />
                      <span className={activePhase === p.phase_number ? 'font-medium text-neutral-800' : 'text-primary-950/40 dark:text-white/40'}>
                        {p.name}
                      </span>
                    </div>
                  ))}
              </div>
            )}

            {/* Context buildings */}
            {showExistingBuildings && (
              <div className="flex items-center gap-2 py-0.5">
                <span className="inline-block h-2.5 w-2.5 rounded-full border border-neutral-200" style={{ backgroundColor: '#c0c0c0', opacity: 0.6 }} />
                <span className="text-primary-950/40 dark:text-white/40">Existing Buildings</span>
              </div>
            )}

            {/* Measurements */}
            {showMeasurements && (
              <div>
                <div className="mb-1 mt-1 font-semibold text-primary-950/30 dark:text-white/30">Measurements</div>
                <div className="flex items-center gap-2 py-0.5">
                  <span className="inline-block h-0.5 w-3 rounded bg-red-500" />
                  <span className="text-primary-950/40 dark:text-white/40">Distance</span>
                </div>
                <div className="flex items-center gap-2 py-0.5">
                  <span className="inline-block h-2.5 w-2.5 rounded-sm bg-amber-400/40 border border-amber-400" />
                  <span className="text-primary-950/40 dark:text-white/40">Area</span>
                </div>
                <div className="flex items-center gap-2 py-0.5">
                  <span className="inline-block h-3 w-0.5 rounded bg-violet-500" />
                  <span className="text-primary-950/40 dark:text-white/40">Height</span>
                </div>
                <div className="flex items-center gap-2 py-0.5">
                  <span className="inline-block h-0.5 w-3 rounded bg-cyan-500" />
                  <span className="text-primary-950/40 dark:text-white/40">Angle</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ComparisonOverlay({
  activePhase,
  comparePhase,
  dividerPct,
  onDividerChange,
  phases,
}: {
  activePhase: number | null;
  comparePhase: number | null;
  dividerPct: number;
  onDividerChange: (pct: number) => void;
  phases?: import('@/types').ConstructionPhase[];
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);

  const getPhaseLabel = (phase: number | null) => {
    if (phase === null) return 'All Phases';
    const p = phases?.find((pp) => pp.phase_number === phase);
    return p?.name || `Phase ${phase}`;
  };

  const handlePointerDown = () => setDragging(true);

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!dragging || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      onDividerChange(pct);
    },
    [dragging, onDividerChange]
  );

  const handlePointerUp = () => setDragging(false);

  return (
    <div
      ref={containerRef}
      className="pointer-events-auto absolute inset-0 z-10"
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
      style={{ pointerEvents: dragging ? 'auto' : 'none' }}
    >
      {/* Left label */}
      <div className="pointer-events-none absolute top-16 z-30" style={{ left: `calc(${dividerPct}% - 120px)` }}>
        <div className="rounded-r-md bg-blue-600/80 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
          {getPhaseLabel(activePhase)}
        </div>
      </div>

      {/* Right label */}
      <div className="pointer-events-none absolute top-16 z-30" style={{ left: `calc(${dividerPct}% + 8px)` }}>
        <div className="rounded-l-md bg-amber-500/80 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
          {getPhaseLabel(comparePhase)}
        </div>
      </div>

      {/* Divider line */}
      <div
        className="absolute top-0 bottom-0 z-20 cursor-col-resize"
        style={{ left: `${dividerPct}%`, width: 4, marginLeft: -2, pointerEvents: 'auto' }}
        onPointerDown={handlePointerDown}
      >
        <div className="h-full w-full bg-white dark:bg-primary-900 shadow-lg" />
        {/* Handle grip */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white dark:bg-primary-900 p-1.5 shadow-lg">
          <div className="flex gap-0.5">
            <div className="h-4 w-0.5 rounded-full bg-neutral-400" />
            <div className="h-4 w-0.5 rounded-full bg-neutral-400" />
          </div>
        </div>
      </div>
    </div>
  );
}
