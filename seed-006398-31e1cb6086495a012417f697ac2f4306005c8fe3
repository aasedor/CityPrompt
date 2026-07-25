import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Link2, Copy, Check, Trash2, Loader2, UserPlus } from 'lucide-react';
import { sharesApi } from '@/services/api';
import type { ProjectShareInfo } from '@/services/api';

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
  const [copied, setCopied] = useState(false);

  const { data: shares, isLoading } = useQuery({
    queryKey: ['shares', projectId],
    queryFn: () => sharesApi.list(projectId),
  });

  const shareMutation = useMutation({
    mutationFn: () => sharesApi.share(projectId, email, permission),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shares', projectId] });
      setEmail('');
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to share project');
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (shareId: string) => sharesApi.revoke(projectId, shareId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shares', projectId] });
    },
  });

  const publicLinkMutation = useMutation({
    mutationFn: () => sharesApi.createPublicLink(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shares', projectId] });
    },
  });

  const revokePublicLinkMutation = useMutation({
    mutationFn: () => sharesApi.revokePublicLink(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shares', projectId] });
    },
  });

  const publicLink = shares?.find((s) => s.is_public_link);
  const emailShares = shares?.filter((s) => !s.is_public_link) || [];

  const handleInvite = () => {
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    setError('');
    shareMutation.mutate();
  };

  const handleCopyLink = async () => {
    if (!publicLink?.invite_token) return;
    const url = `${window.location.origin}/shared/${publicLink.invite_token}`;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-primary-950/60 backdrop-blur-sm sm:items-center" onClick={onClose}>
      <div className="w-full max-w-md rounded-t-2xl bg-white/95 backdrop-blur-xl border border-primary-950/[0.08] p-5 shadow-elevated animate-slide-up sm:rounded-2xl sm:p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-primary-950">Share "{projectName}"</h2>
          <button onClick={onClose} className="rounded-md p-1 text-primary-950/50 hover:bg-primary-950/[0.04] hover:text-primary-950/60">
            <X size={20} />
          </button>
        </div>

        {/* Invite by email */}
        <div className="mt-4">
          <div className="flex gap-2">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleInvite()}
              className="input-base flex-1"
            />
            <select
              value={permission}
              onChange={(e) => setPermission(e.target.value as 'viewer' | 'editor')}
              className="input-base px-2"
            >
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
            </select>
            <button
              onClick={handleInvite}
              disabled={shareMutation.isPending}
              className="btn-primary !px-3"
            >
              {shareMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />}
            </button>
          </div>
          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>

        {/* Shared users list */}
        {emailShares.length > 0 && (
          <div className="mt-4 space-y-2">
            <h3 className="text-xs font-semibold uppercase text-primary-950/50">Shared with</h3>
            {emailShares.map((share) => (
              <ShareRow key={share.id} share={share} onRevoke={() => revokeMutation.mutate(share.id)} revoking={revokeMutation.isPending} />
            ))}
          </div>
        )}

        {/* Public link section */}
        <div className="mt-5 border-t border-primary-950/[0.08] pt-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Link2 size={16} className="text-primary-950/50" />
              <span className="text-sm font-medium text-primary-950/60">Public link</span>
            </div>
            {publicLink ? (
              <button
                onClick={() => revokePublicLinkMutation.mutate()}
                disabled={revokePublicLinkMutation.isPending}
                className="text-xs font-medium text-red-600 hover:text-red-300"
              >
                Disable
              </button>
            ) : (
              <button
                onClick={() => publicLinkMutation.mutate()}
                disabled={publicLinkMutation.isPending}
                className="text-xs font-medium text-primary-500 hover:text-primary-400"
              >
                {publicLinkMutation.isPending ? 'Creating...' : 'Enable'}
              </button>
            )}
          </div>
          {publicLink && (
            <div className="mt-2 flex items-center gap-2">
              <input
                readOnly
                value={`${window.location.origin}/shared/${publicLink.invite_token}`}
                className="flex-1 truncate rounded-lg bg-primary-950/[0.02] px-3 py-1.5 text-xs text-primary-950/50"
              />
              <button
                onClick={handleCopyLink}
                className="rounded-lg bg-primary-950/[0.04] p-1.5 text-primary-950/50 hover:bg-primary-950/[0.08]"
              >
                {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
              </button>
            </div>
          )}
        </div>

        {isLoading && (
          <div className="mt-4 text-center text-sm text-primary-950/50">
            <Loader2 size={16} className="mx-auto animate-spin" />
          </div>
        )}
      </div>
    </div>
  );
}

function ShareRow({ share, onRevoke, revoking }: { share: ProjectShareInfo; onRevoke: () => void; revoking: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-primary-950/[0.08] px-3 py-2">
      <div>
        <p className="text-sm font-medium text-primary-950/60">{share.email}</p>
        <p className="text-xs capitalize text-primary-950/50">{share.permission}</p>
      </div>
      <button
        onClick={onRevoke}
        disabled={revoking}
        className="rounded-md p-1 text-primary-950/50 hover:bg-red-50 hover:text-red-500"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}
