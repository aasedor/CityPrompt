import { useState, useEffect, useCallback, useRef, useLayoutEffect, useMemo } from 'react';
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
    target: '[data-tour="tool-buildings"]',
    title: 'Start with one building',
    body: 'Choose Building and click at least 3 corners on the map. Press Enter or double-click to finish. On a phone, move the map under the crosshair, place points, then tap Finish. Try this after closing the guide.',
    animation: 'place-building',
    placement: 'top',
  },
  {
    target: '[data-tour="tool-parksPlazas"]',
    title: 'Add a park',
    body: 'Choose Park and draw an outline the same way. Leave room for people to walk, gather and play. Backspace removes the last point while drawing; Escape clears an unfinished drawing.',
    animation: 'draw-boundary',
    placement: 'top',
  },
  {
    target: '[data-tour="tool-streetsPaths"]',
    title: 'Connect places with a road',
    body: 'Choose Road and click at least 2 points along its route. Each click adds a bend. Press Enter or double-click to finish, then use Select to change the street or path settings.',
    animation: 'draw-road',
    placement: 'top',
  },
  {
    target: '[data-tour="select-btn"]',
    title: 'Make it yours',
    body: 'Choose Select, then click a drawing to edit its settings. Try a different building type or number of floors. Undo and Redo help you explore. More Tools holds optional site boundaries, measuring and other drawing tools.',
    placement: 'top',
  },
  {
    target: '[data-tour="generate-3d-btn"]',
    title: 'Build your 3D scene',
    body: 'When your drawings are ready, choose Generate 3D. Review the scene from different angles. If you change a drawing afterward, generate the scene again before making your final image.',
    placement: 'top',
  },
  {
    target: '[data-tour="ai-render-btn"]',
    title: 'Create a presentation image',
    body: 'Choose AI Render after generating 3D, then review the image settings before starting. Check the result against your design before presenting it. Start small: one building, one park and one road. Reopen this guide from Help whenever you need it.',
    animation: 'ai-render',
    placement: 'top',
  },
];

const PLACEMENT_STEPS: TourStep[] = [
  {target:'[data-tour="place-infill_home"]',title:'Pick and place a home',body:'Open Buildings, choose Infill homes from the catalogue, then move the preview over an empty part of your site, then click to place it. On a phone, move the map under the crosshair and tap Place at centre. Red means the object does not fit there.',placement:'right'},
  {target:'[data-tour="place-neighbourhood_park"]',title:'Make room for a park',body:'Open Parks, choose Neighbourhood park, and place it beside your homes. The park appears in 3D automatically. Keep some space for streets and connections.',placement:'right'},
  {target:'[data-tour="select-btn"]',title:'Reshape your ideas',body:'Select an object. Drag its body to move, a white corner to resize, or the orange handle to rotate. You can also enter dimensions in the side panel. A wider home plot fits more whole houses; a park rearranges its paths and equipment.',placement:'right'},
  {target:'[data-tour="tool-streetsPaths"]',title:'Connect the places',body:'Choose Road, click at least two points along the route, then press Enter. Roads update in 3D automatically. More Tools contains custom outlines and optional planning tools.',placement:'right'},
  {target:'[data-tour="ai-render-btn"]',title:'Present your community',body:'Once your objects have saved and 3D has updated, choose Render. Review your image settings before starting. Undo and Redo let you explore alternatives; your placed objects remain in the saved project.',placement:'right'},
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

  const config: DrawConfig | null = useMemo(() => type === 'draw-boundary' ? {
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
  } : null, [type]);

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

interface TooltipProps {
  step: TourStep;
  stepIndex: number;
  total: number;
  targetRect: DOMRect | null;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}
function TourTooltip({ step, stepIndex, total, targetRect, onNext, onBack, onSkip }: TooltipProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ top: 12, left: 12 });
  const [reducedMotion, setReducedMotion] = useState(() => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false);
  useEffect(() => {
    const media = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    const update = () => setReducedMotion(Boolean(media?.matches));
    media?.addEventListener?.('change', update);
    return () => media?.removeEventListener?.('change', update);
  }, []);
  useLayoutEffect(() => {
    const card = ref.current?.getBoundingClientRect();
    if (!card) return;
    const pad = 16;
    let left = (window.innerWidth - card.width) / 2;
    let top = (window.innerHeight - card.height) / 2;
    if (targetRect) {
      left = targetRect.left + targetRect.width / 2 - card.width / 2;
      top = targetRect.top - card.height - pad;
      if (top < 12) top = targetRect.bottom + pad;
    }
    setPos({
      left: Math.max(12, Math.min(left, window.innerWidth - card.width - 12)),
      top: Math.max(12, Math.min(top, window.innerHeight - card.height - 12)),
    });
  }, [targetRect, stepIndex, reducedMotion]);
  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    ref.current?.focus();
    return () => previous?.focus();
  }, []);
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      // The guide is a modal: its keys must not finish drawings or trigger map shortcuts.
      event.stopImmediatePropagation();
      if (event.key === 'Escape') { event.preventDefault(); onSkip(); }
      else if (event.key === 'ArrowRight') { event.preventDefault(); onNext(); }
      else if (event.key === 'ArrowLeft') { event.preventDefault(); onBack(); }
      else if (event.key === 'Tab') {
        const buttons = [...(ref.current?.querySelectorAll<HTMLButtonElement>('button:not(:disabled)') ?? [])];
        const first = buttons[0];
        const last = buttons[buttons.length - 1];
        if (!first) { event.preventDefault(); return; }
        if (event.shiftKey && (document.activeElement === first || document.activeElement === ref.current)) {
          event.preventDefault(); last.focus();
        } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === ref.current)) {
          event.preventDefault(); first.focus();
        } else if (!ref.current?.contains(document.activeElement)) {
          event.preventDefault(); first.focus();
        }
      }
      // Enter/Space retain native button behavior, so Back never also advances.
    };
    window.addEventListener('keydown', handler, true);
    return () => window.removeEventListener('keydown', handler, true);
  }, [onNext, onBack, onSkip]);

  const buttonClass = 'min-h-11 rounded-lg px-3 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900';
  return <div ref={ref} role="dialog" aria-modal="true" aria-labelledby="cityprompt-tour-title"
    aria-describedby="cityprompt-tour-body" tabIndex={-1}
    className="fixed z-[999] max-h-[calc(100dvh-24px)] w-96 max-w-[calc(100vw-24px)] overflow-y-auto rounded-xl bg-white text-slate-900 shadow-2xl outline-none"
    style={{ top: pos.top, left: pos.left }}>
    {step.animation && !reducedMotion && <div aria-hidden className="px-5 pt-4"><StepAnimation type={step.animation} /></div>}
    <div className="p-5">
      <p className="text-sm font-semibold text-slate-600" aria-live="polite">Quick guide · Step {stepIndex + 1} of {total}</p>
      <h2 id="cityprompt-tour-title" className="mt-2 text-xl font-bold">{step.title}</h2>
      <p id="cityprompt-tour-body" className="mt-2 text-base leading-relaxed text-slate-700">{step.body}</p>
      <p className="mt-3 text-xs text-slate-500">Close the guide to try it. Nothing is generated during this guide.</p>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
        <button type="button" onClick={onSkip} className={buttonClass + ' text-slate-700 hover:bg-slate-100'}>Close guide</button>
        <div className="flex gap-2">
          <button type="button" disabled={stepIndex === 0} onClick={onBack} className={buttonClass + ' border border-slate-300 disabled:opacity-40 hover:bg-slate-100'}>Back</button>
          <button type="button" onClick={onNext} className={buttonClass + ' bg-slate-900 text-white hover:bg-slate-700'}>{stepIndex === total - 1 ? 'Start drawing' : 'Next'}</button>
        </div>
      </div>
    </div>
  </div>;
}

