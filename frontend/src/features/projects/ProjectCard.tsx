import { Link } from 'react-router-dom';
import { Clock, MapPin } from 'lucide-react';
import type { Project } from '@/types';

const statusColors: Record<string, string> = {
  draft: 'border-2 border-[#151515] bg-white text-[#151515]',
  processing: 'border-2 border-[#151515] bg-[#f2b84b] text-[#151515]',
  ready: 'border-2 border-[#151515] bg-[#c9ff3d] text-[#151515]',
  archived: 'border-2 border-[#151515] bg-[#d7d2c6] text-[#151515]',
};

export interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link
      to={`/projects/${project.id}`}
      className="group block rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[6px_6px_0_0_#151515] transition-transform hover:-translate-y-0.5 sm:p-6"
    >
      <div className="flex items-start justify-between">
        <h3 className="font-black text-[#151515] group-hover:text-[#0aa6a6]">
          {project.name}
        </h3>
        <span
          className={`badge ${statusColors[project.status]}`}
        >
          {project.status}
        </span>
      </div>
      {project.description && (
        <p className="mt-2 line-clamp-2 text-sm font-semibold text-[#5c554d]">
          {project.description}
        </p>
      )}
      {project.location?.address && (
        <div className="mt-2 flex items-center text-xs font-semibold text-[#151515]/50">
          <MapPin size={11} className="mr-1 flex-shrink-0" />
          <span className="truncate">{project.location.address}</span>
        </div>
      )}
      <div className="mt-4 flex items-center text-xs font-semibold text-[#151515]/50">
        <Clock size={12} className="mr-1" />
        Updated {new Date(project.updated_at).toLocaleDateString()}
      </div>
    </Link>
  );
}
