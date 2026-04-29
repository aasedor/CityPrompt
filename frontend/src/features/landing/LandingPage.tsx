import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { LucideIcon } from 'lucide-react';
import {
  ArrowRight,
  Building2,
  Camera,
  Check,
  Image as ImageIcon,
  Layers3,
  Map,
  MoveUpRight,
  Palette,
  Sparkles,
  WandSparkles,
} from 'lucide-react';
import { useAuthStore } from '@/store';
import { ThemeToggle } from '@/components/layout/ThemeToggle';

const imageAssets = {
  prompt: '/images/landing-prompt.jpg',
  render: '/images/landing-render.png',
  collage: '/images/landing-collage.png',
};

function GridBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-[0.16] dark:opacity-[0.22]"
      style={{
        backgroundImage:
          'linear-gradient(var(--city-grid-line) 1px, transparent 1px), linear-gradient(90deg, var(--city-grid-line) 1px, transparent 1px)',
        backgroundSize: '32px 32px',
      }}
    />
  );
}

function BrandMark() {
  return (
    <Link to="/" className="inline-flex items-center gap-2 rounded-md px-1 py-1 text-[#151515]">
      <img src="/images/city-prompt-logo.png" alt="City Prompt" className="h-9 w-9 dark:invert" />
      <span className="text-sm font-black uppercase">City Prompt</span>
    </Link>
  );
}

