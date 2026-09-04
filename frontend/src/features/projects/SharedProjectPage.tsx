import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api, getApiErrorMessage, resolveApiFileUrl, sharesApi } from '@/services/api';
import type { SavedRender, SiteZone } from '@/types';
import { SharedPlanPreview } from './SharedPlanPreview';

interface PublicVideo { id: string; status: string; video_url?: string | null; created_at: string; }
const isMediaUrl = (url: string) => /^https?:\/\//i.test(url) || url.startsWith('/api/v1/files/');

export function SharedProjectPage() {
  const { token } = useParams<{ token: string }>();
  const projectQuery = useQuery({
    queryKey: ['shared-project', token],
    queryFn: () => sharesApi.getSharedProject(token!),
    enabled: Boolean(token), retry: false,
  });
  const project = projectQuery.data;
  const zones = useQuery({
    queryKey: ['shared-project-zones', token, project?.id],
    queryFn: async () => (await api.get<SiteZone[]>('/api/v1/site-zones/projects/' + project!.id + '/zones', { params: { share_token: token } })).data,
    enabled: Boolean(project && token), retry: false,
  });
  const renders = useQuery({
    queryKey: ['shared-project-renders', token, project?.id],
    queryFn: async () => (await api.get<SavedRender[]>('/api/v1/render/projects/' + project!.id + '/renders', { params: { share_token: token } })).data,
    enabled: Boolean(project && token), retry: false,
  });
  const videos = useQuery({
    queryKey: ['shared-project-videos', token, project?.id],
    queryFn: async () => (await api.get<{ attempts: PublicVideo[] }>('/api/v1/video/projects/' + project!.id, { params: { share_token: token } })).data.attempts,
    enabled: Boolean(project && token), retry: false,
  });
  if (projectQuery.isLoading) return <main className="flex min-h-screen items-center justify-center bg-slate-50 p-4"><p role="status">Loading shared presentation…</p></main>;
  if (projectQuery.error || !project) return <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-4 text-center text-slate-900">
    <h1 className="text-2xl font-bold">Presentation unavailable</h1>
    <p role="alert" className="mt-3 max-w-md text-slate-600">{getApiErrorMessage(projectQuery.error, 'This link may have been revoked. Ask the project owner for a current presentation link.')}</p>
    <button type="button" onClick={() => void projectQuery.refetch()} className="mt-5 min-h-11 rounded-lg border border-slate-300 bg-white px-4 font-semibold">Try again</button>
  </main>;
  const mediaUrl = (url: string) => resolveApiFileUrl(url, { projectId: project.id, shareToken: token });
  const completeVideos = (videos.data ?? []).filter((video) => video.status === 'complete' && video.video_url);
  return <div className="min-h-screen bg-slate-50 text-slate-900">
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6">
        <Link to="/" className="text-lg font-bold">City Prompt</Link>
        <span className="rounded-full bg-lime-100 px-3 py-1 text-sm font-semibold">Shared presentation · Read only</span>
      </div>
    </header>
    <main className="mx-auto max-w-6xl space-y-8 px-4 py-6 sm:px-6 sm:py-8">
      <div><h1 className="break-words text-3xl font-bold">{project.name}</h1>{project.description && <p className="mt-3 max-w-3xl whitespace-pre-wrap text-base leading-relaxed text-slate-600">{project.description}</p>}{project.location?.address && <p className="mt-2 text-sm text-slate-500">{project.location.address}</p>}</div>
      <section aria-labelledby="shared-plan-title" className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-6">
        <h2 id="shared-plan-title" className="mb-4 text-xl font-bold">Community plan</h2>
        {zones.isLoading ? <p role="status">Loading saved drawings…</p> : zones.error ? <LoadError error={zones.error} fallback="The saved plan could not load." onRetry={() => void zones.refetch()} /> : <SharedPlanPreview zones={zones.data ?? []} buildings={project.buildings} />}
      </section>
      <section aria-labelledby="shared-images-title">
        <h2 id="shared-images-title" className="text-xl font-bold">Saved presentation images</h2>
        <p className="mt-1 text-sm text-slate-600">Images may show earlier design versions. Compare them with the saved plan above.</p>
        {renders.isLoading ? <p role="status" className="mt-3">Loading images…</p> : renders.error ? <LoadError error={renders.error} fallback="Saved images could not load." onRetry={() => void renders.refetch()} /> : !renders.data?.length ? <p className="mt-3 text-slate-600">No presentation images have been saved yet.</p> : <div className="mt-4 grid gap-4 sm:grid-cols-2">{renders.data.map((render, index) => <SharedImage key={render.id} url={mediaUrl(render.image_url)} label={project.name + ' — presentation image ' + (index + 1)} createdAt={render.created_at} />)}</div>}
      </section>
      <section aria-labelledby="shared-videos-title">
        <h2 id="shared-videos-title" className="text-xl font-bold">Saved videos</h2>
        {videos.isLoading ? <p role="status" className="mt-3">Loading videos…</p> : videos.error ? <LoadError error={videos.error} fallback="Saved videos could not load." onRetry={() => void videos.refetch()} /> : !completeVideos.length ? <p className="mt-3 text-slate-600">No completed videos have been saved yet.</p> : <div className="mt-4 grid gap-4 sm:grid-cols-2">{completeVideos.map((video, index) => <SharedVideo key={video.id} url={mediaUrl(video.video_url!)} label={project.name + ' — video ' + (index + 1)} createdAt={video.created_at} />)}</div>}
      </section>
    </main>
  </div>;
}
function LoadError({ error, fallback, onRetry }: { error: unknown; fallback: string; onRetry: () => void }) {
  return <div role="alert" className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">{getApiErrorMessage(error, fallback)} <button type="button" onClick={onRetry} className="ml-2 min-h-11 px-2 font-semibold underline">Try again</button></div>;
}
function SharedImage({ url, label, createdAt }: { url: string; label: string; createdAt: string }) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const usable = isMediaUrl(url) && failedUrl !== url;
  return <figure className="overflow-hidden rounded-xl border border-slate-200 bg-white">
    {usable ? <a href={url} target="_blank" rel="noreferrer" aria-label={'Open ' + label}><img src={url} alt={label} loading="lazy" referrerPolicy="no-referrer" onError={() => setFailedUrl(url)} className="aspect-video w-full object-contain" /></a> : <p role="status" className="p-6 text-sm text-slate-600">This saved image is unavailable. Its file or public access may have changed.</p>}
    <figcaption className="p-3 text-sm text-slate-600">{label}<br /><time dateTime={createdAt}>{new Date(createdAt).toLocaleString()}</time></figcaption>
  </figure>;
}
function SharedVideo({ url, label, createdAt }: { url: string; label: string; createdAt: string }) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const usable = isMediaUrl(url) && failedUrl !== url;
  return <figure className="overflow-hidden rounded-xl border border-slate-200 bg-white">
    {usable ? <video src={url} aria-label={label} controls preload="none" playsInline onError={() => setFailedUrl(url)} className="aspect-video w-full bg-slate-900" /> : <p role="status" className="p-6 text-sm text-slate-600">This saved video is unavailable. Its file or public access may have changed.</p>}
    <figcaption className="p-3 text-sm text-slate-600">{label}<br /><time dateTime={createdAt}>{new Date(createdAt).toLocaleString()}</time></figcaption>
  </figure>;
}
