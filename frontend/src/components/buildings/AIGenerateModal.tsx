import { useState, useEffect, useRef, useCallback, useSyncExternalStore } from 'react';
import { X, Sparkles, Image, LayoutGrid, Type, Loader2, CheckCircle, AlertCircle, Eye, Cpu } from 'lucide-react';
import { authApi, buildingsApi, getAssetTicketRevision, resolveApiFileUrl, subscribeAssetTicketChanges, type PhotoReferenceStatus, type BuildingReferenceCandidate } from '@/services/api';
import { useAuthStore } from '@/store';
import { StyleSelector } from './StyleSelector';
import { BuildingReferenceSearch } from './BuildingReferenceSearch';
import type { AITemplate, GenerationStatus, GenerationEngine, RenderPreview } from '@/types';

interface AIGenerateModalProps {
  buildingId: string;
  buildingName?: string;
  initialPrompt?: string;
  initialTab?: 'image';
  onClose: () => void;
  onComplete: () => void;
}

type TabId = 'templates' | 'text' | 'image' | 'preview';
type CategoryFilter = 'all' | 'commercial' | 'residential' | 'infrastructure' | 'landscaping';

export function AIGenerateModal({ buildingId, buildingName, initialPrompt, initialTab, onClose, onComplete }: AIGenerateModalProps) {
  // When an initialPrompt is provided (from zone properties), default to the text tab
  const [activeTab, setActiveTab] = useState<TabId>(initialTab ?? (initialPrompt ? 'text' : 'templates'));
  const [generating, setGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState<GenerationStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Style selection (shared across tabs)
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);
  const [showStylePicker, setShowStylePicker] = useState(false);

  // Engine selection
  const [engines, setEngines] = useState<GenerationEngine[]>([]);
  const [selectedEngine, setSelectedEngine] = useState<string | undefined>(undefined);

  // Templates tab state
  const [templates, setTemplates] = useState<AITemplate[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<AITemplate | null>(null);
  const [templatePrompt, setTemplatePrompt] = useState('');

  // Text tab state — pre-fill with initialPrompt from zone properties if provided
  const [textPrompt, setTextPrompt] = useState(initialPrompt || '');
  const [artStyle, setArtStyle] = useState('realistic');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [showNegative, setShowNegative] = useState(false);

  // Student photo workflow state
  const [photoFiles, setPhotoFiles] = useState<File[]>([]);
  const [webReferences, setWebReferences] = useState<BuildingReferenceCandidate[]>([]);
  const [photoPreviews, setPhotoPreviews] = useState<string[]>([]);
  const [photoBrief, setPhotoBrief] = useState('');
  const [photoStatus, setPhotoStatus] = useState<PhotoReferenceStatus | null>(null);
  const [selectedPhotoReferences, setSelectedPhotoReferences] = useState<number[]>([]);
  const [photoBusy, setPhotoBusy] = useState(false);
  const resumedModelRef = useRef(false);
  useSyncExternalStore(subscribeAssetTicketChanges, getAssetTicketRevision);

  const refreshTokenBalance = useCallback(() => {
    authApi.me().then((user) => useAuthStore.getState().setUser(user)).catch(() => {});
  }, []);

  useEffect(() => {
    const urls = photoFiles.map((file) => URL.createObjectURL(file));
    setPhotoPreviews(urls);
    return () => urls.forEach((url) => URL.revokeObjectURL(url));
  }, [photoFiles]);

  useEffect(() => {
    let mounted = true;
    buildingsApi.getPhotoReferences(buildingId)
      .then((status) => { if (mounted) setPhotoStatus(status); })
      .catch(() => { /* Existing text and image generation still work. */ });
    return () => { mounted = false; };
  }, [buildingId]);

  useEffect(() => {
    if (photoStatus?.status !== 'synthesizing' && photoStatus?.status !== 'model_generating') return;
    let mounted = true;
    const timer = setInterval(() => {
      buildingsApi.getPhotoReferences(buildingId)
        .then((status) => { if (mounted) setPhotoStatus(status); })
        .catch(() => {});
    }, 3000);
    return () => { mounted = false; clearInterval(timer); };
  }, [buildingId, photoStatus?.status]);

  useEffect(() => {
    if (photoStatus?.status === 'model_generating') resumedModelRef.current = true;
    if (photoStatus?.status === 'completed' && resumedModelRef.current) {
      resumedModelRef.current = false;
      onComplete();
    }
  }, [photoStatus?.status, onComplete]);

  useEffect(() => {
    if (photoStatus?.status && photoStatus.status !== 'idle') refreshTokenBalance();
  }, [photoStatus?.status, refreshTokenBalance]);

  useEffect(() => {
    if (photoStatus?.status === 'references_ready' || photoStatus?.status === 'failed') {
      setSelectedPhotoReferences(photoStatus.reference_urls.map((_, index) => index));
    } else if (photoStatus?.status === 'completed' || photoStatus?.status === 'model_generating') {
      setSelectedPhotoReferences(photoStatus.selected_reference_indices ?? []);
    }
  }, [photoStatus?.status, photoStatus?.reference_urls, photoStatus?.selected_reference_indices]);

  // Preview tab state
  const [previewPrompt, setPreviewPrompt] = useState('');
  const [previewGenerating, setPreviewGenerating] = useState(false);
  const [renderPreviews, setRenderPreviews] = useState<RenderPreview[]>([]);

  // Load templates and engines
  useEffect(() => {
    buildingsApi.getTemplates().then(setTemplates).catch(() => {});
    buildingsApi.getEngines().then((eng) => {
      setEngines(eng);
    }).catch(() => {});
  }, []);

  // Load existing render previews
  useEffect(() => {
    buildingsApi.getRenderPreviews(buildingId).then(setRenderPreviews).catch(() => {});
  }, [buildingId]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const startPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const status = await buildingsApi.getGenerationStatus(buildingId);
        setGenStatus(status);
        if (status.status === 'completed') {
          if (pollRef.current) clearInterval(pollRef.current);
          setGenerating(false);
          onComplete();
        } else if (status.status === 'failed') {
          if (pollRef.current) clearInterval(pollRef.current);
          setGenerating(false);
          setError(status.error || 'Generation failed');
        }
      } catch {
        // Ignore poll errors
      }
    }, 5000);
  }, [buildingId, onComplete]);

  const handleGenerateText = useCallback(async (prompt: string) => {
    setError(null);
    setGenerating(true);
    setGenStatus({ status: 'generating', progress: 0 });
    try {
      await buildingsApi.generate(
        buildingId, prompt, artStyle,
        negativePrompt || undefined,
        selectedStyle || undefined,
        selectedEngine,
      );
      startPolling();
    } catch (err: unknown) {
      setGenerating(false);
      const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
      const detail = axiosErr.response?.data?.detail;
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: Record<string, unknown>) => (d.msg as string) || JSON.stringify(d)).join('; ')
          : axiosErr.message || 'Failed to start generation';
      setError(msg);
    }
  }, [buildingId, artStyle, negativePrompt, selectedStyle, selectedEngine, startPolling]);

  const handlePreparePhotos = useCallback(async () => {
    if (photoFiles.length + webReferences.length === 0) return;
    setError(null);
    setPhotoBusy(true);
    try {
      await buildingsApi.createPhotoReferences(buildingId, photoFiles, photoBrief.trim(), webReferences.map((item) => item.id));
      setPhotoStatus(await buildingsApi.getPhotoReferences(buildingId));
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(apiError.response?.data?.detail || apiError.message || 'Could not prepare reference views');
    } finally {
      setPhotoBusy(false);
    }
  }, [buildingId, photoFiles, photoBrief, webReferences]);

  const handleGeneratePhotoModel = useCallback(async () => {
    setError(null);
    setGenerating(true);
    setGenStatus({ status: 'generating', progress: 0 });
    try {
      await buildingsApi.generatePhotoModel(buildingId, selectedPhotoReferences);
      setPhotoStatus(await buildingsApi.getPhotoReferences(buildingId));
      startPolling();
    } catch (err: unknown) {
      setGenerating(false);
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(apiError.response?.data?.detail || apiError.message || 'Could not start the 3D model');
    }
  }, [buildingId, selectedPhotoReferences, startPolling]);

  const handleResumePhotos = useCallback(async () => {
    setError(null);
    setPhotoBusy(true);
    try {
      await buildingsApi.resumePhotoReferences(buildingId);
      setPhotoStatus(await buildingsApi.getPhotoReferences(buildingId));
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(apiError.response?.data?.detail || apiError.message || 'Could not resume the views');
    } finally {
      setPhotoBusy(false);
    }
  }, [buildingId]);

  const handleGeneratePreview = useCallback(async () => {
    if (!previewPrompt.trim()) return;
    setPreviewGenerating(true);
    setError(null);
    try {
      await buildingsApi.generatePreview(
        buildingId,
        previewPrompt,
        selectedStyle || undefined,
      );
      // Poll for updated previews
      const pollPreview = setInterval(async () => {
        try {
          const building = await buildingsApi.get(buildingId);
          if (building.preview_status === 'completed') {
            clearInterval(pollPreview);
            setPreviewGenerating(false);
            const previews = await buildingsApi.getRenderPreviews(buildingId);
            setRenderPreviews(previews);
          } else if (building.preview_status === 'failed') {
            clearInterval(pollPreview);
            setPreviewGenerating(false);
            setError('Preview generation failed');
          }
        } catch {
          // ignore
        }
      }, 3000);
      // Timeout after 2 minutes
      setTimeout(() => {
        clearInterval(pollPreview);
        setPreviewGenerating(false);
      }, 120000);
    } catch (err: unknown) {
      setPreviewGenerating(false);
      const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
      const detail = axiosErr.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : axiosErr.message || 'Failed to generate preview');
    }
  }, [buildingId, previewPrompt, selectedStyle]);

  const filteredTemplates = categoryFilter === 'all'
    ? templates
    : templates.filter((t) => t.category === categoryFilter);

  const availableEngines = engines.filter((e) => e.available && e.id !== 'procedural');
  const photoProviderUnavailable = engines.some((engine) => engine.id === 'meshy' && !engine.available);
  const photoWorkInProgress = photoBusy || generating || photoStatus?.status === 'synthesizing' || photoStatus?.status === 'model_generating';

  const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'templates', label: 'Templates', icon: <LayoutGrid size={14} /> },
    { id: 'text', label: 'Text to 3D', icon: <Type size={14} /> },
    { id: 'image', label: 'Photos to 3D', icon: <Image size={14} /> },
    { id: 'preview', label: 'Preview', icon: <Eye size={14} /> },
  ];

  const CATEGORIES: { id: CategoryFilter; label: string }[] = [
    { id: 'all', label: 'All' },
    { id: 'commercial', label: 'Commercial' },
    { id: 'residential', label: 'Residential' },
    { id: 'infrastructure', label: 'Infrastructure' },
    { id: 'landscaping', label: 'Landscaping' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-primary-950/60 backdrop-blur-sm">
      <div className="mx-4 flex max-h-[85vh] w-full max-w-2xl flex-col rounded-2xl bg-white/95 backdrop-blur-xl border border-primary-950/[0.08] shadow-elevated animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-primary-950/[0.08] px-6 py-4">
          <div className="flex items-center gap-2">
            <Sparkles size={20} className="text-purple-500" />
            <div>
              <h2 className="text-lg font-bold text-primary-950">AI 3D Generation</h2>
              <p className="text-xs text-primary-950/50">
                {buildingName ? `Generating for "${buildingName}"` : 'Generate a 3D model'}
                {initialPrompt && ' — prompt pre-filled from zone properties'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Engine selector (only shown when 2+ engines available) */}
            {availableEngines.length >= 2 && (
              <div className="flex items-center gap-1.5 rounded-lg border border-primary-950/[0.08] px-2 py-1">
                <Cpu size={12} className="text-primary-950/50" />
                <select
                  value={selectedEngine || ''}
                  onChange={(e) => setSelectedEngine(e.target.value || undefined)}
                  className="border-none bg-transparent text-xs font-medium text-primary-950/60 focus:outline-none"
                >
                  <option value="">Auto</option>
                  {availableEngines.map((eng) => (
                    <option key={eng.id} value={eng.id}>
                      {eng.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <button
              onClick={onClose}
              aria-label="Close AI generation"
              className="rounded-md p-1.5 text-primary-950/50 hover:bg-primary-950/[0.04] hover:text-primary-950/60"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Style selector bar */}
        <div className="border-b border-primary-950/[0.08] px-6 py-2.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-primary-950/50">Style:</span>
            <StyleSelector
              selectedStyle={selectedStyle}
              onSelect={setSelectedStyle}
              compact
            />
            <button
              onClick={() => setShowStylePicker(!showStylePicker)}
              className="ml-auto text-xs font-medium text-purple-400 hover:text-purple-300"
            >
              {showStylePicker ? 'Less' : 'Browse all'}
            </button>
          </div>
          {showStylePicker && (
            <div className="mt-2.5 max-h-48 overflow-y-auto rounded-lg border border-primary-950/[0.08] p-3">
              <StyleSelector
                selectedStyle={selectedStyle}
                onSelect={(id) => {
                  setSelectedStyle(id);
                  setShowStylePicker(false);
                }}
              />
            </div>
          )}
        </div>

        {/* Engine info banner */}
        {selectedEngine && (
          <div className="border-b border-primary-950/[0.08] bg-primary-950/[0.02] px-6 py-2">
            <p className="text-xs text-primary-950/50">
              <span className="font-medium">{engines.find((e) => e.id === selectedEngine)?.name}:</span>{' '}
              {engines.find((e) => e.id === selectedEngine)?.description}
            </p>
          </div>
        )}

        {/* Generation in progress overlay */}
        {generating && (
          <div className="border-b border-primary-400/20 bg-primary-500/10 px-6 py-4">
            <div className="flex items-center gap-3">
              <Loader2 size={20} className="animate-spin text-primary-400" />
              <div className="flex-1">
                <p className="text-sm font-medium text-primary-200">
                  {genStatus?.progress != null && genStatus.progress > 50
                    ? 'Refining model...'
                    : 'Creating preview...'}
                </p>
                <p className="text-xs text-primary-400">
                  This typically takes 2-4 minutes. You can close this modal and check back later.
                </p>
              </div>
            </div>
            {genStatus?.progress != null && (
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-primary-950/[0.04]">
                <div
                  className="h-full rounded-full bg-primary-500 transition-all duration-1000"
                  style={{ width: `${Math.max(genStatus.progress, 5)}%` }}
                />
              </div>
            )}
          </div>
        )}

        {/* Completed state */}
        {genStatus?.status === 'completed' && (
          <div className="border-b border-green-400/20 bg-green-500/10 px-6 py-4">
            <div className="flex items-center gap-3">
              <CheckCircle size={20} className="text-green-400" />
              <div>
                <p className="text-sm font-medium text-green-200">Model generated successfully!</p>
                <p className="text-xs text-green-400">The 3D model is now available in the viewer.</p>
              </div>
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="border-b border-red-400/20 bg-red-50 px-6 py-4">
            <div className="flex items-center gap-3">
              <AlertCircle size={20} className="text-red-600" />
              <div>
                <p className="text-sm font-medium text-red-200">Generation failed</p>
                <p className="text-xs text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-primary-950/[0.08]">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => !generating && setActiveTab(tab.id)}
              disabled={generating}
              className={`flex flex-1 items-center justify-center gap-1.5 px-4 py-3 text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'border-b-2 border-purple-500 text-purple-400'
                  : 'text-primary-950/50 hover:text-primary-950/60'
              } disabled:opacity-50`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div>
              <div className="mb-4 flex flex-wrap gap-1.5">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setCategoryFilter(cat.id)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition-all ${
                      categoryFilter === cat.id
                        ? 'bg-purple-500/20 text-purple-400'
                        : 'bg-primary-950/[0.04] text-primary-950/50 hover:bg-primary-950/[0.08]'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-3">
                {filteredTemplates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => {
                      setSelectedTemplate(template);
                      setTemplatePrompt(template.prompt);
                    }}
                    className={`rounded-lg border p-3 text-left transition-all ${
                      selectedTemplate?.id === template.id
                        ? 'border-purple-400/40 bg-purple-500/15 ring-2 ring-purple-400/20'
                        : 'border-primary-950/[0.08] hover:border-primary-950/[0.12] hover:bg-white'
                    }`}
                  >
                    <div className="mb-1 flex items-center gap-1.5">
                      <span className="inline-block rounded bg-white/[0.12] px-1.5 py-0.5 text-[10px] font-medium capitalize text-primary-950/50">
                        {template.category}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-primary-950">{template.name}</p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-primary-950/50">{template.prompt}</p>
                  </button>
                ))}
              </div>

              {selectedTemplate && (
                <div className="mt-4 rounded-lg border border-purple-400/20 bg-purple-500/10 p-4">
                  <label className="mb-1 block text-xs font-medium text-purple-400">
                    Prompt (editable)
                  </label>
                  <textarea
                    value={templatePrompt}
                    onChange={(e) => setTemplatePrompt(e.target.value)}
                    rows={2}
                    className="w-full rounded-lg border border-purple-400/30 bg-white px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                  <button
                    onClick={() => handleGenerateText(templatePrompt)}
                    disabled={generating || !templatePrompt.trim()}
                    className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-primary-950 hover:bg-purple-700 disabled:opacity-50"
                  >
                    <Sparkles size={14} />
                    {generating ? 'Generating...' : 'Generate 3D Model'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Text to 3D Tab */}
          {activeTab === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-primary-950/60">Prompt</label>
                <textarea
                  value={textPrompt}
                  onChange={(e) => setTextPrompt(e.target.value)}
                  placeholder="Describe the 3D model you want to generate..."
                  rows={3}
                  className="w-full rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-primary-950/60">Art Style</label>
                <select
                  value={artStyle}
                  onChange={(e) => setArtStyle(e.target.value)}
                  className="w-full rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                >
                  <option value="realistic">Realistic</option>
                  <option value="cartoon">Cartoon</option>
                  <option value="low-poly">Low Poly</option>
                  <option value="sculpture">Sculpture</option>
                </select>
              </div>

              <div>
                <button
                  onClick={() => setShowNegative(!showNegative)}
                  className="text-xs font-medium text-primary-950/50 hover:text-primary-950/60"
                >
                  {showNegative ? 'Hide' : 'Show'} negative prompt
                </button>
                {showNegative && (
                  <textarea
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="What to avoid (e.g., blurry, low quality)..."
                    rows={2}
                    className="mt-1 w-full rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                )}
              </div>

              <button
                onClick={() => handleGenerateText(textPrompt)}
                disabled={generating || !textPrompt.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 px-4 py-2.5 text-sm font-medium text-primary-950 hover:bg-purple-700 disabled:opacity-50"
              >
                <Sparkles size={14} />
                {generating ? 'Generating...' : 'Generate 3D Model'}
              </button>
            </div>
          )}

          {/* Image to 3D Tab */}
          {activeTab === 'image' && (
            <div className="space-y-4">
              <div className="rounded-xl border border-primary-950/[0.1] bg-primary-950/[0.02] p-4">
                <h3 className="text-sm font-bold text-primary-950">Build from your photos</h3>
                <p className="mt-1 text-xs text-primary-950/65">
                  Choose 1–4 views of the same building: upload photos or find more views online below. Put your clearest front photo first. We prepare reference views for you to review, then create a private 3D model preview. This is an AI mesh, not a reviewed catalogue building.
                </p>
                {photoProviderUnavailable && <p role="status" className="mt-2 text-xs text-amber-800">Photo modeling is temporarily unavailable. An administrator needs to connect the 3D provider.</p>}
                <label className="mt-3 block text-xs font-semibold text-primary-950/70">Building photos (JPG or PNG, 5 MB each)</label>
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  multiple
                  disabled={photoWorkInProgress}
                  onChange={(event) => {
                    const files = Array.from(event.target.files || []);
                    if (files.length + webReferences.length > 4 || files.some((file) => file.size > 5 * 1024 * 1024)) {
                      setError('Choose up to 4 photos total, including web photos. Uploads must be 5 MB or smaller.');
                      event.target.value = '';
                      return;
                    }
                    setError(null);
                    setPhotoFiles(files);
                  }}
                  className="mt-1 w-full text-xs text-primary-950/70 file:mr-3 file:rounded-lg file:border-0 file:bg-primary-950 file:px-3 file:py-2 file:text-white"
                />
                {photoPreviews.length > 0 && (
                  <div className="mt-3 grid grid-cols-4 gap-2">
                    {photoPreviews.map((url, index) => <img key={url} src={url} alt={`Uploaded view ${index + 1}`} className="h-20 w-full rounded object-cover" />)}
                  </div>
                )}
                <BuildingReferenceSearch buildingId={buildingId} selected={webReferences} onChange={setWebReferences}
                  capacity={4 - photoFiles.length} disabled={photoWorkInProgress} />
                <label className="mt-3 block text-xs font-semibold text-primary-950/70" htmlFor="photo-building-brief">Describe anything the photos do not show</label>
                <textarea
                  id="photo-building-brief"
                  disabled={photoWorkInProgress}
                  value={photoBrief}
                  onChange={(event) => setPhotoBrief(event.target.value.slice(0, 500))}
                  rows={2}
                  placeholder="For example: two mirrored homes, two storeys, separate front doors..."
                  className="mt-1 w-full rounded-lg border border-primary-950/[0.12] bg-white p-2 text-sm text-primary-950"
                />
                <button
                  onClick={handlePreparePhotos}
                  disabled={photoProviderUnavailable || photoWorkInProgress || photoFiles.length + webReferences.length === 0}
                  className="mt-2 w-full rounded-lg bg-purple-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                >
                  {photoBusy || photoStatus?.status === 'synthesizing' ? 'Preparing reference views…' : 'Step 1 · Prepare reference views'}
                </button>
                <p className="mt-1 text-xs text-primary-950/55">Costs {photoStatus?.reference_token_cost ?? 50} City Prompt tokens. Tokens are restored if this step fails. It may take several minutes.</p>
              </div>

              {photoStatus?.status === 'synthesizing' && <p className="text-sm text-primary-950/65">Preparing reference views. You can close this window and return later.</p>}
              {photoStatus?.status === 'failed' && <p role="alert" className="text-sm text-red-700">{photoStatus.error || 'Photo generation failed.'} Your existing building remains in place.</p>}
              {photoStatus?.resume_available && (
                <button onClick={handleResumePhotos} disabled={photoBusy} className="w-full rounded-lg border border-primary-950 px-3 py-2 text-sm font-semibold text-primary-950 disabled:opacity-50">
                  Recover prepared views · no extra tokens
                </button>
              )}
              {photoStatus && photoStatus.reference_urls.length >= 2 && (
                <div className="rounded-xl border border-primary-950/[0.1] p-4">
                  <h3 className="text-sm font-bold text-primary-950">Review the generated views</h3>
                  {photoStatus.source_provenance?.some((source) => source.provider === 'wikimedia_commons') && (
                    <details className="mt-2 text-xs text-primary-950/65">
                      <summary className="cursor-pointer">Web photo sources used for these views</summary>
                      <ul className="mt-1 space-y-1">
                        {photoStatus.source_provenance.filter((source) => source.provider === 'wikimedia_commons').map((source) => (
                          <li key={source.sha256}><a href={source.source_url} target="_blank" rel="noopener noreferrer" className="underline">{source.title}</a> · {source.author} · {source.license}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                  <p className="mt-1 text-xs text-primary-950/65">Check the roof, entrances, window pattern and materials. Deselect any damaged or misleading view before making a model, or upload better photos to prepare a new set.</p>
                  <div className="mt-3 grid grid-cols-3 gap-2">
                    {photoStatus.reference_urls.map((url, index) => (
                      <label key={url} className="block text-xs text-primary-950/70">
                        <img src={resolveApiFileUrl(url)} alt={`Generated building reference ${index + 1}`} className="aspect-square w-full rounded border border-primary-950/[0.1] object-contain" />
                        <span className="mt-1 flex items-center gap-1">
                          <input
                            type="checkbox"
                            disabled={photoWorkInProgress || photoStatus.status === 'completed'}
                            checked={selectedPhotoReferences.includes(index)}
                            onChange={() => setSelectedPhotoReferences((current) => current.includes(index)
                              ? current.filter((item) => item !== index)
                              : [...current, index].sort((a, b) => a - b))}
                          />
                          Use view {index + 1}
                        </span>
                      </label>
                    ))}
                  </div>
                  <button
                    onClick={handleGeneratePhotoModel}
                    disabled={photoProviderUnavailable || generating || selectedPhotoReferences.length === 0 || !['references_ready', 'failed'].includes(photoStatus.status)}
                    className="mt-3 w-full rounded-lg bg-primary-950 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {photoStatus.status === 'model_generating' ? '3D model generating…' : photoStatus.status === 'completed' ? '3D model ready' : 'Step 2 · Generate 3D model preview'}
                  </button>
                  <p className="mt-1 text-xs text-primary-950/55">Costs {photoStatus.model_token_cost} City Prompt tokens. Tokens are restored if this step fails. Review the result before using it in a final render.</p>
                </div>
              )}

            </div>
          )}

          {/* Preview Tab (AI Render) */}
          {activeTab === 'preview' && (
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-primary-950/60">
                  Render Preview Prompt
                </label>
                <textarea
                  value={previewPrompt}
                  onChange={(e) => setPreviewPrompt(e.target.value)}
                  placeholder="Describe the architectural visualization you want..."
                  rows={3}
                  className="w-full rounded-lg border border-primary-950/[0.1] bg-white px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
                <p className="mt-1 text-xs text-primary-950/50">
                  Generates a photorealistic 2D render preview using Stability AI.
                  {selectedStyle && ` Style "${selectedStyle}" will be applied to the prompt.`}
                </p>
              </div>

              <button
                onClick={handleGeneratePreview}
                disabled={previewGenerating || !previewPrompt.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-600 disabled:opacity-50"
              >
                {previewGenerating ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Generating Preview...
                  </>
                ) : (
                  <>
                    <Eye size={14} />
                    Generate Preview
                  </>
                )}
              </button>

              {/* Render preview gallery */}
              {renderPreviews.length > 0 && (
                <div>
                  <h4 className="mb-2 text-xs font-semibold text-primary-950/50 uppercase">
                    Render Previews ({renderPreviews.length})
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    {renderPreviews.map((preview) => (
                      <div
                        key={preview.id}
                        className="group relative overflow-hidden rounded-lg border border-primary-950/[0.08]"
                      >
                        <img
                          src={preview.image_url}
                          alt={preview.prompt || 'Render preview'}
                          className="h-40 w-full object-cover"
                        />
                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                          <p className="line-clamp-1 text-[10px] text-primary-950">
                            {preview.prompt}
                          </p>
                          {preview.style && (
                            <span className="mt-0.5 inline-block rounded bg-primary-950/[0.06] px-1 py-0.5 text-[9px] text-primary-950">
                              {preview.style}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {renderPreviews.length === 0 && !previewGenerating && (
                <p className="text-center text-xs text-primary-950/50">
                  No render previews yet. Generate one above to see a photorealistic visualization.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-primary-950/[0.08] px-6 py-3">
          <p className="text-center text-xs text-primary-950/50">
            {activeTab === 'preview'
              ? 'Powered by Stability AI'
              : `Powered by ${selectedEngine === 'tripo' ? 'Tripo3D' : 'Meshy.ai'}`}
            {activeTab !== 'preview' && ' \u00b7 Generation typically takes 2-4 minutes'}
          </p>
        </div>
      </div>
    </div>
  );
}
