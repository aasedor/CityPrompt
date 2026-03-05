import { useState, useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { useViewerStore } from '@/store';

export function WalkthroughHUD() {
  const { settings, isWalkthroughActive, exitWalkthrough, setCameraMode } = useViewerStore();
  const mode = settings.cameraMode;
  const showHUD = mode === 'firstPerson' || mode === 'flyThrough';

  // Auto-fade the controls hint after 8 seconds, re-show when mode changes
  const [hintVisible, setHintVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (showHUD) {
      setHintVisible(true);
      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setHintVisible(false), 8000);
    } else {
      setHintVisible(false);
    }
    return () => clearTimeout(timerRef.current);
  }, [showHUD, mode]);

  if (!showHUD) return null;

  const modeLabel = mode === 'firstPerson' ? 'Walk' : 'Fly';

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

      {/* Persistent exit button (top-right) */}
      {isWalkthroughActive ? (
        <button
          onClick={() => {
            if (document.pointerLockElement) document.exitPointerLock();
            exitWalkthrough();
          }}
          className="fixed right-4 top-16 z-40 flex items-center gap-1.5 rounded-lg bg-white/70 px-3 py-2 text-sm font-medium text-primary-950/90 dark:text-white/90 shadow-lg backdrop-blur-md hover:bg-white/95 transition-colors"
        >
          <X size={14} />
          Exit Walkthrough
        </button>
      ) : (
        <button
          onClick={() => {
            if (document.pointerLockElement) document.exitPointerLock();
            setCameraMode('orbit');
          }}
          className="fixed right-4 top-16 z-40 flex items-center gap-1.5 rounded-lg bg-white/70 px-3 py-2 text-sm font-medium text-primary-950/90 dark:text-white/90 shadow-lg backdrop-blur-md hover:bg-white/95 transition-colors"
        >
          <X size={14} />
          Exit {modeLabel} Mode
        </button>
      )}

      {/* Controls hint pill */}
      <div
        className={`pointer-events-none fixed bottom-8 left-1/2 z-30 -translate-x-1/2 transition-opacity duration-500 ${
          hintVisible ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <div className="rounded-full bg-white/70 px-5 py-2.5 text-sm text-primary-950/90 dark:text-white/90 shadow-lg backdrop-blur-md">
          <kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">WASD</kbd> to move
          <span className="mx-2 text-primary-950/40 dark:text-white/40">|</span>
          <kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">Shift</kbd> to sprint
          <span className="mx-2 text-primary-950/40 dark:text-white/40">|</span>
          {mode === 'flyThrough' && (
            <>
              <kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">Q</kbd>/<kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">Space</kbd> up
              <span className="mx-2 text-primary-950/40 dark:text-white/40">|</span>
              <kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">E</kbd> down
              <span className="mx-2 text-primary-950/40 dark:text-white/40">|</span>
            </>
          )}
          <kbd className="mx-1 rounded bg-primary-950/[0.06] px-1.5 py-0.5 text-xs font-mono">ESC</kbd> to exit
        </div>
      </div>
    </>
  );
}
