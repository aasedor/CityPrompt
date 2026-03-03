import { useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Eye, FileText } from 'lucide-react';
import { projectsApi } from '@/services/api';
import { SitePlannerMap } from '@/components/viewer/SitePlannerMap';
import { SitePlannerToolbar } from '@/components/viewer/SitePlannerToolbar';
import { ZonePropertiesPanel } from '@/components/viewer/ZonePropertiesPanel';
import { AIGenerateModal } from '@/components/buildings/AIGenerateModal';
import { useViewerStore } from '@/store';
import { useSiteZones } from '@/hooks/useSiteZones';
import { UndoRedoButtons } from '@/components/ui/UndoRedoButtons';
import { ImageLightbox } from '@/components/ui/ImageLightbox';
import { useUndoRedoKeyboard } from '@/hooks/useUndoRedoKeyboard';
import { useState } from 'react';

export function SitePlannerPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    setSitePlannerActive,
    setActiveSitePlannerTool,
    selectedZoneId,
    selectZone,
  } = useViewerStore();

  useUndoRedoKeyboard();
  const [aiGenerateBuildingId, setAiGenerateBuildingId] = useState<string | null>(null);

  // Activate site planner on mount, set residential as default tool
  useEffect(() => {
    setSitePlannerActive(true);
    setActiveSitePlannerTool('residential');
    return () => {
      setSitePlannerActive(false);
      setActiveSitePlannerTool(null);
      selectZone(null);
    };
  }, [setSitePlannerActive, setActiveSitePlannerTool, selectZone]);

  const { data: project, isLoading, isError } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
    retry: 3,
    retryDelay: (attempt) => Math.min(500 * 2 ** attempt, 3000),
  });

  const {
    siteZones,
    updateZone,
    deleteZone,
    handleZoneCreated,
    handleZoneUpdated,
  } = useSiteZones(id);

  const selectedZone = siteZones.find((z) => z.id === selectedZoneId) || null;

  const handleZoneSelected = useCallback((zoneId: string | null) => {
    selectZone(zoneId);
  }, [selectZone]);

  const handleViewIn3D = useCallback(() => {
    navigate(`/projects/${id}/viewer`);
  }, [navigate, id]);

  const handleWalkThrough = useCallback(() => {
    navigate(`/projects/${id}/viewer`);
  }, [navigate, id]);

  if (isLoading || (!project && !isError)) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-primary-900 text-white">
        Loading project...
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex h-screen w-screen flex-col items-center justify-center gap-3 bg-primary-900 text-white">
        <p>Project not found</p>
        <Link to="/projects" className="text-sm text-primary-400 hover:text-primary-300">
          Back to projects
        </Link>
      </div>
    );
  }

  return (
    <div className="relative flex h-screen w-screen flex-col overflow-hidden bg-primary-900">
      {/* Header overlay */}
      <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between bg-primary-900/70 px-4 py-3 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <Link
            to="/projects"
            className="rounded-lg p-2 text-white/70 hover:bg-white/10 hover:text-white"
            title="Home"
          >
            <ArrowLeft size={18} />
          </Link>
          <Link
            to={`/projects/${id}`}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-white/70 hover:bg-white/10 hover:text-white"
          >
            <FileText size={14} className="mr-1.5 inline" />
            Project Details
          </Link>
        </div>

        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
          <h1 className="text-sm font-semibold text-white sm:text-base">{project.name}</h1>
          {project.location?.address && (
            <p className="mt-0.5 text-xs text-white/60">{project.location.address}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <UndoRedoButtons />
          <Link
            to={`/projects/${id}/viewer`}
            className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700"
          >
            <Eye size={14} />
            <span className="hidden sm:inline">View in 3D</span>
            <span className="sm:hidden">3D</span>
          </Link>
        </div>
      </div>

      {/* Map fills remaining space */}
      <div className="min-h-0 flex-1">
        <SitePlannerMap
          latitude={project.location?.latitude}
          longitude={project.location?.longitude}
          siteZones={siteZones}
          onZoneCreated={handleZoneCreated}
          onZoneUpdated={handleZoneUpdated}
          onZoneSelected={handleZoneSelected}
          onZoneDeleted={(zoneId) => deleteZone.mutate(zoneId)}
        />
      </div>

      {/* Zone properties panel */}
      {selectedZone && (
        <ZonePropertiesPanel
          key={selectedZone.id}
          zone={selectedZone}
          onUpdate={(zoneId, data) => updateZone.mutate({ zoneId, data })}
          onDelete={(zoneId) => deleteZone.mutate(zoneId)}
          onClose={() => selectZone(null)}
          onAIGenerate={(buildingId) => setAiGenerateBuildingId(buildingId)}
          buildings={project.buildings}
          allZones={siteZones}
        />
      )}

      {/* Image lightbox */}
      <ImageLightbox />

      {/* Toolbar */}
      <SitePlannerToolbar
        onViewIn3D={handleViewIn3D}
        onWalkThrough={handleWalkThrough}
        projectId={id}
        zones={siteZones}
      />

      {/* AI Generate modal */}
      {aiGenerateBuildingId && (
        <AIGenerateModal
          buildingId={aiGenerateBuildingId}
          buildingName={project.buildings?.find((b) => b.id === aiGenerateBuildingId)?.name}
          onClose={() => setAiGenerateBuildingId(null)}
          onComplete={() => setAiGenerateBuildingId(null)}
        />
      )}
    </div>
  );
}
