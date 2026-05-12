import axios from 'axios';
import type {
  Project,
  Building,
  Document,
  ProcessingStatus,
  CreateProjectRequest,
  UpdateProjectRequest,
  CreateBuildingRequest,
  SiteZone,
  SiteZoneType,
  SiteZoneProperties,
  GenerationStatus,
  AITemplate,
  ArchitecturalStyle,
  RenderPreview,
  GenerationEngine,
  LayoutPreviewResponse,
  LayoutOption,
  OSMContext,
  LockedLayers,
  BoundaryAnalysisResponse,
  ModelLibraryEntry,
  MasterPlan2DGenerateRequest,
  MasterPlan2DGenerateResponse,
  MasterPlan2DOption,
  MasterPlan2DSelectResponse,
  MasterPlan2DExportResponse,
  MasterPlan3DGenerateRequest,
  MasterPlan3DGenerateResponse,
  SiteMassingResponse,
  SavedRender,
  ZoneHistoryListResponse,
  ZoneHistoryEntry,
  ZoneSnapshotRestoreResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

/**
 * Resolve a relative API URL (e.g. /api/v1/files/...) to an absolute URL
 * pointing at the backend. In dev the Vite proxy handles /api/ routes, but
 * in production the frontend and backend are on different domains.
 */
export function resolveApiFileUrl(url: string): string {
  if (!url) return url;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/api/') && API_BASE_URL && API_BASE_URL !== 'http://localhost:8000') {
    return `${API_BASE_URL}${url}`;
  }
  return url;
}

function formatApiDetail(detail: unknown): string | null {
  if (typeof detail === 'string') {
    const trimmed = detail.trim();
    return trimmed || null;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => formatApiDetail(item))
      .filter((item): item is string => Boolean(item));
    return parts.length > 0 ? parts.join('; ') : null;
  }
  if (detail && typeof detail === 'object') {
    const record = detail as Record<string, unknown>;
    const location = Array.isArray(record.loc)
      ? record.loc.map((part) => String(part)).join(' > ')
      : null;
    const message = typeof record.msg === 'string'
      ? record.msg.trim()
      : typeof record.message === 'string'
        ? record.message.trim()
        : null;
    if (location && message) return `${location}: ${message}`;
    if (message) return message;
  }
  return null;
}

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong'): string {
  const response = (error as any)?.response?.data;
  return (
    formatApiDetail(response?.detail)
    || formatApiDetail(response?.message)
    || formatApiDetail((error as any)?.message)
    || fallback
  );
}
// Request interceptor for auth token
/** Set by the undo/redo store during system actions to skip history recording. */
let _skipHistoryFlag = false;
export function setSkipHistory(v: boolean) { _skipHistoryFlag = v; }

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (_skipHistoryFlag) {
    config.headers['X-Skip-History'] = '1';
  }
  return config;
});

// Response interceptor for automatic token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/')
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await api.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// =============================================================================
// Auth
// =============================================================================

export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  render_credits: number;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
}

