import { useCallback, useEffect, useRef, useState, type FormEvent as ReactFormEvent } from 'react';
import { MapPin, X } from 'lucide-react';
import type { Location, Project, UpdateProjectRequest } from '@/types';
import { getApiErrorMessage } from '@/services/api';
import { geocodingApi, type GeocodeSuggestion } from '@/services/geocoding';

interface ProjectEditModalProps {
  project: Project;
  isSaving: boolean;
  onClose: () => void;
  onSave: (updates: UpdateProjectRequest) => void;
}

export function ProjectEditModal({ project, isSaving, onClose, onSave }: ProjectEditModalProps) {
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description ?? '');
  const [addressQuery, setAddressQuery] = useState(project.location?.address ?? '');
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [suggestions, setSuggestions] = useState<GeocodeSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isResolvingLocation, setIsResolvingLocation] = useState(false);
  const [error, setError] = useState('');
  const geocodeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setName(project.name);
    setDescription(project.description ?? '');
    setAddressQuery(project.location?.address ?? '');
    setSelectedLocation(null);
    setSuggestions([]);
    setError('');
  }, [project]);

  useEffect(() => {
    return () => {
      if (geocodeTimerRef.current) clearTimeout(geocodeTimerRef.current);
    };
  }, []);

  const geocodeAddress = useCallback((query: string) => {
    if (geocodeTimerRef.current) clearTimeout(geocodeTimerRef.current);
    if (query.trim().length < 3) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    geocodeTimerRef.current = setTimeout(async () => {
      try {
        const nextSuggestions = await geocodingApi.autocomplete(query.trim());
        setSuggestions(nextSuggestions);
        setShowSuggestions(nextSuggestions.length > 0);
        setError('');
      } catch (err) {
        setSuggestions([]);
        setShowSuggestions(false);
        setError(getApiErrorMessage(err, 'Address search is temporarily unavailable.'));
      }
    }, 350);
  }, []);

  const geocodeFirstResult = useCallback(async (query: string): Promise<Location | null> => {
    if (query.trim().length < 3) return null;
    try {
      const [suggestion] = await geocodingApi.autocomplete(query.trim());
      return suggestion ? await geocodingApi.resolve(suggestion.id) : null;
    } catch {
      return null;
    }
  }, []);

  const selectSuggestion = async (suggestion: GeocodeSuggestion) => {
    setAddressQuery(suggestion.place_name);
    setShowSuggestions(false);
    setIsResolvingLocation(true);
    try {
      const resolved = await geocodingApi.resolve(suggestion.id);
      setSelectedLocation(resolved);
      setAddressQuery(resolved.address ?? suggestion.place_name);
      setError('');
    } catch (err) {
      setSelectedLocation(null);
      setError(getApiErrorMessage(err, 'The selected address could not be located.'));
    } finally {
      setIsResolvingLocation(false);
    }
  };

  const handleSubmit = async (event: ReactFormEvent) => {
    event.preventDefault();
    const trimmedName = name.trim();
    const trimmedDescription = description.trim();
    const trimmedAddress = addressQuery.trim();

    if (!trimmedName) {
      setError('Project name is required');
      return;
    }

    let location: Location | null | undefined;
    if (selectedLocation) {
      location = selectedLocation;
    } else if (trimmedAddress) {
      const geocodedLocation = await geocodeFirstResult(trimmedAddress);
      if (!geocodedLocation) {
        setError('Select an address suggestion so the map location can be saved.');
        return;
      }
      location = geocodedLocation;
      setAddressQuery(geocodedLocation.address ?? trimmedAddress);
    } else if (project.location) {
      location = {
        latitude: project.location.latitude,
        longitude: project.location.longitude,
        address: trimmedAddress || null,
      };
    }

    setError('');
    onSave({
      name: trimmedName,
      description: trimmedDescription || null,
      ...(location !== undefined ? { location } : {}),
    });
  };

  return (
    <div className="fixed inset-0 z-[260] flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-xl rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[8px_8px_0_0_#151515] sm:p-6"
      >
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-black uppercase text-[#b5652f]">Project Info</p>
            <h2 className="mt-1 text-xl font-black uppercase text-[#151515]">Edit Project</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border-2 border-[#151515] bg-white p-1.5 text-[#151515] hover:bg-[#c9ff3d]"
            aria-label="Close edit project"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-primary-950/70">Project Name *</label>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="input-base w-full"
              autoFocus
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-primary-950/70">Description</label>
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={3}
              className="input-base w-full"
              placeholder="Brief description of the development project..."
            />
          </div>

          <div className="relative">
            <label className="mb-1 block text-sm font-medium text-primary-950/70">Address</label>
            <div className="relative">
              <MapPin size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-primary-950/30" />
              <input
                type="text"
                value={addressQuery}
                onChange={(event) => {
                  setAddressQuery(event.target.value);
                  setSelectedLocation(null);
                  geocodeAddress(event.target.value);
                }}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                className="input-base w-full pl-9"
                placeholder="Search for an address..."
              />
            </div>
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-primary-950/[0.08] bg-white shadow-elevated">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion.id}
                    type="button"
                    onClick={() => void selectSuggestion(suggestion)}
                    className="w-full border-b border-primary-950/[0.04] px-3 py-2 text-left text-sm text-primary-950/70 last:border-0 hover:bg-primary-950/[0.04] hover:text-primary-400"
                  >
                    <MapPin size={12} className="mr-2 inline text-primary-950/30" />
                    {suggestion.place_name}
                  </button>
                ))}
              </div>
            )}
            {selectedLocation && (
              <p className="mt-1 text-xs text-emerald-600">
                {selectedLocation.latitude.toFixed(5)}, {selectedLocation.longitude.toFixed(5)}
              </p>
            )}
          </div>

          {error && <p className="text-sm font-semibold text-red-600">{error}</p>}
        </div>

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center justify-center rounded-full border-2 border-[#151515] bg-white px-5 py-2.5 text-sm font-black text-[#151515] hover:bg-[#c9ff3d]"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSaving || isResolvingLocation}
            className="inline-flex items-center justify-center rounded-full border-2 border-[#151515] bg-[#151515] px-5 py-2.5 text-sm font-black text-white shadow-[4px_4px_0_0_#151515] disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : isResolvingLocation ? 'Locating...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
}
