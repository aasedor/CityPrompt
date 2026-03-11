import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Box, ArrowRight, Sparkles, ChevronDown } from 'lucide-react';
import { useAuthStore } from '@/store';

/* ------------------------------------------------------------------ */
/*  Scroll-reveal hook — fades/slides elements in when they enter view */
/* ------------------------------------------------------------------ */
function useScrollReveal(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return { ref, visible };
}

function RevealSection({
  children,
  className = '',
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const { ref, visible } = useScrollReveal(0.12);
  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
      } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Step progress dots (side rail)                                     */
/* ------------------------------------------------------------------ */
const STEP_IDS = ['hero', 'step-map', 'step-zones', 'step-ai', 'step-3d', 'step-share', 'cta'];

function StepDots() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const observers: IntersectionObserver[] = [];

    STEP_IDS.forEach((id, i) => {
      const el = document.getElementById(id);
      if (!el) return;
      const obs = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setActive(i); },
        { threshold: 0.4 },
      );
      obs.observe(el);
      observers.push(obs);
    });

    return () => observers.forEach((o) => o.disconnect());
  }, []);

  return (
    <div className="fixed right-6 top-1/2 z-40 hidden -translate-y-1/2 flex-col gap-3 lg:flex">
      {STEP_IDS.map((id, i) => (
        <button
          key={id}
          onClick={() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })}
          className={`h-2.5 w-2.5 rounded-full transition-all duration-300 ${
            i === active
              ? 'scale-125 bg-coral-500 shadow-lg shadow-coral-500/40'
              : 'bg-primary-950/15 hover:bg-primary-950/30'
          }`}
          aria-label={`Go to section ${i + 1}`}
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  SVG illustrations for each teaching step                          */
/* ------------------------------------------------------------------ */

function MapIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Satellite map bg */}
      <rect x="40" y="30" width="400" height="300" rx="16" fill="#e8f4ec" stroke="#79d3c5" strokeWidth="1.5" />
      {/* Terrain patches */}
      <rect x="60" y="60" width="140" height="90" rx="8" fill="#c8e6c9" opacity="0.6" />
      <rect x="220" y="80" width="120" height="110" rx="8" fill="#a5d6a7" opacity="0.5" />
      <rect x="360" y="50" width="60" height="60" rx="8" fill="#81c784" opacity="0.4" />
      {/* Roads */}
      <line x1="40" y1="200" x2="440" y2="200" stroke="#bdbdbd" strokeWidth="3" strokeDasharray="8 4" />
      <line x1="240" y1="30" x2="240" y2="330" stroke="#bdbdbd" strokeWidth="3" strokeDasharray="8 4" />
      {/* Map pin */}
      <g className="animate-bounce-gentle">
        <path d="M240,140 C240,120 260,105 260,85 C260,70 250,60 240,60 C230,60 220,70 220,85 C220,105 240,120 240,140Z" fill="#f14a72" />
        <circle cx="240" cy="82" r="8" fill="white" opacity="0.8" />
      </g>
      {/* Cursor */}
      <g className="animate-float" style={{ animationDelay: '0.5s' }}>
        <path d="M320,250 L330,280 L337,268 L350,275 L345,265 L358,262 L320,250Z" fill="#1d1b4f" stroke="#fefaf7" strokeWidth="1.5" />
      </g>
      {/* Zoom controls */}
      <rect x="380" y="240" width="40" height="70" rx="8" fill="white" stroke="#e0e0e0" strokeWidth="1" />
      <line x1="392" y1="265" x2="408" y2="265" stroke="#9e9e9e" strokeWidth="2" />
      <line x1="400" y1="257" x2="400" y2="273" stroke="#9e9e9e" strokeWidth="2" />
      <line x1="392" y1="290" x2="408" y2="290" stroke="#9e9e9e" strokeWidth="2" />
    </svg>
  );
}

function ZoneIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Map background */}
      <rect x="40" y="30" width="400" height="300" rx="16" fill="#f0f4f8" stroke="#4496d5" strokeWidth="1.5" opacity="0.6" />
      {/* Residential zone */}
      <g>
        <rect x="60" y="60" width="160" height="120" rx="8" fill="#00a8ba" opacity="0.15" stroke="#00a8ba" strokeWidth="2" strokeDasharray="6 3" />
        <rect x="70" y="72" width="80" height="18" rx="4" fill="#00a8ba" opacity="0.8" />
        <text x="80" y="85" fill="white" fontSize="10" fontWeight="600">Residential</text>
      </g>
      {/* Commercial zone */}
      <g>
        <rect x="250" y="50" width="170" height="100" rx="8" fill="#f14a72" opacity="0.15" stroke="#f14a72" strokeWidth="2" strokeDasharray="6 3" />
        <rect x="260" y="62" width="80" height="18" rx="4" fill="#f14a72" opacity="0.8" />
        <text x="268" y="75" fill="white" fontSize="10" fontWeight="600">Commercial</text>
      </g>
      {/* Mixed-use zone */}
      <g>
        <rect x="80" y="210" width="200" height="100" rx="8" fill="#f4c25f" opacity="0.15" stroke="#f4c25f" strokeWidth="2" strokeDasharray="6 3" />
        <rect x="90" y="222" width="72" height="18" rx="4" fill="#f4c25f" opacity="0.85" />
        <text x="98" y="235" fill="white" fontSize="10" fontWeight="600">Mixed-Use</text>
      </g>
      {/* Config panel */}
      <g className="animate-float" style={{ animationDelay: '1s' }}>
        <rect x="320" y="190" width="130" height="120" rx="10" fill="white" stroke="#e0e0e0" strokeWidth="1" />
        <text x="335" y="212" fill="#1d1b4f" fontSize="10" fontWeight="600">Zone Settings</text>
        <line x1="330" y1="220" x2="440" y2="220" stroke="#f0f0f0" strokeWidth="1" />
        <text x="335" y="238" fill="#9e9e9e" fontSize="9">Type</text>
        <rect x="335" y="242" width="95" height="14" rx="3" fill="#f0f4f8" />
        <text x="335" y="262" fill="#9e9e9e" fontSize="9">Density</text>
        <rect x="335" y="266" width="70" height="6" rx="3" fill="#00a8ba" opacity="0.5" />
        <circle cx="405" cy="269" r="5" fill="#00a8ba" />
        <text x="335" y="288" fill="#9e9e9e" fontSize="9">Max Height</text>
        <rect x="335" y="292" width="50" height="6" rx="3" fill="#f14a72" opacity="0.5" />
        <circle cx="385" cy="295" r="5" fill="#f14a72" />
      </g>
    </svg>
  );
}

function AIIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Background glow */}
      <circle cx="240" cy="180" r="140" fill="url(#aiGlow)" opacity="0.2" />
      {/* Flat zone outline */}
      <rect x="100" y="220" width="120" height="80" rx="4" fill="#00a8ba" opacity="0.1" stroke="#00a8ba" strokeWidth="1.5" strokeDasharray="4 2" />
      {/* Arrow from zone to building */}
      <g className="animate-glow-pulse">
        <path d="M230,260 L270,220" stroke="url(#aiArrowGrad)" strokeWidth="2.5" strokeLinecap="round" />
        <polygon points="272,216 278,224 268,222" fill="#f14a72" />
        {/* Sparkles around arrow */}
        <circle cx="250" cy="235" r="3" fill="#f4c25f" opacity="0.7" />
        <circle cx="260" cy="245" r="2" fill="#79d3c5" opacity="0.6" />
        <circle cx="242" cy="248" r="2.5" fill="#f14a72" opacity="0.5" />
      </g>
      {/* Generated building - isometric */}
      <g className="animate-pop-in" style={{ animationDelay: '0.3s', opacity: 0 }}>
        <polygon points="310,200 370,170 370,100 310,130" fill="#4496d5" opacity="0.8" />
        <polygon points="370,170 430,200 430,130 370,100" fill="#3578b0" opacity="0.8" />
        <polygon points="310,130 370,100 430,130 370,160" fill="#79d3c5" opacity="0.6" />
        {/* Windows */}
        <rect x="325" y="142" width="12" height="14" rx="1" fill="#fefaf7" opacity="0.4" />
        <rect x="345" y="142" width="12" height="14" rx="1" fill="#fefaf7" opacity="0.4" />
        <rect x="325" y="168" width="12" height="14" rx="1" fill="#fefaf7" opacity="0.4" />
        <rect x="345" y="168" width="12" height="14" rx="1" fill="#fefaf7" opacity="0.4" />
      </g>
      {/* Second building */}
      <g className="animate-pop-in" style={{ animationDelay: '0.8s', opacity: 0 }}>
        <polygon points="100,180 140,165 140,110 100,125" fill="#f14a72" opacity="0.7" />
        <polygon points="140,165 180,180 180,125 140,110" fill="#d93d63" opacity="0.7" />
        <polygon points="100,125 140,110 180,125 140,140" fill="#f47090" opacity="0.5" />
      </g>
      {/* AI brain icon */}
      <g className="animate-float-slow">
        <circle cx="240" cy="80" r="28" fill="white" stroke="#f14a72" strokeWidth="1.5" />
        <path d="M228,72 Q228,65 235,65 L245,65 Q252,65 252,72 L252,82 Q252,89 245,89 L235,89 Q228,89 228,82Z" fill="none" stroke="#f14a72" strokeWidth="1.5" />
        <circle cx="236" cy="76" r="2" fill="#f14a72" />
        <circle cx="244" cy="76" r="2" fill="#f14a72" />
        <path d="M234,83 Q240,87 246,83" stroke="#f14a72" strokeWidth="1.2" fill="none" strokeLinecap="round" />
        <line x1="240" y1="58" x2="240" y2="52" stroke="#f4c25f" strokeWidth="1.5" strokeLinecap="round" />
        <line x1="255" y1="63" x2="260" y2="58" stroke="#f4c25f" strokeWidth="1.5" strokeLinecap="round" />
        <line x1="225" y1="63" x2="220" y2="58" stroke="#f4c25f" strokeWidth="1.5" strokeLinecap="round" />
      </g>
      <defs>
        <radialGradient id="aiGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f14a72" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#fefaf7" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="aiArrowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#00a8ba" />
          <stop offset="100%" stopColor="#f14a72" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function ViewerIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Browser frame */}
      <rect x="40" y="30" width="400" height="300" rx="12" fill="#1d1b4f" stroke="#481c5f" strokeWidth="1.5" />
      {/* Title bar */}
      <rect x="40" y="30" width="400" height="28" rx="12" fill="#28184d" />
      <circle cx="62" cy="44" r="5" fill="#f14a72" opacity="0.7" />
      <circle cx="78" cy="44" r="5" fill="#f4c25f" opacity="0.7" />
      <circle cx="94" cy="44" r="5" fill="#79d3c5" opacity="0.7" />
      {/* Scene viewport */}
      <rect x="48" y="62" width="384" height="260" rx="4" fill="#0d0b2e" />
      {/* Ground plane */}
      <polygon points="48,300 240,240 432,300 432,322 48,322" fill="#1a1548" opacity="0.8" />
      {/* Grid lines on ground */}
      <line x1="100" y1="290" x2="200" y2="255" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
      <line x1="160" y1="300" x2="260" y2="248" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
      <line x1="220" y1="310" x2="320" y2="255" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
      <line x1="280" y1="310" x2="380" y2="268" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
      {/* Building 1 */}
      <polygon points="140,260 190,240 190,160 140,180" fill="#4496d5" opacity="0.9" />
      <polygon points="190,240 240,260 240,180 190,160" fill="#3578b0" opacity="0.9" />
      <polygon points="140,180 190,160 240,180 190,200" fill="#79d3c5" opacity="0.7" />
      {/* Building 1 windows */}
      <rect x="152" y="195" width="10" height="12" fill="#ffd56e" opacity="0.5" />
      <rect x="170" y="195" width="10" height="12" fill="#ffd56e" opacity="0.3" />
      <rect x="152" y="218" width="10" height="12" fill="#ffd56e" opacity="0.6" />
      <rect x="170" y="218" width="10" height="12" fill="#ffd56e" opacity="0.4" />
      {/* Building 2 */}
      <polygon points="280,270 320,255 320,190 280,205" fill="#f14a72" opacity="0.8" />
      <polygon points="320,255 360,270 360,205 320,190" fill="#d93d63" opacity="0.8" />
      <polygon points="280,205 320,190 360,205 320,220" fill="#f47090" opacity="0.6" />
      {/* Sun/light */}
      <circle cx="380" cy="100" r="20" fill="#f4c25f" opacity="0.8" className="animate-glow-pulse" />
      <circle cx="380" cy="100" r="30" fill="#f4c25f" opacity="0.15" />
      {/* Light rays */}
      <line x1="380" y1="70" x2="380" y2="60" stroke="#ffd56e" strokeWidth="1.5" opacity="0.4" strokeLinecap="round" />
      <line x1="405" y1="80" x2="415" y2="74" stroke="#ffd56e" strokeWidth="1.5" opacity="0.4" strokeLinecap="round" />
      <line x1="355" y1="80" x2="345" y2="74" stroke="#ffd56e" strokeWidth="1.5" opacity="0.4" strokeLinecap="round" />
      {/* Time-of-day slider */}
      <g className="animate-float" style={{ animationDelay: '0.5s' }}>
        <rect x="140" y="85" width="160" height="24" rx="12" fill="white" opacity="0.1" />
        <circle cx="260" cy="97" r="8" fill="#f4c25f" opacity="0.9" />
        <text x="158" y="101" fill="white" opacity="0.5" fontSize="8">6am</text>
        <text x="275" y="101" fill="white" opacity="0.5" fontSize="8">6pm</text>
      </g>
    </svg>
  );
}

function ShareIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Central project card */}
      <rect x="160" y="100" width="160" height="160" rx="16" fill="white" stroke="#e0e0e0" strokeWidth="1.5" />
      <rect x="170" y="110" width="140" height="80" rx="8" fill="#f0f4f8" />
      {/* Mini 3D scene in card */}
      <polygon points="210,170 240,155 240,130 210,145" fill="#4496d5" opacity="0.6" />
      <polygon points="240,155 270,170 270,145 240,130" fill="#3578b0" opacity="0.6" />
      <polygon points="210,145 240,130 270,145 240,158" fill="#79d3c5" opacity="0.4" />
      <text x="180" y="210" fill="#1d1b4f" fontSize="11" fontWeight="600">Downtown Project</text>
      <text x="180" y="225" fill="#9e9e9e" fontSize="9">3 zones · 12 buildings</text>
      {/* Share button */}
      <rect x="180" y="235" width="60" height="18" rx="9" fill="#00a8ba" opacity="0.15" />
      <text x="192" y="247" fill="#00a8ba" fontSize="9" fontWeight="600">Share</text>
      {/* User avatars - left */}
      <g className="animate-float" style={{ animationDelay: '0s' }}>
        <circle cx="80" cy="140" r="24" fill="#fdb27a" opacity="0.2" stroke="#fdb27a" strokeWidth="1.5" />
        <circle cx="80" cy="134" r="8" fill="#fdb27a" />
        <path d="M64,158 Q64,148 80,148 Q96,148 96,158" fill="#fdb27a" opacity="0.6" />
        <text x="62" y="178" fill="#9e9e9e" fontSize="8" textAnchor="start">Architect</text>
      </g>
      {/* Connection line left */}
      <line x1="104" y1="140" x2="155" y2="170" stroke="#fdb27a" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
      {/* User avatars - right */}
      <g className="animate-float" style={{ animationDelay: '1s' }}>
        <circle cx="400" cy="140" r="24" fill="#4496d5" opacity="0.2" stroke="#4496d5" strokeWidth="1.5" />
        <circle cx="400" cy="134" r="8" fill="#4496d5" />
        <path d="M384,158 Q384,148 400,148 Q416,148 416,158" fill="#4496d5" opacity="0.6" />
        <text x="385" y="178" fill="#9e9e9e" fontSize="8" textAnchor="start">Client</text>
      </g>
      {/* Connection line right */}
      <line x1="376" y1="140" x2="325" y2="170" stroke="#4496d5" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
      {/* User avatar - bottom */}
      <g className="animate-float" style={{ animationDelay: '0.5s' }}>
        <circle cx="240" cy="310" r="24" fill="#f14a72" opacity="0.2" stroke="#f14a72" strokeWidth="1.5" />
        <circle cx="240" cy="304" r="8" fill="#f14a72" />
        <path d="M224,328 Q224,318 240,318 Q256,318 256,328" fill="#f14a72" opacity="0.6" />
        <text x="222" y="348" fill="#9e9e9e" fontSize="8" textAnchor="start">Planner</text>
      </g>
      {/* Connection line bottom */}
      <line x1="240" y1="286" x2="240" y2="265" stroke="#f14a72" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
      {/* Link icon */}
      <g className="animate-glow-pulse">
        <circle cx="240" cy="50" r="18" fill="#f4c25f" opacity="0.15" />
        <path d="M232,50 L236,46 Q240,42 244,46 L248,50" stroke="#f4c25f" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M248,50 L244,54 Q240,58 236,54 L232,50" stroke="#f4c25f" strokeWidth="2" fill="none" strokeLinecap="round" />
      </g>
      <line x1="240" y1="68" x2="240" y2="95" stroke="#f4c25f" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.3" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Teaching step layout — alternates illustration left/right          */
