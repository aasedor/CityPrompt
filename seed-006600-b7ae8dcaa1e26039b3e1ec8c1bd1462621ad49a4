import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { adminApi } from '@/services/api';

export function ConfirmRoleChangePage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No confirmation token provided.');
      return;
    }

    adminApi
      .confirmRoleChange(token)
      .then((user) => {
        setStatus('success');
        setMessage(`Role changed successfully. ${user.email} is now a ${user.role}.`);
      })
      .catch((err) => {
        setStatus('error');
        setMessage(
          err.response?.data?.detail || 'Failed to confirm role change. The link may be invalid or expired.',
        );
      });
  }, [token]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md rounded-2xl bg-white border border-primary-950/[0.08] p-8 shadow-elevated text-center backdrop-blur-xl">
        {status === 'loading' && (
          <>
            <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary-600" />
            <p className="mt-4 text-sm text-primary-950/50">Confirming role change...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-500/15">
              <CheckCircle className="h-7 w-7 text-green-400" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-primary-950">Role Change Confirmed</h2>
            <p className="mt-2 text-sm text-primary-950/50">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-500/15">
              <XCircle className="h-7 w-7 text-red-600" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-primary-950">Confirmation Failed</h2>
            <p className="mt-2 text-sm text-primary-950/50">{message}</p>
          </>
        )}

        {status !== 'loading' && (
          <Link
            to="/admin/users"
            className="mt-6 inline-block rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
          >
            Back to User Management
          </Link>
        )}
      </div>
    </div>
  );
}
