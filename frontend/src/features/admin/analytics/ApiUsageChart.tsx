import type { ApiUsageResponse } from '@/services/api';

interface Props {
  data: ApiUsageResponse | null;
  range: string;
  onRangeChange: (range: string) => void;
}

const PROVIDER_COLORS: Record<string, string> = {
  meshy: 'bg-blue-500',
  tripo: 'bg-green-500',
  stability: 'bg-amber-500',
  anthropic: 'bg-purple-500',
  gemini: 'bg-teal-500',
};

const PROVIDER_DOT_COLORS: Record<string, string> = {
  meshy: 'bg-blue-500',
  tripo: 'bg-green-500',
  stability: 'bg-amber-500',
  anthropic: 'bg-purple-500',
  gemini: 'bg-teal-500',
};

const ranges = ['7d', '30d', '90d', 'all'] as const;
const rangeLabels: Record<string, string> = {
  '7d': '7 Days',
  '30d': '30 Days',
  '90d': '90 Days',
  all: 'All time',
};

export function ApiUsageChart({ data, range, onRangeChange }: Props) {
  if (!data) {
    return (
      <div className="card">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-primary-950/60">Daily Credit Usage</h3>
          <div className="inline-flex rounded-lg border border-primary-950/[0.08] bg-white p-1">
            {ranges.map((r) => (
              <button
                key={r}
                onClick={() => onRangeChange(r)}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  range === r
                    ? 'bg-primary-600 text-white'
                    : 'text-primary-950/50 hover:bg-primary-950/[0.04]'
                }`}
              >
                {rangeLabels[r]}
              </button>
            ))}
          </div>
        </div>
        <p className="py-8 text-center text-sm text-primary-950/50">No usage data available yet</p>
      </div>
    );
  }

  // Group daily usage by date for stacked bars
  const dateMap = new Map<string, Record<string, number>>();
  for (const entry of data.daily) {
    if (!dateMap.has(entry.date)) {
      dateMap.set(entry.date, {});
    }
    const record = dateMap.get(entry.date)!;
    record[entry.provider] = (record[entry.provider] || 0) + entry.credits;
  }

  const dates = Array.from(dateMap.keys()).sort();
  const allProviders = Array.from(new Set(data.daily.map((d) => d.provider)));

  // Find the max stacked total for scaling
  let maxTotal = 0;
  for (const credits of dateMap.values()) {
    const total = Object.values(credits).reduce((sum, v) => sum + v, 0);
    if (total > maxTotal) maxTotal = total;
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary-950/60">Daily Credit Usage</h3>
        <div className="inline-flex rounded-lg border border-primary-950/[0.08] bg-white p-1">
          {ranges.map((r) => (
            <button
              key={r}
              onClick={() => onRangeChange(r)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                range === r
                  ? 'bg-primary-600 text-white'
                  : 'text-primary-950/50 hover:bg-primary-950/[0.04]'
              }`}
            >
              {rangeLabels[r]}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mb-3 flex flex-wrap gap-3">
        {allProviders.map((provider) => (
          <div key={provider} className="flex items-center gap-1.5 text-xs text-primary-950/50">
            <span className={`inline-block h-2.5 w-2.5 rounded-full ${PROVIDER_DOT_COLORS[provider] || 'bg-neutral-400'}`} />
            <span className="capitalize">{provider}</span>
          </div>
        ))}
      </div>

      {/* CSS Bar Chart */}
      {dates.length === 0 ? (
        <p className="py-8 text-center text-sm text-primary-950/50">No usage data in this period</p>
      ) : (
        <div className="flex items-end gap-px overflow-x-auto" style={{ height: '180px' }}>
          {dates.map((date) => {
            const credits = dateMap.get(date) || {};
            const total = Object.values(credits).reduce((sum, v) => sum + v, 0);
            const heightPct = maxTotal > 0 ? (total / maxTotal) * 100 : 0;

            return (
              <div
                key={date}
                className="group relative flex min-w-[8px] flex-1 flex-col justify-end"
                style={{ height: '100%' }}
                title={`${date}: ${total.toFixed(1)} credits`}
              >
                <div
                  className="flex w-full flex-col justify-end overflow-hidden rounded-t"
                  style={{ height: `${heightPct}%`, minHeight: total > 0 ? '2px' : '0' }}
                >
                  {allProviders.map((provider) => {
                    const val = credits[provider] || 0;
                    if (val === 0) return null;
                    const segPct = total > 0 ? (val / total) * 100 : 0;
                    return (
                      <div
                        key={provider}
                        className={`w-full ${PROVIDER_COLORS[provider] || 'bg-neutral-400'}`}
                        style={{ height: `${segPct}%`, minHeight: '1px' }}
                      />
                    );
                  })}
                </div>
                {/* Tooltip on hover */}
                <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-1 hidden -translate-x-1/2 whitespace-nowrap rounded bg-neutral-800 px-2 py-1 text-xs text-primary-950 group-hover:block">
                  {date}: {total.toFixed(1)} cr
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Provider / Operation breakdown table */}
      {data.providers.length > 0 && (
        <div className="mt-6">
          <p className="mb-2 text-xs font-medium text-primary-950/50">Breakdown by Provider & Operation</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-primary-950/[0.08] text-left text-xs text-primary-950/50">
                  <th className="pb-2 pr-3">Provider</th>
                  <th className="pb-2 pr-3">Operation</th>
                  <th className="pb-2 pr-3 text-right">Credits</th>
                  <th className="pb-2 pr-3 text-right">Calls</th>
                  <th className="pb-2 text-right">Success Rate</th>
                </tr>
              </thead>
              <tbody>
                {data.providers.map((provider) =>
                  provider.by_operation.length > 0 ? (
                    provider.by_operation.map((op, i) => (
                      <tr key={`${provider.provider}-${op.operation}`} className="border-b border-primary-950/[0.06] last:border-0">
                        <td className="py-2 pr-3">
                          {i === 0 ? (
                            <div className="flex items-center gap-1.5">
                              <span className={`inline-block h-2 w-2 rounded-full ${PROVIDER_DOT_COLORS[provider.provider] || 'bg-neutral-400'}`} />
                              <span className="font-medium capitalize text-primary-950/60">{provider.provider}</span>
                            </div>
                          ) : null}
                        </td>
                        <td className="py-2 pr-3 text-primary-950/50">{op.operation}</td>
                        <td className="py-2 pr-3 text-right text-primary-950/50">{op.total_credits.toFixed(1)}</td>
                        <td className="py-2 pr-3 text-right text-primary-950/50">{op.call_count}</td>
                        <td className="py-2 text-right">
                          <span
                            className={`font-medium ${
                              op.success_rate >= 95
                                ? 'text-green-400'
                                : op.success_rate >= 80
                                  ? 'text-yellow-400'
                                  : 'text-red-600'
                            }`}
                          >
                            {op.success_rate.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr key={provider.provider} className="border-b border-primary-950/[0.06] last:border-0">
                      <td className="py-2 pr-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`inline-block h-2 w-2 rounded-full ${PROVIDER_DOT_COLORS[provider.provider] || 'bg-neutral-400'}`} />
                          <span className="font-medium capitalize text-primary-950/60">{provider.provider}</span>
                        </div>
                      </td>
                      <td className="py-2 pr-3 text-primary-950/50">-</td>
                      <td className="py-2 pr-3 text-right text-primary-950/50">{provider.total_credits.toFixed(1)}</td>
                      <td className="py-2 pr-3 text-right text-primary-950/50">{provider.total_calls}</td>
                      <td className="py-2 text-right">
                        <span
                          className={`font-medium ${
                            provider.success_rate >= 95
                              ? 'text-green-400'
                              : provider.success_rate >= 80
                                ? 'text-yellow-400'
                                : 'text-red-600'
                          }`}
                        >
                          {provider.success_rate.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
