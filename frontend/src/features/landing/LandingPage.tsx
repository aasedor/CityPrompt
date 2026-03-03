import { Link, Navigate } from 'react-router-dom';
import { Box, Map, Cpu, Eye, FileText, ArrowRight, Layers } from 'lucide-react';
import { useAuthStore } from '@/store';

const FEATURES = [
  {
    icon: Map,
    title: 'Interactive Site Planning',
    description:
      'Design site layouts directly on satellite maps. Draw zones, place buildings, and plan developments with precision tools.',
    color: 'bg-primary-500/20 text-primary-400',
  },
  {
    icon: Cpu,
    title: 'AI-Powered Generation',
    description:
      'Let AI generate 3D building models from your parameters. Choose architectural styles and watch structures materialize.',
    color: 'bg-accent-500/20 text-accent-400',
  },
  {
    icon: Eye,
    title: '3D Visualization',
    description:
      'Explore your developments in full 3D. Walk through scenes, adjust lighting, and experience designs before they are built.',
    color: 'bg-emerald-500/20 text-emerald-400',
  },
  {
    icon: FileText,
    title: 'Document Processing',
    description:
      'Upload PDFs, CAD files, and images. AI extracts floor plans and building data to accelerate your workflow.',
    color: 'bg-amber-500/20 text-amber-400',
  },
];

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-primary-950">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-accent-300 border-t-transparent" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/projects" replace />;
  }

  return (
    <div className="min-h-screen bg-primary-950">
      {/* Navigation */}
      <nav className="fixed inset-x-0 top-0 z-50 bg-primary-950/80 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5">
            <Box className="h-7 w-7 text-accent-300" />
            <span className="text-lg font-bold text-white">SiteForge</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-neutral-300 transition-colors hover:text-white"
            >
              Sign in
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-white/[0.06] px-4 py-2 text-sm font-medium text-white ring-1 ring-white/[0.12] backdrop-blur-sm transition-all hover:bg-white/[0.12] hover:ring-white/20"
            >
              Get Started
            </Link>
          </div>
        </div>
        {/* Glow line under nav */}
        <div className="glow-line" />
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-primary pb-24 pt-32 sm:pb-32 sm:pt-40">
        {/* Decorative grid */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.5) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />
        {/* Primary radial glow */}
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[700px] w-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary-500/15 blur-3xl" />
        {/* Accent radial glow (blush/rose) */}
        <div className="pointer-events-none absolute left-[65%] top-[35%] h-[400px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-400/10 blur-3xl animate-glow-pulse" />
        {/* Secondary subtle glow */}
        <div className="pointer-events-none absolute left-[25%] top-[70%] h-[300px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary-400/10 blur-3xl" />

        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/[0.08] px-4 py-1.5 text-sm font-medium text-accent-300 ring-1 ring-white/[0.15] shadow-glow-sm backdrop-blur-sm">
            <Layers size={14} />
            Design. Plan. Visualize.
          </div>
          <h1 className="text-4xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
            Build the future of
            <br />
            <span className="bg-gradient-to-r from-accent-300 to-accent-200 bg-clip-text text-transparent">
              architectural design
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-neutral-300 sm:text-xl">
            Create site plans, generate AI-powered 3D buildings, and explore immersive visualizations
            — all in one platform. From concept to walkthrough in minutes.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              to="/register"
              className="btn-accent group flex items-center gap-2 rounded-xl px-6 py-3"
            >
              Start Building Free
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              to="/login"
              className="btn-secondary flex items-center gap-2 rounded-xl px-6 py-3"
            >
              Sign in
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative -mt-16 px-6">
        <div className="mx-auto grid max-w-5xl gap-6 sm:grid-cols-2">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="card-hover group p-6 sm:p-8"
            >
              <div className={`inline-flex rounded-xl p-3 ${feature.color}`}>
                <feature.icon size={24} />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-neutral-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow section */}
      <section className="mx-auto max-w-4xl px-6 py-24 text-center sm:py-32">
        <h2 className="text-2xl font-bold text-white sm:text-3xl">
          From blank canvas to 3D walkthrough
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-neutral-400">
          No complex software to learn. Draw your site plan on the map, let AI generate buildings,
          and step into a fully rendered 3D scene — all from your browser.
        </p>
        <div className="mt-12 grid gap-8 text-left sm:grid-cols-3">
          {[
            { step: '01', title: 'Plan your site', desc: 'Draw zones on satellite imagery. Define residential, commercial, and mixed-use areas.' },
            { step: '02', title: 'Generate buildings', desc: 'Choose architectural styles and let AI create detailed 3D models that fit your vision.' },
            { step: '03', title: 'Explore in 3D', desc: 'Walk through your development with realistic lighting, shadows, and time-of-day controls.' },
          ].map((item) => (
            <div key={item.step}>
              <span className="text-3xl font-bold text-primary-500/50 drop-shadow-[0_0_8px_rgba(78,83,154,0.4)]">{item.step}</span>
              <h3 className="mt-2 text-base font-semibold text-white">{item.title}</h3>
              <p className="mt-1 text-sm text-neutral-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden bg-gradient-primary px-6 py-20 text-center sm:py-24">
        {/* Glow orbs matching hero */}
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary-500/15 blur-3xl" />
        <div className="pointer-events-none absolute left-[60%] top-[30%] h-[300px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-400/10 blur-3xl animate-glow-pulse" />

        <div className="relative">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">Ready to start designing?</h2>
          <p className="mx-auto mt-3 max-w-md text-neutral-300">
            Create a free account and bring your architectural visions to life.
          </p>
          <Link
            to="/register"
            className="btn-accent group mt-8 inline-flex items-center gap-2 rounded-xl px-6 py-3"
          >
            Get Started
            <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/[0.06] bg-primary-950 px-6 py-8 text-center text-sm text-neutral-400">
        &copy; {new Date().getFullYear()} SiteForge. All rights reserved.
      </footer>
    </div>
  );
}
