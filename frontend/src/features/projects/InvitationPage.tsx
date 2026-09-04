import { Link, useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi, getApiErrorMessage, sharesApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { resetSessionState } from '@/utils/sessionReset';

export function InvitationPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, isLoading: authLoading, logout } = useAuthStore();
  const invitation = useQuery({ queryKey: ['invitation', token], queryFn: () => sharesApi.getInvitation(token!), enabled: Boolean(token), retry: false });
  const acceptance = useMutation({
    mutationFn: () => sharesApi.acceptInvitation(token!),
    onSuccess: (share) => {
      void queryClient.invalidateQueries({ queryKey: ['projects'] });
      void queryClient.invalidateQueries({ queryKey: ['shared-with-me'] });
      navigate('/projects/' + share.project_id, { replace: true });
    },
  });
  const returnTo = '/invite/' + encodeURIComponent(token ?? '');
  const loginPath = '/login?returnTo=' + encodeURIComponent(returnTo);
  const registerPath = '/register?returnTo=' + encodeURIComponent(returnTo);
  const details = invitation.data;
  const correctAccount = user && details && user.email.toLowerCase() === details.email.toLowerCase();
  const buttonClass = 'inline-flex min-h-11 items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:opacity-50';

  return <main className="flex min-h-screen items-center justify-center bg-slate-50 p-4 text-slate-900">
    <section className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-lg">
      <p className="text-sm font-semibold text-slate-600">City Prompt · Project invitation</p>
      {invitation.isLoading || authLoading ? <p role="status" className="mt-4">Loading invitation…</p> : invitation.error || !details ? <>
        <h1 className="mt-3 text-2xl font-bold">Invitation unavailable</h1>
        <p role="alert" className="mt-3 text-slate-600">{getApiErrorMessage(invitation.error, 'This invitation may have been revoked. Ask the project owner for a current link.')}</p>
        <button type="button" onClick={() => void invitation.refetch()} className={buttonClass + ' mt-4'}>Try again</button>
      </> : <>
        <h1 className="mt-3 break-words text-2xl font-bold">Join {details.project_name}</h1>
        <p className="mt-3 text-slate-700">Invited account: <strong className="break-words">{details.email}</strong></p>
        <p className="mt-2 text-slate-700">Access: {details.permission === 'editor' ? 'view and edit this project' : 'view this project'}.</p>
        {!user ? <>
          <p className="mt-4 text-slate-600">Sign in or create an account with the invited email address, then return here to accept.</p>
          <div className="mt-5 flex flex-wrap gap-3"><Link to={loginPath} className={buttonClass + ' bg-slate-900 text-white'}>Sign in to continue</Link><Link to={registerPath} className={buttonClass}>Create account</Link></div>
        </> : correctAccount ? <>
          <p className="mt-4 text-sm text-slate-600">Signed in as {user.email}.</p>
          <button type="button" disabled={acceptance.isPending} onClick={() => acceptance.mutate()} className={buttonClass + ' mt-5 bg-slate-900 text-white'}>{acceptance.isPending ? 'Opening project…' : details.accepted ? 'Open shared project' : 'Accept invitation'}</button>
        </> : <>
          <p role="alert" className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-950">You are signed in as {user.email}. This invitation is for {details.email}.</p>
          <button type="button" onClick={() => { authApi.logout(); resetSessionState(queryClient); logout(); navigate(loginPath, { replace: true }); }} className={buttonClass + ' mt-4'}>Sign in with the invited account</button>
        </>}
        {acceptance.error && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-800">{getApiErrorMessage(acceptance.error, 'The invitation could not be accepted. Please try again.')}</p>}
      </>}
    </section>
  </main>;
}
