import { useState, useEffect, useCallback, useRef, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';

// ---------------------------------------------------------------------------
// Tour step definitions
// ---------------------------------------------------------------------------

interface TourStep {
  /** CSS selector for the element to spotlight */
  target: string;
  title: string;
  body: string;
  /** Optional animation key */
  animation?: 'draw-boundary' | 'draw-road' | 'place-building' | 'ai-render';
  /** Which side to position the tooltip relative to the target */
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

const STEPS: TourStep[] = [
  {
    target: '[data-tour="more-tools-btn"]',
    title: 'Optional Site Boundary',
    body: 'Use More Tools > Site Boundary when you want a parcel-wide planning and landscaping scope. You can also start directly with a park, building, or street.',
    animation: 'draw-boundary',
    placement: 'top',
  },
  {
    target: '[data-tour="tool-streetsPaths"]',
    title: 'Draw Roads & Paths',
    body: 'Click to draw a path for streets and walkways. Each click adds a point — double-click or press Enter to finish the road.',
    animation: 'draw-road',
    placement: 'top',
  },
  {
    target: '[data-tour="tool-buildings"]',
    title: 'Place Buildings',
    body: 'Draw polygons to place building zones. If you added a site boundary, keep them inside it. Click to add corners, double-click or press Enter to finish.',
    animation: 'place-building',
    placement: 'top',
  },
  {
    target: '[data-tour="select-btn"]',
    title: 'Select & Customize',
    body: 'Switch to Select mode to click on any zone you\'ve drawn. You can edit its properties — height, style, materials, and more.',
    placement: 'top',
  },
  {
    target: '[data-tour="ai-render-btn"]',
    title: 'Generate AI Render',
    body: 'Once your zones are placed, hit AI Render to bring your site plan to life with a photorealistic aerial view.',
    animation: 'ai-render',
    placement: 'top',
  },
];

// ---------------------------------------------------------------------------
// Mini SVG animations for each step
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Canvas-based click-to-draw animation
// ---------------------------------------------------------------------------

interface Shape {
  /** Vertices the "cursor" clicks through */
  points: [number, number][];
  /** Whether to close the polygon or leave as polyline */
  closed: boolean;
  /** Stroke color */
  stroke: string;
  /** Fill color (only used if closed) */
  fill: string;
}

interface DrawConfig {
  /** One or more shapes to draw in sequence */
  shapes: Shape[];
  /** Milliseconds the cursor sits on each vertex before moving to the next */
  msPerVertex: number;
  /** Milliseconds to show the fill after each shape is complete */
  msFill: number;
  /** Milliseconds to hold after everything is drawn before restarting */
  msPause: number;
}

function useDrawAnimation(canvasRef: React.RefObject<HTMLCanvasElement | null>, config: DrawConfig) {
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 400;
    const H = 160;
    canvas.width = W;
    canvas.height = H;

    const { shapes, msPerVertex, msFill, msPause } = config;
    if (shapes.length === 0) return;

    // Build a timeline: for each shape, time to draw vertices + fill
    const shapeTimes = shapes.map((s) => s.points.length * msPerVertex + (s.closed ? msFill : 0));
    const totalDraw = shapeTimes.reduce((a, b) => a + b, 0);
    const totalCycle = totalDraw + msPause;

    let raf = 0;
    const start = performance.now();

    const drawShape = (
      shape: Shape,
      verticesPlaced: number,
      fillProgress: number,
    ) => {
      const { points, closed, stroke, fill } = shape;

      // Draw lines between placed vertices
      if (verticesPlaced >= 2) {
        ctx.beginPath();
        ctx.moveTo(points[0][0], points[0][1]);
        for (let i = 1; i < verticesPlaced; i++) {
          ctx.lineTo(points[i][0], points[i][1]);
        }
        if (closed && verticesPlaced === points.length) {
          ctx.closePath();
        }
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 3;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.globalAlpha = 1;
        ctx.stroke();
      }

      // Fill when complete
      if (closed && fillProgress > 0) {
        ctx.fillStyle = fill;
        ctx.globalAlpha = fillProgress * 0.18;
        ctx.beginPath();
        ctx.moveTo(points[0][0], points[0][1]);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i][0], points[i][1]);
        }
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Vertex dots
      for (let i = 0; i < verticesPlaced; i++) {
        const [x, y] = points[i];
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = stroke;
        ctx.globalAlpha = 1;
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x, y, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
      }
    };

    const render = (now: number) => {
      const elapsed = (now - start) % totalCycle;
      ctx.clearRect(0, 0, W, H);

      let timeOffset = 0;

      for (let s = 0; s < shapes.length; s++) {
        const shape = shapes[s];
        const drawTime = shape.points.length * msPerVertex;
        const shapeEnd = drawTime + (shape.closed ? msFill : 0);
        const localTime = elapsed - timeOffset;

        if (localTime < 0) {
          // Haven't reached this shape yet
          break;
        }

        if (localTime >= shapeEnd) {
          // Shape fully complete — draw it finished
          drawShape(shape, shape.points.length, shape.closed ? 1 : 0);
          timeOffset += shapeEnd;
          continue;
        }

        // Currently drawing this shape
        if (localTime < drawTime) {
          const verticesPlaced = Math.min(
            Math.floor(localTime / msPerVertex),
            shape.points.length,
          );
          drawShape(shape, verticesPlaced, 0);

          // Cursor pulse on current vertex
          if (verticesPlaced < shape.points.length) {
            const withinVertex = localTime - verticesPlaced * msPerVertex;
            const pulse = Math.sin((withinVertex / msPerVertex) * Math.PI);
            const [cx, cy] = shape.points[verticesPlaced];
            ctx.beginPath();
            ctx.arc(cx, cy, 10 + pulse * 3, 0, Math.PI * 2);
            ctx.strokeStyle = shape.stroke;
            ctx.globalAlpha = 0.3 + pulse * 0.2;
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.globalAlpha = 1;
          }
        } else {
          // In fill phase
          const fillElapsed = localTime - drawTime;
          const fillProgress = Math.min(fillElapsed / msFill, 1);
          drawShape(shape, shape.points.length, fillProgress);
        }
        break; // only one shape is "active" at a time
      }

      raf = requestAnimationFrame(render);
    };

    raf = requestAnimationFrame(render);
    return () => cancelAnimationFrame(raf);
  }, [canvasRef, config]);
}

