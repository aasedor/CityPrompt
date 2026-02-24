import { useState, useEffect, useRef } from 'react';
import { useViewerStore } from '@/store';

export function WalkthroughHUD() {
  const { settings, isWalkthroughActive } = useViewerStore();
  const mode = settings.cameraMode;
  const showHUD = mode === 'firstPerson' || mode === 'flyThrough';

  // Auto-fade the controls hint after 5 seconds
  const [hintVisible, setHintVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (isWalkthroughActive) {
      setHintVisible(true);
      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setHintVisible(false), 5000);
    } else {
      setHintVisible(false);
    }
    return () => clearTimeout(timerRef.current);
  }, [isWalkthroughActive]);

  if (!showHUD) return null;

  return (
    <>
      {/* Crosshair */}
      {settings.showCrosshair && (
        <div className="pointer-events-none fixed inset-0 z-30 flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" className="opacity-60">
            {/* Horizontal line */}
            <line x1="4" y1="12" x2="10" y2="12" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="14" y1="12" x2="20" y2="12" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            {/* Vertical line */}
            <line x1="12" y1="4" x2="12" y2="10" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="12" y1="14" x2="12" y2="20" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            {/* Center dot */}
            <circle cx="12" cy="12" r="1.5" fill="white" />
          </svg>
        </div>
      )}

      {/* Controls hint pill */}
      {isWalkthroughActive && (
        <div
          className={`pointer-events-none fixed bottom-8 left-1/2 z-30 -translate-x-1/2 transition-opacity duration-500 ${
            hintVisible ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <div className="rounded-full bg-gray-900/70 px-5 py-2.5 text-sm text-white/90 shadow-lg backdrop-blur-md">
            Press <kbd className="mx-1 rounded bg-white/20 px-1.5 py-0.5 text-xs font-mono">ESC</kbd> to exit
            <span className="mx-2 text-white/40">|</span>
            <kbd className="mx-1 rounded bg-white/20 px-1.5 py-0.5 text-xs font-mono">WASD</kbd> to move
            <span className="mx-2 text-white/40">|</span>
            <kbd className="mx-1 rounded bg-white/20 px-1.5 py-0.5 text-xs font-mono">Shift</kbd> to sprint
          </div>
        </div>
      )}
    </>
  );
}
