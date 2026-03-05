import { Link, Navigate } from 'react-router-dom';
import { Box, Map, Cpu, Eye, FileText, ArrowRight, Sparkles, Zap, Globe } from 'lucide-react';
import { useAuthStore } from '@/store';

const FEATURES = [
  {
    icon: Map,
    title: 'Interactive Site Planning',
    description:
      'Design site layouts directly on satellite maps. Draw zones, place buildings, and plan developments with precision tools.',
    iconBg: 'bg-teal-400/15',
    iconColor: 'text-teal-400',
  },
  {
    icon: Cpu,
    title: 'AI-Powered Generation',
    description:
      'Let AI generate 3D building models from your parameters. Choose architectural styles and watch structures materialize.',
    iconBg: 'bg-coral-500/15',
    iconColor: 'text-coral-500',
  },
  {
    icon: Eye,
    title: '3D Visualization',
    description:
      'Explore your developments in full 3D. Walk through scenes, adjust lighting, and experience designs before they are built.',
    iconBg: 'bg-primary-400/15',
    iconColor: 'text-primary-400',
  },
  {
    icon: FileText,
    title: 'Document Processing',
    description:
      'Upload PDFs, CAD files, and images. AI extracts floor plans and building data to accelerate your workflow.',
    iconBg: 'bg-peach-400/15',
    iconColor: 'text-peach-500',
  },
];

