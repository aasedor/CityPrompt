import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Project, SavedRender, SiteZone } from '@/types';
import { resolveApiFileUrl } from '@/services/api';
import type { VideoAttempt } from '@/components/viewer/VideoGeneratePanel';
import { StudentPlanningReport } from '@/features/studentReports/StudentPlanningReport';
import { SharedPlanPreview } from './SharedPlanPreview';
import { savedRenderNotice } from '@/utils/renderPresentation';

/** Accepted viewers can inspect a team's work without being offered edits. */
export function ReadOnlyProject({ project, zones, renders, videos = [] }: { project: Project; zones: SiteZone[]; renders: SavedRender[]; videos?: VideoAttempt[] }) {
  const [reportOpen, setReportOpen] = useState(false);
  return <main className="mx-auto max-w-6xl space-y-6 text-slate-900">
    <Link to="/projects" className="inline-flex min-h-11 items-center font-semibold underline">Back to projects</Link>
    <header><p className="text-sm font-semibold text-teal-800">Shared project · View access</p><h1 className="mt-1 text-3xl font-bold">{project.name}</h1><p className="mt-2 text-slate-600">You can explore the plan and report. Ask the owner for editor access to contribute to the design.</p></header>
    <section aria-label="Community plan" className="rounded-xl border bg-white p-5"><SharedPlanPreview zones={zones} buildings={project.buildings} /></section>
    <button onClick={() => setReportOpen((open) => !open)} aria-expanded={reportOpen} className="min-h-11 rounded-lg bg-teal-800 px-5 font-semibold text-white">{reportOpen ? 'Hide planning report' : 'View planning report'}</button>
    {reportOpen && <StudentPlanningReport projectId={project.id} canEdit={false} />}
    <section aria-label="Saved presentation images" className="grid gap-4 sm:grid-cols-2">
      {renders.filter((render) => render.variant !== 'provider_original').map((render) => <figure key={render.id} className="rounded-xl border bg-white p-3">
        <a href={resolveApiFileUrl(render.image_url)} target="_blank" rel="noreferrer"><img src={resolveApiFileUrl(render.image_url)} alt={render.style || 'Saved community view'} className="aspect-video w-full object-contain" /></a>
        <figcaption className="mt-2 text-sm text-slate-600">{render.style || 'Community view'} · {new Date(render.created_at).toLocaleDateString()} {savedRenderNotice(render)}</figcaption>
      </figure>)}
    </section>
    {videos.some((video) => video.video_url) && <section aria-label="Saved presentation videos" className="grid gap-4 sm:grid-cols-2">
      {videos.filter((video) => video.video_url).map((video) => <figure key={video.id} className="rounded-xl border bg-white p-3">
        <video src={resolveApiFileUrl(video.video_url!)} controls playsInline preload="metadata" className="aspect-video w-full bg-slate-950" />
        <figcaption className="mt-2 text-sm text-slate-600">Community video · {new Date(video.created_at).toLocaleDateString()} · Review against the plan before presenting</figcaption>
      </figure>)}
    </section>}
  </main>;
}
