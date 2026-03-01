import { useEffect } from 'react';
import { X } from 'lucide-react';
import { useViewerStore } from '@/store';

export function ImageLightbox() {
  const lightboxImageUrl = useViewerStore((s) => s.lightboxImageUrl);
  const setLightboxImage = useViewerStore((s) => s.setLightboxImage);

  useEffect(() => {
    if (!lightboxImageUrl) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setLightboxImage(null);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [lightboxImageUrl, setLightboxImage]);

  if (!lightboxImageUrl) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={() => setLightboxImage(null)}
    >
      <button
        className="absolute top-4 right-4 rounded-full bg-black/50 p-2 text-white/80 hover:bg-black/70 hover:text-white"
        onClick={() => setLightboxImage(null)}
      >
        <X size={20} />
      </button>
      <img
        src={lightboxImageUrl}
        alt="Expanded preview"
        className="max-h-[90vh] max-w-[90vw] rounded-lg object-contain shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      />
    </div>
  );
}
