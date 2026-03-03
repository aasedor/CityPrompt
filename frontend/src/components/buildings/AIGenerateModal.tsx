import { useState, useEffect, useRef, useCallback } from 'react';
import { X, Sparkles, Image, LayoutGrid, Type, Loader2, CheckCircle, AlertCircle, Upload, Eye, Cpu } from 'lucide-react';
import { buildingsApi } from '@/services/api';
import { StyleSelector } from './StyleSelector';
import type { AITemplate, GenerationStatus, GenerationEngine, RenderPreview } from '@/types';

interface AIGenerateModalProps {
  buildingId: string;
  buildingName?: string;
  initialPrompt?: string;
  onClose: () => void;
  onComplete: () => void;
}

type TabId = 'templates' | 'text' | 'image' | 'preview';
type CategoryFilter = 'all' | 'commercial' | 'residential' | 'infrastructure' | 'landscaping';

export function AIGenerateModal({ buildingId, buildingName, initialPrompt, onClose, onComplete }: AIGenerateModalProps) {
  // When an initialPrompt is provided (from zone properties), default to the text tab
  const [activeTab, setActiveTab] = useState<TabId>(initialPrompt ? 'text' : 'templates');
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

  // Image tab state
  const [imageUrl, setImageUrl] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);

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

  const handleGenerateImage = useCallback(async () => {
    if (!imageUrl.trim()) return;
    setError(null);
    setGenerating(true);
    setGenStatus({ status: 'generating', progress: 0 });
    try {
      await buildingsApi.generateFromImage(buildingId, imageUrl.trim());
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
  }, [buildingId, imageUrl, startPolling]);

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

  const handleImageFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setImagePreview(dataUrl);
      setImageUrl(dataUrl);
    };
    reader.readAsDataURL(file);
  }, []);

  const filteredTemplates = categoryFilter === 'all'
    ? templates
    : templates.filter((t) => t.category === categoryFilter);

  const availableEngines = engines.filter((e) => e.available && e.id !== 'procedural');

  const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'templates', label: 'Templates', icon: <LayoutGrid size={14} /> },
    { id: 'text', label: 'Text to 3D', icon: <Type size={14} /> },
    { id: 'image', label: 'Image to 3D', icon: <Image size={14} /> },
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
      <div className="mx-4 flex max-h-[85vh] w-full max-w-2xl flex-col rounded-2xl bg-primary-900/95 backdrop-blur-xl border border-white/[0.1] shadow-elevated animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/[0.08] px-6 py-4">
          <div className="flex items-center gap-2">
            <Sparkles size={20} className="text-purple-500" />
            <div>
              <h2 className="text-lg font-bold text-white">AI 3D Generation</h2>
              <p className="text-xs text-neutral-400">
                {buildingName ? `Generating for "${buildingName}"` : 'Generate a 3D model'}
                {initialPrompt && ' — prompt pre-filled from zone properties'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Engine selector (only shown when 2+ engines available) */}
            {availableEngines.length >= 2 && (
              <div className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] px-2 py-1">
                <Cpu size={12} className="text-neutral-400" />
                <select
                  value={selectedEngine || ''}
                  onChange={(e) => setSelectedEngine(e.target.value || undefined)}
                  className="border-none bg-transparent text-xs font-medium text-neutral-300 focus:outline-none"
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
              className="rounded-md p-1.5 text-neutral-400 hover:bg-white/10 hover:text-neutral-300"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Style selector bar */}
        <div className="border-b border-white/[0.08] px-6 py-2.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-neutral-400">Style:</span>
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
            <div className="mt-2.5 max-h-48 overflow-y-auto rounded-lg border border-white/[0.08] p-3">
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
          <div className="border-b border-white/[0.08] bg-white/[0.03] px-6 py-2">
            <p className="text-xs text-neutral-400">
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
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
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
          <div className="border-b border-red-400/20 bg-red-500/10 px-6 py-4">
            <div className="flex items-center gap-3">
              <AlertCircle size={20} className="text-red-400" />
              <div>
                <p className="text-sm font-medium text-red-200">Generation failed</p>
                <p className="text-xs text-red-400">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-white/[0.08]">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => !generating && setActiveTab(tab.id)}
              disabled={generating}
              className={`flex flex-1 items-center justify-center gap-1.5 px-4 py-3 text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'border-b-2 border-purple-500 text-purple-400'
                  : 'text-neutral-400 hover:text-neutral-300'
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
                        : 'bg-white/10 text-neutral-400 hover:bg-white/[0.15]'
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
                        : 'border-white/[0.08] hover:border-white/[0.15] hover:bg-white/[0.06]'
                    }`}
                  >
                    <div className="mb-1 flex items-center gap-1.5">
                      <span className="inline-block rounded bg-white/[0.12] px-1.5 py-0.5 text-[10px] font-medium capitalize text-neutral-400">
                        {template.category}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-white">{template.name}</p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-neutral-400">{template.prompt}</p>
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
                    className="w-full rounded-lg border border-purple-400/30 bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                  <button
                    onClick={() => handleGenerateText(templatePrompt)}
                    disabled={generating || !templatePrompt.trim()}
                    className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
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
                <label className="mb-1 block text-sm font-medium text-neutral-300">Prompt</label>
                <textarea
                  value={textPrompt}
                  onChange={(e) => setTextPrompt(e.target.value)}
                  placeholder="Describe the 3D model you want to generate..."
                  rows={3}
                  className="w-full rounded-lg border border-white/[0.12] bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-neutral-300">Art Style</label>
                <select
                  value={artStyle}
                  onChange={(e) => setArtStyle(e.target.value)}
                  className="w-full rounded-lg border border-white/[0.12] bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
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
                  className="text-xs font-medium text-neutral-400 hover:text-neutral-300"
                >
                  {showNegative ? 'Hide' : 'Show'} negative prompt
                </button>
                {showNegative && (
                  <textarea
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="What to avoid (e.g., blurry, low quality)..."
                    rows={2}
                    className="mt-1 w-full rounded-lg border border-white/[0.12] bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                )}
              </div>

              <button
                onClick={() => handleGenerateText(textPrompt)}
                disabled={generating || !textPrompt.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
              >
                <Sparkles size={14} />
                {generating ? 'Generating...' : 'Generate 3D Model'}
              </button>
            </div>
          )}

          {/* Image to 3D Tab */}
          {activeTab === 'image' && (
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-neutral-300">Upload Image</label>
                <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-white/[0.15] p-6 transition-all hover:border-purple-400/50 hover:bg-purple-500/10">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview" className="max-h-40 rounded-lg object-contain" />
                  ) : (
                    <>
                      <Upload size={32} className="mb-2 text-neutral-400" />
                      <p className="text-sm text-neutral-400">Click to upload an image</p>
                      <p className="text-xs text-neutral-500">PNG, JPG up to 10MB</p>
                    </>
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageFileSelect}
                    className="hidden"
                  />
                </label>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/[0.08]" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-primary-900/95 px-2 text-xs text-neutral-400">or</span>
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-neutral-300">Image URL</label>
                <input
                  type="url"
                  value={imageUrl.startsWith('data:') ? '' : imageUrl}
                  onChange={(e) => {
                    setImageUrl(e.target.value);
                    setImagePreview(null);
                  }}
                  placeholder="https://example.com/building-photo.jpg"
                  className="w-full rounded-lg border border-white/[0.12] bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <button
                onClick={handleGenerateImage}
                disabled={generating || !imageUrl.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-purple-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
              >
                <Sparkles size={14} />
                {generating ? 'Generating...' : 'Generate from Image'}
              </button>
            </div>
          )}

          {/* Preview Tab (AI Render) */}
          {activeTab === 'preview' && (
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-neutral-300">
                  Render Preview Prompt
                </label>
                <textarea
                  value={previewPrompt}
                  onChange={(e) => setPreviewPrompt(e.target.value)}
                  placeholder="Describe the architectural visualization you want..."
                  rows={3}
                  className="w-full rounded-lg border border-white/[0.12] bg-white/[0.04] px-3 py-2 text-sm text-neutral-100 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
                <p className="mt-1 text-xs text-neutral-400">
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
                  <h4 className="mb-2 text-xs font-semibold text-neutral-400 uppercase">
                    Render Previews ({renderPreviews.length})
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    {renderPreviews.map((preview) => (
                      <div
                        key={preview.id}
                        className="group relative overflow-hidden rounded-lg border border-white/[0.08]"
                      >
                        <img
                          src={preview.image_url}
                          alt={preview.prompt || 'Render preview'}
                          className="h-40 w-full object-cover"
                        />
                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                          <p className="line-clamp-1 text-[10px] text-white">
                            {preview.prompt}
                          </p>
                          {preview.style && (
                            <span className="mt-0.5 inline-block rounded bg-white/20 px-1 py-0.5 text-[9px] text-white">
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
                <p className="text-center text-xs text-neutral-400">
                  No render previews yet. Generate one above to see a photorealistic visualization.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-white/[0.08] px-6 py-3">
          <p className="text-center text-xs text-neutral-400">
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
