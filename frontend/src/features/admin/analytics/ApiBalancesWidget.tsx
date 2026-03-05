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
  if (balance === undefined || balance === null) return 'text-primary-950/50';
  if (balance <= DANGER_THRESHOLD) return 'text-red-600';
  if (balance <= WARN_THRESHOLD) return 'text-yellow-400';
  return 'text-green-400';
}

function balanceBg(configured: boolean, balance?: number): string {
  if (!configured) return 'bg-white';
  if (balance === undefined || balance === null) return 'bg-white';
  if (balance <= DANGER_THRESHOLD) return 'bg-red-50';
  if (balance <= WARN_THRESHOLD) return 'bg-yellow-500/10';
  return 'bg-green-500/10';
}

function formatBalance(balance: number | undefined, unit: string | undefined): string {
  if (balance === undefined || balance === null) return 'N/A';
  const rounded = Number.isInteger(balance) ? balance.toLocaleString() : balance.toFixed(2);
  return `${rounded} ${unit || 'credits'}`;
}

function ProviderCard({ label, provider }: { label: string; provider: ProviderBalance }) {
  if (!provider.configured) {
    return (
      <div className="rounded-lg border border-primary-950/[0.08] bg-white p-3">
        <div className="mb-2 flex items-center gap-2">
          <Minus size={16} className="text-primary-950/40" />
          <span className="text-xs font-semibold text-primary-950/50">{label}</span>
        </div>
        <p className="text-sm text-primary-950/50">Not configured</p>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border border-primary-950/[0.08] p-3 ${balanceBg(provider.configured, provider.balance)}`}>
      <div className="mb-2 flex items-center gap-2">
        <DollarSign size={16} className={balanceColor(provider.balance)} />
        <span className="text-xs font-semibold text-primary-950/60">{label}</span>
      </div>
      {provider.error ? (
        <div className="flex items-center gap-1.5 text-sm text-red-600">
          <AlertTriangle size={14} />
          <span className="truncate">{provider.error}</span>
        </div>
      ) : (
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-primary-950/50">Balance</span>
            <span className={`font-bold ${balanceColor(provider.balance)}`}>
              {formatBalance(provider.balance, provider.unit)}
            </span>
          </div>
          {provider.frozen !== undefined && provider.frozen > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-primary-950/50">Frozen</span>
              <span className="font-medium text-primary-950/50">
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
    <div className={`rounded-lg border border-primary-950/[0.08] p-3 ${service.configured ? 'bg-blue-500/10' : 'bg-white'}`}>
      <div className="mb-2 flex items-center gap-2">
        <Icon size={16} className={service.configured ? 'text-blue-400' : 'text-primary-950/40'} />
        <span className={`text-xs font-semibold ${service.configured ? 'text-primary-950/60' : 'text-primary-950/50'}`}>{label}</span>
      </div>
      {service.configured ? (
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-primary-950/50">Status</span>
            <span className="font-medium text-green-400">Active</span>
          </div>
          {service.description && (
            <p className="text-xs text-primary-950/50">{service.description}</p>
          )}
        </div>
      ) : (
        <p className="text-sm text-primary-950/50">Not configured</p>
      )}
    </div>
  );
}

export function ApiBalancesWidget({ data, loading, onRefresh }: Props) {
  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary-950/60">API Balances</h3>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-primary-950/50 hover:bg-primary-950/[0.04] disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {loading && !data ? (
        <p className="py-6 text-center text-sm text-primary-950/50">Loading balances...</p>
      ) : !data ? (
        <p className="py-6 text-center text-sm text-primary-950/50">Unable to load balances. Click Refresh to retry.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <ProviderCard label="Meshy" provider={data.meshy} />
          <ProviderCard label="Tripo" provider={data.tripo} />
          <ProviderCard label="Stability AI" provider={data.stability} />

          {/* Anthropic Claude card */}
          {data.anthropic.configured ? (
            <div className="rounded-lg border border-primary-950/[0.08] bg-purple-500/10 p-3">
              <div className="mb-2 flex items-center gap-2 text-purple-400">
                <Bot size={16} />
                <span className="text-xs font-semibold">Anthropic Claude</span>
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Total Calls</span>
                  <span className="font-bold text-purple-400">{data.anthropic.total_calls.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Input Tokens</span>
                  <span className="font-medium text-primary-950/60">
                    {(data.anthropic.total_input_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Output Tokens</span>
                  <span className="font-medium text-primary-950/60">
                    {(data.anthropic.total_output_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-primary-950/[0.08] bg-white p-3">
              <div className="mb-2 flex items-center gap-2">
                <Minus size={16} className="text-primary-950/40" />
                <span className="text-xs font-semibold text-primary-950/50">Anthropic Claude</span>
              </div>
              <p className="text-sm text-primary-950/50">Not configured</p>
            </div>
          )}

          {/* Gemini card */}
          {data.gemini.configured ? (
            <div className="rounded-lg border border-primary-950/[0.08] bg-teal-500/10 p-3">
              <div className="mb-2 flex items-center gap-2 text-teal-400">
                <Bot size={16} />
                <span className="text-xs font-semibold">Google Gemini</span>
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Total Calls</span>
                  <span className="font-bold text-teal-400">{data.gemini.total_calls.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Input Tokens</span>
                  <span className="font-medium text-primary-950/60">
                    {(data.gemini.total_input_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-primary-950/50">Output Tokens</span>
                  <span className="font-medium text-primary-950/60">
                    {(data.gemini.total_output_tokens / 1000).toFixed(1)}k
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-primary-950/[0.08] bg-white p-3">
              <div className="mb-2 flex items-center gap-2">
                <Minus size={16} className="text-primary-950/40" />
                <span className="text-xs font-semibold text-primary-950/50">Google Gemini</span>
              </div>
              <p className="text-sm text-primary-950/50">Not configured</p>
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
