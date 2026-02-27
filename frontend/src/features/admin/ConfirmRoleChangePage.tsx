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
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg text-center">
        {status === 'loading' && (
          <>
            <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary-600" />
            <p className="mt-4 text-sm text-gray-500">Confirming role change...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <CheckCircle className="h-7 w-7 text-green-600" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-gray-900">Role Change Confirmed</h2>
            <p className="mt-2 text-sm text-gray-600">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
              <XCircle className="h-7 w-7 text-red-600" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-gray-900">Confirmation Failed</h2>
            <p className="mt-2 text-sm text-gray-600">{message}</p>
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