const STORAGE_KEY = 'onboarding-tour-completed';
interface OnboardingTourProps {
  placementMode?: boolean;
  /** Force-show even if previously dismissed; false keeps the guide closed. */
  forceShow?: boolean;
  onComplete?: () => void;
}
export function OnboardingTour({ forceShow, onComplete, placementMode = false }: OnboardingTourProps) {
  const steps = placementMode ? PLACEMENT_STEPS : STEPS;
  const [active, setActive] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const rafRef = useRef<number>(0);
  useEffect(() => {
    if (forceShow === false) { setActive(false); return; }
    if (forceShow) { setActive(true); setStepIndex(0); return; }
    try {
      if (localStorage.getItem(STORAGE_KEY) !== 'true') {
        const timer = setTimeout(() => setActive(true), 800);
        return () => clearTimeout(timer);
      }
    } catch { /* Help can still open the guide when browser storage is unavailable. */ }
  }, [forceShow]);
  useEffect(() => {
    if (!active) return;
    const step = steps[stepIndex];
    document.querySelector(step.target)?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
    const track = () => {
      const element = document.querySelector(step.target);
      const rect = element?.getBoundingClientRect();
      const visible = rect && rect.width > 0 && rect.height > 0 ? rect : null;
      setTargetRect((previous) => {
        if (previous && visible && Math.abs(previous.top - visible.top) < 0.5 &&
          Math.abs(previous.left - visible.left) < 0.5 && Math.abs(previous.width - visible.width) < 0.5 &&
          Math.abs(previous.height - visible.height) < 0.5) return previous;
        return visible;
      });
      rafRef.current = requestAnimationFrame(track);
    };
    track();
    return () => cancelAnimationFrame(rafRef.current);
  }, [active, stepIndex, steps]);
  const dismiss = useCallback(() => {
    setActive(false);
    try { localStorage.setItem(STORAGE_KEY, 'true'); } catch { /* optional preference */ }
    onComplete?.();
  }, [onComplete]);
  const handleNext = useCallback(() => {
    if (stepIndex < steps.length - 1) setStepIndex((index) => index + 1);
    else dismiss();
  }, [stepIndex, dismiss, steps]);
  const handleBack = useCallback(() => setStepIndex((index) => Math.max(0, index - 1)), []);
  if (!active) return null;
  return createPortal(<>
    <SpotlightOverlay rect={targetRect} />
    <div aria-hidden className="fixed inset-0 z-[998]" />
    <TourTooltip step={steps[stepIndex]} stepIndex={stepIndex} total={steps.length}
      targetRect={targetRect} onNext={handleNext} onBack={handleBack} onSkip={dismiss} />
  </>, document.body);
}
