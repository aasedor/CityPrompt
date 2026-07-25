import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Image as ImageIcon,
  Layers3,
  Map,
  Sparkles,
  WandSparkles,
} from 'lucide-react';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { TileTrail } from '@/components/ui/TileTrail';
import { useAuthStore } from '@/store';
import { LoginForm } from '@/features/auth/LoginPage';

function GridBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-[0.22] dark:opacity-[0.34]"
      style={{
        backgroundImage:
          'linear-gradient(var(--city-grid-line) 2px, transparent 2px), linear-gradient(90deg, var(--city-grid-line) 2px, transparent 2px), linear-gradient(var(--city-grid-line) 1px, transparent 1px), linear-gradient(90deg, var(--city-grid-line) 1px, transparent 1px)',
        backgroundSize: '128px 128px, 128px 128px, 32px 32px, 32px 32px',
      }}
    />
  );
}

function BrandMark() {
  return (
    <Link to="/" className="inline-flex items-center gap-2 rounded-md px-1 py-1">
      <img src="/images/city-prompt-logo.png" alt="City Prompt" className="h-9 w-9 dark:invert" />
      <span className="text-sm font-black uppercase">City Prompt</span>
    </Link>
  );
}

function MiniTile({
  src,
  label,
  className = '',
}: {
  src: string;
  label: string;
  className?: string;
}) {
  return (
    <figure className={`overflow-hidden rounded-lg border-2 border-[#151515] bg-white shadow-[7px_7px_0_0_#151515] ${className}`}>
      <img src={src} alt={label} className="h-full w-full object-cover" />
    </figure>
  );
}

function ValueStrip() {
  return (
    <div className="mt-6 grid max-w-lg grid-cols-3 gap-2 sm:gap-3">
      <div className="rounded-lg border-2 border-[#151515] bg-white p-3 shadow-[4px_4px_0_0_#151515]">
        <div className="flex items-center gap-2">
          <Map size={16} />
          <span className="text-[10px] font-black uppercase text-[#5a5a5a]">Sites</span>
        </div>
        <p className="mt-2 text-xl font-black leading-none">Real</p>
      </div>
      <div className="rounded-lg border-2 border-[#151515] bg-white p-3 shadow-[4px_4px_0_0_#151515]">
        <div className="flex items-center gap-2">
          <Layers3 size={16} />
          <span className="text-[10px] font-black uppercase text-[#5a5a5a]">Zones</span>
        </div>
        <p className="mt-2 text-xl font-black leading-none">Typed</p>
      </div>
      <div className="rounded-lg border-2 border-[#151515] bg-white p-3 shadow-[4px_4px_0_0_#151515]">
        <div className="flex items-center gap-2">
          <ImageIcon size={16} />
          <span className="text-[10px] font-black uppercase text-[#5a5a5a]">Renders</span>
        </div>
        <p className="mt-2 text-xl font-black leading-none">Saved</p>
      </div>
    </div>
  );
}

function PlanningCollage() {
  return (
    <div className="relative mt-8 h-80 max-w-[36rem] sm:mt-10">
      <MiniTile
        src="/images/landing-collage.png"
        label="Prompt view"
        className="absolute left-0 top-0 z-10 h-44 w-[min(18rem,64vw)] rotate-[-5deg]"
      />
      <MiniTile
        src="/images/landing-render.png"
        label="Final render"
        className="absolute left-[min(13rem,28vw)] top-20 z-20 h-40 w-[min(18rem,62vw)] rotate-[4deg]"
      />
      <div className="absolute bottom-2 left-4 z-30 rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-4 py-3 shadow-[5px_5px_0_0_#151515]">
        <div className="flex items-center gap-2 text-sm font-black uppercase">
          <Layers3 size={17} />
          Map to render
        </div>
      </div>
      <div className="absolute bottom-2 right-0 z-30 rounded-full border-2 border-[#151515] bg-[#0aa6a6] px-4 py-2 text-xs font-black uppercase text-white shadow-[4px_4px_0_0_#151515]">
        <ImageIcon size={14} className="mr-1 inline" />
        Saved
      </div>
    </div>
  );
}

function AuthenticatedCard() {
  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[10px_10px_0_0_#151515] sm:p-6">
      <div className="inline-flex h-11 w-11 items-center justify-center rounded-full border-2 border-[#151515] bg-[#c9ff3d]">
        <Map size={20} />
      </div>
      <h1 className="mt-5 text-4xl font-black uppercase leading-none tracking-normal sm:text-5xl">
        Welcome back
      </h1>
      <p className="mt-3 text-sm font-semibold leading-6 text-[#5c554d]">
        Your projects, saved render studies, and planning experiments are ready.
      </p>
      <Link
        to="/projects"
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-full border-2 border-[#151515] bg-[#151515] px-4 py-3 text-sm font-black text-white shadow-[5px_5px_0_0_#151515] transition hover:bg-[#2a2a2a] active:translate-x-0.5 active:translate-y-0.5"
      >
        Open projects
        <ArrowRight size={16} />
      </Link>
    </div>
  );
}

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#fff9ec]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#151515] border-t-[#ff5a3d]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#fff9ec] text-[#151515]">
      <GridBackground />
      <TileTrail />

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <BrandMark />
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {isAuthenticated ? (
            <Link
              to="/projects"
              className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-4 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] hover:bg-[#d7ff66]"
            >
              Dashboard
              <ArrowRight size={14} />
            </Link>
          ) : (
            <Link
              to="/register"
              className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-white px-4 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] hover:bg-[#c9ff3d]"
            >
              Create account
              <ArrowRight size={14} />
            </Link>
          )}
        </div>
      </header>

      <main className="relative z-10 mx-auto grid min-h-[calc(100vh-76px)] max-w-7xl items-center gap-8 px-4 pb-10 sm:px-6 lg:grid-cols-[minmax(0,1fr)_440px] lg:px-8">
        <section className="order-2 lg:order-1">
          <span className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#ff5a3d] px-3 py-1 text-xs font-black uppercase text-white">
            <Sparkles size={13} />
            Sketch, style, render
          </span>
          <h2 className="mt-7 max-w-4xl text-[4.2rem] font-black uppercase leading-[0.84] tracking-normal sm:text-[5.4rem]">
            Plan visual futures.
          </h2>
          <p className="mt-6 max-w-lg text-lg font-semibold leading-8 text-[#5c554d]">
            Turn a real address into mapped zones, style systems, saved generations, and AI
            renders that make early development ideas feel tangible.
          </p>

          <ValueStrip />
          <PlanningCollage />
        </section>

        <section className="order-1 lg:order-2">
          <div className="mb-6">
            <span className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1 text-xs font-black uppercase">
              <WandSparkles size={13} />
              Welcome back
            </span>
            <h1 className="mt-4 text-4xl font-black uppercase leading-none tracking-normal sm:text-5xl">
              Sign in
            </h1>
            <p className="mt-3 text-sm font-semibold leading-6 text-[#5c554d]">
              Get back to your projects, saved images, and render experiments.
            </p>
          </div>

          {isAuthenticated ? <AuthenticatedCard /> : <LoginForm />}
        </section>
      </main>
    </div>
  );
}
