import { Link } from 'react-router-dom';
import { ArrowRight, Footprints, Image as ImageIcon, Layers3, Map, Trees } from 'lucide-react';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { useAuthStore } from '@/store';
import { LoginForm } from '@/features/auth/LoginPage';

const ink = 'text-[var(--city-ink)]';
const muted = 'text-[var(--city-muted)]';
const panel = 'rounded-xl border-2 border-[var(--city-ink)] bg-[var(--city-surface)]';

function BrandMark() {
  return <Link to="/" className="inline-flex items-center gap-2 rounded-md py-1">
    <img src="/images/city-prompt-logo.png" alt="" width={36} height={36} className="h-9 w-9 dark:invert" />
    <span className="text-sm font-black uppercase">City Prompt</span>
  </Link>;
}

/** An illustrative plan, rather than a screenshot of an invented app state.
 * Static vector geometry keeps the first view independent of map/3D loading. */
function CommunityPlan() {
  return <figure className={`${panel} mt-7 overflow-hidden`}>
    <div className="flex items-center justify-between gap-2 border-b border-[var(--city-ink)] px-4 py-3 text-xs font-bold">
      <span className="inline-flex items-center gap-2"><Layers3 size={16} /> A community, zone by zone</span>
      <span className={muted}>Illustrative plan</span>
    </div>
    <svg viewBox="0 0 640 300" role="img" aria-labelledby="community-plan-title community-plan-description" className="block w-full bg-[#f3eddf]">
      <title id="community-plan-title">An illustrated community zoning study</title>
      <desc id="community-plan-description">Homes, a shared courtyard and an irregular park connected by streets and a walking path inside a site boundary.</desc>
      <defs>
        <pattern id="community-plan-grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0H0V20" fill="none" stroke="#ded7c8" strokeWidth="0.6" />
        </pattern>
      </defs>
      <rect width="640" height="300" fill="url(#community-plan-grid)" />
      <g stroke="#151515" strokeWidth="1.5" strokeLinejoin="round">
        <path d="M45 45H265V125H45Z" fill="#f7b19b" />
        <path d="M45 160H265V260H45Z" fill="#f7b19b" />
        <path d="M300 45H430V140H300Z" fill="#95d5ce" />
        <path d="M300 170H410L445 205L420 260H300Z" fill="#95d5ce" />
        <path d="M465 45H595V230L465 260L445 185L465 140Z" fill="#c9ee86" />
      </g>
      <g fill="#fff9ec" stroke="#715548" strokeWidth="1.3">
        {[65,110,155,200].map(x => <g key={x}><rect x={x} y="64" width="30" height="39" /><path d={`M${x} 77h30M${x + 15} 64v13`} /></g>)}
        {[65,110,155,200].map(x => <g key={x}><rect x={x} y="184" width="30" height="49" /><path d={`M${x} 198h30M${x + 15} 184v14`} /></g>)}
        <path d="M317 62H412V119H385V84H344V119H317Z" />
        <path d="M320 189H379V213H405V243H320Z" />
      </g>
      <path d="M38 143H437M282 38V265" stroke="#ffffff" strokeWidth="18" />
      <path d="M38 143H437M282 38V265" stroke="#c8bdad" strokeWidth="1" strokeDasharray="4 5" />
      <path d="M515 60C575 92 477 142 536 192L568 214" fill="none" stroke="#fff9ec" strokeWidth="10" />
      <g fill="#579565" stroke="#315d3b" strokeWidth="1">
        {[[488,72],[565,62],[577,110],[487,149],[574,167],[479,211],[529,234]].map(([cx,cy]) => <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="9" />)}
      </g>
      <g fill="#151515" fontFamily="system-ui, sans-serif" fontSize="10" fontWeight="600">
        <text x="153" y="119" textAnchor="middle">HOMES</text>
        <text x="365" y="133" textAnchor="middle">COURTYARD</text>
        <text x="365" y="255" textAnchor="middle">SHARED SPACE</text>
        <text x="542" y="147" textAnchor="middle">PARK</text>
      </g>
      <path d="M30 30H610V245L460 280H30Z" fill="none" stroke="#151515" strokeWidth="1.5" strokeDasharray="6 5" />
    </svg>
    <figcaption className={`px-4 py-3 text-xs leading-5 ${muted}`}>
      Draw the zones. Connect the places. Give your proposal its own character.
    </figcaption>
  </figure>;
}

const workflow = [
  { number: '01', label: 'Site', title: 'Read the place.', icon: Map,
    description: 'Choose a real location and draw your site boundary. See Calgary land-use districts and assessment context, then make separate maps of existing and proposed land use.' },
  { number: '02', label: 'Design', title: 'Shape a community.', icon: Trees,
    description: 'Find buildings by land use, plot size and architectural style. Place buildings, draw parks and street routes, and edit the composition as your idea develops.' },
  { number: '03', label: 'Present', title: 'Bring people into the idea.', icon: Footprints,
    description: 'Explore at street level, choose a useful camera view and export your zoning study. Capture the 3D design or create an AI still-image study for your presentation.' },
];

function StudioEntry({ authenticated }: { authenticated: boolean }) {
  return <section id="studio" aria-labelledby="studio-title" className="scroll-mt-6 lg:pt-3">
    <p className={`text-xs font-bold uppercase tracking-widest ${muted}`}>{authenticated ? 'Your studio' : 'Start your next study'}</p>
    <h2 id="studio-title" className="mt-3 text-3xl font-black leading-tight">{authenticated ? 'Welcome back.' : 'A place for your ideas.'}</h2>
    <p className={`mb-6 mt-3 text-sm leading-6 ${muted}`}>
      {authenticated ? 'Return to your communities, saved views and planning studies.' : 'Sign in to open your projects and start designing.'}
    </p>
    {authenticated ? <div className={`${panel} p-6 shadow-[5px_5px_0_0_var(--city-ink)]`}>
      <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-full bg-lime-300 text-slate-950"><Map size={22} /></div>
      <p className="text-lg font-bold">Pick up where you left off.</p>
      <Link to="/projects" className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-full bg-[var(--city-ink)] px-4 py-3 text-sm font-bold text-[var(--city-surface)] hover:opacity-90">
        Open projects <ArrowRight size={16} />
      </Link>
    </div> : <LoginForm />}
  </section>;
}

