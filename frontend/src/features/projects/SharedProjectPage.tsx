import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Box, Eye, Loader2 } from 'lucide-react';
import { sharesApi } from '@/services/api';

export function SharedProjectPage() {
  const { token } = useParams<{ token: string }>();

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['shared-project', token],
    queryFn: () => sharesApi.getSharedProject(token!),
    enabled: !!token,
  });

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 size={32} className="animate-spin text-primary-500" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center px-4">
        <h1 className="text-xl font-bold text-primary-950 dark:text-accent-50">Link expired or invalid</h1>
        <p className="mt-2 text-sm text-primary-950/50 dark:text-white/50">This share link may have been revoked.</p>
        <Link to="/projects" className="mt-4 text-sm font-medium text-primary-500 hover:text-primary-400">
          Go to home page
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="bg-white dark:bg-primary-900 shadow-lg">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:h-16 sm:px-6">
          <Link to="/projects" className="flex items-center gap-2">
            <Box className="h-7 w-7 text-coral-500" />
            <span className="text-lg font-bold text-primary-950 dark:text-accent-50">SiteForge</span>
          </Link>
          <span className="rounded-full bg-primary-500/20 px-3 py-1 text-xs font-medium text-coral-500">
            Shared view
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-bold text-primary-950 dark:text-accent-50 sm:text-2xl">{project.name}</h1>
            {project.description && (
              <p className="mt-1 text-sm text-primary-950/50 dark:text-white/50">{project.description}</p>
            )}
          </div>
          <Link
            to={`/projects/${project.id}/viewer`}
            className="btn-primary shrink-0 self-start sm:self-auto"
          >
            <Eye size={16} className="mr-2" />
            Open 3D Viewer
          </Link>
        </div>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div className="card">
            <h3 className="font-semibold text-primary-950 dark:text-accent-50">Project Info</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div>
                <dt className="text-primary-950/50 dark:text-white/50">Status</dt>
                <dd className="capitalize text-primary-950 dark:text-accent-50">{project.status}</dd>
              </div>
              <div>
                <dt className="text-primary-950/50 dark:text-white/50">Buildings</dt>
                <dd className="text-primary-950 dark:text-accent-50">{project.buildings?.length || 0}</dd>
              </div>
              <div>
                <dt className="text-primary-950/50 dark:text-white/50">Documents</dt>
                <dd className="text-primary-950 dark:text-accent-50">{project.documents?.length || 0}</dd>
              </div>
            </dl>
          </div>

          {project.buildings && project.buildings.length > 0 && (
            <div className="card sm:col-span-2">
              <h3 className="font-semibold text-primary-950 dark:text-accent-50">Buildings</h3>
              <div className="mt-3 space-y-2">
                {project.buildings.map((b) => (
                  <div key={b.id} className="flex items-center justify-between rounded-lg border border-primary-950/[0.08] dark:border-white/[0.08] px-3 py-2">
                    <p className="text-sm font-medium text-primary-950/60 dark:text-white/60">{b.name || 'Unnamed Building'}</p>
                    <span className="text-xs text-primary-950/50 dark:text-white/50">
                      {b.floor_count && `${b.floor_count} floors`}
                      {b.height_meters && ` · ${b.height_meters}m`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
