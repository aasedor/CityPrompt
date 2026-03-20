/**
 * RenderResultModal — Full-screen presentation modal for AI render results.
 *
 * Flow:
 *   1. Shows 3 preview thumbnails — user clicks to select one
 *   2. Selected preview triggers full-quality render
 *   3. Full result displayed with download button
 */
import { useCallback } from 'react';
import type { AIRenderResult } from './useAIRender';

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
}

export function RenderResultModal({
  previews,
  selectedIndex,
  onSelectPreview,
  onClose,
  isGeneratingFull,
  fullResult,
  progressMessage,
}: RenderResultModalProps) {
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
              className="max-h-[60vh] max-w-full rounded-lg object-contain shadow-xl"
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
    </div>
  );
}