function CreatorAnimation() {
  return (
    <div className="relative w-full h-full min-h-[380px] lg:min-h-[460px]">
      <svg
        viewBox="0 0 500 500"
        className="w-full h-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Soft background circles */}
        <circle cx="250" cy="250" r="200" fill="url(#bgGlow)" opacity="0.25" />
        <circle cx="250" cy="250" r="130" fill="url(#bgGlow2)" opacity="0.15" className="animate-glow-pulse" />

        {/* Desk shadow */}
        <ellipse cx="250" cy="385" rx="170" ry="16" fill="#1d1b4f" opacity="0.06" />

        {/* Monitor */}
        <g className="animate-float" style={{ animationDelay: '0s' }}>
          <rect x="165" y="185" width="170" height="125" rx="10" fill="#1d1b4f" stroke="#481c5f" strokeWidth="2" />
          <rect x="173" y="193" width="154" height="109" rx="6" fill="#fefaf7" />
          {/* Screen grid */}
          <line x1="185" y1="255" x2="315" y2="255" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
          <line x1="185" y1="235" x2="315" y2="235" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
          <line x1="185" y1="215" x2="315" y2="215" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
          <line x1="220" y1="195" x2="220" y2="300" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
          <line x1="260" y1="195" x2="260" y2="300" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />
          <line x1="300" y1="195" x2="300" y2="300" stroke="#4496d5" strokeWidth="0.5" opacity="0.2" />

          {/* Teal building on screen */}
          <g className="animate-pop-in" style={{ animationDelay: '0.5s', opacity: 0 }}>
            <polygon points="232,278 268,278 268,232 232,232" fill="#00a8ba" opacity="0.7" />
            <polygon points="268,278 296,260 296,214 268,232" fill="#009aab" opacity="0.7" />
            <polygon points="232,232 268,232 296,214 260,214" fill="#79d3c5" opacity="0.7" />
          </g>

          {/* Coral building on screen */}
          <g className="animate-pop-in" style={{ animationDelay: '1s', opacity: 0 }}>
            <polygon points="192,278 218,278 218,248 192,248" fill="#f14a72" opacity="0.7" />
            <polygon points="218,278 236,268 236,238 218,248" fill="#d93d63" opacity="0.7" />
            <polygon points="192,248 218,248 236,238 210,238" fill="#f47090" opacity="0.7" />
          </g>

          {/* Monitor stand */}
          <rect x="237" y="310" width="26" height="28" rx="2" fill="#1d1b4f" opacity="0.8" />
          <rect x="220" y="336" width="60" height="5" rx="3" fill="#1d1b4f" opacity="0.6" />
        </g>

        {/* Person */}
        <g>
          <circle cx="128" cy="242" r="20" fill="#fdb27a" />
          <path d="M110,237 Q110,219 128,219 Q146,219 146,237" fill="#481c5f" />
          <path d="M110,262 Q110,288 114,325 L142,325 Q146,288 146,262 Q146,258 128,258 Q110,258 110,262Z" fill="#4496d5" />
          <g className="animate-bounce-gentle">
            <path d="M146,275 Q160,268 170,262 Q173,260 175,262" stroke="#fdb27a" strokeWidth="5.5" strokeLinecap="round" fill="none" />
            <circle cx="177" cy="260" r="3.5" fill="#fdb27a" />
            <line x1="179" y1="256" x2="185" y2="250" stroke="#f4c25f" strokeWidth="2" strokeLinecap="round" />
          </g>
          <path d="M110,275 Q96,284 92,298" stroke="#fdb27a" strokeWidth="5.5" strokeLinecap="round" fill="none" />
        </g>

        {/* Floating coral cube */}
        <g className="animate-float-slow" style={{ animationDelay: '1s' }}>
          <polygon points="372,122 395,110 395,138 372,150" fill="#f14a72" opacity="0.8" />
          <polygon points="395,110 418,122 418,150 395,138" fill="#d93d63" opacity="0.8" />
          <polygon points="372,122 395,110 418,122 395,133" fill="#f47090" opacity="0.8" />
        </g>

        {/* Floating teal sphere */}
        <g className="animate-float-reverse" style={{ animationDelay: '2s' }}>
          <circle cx="398" cy="222" r="16" fill="url(#sphereGrad)" opacity="0.85" />
        </g>

        {/* Floating gold triangle */}
        <g className="animate-float-slow" style={{ animationDelay: '0.5s' }}>
          <polygon points="82,152 100,115 118,152" fill="#f4c25f" opacity="0.75" />
          <polygon points="100,115 118,152 132,138" fill="#fdb27a" opacity="0.7" />
        </g>

        {/* Sparkle particles */}
        <g className="animate-glow-pulse" style={{ animationDelay: '0s' }}>
          <circle cx="352" cy="172" r="3.5" fill="#ffd56e" />
          <circle cx="378" cy="278" r="2.5" fill="#79d3c5" />
          <circle cx="98" cy="178" r="3" fill="#f14a72" />
          <circle cx="418" cy="162" r="2.5" fill="#4496d5" />
          <circle cx="342" cy="298" r="2" fill="#fdb27a" />
        </g>
        <g className="animate-glow-pulse" style={{ animationDelay: '1.5s' }}>
          <circle cx="72" cy="218" r="2.5" fill="#f4c25f" />
          <circle cx="428" cy="248" r="3.5" fill="#f14a72" />
          <circle cx="362" cy="338" r="2.5" fill="#00a8ba" />
          <circle cx="142" cy="142" r="3" fill="#ffd56e" />
        </g>

        {/* Creation lines from stylus */}
        <path
          d="M185,250 Q215,205 275,195 Q315,190 338,165"
          stroke="url(#drawGrad)"
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          strokeDasharray="1000"
          strokeDashoffset="1000"
          style={{ animation: 'draw-path 3s ease-in-out forwards 1.5s' }}
        />
        <path
          d="M185,250 Q198,232 228,222 Q258,216 298,232"
          stroke="url(#drawGrad2)"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
          strokeDasharray="1000"
          strokeDashoffset="1000"
          style={{ animation: 'draw-path 2.5s ease-in-out forwards 2s' }}
        />

        {/* Orbit ring */}
        <g className="animate-spin-slow" style={{ transformOrigin: '250px 250px' }}>
          <ellipse cx="250" cy="250" rx="215" ry="55" stroke="#481c5f" strokeWidth="0.5" opacity="0.08" fill="none" transform="rotate(-20, 250, 250)" />
        </g>

        <defs>
          <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#4496d5" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#fefaf7" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bgGlow2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f14a72" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#fefaf7" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="sphereGrad" cx="40%" cy="35%" r="60%">
            <stop offset="0%" stopColor="#79d3c5" />
            <stop offset="100%" stopColor="#00a8ba" />
          </radialGradient>
          <linearGradient id="drawGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f14a72" />
            <stop offset="50%" stopColor="#fdb27a" />
            <stop offset="100%" stopColor="#f4c25f" />
          </linearGradient>
          <linearGradient id="drawGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4496d5" />
            <stop offset="100%" stopColor="#79d3c5" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-accent-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-coral-500 border-t-transparent" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/projects" replace />;
  }

  return (
    <div className="min-h-screen bg-accent-50">
      {/* Navigation */}
      <nav className="fixed inset-x-0 top-0 z-50 bg-accent-50/80 backdrop-blur-xl border-b border-primary-950/[0.06]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5">
            <Box className="h-7 w-7 text-coral-500" />
            <span className="text-lg font-bold text-primary-950">SiteForge</span>
          </Link>
          <div className="flex items-center gap-3">
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
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pb-12 pt-32 sm:pb-20 sm:pt-40 lg:pb-8">
        <div className="relative mx-auto max-w-6xl px-6">
          <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
            <div className="text-center lg:text-left">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary-950/[0.04] px-4 py-1.5 text-sm font-medium text-coral-500 ring-1 ring-primary-950/[0.08]">
                <Sparkles size={14} />
                Design. Plan. Visualize.
              </div>
              <h1 className="text-4xl font-bold leading-tight tracking-tight text-primary-950 sm:text-5xl lg:text-6xl">
                Build the future of
                <br />
                <span className="bg-gradient-to-r from-coral-500 via-peach-400 to-gold-400 bg-clip-text text-transparent">
                  architectural design
                </span>
              </h1>
              <p className="mx-auto mt-6 max-w-xl text-lg text-primary-950/50 lg:mx-0">
                Create site plans, generate AI-powered 3D buildings, and explore immersive visualizations
                &mdash; all in one platform. From concept to walkthrough in minutes.
              </p>
              <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row lg:justify-start">
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
              </div>

              <div className="mt-10 flex flex-wrap items-center justify-center gap-6 lg:justify-start">
                <div className="flex items-center gap-2 text-sm text-primary-950/40">
                  <Zap size={14} className="text-gold-400" />
                  AI-Powered
                </div>
                <div className="flex items-center gap-2 text-sm text-primary-950/40">
                  <Globe size={14} className="text-teal-400" />
                  Browser-Based
                </div>
                <div className="flex items-center gap-2 text-sm text-primary-950/40">
                  <Sparkles size={14} className="text-coral-500" />
                  No Software Install
                </div>
              </div>
            </div>

            <div className="relative">
              <CreatorAnimation />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative px-6 py-20 sm:py-24">
        <div className="mx-auto max-w-5xl">
          <div className="mb-12 text-center">
            <h2 className="text-2xl font-bold text-primary-950 sm:text-3xl">
              Everything you need to{' '}
              <span className="bg-gradient-to-r from-teal-400 to-primary-400 bg-clip-text text-transparent">
                create
              </span>
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-primary-950/50">
              Powerful tools that work together to bring your architectural visions to life.
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-2xl border border-primary-950/[0.06] bg-white p-6 shadow-sm transition-all duration-300 hover:border-primary-950/[0.1] hover:shadow-lg sm:p-8"
              >
                <div className={`inline-flex rounded-xl p-3 ${feature.iconBg}`}>
                  <feature.icon size={24} className={feature.iconColor} />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-primary-950">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-primary-950/50">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow section */}
      <section className="mx-auto max-w-5xl px-6 py-20 sm:py-24">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-primary-950 sm:text-3xl">
            From blank canvas to 3D walkthrough
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-primary-950/50">
            No complex software to learn. Draw your site plan on the map, let AI generate buildings,
            and step into a fully rendered 3D scene &mdash; all from your browser.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-3">
          {[
            {
              step: '01',
              title: 'Plan your site',
              desc: 'Draw zones on satellite imagery. Define residential, commercial, and mixed-use areas.',
              color: 'text-teal-400',
            },
            {
              step: '02',
              title: 'Generate buildings',
              desc: 'Choose architectural styles and let AI create detailed 3D models that fit your vision.',
              color: 'text-coral-500',
            },
            {
              step: '03',
              title: 'Explore in 3D',
              desc: 'Walk through your development with realistic lighting, shadows, and time-of-day controls.',
              color: 'text-gold-500',
            },
          ].map((item) => (
            <div key={item.step} className="relative text-center sm:text-left">
              <span className={`text-4xl font-bold ${item.color} opacity-70`}>
                {item.step}
              </span>
              <h3 className="mt-3 text-base font-semibold text-primary-950">{item.title}</h3>
              <p className="mt-2 text-sm text-primary-950/50">{item.desc}</p>
            </div>
          ))}
        </div>
        <div className="mx-auto mt-12 h-1 max-w-md rounded-full bg-gradient-to-r from-teal-400 via-coral-500 to-gold-400 opacity-25" />
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden px-6 py-20 text-center sm:py-24">
        <div className="relative mx-auto max-w-lg rounded-3xl bg-primary-950 px-8 py-14 sm:px-12">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">Ready to start designing?</h2>
          <p className="mx-auto mt-3 max-w-md text-white/60">
            Create a free account and bring your architectural visions to life.
          </p>
          <Link
            to="/register"
            className="group mt-8 inline-flex items-center gap-2 rounded-xl bg-coral-500 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-coral-500/30 transition-all hover:bg-coral-400 hover:shadow-xl active:scale-[0.97]"
          >
            Get Started
            <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-primary-950/[0.06] px-6 py-8 text-center text-sm text-primary-950/40">
        &copy; {new Date().getFullYear()} SiteForge. All rights reserved.
      </footer>
    </div>
  );
}
