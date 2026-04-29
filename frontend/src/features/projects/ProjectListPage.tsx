import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Download, Images, Plus, FolderOpen, Clock, X, MapPin } from 'lucide-react';
import { getApiErrorMessage, projectsApi, rendersApi, resolveApiFileUrl } from '@/services/api';
import { useAuthStore } from '@/store';
import type { Project, Location, SavedRender } from '@/types';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface GeocodeSuggestion {
  place_name: string;
  center: [number, number]; // [lng, lat]
}

function isTextEntryTarget(target: EventTarget | null): boolean {
  const element = target as HTMLElement | null;
  return Boolean(element?.closest('input, textarea, select, [contenteditable="true"]'));
}

export function ProjectListPage() {
  const { user: currentUser } = useAuthStore();
  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'cofounder';
  const queryClient = useQueryClient();
  const location = useLocation();
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [addressQuery, setAddressQuery] = useState('');
  const [addressSuggestions, setAddressSuggestions] = useState<GeocodeSuggestion[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [error, setError] = useState('');
  const [expandedRender, setExpandedRender] = useState<{ project: Project; render: SavedRender } | null>(null);
  const geocodeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Debounced geocoding
  const geocodeAddress = useCallback((query: string) => {
    if (geocodeTimerRef.current) clearTimeout(geocodeTimerRef.current);
    if (!query.trim() || !MAPBOX_TOKEN) {
      setAddressSuggestions([]);
      return;
    }
    geocodeTimerRef.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${MAPBOX_TOKEN}&limit=5&types=address,place,locality,neighborhood`
        );
        const data = await res.json();
        if (data.features) {
          setAddressSuggestions(
            data.features.map((f: any) => ({ place_name: f.place_name, center: f.center }))
          );
          setShowSuggestions(true);
          setHighlightedIndex(-1);
        }
      } catch {
        setAddressSuggestions([]);
      }
    }, 350);
  }, []);

  const selectSuggestion = (s: GeocodeSuggestion) => {
    setAddressQuery(s.place_name);
    setSelectedLocation({
      latitude: s.center[1],
      longitude: s.center[0],
      address: s.place_name,
    });
    setShowSuggestions(false);
    setHighlightedIndex(-1);
  };

  const handleAddressKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || addressSuggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < addressSuggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev > 0 ? prev - 1 : addressSuggestions.length - 1
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightedIndex >= 0) {
        selectSuggestion(addressSuggestions[highlightedIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  useEffect(() => {
    if (location.pathname === '/projects/new') {
      setShowCreate(true);
    }
  }, [location.pathname]);

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  });

  const { data: rendersByProject = {}, isLoading: rendersLoading } = useQuery({
    queryKey: ['projects', 'saved-renders', projects?.map((project) => project.id) ?? []],
    enabled: Boolean(projects?.length),
    queryFn: async () => {
      const entries = await Promise.all(
        (projects ?? []).map(async (project) => {
          try {
            return [project.id, await rendersApi.list(project.id)] as const;
          } catch {
            return [project.id, []] as const;
          }
        }),
      );
      return Object.fromEntries(entries) as Record<string, SavedRender[]>;
    },
    staleTime: 30_000,
  });

  const createMutation = useMutation({
    mutationFn: () => projectsApi.create({
      name: newName,
      description: newDescription || undefined,
      location: selectedLocation || undefined,
    }),
    onSuccess: (newProject) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      if (newProject?.id) {
        queryClient.setQueryData(['project', newProject.id], newProject);
      }
      setShowCreate(false);
      setNewName('');
      setNewDescription('');
      setAddressQuery('');
      setSelectedLocation(null);
      setError('');
      toast.success('Project created!');
      if (newProject?.id) {
        navigate(`/projects/${newProject.id}`);
      }
    },
    onError: (err: any) => {
      setError(getApiErrorMessage(err, 'Failed to create project. Check that the backend is running.'));
    },
  });

  const handleCreate = () => {
    if (!newName.trim()) {
      setError('Project name is required');
      return;
    }
    setError('');
    createMutation.mutate();
  };

  const handleCancel = () => {
    setShowCreate(false);
    setError('');
    if (location.pathname === '/projects/new') {
      navigate('/projects');
    }
  };

  const statusColors: Record<string, string> = {
    draft: 'border-2 border-[#151515] bg-[#fefaf7] text-[#151515]',
    processing: 'border-2 border-[#151515] bg-[#f2b84b] text-[#151515]',
    ready: 'border-2 border-[#151515] bg-[#c9ff3d] text-[#151515]',
    archived: 'border-2 border-[#151515] bg-[#d7d2c6] text-[#151515]',
  };

  const stepExpandedRender = useCallback((direction: -1 | 1) => {
    if (!expandedRender) return;
    const projectRenders = rendersByProject[expandedRender.project.id] ?? [];
    if (projectRenders.length < 2) return;
    const currentIndex = projectRenders.findIndex((render) => render.id === expandedRender.render.id);
    const startIndex = currentIndex >= 0 ? currentIndex : 0;
    const nextIndex = (startIndex + direction + projectRenders.length) % projectRenders.length;
    setExpandedRender({ project: expandedRender.project, render: projectRenders[nextIndex] });
  }, [expandedRender, rendersByProject]);

  useEffect(() => {
    if (!expandedRender) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setExpandedRender(null);
        return;
      }
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      if (isTextEntryTarget(e.target)) return;
      e.preventDefault();
      stepExpandedRender(e.key === 'ArrowRight' ? 1 : -1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [expandedRender, stepExpandedRender]);

  return (
    <div className="pb-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-black uppercase text-[#b5652f]">Workspace</p>
          <h1 className="mt-1 text-4xl font-black uppercase leading-none tracking-normal text-[#151515] sm:text-5xl">
            Projects
          </h1>
          <p className="mt-3 text-sm font-semibold text-[#5c554d]">
            Manage site plans, saved generations, and visual planning studies.
          </p>
        </div>
        {!showCreate && (
          <button
            onClick={() => setShowCreate(true)}
            className="inline-flex items-center rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-5 py-3 text-sm font-black uppercase text-[#151515] shadow-[5px_5px_0_0_#151515] transition hover:bg-[#d7ff66] active:translate-x-0.5 active:translate-y-0.5"
          >
            <Plus size={16} className="mr-2" />
            New Project
          </button>
        )}
      </div>

      {showCreate && (
        <div className="mt-6 rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[8px_8px_0_0_#151515] sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-black uppercase">Create New Project</h2>
            <button onClick={handleCancel} className="rounded-full border-2 border-[#151515] bg-white p-1 text-[#151515] hover:bg-[#c9ff3d]">
              <X size={20} />
            </button>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-primary-950/70 mb-1">Project Name *</label>
              <input
                type="text"
                placeholder="e.g., Riverside Development Phase 1"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
                className="input-base w-full"
                autoFocus
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-950/70 mb-1">Description</label>
              <textarea
                placeholder="Brief description of the development project..."
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                rows={2}
                className="input-base w-full"
              />
            </div>
            <div className="relative" ref={suggestionsRef}>
              <label className="block text-sm font-medium text-primary-950/70 mb-1">Location</label>
              <div className="relative">
                <MapPin size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/30" />
                <input
                  type="text"
                  placeholder={MAPBOX_TOKEN ? 'Search for an address...' : 'Set VITE_MAPBOX_TOKEN to enable'}
                  value={addressQuery}
                  disabled={!MAPBOX_TOKEN}
                  onChange={(e) => {
                    setAddressQuery(e.target.value);
                    setSelectedLocation(null);
                    geocodeAddress(e.target.value);
                  }}
                  onFocus={() => addressSuggestions.length > 0 && setShowSuggestions(true)}
                  onKeyDown={handleAddressKeyDown}
                  className="input-base w-full pl-9 disabled:bg-primary-950/[0.02] disabled:text-primary-950/30"
                />
              </div>
              {showSuggestions && addressSuggestions.length > 0 && (
                <div className="absolute z-10 mt-1 w-full rounded-lg border border-primary-950/[0.08] bg-white shadow-elevated max-h-48 overflow-y-auto animate-fade-in">
                  {addressSuggestions.map((s, i) => (
                    <button
                      key={i}
                      type="button"
                      className={`w-full text-left px-3 py-2 text-sm border-b border-primary-950/[0.04] last:border-0 ${
                        i === highlightedIndex
                          ? 'bg-primary-950/[0.06] text-primary-400'
                          : 'text-primary-950/70 hover:bg-primary-950/[0.04] hover:text-primary-400'
                      }`}
                      onClick={() => selectSuggestion(s)}
                    >
                      <MapPin size={12} className="inline mr-2 text-primary-950/30" />
                      {s.place_name}
                    </button>
                  ))}
                </div>
              )}
              {selectedLocation && (
                <p className="mt-1 text-xs text-emerald-400">
                  {selectedLocation.latitude.toFixed(5)}, {selectedLocation.longitude.toFixed(5)}
                </p>
              )}
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex gap-3">
              <button
                onClick={handleCreate}
                disabled={createMutation.isPending}
                className="inline-flex items-center rounded-full border-2 border-[#151515] bg-[#151515] px-5 py-2.5 text-sm font-black text-white shadow-[4px_4px_0_0_#151515] disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Project'}
              </button>
              <button
                onClick={handleCancel}
                className="inline-flex items-center rounded-full border-2 border-[#151515] bg-white px-5 py-2.5 text-sm font-black text-[#151515] hover:bg-[#c9ff3d]"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="mt-8 text-center text-primary-950/40">Loading projects...</div>
      ) : !projects?.length && !showCreate ? (
        <div className="mx-auto mt-16 max-w-md rounded-lg border-2 border-[#151515] bg-white p-8 text-center shadow-[8px_8px_0_0_#151515]">
          <FolderOpen className="mx-auto h-12 w-12 text-[#151515]" />
          <h3 className="mt-4 text-2xl font-black uppercase text-[#151515]">No projects yet</h3>
          <p className="mt-2 text-sm font-semibold text-[#5c554d]">
            Create your first project to start visualizing developments in 3D.
          </p>
          <button
            onClick={() => setShowCreate(true)}
            className="mt-6 inline-flex items-center rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-5 py-3 text-sm font-black uppercase text-[#151515] shadow-[5px_5px_0_0_#151515] transition hover:bg-[#d7ff66]"
          >
            <Plus size={16} className="mr-2" />
            Create Project
          </button>
        </div>
      ) : (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project: Project) => {
            const projectRenders = rendersByProject[project.id] ?? [];
            const previewRenders = projectRenders.slice(0, 4);
            return (
              <div
                key={project.id}
                className="group flex flex-col rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[6px_6px_0_0_#151515] transition-transform hover:-translate-y-0.5 sm:p-6"
              >
                <Link to={`/projects/${project.id}`} className="block flex-1">
                  <div className="flex items-start justify-between">
                    <h3 className="font-black text-[#151515] group-hover:text-[#0aa6a6]">{project.name}</h3>
                    <span className={`badge ${statusColors[project.status]}`}>{project.status}</span>
                  </div>
                  {project.description && <p className="mt-2 line-clamp-2 text-sm font-semibold text-[#5c554d]">{project.description}</p>}
                  {isAdmin && project.owner_email && (
                    <div className="mt-1.5 truncate text-xs font-bold text-[#0aa6a6]">{project.owner_email}</div>
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

                {rendersLoading ? (
                  <div className="mt-4 border-t border-primary-950/[0.06] pt-3">
                    <div className="grid grid-cols-4 gap-1.5">
                      {[0, 1, 2, 3].map((slot) => (
                        <div key={slot} className="aspect-video animate-pulse rounded-lg bg-primary-950/[0.05]" />
                      ))}
                    </div>
                  </div>
                ) : projectRenders.length > 0 ? (
                  <div className="mt-4 border-t border-primary-950/[0.06] pt-3">
                    <div className="mb-2 flex items-center justify-between text-[11px] font-medium text-primary-950/45">
                      <span className="flex items-center gap-1">
                        <Images size={12} />
                        Saved renders
                      </span>
                      <span>{projectRenders.length}</span>
                    </div>
                    <div className="grid grid-cols-4 gap-1.5">
                      {previewRenders.map((render, index) => {
                        const hiddenCount = projectRenders.length - 4;
                        return (
                          <button
                            key={render.id}
                            type="button"
                            onClick={() => setExpandedRender({ project, render })}
                            className="group/render relative aspect-video overflow-hidden rounded-lg border border-primary-950/[0.08] bg-primary-950/[0.03] transition hover:border-coral-400/60 hover:shadow-sm"
                            title="Open saved render"
                          >
                            <img
                              src={resolveApiFileUrl(render.image_url)}
                              alt={render.prompt || `${project.name} saved render`}
                              className="h-full w-full object-cover transition group-hover/render:scale-105"
                            />
                            {index === 3 && hiddenCount > 0 && (
                              <span className="absolute inset-0 flex items-center justify-center bg-black/55 text-xs font-semibold text-white">
                                +{hiddenCount}
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      )}

      {expandedRender && createPortal(
        <div
          className="fixed inset-0 z-[250] flex cursor-zoom-out items-center justify-center bg-black/85 p-6 backdrop-blur-sm"
          onClick={() => setExpandedRender(null)}
          role="dialog"
          aria-label="Saved project render"
        >
          <div className="relative max-h-[90vh] max-w-[90vw] cursor-default" onClick={(e) => e.stopPropagation()}>
            <img
              src={resolveApiFileUrl(expandedRender.render.image_url)}
              alt={expandedRender.render.prompt || `${expandedRender.project.name} saved render`}
              className="max-h-[85vh] max-w-full rounded-xl object-contain shadow-2xl"
            />
            <div className="absolute inset-x-0 bottom-0 rounded-b-xl bg-gradient-to-t from-black/85 to-transparent px-5 py-4">
              <p className="text-sm font-semibold text-white">{expandedRender.project.name}</p>
              {expandedRender.render.prompt && (
                <p className="mt-1 line-clamp-2 text-xs text-white/75">{expandedRender.render.prompt}</p>
              )}
              <p className="mt-1 text-[11px] text-white/50">
                {new Date(expandedRender.render.created_at).toLocaleDateString()}
                {expandedRender.render.style && ` - ${expandedRender.render.style}`}
              </p>
            </div>
            <div className="absolute right-3 top-3 flex gap-2">
              <a
                href={resolveApiFileUrl(expandedRender.render.image_url)}
                download={`render-${expandedRender.render.id}.png`}
                className="rounded-full bg-black/60 p-2 text-white/80 transition hover:bg-black/80 hover:text-white"
                title="Download"
              >
                <Download size={18} />
              </a>
              <button
                onClick={() => setExpandedRender(null)}
                className="rounded-full bg-black/60 p-2 text-white/80 transition hover:bg-black/80 hover:text-white"
                title="Close"
              >
                <X size={18} />
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </div>
  );
}

