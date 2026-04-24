/**
 * RenderResultModal — Full-screen presentation modal for AI render results.
 *
 * Flow:
 *   1. Shows 3 preview thumbnails — user clicks to select one
 *   2. Selected preview triggers full-quality render
 *   3. Full result displayed with download + save buttons
 */
import { useCallback, useEffect, useState } from 'react';
import type { AIRenderResult } from './useAIRender';
import { rendersApi } from '@/services/api';

interface RenderResultModalProps {
  /** The 3 preview renders to choose from */
  previews: AIRenderResult[];
  /** Index of the currently selected preview (null = none yet) */
  selectedIndex: number | null;
  /** Called when user clicks a preview to select it */
  onSelectPreview: (index: number) => void;
  /** Called when user closes the modal */
  onClose: () => void;
  /** Whether a full-quality render is in progress */
  isGeneratingFull: boolean;
  /** The final full-quality render result */
  fullResult: AIRenderResult | null;
  /** Progress / status message */
  progressMessage: string;
  /** Project ID for saving renders */
  projectId?: string;
  /** Style preset used for generation */
  style?: string;
  /** Called after a render is saved successfully */
  onSaved?: () => void;
}

export function RenderResultModal({
  previews,
  selectedIndex,
  onSelectPreview,
  onClose,
  isGeneratingFull,
  fullResult,
  progressMessage,
  projectId,
  style,
  onSaved,
}: RenderResultModalProps) {
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [expandedImage, setExpandedImage] = useState<string | null>(null);

  useEffect(() => {
    if (!expandedImage) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setExpandedImage(null);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [expandedImage]);

  const handleDownload = useCallback(() => {
    const url = fullResult?.imageUrl;
    if (!url) return;
    const a = document.createElement('a');
    a.href = url;
    a.download = `siteforge-render-${Date.now()}.png`;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [fullResult]);

  const handleSave = useCallback(async () => {
    if (!fullResult?.imageUrl || !projectId || saveStatus === 'saving' || saveStatus === 'saved') return;
    setSaveStatus('saving');
    try {
      // Extract base64 from data URI
      let base64 = '';
      if (fullResult.imageUrl.startsWith('data:')) {
        base64 = fullResult.imageUrl.split(',')[1];
      } else {
        // Fetch the image and convert to base64
        const resp = await fetch(fullResult.imageUrl);
        const blob = await resp.blob();
        base64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
          reader.readAsDataURL(blob);
        });
      }
      await rendersApi.save(projectId, {
        image_base64: base64,
        prompt: fullResult.prompt || '',
        style: style,
        seed: fullResult.seed,
      });
      setSaveStatus('saved');
      onSaved?.();
    } catch (err) {
      console.error('[RenderResultModal] Save failed:', err);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  }, [fullResult, projectId, style, saveStatus]);

  const displayImage = fullResult?.imageUrl ?? (selectedIndex != null ? previews[selectedIndex]?.imageUrl : null);

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative flex max-h-[95vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-gray-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
          <div className="flex items-center gap-3">
            <svg className="h-5 w-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
            <h2 className="text-lg font-semibold text-white">
              {fullResult ? 'Render Complete' : isGeneratingFull ? 'Generating Full Quality...' : 'Choose a Preview'}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {fullResult && projectId && (
              <button
                onClick={handleSave}
                disabled={saveStatus === 'saving' || saveStatus === 'saved'}
                className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                  saveStatus === 'saved'
                    ? 'bg-green-600 text-white'
                    : saveStatus === 'error'
                      ? 'bg-red-600 text-white hover:bg-red-500'
                      : 'bg-white/10 text-white hover:bg-white/20'
                }`}
              >
                {saveStatus === 'saving' ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : saveStatus === 'saved' ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                ) : (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
                  </svg>
                )}
                {saveStatus === 'saved' ? 'Saved' : saveStatus === 'error' ? 'Failed — Retry' : 'Save to Project'}
              </button>
            )}
            {fullResult && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-amber-400"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                Download PNG
              </button>
            )}
            <button
              onClick={onClose}
              className="rounded-lg p-2 text-gray-400 transition hover:bg-white/10 hover:text-white"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Main image area */}
        <div className="flex flex-1 items-center justify-center overflow-hidden p-6">
          {displayImage ? (
            <img
              src={displayImage}
              alt="AI Render"
              className="max-h-[60vh] max-w-full cursor-zoom-in rounded-lg object-contain shadow-xl transition hover:opacity-95"
              onClick={() => setExpandedImage(displayImage)}
              title="Click to enlarge"
            />
          ) : (
            <div className="flex flex-col items-center gap-4 text-gray-500">
              <svg className="h-16 w-16 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
              </svg>
              <p className="text-sm">Select a preview below to see it larger</p>
            </div>
          )}

          {/* Loading overlay on image */}
          {isGeneratingFull && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-black/50">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-amber-500 border-t-transparent" />
              <p className="text-sm font-medium text-white">{progressMessage || 'Generating full quality render...'}</p>
            </div>
          )}
        </div>

        {/* Preview strip */}
        <div className="border-t border-white/10 bg-gray-950/50 px-6 py-4">
          <div className="mb-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
            {fullResult ? 'Original previews' : 'Select a preview to generate full quality'}
          </div>
          <div className="flex gap-3">
            {previews.map((preview, idx) => (
              <button
                key={preview.seed ?? idx}
                onClick={() => !isGeneratingFull && onSelectPreview(idx)}
                disabled={isGeneratingFull}
                className={`
                  relative overflow-hidden rounded-lg border-2 transition
                  ${isGeneratingFull ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:border-white/30'}
                  ${selectedIndex === idx
                    ? 'border-amber-400 shadow-lg shadow-amber-500/20'
                    : 'border-transparent'
                  }
                `}
              >
                <img
                  src={preview.imageUrl}
                  alt={`Preview ${idx + 1}`}
                  className="h-24 w-24 object-cover"
                />
                <span className="absolute bottom-1 right-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-medium text-white/80">
                  #{idx + 1}
                </span>
                {selectedIndex === idx && (
                  <div className="absolute inset-0 flex items-center justify-center bg-amber-500/10">
                    <svg className="h-6 w-6 text-amber-400 drop-shadow" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
      {expandedImage && (
        <div
          className="fixed inset-0 z-[260] flex items-center justify-center bg-black/90 p-6"
          onClick={() => setExpandedImage(null)}
          role="dialog"
          aria-label="Expanded AI render"
        >
          <button
            onClick={(e) => { e.stopPropagation(); setExpandedImage(null); }}
            className="absolute top-4 right-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
            aria-label="Close"
            title="Close (Esc)"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <img
            src={expandedImage}
            alt="Expanded AI render"
            className="max-h-[86vh] max-w-[92vw] rounded-lg object-contain shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
