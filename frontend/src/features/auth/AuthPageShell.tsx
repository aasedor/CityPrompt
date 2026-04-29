import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Image as ImageIcon, Layers3, Sparkles } from 'lucide-react';

export const authFormClassName =
  'space-y-4 rounded-lg border-2 border-[#151515] bg-white p-5 shadow-[10px_10px_0_0_#151515] sm:p-6';

export const authInputClassName =
  'w-full rounded-lg border-2 border-[#151515] bg-[#fff9ec] px-3.5 py-2.5 text-sm font-semibold text-[#151515] placeholder:text-[#151515]/35 transition focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#c9ff3d]';

export const authLabelClassName =
  'mb-1 block text-xs font-black uppercase text-[#151515]/70';

export const authSubmitClassName =
  'inline-flex w-full items-center justify-center rounded-full border-2 border-[#151515] bg-[#151515] px-4 py-3 text-sm font-black text-white shadow-[5px_5px_0_0_#151515] transition hover:bg-[#2a2a2a] active:translate-x-0.5 active:translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60';

export const authErrorClassName =
  'rounded-lg border-2 border-red-700 bg-red-50 px-3 py-2 text-sm font-bold text-red-700';

export const authSuccessClassName =
  'rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-3 py-3 text-sm font-black text-[#151515]';

interface AuthPageShellProps {
  eyebrow: string;
  title: string;
  description: string;
  sideTitle: string;
  sideDescription: string;
  children: ReactNode;
}

function GridBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-[0.16]"
      style={{
        backgroundImage:
          'linear-gradient(#151515 1px, transparent 1px), linear-gradient(90deg, #151515 1px, transparent 1px)',
        backgroundSize: '32px 32px',
      }}
    />
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

export function AuthPageShell({
  eyebrow,
  title,
  description,
  sideTitle,
  sideDescription,
  children,
}: AuthPageShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#fff9ec] text-[#151515]">
      <GridBackground />

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="inline-flex items-center gap-2 rounded-md px-1 py-1">
          <img src="/images/city-prompt-logo.png" alt="City Prompt" className="h-9 w-9" />
          <span className="text-sm font-black uppercase">City Prompt</span>
        </Link>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-white px-4 py-2 text-xs font-black uppercase shadow-[3px_3px_0_0_#151515] hover:bg-[#c9ff3d]"
        >
          <ArrowLeft size={14} />
          Home
        </Link>
      </header>

      <main className="relative z-10 mx-auto grid min-h-[calc(100vh-76px)] max-w-7xl items-center gap-8 px-4 pb-10 sm:px-6 lg:grid-cols-[minmax(0,1fr)_440px] lg:px-8">
        <section className="hidden lg:block">
          <span className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#ff5a3d] px-3 py-1 text-xs font-black uppercase text-white">
            <Sparkles size={13} />
            {eyebrow}
          </span>
          <h2 className="mt-7 max-w-4xl text-[5.4rem] font-black uppercase leading-[0.84] tracking-normal">
            {sideTitle}
          </h2>
          <p className="mt-6 max-w-lg text-lg font-semibold leading-8 text-[#5c554d]">
            {sideDescription}
          </p>

          <div className="relative mt-10 h-80 max-w-[36rem]">
            <MiniTile
              src="/images/style-lab-pic2.png"
              label="Prompt view"
              className="absolute left-0 top-0 z-10 h-44 w-72 rotate-[-5deg]"
            />
            <MiniTile
              src="/images/style-lab-render.png"
              label="Final render"
              className="absolute left-52 top-20 z-20 h-40 w-72 rotate-[4deg]"
            />
            <div className="absolute bottom-2 left-4 z-30 rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-4 py-3 shadow-[5px_5px_0_0_#151515]">
              <div className="flex items-center gap-2 text-sm font-black uppercase">
                <Layers3 size={17} />
                Map to render
              </div>
            </div>
            <div className="absolute bottom-2 left-[23rem] z-30 rounded-full border-2 border-[#151515] bg-[#0aa6a6] px-4 py-2 text-xs font-black uppercase text-white shadow-[4px_4px_0_0_#151515]">
              <ImageIcon size={14} className="mr-1 inline" />
              Saved
            </div>
          </div>
        </section>

        <section>
          <div className="mb-6">
            <span className="inline-flex items-center gap-2 rounded-full border-2 border-[#151515] bg-[#c9ff3d] px-3 py-1 text-xs font-black uppercase">
              {eyebrow}
            </span>
            <h1 className="mt-4 text-4xl font-black uppercase leading-none tracking-normal sm:text-5xl">
              {title}
            </h1>
            <p className="mt-3 text-sm font-semibold leading-6 text-[#5c554d]">
              {description}
            </p>
          </div>

          {children}
        </section>
      </main>
    </div>
  );
}