function Pill({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border-2 px-3 py-1 text-xs font-black uppercase ${className}`}
    >
      {children}
    </span>
  );
}

function ImageTile({
  src,
  label,
  className = '',
}: {
  src: string;
  label: string;
  className?: string;
}) {
  return (
    <figure className={`overflow-hidden rounded-lg bg-white shadow-xl ${className}`}>
      <img src={src} alt={label} className="h-full w-full object-cover" />
      <figcaption className="flex items-center justify-between border-t-2 border-[#151515] bg-white px-3 py-2 text-xs font-black uppercase">
        <span>{label}</span>
        <MoveUpRight size={14} />
      </figcaption>
    </figure>
  );
}

function ActionLink({
  to,
  children,
  variant = 'solid',
}: {
  to: string;
  children: ReactNode;
  variant?: 'solid' | 'outline';
}) {
  const isSolid = variant === 'solid';

  return (
    <Link
      to={to}
      className={`inline-flex min-h-12 items-center justify-center gap-2 rounded-full border-2 border-[#151515] px-5 py-3 text-sm font-black transition-transform active:translate-x-0.5 active:translate-y-0.5 ${
        isSolid
          ? 'bg-[#151515] text-white shadow-[5px_5px_0_0_#151515] hover:bg-[#2a2a2a]'
          : 'bg-white text-[#151515] hover:bg-[#c9ff3d]'
      }`}
    >
      {children}
    </Link>
  );
}

function MiniStat({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border-2 border-[#151515] bg-white p-3 shadow-[4px_4px_0_0_#151515]">
      <div className="flex items-center gap-2">
        <Icon size={16} />
        <span className="text-[10px] font-black uppercase text-[#5a5a5a]">{label}</span>
      </div>
      <p className="mt-2 text-xl font-black leading-none">{value}</p>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  body,
}: {
  icon: LucideIcon;
  title: string;
  body: string;
}) {
  return (
    <article className="rounded-lg border-2 border-[#151515] bg-[#fff9ec] p-4 shadow-[6px_6px_0_0_#151515]">
      <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-[#151515] bg-[#c9ff3d]">
        <Icon size={19} />
      </div>
      <h2 className="mt-4 text-lg font-black uppercase leading-tight">{title}</h2>
      <p className="mt-3 text-sm font-semibold leading-6 text-[#55504a]">{body}</p>
    </article>
  );
}

function MobileCollage() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:hidden">
      <ImageTile
        src={imageAssets.collage}
        label="Prompt view"
        className="h-64 border-2 border-[#151515]"
      />
      <ImageTile
        src={imageAssets.prompt}
        label="Site prompt"
        className="h-64 border-2 border-[#151515]"
      />
      <ImageTile
        src={imageAssets.render}
        label="Final AI render"
        className="h-80 border-[3px] border-[#151515] shadow-[8px_8px_0_0_#151515] sm:col-span-2"
      />
    </div>
  );
}

function DesktopCollage() {
  return (
    <div className="relative hidden min-h-[640px] lg:block">
      <ImageTile
        src={imageAssets.collage}
        label="Prompt view"
        className="absolute -left-10 top-8 z-10 h-48 w-72 rotate-[-7deg] border-2 border-[#151515] shadow-[7px_7px_0_0_#151515]"
      />
      <ImageTile
        src={imageAssets.prompt}
        label="Site prompt"
        className="absolute -right-14 top-12 z-10 h-56 w-80 rotate-[7deg] border-2 border-[#151515] shadow-[7px_7px_0_0_#151515]"
      />

      <div className="absolute left-[16%] top-56 z-30 w-[25.5rem] rotate-[2deg]">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#ff5a3d] px-4 py-2 text-xs font-black uppercase text-white shadow-[4px_4px_0_0_#151515]">
          <WandSparkles size={14} />
          Final product
        </div>
        <ImageTile
          src={imageAssets.render}
          label="Final AI render"
          className="h-72 border-[3px] border-[#151515] shadow-[14px_14px_0_0_#151515]"
        />
      </div>

      <div className="absolute -left-24 bottom-8 rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-5 py-4 shadow-[6px_6px_0_0_#151515]">
        <div className="flex items-center gap-3">
          <Palette size={23} />
          <div>
            <p className="text-xs font-black uppercase">Style set</p>
            <p className="text-2xl font-black leading-none">119 kits</p>
          </div>
        </div>
      </div>

      <div className="absolute bottom-28 right-8 z-40 rounded-full border-2 border-[#151515] bg-[#0aa6a6] px-5 py-3 text-sm font-black text-white shadow-[5px_5px_0_0_#151515]">
        AI render ready
      </div>
    </div>
  );
}

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const primaryHref = isAuthenticated ? '/projects' : '/register';
  const primaryLabel = isAuthenticated ? 'Open projects' : 'Try the tool';

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#fff9ec]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#151515] border-t-[#ff5a3d]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen overflow-hidden bg-[#fff9ec] text-[#151515]">
      <section className="relative min-h-screen overflow-hidden border-b-2 border-[#151515]">
        <GridBackground />

        <header className="relative z-20 border-b-2 border-[#151515] bg-[#fff9ec]/90 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
            <BrandMark />

            <nav className="hidden items-center gap-5 text-xs font-black uppercase md:flex">
              <a href="#how-it-works" className="rounded-full px-2 py-1 hover:bg-[#c9ff3d]">
                Workflow
              </a>
              <Link to="/projects" className="rounded-full px-2 py-1 hover:bg-[#c9ff3d]">
                Projects
              </Link>
            </nav>

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
                <>
                  <Link
                    to="/login"
                    className="rounded-full px-3 py-2 text-xs font-black uppercase hover:bg-white"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/register"
                    className="rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-4 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] hover:bg-[#d7ff66]"
                  >
                    Start
                  </Link>
                </>
              )}
            </div>
          </div>
        </header>

        <main className="relative z-10 mx-auto grid max-w-7xl gap-9 px-4 pb-12 pt-10 sm:px-6 lg:min-h-[calc(100vh-66px)] lg:grid-cols-[minmax(0,0.92fr)_minmax(520px,1fr)] lg:items-center lg:px-8 lg:pt-0">
          <div>
            <Pill className="border-[#151515] bg-[#ff5a3d] text-white">
              <Sparkles size={13} />
              Sketch, style, render
            </Pill>

            <h1 className="mt-7 max-w-5xl text-[4.15rem] font-black uppercase leading-[0.82] tracking-normal sm:text-[6.8rem] lg:text-[8.5rem]">
              Plan visual futures.
            </h1>

            <p className="mt-7 max-w-xl text-lg font-semibold leading-8 text-[#5c554d]">
              Turn a real address into a creative planning wall: mapped zones, style systems,
              saved generations, and AI renders that make early development ideas feel tangible.
            </p>

            <div className="mt-7 flex flex-wrap gap-3">
              <ActionLink to={primaryHref}>
                {primaryLabel}
                <ArrowRight size={16} />
              </ActionLink>
            </div>

            <div className="mt-8 grid max-w-xl grid-cols-3 gap-3">
              <MiniStat icon={Map} label="Sites" value="Real" />
              <MiniStat icon={Layers3} label="Zones" value="Typed" />
              <MiniStat icon={ImageIcon} label="Renders" value="Saved" />
            </div>
          </div>

          <div>
            <MobileCollage />
            <DesktopCollage />
          </div>
        </main>
      </section>

      <section id="how-it-works" className="relative border-b-2 border-[#151515] bg-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-12 sm:px-6 lg:grid-cols-[0.8fr_1.2fr] lg:px-8">
          <div>
            <Pill className="border-[#151515] bg-[#0aa6a6] text-white">
              <WandSparkles size={13} />
              Built for fast planning
            </Pill>
            <h2 className="mt-6 max-w-lg text-4xl font-black uppercase leading-none sm:text-5xl">
              From map to image without losing the project.
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <FeatureCard
              icon={Building2}
              title="Draw the site"
              body="Use the map and zone tools to sketch buildings, roads, parks, and plazas against real context."
            />
            <FeatureCard
              icon={Palette}
              title="Set the vibe"
              body="Choose development types and style kits before generating so each image is grounded in the plan."
            />
            <FeatureCard
              icon={Camera}
              title="Compare renders"
              body="Save generations, move through images quickly, and keep the best visual direction attached to the project."
            />
          </div>
        </div>
      </section>

      <section className="bg-[#151515] px-4 py-8 text-white sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-5">
          <div className="flex flex-wrap gap-3 text-sm font-black uppercase">
            {['Version history', 'Saved images', 'Render comparisons'].map((item) => (
              <span key={item} className="inline-flex items-center gap-2 rounded-full border border-white/20 px-3 py-2">
                <Check size={14} className="text-[#c9ff3d]" />
                {item}
              </span>
            ))}
          </div>
          <Link
            to={primaryHref}
            className="inline-flex items-center gap-2 rounded-full bg-[#c9ff3d] px-5 py-3 text-sm font-black text-[#151515] hover:bg-[#d7ff66]"
          >
            {primaryLabel}
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </div>
  );
}
