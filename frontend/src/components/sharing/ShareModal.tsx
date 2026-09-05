import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Copy, Trash2, Loader2, UserPlus } from 'lucide-react';
import { getApiErrorMessage, sharesApi, type ProjectShareInfo } from '@/services/api';
import { StudioDialog } from '@/features/projects/StudioControls';

interface ShareModalProps {
  projectId: string;
  projectName: string;
  onClose: () => void;
}
export function ShareModal({ projectId, projectName, onClose }: ShareModalProps) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState<'viewer' | 'editor'>('viewer');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [confirmRevoke, setConfirmRevoke] = useState<string | null>(null);
  const query = useQuery({ queryKey: ['shares', projectId], queryFn: () => sharesApi.list(projectId), retry: false });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ['shares', projectId] });
  const mutationError = (cause: unknown) => setError(getApiErrorMessage(cause, 'Sharing could not be updated. Please try again.'));
  const invite = useMutation({
    mutationFn: (details: { email: string; permission: string }) => sharesApi.share(projectId, details.email, details.permission),
    onSuccess: (share) => {
      queryClient.setQueryData<ProjectShareInfo[]>(['shares', projectId], (previous = []) => [...previous.filter((item) => item.id !== share.id), share]);
      void refresh();
      setEmail(''); setError('');
      setNotice('Invitation ready. Copy its invitation link below and send it to your teammate.');
    },
    onError: mutationError,
  });
  const revoke = useMutation({
    mutationFn: (shareId: string) => sharesApi.revoke(projectId, shareId),
    onSuccess: () => { void refresh(); setConfirmRevoke(null); setError(''); setNotice('Project access removed.'); },
    onError: mutationError,
  });
  const createPublic = useMutation({
    mutationFn: () => sharesApi.createPublicLink(projectId),
    onSuccess: () => { void refresh(); setError(''); setNotice('Presentation link enabled. Anyone with this link can view the plan and saved images and videos.'); },
    onError: mutationError,
  });
  const revokePublic = useMutation({
    mutationFn: () => sharesApi.revokePublicLink(projectId),
    onSuccess: () => { void refresh(); setError(''); setNotice('Presentation link disabled.'); },
    onError: mutationError,
  });
  const publicLink = query.data?.find((share) => share.is_public_link);
  const emailShares = query.data?.filter((share) => !share.is_public_link) ?? [];
  const publicUrl = publicLink?.invite_token ? window.location.origin + '/shared/' + encodeURIComponent(publicLink.invite_token) : '';
  const buttonClass = 'inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:opacity-50';
  const copy = async (url: string) => {
    try { await navigator.clipboard.writeText(url); setNotice('Link copied.'); setError(''); }
    catch { setError('Copy is unavailable in this browser. Select the link text and copy it manually.'); }
  };
  const unavailable = query.isLoading || Boolean(query.error);

  return <StudioDialog title={'Share “' + projectName + '”'} onClose={onClose}>
    <div className="mx-auto max-w-2xl space-y-6 p-2 text-slate-900">
      <section aria-labelledby="team-invite-heading">
        <h2 id="team-invite-heading" className="text-lg font-semibold">Invite a teammate</h2>
        <p className="mt-1 text-sm text-slate-600">Create an invitation for their email address, then copy and send them the link. They must sign in with that address to accept.</p>
        <form className="mt-3 flex flex-wrap items-end gap-2" onSubmit={(event) => {
          event.preventDefault();
          if (!email.trim() || invite.isPending || unavailable) return;
          setError(''); setNotice('');
          invite.mutate({ email: email.trim(), permission });
        }}>
          <label className="min-w-0 flex-1 text-sm font-semibold">Teammate email<input type="email" required value={email} disabled={invite.isPending || unavailable} onChange={(event) => setEmail(event.target.value)} placeholder="teammate@university.ca" className="mt-1 min-h-11 w-full rounded-lg border border-slate-300 px-3 font-normal" /></label>
          <label className="text-sm font-semibold">Access<select value={permission} disabled={invite.isPending || unavailable} onChange={(event) => setPermission(event.target.value as 'viewer' | 'editor')} className="mt-1 block min-h-11 rounded-lg border border-slate-300 px-3 font-normal"><option value="viewer">Can view</option><option value="editor">Can edit</option></select></label>
          <button type="submit" disabled={invite.isPending || unavailable || !email.trim()} className={buttonClass + ' bg-slate-900 text-white hover:bg-slate-700'}>{invite.isPending ? <Loader2 size={17} className="animate-spin" /> : <UserPlus size={17} />} Create invitation</button>
        </form>
      </section>

      {query.isLoading && <p role="status">Loading project access…</p>}
      {query.error && <div role="alert" className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">{getApiErrorMessage(query.error, 'Project access could not load. The project owner manages invitations.')} <button type="button" onClick={() => void query.refetch()} className={buttonClass}>Try again</button></div>}
      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {notice && <p role="status" className="rounded-lg bg-lime-50 p-3 text-sm text-slate-800">{notice}</p>}

      {emailShares.length > 0 && <section aria-labelledby="team-members-heading">
        <h2 id="team-members-heading" className="text-lg font-semibold">Team access</h2>
        <ul className="mt-3 space-y-3">{emailShares.map((share) => {
          const inviteUrl = share.invite_token ? window.location.origin + '/invite/' + encodeURIComponent(share.invite_token) : '';
          const pending = !share.user_id;
          return <li key={share.id} className="rounded-lg border border-slate-200 p-3">
            <div className="flex items-start justify-between gap-2"><div className="min-w-0">
              <p className="break-words font-semibold">{share.email}</p>
              <p className="mt-1 text-sm text-slate-600">{share.permission === 'editor' ? 'Can edit' : 'Can view'} · {pending ? 'Pending acceptance' : 'Accepted'}</p>
            </div><button type="button" aria-label={'Remove access for ' + share.email} onClick={() => setConfirmRevoke(share.id)} disabled={revoke.isPending} className={buttonClass}><Trash2 size={17} /></button></div>
            {pending && inviteUrl && <div className="mt-3 flex flex-wrap gap-2">
              <input aria-label={'Invitation link for ' + share.email} readOnly value={inviteUrl} onFocus={(event) => event.target.select()} className="min-h-11 min-w-0 flex-1 rounded-lg border border-slate-300 px-2 text-sm" />
              <button type="button" onClick={() => void copy(inviteUrl)} className={buttonClass}><Copy size={16} /> Copy invitation</button>
            </div>}
            {confirmRevoke === share.id && <div className="mt-3 rounded bg-red-50 p-3 text-sm">
              <p>Remove this person's project access and invitation?</p>
              <div className="mt-2 flex gap-2"><button type="button" disabled={revoke.isPending} onClick={() => revoke.mutate(share.id)} className={buttonClass}>Remove access</button><button type="button" onClick={() => setConfirmRevoke(null)} className={buttonClass}>Keep access</button></div>
            </div>}
          </li>;
        })}</ul>
      </section>}

      <section aria-labelledby="presentation-link-heading" className="border-t border-slate-200 pt-5">
        <h2 id="presentation-link-heading" className="text-lg font-semibold">Presentation link</h2>
        <p className="mt-1 text-sm text-slate-600">Anyone with this link can view your plan and saved images and videos. It does not allow editing. Disable it when you no longer want to share.</p>
        {publicUrl ? <div className="mt-3 space-y-2">
          <div className="flex flex-wrap gap-2"><input aria-label="Public presentation link" readOnly value={publicUrl} onFocus={(event) => event.target.select()} className="min-h-11 min-w-0 flex-1 rounded-lg border border-slate-300 px-2 text-sm" /><button type="button" onClick={() => void copy(publicUrl)} className={buttonClass}><Copy size={16} /> Copy presentation link</button></div>
          <div className="flex flex-wrap gap-2"><a href={publicUrl} target="_blank" rel="noreferrer" className={buttonClass}>Preview presentation</a><button type="button" onClick={() => revokePublic.mutate()} disabled={revokePublic.isPending} className={buttonClass}>Disable presentation link</button></div>
        </div> : <button type="button" disabled={createPublic.isPending || unavailable} onClick={() => createPublic.mutate()} className={buttonClass + ' mt-3'}>{createPublic.isPending ? 'Creating link…' : 'Enable presentation link'}</button>}
      </section>
    </div>
  </StudioDialog>;
}
