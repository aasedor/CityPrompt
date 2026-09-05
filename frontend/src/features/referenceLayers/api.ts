import { api } from '@/services/api';

export type ReferencePosition = [number, number] | [number, number, number];
export type ReferenceGeometry =
  | { type: 'Point'; coordinates: ReferencePosition }
  | { type: 'MultiPoint' | 'LineString'; coordinates: ReferencePosition[] }
  | { type: 'MultiLineString' | 'Polygon'; coordinates: ReferencePosition[][] }
  | { type: 'MultiPolygon'; coordinates: ReferencePosition[][][] }
  | { type: 'GeometryCollection'; geometries: ReferenceGeometry[] };

export interface ReferenceFeature {
  type: 'Feature';
  id?: string | number;
  geometry: ReferenceGeometry;
  properties: Record<string, unknown>;
}

export interface ReferenceLayer {
  id: string;
  project_id: string;
  name: string;
  source_filename: string;
  source_crs: string;
  source_url: string | null;
  description: string | null;
  kind: 'reference' | 'zoning';
  feature_collection: { type: 'FeatureCollection'; features: ReferenceFeature[] };
  feature_count: number;
  bounds: [number, number, number, number];
  warnings: string[];
  color: string;
  opacity: number;
  created_at: string;
}

export const referenceLayerQueryKey = (projectId: string | undefined) => ['reference-layers', projectId] as const;

export const referenceLayersApi = {
  list: async (projectId: string): Promise<{ layers: ReferenceLayer[]; can_edit: boolean }> => {
    const { data } = await api.get(`/api/v1/reference-layers/projects/${projectId}`);
    return data;
  },
  import: async (projectId: string, file: File, metadata: {
    name: string; kind: 'reference' | 'zoning'; source_url?: string; description?: string;
  }): Promise<ReferenceLayer> => {
    const body = new FormData();
    body.append('file', file);
    Object.entries(metadata).forEach(([key, value]) => { if (value) body.append(key, value); });
    const { data } = await api.post(`/api/v1/reference-layers/projects/${projectId}/import`, body, {
      timeout: 120_000,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
  remove: async (layerId: string): Promise<void> => {
    await api.delete(`/api/v1/reference-layers/${layerId}`);
  },
};
