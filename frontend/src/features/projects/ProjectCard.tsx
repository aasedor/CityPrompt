import { Link } from 'react-router-dom';
import { Clock, MapPin } from 'lucide-react';
import type { Project } from '@/types';

const statusColors: Record<string, string> = {
  draft: 'bg-primary-950/[0.06] dark:bg-white/[0.06] text-primary-950/50 dark:text-white/50',
  processing: 'bg-amber-500/15 text-amber-400',
  ready: 'bg-emerald-500/15 text-emerald-400',
  archived: 'bg-primary-500/15 text-primary-400',
};

export interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link
      to={`/projects/${project.id}`}
      className="card-hover group"
    >
      <div className="flex items-start justify-between">
        <h3 className="font-semibold text-primary-950 dark:text-accent-50 group-hover:text-coral-500">
          {project.name}
        </h3>
        <span
          className={`badge ${statusColors[project.status]}`}
        >
          {project.status}
        </span>
      </div>
      {project.description && (
        <p className="mt-2 line-clamp-2 text-sm text-primary-950/50 dark:text-white/50">
          {project.description}
        </p>
      )}
      {project.location?.address && (
        <div className="mt-2 flex items-center text-xs text-primary-950/40 dark:text-white/40">
          <MapPin size={11} className="mr-1 flex-shrink-0" />
          <span className="truncate">{project.location.address}</span>
        </div>
      )}
      <div className="mt-4 flex items-center text-xs text-primary-950/40 dark:text-white/40">
        <Clock size={12} className="mr-1" />
        Updated {new Date(project.updated_at).toLocaleDateString()}
      </div>
    </Link>
  );
}
