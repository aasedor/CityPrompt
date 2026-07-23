import { useEffect, useState } from 'react';
import { X, ArrowDownToLine, Sparkles, Loader2 } from 'lucide-react';
import { useViewerStore } from '@/store';
import { isTextEntryTarget } from '@/utils/domEvents';

export function ImageLightbox() {
  const lightboxImageUrl = useViewerStore((s) => s.lightboxImageUrl);
  const lightboxActions = useViewerStore((s) => s.lightboxActions);
  const setLightboxImage = useViewerStore((s) => s.setLightboxImage);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    if (!lightboxImageUrl) return;
    const handleKey = (e: KeyboardEvent) => {
      if (isTextEntryTarget(e.target)) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        setLightboxImage(null);
        return;
      }

      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
    };
    window.addEventListener('keydown', handleKey, true);
    return () => window.removeEventListener('keydown', handleKey, true);
  }, [lightboxImageUrl, setLightboxImage]);

  // Reset applying state when lightbox closes
  useEffect(() => {
    if (!lightboxImageUrl) setApplying(false);
  }, [lightboxImageUrl]);

  if (!lightboxImageUrl) return null;

  const handleApply = async () => {
    if (!lightboxActions?.onApply || applying) return;
    setApplying(true);
    try {
      await lightboxActions.onApply();
      setLightboxImage(null);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={() => setLightboxImage(null)}
    >
      <button
        onClick={(e) => { e.stopPropagation(); setLightboxImage(null); }}
        className="absolute top-4 right-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black text-xl font-bold text-white shadow-lg ring-2 ring-white/30 transition hover:bg-white hover:text-black"
        aria-label="Close"
        title="Close (Esc)"
      >
        <X size={22} strokeWidth={2.5} />
      </button>
      <div className="flex flex-col items-center gap-3" onClick={(e) => e.stopPropagation()}>
        <img
          src={lightboxImageUrl}
          alt="Expanded preview"
          className="max-h-[85vh] max-w-[90vw] rounded-lg object-contain shadow-2xl"
        />
        {lightboxActions && (lightboxActions.onDownload || lightboxActions.onApply) && (
          <div className="flex items-center gap-2">
            {lightboxActions.onDownload && (
              <button
                onClick={lightboxActions.onDownload}
                className="flex items-center gap-1.5 rounded-lg bg-white/15 px-3 py-2 text-sm font-medium text-white hover:bg-white/25 transition-colors"
              >
                <ArrowDownToLine size={14} />
                Download
              </button>
            )}
            {lightboxActions.onApply && (
              <button
                onClick={handleApply}
                disabled={applying}
                className="flex items-center gap-1.5 rounded-lg bg-purple-600 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
              >
                {applying ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                {applying ? 'Applying...' : (lightboxActions.applyLabel || 'Apply Layout')}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
