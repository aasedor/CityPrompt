import { RefreshCw, DollarSign, Bot, AlertTriangle, Minus, Globe, KeyRound } from 'lucide-react';
import type { ApiBalanceResponse, ProviderBalance, ServiceStatus } from '@/services/api';

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

function balanceBg(configured: boolean, balance?: number): string {
  if (!configured) return 'bg-gray-50';
  if (balance === undefined || balance === null) return 'bg-gray-50';
  if (balance <= DANGER_THRESHOLD) return 'bg-red-50';
  if (balance <= WARN_THRESHOLD) return 'bg-yellow-50';
  return 'bg-green-50';
}

function formatBalance(balance: number | undefined, unit: string | undefined): string {
  if (balance === undefined || balance === null) return 'N/A';
  const rounded = Number.isInteger(balance) ? balance.toLocaleString() : balance.toFixed(2);
  return `${rounded} ${unit || 'credits'}`;
}

function ProviderCard({ label, provider }: { label: string; provider: ProviderBalance }) {
  if (!provider.configured) {
    return (
      <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
        <div className="mb-2 flex items-center gap-2">
          <Minus size={16} className="text-gray-300" />
          <span className="text-xs font-semibold text-gray-400">{label}</span>
        </div>
        <p className="text-sm text-gray-400">Not configured</p>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border border-gray-100 p-3 ${balanceBg(provider.configured, provider.balance)}`}>
      <div className="mb-2 flex items-center gap-2">
        <DollarSign size={16} className={balanceColor(provider.balance)} />
        <span className="text-xs font-semibold text-gray-700">{label}</span>
      </div>
      {provider.error ? (
        <div className="flex items-center gap-1.5 text-sm text-red-500">
          <AlertTriangle size={14} />
          <span className="truncate">{provider.error}</span>
        </div>
      ) : (
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Balance</span>
            <span className={`font-bold ${balanceColor(provider.balance)}`}>
              {formatBalance(provider.balance, provider.unit)}
            </span>
          </div>
          {provider.frozen !== undefined && provider.frozen > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Frozen</span>
              <span className="font-medium text-gray-600">
                {formatBalance(provider.frozen, provider.unit)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ServiceCard({ service }: { service: ServiceStatus }) {
  const LABELS: Record<string, string> = {
    mapbox: 'Mapbox',
    google_oauth: 'Google OAuth',
  };
  const ICONS: Record<string, typeof Globe> = {
    mapbox: Globe,
    google_oauth: KeyRound,
  };
  const Icon = ICONS[service.provider] || Globe;
  const label = LABELS[service.provider] || service.provider;

  return (
    <div className={`rounded-lg border border-gray-100 p-3 ${service.configured ? 'bg-blue-50' : 'bg-gray-50'}`}>
      <div className="mb-2 flex items-center gap-2">
        <Icon size={16} className={service.configured ? 'text-blue-500' : 'text-gray-300'} />
        <span className={`text-xs font-semibold ${service.configured ? 'text-gray-700' : 'text-gray-400'}`}>{label}</span>
      </div>
      {service.configured ? (
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Status</span>
            <span className="font-medium text-green-600">Active</span>
          </div>
          {service.description && (
            <p className="text-xs text-gray-400">{service.description}</p>
          )}
        </div>
      ) : (
        <p className="text-sm text-gray-400">Not configured</p>
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
        <p className="py-6 text-center text-sm text-gray-400">Loading balances...</p>
      ) : !data ? (
        <p className="py-6 text-center text-sm text-gray-400">Unable to load balances. Click Refresh to retry.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ProviderCard label="Meshy" provider={data.meshy} />
          <ProviderCard label="Tripo" provider={data.tripo} />
          <ProviderCard label="Stability AI" provider={data.stability} />

          {/* Anthropic Claude card */}
          {data.anthropic.configured ? (
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
          ) : (
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
              <div className="mb-2 flex items-center gap-2">
                <Minus size={16} className="text-gray-300" />
                <span className="text-xs font-semibold text-gray-400">Anthropic Claude</span>
              </div>
              <p className="text-sm text-gray-400">Not configured</p>
            </div>
          )}

          {/* Gemini card */}
          {data.gemini.configured ? (
            <div className="rounded-lg border border-gray-100 bg-teal-50 p-3">
              <div className="mb-2 flex items-center gap-2 text-teal-600">
                <Bot size={16} />
                <span className="text-xs font-semibold">Google Gemini</span>
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total Calls</span>
                  <span className="font-bold text-teal-700">{data.gemini.total_calls.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Input Tokens</span>
                  <span className="font-medium text-gray-700">
                    {(data.gemini.total_input_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Output Tokens</span>
                  <span className="font-medium text-gray-700">
                    {(data.gemini.total_output_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
              <div className="mb-2 flex items-center gap-2">
                <Minus size={16} className="text-gray-300" />
                <span className="text-xs font-semibold text-gray-400">Google Gemini</span>
              </div>
              <p className="text-sm text-gray-400">Not configured</p>
            </div>
          )}

          {/* Non-metered services */}
          {data.services?.map((svc) => (
            <ServiceCard key={svc.provider} service={svc} />
          ))}
        </div>
      )}
    </div>
  );
}
