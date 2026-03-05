import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { X } from 'lucide-react';
import { buildingsApi } from '@/services/api';
import type { CreateBuildingRequest } from '@/types';

interface AddBuildingModalProps {
  projectId: string;
  projectLocation?: { latitude?: number; longitude?: number } | null;
  onClose: () => void;
}

export function AddBuildingModal({ projectId, projectLocation, onClose }: AddBuildingModalProps) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CreateBuildingRequest>({
    name: '',
    height_meters: 10,
    floor_count: 3,
    floor_height_meters: 3,
    roof_type: 'flat',
  });

  const mutation = useMutation({
    mutationFn: (data: CreateBuildingRequest) => buildingsApi.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      toast.success('Building added!');
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = { ...form };
    // Create a default footprint at the project location so the building appears on the map
    if (!data.footprint_coordinates && projectLocation?.latitude && projectLocation?.longitude) {
      const lat = projectLocation.latitude;
      const lng = projectLocation.longitude;
      const h = data.height_meters || 10;
      const sideMeters = Math.max(h * 0.8, 10);
      const metersPerDegLon = 111320 * Math.cos((lat * Math.PI) / 180);
      const metersPerDegLat = 111320;
      const halfW = (sideMeters / 2) / metersPerDegLon;
      const halfH = (sideMeters / 2) / metersPerDegLat;
      data.footprint_coordinates = [
        [lng - halfW, lat - halfH],
        [lng + halfW, lat - halfH],
        [lng + halfW, lat + halfH],
        [lng - halfW, lat + halfH],
      ];
    }
    mutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-primary-950/60 backdrop-blur-sm sm:items-center" onClick={onClose}>
      <div className="w-full max-w-md rounded-t-2xl bg-white/95 backdrop-blur-xl border border-primary-950/[0.08] p-5 shadow-elevated animate-slide-up sm:rounded-2xl sm:p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-primary-950">Add Building</h2>
          <button onClick={onClose} className="text-primary-950/50 hover:text-primary-950/60">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-primary-950/60">Building Name</label>
            <input
              type="text"
              value={form.name || ''}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="input-base mt-1 w-full"
              placeholder="e.g. Tower A"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-primary-950/60">Height (m)</label>
              <input
                type="number"
                value={form.height_meters || ''}
                onChange={(e) => setForm({ ...form, height_meters: parseFloat(e.target.value) || undefined })}
                className="input-base mt-1 w-full"
                min={1}
                step={0.5}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-950/60">Floors</label>
              <input
                type="number"
                value={form.floor_count || ''}
                onChange={(e) => setForm({ ...form, floor_count: parseInt(e.target.value) || undefined })}
                className="input-base mt-1 w-full"
                min={1}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-primary-950/60">Floor Height (m)</label>
              <input
                type="number"
                value={form.floor_height_meters || ''}
                onChange={(e) => setForm({ ...form, floor_height_meters: parseFloat(e.target.value) || undefined })}
                className="input-base mt-1 w-full"
                min={2}
                max={10}
                step={0.1}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-950/60">Roof Type</label>
              <select
                value={form.roof_type || 'flat'}
                onChange={(e) => setForm({ ...form, roof_type: e.target.value })}
                className="input-base mt-1 w-full"
              >
                <option value="flat">Flat</option>
                <option value="gabled">Gabled</option>
                <option value="hipped">Hipped</option>
                <option value="mansard">Mansard</option>
              </select>
            </div>
          </div>

          {mutation.isError && (
            <p className="text-sm text-red-600">Failed to create building. Please try again.</p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="rounded-lg px-4 py-2 text-sm font-medium text-primary-950/60 hover:bg-primary-950/[0.04]">
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn-primary"
            >
              {mutation.isPending ? 'Creating...' : 'Add Building'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