function ImageStudy() {
  return <section aria-labelledby="image-study-title" className={`${panel} mt-10 overflow-hidden sm:mt-14`}>
    <div className="flex flex-wrap items-start justify-between gap-4 p-5 sm:p-6">
      <div>
        <p className={`text-xs font-bold uppercase tracking-widest ${muted}`}>An image study</p>
        <h2 id="image-study-title" className="mt-2 text-2xl font-black">Give the proposal a point of view.</h2>
      </div>
      <p className={`max-w-sm text-sm leading-6 ${muted}`}>Use your mapped design to guide an AI image. Compare it with the 3D view as you refine the presentation.</p>
    </div>
    <div className="grid gap-px bg-[var(--city-ink)] sm:grid-cols-2">
      <figure className="bg-[var(--city-surface)]">
        <img src="/images/landing-prompt.jpg" alt="A drawn development zone on a real Calgary site" width={2048} height={777} loading="lazy" decoding="async" className="aspect-[2.6] w-full object-cover" />
        <figcaption className="flex items-center gap-2 px-5 py-3 text-xs font-semibold"><Layers3 size={15} /> Mapped design</figcaption>
      </figure>
      <figure className="bg-[var(--city-surface)]">
        <img src="/images/landing-render.png" alt="An AI image study of a terraced building on the same Calgary site" width={2035} height={773} loading="lazy" decoding="async" className="aspect-[2.6] w-full object-cover" />
        <figcaption className="flex items-center gap-2 px-5 py-3 text-xs font-semibold"><ImageIcon size={15} /> AI image study</figcaption>
      </figure>
    </div>
  </section>;
}

export function LandingPage() {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const isLoading = useAuthStore(state => state.isLoading);
  if (isLoading) return <div role="status" aria-label="Loading City Prompt" className="flex min-h-screen items-center justify-center bg-[var(--city-bg)]">
    <div aria-hidden="true" className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--city-ink)] border-t-transparent motion-reduce:animate-none" />
  </div>;

  return <div className={`min-h-screen bg-[var(--city-bg)] ${ink}`}>
    <a href="#main-content" className="sr-only z-50 rounded bg-[var(--city-surface)] p-3 focus:not-sr-only focus:absolute">Skip to content</a>
    <header className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-5 sm:px-6 lg:px-8">
      <BrandMark />
      <nav aria-label="Account" className="flex items-center gap-2">
        <ThemeToggle />
        {isAuthenticated ? <Link to="/projects" className="inline-flex min-h-11 items-center gap-2 rounded-full border-2 border-[var(--city-ink)] bg-lime-300 px-4 text-xs font-bold text-slate-950 hover:bg-lime-200">Projects <ArrowRight size={14} /></Link>
          : <a href="#studio" className="inline-flex min-h-11 items-center gap-2 rounded-full border-2 border-[var(--city-ink)] bg-lime-300 px-4 text-xs font-bold text-slate-950 hover:bg-lime-200">Sign in <ArrowRight size={14} /></a>}
      </nav>
    </header>
    <main id="main-content" className="mx-auto max-w-7xl px-4 pb-10 pt-7 sm:px-6 sm:pt-12 lg:px-8">
      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_380px] lg:gap-16">
        <section aria-labelledby="landing-title">
          <p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest"><span className="h-2 w-2 rounded-full bg-[#ff5a3d]" /> A studio for community design</p>
          <h1 id="landing-title" className="mt-5 text-5xl font-black leading-[0.98] tracking-tight sm:text-6xl xl:text-7xl">Your site.<br />Your community.</h1>
          <p className={`mt-5 max-w-xl text-base leading-7 sm:text-lg sm:leading-8 ${muted}`}>Start with a real place. Shape its buildings, parks and streets, then explore your proposal in 3D and explain it with maps and still images.</p>
          <CommunityPlan />
        </section>
        <StudioEntry authenticated={isAuthenticated} />
      </div>
      <section aria-labelledby="workflow-title" className="mt-12 border-t-2 border-[var(--city-ink)] pt-7 sm:mt-16">
        <h2 id="workflow-title" className="text-2xl font-black">From a real site to a shared idea.</h2>
        <div className="mt-6 grid gap-6 md:grid-cols-3">
          {workflow.map(({number,label,title,icon:Icon,description}) => <article key={number}>
            <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest"><span className={`flex h-9 w-9 items-center justify-center rounded-full border border-[var(--city-ink)] ${muted}`}>{number}</span><Icon size={18} />{label}</div>
            <h3 className="mt-4 text-xl font-black">{title}</h3>
            <p className={`mt-3 text-sm leading-7 ${muted}`}>{description}</p>
          </article>)}
        </div>
      </section>
      <ImageStudy />
    </main>
    <footer className={`mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 border-t border-[var(--city-ink)] px-4 py-6 text-xs sm:px-6 lg:px-8 ${muted}`}>
      <p>City Prompt · Urban design learning & early planning</p>
      {!isAuthenticated && <Link to="/register" className="inline-flex min-h-11 items-center gap-2 font-bold underline underline-offset-4">Create an account <ArrowRight size={14} /></Link>}
    </footer>
  </div>;
}
