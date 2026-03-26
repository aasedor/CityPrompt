import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Box, ArrowRight, Sparkles, ChevronDown } from 'lucide-react';
import { useAuthStore } from '@/store';

/* ------------------------------------------------------------------ */
/*  Scroll-reveal hook                                                 */
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
const STEP_IDS = ['hero', 'step-map', 'step-zones', 'step-style', 'step-render', 'cta'];

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
/*  SVG illustrations                                                  */
/* ------------------------------------------------------------------ */

function RenderIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Split view: zone overlay -> photorealistic render */}
      <rect x="40" y="30" width="190" height="300" rx="12" fill="#f0f4f8" stroke="#e0e0e0" strokeWidth="1" />
      <rect x="250" y="30" width="190" height="300" rx="12" fill="#1d1b4f" stroke="#481c5f" strokeWidth="1" />
      {/* Left: zone overlay */}
      <rect x="55" y="60" width="80" height="60" rx="4" fill="#E03C31" opacity="0.2" stroke="#E03C31" strokeWidth="1.5" strokeDasharray="4 2" />
      <rect x="55" y="140" width="160" height="40" rx="4" fill="#616161" opacity="0.15" stroke="#616161" strokeWidth="1.5" strokeDasharray="4 2" />
      <rect x="145" y="60" width="70" height="80" rx="4" fill="#4CAF50" opacity="0.2" stroke="#4CAF50" strokeWidth="1.5" strokeDasharray="4 2" />
      <rect x="55" y="200" width="100" height="50" rx="4" fill="#E03C31" opacity="0.2" stroke="#E03C31" strokeWidth="1.5" strokeDasharray="4 2" />
      <text x="70" y="95" fill="#E03C31" fontSize="8" fontWeight="600">Building</text>
      <text x="155" y="105" fill="#4CAF50" fontSize="8" fontWeight="600">Park</text>
      <text x="100" y="165" fill="#616161" fontSize="8" fontWeight="600">Road</text>
      {/* Arrow */}
      <g className="animate-glow-pulse">
        <path d="M235,180 L255,180" stroke="url(#renderArrow)" strokeWidth="2.5" strokeLinecap="round" />
        <polygon points="257,176 265,180 257,184" fill="#f14a72" />
        <circle cx="245" cy="172" r="2" fill="#f4c25f" opacity="0.7" />
        <circle cx="250" cy="188" r="1.5" fill="#79d3c5" opacity="0.6" />
      </g>
      {/* Right: rendered result */}
      <rect x="265" y="50" width="160" height="120" rx="6" fill="#2a4a3a" opacity="0.8" />
      {/* Buildings in render */}
      <rect x="280" y="80" width="30" height="90" rx="2" fill="#8faaaa" opacity="0.9" />
      <rect x="280" y="80" width="30" height="5" rx="1" fill="#a0c0c0" />
      <rect x="285" y="90" width="8" height="10" rx="1" fill="#d4e8ff" opacity="0.5" />
      <rect x="297" y="90" width="8" height="10" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="285" y="108" width="8" height="10" rx="1" fill="#d4e8ff" opacity="0.6" />
      <rect x="297" y="108" width="8" height="10" rx="1" fill="#d4e8ff" opacity="0.3" />
      {/* Trees */}
      <circle cx="340" cy="145" r="12" fill="#3a7a3a" opacity="0.7" />
      <circle cx="360" cy="140" r="14" fill="#4a8a4a" opacity="0.6" />
      <circle cx="350" cy="150" r="10" fill="#2a6a2a" opacity="0.5" />
      {/* Road in render */}
      <rect x="265" y="155" width="160" height="15" rx="2" fill="#555555" opacity="0.8" />
      {/* Second building */}
      <rect x="390" y="100" width="25" height="70" rx="2" fill="#b09070" opacity="0.8" />
      <rect x="394" y="110" width="7" height="8" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="406" y="110" width="7" height="8" rx="1" fill="#d4e8ff" opacity="0.5" />
      {/* Sparkle icon */}
      <g className="animate-float-slow">
        <circle cx="370" cy="55" r="14" fill="#f4c25f" opacity="0.2" />
        <path d="M370,45 L372,52 L379,54 L372,56 L370,63 L368,56 L361,54 L368,52Z" fill="#f4c25f" opacity="0.8" />
      </g>
      {/* Style chips */}
      <rect x="270" y="195" width="55" height="16" rx="8" fill="#f14a72" opacity="0.2" />
      <text x="280" y="206" fill="#f14a72" fontSize="7" fontWeight="600">Photorealistic</text>
      <rect x="332" y="195" width="45" height="16" rx="8" fill="#4496d5" opacity="0.2" />
      <text x="340" y="206" fill="#4496d5" fontSize="7" fontWeight="600">Watercolour</text>
      <rect x="384" y="195" width="30" height="16" rx="8" fill="#79d3c5" opacity="0.2" />
      <text x="390" y="206" fill="#79d3c5" fontSize="7" fontWeight="600">Clay</text>
      <defs>
        <linearGradient id="renderArrow" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#00a8ba" />
          <stop offset="100%" stopColor="#f14a72" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function StreetViewIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Viewport frame */}
      <rect x="40" y="30" width="400" height="300" rx="12" fill="#2a3a5a" />
      {/* Sky gradient */}
      <rect x="48" y="38" width="384" height="150" rx="8" fill="url(#skyGrad)" />
      {/* Street perspective */}
      <polygon points="48,188 240,140 432,188 432,322 48,322" fill="#555050" />
      {/* Center road lines */}
      <line x1="240" y1="145" x2="240" y2="322" stroke="#f4c25f" strokeWidth="1.5" strokeDasharray="12 8" opacity="0.4" />
      {/* Sidewalks */}
      <polygon points="48,188 180,155 180,322 48,322" fill="#888585" opacity="0.4" />
      <polygon points="432,188 300,155 300,322 432,322" fill="#888585" opacity="0.4" />
      {/* Left building */}
      <rect x="55" y="80" width="110" height="108" rx="4" fill="#c8a882" opacity="0.9" />
      <rect x="55" y="80" width="110" height="12" rx="4" fill="#b09570" />
      {/* Left windows */}
      <rect x="65" y="100" width="14" height="18" rx="1" fill="#d4e8ff" opacity="0.5" />
      <rect x="85" y="100" width="14" height="18" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="105" y="100" width="14" height="18" rx="1" fill="#d4e8ff" opacity="0.6" />
      <rect x="125" y="100" width="14" height="18" rx="1" fill="#d4e8ff" opacity="0.3" />
      <rect x="65" y="130" width="14" height="18" rx="1" fill="#ffd56e" opacity="0.4" />
      <rect x="85" y="130" width="14" height="18" rx="1" fill="#ffd56e" opacity="0.6" />
      <rect x="105" y="130" width="14" height="18" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="125" y="130" width="14" height="18" rx="1" fill="#ffd56e" opacity="0.3" />
      {/* Ground floor storefront */}
      <rect x="65" y="158" width="90" height="30" rx="2" fill="#d4e8ff" opacity="0.3" />
      {/* Right building */}
      <rect x="315" y="70" width="110" height="118" rx="4" fill="#7a99b0" opacity="0.9" />
      <rect x="315" y="70" width="110" height="10" rx="4" fill="#6a8a9f" />
      <rect x="325" y="88" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.5" />
      <rect x="345" y="88" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="365" y="88" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.6" />
      <rect x="385" y="88" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.3" />
      <rect x="325" y="115" width="12" height="16" rx="1" fill="#ffd56e" opacity="0.5" />
      <rect x="345" y="115" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.4" />
      <rect x="365" y="115" width="12" height="16" rx="1" fill="#ffd56e" opacity="0.4" />
      <rect x="385" y="115" width="12" height="16" rx="1" fill="#d4e8ff" opacity="0.5" />
      {/* Trees along street */}
      <circle cx="185" cy="160" r="16" fill="#3a7a3a" opacity="0.7" />
      <rect x="183" y="176" width="4" height="12" rx="1" fill="#5a4a3a" opacity="0.6" />
      <circle cx="295" cy="155" r="14" fill="#4a8a4a" opacity="0.6" />
      <rect x="293" y="169" width="4" height="10" rx="1" fill="#5a4a3a" opacity="0.6" />
      {/* Pegman marker */}
      <g className="animate-bounce-gentle">
        <circle cx="240" cy="270" r="10" fill="#f14a72" opacity="0.3" />
        <circle cx="240" cy="270" r="5" fill="#f14a72" />
      </g>
      {/* Direction compass */}
      <g className="animate-float" style={{ animationDelay: '0.5s' }}>
        <circle cx="400" cy="55" r="16" fill="white" opacity="0.15" />
        <text x="396" y="59" fill="white" fontSize="10" fontWeight="600" opacity="0.8">N</text>
        <path d="M400,42 L402,48 L398,48Z" fill="white" opacity="0.6" />
      </g>
      <defs>
        <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#5a7faa" />
          <stop offset="100%" stopColor="#c8a882" stopOpacity="0.4" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function ShareIllustration() {
  return (
    <svg viewBox="0 0 480 360" fill="none" className="w-full h-full">
      {/* Central project card */}
      <rect x="160" y="100" width="160" height="160" rx="16" fill="white" stroke="#e0e0e0" strokeWidth="1.5" />
      <rect x="170" y="110" width="140" height="80" rx="8" fill="#f0f4f8" />
      {/* Mini render in card */}
      <rect x="180" y="120" width="50" height="60" rx="4" fill="#2a4a3a" opacity="0.6" />
      <rect x="190" y="130" width="15" height="40" rx="1" fill="#8faaaa" opacity="0.7" />
      <rect x="210" y="140" width="12" height="30" rx="1" fill="#b09070" opacity="0.7" />
      <rect x="240" y="120" width="60" height="60" rx="4" fill="#2a3a5a" opacity="0.6" />
      <rect x="250" y="135" width="20" height="35" rx="1" fill="#c8a882" opacity="0.6" />
      <rect x="278" y="130" width="15" height="40" rx="1" fill="#7a99b0" opacity="0.6" />
      <text x="180" y="210" fill="#1d1b4f" fontSize="11" fontWeight="600">Master Plan</text>
      <text x="180" y="225" fill="#9e9e9e" fontSize="9">4 zones  &#183;  2 renders</text>
      {/* Share button */}
      <rect x="180" y="235" width="60" height="18" rx="9" fill="#00a8ba" opacity="0.15" />
      <text x="192" y="247" fill="#00a8ba" fontSize="9" fontWeight="600">Share</text>
      {/* User avatars */}
      <g className="animate-float" style={{ animationDelay: '0s' }}>
        <circle cx="80" cy="140" r="24" fill="#fdb27a" opacity="0.2" stroke="#fdb27a" strokeWidth="1.5" />
        <circle cx="80" cy="134" r="8" fill="#fdb27a" />
        <path d="M64,158 Q64,148 80,148 Q96,148 96,158" fill="#fdb27a" opacity="0.6" />
        <text x="62" y="178" fill="#9e9e9e" fontSize="8" textAnchor="start">Architect</text>
      </g>
      <line x1="104" y1="140" x2="155" y2="170" stroke="#fdb27a" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
      <g className="animate-float" style={{ animationDelay: '1s' }}>
        <circle cx="400" cy="140" r="24" fill="#4496d5" opacity="0.2" stroke="#4496d5" strokeWidth="1.5" />
        <circle cx="400" cy="134" r="8" fill="#4496d5" />
        <path d="M384,158 Q384,148 400,148 Q416,148 416,158" fill="#4496d5" opacity="0.6" />
        <text x="385" y="178" fill="#9e9e9e" fontSize="8" textAnchor="start">Client</text>
      </g>
      <line x1="376" y1="140" x2="325" y2="170" stroke="#4496d5" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
      <g className="animate-float" style={{ animationDelay: '0.5s' }}>
        <circle cx="240" cy="310" r="24" fill="#f14a72" opacity="0.2" stroke="#f14a72" strokeWidth="1.5" />
        <circle cx="240" cy="304" r="8" fill="#f14a72" />
        <path d="M224,328 Q224,318 240,318 Q256,318 256,328" fill="#f14a72" opacity="0.6" />
        <text x="222" y="348" fill="#9e9e9e" fontSize="8" textAnchor="start">Planner</text>
      </g>
      <line x1="240" y1="286" x2="240" y2="265" stroke="#f14a72" strokeWidth="1.5" strokeDasharray="4 3" opacity="0.4" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Teaching step layout                                               */
/* ------------------------------------------------------------------ */

interface TeachingStepProps {
  id: string;
  stepNumber: string;
  stepLabel: string;
  title: React.ReactNode;
  description: string;
  details: string[];
  illustration: React.ReactNode;
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
  accentColor,
}: TeachingStepProps) {
  return (
    <section id={id} className="relative px-6 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl w-full">
        <div className="mx-auto max-w-2xl text-center">
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
            <ul className="mt-6 inline-flex flex-wrap justify-center gap-x-6 gap-y-2">
              {details.map((detail, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-primary-950/60">
                  <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-coral-500" />
                  {detail}
                </li>
              ))}
            </ul>
          </RevealSection>
        </div>
        <RevealSection delay={250}>
          <div className="mt-12 overflow-hidden rounded-2xl border border-primary-950/[0.06] bg-white shadow-lg sm:mt-14">
            {illustration}
          </div>
        </RevealSection>
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
            <span className="text-lg font-bold text-primary-950">City Prompt</span>
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

      {/* Hero */}
      <section
        id="hero"
        className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 text-center"
      >
        <RevealSection>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary-950/[0.04] px-4 py-1.5 text-sm font-medium text-coral-500 ring-1 ring-primary-950/[0.08]">
            <Sparkles size={14} />
            Draw. Style. Render.
          </div>
        </RevealSection>
        <RevealSection delay={100}>
          <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight text-primary-950 sm:text-5xl lg:text-6xl">
            Turn site plans into{' '}
            <span className="bg-gradient-to-r from-coral-500 via-peach-400 to-gold-400 bg-clip-text text-transparent">
              photorealistic renders
            </span>
          </h1>
        </RevealSection>
        <RevealSection delay={200}>
          <p className="mx-auto mt-6 max-w-xl text-lg text-primary-950/50">
            Draw zones on satellite maps. Pick architectural styles. Generate stunning aerial and street-level renders with AI &mdash; all from your browser.
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
                  Start Designing Free
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

        <div className="absolute bottom-10 flex flex-col items-center gap-2 animate-bounce-gentle">
          <span className="text-xs font-medium tracking-wide text-primary-950/30 uppercase">Scroll to explore</span>
          <ChevronDown size={18} className="text-primary-950/30" />
        </div>
      </section>

      <div className="mx-auto h-px max-w-md bg-gradient-to-r from-transparent via-primary-950/10 to-transparent" />

      {/* Step 1: Find your site */}
      <TeachingStep
        id="step-map"
        stepNumber="01"
        stepLabel="Locate"
        title={<>Start with the <span className="bg-gradient-to-r from-teal-400 to-primary-400 bg-clip-text text-transparent">real world</span></>}
        description="Navigate to any location on a satellite map, zoom in, and start planning directly on real terrain."
        details={[
          'Search any address worldwide',
          'High-resolution satellite imagery as your canvas',
          'Real terrain context for every design decision',
        ]}
        illustration={
          <img
            src="/images/master-plan-preview.png"
            alt="City Prompt satellite map view"
            className="w-full rounded-lg"
          />
        }
        accentColor="bg-teal-400/15 text-teal-500"
      />

      {/* Step 2: Draw zones */}
      <TeachingStep
        id="step-zones"
        stepNumber="02"
        stepLabel="Draw"
        title={<>Draw zones, define <span className="bg-gradient-to-r from-coral-500 to-peach-400 bg-clip-text text-transparent">purpose</span></>}
        description="Sketch buildings, streets, parks, and plazas directly on the map. Each zone gets its own type, density, and architectural style."
        details={[
          'Click-to-place polygon and line drawing tools',
          'Building, street, park, and plaza zone types',
          'Color-coded zones for instant visual clarity',
        ]}
        illustration={
          <img
            src="/images/zone-planning-preview.png"
            alt="City Prompt site plan with color-coded zones"
            className="w-full rounded-lg"
          />
        }
        accentColor="bg-coral-500/15 text-coral-500"
      />

      {/* Step 3: Pick styles */}
      <TeachingStep
        id="step-style"
        stepNumber="03"
        stepLabel="Style"
        title={<>Choose the <span className="bg-gradient-to-r from-gold-400 to-peach-400 bg-clip-text text-transparent">architecture</span></>}
        description="Browse a library of 50+ building archetypes, street typologies, and park styles. Each comes with four material variants and detailed metadata that drives the AI render."
        details={[
          'Brownstone, Art Deco, Glass Tower, Nordic, and dozens more',
          'Street types from bike lanes to BRT corridors',
          'Parks, plazas, playgrounds, and water features',
        ]}
        illustration={
          <img
            src="/images/block-editor-preview.png"
            alt="City Prompt archetype selection with building style cards"
            className="w-full rounded-lg"
          />
        }
        accentColor="bg-gold-400/15 text-gold-500"
      />

      {/* Step 4: AI Render */}
      <TeachingStep
        id="step-render"
        stepNumber="04"
        stepLabel="Render"
        title={<>Generate photorealistic <span className="bg-gradient-to-r from-primary-400 to-teal-400 bg-clip-text text-transparent">aerial views</span></>}
        description="Hit Render and watch your color-coded site plan transform into a photorealistic aerial image. The AI reads your zone shapes, building styles, and street layouts to produce architectural-quality visualizations."
        details={[
          'One-click render from zone overlay to photorealistic image',
          '12+ render styles including photomontage, watercolour, and clay model',
          'Zone-aware AI uses your archetype metadata as the prompt',
        ]}
        illustration={<RenderIllustration />}
        accentColor="bg-primary-400/15 text-primary-500"
      />

      {/* Final CTA */}
      <section id="cta" className="relative overflow-hidden px-6 py-24 text-center sm:py-32">
        <RevealSection>
          <div className="relative mx-auto max-w-lg rounded-3xl bg-primary-950 px-8 py-16 sm:px-12">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              {isAuthenticated ? 'Ready to keep designing?' : 'Ready to start rendering?'}
            </h2>
            <p className="mx-auto mt-4 max-w-md text-white/50">
              {isAuthenticated
                ? 'Jump back into your projects and bring your next idea to life.'
                : 'Create a free account and go from blank map to photorealistic render in minutes.'}
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

      <footer className="border-t border-primary-950/[0.06] px-6 py-8 text-center text-sm text-primary-950/40">
        &copy; {new Date().getFullYear()} City Prompt. All rights reserved.
      </footer>
    </div>
  );
}