export const authApi = {
  register: async (email: string, password: string, fullName?: string): Promise<AuthUser> => {
    const { data } = await api.post('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return data;
  },

  login: async (email: string, password: string): Promise<AuthTokens> => {
    const { data } = await api.post('/api/v1/auth/login', { email, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  me: async (): Promise<AuthUser> => {
    const { data } = await api.get('/api/v1/auth/me');
    return data;
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<{ message: string }> => {
    const { data } = await api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return data;
  },

  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const { data } = await api.post('/api/v1/auth/forgot-password', { email });
    return data;
  },

  resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
    const { data } = await api.post('/api/v1/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return data;
  },
};

// =============================================================================
// Projects
// =============================================================================

export const projectsApi = {
  list: async (skip = 0, limit?: number): Promise<Project[]> => {
    const params: { skip: number; limit?: number } = { skip };
    if (limit !== undefined) params.limit = limit;
    const { data } = await api.get('/api/v1/projects/', { params });
    return data;
  },

  get: async (id: string): Promise<Project> => {
    const { data } = await api.get(`/api/v1/projects/${id}`);
    return data;
  },

  create: async (project: CreateProjectRequest): Promise<Project> => {
    const { data } = await api.post('/api/v1/projects/', project);
    return data;
  },

  update: async (id: string, project: UpdateProjectRequest): Promise<Project> => {
    const { data } = await api.put(`/api/v1/projects/${id}`, project);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/projects/${id}`);
  },
};

// =============================================================================
// Documents
// =============================================================================

export const documentsApi = {
  upload: async (projectId: string, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post(
      `/api/v1/documents/projects/${projectId}/upload`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return data;
  },

  triggerProcessing: async (documentId: string): Promise<ProcessingStatus> => {
    const { data } = await api.post(`/api/v1/documents/${documentId}/process`);
    return data;
  },

  getStatus: async (jobId: string): Promise<ProcessingStatus> => {
    const { data } = await api.get(`/api/v1/documents/status/${jobId}`);
    return data;
  },

  delete: async (documentId: string): Promise<void> => {
    await api.delete(`/api/v1/documents/${documentId}`);
  },
};

// =============================================================================
// Buildings
// =============================================================================

export const buildingsApi = {
  list: async (projectId: string): Promise<Building[]> => {
    const { data } = await api.get(`/api/v1/buildings/projects/${projectId}/buildings`);
    return data;
  },

  create: async (projectId: string, building: CreateBuildingRequest): Promise<Building> => {
    const { data } = await api.post(`/api/v1/buildings/projects/${projectId}/buildings`, building);
    return data;
  },

  get: async (id: string): Promise<Building> => {
    const { data } = await api.get(`/api/v1/buildings/${id}`);
    return data;
  },

  update: async (id: string, building: Partial<CreateBuildingRequest>): Promise<Building> => {
    const { data } = await api.put(`/api/v1/buildings/${id}`, building);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/buildings/${id}`);
  },

  getModelUrl: async (id: string): Promise<string> => {
    const { data } = await api.get(`/api/v1/buildings/${id}/model`);
    return data.model_url;
  },

  generate: async (
    id: string,
    prompt: string,
    artStyle = 'realistic',
    negativePrompt?: string,
    style?: string,
    engine?: string,
  ): Promise<GenerationStatus> => {
    const { data } = await api.post(`/api/v1/buildings/${id}/generate`, {
      prompt,
      art_style: artStyle,
      negative_prompt: negativePrompt,
      style,
      engine,
    });
    return data;
  },

  generateFromImage: async (id: string, imageUrl: string): Promise<GenerationStatus> => {
    const { data } = await api.post(`/api/v1/buildings/${id}/generate-from-image`, {
      image_url: imageUrl,
    });
    return data;
  },

  getGenerationStatus: async (id: string): Promise<GenerationStatus> => {
    const { data } = await api.get(`/api/v1/buildings/${id}/generation-status`);
    return data;
  },

  cancelGeneration: async (id: string): Promise<void> => {
    await api.post(`/api/v1/buildings/${id}/cancel-generation`);
  },

  batchCancelGeneration: async (buildingIds: string[]): Promise<void> => {
    await api.post('/api/v1/buildings/batch-cancel-generation', { building_ids: buildingIds });
  },

  getTemplates: async (): Promise<AITemplate[]> => {
    const { data } = await api.get('/api/v1/buildings/ai/templates');
    return data;
  },

  getStyles: async (): Promise<ArchitecturalStyle[]> => {
    const { data } = await api.get('/api/v1/buildings/ai/styles');
    return data;
  },

  getEngines: async (): Promise<GenerationEngine[]> => {
    const { data } = await api.get('/api/v1/buildings/ai/engines');
    return data;
  },

  generatePreview: async (
    id: string,
    prompt: string,
    style?: string,
    sourceType = 'text',
    sourceImageUrl?: string,
  ): Promise<RenderPreview> => {
    const { data } = await api.post(`/api/v1/buildings/${id}/render-preview`, {
      prompt,
      style,
      source_type: sourceType,
      source_image_url: sourceImageUrl,
    });
    return data;
  },

  getRenderPreviews: async (id: string): Promise<RenderPreview[]> => {
    const { data } = await api.get(`/api/v1/buildings/${id}/render-previews`);
    return data;
  },
};

// =============================================================================
// Annotations
// =============================================================================

export interface Annotation {
  id: string;
  project_id: string;
  building_id?: string;
  author_id: string;
  text: string;
  position_x: number;
  position_y: number;
  position_z: number;
  resolved: boolean;
  created_at: string;
}

export const annotationsApi = {
  list: async (projectId: string, resolved?: boolean): Promise<Annotation[]> => {
    const params = resolved !== undefined ? `?resolved=${resolved}` : '';
    const { data } = await api.get(`/api/v1/annotations/projects/${projectId}/annotations${params}`);
    return data;
  },

  create: async (projectId: string, annotation: {
    text: string;
    building_id?: string;
    position_x: number;
    position_y: number;
    position_z: number;
  }): Promise<Annotation> => {
    const { data } = await api.post(`/api/v1/annotations/projects/${projectId}/annotations`, annotation);
    return data;
  },

  update: async (annotationId: string, update: { text?: string; resolved?: boolean }): Promise<Annotation> => {
    const { data } = await api.put(`/api/v1/annotations/${annotationId}`, update);
    return data;
  },

  delete: async (annotationId: string): Promise<void> => {
    await api.delete(`/api/v1/annotations/${annotationId}`);
  },
};

// =============================================================================
// Context (OSM)
// =============================================================================

export interface ContextBuilding {
  osm_id: number;
  name?: string;
  height: number;
  levels?: number;
  building_type: string;
  footprint: number[][]; // [[lon, lat], ...]
}

export interface ContextRoad {
  osm_id: number;
  name?: string;
  highway_type: string;
  width: number;
  coords: number[][]; // [[lon, lat], ...]
}

export const contextApi = {
  getBuildings: async (lat: number, lon: number, radius = 500): Promise<ContextBuilding[]> => {
    const { data } = await api.get(
      `/api/v1/context/buildings?lat=${lat}&lon=${lon}&radius=${radius}`
    );
    return data.buildings;
  },
  getRoads: async (lat: number, lon: number, radius = 500): Promise<ContextRoad[]> => {
    const { data } = await api.get(
      `/api/v1/context/roads?lat=${lat}&lon=${lon}&radius=${radius}`
    );
    return data.roads;
  },
};

// =============================================================================
// Sharing
// =============================================================================

export interface ProjectShareInfo {
  id: string;
  project_id: string;
  user_id?: string;
  email?: string;
  permission: string;
  is_public_link: boolean;
  invite_token?: string;
  created_at: string;
}

export interface PublicLinkInfo {
  token: string;
  url: string;
}

export const sharesApi = {
  share: async (projectId: string, email: string, permission = 'viewer'): Promise<ProjectShareInfo> => {
    const { data } = await api.post(`/api/v1/shares/projects/${projectId}/shares`, {
      email,
      permission,
    });
    return data;
  },

  list: async (projectId: string): Promise<ProjectShareInfo[]> => {
    const { data } = await api.get(`/api/v1/shares/projects/${projectId}/shares`);
    return data;
  },

  revoke: async (projectId: string, shareId: string): Promise<void> => {
    await api.delete(`/api/v1/shares/projects/${projectId}/shares/${shareId}`);
  },

  createPublicLink: async (projectId: string): Promise<PublicLinkInfo> => {
    const { data } = await api.post(`/api/v1/shares/projects/${projectId}/shares/public-link`);
    return data;
  },

  revokePublicLink: async (projectId: string): Promise<void> => {
    await api.delete(`/api/v1/shares/projects/${projectId}/shares/public-link`);
  },

  getSharedProject: async (token: string): Promise<Project> => {
    const { data } = await api.get(`/api/v1/shares/shared/${token}`);
    return data;
  },

  listSharedWithMe: async (): Promise<ProjectShareInfo[]> => {
    const { data } = await api.get('/api/v1/shares/shared-with-me');
    return data;
  },
};

// =============================================================================
// Activity Feed
// =============================================================================

export interface ActivityEntry {
  id: string;
  action: string;
  details?: Record<string, unknown>;
  user_email?: string;
  user_name?: string;
  created_at: string;
}

export const activityApi = {
  list: async (projectId: string, limit = 20): Promise<ActivityEntry[]> => {
    const { data } = await api.get(`/api/v1/activity/projects/${projectId}/activity?limit=${limit}`);
    return data;
  },
};

// =============================================================================
// Site Zones
// =============================================================================

export const siteZonesApi = {
  list: async (projectId: string): Promise<SiteZone[]> => {
    const { data } = await api.get(`/api/v1/site-zones/projects/${projectId}/zones`);
    return data;
  },

  create: async (projectId: string, zone: {
    name?: string;
    zone_type: SiteZoneType;
    coordinates: number[][];
    color: string;
    properties?: SiteZoneProperties;
    sort_order?: number;
  }): Promise<SiteZone> => {
    const { data } = await api.post(`/api/v1/site-zones/projects/${projectId}/zones`, zone);
    return data;
  },

  update: async (zoneId: string, update: {
    name?: string;
    zone_type?: SiteZoneType;
    coordinates?: number[][];
    color?: string;
    properties?: SiteZoneProperties;
    sort_order?: number;
  }): Promise<SiteZone> => {
    const { data } = await api.put(`/api/v1/site-zones/${zoneId}`, update);
    return data;
  },

  delete: async (zoneId: string): Promise<void> => {
    await api.delete(`/api/v1/site-zones/${zoneId}`);
  },

  createBuildingFromZone: async (zoneId: string): Promise<Building> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/create-building`);
    return data;
  },

  previewLayouts: async (zoneId: string): Promise<LayoutPreviewResponse> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/preview-layouts`, {}, { timeout: 60000 });
    return data;
  },

  applyLayout: async (zoneId: string, optionIndex: number, layout: LayoutOption): Promise<Building> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/apply-layout`, {
      option_index: optionIndex,
      layout: {
        buildings: layout.buildings,
        roads: layout.roads,
        green_spaces: layout.green_spaces,
        layout_strategy: layout.layout_strategy,
        reasoning: layout.reasoning,
        density_achieved: layout.density_achieved,
      },
    });
    return data;
  },

  generateAll: async (projectId: string): Promise<{ total_zones: number; buildings_created: number; generations_queued: number; queued_buildings?: { id: string; name: string }[] }> => {
    const { data } = await api.post(`/api/v1/site-zones/projects/${projectId}/generate-all`);
    return data;
  },

  fetchContext: async (zoneId: string): Promise<OSMContext> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/fetch-context`, {}, { timeout: 35000 });
    return data;
  },

  regenerateLayout: async (zoneId: string, locked: LockedLayers): Promise<LayoutPreviewResponse> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/regenerate-layout`, {
      locked_roads: locked.roads,
      locked_buildings: locked.buildings,
      locked_green_spaces: locked.green_spaces,
    }, { timeout: 60000 });
    return data;
  },

  renderLayoutPreview: async (zoneId: string, layout: LayoutOption): Promise<{ image_url: string; zone_id: string }> => {
    const { data } = await api.post(`/api/v1/site-zones/${zoneId}/render-layout-preview`, { layout }, { timeout: 60000 });
    return { ...data, image_url: resolveApiFileUrl(data.image_url) };
  },

  renderSitePreview: async (
    boundaryZoneId: string,
    optionIndex: number,
    zoneLayouts: Record<string, LayoutOption>,
    mapScreenshots?: { satellite: string; withZones: string },
    zoneMeta?: Record<string, { color: string; name: string; zone_type: string }>,
  ): Promise<{ image_url: string; zone_id: string; option_index: number }> => {
    const { data } = await api.post(
      `/api/v1/site-zones/${boundaryZoneId}/render-site-preview`,
      {
        option_index: optionIndex,
        zone_layouts: zoneLayouts,
        ...(mapScreenshots && {
          map_screenshot_satellite: mapScreenshots.satellite,
          map_screenshot_with_zones: mapScreenshots.withZones,
        }),
        ...(zoneMeta && { zone_meta: zoneMeta }),
      },
      { timeout: 240000 },
    );
    return { ...data, image_url: resolveApiFileUrl(data.image_url) };
  },

  getBoundaryAnalysis: async (zoneId: string): Promise<BoundaryAnalysisResponse> => {
    const { data } = await api.get(`/api/v1/site-zones/${zoneId}/boundary-analysis`);
    return data;
  },

  saveLayout: async (zoneId: string, layout: LayoutOption): Promise<{ status: string; zone_id: string; buildings_updated: number; buildings_created: number; buildings_deleted: number }> => {
    const { data } = await api.put(`/api/v1/site-zones/${zoneId}/save-layout`, { layout });
    return data;
  },

  generateForBoundary: async (projectId: string, boundaryZoneId: string): Promise<{ total_zones: number; buildings_created: number; generations_queued: number; queued_buildings?: { id: string; name: string }[] }> => {
    const { data } = await api.post(`/api/v1/site-zones/projects/${projectId}/generate-all?boundary_zone_id=${boundaryZoneId}`);
    return data;
  },

  generateSiteMassing: async (projectId: string): Promise<SiteMassingResponse> => {
    const { data } = await api.post(`/api/v1/site-zones/projects/${projectId}/generate-site-massing`, {}, { timeout: 90000 });
    return data;
  },
};


// =============================================================================
// Zone History / Version Control
// =============================================================================

export const zoneHistoryApi = {
  list: async (projectId: string, params?: { limit?: number; offset?: number; zone_id?: string }): Promise<ZoneHistoryListResponse> => {
    const { data } = await api.get(`/api/v1/site-zones/projects/${projectId}/history`, { params });
    return data;
  },

  get: async (historyId: string): Promise<ZoneHistoryEntry> => {
    const { data } = await api.get(`/api/v1/site-zones/history/${historyId}`);
    return data;
  },

  revert: async (historyId: string): Promise<SiteZone> => {
    const { data } = await api.post(`/api/v1/site-zones/history/${historyId}/revert`);
    return data;
  },

  restoreSnapshot: async (
    projectId: string,
    zoneId: string,
    snapshot: SiteZone | null,
  ): Promise<ZoneSnapshotRestoreResponse> => {
    const { data } = await api.post(`/api/v1/site-zones/projects/${projectId}/restore-snapshot`, {
      zone_id: zoneId,
      snapshot,
    });
    return data;
  },
};


// =============================================================================
// 2D Master Plan Generator
// =============================================================================

function normalizeMasterPlan2DOption(option: MasterPlan2DOption): MasterPlan2DOption {
  return {
    ...option,
    preview_url: resolveApiFileUrl(option.preview_url),
    preview_png_url: resolveApiFileUrl(option.preview_png_url || option.preview_url),
    full_png_url: option.full_png_url ? resolveApiFileUrl(option.full_png_url) : undefined,
    svg_url: option.svg_url ? resolveApiFileUrl(option.svg_url) : undefined,
    plan_preview_png_url: option.plan_preview_png_url ? resolveApiFileUrl(option.plan_preview_png_url) : undefined,
    plan_full_png_url: option.plan_full_png_url ? resolveApiFileUrl(option.plan_full_png_url) : undefined,
    plan_svg_url: option.plan_svg_url ? resolveApiFileUrl(option.plan_svg_url) : undefined,
    debug_png_url: option.debug_png_url ? resolveApiFileUrl(option.debug_png_url) : undefined,
  };
}

function normalizeMasterPlan2DResponse(response: MasterPlan2DGenerateResponse): MasterPlan2DGenerateResponse {
  return {
    ...response,
    options: response.options.map(normalizeMasterPlan2DOption),
  };
}

export const masterPlan2DApi = {
  list: async (projectId: string): Promise<MasterPlan2DOption[]> => {
    const { data } = await api.get(`/api/v1/master-plan-2d/projects/${projectId}/options`);
    return data.map(normalizeMasterPlan2DOption);
  },

  generate: async (projectId: string, request: MasterPlan2DGenerateRequest): Promise<MasterPlan2DGenerateResponse> => {
    const { data } = await api.post(`/api/v1/master-plan-2d/projects/${projectId}/generate`, request, { timeout: 240000 });
    return normalizeMasterPlan2DResponse(data);
  },

  regenerate: async (projectId: string, request: MasterPlan2DGenerateRequest): Promise<MasterPlan2DGenerateResponse> => {
    const { data } = await api.post(`/api/v1/master-plan-2d/projects/${projectId}/regenerate`, request, { timeout: 240000 });
    return normalizeMasterPlan2DResponse(data);
  },

  select: async (optionId: string): Promise<MasterPlan2DSelectResponse> => {
    const { data } = await api.post(`/api/v1/master-plan-2d/options/${optionId}/select`);
    return data;
  },

  export: async (optionId: string, width = 4200): Promise<MasterPlan2DExportResponse> => {
    const { data } = await api.get(`/api/v1/master-plan-2d/options/${optionId}/export?width=${width}`);
    return {
      ...data,
      preview_png_url: data.preview_png_url ? resolveApiFileUrl(data.preview_png_url) : undefined,
      full_png_url: data.full_png_url ? resolveApiFileUrl(data.full_png_url) : undefined,
      svg_url: data.svg_url ? resolveApiFileUrl(data.svg_url) : undefined,
      plan_preview_png_url: data.plan_preview_png_url ? resolveApiFileUrl(data.plan_preview_png_url) : undefined,
      plan_full_png_url: data.plan_full_png_url ? resolveApiFileUrl(data.plan_full_png_url) : undefined,
      plan_svg_url: data.plan_svg_url ? resolveApiFileUrl(data.plan_svg_url) : undefined,
      debug_png_url: data.debug_png_url ? resolveApiFileUrl(data.debug_png_url) : undefined,
    };
  },

  generate3D: async (optionId: string, request: MasterPlan3DGenerateRequest): Promise<MasterPlan3DGenerateResponse> => {
    const { data } = await api.post(`/api/v1/master-plan-2d/options/${optionId}/generate-3d`, request, { timeout: 120000 });
    return data;
  },
};
// =============================================================================
// Admin
// =============================================================================

export interface AdminUser {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
  project_count: number;
  render_credits: number;
}

export interface AdminUserUpdate {
  role?: string;
  is_active?: boolean;
  full_name?: string;
}

export interface AdminDashboardStats {
  total_users: number;
  active_users: number;
  total_projects: number;
  total_buildings: number;
  total_documents: number;
  users_by_role: Record<string, number>;
  projects_by_status: Record<string, number>;
}

export interface AdminBuilding {
  id: string;
  name?: string;
  project_id: string;
  project_name: string;
  owner_email: string;
  generation_status?: string;
  generation_engine?: string;
  architectural_style?: string;
  model_url?: string;
  preview_url?: string;
  generation_prompt?: string;
  created_at: string;
}

export interface AdminProject {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  owner_email: string;
  owner_name?: string;
  building_count: number;
}

export interface RenderAuditLog {
  id: string;
  user_email: string;
  project_id?: string | null;
  project_name?: string | null;
  model: string;
  tokens_spent: number;
  input_image_url?: string;
  output_image_url?: string;
  input_thumbnail_url?: string;
  output_thumbnail_url?: string;
  prompt_preview?: string;
  created_at: string;
}

export interface RenderLogStats {
  total_renders: number;
  storage_bytes: number;
  storage_mb: number;
  storage_gb: number;
  storage_limit_gb: number;
  oldest_render?: string;
}

export const adminApi = {
  getStats: async (): Promise<AdminDashboardStats> => {
    const { data } = await api.get('/api/v1/admin/stats');
    return data;
  },

  listUsers: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    role?: string;
  }): Promise<AdminUser[]> => {
    const { data } = await api.get('/api/v1/admin/users', { params });
    return data;
  },

  updateUser: async (userId: string, update: AdminUserUpdate): Promise<AdminUser> => {
    const { data } = await api.put(`/api/v1/admin/users/${userId}`, update);
    return data;
  },

  deleteUser: async (userId: string): Promise<void> => {
    await api.delete(`/api/v1/admin/users/${userId}`);
  },

  updateTokens: async (userId: string, amount: number, mode: 'add' | 'set' = 'add'): Promise<AdminUser> => {
    const { data } = await api.post(`/api/v1/admin/users/${userId}/tokens`, { amount, mode });
    return data;
  },

  renderLogStats: async (): Promise<RenderLogStats> => {
    const { data } = await api.get('/api/v1/admin/render-logs/stats');
    return data;
  },

  listRenderLogs: async (params?: { skip?: number; limit?: number; user_email?: string }): Promise<RenderAuditLog[]> => {
    const { data } = await api.get('/api/v1/admin/render-logs', { params });
    return data;
  },

  deleteRenderLogs: async (ids: string[]): Promise<void> => {
    await api.delete('/api/v1/admin/render-logs', { params: { ids } });
  },

  listAllBuildings: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
    engine?: string;
  }): Promise<AdminBuilding[]> => {
    const { data } = await api.get('/api/v1/admin/buildings', { params });
    return data;
  },

  backfillThumbnails: async (): Promise<{ status: string; queued: number }> => {
    const { data } = await api.post('/api/v1/admin/buildings/backfill-thumbnails');
    return data;
  },

  uploadBuildingThumbnail: async (buildingId: string, imageBlob: Blob): Promise<{ status: string; preview_url: string }> => {
    const form = new FormData();
    form.append('file', imageBlob, 'thumbnail.png');
    const { data } = await api.post(`/api/v1/admin/buildings/${buildingId}/upload-thumbnail`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    });
    return data;
  },

  assignArchetype: async (
    buildingId: string,
    archetypeId: string,
    categoryId: string,
  ): Promise<{ status: string; building_id: string; archetype_id: string; category_id: string }> => {
    const { data } = await api.put(
      `/api/v1/admin/buildings/${buildingId}/assign-archetype`,
      null,
      { params: { archetype_id: archetypeId, category_id: categoryId } },
    );
    return data;
  },

  listAllProjects: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
  }): Promise<AdminProject[]> => {
    const { data } = await api.get('/api/v1/admin/projects', { params });
    return data;
  },
};

// =============================================================================
// Cofounder Analytics
// =============================================================================

export interface TimeSeriesPoint {
  period: string;
  count: number;
}

export interface TimeSeriesResponse {
  data: TimeSeriesPoint[];
  total_in_range: number;
  range: string;
  granularity: string;
}

export interface CreationTrendsResponse {
  projects: TimeSeriesPoint[];
  buildings: TimeSeriesPoint[];
  range: string;
  granularity: string;
}

export interface GenerationStatsResponse {
  by_engine: Record<string, Record<string, number>>;
  total_generations: number;
  success_rate: number;
  range: string;
}

export interface PlatformHealthResponse {
  api: {
    total_requests: number;
    uptime_seconds: number;
    avg_response_ms: number;
    p95_response_ms: number;
    recent_samples: number;
  };
  queue: {
    active: number;
    reserved: number;
    scheduled: number;
    available: boolean;
  };
  documents: Record<string, number>;
}

export interface TopUserEntry {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  project_count: number;
  building_count: number;
  document_count: number;
  total_activity: number;
}

export interface TopUsersResponse {
  users: TopUserEntry[];
  range: string;
}

export interface ProviderBalance {
  provider: string;
  balance?: number;
  frozen?: number;
  unit?: string;
  configured: boolean;
  error?: string;
}

export interface AnthropicTokenUsage {
  total_input_tokens: number;
  total_output_tokens: number;
  total_calls: number;
  configured: boolean;
}

export interface GeminiTokenUsage {
  total_input_tokens: number;
  total_output_tokens: number;
  total_calls: number;
  configured: boolean;
}

export interface ServiceStatus {
  provider: string;
  configured: boolean;
  description: string;
}

export interface ApiBalanceResponse {
  meshy: ProviderBalance;
  tripo: ProviderBalance;
  stability: ProviderBalance;
  anthropic: AnthropicTokenUsage;
  gemini: GeminiTokenUsage;
  services: ServiceStatus[];
}

export interface OperationBreakdown {
  operation: string;
  total_credits: number;
  call_count: number;
  success_rate: number;
}

export interface ApiUsageByProvider {
  provider: string;
  total_credits: number;
  total_calls: number;
  success_rate: number;
  by_operation: OperationBreakdown[];
}

export interface DailyUsage {
  date: string;
  provider: string;
  credits: number;
  calls: number;
}

export interface ApiUsageResponse {
  providers: ApiUsageByProvider[];
  daily: DailyUsage[];
  range: string;
}

export const analyticsApi = {
  getUserGrowth: async (range = '30d'): Promise<TimeSeriesResponse> => {
    const { data } = await api.get('/api/v1/analytics/user-growth', { params: { range } });
    return data;
  },

  getActiveUsers: async (range = '30d'): Promise<TimeSeriesResponse> => {
    const { data } = await api.get('/api/v1/analytics/active-users', { params: { range } });
    return data;
  },

  getCreationTrends: async (range = '30d'): Promise<CreationTrendsResponse> => {
    const { data } = await api.get('/api/v1/analytics/creation-trends', { params: { range } });
    return data;
  },

  getGenerationStats: async (range = '30d'): Promise<GenerationStatsResponse> => {
    const { data } = await api.get('/api/v1/analytics/generation-stats', { params: { range } });
    return data;
  },

  getPlatformHealth: async (): Promise<PlatformHealthResponse> => {
    const { data } = await api.get('/api/v1/analytics/platform-health');
    return data;
  },

  getTopUsers: async (range = '30d'): Promise<TopUsersResponse> => {
    const { data } = await api.get('/api/v1/analytics/top-users', { params: { range } });
    return data;
  },

  getApiBalances: async (): Promise<ApiBalanceResponse> => {
    const { data } = await api.get('/api/v1/analytics/api-balances');
    return data;
  },

  getApiUsage: async (range = '30d'): Promise<ApiUsageResponse> => {
    const { data } = await api.get('/api/v1/analytics/api-usage', { params: { range } });
    return data;
  },
};

// =============================================================================
// Platform Settings (Cofounder)
// =============================================================================

export interface PlatformSettings {
  layout_ai_provider: string;
  claude_configured: boolean;
  gemini_configured: boolean;
  openai_configured: boolean;
}

export const settingsApi = {
  getPlatformSettings: async (): Promise<PlatformSettings> => {
    const { data } = await api.get('/api/v1/settings/platform-settings');
    return data;
  },

  updatePlatformSettings: async (update: { layout_ai_provider?: string }): Promise<PlatformSettings> => {
    const { data } = await api.put('/api/v1/settings/platform-settings', update);
    return data;
  },
};

// =============================================================================
// Model Library
// =============================================================================

export const modelLibraryApi = {
  list: async (params?: {
    category?: string;
    search?: string;
    include_public?: boolean;
  }): Promise<ModelLibraryEntry[]> => {
    const { data } = await api.get('/api/v1/model-library/items', { params });
    return data;
  },

  get: async (itemId: string): Promise<ModelLibraryEntry> => {
    const { data } = await api.get(`/api/v1/model-library/items/${itemId}`);
    return data;
  },

  saveFromBuilding: async (
    buildingId: string,
    name: string,
    description?: string,
    category = 'other',
    tags: string[] = [],
  ): Promise<ModelLibraryEntry> => {
    const { data } = await api.post(`/api/v1/model-library/buildings/${buildingId}/save`, {
      name,
      description,
      category,
      tags,
    });
    return data;
  },

  applyToBuilding: async (itemId: string, buildingId: string): Promise<{
    status: string;
    building_id: string;
    model_url: string;
    library_item_id: string;
  }> => {
    const { data } = await api.post(`/api/v1/model-library/items/${itemId}/apply`, {
      building_id: buildingId,
    });
    return data;
  },

  update: async (itemId: string, update: {
    name?: string;
    description?: string;
    category?: string;
    tags?: string[];
    is_public?: boolean;
  }): Promise<ModelLibraryEntry> => {
    const { data } = await api.put(`/api/v1/model-library/items/${itemId}`, null, { params: update });
    return data;
  },

  delete: async (itemId: string): Promise<void> => {
    await api.delete(`/api/v1/model-library/items/${itemId}`);
  },

  bulkImport: async (): Promise<{ status: string; imported: number; skipped: number; total_buildings_with_models: number }> => {
    const { data } = await api.post('/api/v1/model-library/bulk-import', {}, { timeout: 120000 });
    return data;
  },

  /** Get building preview thumbnails grouped by archetype ID. */
  archetypePreviews: async (): Promise<Record<string, Array<{ id: string; name: string; preview_url: string; model_url: string; project_id?: string }>>> => {
    const { data } = await api.get('/api/v1/model-library/archetype-previews');
    return data;
  },
};

export const rendersApi = {
  save: async (projectId: string, render: {
    image_base64: string;
    prompt: string;
    style?: string;
    seed?: number;
    model?: string;
    image_quality?: 'auto' | 'low' | 'medium' | 'high';
  }): Promise<SavedRender> => {
    const { data } = await api.post(`/api/v1/render/projects/${projectId}/save`, render, { timeout: 30000 });
    return data;
  },

  list: async (projectId: string): Promise<SavedRender[]> => {
    const { data } = await api.get(`/api/v1/render/projects/${projectId}/renders`);
    return data;
  },

  delete: async (projectId: string, renderId: string): Promise<void> => {
    await api.delete(`/api/v1/render/projects/${projectId}/renders/${renderId}`);
  },
};

export const elevationApi = {
  get: async (
    lat: number,
    lng: number,
  ): Promise<{ elevation: number; ellipsoidal_height: number; resolution: number }> => {
    const { data } = await api.get('/api/v1/elevation', {
      params: { lat, lng },
    });
    return data;
  },
};

// ---------------------------------------------------------------------------
// Beta Feedback
// ---------------------------------------------------------------------------

export interface FeedbackItem {
  id: string;
  author_id: string;
  author_email?: string;
  author_name?: string;
  category: string;
  text: string;
  page_url?: string;
  status: string;
  admin_notes?: string;
  created_at: string;
}

export interface FeedbackCounts {
  open: number;
  reviewed: number;
  resolved: number;
  dismissed: number;
  total: number;
}

export const feedbackApi = {
  submit: async (body: { category: string; text: string; page_url?: string }): Promise<FeedbackItem> => {
    const { data } = await api.post('/api/v1/feedback', body);
    return data;
  },

  mine: async (): Promise<FeedbackItem[]> => {
    const { data } = await api.get('/api/v1/feedback/mine');
    return data;
  },

  inbox: async (params?: { status_filter?: string; category?: string; limit?: number; skip?: number }): Promise<FeedbackItem[]> => {
    const { data } = await api.get('/api/v1/feedback/inbox', { params });
    return data;
  },

  counts: async (): Promise<FeedbackCounts> => {
    const { data } = await api.get('/api/v1/feedback/inbox/counts');
    return data;
  },

  update: async (feedbackId: string, body: { status?: string; admin_notes?: string }): Promise<FeedbackItem> => {
    const { data } = await api.put(`/api/v1/feedback/${feedbackId}`, body);
    return data;
  },

  delete: async (feedbackId: string): Promise<void> => {
    await api.delete(`/api/v1/feedback/${feedbackId}`);
  },
};

export default api;
