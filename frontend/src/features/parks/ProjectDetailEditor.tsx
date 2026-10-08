import { useState } from "react";
import { createPortal } from "react-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import type { Project, SiteZone } from "@/types";
import { BenchLayoutEditor } from "./BenchDetailEditor";
import {
  projectBenchFrame,
  projectBenchContext,
  readProjectDetails,
  saveProjectDetails,
  type ProjectDetails,
} from "./projectBenches";

export function useProjectDetails(projectId?: string) {
  return useQuery({
    queryKey: ["project-details", projectId],
    queryFn: async () =>
      (await api.get<ProjectDetails>(`/api/v1/projects/${projectId}/details`))
        .data,
    enabled: !!projectId,
    staleTime: 30_000,
    refetchOnWindowFocus: false,
  });
}

export function ProjectDetailEditor({
  project,
  zones,
  data,
  onClose,
}: {
  project: Project;
  zones: SiteZone[];
  data: ProjectDetails;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  // Keep the opened revision: concurrent writes must never replace this draft silently.
  const [source] = useState(data);
  const [context] = useState(() =>
    projectBenchContext(
      projectBenchFrame(
        zones,
        [
          ...source.benches,
          ...(source.trees ?? []),
          ...(source.props ?? []),
          ...(source.surfaces ?? []).flatMap((s) =>
            s.coordinates.map(([lng, lat], i) => ({
              id: `${s.id}-${i}`,
              lng,
              lat,
              angle: 0,
            })),
          ),
        ],
        project.location,
      ),
    ),
  );
  return createPortal(
    <BenchLayoutEditor
      title={project.name}
      context={context}
      initialBenches={readProjectDetails(source, context)}
      initialSurfaces={source.surfaces ?? []}
      contextZones={zones}
      disabled={!source.can_edit}
      onClose={onClose}
      onSave={async (benches, surfaces) => {
        const response = await api.put<ProjectDetails>(
          `/api/v1/projects/${project.id}/details`,
          {
            expected_revision: source.revision,
            ...saveProjectDetails(benches, context),
            surfaces,
          },
        );
        queryClient.setQueryData(
          ["project-details", project.id],
          response.data,
        );
      }}
    />,
    document.body,
  );
}