/* ------------------------------------------------------------------ */

interface TeachingStepProps {
  id: string;
  stepNumber: string;
  stepLabel: string;
  title: React.ReactNode;
  description: string;
  details: string[];
  illustration: React.ReactNode;
  reverse?: boolean;
  accentColor: string;
}

function TeachingStep({
  id,
  stepNumber,
  stepLabel,
  title,
  description,
  details,
  illustration,
  reverse = false,
  accentColor,
}: TeachingStepProps) {
  return (
    <section
      id={id}
      className="relative min-h-[80vh] flex items-center px-6 py-20 sm:py-28"
    >
      <div className="mx-auto max-w-6xl w-full">
        <div className={`grid items-center gap-12 lg:grid-cols-2 lg:gap-16 ${reverse ? 'lg:[direction:rtl]' : ''}`}>
          {/* Text side */}
          <div className={reverse ? 'lg:[direction:ltr]' : ''}>
            <RevealSection>
              <div className={`mb-4 inline-flex items-center gap-2 rounded-full px-3.5 py-1 text-xs font-semibold tracking-wide uppercase ${accentColor}`}>
                <span className="text-base font-bold">{stepNumber}</span>
                {stepLabel}
              </div>
            </RevealSection>
            <RevealSection delay={100}>
              <h2 className="text-3xl font-bold leading-tight text-primary-950 sm:text-4xl">
                {title}
              </h2>
            </RevealSection>
            <RevealSection delay={200}>
              <p className="mt-5 text-lg leading-relaxed text-primary-950/50">
                {description}
              </p>
            </RevealSection>
            <RevealSection delay={300}>
              <ul className="mt-8 space-y-3">
                {details.map((detail, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-primary-950/60">
                    <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-coral-500" />
                    {detail}
                  </li>
                ))}
              </ul>
            </RevealSection>
          </div>

          {/* Illustration side */}
          <RevealSection delay={150} className={reverse ? 'lg:[direction:ltr]' : ''}>
            <div className="rounded-2xl border border-primary-950/[0.06] bg-white p-4 shadow-sm sm:p-6">
              {illustration}
            </div>
          </RevealSection>
        </div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Main landing page                                                  */
/* ------------------------------------------------------------------ */

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-accent-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-coral-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-accent-50">
      <StepDots />

      {/* Navigation */}
      <nav className="fixed inset-x-0 top-0 z-50 bg-accent-50/80 backdrop-blur-xl border-b border-primary-950/[0.06]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5">
            <Box className="h-7 w-7 text-coral-500" />
            <span className="text-lg font-bold text-primary-950">SiteForge</span>
          </Link>
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/projects"
                className="group flex items-center gap-2 rounded-lg bg-coral-500 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-coral-400 hover:shadow-lg hover:shadow-coral-500/20"
              >
                Go to Projects
                <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-lg px-4 py-2 text-sm font-medium text-primary-950/60 transition-colors hover:text-primary-950"
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="rounded-lg bg-coral-500 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-coral-400 hover:shadow-lg hover:shadow-coral-500/20"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero — full viewport */}
      <section
        id="hero"
        className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 text-center"
      >
        <RevealSection>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary-950/[0.04] px-4 py-1.5 text-sm font-medium text-coral-500 ring-1 ring-primary-950/[0.08]">
            <Sparkles size={14} />
            Design. Plan. Visualize.
          </div>
        </RevealSection>
        <RevealSection delay={100}>
          <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight text-primary-950 sm:text-5xl lg:text-6xl">
            Site planning,{' '}
            <span className="bg-gradient-to-r from-coral-500 via-peach-400 to-gold-400 bg-clip-text text-transparent">
              reimagined
            </span>
          </h1>
        </RevealSection>
        <RevealSection delay={200}>
          <p className="mx-auto mt-6 max-w-xl text-lg text-primary-950/50">
            Draw on real maps. Generate 3D buildings with AI. Walk through your designs
            &mdash; all from your browser, in minutes.
          </p>
        </RevealSection>
        <RevealSection delay={300}>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
            {isAuthenticated ? (
              <Link
                to="/projects"
                className="group flex items-center gap-2 rounded-xl bg-coral-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-coral-500/20 transition-all hover:bg-coral-400 hover:shadow-xl hover:shadow-coral-500/25 active:scale-[0.97]"
              >
                Go to Your Projects
                <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="group flex items-center gap-2 rounded-xl bg-coral-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-coral-500/20 transition-all hover:bg-coral-400 hover:shadow-xl hover:shadow-coral-500/25 active:scale-[0.97]"
                >
                  Start Building Free
                  <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
                </Link>
                <Link
                  to="/login"
                  className="flex items-center gap-2 rounded-xl border border-primary-950/[0.1] px-6 py-3 text-sm font-semibold text-primary-950/70 transition-all hover:border-primary-950/20 hover:text-primary-950 active:scale-[0.97]"
                >
                  Sign in
                </Link>
              </>
            )}
          </div>
        </RevealSection>

        {/* Scroll hint */}
        <div className="absolute bottom-10 flex flex-col items-center gap-2 animate-bounce-gentle">
          <span className="text-xs font-medium tracking-wide text-primary-950/30 uppercase">Scroll to explore</span>
          <ChevronDown size={18} className="text-primary-950/30" />
        </div>
      </section>

      {/* Divider */}
      <div className="mx-auto h-px max-w-md bg-gradient-to-r from-transparent via-primary-950/10 to-transparent" />

      {/* Step 1: Find your site */}
      <TeachingStep
        id="step-map"
        stepNumber="01"
        stepLabel="Locate"
        title={<>Start with the <span className="bg-gradient-to-r from-teal-400 to-primary-400 bg-clip-text text-transparent">real world</span></>}
        description="Every great project begins with its site. Navigate to any location on a satellite map, zoom in, and start planning directly on real terrain."
        details={[
          'Search any address or navigate the globe freely',
          'High-resolution satellite imagery as your canvas',
          'Accurate geolocation and terrain context for every design',
        ]}
        illustration={
          <img
            src="/images/master-plan-preview.png"
            alt="SiteForge master plan view showing satellite imagery at a wide zoom level"
            className="w-full rounded-lg"
          />
        }
        accentColor="bg-teal-400/15 text-teal-500"
      />

      {/* Step 2: Define your zones */}
      <TeachingStep
        id="step-zones"
        stepNumber="02"
        stepLabel="Plan"
        title={<>Draw zones, define <span className="bg-gradient-to-r from-coral-500 to-peach-400 bg-clip-text text-transparent">purpose</span></>}
        description="Sketch out areas on the map and assign them types — residential, commercial, mixed-use, and more. Each zone carries its own rules and parameters."
        details={[
          'Draw polygonal zones with intuitive click-to-place tools',
          'Set building density, max height, and architectural style per zone',
          'Color-coded zones give instant visual clarity over your master plan',
        ]}
        illustration={
          <img
            src="/images/zone-planning-preview.png"
            alt="SiteForge site plan with color-coded residential, commercial, and park zones"
            className="w-full rounded-lg"
          />
        }
        reverse
        accentColor="bg-coral-500/15 text-coral-500"
      />

      {/* Step 3: Block Editor */}
      <TeachingStep
        id="step-ai"
        stepNumber="03"
        stepLabel="Design"
        title={<>Refine every <span className="bg-gradient-to-r from-gold-400 to-peach-400 bg-clip-text text-transparent">block</span></>}
        description="Zoom into any zone and open the Block Editor. Place buildings, draw streets and paths, add parks and plazas — shaping each block of your development with precision."
        details={[
          'Place and arrange buildings within each zone interactively',
          'Draw streets, paths, and infrastructure connecting your site',
          'Add parks, plazas, and green spaces to complete the layout',
        ]}
        illustration={
          <img
            src="/images/block-editor-preview.png"
            alt="SiteForge block editor with satellite map showing building and residential zone placement"
            className="w-full rounded-lg"
          />
        }
        accentColor="bg-gold-400/15 text-gold-500"
      />

      {/* Step 4: Explore in 3D */}
      <TeachingStep
        id="step-3d"
        stepNumber="04"
        stepLabel="Explore"
        title={<>Step inside your <span className="bg-gradient-to-r from-primary-400 to-teal-400 bg-clip-text text-transparent">creation</span></>}
        description="Switch to the 3D viewer and walk through your development. Adjust time of day, see realistic shadows, and experience the space as if you were standing in it."
        details={[
          'First-person and orbital camera controls',
          'Dynamic lighting with time-of-day simulation',
          'Realistic shadows and atmospheric effects bring scenes to life',
        ]}
        illustration={<ViewerIllustration />}
        reverse
        accentColor="bg-primary-400/15 text-primary-500"
      />

      {/* Step 5: Share & collaborate */}
      <TeachingStep
        id="step-share"
        stepNumber="05"
        stepLabel="Share"
        title={<>Collaborate with your <span className="bg-gradient-to-r from-coral-500 to-gold-400 bg-clip-text text-transparent">team</span></>}
        description="Generate secure share links so clients and stakeholders can explore your 3D development in their browser — no account needed. Keep your projects private or open them up selectively."
        details={[
          'One-click shareable links for any project',
          'Clients view interactive 3D scenes without an account',
          'Full privacy control — projects are private by default',
        ]}
        illustration={<ShareIllustration />}
        accentColor="bg-peach-400/15 text-peach-500"
      />

      {/* Final CTA */}
      <section id="cta" className="relative overflow-hidden px-6 py-24 text-center sm:py-32">
        <RevealSection>
          <div className="relative mx-auto max-w-lg rounded-3xl bg-primary-950 px-8 py-16 sm:px-12">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              {isAuthenticated ? 'Ready to keep building?' : 'Ready to start designing?'}
            </h2>
            <p className="mx-auto mt-4 max-w-md text-white/50">
              {isAuthenticated
                ? 'Jump back into your projects and bring your next idea to life.'
                : 'Create a free account and go from blank map to 3D walkthrough in minutes.'}
            </p>
            <Link
              to={isAuthenticated ? '/projects' : '/register'}
              className="group mt-8 inline-flex items-center gap-2 rounded-xl bg-coral-500 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-coral-500/30 transition-all hover:bg-coral-400 hover:shadow-xl active:scale-[0.97]"
            >
              {isAuthenticated ? 'Go to Projects' : 'Get Started Free'}
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </RevealSection>
      </section>

      {/* Footer */}
      <footer className="border-t border-primary-950/[0.06] px-6 py-8 text-center text-sm text-primary-950/40">
        &copy; {new Date().getFullYear()} SiteForge. All rights reserved.
      </footer>
    </div>
  );
}
