import { RefreshCw, DollarSign, Bot, AlertTriangle } from 'lucide-react';
import type { ApiBalanceResponse, ProviderBalance } from '@/services/api';

interface Props {
  data: ApiBalanceResponse | null;
  loading?: boolean;
  onRefresh: () => void;
}

const WARN_THRESHOLD = 50;
const DANGER_THRESHOLD = 10;

function balanceColor(balance?: number): string {
  if (balance === undefined || balance === null) return 'text-gray-400';
  if (balance <= DANGER_THRESHOLD) return 'text-red-600';
  if (balance <= WARN_THRESHOLD) return 'text-yellow-600';
  return 'text-green-600';
}

function balanceBg(balance?: number): string {
  if (balance === undefined || balance === null) return 'bg-gray-50';
  if (balance <= DANGER_THRESHOLD) return 'bg-red-50';
  if (balance <= WARN_THRESHOLD) return 'bg-yellow-50';
  return 'bg-green-50';
}

function ProviderCard({ label, provider }: { label: string; provider: ProviderBalance }) {
  return (
    <div className={`rounded-lg border border-gray-100 p-3 ${balanceBg(provider.balance)}`}>
      <div className="mb-2 flex items-center gap-2">
        <DollarSign size={16} className={balanceColor(provider.balance)} />
        <span className="text-xs font-semibold text-gray-700">{label}</span>
      </div>
      {provider.error ? (
        <div className="flex items-center gap-1.5 text-sm text-red-500">
          <AlertTriangle size={14} />
          <span>{provider.error}</span>
        </div>
      ) : (
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Balance</span>
            <span className={`font-bold ${balanceColor(provider.balance)}`}>
              {provider.balance !== undefined ? `$${provider.balance.toFixed(2)}` : 'N/A'}
            </span>
          </div>
          {provider.frozen !== undefined && provider.frozen > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Frozen</span>
              <span className="font-medium text-gray-600">${provider.frozen.toFixed(2)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ApiBalancesWidget({ data, loading, onRefresh }: Props) {
  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">API Balances</h3>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {loading && !data ? (
        <p className="py-6 text-center text-sm text-gray-400">Loading balances…</p>
      ) : !data ? (
        <p className="py-6 text-center text-sm text-gray-400">Unable to load balances. Click Refresh to retry.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ProviderCard label="Meshy" provider={data.meshy} />
          <ProviderCard label="Tripo" provider={data.tripo} />
          <ProviderCard label="Stability AI" provider={data.stability} />

          {/* Anthropic Claude card */}
          <div className="rounded-lg border border-gray-100 bg-purple-50 p-3">
            <div className="mb-2 flex items-center gap-2 text-purple-600">
              <Bot size={16} />
              <span className="text-xs font-semibold">Anthropic Claude</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Calls</span>
                <span className="font-bold text-purple-700">{data.anthropic.total_calls.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Input Tokens</span>
                <span className="font-medium text-gray-700">
                  {(data.anthropic.total_input_tokens / 1000).toFixed(1)}k
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Output Tokens</span>
                <span className="font-medium text-gray-700">
                  {(data.anthropic.total_output_tokens / 1000).toFixed(1)}k
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