function StepAnimation({ type }: { type: TourStep['animation'] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const config: DrawConfig | null = type === 'draw-boundary' ? {
    shapes: [{
      points: [[60,120],[100,25],[240,18],[340,55],[320,130],[160,140]],
      closed: true,
      stroke: '#f59e0b',
      fill: '#f59e0b',
    }],
    msPerVertex: 770,
    msFill: 660,
    msPause: 1300,
  } : type === 'draw-road' ? {
    shapes: [{
      points: [[70,110],[140,65],[240,75],[330,45]],
      closed: false,
      stroke: '#4b5563',
      fill: '#4b5563',
    }],
    msPerVertex: 770,
    msFill: 0,
    msPause: 1650,
  } : type === 'place-building' ? {
    shapes: [
      {
        points: [[55,30],[165,30],[165,100],[55,100]],
        closed: true,
        stroke: '#8b5cf6',
        fill: '#8b5cf6',
      },
      {
        points: [[230,45],[340,45],[340,110],[230,110]],
        closed: true,
        stroke: '#8b5cf6',
        fill: '#8b5cf6',
      },
    ],
    msPerVertex: 770,
    msFill: 660,
    msPause: 1300,
  } : null;

  useDrawAnimation(canvasRef, config ?? {
    shapes: [],
    msPerVertex: 770, msFill: 0, msPause: 0,
  });

  if (!type) return null;

  const common = 'w-full h-24 rounded-lg bg-primary-950/5 overflow-hidden';

  // Canvas-based animations for boundary, road, building
  if (type === 'draw-boundary' || type === 'draw-road' || type === 'place-building') {
    return (
      <div className={common}>
        <canvas ref={canvasRef} className="h-full w-full" />
      </div>
    );
  }

  // AI Render: SVG sparkle effect (no drawing needed)
  if (type === 'ai-render') {
    return (
      <div className={common}>
        <svg viewBox="0 0 200 80" className="h-full w-full">
          <polygon points="20,65 40,12 130,8 180,28 170,68 70,72" fill="#f59e0b" opacity="0.08" stroke="#f59e0b" strokeWidth="1" strokeDasharray="4,3" />
          {/* Road running through the middle */}
          <polyline points="35,40 75,38 130,40 175,36" fill="none" stroke="#4b5563" strokeWidth="3" strokeLinecap="round" opacity="0.35" />
          {/* Buildings above the road */}
          <rect x="58" y="16" width="28" height="18" rx="2" fill="#8b5cf6" opacity="0.35" />
          <rect x="108" y="14" width="32" height="20" rx="2" fill="#8b5cf6" opacity="0.35" />
          {/* Buildings below the road */}
          <rect x="65" y="48" width="25" height="16" rx="2" fill="#8b5cf6" opacity="0.35" />
          <rect x="115" y="46" width="30" height="18" rx="2" fill="#8b5cf6" opacity="0.35" />
          <g opacity="0">
            <animate attributeName="opacity" values="0;1;1;0" dur="2.5s" repeatCount="indefinite" begin="0.5s" />
            <circle cx="100" cy="40" r="2" fill="#818cf8">
              <animate attributeName="r" values="2;25;30" dur="2s" repeatCount="indefinite" begin="0.5s" />
              <animate attributeName="opacity" values="0.6;0.15;0" dur="2s" repeatCount="indefinite" begin="0.5s" />
            </circle>
            <line x1="100" y1="25" x2="100" y2="15" stroke="#818cf8" strokeWidth="2" strokeLinecap="round">
              <animate attributeName="y2" values="25;10" dur="1s" repeatCount="indefinite" begin="0.8s" />
              <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="0.8s" />
            </line>
            <line x1="115" y1="30" x2="125" y2="22" stroke="#818cf8" strokeWidth="2" strokeLinecap="round">
              <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="1s" />
            </line>
            <line x1="85" y1="30" x2="75" y2="22" stroke="#818cf8" strokeWidth="2" strokeLinecap="round">
              <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="1.2s" />
            </line>
          </g>
        </svg>
      </div>
    );
  }

  return null;
}

// ---------------------------------------------------------------------------
// Spotlight overlay — dims everything except the target rect
// Uses a fixed-position SVG with mask so scrolling doesn't affect it
// ---------------------------------------------------------------------------

function SpotlightOverlay({ rect }: { rect: DOMRect | null }) {
  if (!rect) {
    return <div className="fixed inset-0 z-[998] bg-black/50 transition-opacity duration-300" />;
  }

  const pad = 8;
  const r = 12;
  const x = rect.left - pad;
  const y = rect.top - pad;
  const w = rect.width + pad * 2;
  const h = rect.height + pad * 2;

  return (
    <svg
      className="fixed inset-0 z-[998] transition-all duration-300"
      width="100%"
      height="100%"
      style={{ pointerEvents: 'none' }}
    >
      <defs>
        <mask id="tour-mask">
          <rect x="0" y="0" width="100%" height="100%" fill="white" />
          <rect x={x} y={y} width={w} height={h} rx={r} fill="black" />
        </mask>
      </defs>
      <rect x="0" y="0" width="100%" height="100%" fill="rgba(0,0,0,0.55)" mask="url(#tour-mask)" />
      {/* Glow ring */}
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={r}
        fill="none"
        stroke="rgba(245,158,11,0.5)"
        strokeWidth="2"
        className="animate-pulse"
      />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Click blocker — prevents clicks passing through the overlay except on
// the spotlighted element area
// ---------------------------------------------------------------------------

function ClickBlocker({ rect }: { rect: DOMRect | null }) {
  const handleClick = useCallback((e: React.MouseEvent) => {
    // If clicking inside the spotlight hole, let it through
    if (rect) {
      const pad = 8;
      const x = rect.left - pad;
      const y = rect.top - pad;
      const w = rect.width + pad * 2;
      const h = rect.height + pad * 2;
      if (e.clientX >= x && e.clientX <= x + w && e.clientY >= y && e.clientY <= y + h) {
        return; // allow
      }
    }
    e.stopPropagation();
    e.preventDefault();
  }, [rect]);

  return (
    <div
      className="fixed inset-0 z-[998]"
      onClick={handleClick}
    />
  );
}

// ---------------------------------------------------------------------------
// Tooltip card
// ---------------------------------------------------------------------------

interface TooltipProps {
  step: TourStep;
  stepIndex: number;
  total: number;
  targetRect: DOMRect | null;
  onNext: () => void;
  onSkip: () => void;
}

function TourTooltip({ step, stepIndex, total, targetRect, onNext, onSkip }: TooltipProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });

  useLayoutEffect(() => {
    if (!targetRect || !ref.current) return;
    const card = ref.current.getBoundingClientRect();
    const pad = 16;

    let top = 0;
    let left = targetRect.left + targetRect.width / 2 - card.width / 2;

    const placement = step.placement ?? 'top';
    if (placement === 'top') {
      top = targetRect.top - card.height - pad;
      // If not enough room above, go below
      if (top < 12) top = targetRect.bottom + pad;
    } else {
      top = targetRect.bottom + pad;
      // If not enough room below, go above
      if (top + card.height > window.innerHeight - 12) {
        top = targetRect.top - card.height - pad;
      }
    }

    // Clamp to viewport
    left = Math.max(12, Math.min(left, window.innerWidth - card.width - 12));
    top = Math.max(12, Math.min(top, window.innerHeight - card.height - 12));

    setPos({ top, left });
  }, [targetRect, step.placement, stepIndex]);

  const isLast = stepIndex === total - 1;

  return (
    <div
      ref={ref}
      className="fixed z-[999] w-80 rounded-xl bg-white shadow-2xl ring-1 ring-black/5 transition-all duration-300"
      style={{ top: pos.top, left: pos.left }}
    >
      {/* Step animation */}
      {step.animation && (
        <div className="px-4 pt-4">
          <StepAnimation type={step.animation} />
        </div>
      )}

      <div className="px-4 pt-3 pb-4">
        {/* Step counter */}
        <div className="mb-1 flex items-center gap-2">
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white">
            {stepIndex + 1}
          </span>
          <span className="text-[11px] font-medium text-primary-950/40">
            Step {stepIndex + 1} of {total}
          </span>
        </div>

        <h3 className="text-sm font-bold text-primary-950">{step.title}</h3>
        <p className="mt-1 text-xs leading-relaxed text-primary-950/60">{step.body}</p>

        {/* Progress dots */}
        <div className="mt-3 flex items-center gap-1">
          {Array.from({ length: total }).map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === stepIndex ? 'w-6 bg-amber-500' : i < stepIndex ? 'w-1.5 bg-amber-500/40' : 'w-1.5 bg-primary-950/10'
              }`}
            />
          ))}
        </div>

        {/* Buttons */}
        <div className="mt-3 flex items-center justify-between">
          <button
            onClick={onSkip}
            className="text-xs font-medium text-primary-950/40 hover:text-primary-950/70 transition"
          >
            Skip tour
          </button>
          <button
            onClick={onNext}
            className="rounded-lg bg-amber-500 px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-amber-400 transition"
          >
            {isLast ? 'Get Started' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main OnboardingTour component
// ---------------------------------------------------------------------------

const STORAGE_KEY = 'onboarding-tour-completed';

interface OnboardingTourProps {
  /** Force-show even if previously dismissed */
  forceShow?: boolean;
  onComplete?: () => void;
}

export function OnboardingTour({ forceShow, onComplete }: OnboardingTourProps) {
  const [active, setActive] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const rafRef = useRef<number>(0);

  // Show tour on mount if not completed, or when forceShow changes
  useEffect(() => {
    if (forceShow) {
      setActive(true);
      setStepIndex(0);
      return;
    }
    try {
      if (localStorage.getItem(STORAGE_KEY) !== 'true') {
        const t = setTimeout(() => setActive(true), 800);
        return () => clearTimeout(t);
      }
    } catch {
      // ignore
    }
  }, [forceShow]);

  // Continuously track the target element position via rAF so the
  // spotlight stays locked to the button even when scrolling
  useEffect(() => {
    if (!active) return;

    const step = STEPS[stepIndex];
    if (!step) return;

    const track = () => {
      const el = document.querySelector(step.target);
      if (el) {
        const r = el.getBoundingClientRect();
        setTargetRect((prev) => {
          // Only update state if the rect actually changed to avoid re-renders
          if (
            prev &&
            Math.abs(prev.top - r.top) < 0.5 &&
            Math.abs(prev.left - r.left) < 0.5 &&
            Math.abs(prev.width - r.width) < 0.5 &&
            Math.abs(prev.height - r.height) < 0.5
          ) {
            return prev;
          }
          return r;
        });
      } else {
        setTargetRect(null);
      }
      rafRef.current = requestAnimationFrame(track);
    };

    rafRef.current = requestAnimationFrame(track);
    return () => cancelAnimationFrame(rafRef.current);
  }, [active, stepIndex]);

  const dismiss = useCallback(() => {
    setActive(false);
    try {
      localStorage.setItem(STORAGE_KEY, 'true');
    } catch {
      // ignore
    }
    onComplete?.();
  }, [onComplete]);

  const handleNext = useCallback(() => {
    if (stepIndex < STEPS.length - 1) {
      setStepIndex((i) => i + 1);
    } else {
      dismiss();
    }
  }, [stepIndex, dismiss]);

  // Keyboard: Escape to skip, Enter/Arrow-Right to advance
  useEffect(() => {
    if (!active) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') dismiss();
      if (e.key === 'Enter' || e.key === 'ArrowRight') handleNext();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [active, dismiss, handleNext]);

  if (!active) return null;

  // Render via portal to document.body so that position:fixed works correctly
  // even when parent elements have CSS transforms (e.g. Mapbox containers)
  return createPortal(
    <>
      <SpotlightOverlay rect={targetRect} />
      <ClickBlocker rect={targetRect} />
      <TourTooltip
        step={STEPS[stepIndex]}
        stepIndex={stepIndex}
        total={STEPS.length}
        targetRect={targetRect}
        onNext={handleNext}
        onSkip={dismiss}
      />
    </>,
    document.body,
  );
}
